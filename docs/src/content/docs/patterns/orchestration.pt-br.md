---
title: Orquestração
description: Coordene múltiplos fluxos de trabalho agenticos usando workflow dispatch ou chamadas de fluxo de trabalho reutilizáveis (padrão orquestrador/trabalhador).
---

Use este padrão quando um fluxo de trabalho (o **orquestrador**) precisar distribuir trabalho para um ou mais fluxos de trabalho **trabalhadores** (workers).

## O padrão orquestrador/trabalhador

- **Orquestrador**: decide o que fazer a seguir, divide o trabalho em unidades, despacha trabalhadores.
- **Trabalhador(es)**: realizam o trabalho concreto (triagem, mudanças de código, análise) com permissões/ferramentas limitadas.
- **Monitoramento opcional**: tanto o orquestrador quanto os trabalhadores podem atualizar um quadro de Projeto do GitHub para visibilidade.

## Trabalhadores de despacho com `dispatch-workflow`

Permita o despacho de fluxos de trabalho específicos via API `workflow_dispatch` do GitHub:

```yaml
safe-outputs:
  dispatch-workflow:
    workflows: [repo-triage-worker, dependency-audit-worker]
    max: 10
```

Durante a compilação, o gh-aw valida se os fluxos de trabalho de destino existem e suportam `workflow_dispatch`. Os trabalhadores recebem um payload JSON e são executados de forma assíncrona como execuções de fluxo de trabalho independentes.

Veja o safe output [`dispatch-workflow`](/gh-aw/reference/safe-outputs/#workflow-dispatch-dispatch-workflow).

## Trabalhadores de chamada com `call-workflow`

Chame fluxos de trabalho reutilizáveis (`workflow_call`) via fan-out em tempo de compilação — sem chamada de API em tempo de execução:

```yaml
safe-outputs:
  call-workflow:
    workflows: [spring-boot-bugfix, frontend-dep-upgrade]
    max: 1
```

O compilador valida que cada trabalhador declara `workflow_call`, gera uma ferramenta MCP tipada por trabalhador a partir de suas entradas e emite um job condicional `uses:`. Em tempo de execução, o trabalhador que o agente selecionou executa como parte da mesma execução de fluxo de trabalho — preservando `github.actor` e a atribuição de cobrança.

Veja o safe output [`call-workflow`](/gh-aw/reference/safe-outputs/#workflow-call-call-workflow).

## Escolhendo entre as duas abordagens

Use `call-workflow` quando a atribuição do ator importa, os trabalhadores precisam terminar antes que o orquestrador conclua, ou você deseja zero sobrecarga de API. Use `dispatch-workflow` quando os trabalhadores devem ser executados de forma assíncrona, sobreviver à execução pai ou precisar de entradas `workflow_dispatch`.

## Passando IDs de correlação

Se seus trabalhadores precisarem de contexto compartilhado, passe uma entrada explícita como `tracker_id` (string) e inclua-a nas saídas dos trabalhadores (por exemplo, escrevendo-a em um campo personalizado do Projeto).

Veja também: [Monitoramento](/gh-aw/experimental/monitoring-with-projects/)
