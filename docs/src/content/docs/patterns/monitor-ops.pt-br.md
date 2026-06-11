---
title: MonitorOps
description: Monitore fluxos de trabalho agenticos em um repositório, publique relatórios de observabilidade e escale falhas recorrentes ou desperdício.
sidebar:
  badge: { text: 'Observabilidade', variant: 'tip' }
---

Use este padrão quando desejar que um fluxo de trabalho agendado inspecione outros fluxos de trabalho agenticos, resuma o que aconteceu e escale padrões incomuns de custo ou falha.

O [repositório agentic-ops](https://github.com/githubnext/agentic-ops) fornece a implementação de referência para esta abordagem.

## O que este padrão faz

Este padrão revisa logs de fluxo de trabalho em todo um repositório, classifica comportamentos notáveis e publica um relatório estruturado. Quando detecta falhas repetidas, consumo anormal de tokens ou outros padrões insalubres, ele pode escalar essas descobertas em issues para acompanhamento.

Este padrão é útil para monitoramento de todo o repositório porque cria um registro operacional durável em vez de depender de inspeção ad hoc de execuções individuais de fluxo de trabalho.

## Fluxo de trabalho típico

1. Executar em um agendamento para coletar atividade recente do fluxo de trabalho.
2. Analisar logs, custos e sinais de falha em todas as execuções.
3. Postar um relatório de resumo em uma Discussão do GitHub ou outro destino durável.
4. Abrir ou atualizar issues quando o mesmo problema cruzar um limite.

## Quando usar

Use este padrão quando um repositório tiver atividade de fluxo de trabalho suficiente para que os mantenedores precisem de um resumo regular em vez de verificar cada execução manualmente. Também ajuda quando os fluxos de trabalho abrangem múltiplas equipes e falhas ou desperdícios precisam ser expostos em um local compartilhado.

## Documentação relacionada

- [Monitoramento com Projetos](/gh-aw/experimental/monitoring-with-projects/) para rastreamento durável com Projetos e safe outputs
- [OpenTelemetry](/gh-aw/reference/open-telemetry/) para enriquecer a telemetria do fluxo de trabalho
- [Comandos de Auditoria](/gh-aw/reference/audit/) para investigar execuções individuais e regressões
