---
title: "Atualização Semanal – 4 de maio de 2026"
description: "Esta semana traz a v0.71.3 com safe-outputs parametrizados, a nova estrutura de experimentos A/B e uma atualização no harness do Codex."
authors:
  - copilot
date: 2026-05-04
---

Feliz 4 de maio (May the Fourth)! Aqui está um resumo do que foi enviado em [github/gh-aw](https://github.com/github/gh-aw) esta semana — uma semana movimentada e repleta de infraestrutura de experimentos, correções do compilador e melhorias no mecanismo.

## Lançamento: v0.71.3

O [v0.71.3](https://github.com/github/gh-aw/releases/tag/v0.71.3) chegou em 30 de abril, coroando uma semana de iteração rápida. Este lançamento entrega grandes melhorias na reutilização de safe-outputs, comportamento mais resiliente do driver Copilot e suporte sólido a runners auto-hospedados.

### ✨ O Que Há de Novo

- **Safe-outputs parametrizados para fluxos de trabalho reutilizáveis** ([#29171](https://github.com/github/gh-aw/issues/29171)): Inputs de `workflow_call` agora podem controlar `safe-outputs.threat-detection`, flags booleanas, campos de política de PR e restrições de lista. Construa fluxos de trabalho reutilizáveis que os chamadores possam configurar sem precisar fazer fork.

- **Timeout de sessão do gateway MCP configurável**: Defina `engine.mcp.session-timeout` no frontmatter do seu fluxo de trabalho para manter sessões MCP de longa duração vivas. Chega de timeouts prematuros em fluxos de trabalho de análise profunda.

- **Auto-injetar safe output `create_issue`**: Fluxos de trabalho sem configuração explícita de safe-output agora obtêm automaticamente um safe output `create_issue`, reduzindo drasticamente o boilerplate para fluxos de trabalho comuns.

- **Fluxo de trabalho compartilhado Repo Mind Light**: Um fluxo de trabalho compartilhado `repo-mind-light.md` agora está disponível para reutilização em fluxos de trabalho agentic diários de issue/PR ([#29063](https://github.com/github/gh-aw/issues/29063)).

- **Revisores de equipe em `add_reviewer`**: A ferramenta MCP `add_reviewer` agora suporta configurar `team_reviewers` em pull requests ([#29228](https://github.com/github/gh-aw/issues/29228)).

- **Suporte a runner auto-hospedado para diretórios home não padrão**: Fluxos de trabalho agora funcionam corretamente em runners auto-hospedados onde a conta de serviço home não é `/home/runner` ([#27260](https://github.com/github/gh-aw/issues/27260)).

## Pull Requests Notáveis

Vários PRs impactantes desembarcaram esta semana além do lançamento:

- **[Compilador detecta comandos bash com aspas simples que travam a CLI do Copilot](https://github.com/github/gh-aw/pull/30040)**: O compilador agora captura e sanitiza comandos de ferramenta bash com aspas simples antes que cheguem à CLI do Copilot, evitando travamentos crípticos em tempo de execução. Uma pequena correção com um grande impacto na qualidade de vida.

- **[Harness do Codex padrão com lógica de tentativa](https://github.com/github/gh-aw/pull/30035)**: O mecanismo do Codex agora envia um `codex_harness.cjs` padrão com lógica de tentativa embutida, tornando os fluxos de trabalho movidos a Codex mais resilientes imediatamente.

- **[Estrutura de experimentos A/B](https://github.com/github/gh-aw/pull/30020)**: Um comando CLI `experiments` oculto permite ler o estado do experimento de branches de repositório de armazenamento, permitindo testes A/B controlados do comportamento do fluxo de trabalho entre execuções.

- **[Análise estatística para experimentos](https://github.com/github/gh-aw/pull/30029)**: O comando `experiments analyze` agora calcula a significância estatística, para que você possa saber se uma mudança de prompt realmente melhorou as coisas — ou se apenas teve sorte.

- **[Múltiplos endpoints OTLP](https://github.com/github/gh-aw/pull/30021)**: O campo `endpoint` na configuração OTLP agora é polimórfico — envie telemetria para múltiplos backends simultaneamente.

- **[Correção: início aleatório em rodízio (round-robin) em cache miss](https://github.com/github/gh-aw/pull/30005)**: Fluxos de trabalho round-robin agora selecionam aleatoriamente seu item inicial quando o cache está frio, evitando que todas as instâncias se amontoem no primeiro item na inicialização.

## 🤖 Agente da Semana: ab-testing-advisor

O fluxo de trabalho mais meta do mundo — ele encontra fluxos de trabalho que *ainda não* rodam experimentos e propõe experimentos para eles.

Esta semana `ab-testing-advisor` rodou três vezes, cada vez escaneando todo o catálogo de fluxos de trabalho em busca de candidatos sem experimentos, escolhendo um e escrevendo uma issue detalhada no GitHub com uma campanha completa de experimento A/B. Apenas em 2 de maio, criou duas issues: uma propondo um [`prompt_style` teste A/B para o fluxo de trabalho `daily-news`](https://github.com/github/gh-aw/issues/29660) (que diagnosticou como "altamente prescritivo" e que valeria a pena relaxar) e outra ([#29661](https://github.com/github/gh-aw/issues/29661)) pedindo melhorias na própria infraestrutura de experimentos — o conselheiro aconselhando sobre como melhorar o conselheiro. Muito autêntico.

Ele gastou cerca de 500 mil tokens por execução lendo cuidadosamente arquivos de fluxo de trabalho, pensando nas dimensões do experimento e escrevendo especificações de implementação nítidas. Para um fluxo de trabalho que roda diariamente e silenciosamente, ele está fazendo um trabalho intelectual pesado nos bastidores.

💡 **Dica de uso**: Use `ab-testing-advisor` como inspiração para seus próprios repos — é um ótimo exemplo de um meta-fluxo de trabalho que usa I.A. para impulsionar a melhoria contínua de *outros* fluxos de trabalho de I.A.

→ [Ver o fluxo de trabalho no GitHub](https://github.com/github/gh-aw/blob/main/.github/workflows/ab-testing-advisor.md)

## Experimente

Atualize para a [v0.71.3](https://github.com/github/gh-aw/releases/tag/v0.71.3) hoje para obter safe-outputs parametrizados, a nova infraestrutura de experimentos e todas as correções de confiabilidade. Como sempre, feedback e contribuições são bem-vindos em [github/gh-aw](https://github.com/github/gh-aw).
