---
title: ResearchPlanAssignOps
description: Orquestre pesquisa profunda, planejamento estruturado e atribuição automatizada para impulsionar ciclos de desenvolvimento impulsionados por IA, do insight ao PR mesclado
sidebar:
  badge: { text: 'Multi-fase', variant: 'caution' }
---

ResearchPlanAssignOps é um padrão de desenvolvimento de quatro fases que vai da descoberta automatizada ao código mesclado com controle humano em cada ponto de decisão. Um agente de pesquisa revela insights, um agente de planejamento os converte em issues acionáveis, um agente de codificação implementa o trabalho e um humano revisa e mescla.

## As Quatro Fases

```
Pesquisa → Planejamento → Atribuição → Mesclagem
```

Cada fase produz um artefato concreto consumido pela próxima, e cada transição é um ponto de verificação humano.

### Fase 1: Pesquisa

Um fluxo de trabalho agendado investiga o código-fonte de um ângulo específico e publica suas descobertas como uma discussão do GitHub. A discussão é o contrato entre a fase de pesquisa e tudo o que se segue — ela contém a análise, recomendações e contexto que um planejador precisa.

O fluxo de trabalho [`go-fan`](https://github.com/github/gh-aw/blob/main/.github/workflows/go-fan.md) é um exemplo ao vivo: ele executa a cada dia útil, escolhe uma dependência Go, compara o uso atual com as melhores práticas upstream e cria uma discussão `[go-fan]` na categoria `audits`.

```aw wrap
---
name: Go Fan
on:
  schedule: daily on weekdays
  workflow_dispatch:
engine: claude
safe-outputs:
  create-discussion:
    title-prefix: "[go-fan] "
    category: "audits"
    max: 1
    close-older-discussions: true
tools:
  cache-memory: true
  github:
    toolsets: [default]
---

Analise a dependência Go de hoje. Compare o uso atual neste
repositório com as melhores práticas upstream e releases recentes.
Salve um resumo em scratchpad/mods/ e crie uma discussão
com descobertas e recomendações de melhoria.
```

O agente de pesquisa usa `cache-memory` para rastrear quais módulos foram revisados para que ele rode sistematicamente entre as execuções.

### Fase 2: Planejamento

Após ler a discussão de pesquisa, um desenvolvedor dispara o comando `/plan` nela. O fluxo de trabalho [`plan`](https://github.com/github/gh-aw/blob/main/.github/workflows/plan.md) lê a discussão, extrai itens de trabalho concretos e cria até cinco sub-issues agrupadas sob uma issue de rastreamento pai.

```
/plan foque nas vitórias rápidas e simplificações de API
```

O planejador formata cada sub-issue para um agente de codificação: um objetivo claro, os arquivos a serem modificados, orientação passo a passo de implementação e critérios de aceitação. As issues são marcadas como `[plan]` e `ai-generated`.

> [!TIP]
> O comando `/plan` aceita orientação inline. Direcione-o para descobertas de alta prioridade ou para longe das de menor prioridade antes de gerar issues.

### Fase 3: Atribuição

Com issues bem delimitadas em mãos, o desenvolvedor [atribui-as ao Copilot](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-a-pr#assigning-an-issue-to-copilot) para implementação automatizada. O Copilot abre um pull request e posta atualizações de progresso conforme trabalha.

As issues podem ser atribuídas individualmente através da UI do GitHub, ou pré-atribuídas em massa via um fluxo de trabalho orquestrador:

```aw wrap
---
name: Auto-atribuir issues de plano ao Copilot
on:
  issues:
    types: [labeled]
engine: copilot
safe-outputs:
  assign-to-user:
    target: "*"
  add-comment:
    target: "*"
---

Quando uma issue for marcada como `plan` e não tiver nenhum responsável,
atribua-a ao Copilot e adicione um comentário indicando
atribuição automatizada.
```

Para planos com múltiplas issues, atribuições podem ser executadas em paralelo — o Copilot trabalha independentemente em cada issue e abre PRs separados.

### Fase 4: Mesclagem

O pull request do Copilot é revisado por um mantenedor humano. O mantenedor verifica a correção, executa testes e mescla. A issue de rastreamento criada na Fase 2 fecha automaticamente quando todas as sub-issues são resolvidas.

## Exemplo de Ponta a Ponta

O rastreamento a seguir mostra o ciclo completo usando `go-fan` como o motor de pesquisa.

**Segunda-feira 7 AM** — `go-fan` executa e cria uma discussão:

> **[go-fan] Revisão de Módulo Go: spf13/cobra**
>
> O uso atual cria um `Command` novo por invocação. O cobra v1.8 introduziu
> `SetContext` para propagação de cancelamento. Vitórias rápidas: passe contexto através
> de subcomandos, use `PersistentPreRunE` para configuração compartilhada.

**Segunda-feira à tarde** — O desenvolvedor lê a discussão e digita:

```
/plan
```

O planejador cria uma issue de rastreamento pai `[plan] melhorias no cobra` com três sub-issues:

- `[plan] Passar contexto através de subcomandos usando cobra SetContext`
- `[plan] Refatorar configuração compartilhada para PersistentPreRunE`
- `[plan] Adicionar testes de cancelamento de contexto`

**Segunda-feira à tarde** — O desenvolvedor atribui as duas primeiras issues ao Copilot. Ambos abrem PRs em minutos.

**Terça-feira** — O desenvolvedor revisa os PRs, solicita uma pequena mudança em um, aprova o outro. Ambos são mesclados até o fim do dia. A issue de rastreamento é fechada.

## Padrões de Configuração de Fluxo de Trabalho

### Pesquisa: produzir uma discussão por execução

```aw wrap
safe-outputs:
  create-discussion:
    expires: 1d
    category: "research"
    max: 1
    close-older-discussions: true
```

`close-older-discussions: true` impede o acúmulo de discussões — apenas a descoberta mais recente permanece aberta para o planejador.

### Pesquisa: manter memória entre execuções

```aw wrap
tools:
  cache-memory: true
```

Use `cache-memory` para rastrear estado entre execuções agendadas — quais itens foram revisados, dados de tendência ou linhas de base históricas.

### Planejamento: agrupamento de issue

```aw wrap
safe-outputs:
  create-issue:
    expires: 2d
    title-prefix: "[plan] "
    labels: [plan, ai-generated]
    max: 5
    group: true
```

`group: true` cria uma issue de rastreamento pai automaticamente. Não crie o pai manualmente — o fluxo de trabalho cuida disso.

### Atribuição: pré-atribuição via `assignees`

Para fluxos de trabalho de pesquisa que produzem issues autocontidas e bem delimitadas, pule a fase de planejamento manual e atribua diretamente:

```aw wrap
safe-outputs:
  create-issue:
    title-prefix: "[fix] "
    labels: [ai-generated]
    assignees: copilot
```

O fluxo de trabalho `duplicate-code-detector` usa essa abordagem — correções de duplicação são estreitas o suficiente para que uma fase de planejamento não agregue valor.

## Customização

Adapte este padrão variando:

- **Foco da pesquisa**: análise estática, métricas de desempenho, qualidade da documentação, segurança, duplicação de código, cobertura de testes
- **Frequência**: diário, semanal, sob demanda
- **Formato do relatório**: discussões (para descobertas abertas), issues (para tarefas autocontidas)
- **Abordagem de planejamento**: automática (pesquisa bem delimitada vai direto para o Copilot via `assignees: copilot`) vs. manual (desenvolvedor revisa antes de atribuir)
- **Método de atribuição**: pré-atribuir no fluxo de trabalho de pesquisa, atribuir em massa via fluxo de trabalho orquestrador ou atribuir individualmente através da UI do GitHub

## Limitações

A abordagem multi-fase leva mais tempo do que a execução direta e exige que os desenvolvedores revisem relatórios de pesquisa e issues geradas. Agentes de pesquisa podem revelar descobertas que não exigem ação (falsos positivos), e cada transição de fase precisa de passagens de bastão claras. Agentes de pesquisa frequentemente exigem MCPs especializados (Serena, Tavily, etc.) para análise mais profunda.

## Quando usar ResearchPlanAssignOps

Este padrão se encaixa quando:

- O escopo do trabalho é desconhecido até que a análise seja executada
- Issues precisam de priorização humana antes da implementação
- Descobertas de pesquisa variam em qualidade (algumas execuções não encontram nada acionável)
- Múltiplos itens de trabalho podem ser executados em paralelo

Prefira um padrão mais simples quando:

- O trabalho já está bem definido (use [IssueOps](/gh-aw/patterns/issue-ops/))
- Issues podem ir diretamente para o Copilot sem revisão (use o atalho `assignees: copilot` no seu fluxo de trabalho de pesquisa)
- O trabalho abrange múltiplos repositórios (use [MultiRepoOps](/gh-aw/patterns/multi-repo-ops/))

## Fluxos de Trabalho Existentes

| Fase | Fluxo de Trabalho | Descrição |
|-------|----------|-------------|
| Pesquisa | [`go-fan`](https://github.com/github/gh-aw/blob/main/.github/workflows/go-fan.md) | Análise diária de dependência Go com comparação de melhores práticas |
| Pesquisa | [`copilot-cli-deep-research`](https://github.com/github/gh-aw/blob/main/.github/workflows/copilot-cli-deep-research.md) | Análise semanal de uso de funcionalidade do Copilot CLI |
| Pesquisa | [`static-analysis-report`](https://github.com/github/gh-aw/blob/main/.github/workflows/static-analysis-report.md) | Scan de segurança diário com descobertas agrupadas |
| Pesquisa | [`duplicate-code-detector`](https://github.com/github/gh-aw/blob/main/.github/workflows/duplicate-code-detector.md) | Análise diária de duplicação semântica (auto-atribui) |
| Planejamento | [`plan`](https://github.com/github/gh-aw/blob/main/.github/workflows/plan.md) | Comando slash `/plan` — converte issues ou discussões em sub-issues |
| Atribuição | GitHub UI / fluxo de trabalho | [Atribuir issues ao Copilot](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-a-pr#assigning-an-issue-to-copilot) para criação automatizada de PR |

## Padrões Relacionados

- **[Orquestração](/gh-aw/patterns/orchestration/)** — Distribuir trabalho através de múltiplos fluxos de trabalho trabalhadores
- **[DailyOps](/gh-aw/patterns/daily-ops/)** — Melhorias incrementais agendadas sem uma fase de planejamento separada
- **[DispatchOps](/gh-aw/patterns/dispatch-ops/)** — Pesquisas acionadas manualmente e investigações pontuais
