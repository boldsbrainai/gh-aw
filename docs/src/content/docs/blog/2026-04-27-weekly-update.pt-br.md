---
title: "Atualização Semanal – 27 de abril de 2026"
description: "A v0.71.1 chega com correções críticas de bugs, v0.71.0 adiciona melhorias na detecção de ameaças e atualizações do mecanismo Claude, além de um destaque para o fluxo de trabalho auto-triage-issues."
authors:
  - copilot
date: 2026-04-27
---

Mais uma semana produtiva em [github/gh-aw](https://github.com/github/gh-aw)! Dois lançamentos foram feitos — v0.71.0 e v0.71.1 — trazendo correções de confiabilidade em todos os níveis, desde melhorias na detecção de ameaças para o mecanismo Claude até um loop que estava silenciosamente consumindo milhões de tokens. Aqui está o que foi enviado.

## Lançamento: [v0.71.1](https://github.com/github/gh-aw/releases/tag/v0.71.1)

Lançado em 24 de abril, este lançamento de patch é todo sobre correção:

- **Forma de objeto `protected-files` agora compila corretamente** ([#28341](https://github.com/github/gh-aw/pull/28341)): Fluxos de trabalho usando a sintaxe de objeto documentada `{policy, exclude}` estavam sendo rejeitados em tempo de compilação. Isso foi corrigido — o esquema agora aceita tanto a forma abreviada de string quanto a forma de objeto completo.
- **Skills pré-agente não são mais sobrescritas em gatilhos `pull_request`** ([#28290](https://github.com/github/gh-aw/pull/28290)): Skills instaladas por `pre-agent-steps` estavam sendo silenciadas porque o passo "Restaurar pastas de configuração do agente" rodava _depois_ delas. A ordenação dos passos agora está correta.
- **Diff incremental para tamanho de patch de `push_to_pull_request_branch`** ([#28198](https://github.com/github/gh-aw/pull/28198)): A verificação de tamanho máximo de patch agora mede apenas a mudança incremental desde o último push, não o diff completo do branch padrão. Chega de rejeições espúrias por limite de tamanho em branches de longa duração.
- **Loop infinito `jsweep` corrigido** ([#28353](https://github.com/github/gh-aw/pull/28353)): Um fluxo de trabalho estava chamando `create_pull_request` em um loop, acumulando 4,64M de tokens por execução. Ele agora sai após criar um PR. 😅

## Lançamento: [v0.71.0](https://github.com/github/gh-aw/releases/tag/v0.71.0)

Lançado em 23 de abril, focado em confiabilidade de tempo de execução e novas capacidades:

- **Configuração de Node.js adicionada aos jobs de detecção de ameaças** ([#28160](https://github.com/github/gh-aw/pull/28160)): O erro `node: command not found` nos fluxos de trabalho de detecção de ameaças do Copilot desapareceu — a configuração do Node.js agora é emitida antes de `copilot_driver.cjs`.
- **Rastreamento OTLP para execuções canceladas** ([#28172](https://github.com/github/gh-aw/pull/28172)): Execuções canceladas manualmente agora emitem um span de OpenTelemetry adequado, para que você tenha visibilidade total da duração mesmo quando uma execução é interrompida.
- **Mecanismo Claude: `bypassPermissions` → `acceptEdits`** ([#28047](https://github.com/github/gh-aw/pull/28047)): Migra para longe do flag descontinuado e corrige entradas de servidor MCP ausentes em `--allowed-tools`, mantendo fluxos de trabalho movidos a Claude totalmente funcionais.

## Pull Requests Notáveis

Além dos lançamentos, esta semana também viu algumas melhorias úteis de qualidade de vida mescladas diretamente à main:

- **[Adicionar orientação do comando `gh aw run` e referência de comandos CLI](https://github.com/github/gh-aw/pull/28616)**: Melhores docs para rodar fluxos de trabalho localmente — uma fonte comum de confusão.
- **[Correção de acessibilidade: âncora de link de salto](https://github.com/github/gh-aw/pull/28618)**: Renomeado `#_top` → `#main-content` para atender aos requisitos WCAG 2.4.1.
- **[Corrigir falso alarme de `daily-cache-strategy-analyzer`](https://github.com/github/gh-aw/pull/28617)**: O fluxo de trabalho estava gerando alertas espúrios na inicialização quando o cache estava simplesmente vazio. Agora ele verifica adequadamente antes de soar o alarme.

## 🤖 Agente da Semana: auto-triage-issues

O sentinela incansável do rastreador de issues — lê cada issue aberta e a classifica para que as pessoas certas a vejam, automaticamente, em uma agenda.

Esta semana `auto-triage-issues` rodou **três vezes em um único dia** (apenas em 27 de abril), escanear fielmente em busca de issues não triadas a cada vez de forma agendada. Em suas execuções, ele teve uma média de apenas 4-6 turnos por execução, mantendo as coisas enxutas enquanto ainda fazia 6 chamadas de API do GitHub por execução. O fluxo de trabalho até melhorou sua própria eficiência no meio do dia — caindo de 6 turnos na execução da manhã para 4 turnos à tarde, aparentemente aprendendo a chegar ao ponto mais rápido. As métricas de observabilidade notaram educadamente que ele poderia ser "parcialmente redutível à automação determinística", mas, honestamente, onde está a diversão nisso?

Uma de suas execuções ganhou uma menção honrosa do sistema de avaliação agentic: "Esta execução de Triagem parece estável o suficiente para que a automação determinística possa ser um ajuste mais simples." O fluxo de trabalho respondeu rodando novamente uma hora depois, exatamente da mesma forma que antes. Icônico.

💡 **Dica de uso**: Combine `auto-triage-issues` com um fluxo de trabalho de notificação baseado em label para que os membros certos da equipe sejam chamados no momento em que uma nova issue for categorizada.

→ [Ver o fluxo de trabalho no GitHub](https://github.com/github/gh-aw/blob/main/.github/workflows/auto-triage-issues.md)

## Experimente

Atualize para a [v0.71.1](https://github.com/github/gh-aw/releases/tag/v0.71.1) hoje e confira todas as correções. Feedback e contribuições são sempre bem-vindos em [github/gh-aw](https://github.com/github/gh-aw).
