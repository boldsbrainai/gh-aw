---
title: WorkQueueOps
description: Processe uma fila de itens de trabalho usando issues do GitHub, sub-issues, cache-memory ou Discussões como backends de fila duráveis
sidebar:
  badge: { text: 'Baseado em fila', variant: 'note' }
---

WorkQueueOps é um padrão para processar sistematicamente um grande backlog de itens de trabalho. Em vez de processar tudo de uma vez, o trabalho é enfileirado, rastreado e consumido incrementalmente — sobrevivendo a interrupções, limites de taxa e horizontes de vários dias. Use-o quando as operações forem idempotentes e a visibilidade do progresso importar.

## Estratégia de Fila 1: Lista de Verificação de Issue como Fila

Use checkboxes de issue do GitHub como uma fila leve e legível por humanos. O agente lê o corpo da issue, encontra itens não marcados, processa cada um e marca o item. Melhor para lotes pequenos a médios (< 100 itens). Use controles de [Concorrência](/gh-aw/reference/concurrency/) para evitar condições de corrida entre execuções paralelas.

```aw wrap
---
on:
  workflow_dispatch:
    inputs:
      queue_issue:
        description: "Número da issue contendo a fila da lista de verificação"
        required: true

tools:
  github:
    toolsets: [issues]

safe-outputs:
  update-issue:
    body: true
  add-comment:
    max: 1

concurrency:
  group: workqueue-${{ inputs.queue_issue }}
  cancel-in-progress: false
---

# Processador de Fila de Lista de Verificação

Você está processando uma fila de trabalho armazenada como checkboxes na issue #${{ inputs.queue_issue }}.

1. Leia a issue #${{ inputs.queue_issue }} e encontre todos os itens não marcados (`- [ ]`).
2. Para cada item não marcado (no máximo 10 por execução): execute o trabalho necessário, então edite o corpo da issue para mudar `- [ ]` para `- [x]`.
3. Adicione um comentário resumindo o que foi concluído e o que resta.
4. Se todos os itens estiverem marcados, feche a issue com um comentário de resumo.
```

## Estratégia de Fila 2: Sub-Issues como Fila

Crie uma sub-issue por item de trabalho. O agente consulta sub-issues abertas de uma issue de rastreamento pai, processa cada uma e a fecha quando concluído. Escala para centenas de itens com threads de discussão individuais por item. Use limites `max:` em `close-issue` para evitar tempestades de notificação.

```aw wrap
---
on:
  schedule: hourly
  workflow_dispatch:

tools:
  github:
    toolsets: [issues]

safe-outputs:
  add-comment:
    max: 5
  close-issue:
    max: 5

concurrency:
  group: sub-issue-queue
  cancel-in-progress: false
---

# Processador de Fila de Sub-Issue

Você está processando uma fila de sub-issues abertas. A issue de rastreamento pai está marcada com `queue-tracking`.

1. Encontre a issue aberta marcada com `queue-tracking` — este é o pai da fila.
2. Liste suas sub-issues abertas e processe no máximo 5 por execução.
3. Para cada sub-issue: leia o corpo, execute o trabalho, adicione um comentário de resultado, então feche a issue.
4. Adicione um comentário de progresso na issue pai mostrando quantos itens restam.

Se não houver sub-issues abertas, poste um comentário na issue pai dizendo que a fila está vazia.
```

## Estratégia de Fila 3: Fila de Cache-Memory

Armazene o estado da fila como um arquivo JSON em [cache-memory](/gh-aw/reference/cache-memory/). Cada execução carrega o arquivo, retoma de onde a última execução parou e salva o estado atualizado. Melhor para filas grandes e horizontes de processamento de vários dias onde os itens são gerados programaticamente. Cache-memory é escopado a um único branch; use timestamps seguros para sistemas de arquivos em nomes de arquivos (sem dois-pontos — ex: `YYYY-MM-DD-HH-MM-SS-sss`).

```aw wrap
---
on:
  schedule: daily on weekdays
  workflow_dispatch:

tools:
  cache-memory: true
  github:
    toolsets: [repos, issues]
  bash:
    - "jq"

safe-outputs:
  add-comment:
    max: 10
  add-labels:
    allowed: [processed, needs-review]
    max: 10
---

# Processador de Fila de Cache-Memory

Você processa itens de uma fila JSON persistente em `/tmp/gh-aw/cache-memory/workqueue.json`:

```json
{
  "pending": ["item-1", "item-2"],
  "in_progress": [],
  "completed": ["item-0"],
  "failed": [],
  "last_run": "2026-04-07-06-00-00"
}
```

1. Carregue o arquivo da fila. Se ele não existir, inicialize-o listando todas as issues abertas sem a label `processed` e populando `pending` com seus números.
2. Mova até 10 itens de `pending` para `in_progress`.
3. Para cada item: execute a operação necessária, então mova-o para `completed` em caso de sucesso ou `failed` (com uma nota de erro) em caso de falha.
4. Salve o JSON da fila atualizado e relate: X concluídos, Y falhas, Z restantes.

Se `pending` estiver vazio, anuncie que a fila está esgotada.
```

## Estratégia de Fila 4: Fila Baseada em Discussão

Use uma Discussão do GitHub para rastrear itens de trabalho pendentes. Respostas não resolvidas representam trabalho pendente; processar um item significa resolver sua resposta. Melhor para filas de origem comunitária e colaboração assíncrona onde humanos precisam inspecionar itens antes ou depois do processamento. Requer `discussions` no conjunto de ferramentas do GitHub.

```aw wrap
---
on:
  schedule: daily
  workflow_dispatch:

tools:
  github:
    toolsets: [discussions]

safe-outputs:
  add-comment:
    max: 5
  create-discussion:
    title-prefix: "[queue-log] "
    category: "General"

concurrency:
  group: discussion-queue
  cancel-in-progress: false
---

# Processador de Fila de Discussão

Uma Discussão do GitHub intitulada "Work Queue" (categoria "General") rastreia itens de trabalho pendentes.
Cada resposta de nível superior não resolvida é um item de trabalho.

1. Encontre a discussão "Work Queue" e liste todas as respostas não resolvidas (`isAnswered: false`).
2. Para cada resposta não resolvida (no máximo 5 por execução): analise a descrição do trabalho, execute o trabalho, então responda com o resultado.
3. Crie um post de discussão de resumo documentando o que foi processado hoje.
```

## Idempotência e Concorrência

Todos os padrões de WorkQueueOps devem ser **idempotentes**: executar o mesmo item duas vezes não deve causar processamento duplo.

| Técnica | Como |
|-----------|-----|
| Verificar antes de agir | Consulte o estado atual (label presente? comentário existe?) antes de fazer mudanças |
| Atualizações de estado atômicas | Escreva o estado da fila em uma única etapa; evite atualizações parciais |
| Grupos de concorrência | Use `concurrency.group` com `cancel-in-progress: false` para evitar execuções paralelas |
| Orçamentos de nova tentativa | Rastreie itens com falha separadamente; defina um limite de nova tentativa antes de desistir |

## Páginas Relacionadas

- [BatchOps](/gh-aw/patterns/batch-ops/) — Processe grandes volumes em chunks paralelos em vez de sequencialmente
- [ResearchPlanAssignOps](/gh-aw/patterns/research-plan-assign-ops/) — Padrão Pesquisa → Planejamento → Atribuição para trabalho supervisionado por desenvolvedor
- [Cache Memory](/gh-aw/reference/cache-memory/) — Armazenamento de estado persistente entre execuções de fluxo de trabalho
- [Repo Memory](/gh-aw/reference/repo-memory/) — Estado persistente commitado no git para compartilhamento entre branches
- [Concorrência](/gh-aw/reference/concurrency/) — Evite condições de corrida em fluxos de trabalho baseados em fila
