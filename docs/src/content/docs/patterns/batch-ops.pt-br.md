---
title: BatchOps
description: Processe grandes volumes de trabalho em paralelo ou em lotes particionados usando jobs de matriz, limitação de taxa (rate-limit) e agregação de resultados
sidebar:
  badge: { text: 'Processamento em lote', variant: 'caution' }
---

BatchOps é um padrão para processar grandes volumes de itens de trabalho de forma eficiente. Em vez de iterar sequencialmente por centenas de itens em uma única execução de fluxo de trabalho, o BatchOps divide o trabalho em partes (chunks), paraleliza quando possível, lida com falhas parciais de forma graciosa e agrega resultados em um relatório consolidado.

## Quando usar BatchOps vs Processamento Sequencial

| Cenário | Recomendação |
|----------|----------------|
| < 50 itens, a ordem importa | Sequencial ([WorkQueueOps](/gh-aw/patterns/workqueue-ops/)) |
| 50–500 itens, a ordem não importa | BatchOps com processamento particionado |
| > 500 itens, paralelismo alto seguro | BatchOps com distribuição de matriz (matrix fan-out) |
| Itens têm dependências entre si | Sequencial (WorkQueueOps) |
| Itens são totalmente independentes | BatchOps (qualquer estratégia) |
| Limites de taxa ou cotas rigorosos | Processamento em lote com consciência de limite de taxa |

## Estratégia de Lote 1: Processamento Particionado (Chunked)

Divida o trabalho em páginas de tamanho fixo usando `GITHUB_RUN_NUMBER`. Cada execução processa uma página, pegando a próxima fatia na próxima execução agendada. Os itens devem ter uma chave de ordenação estável (data de criação, número da issue) para que a paginação seja determinística.

```aw wrap
---
on:
  schedule: daily on weekdays
  workflow_dispatch:

tools:
  github:
    toolsets: [issues]
  bash:
    - "jq"
    - "date"

safe-outputs:
  add-labels:
    allowed: [stale, needs-triage, archived]
    max: 30
  add-comment:
    max: 30

steps:
  - name: compute-page
    id: compute-page
    run: |
      PAGE_SIZE=25
      # Use o resto da divisão do número da execução para percorrer as páginas; reinicie a cada 1000 execuções
      PAGE=$(( (GITHUB_RUN_NUMBER % 1000) * PAGE_SIZE ))
      echo "page_offset=$PAGE" >> "$GITHUB_OUTPUT"
      echo "page_size=$PAGE_SIZE" >> "$GITHUB_OUTPUT"
---

# Processador de Issues Particionado

Esta execução cobre o offset ${{ steps.compute-page.outputs.page_offset }} com tamanho de página ${{ steps.compute-page.outputs.page_size }}.

1. Liste issues ordenadas por data de criação (mais antigas primeiro), pulando as primeiras ${{ steps.compute-page.outputs.page_offset }} e pegando ${{ steps.compute-page.outputs.page_size }}.
2. Para cada issue: adicione `stale` se atualizada há mais de 90 dias sem comentários recentes; adicione `needs-triage` se não tiver labels; poste um comentário de aviso de stale, se aplicável.
3. Resuma: issues rotuladas, comentários postados, quaisquer erros.
```

## Estratégia de Lote 2: Fan-Out com Matriz

Use a matriz (matrix) do GitHub Actions para executar vários trabalhadores de lote em paralelo, cada um responsável por um shard (fragmento) não sobreposto. Use `fail-fast: false` para que uma falha de shard não cancele os outros. Cada shard obtém seu próprio token e cota de limite de taxa da API.

```aw wrap
---
on:
  workflow_dispatch:
    inputs:
      total_shards:
        description: "Número de trabalhadores paralelos"
        default: "4"
        required: false

jobs:
  batch:
    strategy:
      matrix:
        shard: [0, 1, 2, 3]
      fail-fast: false   # Continue outros shards mesmo se um falhar

tools:
  github:
    toolsets: [issues, pull_requests]

safe-outputs:
  add-labels:
    allowed: [reviewed, duplicate, wontfix]
    max: 50
---

# Trabalhador de Lote em Matriz — Shard ${{ matrix.shard }} de ${{ inputs.total_shards }}

Processar apenas issues onde `(issue_number % ${{ inputs.total_shards }}) == ${{ matrix.shard }}` — isso garante que nenhum shard processe a mesma issue.

1. Liste todas as issues abertas (até 500) e mantenha apenas aquelas atribuídas a este shard.
2. Para cada issue: verifique duplicatas (título/conteúdo similar); adicione label `reviewed`; se uma duplicata for encontrada, adicione `duplicate` e referencie a original.
3. Relatório: issues neste shard, quantas rotuladas, quaisquer falhas.
```

## Estratégia de Lote 3: Processamento com Consciência de Limite de Taxa

Limite as chamadas de API processando itens em pequenos sub-lotes com pausas explícitas. Mais lento que o processamento sem limites, mas reduz drasticamente os erros de limite de taxa. Use [Controles de Limitação de Taxa](/gh-aw/reference/rate-limiting-controls/) para limitação integrada.

```aw wrap
---
on:
  workflow_dispatch:
    inputs:
      batch_size:
        description: "Itens por sub-lote"
        default: "10"
      pause_seconds:
        description: "Segundos para pausar entre sub-lotes"
        default: "30"

tools:
  github:
    toolsets: [repos, issues]
  bash:
    - "sleep"
    - "jq"

safe-outputs:
  add-comment:
    max: 100
  add-labels:
    allowed: [labeled-by-bot]
    max: 100
---

# Processador de Lote com Limite de Taxa

Processe todas as issues abertas em sub-lotes de ${{ inputs.batch_size }}, pausando ${{ inputs.pause_seconds }} segundos entre lotes.

1. Busque todos os números de issue abertos (pagine se necessário).
2. Para cada sub-lote: leia o corpo de cada issue, determine o label correto, adicione o label, então pause antes do próximo sub-lote.
3. No HTTP 429: pause 60 segundos e tente novamente uma vez antes de marcar o item como falho.
4. Relatório: total processado, falhas, ignorados.
```

## Estratégia de Lote 4: Agregação de Resultados

Colete resultados de vários trabalhadores ou execuções de lote e agregue-os em uma única issue de resumo. Use [cache-memory](/gh-aw/reference/cache-memory/) para armazenar resultados intermediários quando as execuções abrangerem vários dias.

```aw wrap
---
on:
  workflow_dispatch:
    inputs:
      report_issue:
        description: "Número da issue para agregar resultados"
        required: true

tools:
  cache-memory: true
  github:
    toolsets: [issues, repos]
  bash:
    - "jq"

safe-outputs:
  add-comment:
    max: 1
  update-issue:
    body: true

steps:
  - name: collect-results
    run: |
      # Agregar resultados de todos os arquivos de resultado escritos por execuções de lote anteriores
      RESULTS_DIR="/tmp/gh-aw/cache-memory/batch-results"
      if [ -d "$RESULTS_DIR" ]; then
        jq -s '
          {
            total_processed: (map(.processed) | add // 0),
            total_failed: (map(.failed) | add // 0),
            total_skipped: (map(.skipped) | add // 0),
            runs: length,
            errors: (map(.errors // []) | add // [])
          }
        ' "$RESULTS_DIR"/*.json > /tmp/gh-aw/cache-memory/aggregate.json
        cat /tmp/gh-aw/cache-memory/aggregate.json
      else
        echo '{"total_processed":0,"total_failed":0,"total_skipped":0,"runs":0,"errors":[]}' \
          > /tmp/gh-aw/cache-memory/aggregate.json
      fi
---

# Agregador de Resultados de Lote

Agregue resultados de execuções de lote anteriores armazenadas em `/tmp/gh-aw/cache-memory/batch-results/` na issue #${{ inputs.report_issue }}.

1. Leia `/tmp/gh-aw/cache-memory/aggregate.json` para totais e cada arquivo de resultado individual para detalhamento por execução.
2. Atualize o corpo da issue #${{ inputs.report_issue }} com uma tabela Markdown: linha de resumo (processado/falha/ignorado) mais detalhamento por execução. Liste quaisquer erros que exijam intervenção manual.
3. Adicione um comentário: "Lote completo ✅" se não houver falhas, ou "Lote completo com falhas ⚠️" com uma lista de itens falhos.
4. Para cada item falho, crie uma sub-issue para que possa ser tentado novamente.
```

## Manipulação de Erros e Falhas Parciais

Fluxos de trabalho em lote devem ser resilientes a falhas individuais de itens.

**Padrão de tentativa (retry)**: Ao usar filas em cache-memory, rastreie `retry_count` por item falho. Tente novamente itens onde `retry_count < 3`; após três falhas, mova-os para `permanently_failed` para revisão humana. Incremente a contagem e salve a fila após cada tentativa.

**Isolamento de falha**:

- Use `fail-fast: false` em jobs de matriz para que uma falha de shard não cancele os outros
- Grave resultados por item antes de passar para o próximo item
- Armazene erros com contexto suficiente para diagnosticar e tentar novamente

## Exemplo do Mundo Real: Atualizando Labels em Mais de 100 Issues

Este exemplo processa uma migração de label (renomear `bug` para `type:bug`) em todas as issues abertas e fechadas.

```aw wrap
---
on:
  workflow_dispatch:
    inputs:
      dry_run:
        description: "Visualizar alterações sem aplicá-las"
        default: "true"

tools:
  github:
    toolsets: [issues]
  bash:
    - "jq"

safe-outputs:
  add-labels:
    allowed: [type:bug]
    max: 200
  remove-labels:
    allowed: [bug]
    max: 200
  add-comment:
    max: 1

concurrency:
  group: label-migration
  cancel-in-progress: false
---

# Migração de Label: `bug` → `type:bug`

Migre todas as issues com o label `bug` para usar `type:bug`. Liste todas as issues (abertas e fechadas) com label `bug`, paginando para recuperar todas elas.

- Se `${{ inputs.dry_run }}` for `true`: reporte quantas issues seriam atualizadas e adicione um comentário de visualização. Não faça alterações.
- Se `${{ inputs.dry_run }}` for `false`: para cada issue, adicione `type:bug` e remova `bug`. Processe em sub-lotes de 20 com pausas de 15 segundos. Rastreie sucessos e falhas.

Adicione um comentário final com totais e um link de pesquisa para verificar se nenhum label `bug` permanece.
```

## Páginas Relacionadas

- [WorkQueueOps](/gh-aw/patterns/workqueue-ops/) — Processamento de fila sequencial com listas de verificação de issue, sub-issues, cache-memory e Discussões
- [ResearchPlanAssignOps](/gh-aw/patterns/research-plan-assign-ops/) — Pesquisa → Plano → Atribuição para trabalho supervisionado por desenvolvedor
- [Memória de Cache](/gh-aw/reference/cache-memory/) — Armazenamento de estado persistente entre execuções de fluxo de trabalho
- [Memória de Repositório](/gh-aw/reference/repo-memory/) — Estado persistente com commit no Git
- [Controles de Limitação de Taxa](/gh-aw/reference/rate-limiting-controls/) — Limitação integrada para fluxos de trabalho que consomem muita API
- [Concorrência](/gh-aw/reference/concurrency/) — Impedir execuções de lote sobrepostas
