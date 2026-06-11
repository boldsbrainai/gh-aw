---
title: CorrectionOps
description: Melhore fluxos de trabalho agentic a partir de correções humanas confiáveis sem retreinar o modelo subjacente
---

:::caution[Experimental]
CorrectionOps é um padrão experimental. A orientação e a forma do fluxo de trabalho nesta página podem mudar à medida que o padrão é testado em mais fluxos de trabalho do mundo real.
:::

CorrectionOps é um padrão de fluxo de trabalho que compara previsões com correções humanas posteriores.

Em vez de retreinar o modelo, o CorrectionOps melhora o fluxo de trabalho em torno do modelo. Ele armazena previsões no momento da decisão, compara-as com a verdade humana confiável posterior e usa essa evidência para atualizar instruções, roteamento, limites e decisões de rollout.

O loop básico é simples:

1. Salve o que o fluxo de trabalho previu
2. Colete o que os humanos decidiram mais tarde
3. Use a diferença para melhorar o fluxo de trabalho

## Quando Usar CorrectionOps

Use CorrectionOps quando você quiser transformar um processo de decisão humana em um fluxo de trabalho agentic iterativamente em vez de tudo de uma vez.

É um bom ajuste quando humanos ainda tomam ou corrigem a decisão real, mas você quer que o fluxo de trabalho melhore com o tempo atualizando instruções, roteamento, limites ou estado de rollout.

Ajustes típicos incluem rotulagem e classificação, roteamento e priorização, moderação e aprovações, e resumos ou recomendações que humanos corrigem mais tarde.

É especialmente útil quando o caminho de rollout é gradual:

- Comece com `staged: true`
- Mantenha a avaliação e o relatório em Ops
- Use correções posteriores para melhorar o fluxo de trabalho
- Promova para gravações diretas apenas quando a evidência for forte o suficiente

## Como Funciona

Uma configuração limpa de CorrectionOps tem duas superfícies de longa duração. A produção permanece autoritativa. Ops é o lar de longa duração para predição, entrada de correção, relatórios, atualizações de instrução e controle de rollout.

Isso significa que os fluxos de trabalho geralmente permanecem em Ops. No início, eles relatam, comparam e se adaptam a partir de Ops sem gravar de volta na produção. Após a promoção, eles podem gravar diretamente na produção.

A maioria das implementações se reduz a três classes de fluxo de trabalho: um relay leve que encaminha fatos estáveis para ops, um fluxo de trabalho de predição que persiste snapshots e grava com segurança, e um fluxo de trabalho de comparar/relatar/decidir que verifica a verdade humana posterior e atualiza o sistema quando a evidência é forte o suficiente.

A regra importante é manter relés, resolução de snapshot, diffing e agrupamento determinísticos. Use o agente para julgamento semântico, não para reconstruir o histórico de eventos ou inferir proveniência após o fato.

A maioria das implementações reduz-se a três classes de fluxo de trabalho: um relay leve que encaminha fatos estáveis para ops, um fluxo de trabalho de predição que persiste snapshots e grava com segurança, e um fluxo de trabalho de comparar/relatar/decidir que verifica a verdade humana posterior e atualiza o sistema quando a evidência é forte o suficiente.

CorrectionOps não requer um repositório de avaliação separado. A progressão normal é começar com `staged: true`, depois usar adaptação gerenciada por ops e revisão protegida, depois habilitar gravações diretas em produção uma vez que a evidência seja forte o suficiente.

### Peças do Fluxo de Trabalho Completo

Se você quiser a divisão explícita do fluxo de trabalho, o mesmo exemplo geralmente se divide em quatro peças.

#### 1. Relay no Repositório de Origem

O relay apenas encaminha fatos estáveis e proveniência para ops. Ele não deve calcular diffs, inferir intenção humana ou decidir se o fluxo de trabalho estava correto.

```yaml title="prod-repo/.github/workflows/relay-correction-signals.yml"
name: Relay Sinais de Correção

on:
  issues:
    types: [opened, labeled, unlabeled]

jobs:
  relay:
    runs-on: ubuntu-latest
    steps:
      - name: Encaminhar fatos estáveis para ops
        uses: actions/github-script@v8
        with:
          github-token: ${{ secrets.OPS_DISPATCH_TOKEN }}
          script: |
            await github.rest.repos.createDispatchEvent({
              owner: 'org',
              repo: 'ops-repo',
              event_type: context.payload.action === 'opened' ? 'item-created' : 'truth-feedback',
              client_payload: {
                data: {
                  source_repository: `${context.repo.owner}/${context.repo.repo}`,
                  source_type: 'issue',
                  item_number: context.payload.issue.number,
                  item_title: context.payload.issue.title,
                  item_url: context.payload.issue.html_url,
                  event_type: context.payload.action,
                  label: context.payload.label?.name || null,
                  actor: context.actor,
                  actor_type: context.actor.endsWith('[bot]') ? 'bot' : 'human',
                  occurred_at: new Date().toISOString(),
                },
              },
            });
```

#### 2. Fluxo de Trabalho de Predição em Ops

O fluxo de trabalho de predição consome entradas normalizadas, aplica as instruções atuais e persiste um snapshot durável que pode ser comparado mais tarde.

```aw wrap title="ops-repo/.github/workflows/predict-items.md"
---
name: Predizer Itens

on:
  schedule: daily
  workflow_dispatch:
  repository_dispatch:
    types: [item-created]

tools:
  github:
    toolsets: [issues, repos]

safe-outputs:
  create-issue:
  update-issue:
---

# Predizer Itens

Leia itens preparados de `/tmp/gh-aw/agent/item-scan`, aplique as instruções atuais, escreva artefatos de revisão através de safe outputs em Ops e anexe um snapshot de predição contendo o identificador de origem, ação prevista, versão da instrução e timestamp.
```

#### 3. Comparar, Relatar e Decidir em Ops

O fluxo de trabalho de revisão lê previsões persistidas e verdade humana posterior, constrói diffs determinísticos primeiro e somente então pede ao agente para resumir padrões ou propor atualizações de instrução.

```aw wrap title="ops-repo/.github/workflows/review-corrections.md"
---
name: Revisar Correções

on:
  schedule: weekly
  workflow_dispatch:
    inputs:
      mode:
        description: relatório ou adaptação
        required: false
        default: relatório
        type: choice
        options: [relatório, adaptação]

safe-outputs:
  create-issue:
  create-pull-request:
---

# Revisar Correções

Leia `correction-diffs.json` de `/tmp/gh-aw/agent/correction-review`. No modo `relatório`, publique um resumo de saúde. No modo `adaptação`, abra um PR de rascunho atualizando o arquivo de instrução apenas quando a evidência agrupada for forte o suficiente.
```

#### 4. Coletor Determinístico Opcional

Adicione um coletor separado apenas quando o limite de verdade posterior merecer seu próprio gatilho, permissões ou caminho de gravação serializado.

```yaml title="ops-repo/.github/workflows/collect-corrections.yml"
name: Coletar Correções

on:
  repository_dispatch:
    types: [truth-feedback]

jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - name: Resolver verdade autoritativa e armazenar evidência de correção
        run: ./scripts/store-correction-evidence.sh
```

### Contratos Estáveis Para Definir Primeiro

Antes de adicionar lógica de rollout ou prompts de adaptação, defina quatro pequenos contratos determinísticos:

1. payload de relay: a identidade mínima de origem, identidade de objeto, tipo de evento, fatos do ator e timestamps encaminhados para ops
2. snapshot de predição: o registro durável do que o fluxo de trabalho previu e sob qual versão de instrução
3. entrada de revisão de correção: o artefato de diff determinístico usado por relatórios e adaptação
4. contrato de portão de rollout: quais evidências ou aprovações são necessárias antes que as gravações diretas em produção sejam habilitadas

Rotulagem de discussão, roteamento, moderação, priorização, aprovações e resumos podem reutilizar essa forma. O objeto de produção muda, mas a configuração de CorrectionOps não.

## Documentação Relacionada

- [Modo Staged](/gh-aw/reference/staged-mode/) para orientação opcional de rollout de gravação segura dentro de CorrectionOps
- [SideRepoOps](/gh-aw/patterns/side-repo-ops/) para separar a infraestrutura de fluxo de trabalho do repositório de produção
- [MultiRepoOps](/gh-aw/patterns/multi-repo-ops/) para coordenar fluxos de trabalho através de fronteiras de repositório
- [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/) para controlar alvos de gravação e proteções
- [Ferramentas GitHub](/gh-aw/reference/github-tools/) para leituras e operações cross-repository
