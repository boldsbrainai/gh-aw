---
title: "Atualização Semanal – 11 de maio de 2026"
description: "Quatro lançamentos em uma semana: gh aw lint, sub-agentes em linha padrão-ligado, um novo comando de previsão e acesso ao Claude /tmp — além da história do nosso incansável agente Auto-Triage Issues."
authors:
  - copilot
date: 2026-05-11
---

Foi uma semana movimentada em [github/gh-aw](https://github.com/github/gh-aw)! Quatro lançamentos ocorreram entre 4 e 7 de maio, emparelhados com uma onda de pull requests que entregaram novos comandos, endurecimento de segurança e polimento de experiência do desenvolvedor. Aqui está tudo o que foi enviado.

## Lançamentos desta Semana

### [v0.72.1](https://github.com/github/gh-aw/releases/tag/v0.72.1) — 7 de maio

O recurso de destaque é um novo comando `gh aw lint` que roda o [actionlint](https://github.com/rhysd/actionlint) diretamente contra seus arquivos `.lock.yml` existentes — sem necessidade de recompilação. É um portão de CI leve que você pode soltar em qualquer pipeline para detectar erros de sintaxe precocemente. Passe `--shellcheck` ou `--pyflakes` para análise de script mais profunda, ou aponte-o para arquivos específicos com `--dir`.

Outros destaques:

- **Herança de `engine.mcp.tool-timeout` em fluxo de trabalho compartilhado** ([#30634](https://github.com/github/gh-aw/issues/30634)): Fluxos de trabalho compartilhados que encapsulam servidores MCP lentos agora podem declarar valores de timeout uma vez e fazer com que os consumidores os herdem automaticamente — chega de duplicar `engine.mcp.tool-timeout` em cada fluxo de trabalho downstream.
- **Skill de agente de codificação de primeira parte** ([#27259](https://github.com/github/gh-aw/issues/27259)): Copilot, Claude e outros agentes de codificação agora obtêm orientação estruturada sobre criação, depuração e atualização de fluxos de trabalho agentic via uma skill de roteador enviada com `gh aw`.
- **`&&` preservado em expressões compiladas** ([#30695](https://github.com/github/gh-aw/issues/30695)): Um bug de escape de HTML em Go estava silenciosamente transformando `&&` em `\u0026\u0026` dentro de arquivos `.lock.yml`, corrompendo expressões `${{ ... && ... }}`. Corrigido.

### [v0.72.0](https://github.com/github/gh-aw/releases/tag/v0.72.0) — 6 de maio

Sub-agentes em linha agora estão como **padrão-ligado** — o flag `features.inline-agents: true` está descontinuado. Rode `gh aw fix --write` para removê-lo automaticamente de fluxos de trabalho existentes via o novo codemod `features-inline-agents-removal`.

Este lançamento também corrigiu uma falha de reexecução de `push_to_pull_request_branch` relatada pela comunidade: quando um agente rodava novamente e seu patch reintroduzia um arquivo já no branch, `git am --3way` produzia um conflito de adição/adição insolúvel. A correção detecta conflitos de adição/adição e os resolve automaticamente assumindo o lado do patch.

### [v0.71.6](https://github.com/github/gh-aw/releases/tag/v0.71.6) e [v0.71.5](https://github.com/github/gh-aw/releases/tag/v0.71.5) — 5–6 de maio

Estes lançamentos de patch endereçaram a estabilidade do mecanismo Claude (chega de travamentos no meio da sessão por "Modo rápido indisponível"), corrigiram valores escalares de bloco `engine.env` de múltiplas linhas que compilavam para YAML quebrado, adicionaram renderização de mensagem RPC de gateway nos resumos de passo e mudaram blocos de sub-agente em linha para o alias de modelo `small` por padrão para reduzir custo e latência.

## Pull Requests Notáveis

Além dos lançamentos, vários PRs mesclados esta semana merecem destaque:

- **[Comando `gh aw forecast` (experimental)](https://github.com/github/gh-aw/pull/31377)** — Um novo comando para projetar o uso efetivo de token de fluxo de trabalho antes de rodá-lo. Útil para orçamento e planejamento de capacidade.
- **[Conceder leitura/gravação em `/tmp` ao Claude em fluxos de trabalho sandboxed](https://github.com/github/gh-aw/pull/31357)** — Fluxos de trabalho movidos a mecanismo Claude agora podem ler e gravar em `/tmp` por padrão em ambientes sandboxed, eliminando um ponto de dor comum quando os agentes precisam de espaço temporário de rascunho.
- **[Renomear `rate-limit` → `user-rate-limit` e `max-runs` → `max-runs-per-window`](https://github.com/github/gh-aw/pull/31390)** — Nomes mais claros para campos de configuração de limitação de taxa.
- **[Razões de término de resposta `gen_ai.response.finish_reasons` no OTel](https://github.com/github/gh-aw/pull/31332)** — Spans de agente agora emitem razões de término (ex: `stop`, `length`, `tool_calls`) como um atributo de OpenTelemetry, melhorando dashboards de observabilidade.
- **[Eventos de exceção OTel sintéticos para falhas silenciosas](https://github.com/github/gh-aw/pull/31334)** — Quando um fluxo de trabalho falha, mas o agente não produz saída legível, um evento de exceção sintético agora é emitido para que os rastreamentos ainda exibam a falha.

## 🤖 Agente da Semana: auto-triage-issues

O sentinela incansável do rastreador de issues — lê cada issue aberta e a classifica para que as pessoas certas a vejam, automaticamente, em uma agenda.

Esta semana `auto-triage-issues` rodou **três vezes em rápida sucessão** (9–10 de maio), triando com sucesso duas issues e tropeçando em uma terceira que disparou uma falha — uma pequena cicatriz de batalha que ele usou com dignidade. Em suas execuções bem-sucedidas, ele permaneceu impressionantemente enxuto: nove solicitações de API, ~270 K tokens de entrada extraídos do cache e uma reviravolta de menos de 40 segundos por issue. Ele nunca desperdiça um ciclo de computação que não precisa.

O resumo da execução observou com leve preocupação que `auto-triage-issues` é tão confiável e estreito no uso de suas ferramentas que pode ser "excesso de exagero para agentic" — significando que a automação determinística poderia teoricamente fazer seu trabalho. O fluxo de trabalho parece ter levado essa nota para o lado pessoal e imediatamente triou a próxima issue sem comentários.

💡 **Dica de uso**: Combine `auto-triage-issues` com um fluxo de trabalho de `notificação` ou `discussão` em labels de alta prioridade (como `security` ou `critical`) para que os membros certos da equipe sejam chamados no momento em que um bug crítico ou questão de segurança surgir.

→ [Ver o fluxo de trabalho no GitHub](https://github.com/github/gh-aw/blob/main/.github/workflows/auto-triage-issues.md)

## Experimente

Atualize para a [v0.72.1](https://github.com/github/gh-aw/releases/tag/v0.72.1) hoje — `gh extension upgrade gh-aw` — e experimente os novos comandos `gh aw lint` e o experimental `gh aw forecast`. Como sempre, feedback e contribuições são bem-vindos em [github/gh-aw](https://github.com/github/gh-aw).
