---
title: DailyOps
description: Fluxos de trabalho agendados para melhorias diárias incrementais - pequenas alterações automatizadas que se acumulam ao longo do tempo
sidebar:
  badge: { text: 'Agendado', variant: 'tip' }
---

Os fluxos de trabalho DailyOps automatizam o progresso incremental em direção a grandes objetivos através de pequenas alterações agendadas diariamente. O trabalho acontece automaticamente em partes gerenciáveis que são fáceis de revisar e integrar.

## O Padrão DailyOps

### Execução Agendada

Os fluxos de trabalho são executados em agendamentos de dias úteis (evitando fins de semana) com `workflow_dispatch` habilitado para testes manuais:

```aw wrap
---
on:
  schedule: daily on weekdays
  workflow_dispatch:
---
```

### Abordagem Faseada

O trabalho progride através de três fases com aprovação do mantenedor entre cada uma:

1. **Pesquisa** - Analise o estado, crie discussão com descobertas
2. **Configuração** - Defina etapas, crie PR de configuração
3. **Execução** - Faça melhorias, verifique, crie PRs de rascunho

### Rastreamento de Progresso

Use discussões do GitHub para manter a continuidade entre execuções. O fluxo de trabalho cria uma discussão (se nenhuma existir) e adiciona comentários de progresso em execuções subsequentes:

```aw wrap
safe-outputs:
  create-discussion:
    title-prefix: "${{ github.workflow }}"
    category: "ideas"
```

A configuração [`safe-outputs:`](/gh-aw/reference/safe-outputs/) (operações validadas do GitHub) permite que a IA solicite a criação de discussão sem exigir permissões de escrita.

### Comentários de Discussão

Para fluxos de trabalho que postam atualizações em uma discussão existente, use `add-comment` com um número de discussão `target` específico. O direcionamento de discussão é automático quando o fluxo de trabalho é executado em um contexto de evento de discussão, ou quando o agente fornece um `item_number`:

```aw wrap
safe-outputs:
  add-comment:
    target: "4750"
```

Este padrão é ideal para postagens de status diárias, relatórios recorrentes ou atualizações da comunidade. O fluxo de trabalho [daily-fact.md](https://github.com/github/gh-aw/blob/main/.github/workflows/daily-fact.md) demonstra isso postando fatos diários sobre o repositório em um tópico de discussão fixado.

### Memória Persistente

Habilite `cache-memory` para manter o estado em `/tmp/gh-aw/cache-memory/` entre execuções, útil para rastrear o progresso, armazenar métricas e construir bases de conhecimento ao longo do tempo:

```aw wrap
tools:
  cache-memory: true
```

## Fluxos de Trabalho DailyOps Comuns

Este repositório implementa vários fluxos de trabalho DailyOps demonstrando diferentes casos de uso:

- **daily-fact.md** - Posta fatos diários sobre o repositório em um tópico de discussão
- **daily-test-improver.md** - Adiciona testes sistematicamente para melhorar a cobertura incrementalmente
- **daily-perf-improver.md** - Identifica e implementa otimizações de desempenho
- **daily-doc-updater.md** - Mantém a documentação sincronizada com as alterações de código mescladas
- **daily-team-status** (do [agentics](https://github.com/githubnext/agentics)) - Cria relatórios de status diários da equipe com resumos de atividades
- **daily-repo-chronicle.md** - Produz atualizações do repositório no estilo de jornal
- **daily-security-observability.md** - Relatório de observabilidade de segurança unificado combinando análise de tráfego de firewall e análise de eventos filtrados por integridade DIFC

Todos seguem a abordagem faseada com discussões para rastreamento e pull requests de rascunho para revisão.

## Padrões Relacionados

- **IssueOps** - Dispare fluxos de trabalho a partir da criação ou comentários de issue
- **ChatOps** - Dispare fluxos de trabalho a partir de slash commands em comentários
- **LabelOps** - Dispare fluxos de trabalho quando labels mudam em issues ou pull requests
- **Fluxo de Trabalho de Planejamento** - Use o comando `/plan` para dividir grandes discussões em itens de trabalho acionáveis, depois atribua sub-tarefas ao Copilot para execução

O DailyOps complementa esses padrões fornecendo automação agendada que não requer gatilhos manuais.
