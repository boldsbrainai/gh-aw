---
title: DeterministicOps
description: Combine computação determinística e extração de dados com raciocínio agentico no GitHub Agentic Workflows para automação híbrida poderosa.
sidebar:
  order: 6
  badge: { text: 'Híbrido', variant: 'caution' }
---

O GitHub Agentic Workflows combina computação determinística com raciocínio de IA, permitindo pré-processamento de dados, filtragem de gatilho personalizada e padrões de pós-processamento. Isso inclui o sub-padrão **DataOps**, onde comandos de shell em `steps:` coletam e preparam dados de forma confiável — rápido, cacheável e reprodutível — então o agente de IA lê os resultados e gera insights. Use isso para agregação de dados, geração de relatórios, análise de tendências, auditoria e qualquer pipeline híbrido.

## Quando usar

Combine etapas determinísticas com agentes de IA para pré-computar dados, filtrar gatilhos, pré-processar entradas, pós-processar saídas ou construir pipelines de computação e raciocínio de várias etapas.

## Arquitetura

Defina jobs determinísticos no frontmatter juntamente com a execução agêntica:

```text
┌────────────────────────┐
│  Jobs Determinísticos  │
│  - Busca de dados      │
│  - Pré-processamento   │
└───────────┬────────────┘
            │ artefatos/saídas
            ▼
┌────────────────────────┐
│   Job do Agente (IA)   │
│   - Raciocina e decide │
└───────────┬────────────┘
            │ saídas seguras
            ▼
┌────────────────────────┐
│ Jobs de Saída Segura   │
│  - Chamadas API GitHub │
└────────────────────────┘
```

## Exemplo de Pré-computação

```yaml wrap title=".github/workflows/release-highlights.md"
---
on:
  push:
    tags: ['v*.*.*']
engine: copilot
safe-outputs:
  update-release:

steps:
  - run: |
      gh release view "${GITHUB_REF#refs/tags/}" --json name,tagName,body > /tmp/gh-aw/agent/release.json
      gh pr list --state merged --limit 100 --json number,title,labels > /tmp/gh-aw/agent/prs.json
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
---

# Gerador de Destaques de Release

Gere destaques de release para `${GITHUB_REF#refs/tags/}`. Analise PRs em `/tmp/gh-aw/agent/prs.json`, categorize alterações e use update-release para anexar destaques às notas de release.
```

Arquivos em `/tmp/gh-aw/agent/` são carregados automaticamente como artefatos e disponibilizados para o agente de IA.

## Padrão de Múltiplos Jobs

```yaml wrap title=".github/workflows/static-analysis.md"
---
on:
  schedule: daily
engine: claude
safe-outputs:
  create-discussion:

jobs:
  run-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: ./gh-aw compile --zizmor --poutine > /tmp/gh-aw/agent/analysis.txt

steps:
  - uses: actions/download-artifact@v6
    with:
      name: analysis-results
      path: /tmp/gh-aw/
---

# Relatório de Análise Estática

Analise as descobertas em `/tmp/gh-aw/agent/analysis.txt`, agrupe por severidade e crie uma discussão com sugestões de correção.
```

Passe dados entre jobs via artefatos, saídas de job ou variáveis de ambiente.

## Filtragem de Gatilho Personalizada

### Etapas Inline (`on.steps:`) — Preferencial

Injete etapas determinísticas diretamente no job de pré-ativação usando `on.steps:`. Isso economiza **um job de fluxo de trabalho** em comparação com o padrão de múltiplos jobs e é a abordagem recomendada para filtragem leve:

```yaml wrap title=".github/workflows/smart-responder.md"
---
on:
  issues:
    types: [opened]
  steps:
    - id: check
      env:
        LABELS: ${{ toJSON(github.event.issue.labels.*.name) }}
      run: echo "$LABELS" | grep -q '"bug"'
      # sai 0 (resultado: success) se o label for encontrado, 1 (resultado: failure) se não
engine: copilot
safe-outputs:
  add-comment:

if: needs.pre_activation.outputs.check_result == 'success'
---

# Respondente de Issue de Bug

Triage de relatório de bug: "${{ github.event.issue.title }}" e add-comment com um resumo dos próximos passos.
```

Cada etapa com um `id` recebe uma saída auto-conectada `<id>_result` definida como `${{ steps.<id>.outcome }}` — `success` quando o código de saída da etapa é 0, `failure` quando diferente de zero. Gateie o fluxo de trabalho verificando `needs.pre_activation.outputs.<id>_result == 'success'`.

Para passar um valor explícito em vez de depender de códigos de saída, defina uma saída de etapa e re-exponha-a via `jobs.pre-activation.outputs`:

```yaml wrap
jobs:
  pre-activation:
    outputs:
      has_bug_label: ${{ steps.check.outputs.has_bug_label }}

if: needs.pre_activation.outputs.has_bug_label == 'true'
```

Quando `on.steps:` precisam de acesso à API do GitHub, use `on.permissions:` para conceder os escopos necessários ao job de pré-ativação:

```yaml wrap
on:
  schedule: every 30m
  permissions:
    issues: read
  steps:
    - id: search
      uses: actions/github-script@v8
      with:
        script: |
          const open = await github.rest.issues.listForRepo({ ...context.repo, state: 'open' });
          core.setOutput('has_work', open.data.length > 0 ? 'true' : 'false');

jobs:
  pre-activation:
    outputs:
      has_work: ${{ steps.search.outputs.has_work }}

if: needs.pre_activation.outputs.has_work == 'true'
```

Veja [Etapas de Pré-Ativação](/gh-aw/reference/triggers/#pre-activation-steps-onsteps) e [Permissões de Pré-Ativação](/gh-aw/reference/triggers/#pre-activation-permissions-onpermissions) para documentação completa.

### Padrão de Múltiplos Jobs — Para Casos Complexos

Use uma entrada `jobs:` separada quando a filtragem exigir ferramentas pesadas (checkout, ferramentas compiladas, múltiplos runners):

```yaml wrap title=".github/workflows/smart-responder.md"
---
on:
  issues:
    types: [opened]
engine: copilot
safe-outputs:
  add-comment:

jobs:
  filter:
    runs-on: ubuntu-latest
    outputs:
      should-run: ${{ steps.check.outputs.result }}
    steps:
      - id: check
        env:
          LABELS: ${{ toJSON(github.event.issue.labels.*.name) }}
        run: |
          if echo "$LABELS" | grep -q '"bug"'; then
            echo "result=true" >> "$GITHUB_OUTPUT"
          else
            echo "result=false" >> "$GITHUB_OUTPUT"
          fi

if: needs.filter.outputs.should-run == 'true'
---

# Respondente de Issue de Bug

Triage de relatório de bug: "${{ github.event.issue.title }}" e add-comment com um resumo dos próximos passos.
```

O compilador adiciona automaticamente o job de filtro como uma dependência do job de ativação, então, quando a condição é falsa, a execução do fluxo de trabalho é **ignorada** (não falha), mantendo a aba Actions limpa.

### Condições de Contexto Simples

Para condições que podem ser expressas diretamente com o contexto do GitHub Actions, use `if:` sem um job personalizado:

```yaml wrap
---
on:
  pull_request:
    types: [opened, synchronize]
engine: copilot
if: github.event.pull_request.draft == false
---
```

### Filtragem Baseada em Consulta

Para condições baseadas em resultados de pesquisa do GitHub, use [`skip-if-match:`](/gh-aw/reference/triggers/#skip-if-match-condition-skip-if-match) ou [`skip-if-no-match:`](/gh-aw/reference/triggers/#skip-if-no-match-condition-skip-if-no-match) na seção `on:` — estes aceitam a [sintaxe de consulta de pesquisa padrão do GitHub](https://docs.github.com/en/search-github/searching-on-github/searching-issues-and-pull-requests) e são avaliados no job de pré-ativação, produzindo o mesmo comportamento de ignorado-não-falha:

```yaml wrap
---
on:
  issues:
    types: [opened]
  # Ignorar se uma issue duplicada já existir (sintaxe de consulta de pesquisa do GitHub)
  skip-if-match: 'is:issue is:open label:duplicate'
engine: copilot
---
```

## Padrão de Pós-Processamento

```yaml wrap title=".github/workflows/code-review.md"
---
on:
  pull_request:
    types: [opened]
engine: copilot

safe-outputs:
  jobs:
    format-and-notify:
      description: "Formatar e postar revisão"
      runs-on: ubuntu-latest
      inputs:
        summary: {required: true, type: string}
      steps:
        - ...
---

# Agente de Revisão de Código

Revise o pull request e use format-and-notify para postar seu resumo.
```

## Importando Instruções Compartilhadas

Defina orientações reutilizáveis em arquivos compartilhados e importe-os:

```yaml wrap title=".github/workflows/analysis.md"
---
on:
  schedule: daily
engine: copilot
imports:
  - shared/reporting.md
safe-outputs:
  create-discussion:
---

# Análise Diária

Siga as diretrizes de formatação de relatório de shared/reporting.md.
```

Para fluxos de trabalho de auditoria baseados em discussão diária, prefira `shared/daily-audit-base.md` para agrupar publicação de discussão, orientação de relatório e observabilidade OTLP em uma única importação.

## Diretório de Dados do Agente

Use `/tmp/gh-aw/agent/` para compartilhar dados com agentes de IA. Os arquivos aqui são carregados automaticamente como artefatos e acessíveis ao agente:

```yaml
steps:
  - run: |
      gh api repos/${{ github.repository }}/issues > /tmp/gh-aw/agent/issues.json
      gh api repos/${{ github.repository }}/pulls > /tmp/gh-aw/agent/pulls.json
```

Referência em prompts: "Analise issues em `/tmp/gh-aw/agent/issues.json` e PRs em `/tmp/gh-aw/agent/pulls.json`."

## DataOps: Extração e Análise de Dados Agendada

Use `steps:` para coletar e pré-processar dados deterministicamente, então deixe o agente analisar e relatar os resultados. Isso é especialmente útil para relatórios agendados, análise de tendências e fluxos de trabalho de auditoria.

### Exemplo: Resumo de Atividade de PR Semanal

````aw wrap
---
name: Resumo Semanal de PR
description: Resume a atividade de pull request da última semana
on:
  schedule: weekly
  workflow_dispatch:

permissions:
  contents: read
  pull-requests: read

engine: copilot
strict: true

network:
  allowed:
    - defaults
    - github

safe-outputs:
  create-discussion:
    title-prefix: "[semanal-resumo] "
    category: "announcements"
    max: 1
    close-older-discussions: true

tools:
  bash: ["*"]

steps:
  - name: Buscar pull requests recentes
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: |
      mkdir -p /tmp/gh-aw/pr-data

      gh pr list \
        --repo "${{ github.repository }}" \
        --state all \
        --limit 100 \
        --json number,title,state,author,createdAt,mergedAt,closedAt,additions,deletions,changedFiles,labels \
        > /tmp/gh-aw/pr-data/recent-prs.json

  - name: Computar estatísticas de resumo
    run: |
      cd /tmp/gh-aw/pr-data

      jq '{
        total: length,
        merged: [.[] | select(.state == "MERGED")] | length,
        open: [.[] | select(.state == "OPEN")] | length,
        closed: [.[] | select(.state == "CLOSED")] | length,
        total_additions: [.[].additions] | add,
        total_deletions: [.[].deletions] | add,
        top_authors: ([.[].author.login] | group_by(.) | map({author: .[0], count: length}) | sort_by(-.count) | .[0:5])
      }' recent-prs.json > stats.json

timeout-minutes: 10
---

# Resumo Semanal de Pull Request

Analise os dados preparados:
- `/tmp/gh-aw/pr-data/recent-prs.json` - Últimos 100 PRs com metadados completos
- `/tmp/gh-aw/pr-data/stats.json` - Estatísticas pré-computadas

Crie uma discussão resumindo: total de PRs, taxa de merge, alterações de código (+/- linhas), principais contribuintes e quaisquer tendências notáveis.
````

### Cache de Dados

Para fluxos de trabalho que são executados com frequência ou processam grandes conjuntos de dados, use cache para evitar chamadas de API redundantes:

```aw wrap
---
cache:
  - key: pr-data-${{ github.run_id }}
    path: /tmp/gh-aw/pr-data
    restore-keys: |
      pr-data-

steps:
  - name: Verifique cache e busque apenas novos dados
    run: |
      if [ -f /tmp/gh-aw/pr-data/recent-prs.json ]; then
        echo "Usando dados em cache"
      else
        gh pr list --limit 100 --json ... > /tmp/gh-aw/pr-data/recent-prs.json
      fi
---
```

### Dados de Múltiplas Fontes

Combine dados de múltiplas fontes antes da análise:

```aw wrap
---
steps:
  - name: Buscar dados de PR
    run: gh pr list --json ... > /tmp/gh-aw/prs.json

  - name: Buscar dados de issue
    run: gh issue list --json ... > /tmp/gh-aw/issues.json

  - name: Buscar execuções de fluxo de trabalho
    run: gh run list --json ... > /tmp/gh-aw/runs.json

  - name: Combinar em dataset unificado
    run: |
      jq -s '{prs: .[0], issues: .[1], runs: .[2]}' \
        /tmp/gh-aw/prs.json \
        /tmp/gh-aw/issues.json \
        /tmp/gh-aw/runs.json \
        > /tmp/gh-aw/combined.json
---

# Relatório de Saúde do Repositório

Analise os dados combinados em `/tmp/gh-aw/combined.json`.
```

## Subagentes com Modelos Menores

Após mover a computação para `steps:`, a próxima otimização é delegar tarefas de raciocínio estreitas e repetitivas — categorização, resumo por item, pontuação de sentimento — para **subagentes inline** apoiados por um modelo menor e mais barato. O agente principal então só precisa ler os resultados pré-processados e sintetizar um relatório final.

```bash
steps:          → comandos de shell determinísticos (rápido, reprodutível, custo zero de IA)
sub-agents:     → agentes de modelo pequeno para análise por item (barato, paralelizado)
main agent:     → orquestra sub-agentes, sintetiza relatório final (raciocínio de alta qualidade)
```

Habilite subagentes inline adicionando `cli-proxy` para que possam fazer chamadas autenticadas à API do GitHub:

```yaml
tools:
  cli-proxy: true
```

### Exemplo: Triagem de Issue com Categorização

```aw wrap
# Triagem Semanal de Issue

Os dados brutos da issue estão em `/tmp/gh-aw/triage/` — um arquivo por issue (`issue-<number>.json`).

## Passo 1 — categorizar cada issue

Para cada arquivo correspondente a `/tmp/gh-aw/triage/issue-*.json`, use o agente
`issue-categorizer` para classificá-la. Escreva o resultado em `/tmp/gh-aw/triage/category-<number>.json`.

## Passo 2 — resumir cada issue

Para cada arquivo de issue, use o agente `issue-summarizer` para produzir um resumo
de uma frase. Escreva o resultado em `/tmp/gh-aw/triage/summary-<number>.json`.

## Passo 3 — sintetizar relatório de triagem

Leia todos os arquivos de categoria e resumo, então crie uma discussão que agrupe issues
por categoria, liste cada uma com seu resumo de uma frase e um link para a issue,
e destaque as 3 principais issues que precisam de atenção mais urgente.

## agent: `issue-categorizer`
---
description: Classifica uma issue do GitHub em exatamente uma categoria
model: claude-haiku-4.5
---
Classifique a issue em exatamente uma de: bug, feature-request, question, documentation, performance, security, ou other.
Retorne um objeto JSON: `{"number": <número da issue>, "category": "<categoria>"}`.

## agent: `issue-summarizer`
---
description: Produz um resumo de uma frase de uma issue do GitHub
model: claude-haiku-4.5
---
Escreva uma única frase (≤ 20 palavras) que descreva sobre o que é a issue.
Retorne um objeto JSON: `{"number": <número da issue>, "summary": "<frase>"}`.
```

| Camada | Modelo | Trabalho feito | Direcionador de custo |
|---|---|---|---|
| `steps:` | — | Buscar + preparar dados | Apenas API do GitHub |
| `issue-categorizer` | Haiku / pequeno | Classificar uma issue | ~200 tokens por issue |
| `issue-summarizer` | Haiku / pequeno | Resumir uma issue | ~150 tokens por issue |
| Agente principal | Modelo completo | Ler todos os resultados, escrever relatório | Uma passada de alta qualidade |

## Documentação relacionada

- [Etapas de Pré-Ativação](/gh-aw/reference/triggers/#pre-activation-steps-onsteps) - Injeção de etapa inline no job de pré-ativação
- [Permissões de Pré-Ativação](/gh-aw/reference/triggers/#pre-activation-permissions-onpermissions) - Conceder escopos adicionais para chamadas de API `on.steps:`
- [Saídas Seguras Personalizadas](/gh-aw/reference/custom-safe-outputs/) - Jobs de pós-processamento personalizados
- [Referência de Frontmatter](/gh-aw/reference/frontmatter/) - Opções de configuração
- [Processo de Compilação](/gh-aw/reference/compilation-process/) - Como os jobs são orquestrados
- [Importações](/gh-aw/reference/imports/) - Compartilhando configurações entre fluxos de trabalho
- [Templating](/gh-aw/reference/templating/) - Usando expressões do GitHub Actions
