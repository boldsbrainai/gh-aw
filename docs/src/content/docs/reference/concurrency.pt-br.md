---
title: Controle de concorrência
description: Guia completo para controle de concorrência no GitHub Agentic Workflows, incluindo configuração de concorrência de job de agente e isolamento de motor.
sidebar:
  order: 1400
---

O GitHub Agentic Workflows usa controle de concorrência de nível duplo para evitar exaustão de recursos e garantir uma execução previsível:
- **Por fluxo de trabalho**: Limites baseados no nome do fluxo de trabalho e contexto de gatilho (issue, PR, branch)
- **Por motor**: Limita a execução da IA em todos os fluxos de trabalho via `engine.concurrency`

## Concorrência por Fluxo de Trabalho

Grupos de concorrência em nível de fluxo de trabalho incluem o nome do fluxo de trabalho mais identificadores específicos de contexto:

| Tipo de gatilho | Grupo de concorrência | Cancelar em andamento |
|--------------|-------------------|-------------------|
| Issues | `gh-aw-${{ github.workflow }}-${{ issue.number }}` | Não |
| Pull Requests | `gh-aw-${{ github.workflow }}-${{ pr.number \|\| ref }}` | Sim (novos commits cancelam execuções obsoletas) |
| Push | `gh-aw-${{ github.workflow }}-${{ github.ref }}` | Não |
| Schedule/Outro | `gh-aw-${{ github.workflow }}` | Não |
| Gatilho de label (atalho de gatilho de label ou label_command) | `gh-aw-${{ github.workflow }}-${{ entity.number }}-${{ github.event.label.name }}` | Sim para PRs, Não caso contrário |

Isso garante que fluxos de trabalho em diferentes issues, PRs ou branches sejam executados simultaneamente sem interferência.

## Concorrência por Motor

O padrão `gh-aw-{engine-id}` por motor padrão garante que apenas um job de agente seja executado por motor em todos os fluxos de trabalho, impedindo a exaustão de recursos de IA. O grupo inclui apenas o ID do motor e o prefixo `gh-aw-` — nome do fluxo de trabalho, números de issue/PR e branches são excluídos.

```yaml wrap
jobs:
  agent:
    concurrency:
      group: "gh-aw-{engine-id}"
```

## Concorrência Personalizada

Substitua qualquer nível independentemente:

```yaml wrap
---
on: push
concurrency:  # Nível de fluxo de trabalho
  group: custom-group-${{ github.ref }}
  cancel-in-progress: true
engine:
  id: copilot
  concurrency:  # Nível de motor
    group: "gh-aw-copilot-${{ github.workflow }}"
tools:
  github:
    allowed: [list_issues]
---
```

## Concorrência de Job de Safe Outputs

O job `safe_outputs` executa independentemente do job do agente e pode processar saídas simultaneamente entre execuções de fluxo de trabalho. Use `safe-outputs.concurrency-group` para serializar o acesso quando necessário:

```yaml wrap
safe-outputs:
  concurrency-group: "safe-outputs-${{ github.repository }}"
  create-issue:
```

Quando definido, o job `safe_outputs` usa `cancel-in-progress: false` — significando que execuções enfileiradas esperam a execução em andamento terminar em vez de serem canceladas. Isso é útil para fluxos de trabalho que criam issues ou pull requests onde operações duplicadas seriam indesejáveis.

Veja [Safe Outputs](/gh-aw/reference/safe-outputs/#safe-outputs-job-concurrency-concurrency-group) para detalhes.

## Comportamento da Fila (`queue`)

Grupos de concorrência do GitHub Actions aceitam um campo opcional `queue` que controla como múltiplas execuções pendentes no mesmo grupo são manipuladas. O compilador gh-aw preserva este campo tanto em blocos de concorrência de nível superior quanto por motor:

| Valor | Comportamento |
|---|---|
| `single` (padrão de Actions) | Apenas a última execução pendente é mantida; execuções pendentes anteriores são descartadas. |
| `max` | Todas as execuções pendentes ficam na fila e executam na ordem de chegada. |

```yaml wrap
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  queue: max
```

Grupos de concorrência gerados pelo compilador (jobs de agente, saída e conclusão) emitem `queue: max` por padrão, para que gatilhos consecutivos sejam executados sequencialmente em vez de serem descartados. Defina `features.group-concurrency-queue: false` para omitir `queue` dos grupos gerados e reverter para o padrão do Actions:

```yaml wrap
features:
  group-concurrency-queue: false
```

## Concorrência de Job de Conclusão

O job `conclusion` — que lida com relatórios e limpeza pós-agente — recebe automaticamente um grupo de concorrência específico do fluxo de trabalho derivado do nome do arquivo do fluxo de trabalho:

```yaml wrap
conclusion:
  concurrency:
    group: "gh-aw-conclusion-my-workflow"
    cancel-in-progress: false
    queue: max
```

Isso evita que jobs de conclusão colidam quando múltiplos agentes executam o mesmo fluxo de trabalho simultaneamente. O grupo usa `cancel-in-progress: false` para que as execuções de conclusão enfileiradas completem em ordem em vez de serem descartadas, e `queue: max` preserva a ordem de chegada para execuções enfileiradas (veja [Comportamento da Fila](#queue-behavior-queue)).

Este grupo de concorrência é definido automaticamente durante a compilação e não requer configuração manual.

Quando `concurrency.job-discriminator` é definido, o discriminador também é anexado ao grupo de concorrência do job de conclusão, tornando o grupo de cada execução distinto:

```yaml wrap
concurrency:
  job-discriminator: ${{ github.event.issue.number || github.run_id }}
```

Isso gera um grupo como `gh-aw-conclusion-my-workflow-${{ github.event.issue.number || github.run_id }}`, evitando que execuções simultâneas para diferentes issues ou entradas compitam pelo mesmo slot de conclusão.

## Concorrência de Fan-Out (`job-discriminator`)

Quando múltiplas instâncias de fluxo de trabalho são despachadas simultaneamente com diferentes entradas (padrão fan-out), os grupos de concorrência em nível de job gerados pelo compilador são estáticos em todas as execuções — fazendo com que todas as execuções despachadas, exceto a última, sejam canceladas à medida que competem pelo mesmo slot.

Use `concurrency.job-discriminator` para anexar uma expressão única aos grupos de concorrência em nível de job gerados pelo compilador (jobs de `agent`, `output` e `conclusion`), tornando o grupo de cada execução despachada distinto:

```yaml wrap
concurrency:
  job-discriminator: ${{ inputs.finding_id }}
```

Sua geração cria um grupo de concorrência em nível de job único por execução despachada, evitando cancelamentos de fan-out enquanto preserva o grupo de concorrência por fluxo de trabalho no nível de fluxo de trabalho.

Expressões comuns:

| Cenário | Expressão |
|---|---|
| Fan-out por uma entrada específica | `${{ inputs.finding_id }}` |
| Unicidade universal (ex: execuções agendadas) | `${{ github.run_id }}` |
| Fallback despachado ou agendado | `${{ inputs.organization \|\| github.run_id }}` |

:::note
`job-discriminator` é uma extensão do gh-aw e é removido do arquivo de lock compilado. Ele não aparece no YAML do GitHub Actions gerado.
:::

:::note
`job-discriminator` não tem efeito em fluxos de trabalho acionados apenas por `workflow_dispatch`, `push` ou `pull_request`, ou quando o motor fornece uma configuração de concorrência explícita em nível de job.
:::

## Documentação relacionada

- [Frontmatter](/gh-aw/reference/frontmatter/) - Referência completa de frontmatter
- [Safe Outputs](/gh-aw/reference/safe-outputs/) - Processamento de safe output e configuração de job
