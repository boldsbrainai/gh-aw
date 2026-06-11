---
title: "Atualização Semanal – 13 de abril de 2026"
description: "Cinco lançamentos esta semana: controle de contexto engine.bare, uma correção crítica da CLI do Copilot, rastreamento distribuído cross-job e uma onda de endurecimento de segurança."
authors:
  - copilot
date: 2026-04-13
---

Foi uma semana movimentada em [github/gh-aw](https://github.com/github/gh-aw) — cinco lançamentos entre 6 e 10 de abril, abordando tudo, desde uma crise crítica de confiabilidade da CLI do Copilot até novos recursos brilhantes de composição de fluxo de trabalho. Aqui está o resumo completo.

## Destaques do Lançamento

### [v0.68.1](https://github.com/github/gh-aw/releases/tag/v0.68.1) — 10 de abril

O destaque deste patch é uma **correção crítica de confiabilidade da CLI do Copilot**. Fluxos de trabalho usando o mecanismo Copilot travavam indefinidamente ou produziam saída de zero byte devido a uma incompatibilidade introduzida na v1.0.22 da CLI do Copilot. [v0.68.1](https://github.com/github/gh-aw/releases/tag/v0.68.1) fixa a CLI de volta na v1.0.21 — a última versão confirmada como funcional — e coloca os fluxos de trabalho de todos funcionando novamente ([#25689](https://github.com/github/gh-aw/pull/25689)).

Além da correção, este lançamento também envia:

- **Campo de frontmatter `engine.bare`** ([#25661](https://github.com/github/gh-aw/pull/25661)): Defina `bare: true` para suprimir o carregamento automático de contexto — `AGENTS.md` e instruções do usuário para o Copilot, arquivos de memória `CLAUDE.md` para o Claude. Ótimo quando você quer que a I.A. comece do zero.
- **Diagnósticos melhorados de arquivo de trava obsoleto** ([#25571](https://github.com/github/gh-aw/pull/25571)): Quando o job de ativação detecta um hash obsoleto, ele agora emite linhas de log `[hash-debug]` passo a passo e abre uma issue acionável orientando você a corrigi-lo.
- **`actions/github-script` atualizado para v9** ([#25553](https://github.com/github/gh-aw/pull/25553)): Scripts agora recebem `getOctokit` como um parâmetro de contexto nativo, removendo a necessidade de imports manuais `@actions/github` em manipuladores de safe-output.
- **Fallback de squash-merge em `gh aw add`** ([#25609](https://github.com/github/gh-aw/pull/25609)): Se um repositório não permitir merge commits, o PR de setup agora usa squash merge automaticamente em vez de falhar.
- **Segurança: Permissões de `agent-stdio.log` endurecidas** — Arquivos de log agora são pré-criados com permissões `0600` antes de o `tee` escrever, evitando a exposição de tokens bearer do gateway MCP para leitura mundial.

### [v0.68.0](https://github.com/github/gh-aw/releases/tag/v0.68.0) — 10 de abril

Este lançamento traz melhorias de [rastreamento distribuído](https://github.com/github/gh-aw/releases/tag/v0.68.0) e uma API de comentários mais limpa:

- **Hierarquia de trace OpenTelemetry cross-job** ([#25540](https://github.com/github/gh-aw/pull/25540)): IDs de span pai agora propagam através de `aw_context` entre jobs, dando a você visibilidade de trace distribuído de ponta a ponta para fluxos de trabalho de múltiplos jobs em backends como Tempo, Honeycomb e Datadog.
- **API de comentários de discussão simplificada** ([#25532](https://github.com/github/gh-aw/pull/25532)): O booleano `add-comment.discussion` (descontinuado) foi removido em favor da sintaxe `discussions: true/false` mais clara. Rode `gh aw fix --write` para migrar fluxos de trabalho existentes.
- **Segurança: validação de conteúdo heredoc** ([#25510](https://github.com/github/gh-aw/pull/25510)): As verificações de `ValidateHeredocContent` agora cobrem cinco locais de inserção de heredoc controlados pelo usuário, fechando uma classe de vetores de injeção em potencial.

### [v0.67.4](https://github.com/github/gh-aw/releases/tag/v0.67.4) — 9 de abril

Este liderou com **cinco novos templates de fluxo de trabalho agentic**: [approach-validator](https://github.com/github/gh-aw/pull/25354), [test-quality-sentinel](https://github.com/github/gh-aw/pull/25353), [refactoring-cadence](https://github.com/github/gh-aw/pull/25352), [architecture-guardian](https://github.com/github/gh-aw/pull/25334) e [design-decision-gate](https://github.com/github/gh-aw/pull/25323). Eles expandem a biblioteca nativa para qualidade de código, aplicação de ADR e governança arquitetural. O lançamento também incluiu lógica de tentativa do driver Copilot e um flag de compilação `--runner-guard`.

### [v0.67.3](https://github.com/github/gh-aw/releases/tag/v0.67.3) — 8 de abril

A estrela deste lançamento é o novo **campo de frontmatter `pre-steps`** — injete passos que rodam _antes_ do checkout e do agente dentro do mesmo job. Este é o padrão recomendado para ações de criação de token (ex: `actions/create-github-app-token`, `octo-sts`) que precisam fazer checkout de repos externos. Como o token criado permanece no mesmo job, ele nunca é mascarado ao cruzar um limite de job. Também enviado: suporte à expressão `${{ github.aw.import-inputs.* }}` na seção `imports:`, e suporte a `assignees` em issues de fallback de `create-pull-request`.

### [v0.67.2](https://github.com/github/gh-aw/releases/tag/v0.67.2) — 6 de abril

Focado em confiabilidade: verificações de hash de fluxo de trabalho cross-repo, tokens de checkout não mais descartados silenciosamente em runners mais novos, invocações com flags `curl`/`wget` agora permitidas em fluxos de trabalho `network.allowed` e um limite de esquema `timeout-minutes` em 360.

## Pull Requests Notáveis

Além dos lançamentos, a última semana também entregou:

- **[#25923](https://github.com/github/gh-aw/pull/25923)**: Artefatos de imagem agora podem ser enviados sem arquivamento zip usando `skip-archive: true`, e as URLs de artefato resultantes são exibidas como saídas — permitindo que fluxos de trabalho incorporem imagens diretamente em comentários Markdown.
- **[#25908](https://github.com/github/gh-aw/pull/25908)**: Um job agendado `cleanup-cache-memory` foi adicionado ao fluxo de trabalho de manutenção de agentics para podar entradas de cache-memory obsoletas automaticamente (e pode ser disparado sob demanda).
- **[#25914](https://github.com/github/gh-aw/pull/25914) + [#25972](https://github.com/github/gh-aw/pull/25972)**: Eventos de span de exceção OTel agora emitem `exception.type` junto com `exception.message` e atributos de erro individuais são consultáveis — chega de vasculhar strings delimitadas por pipe no Grafana.
- **[#25960](https://github.com/github/gh-aw/pull/25960)**: Corrigido um bug sorrateiro onde `push_repo_memory` rodava em cada no-op disparado por bot porque `always()` ignorava a propagação de skip.
- **[#25971](https://github.com/github/gh-aw/pull/25971)**: A saída bruta do subprocesso de `gh aw compile --validate` agora é sanitizada antes de ser incorporada aos corpos das issues, fechando um vetor de injeção de Markdown.

## 🤖 Agente da Semana: auto-triage-issues

A espinha dorsal silenciosa da higiene de issues — lê cada nova issue no momento em que ela é aberta e descobre a quem ela pertence.

Esta semana `auto-triage-issues` provou que está fazendo seu trabalho quase bem demais. Na execução agendada em 13 de abril, ele escaneou todas as issues abertas e encontrou exatamente **zero** issues sem label — relatando uma taxa de cobertura de label de 100% sem necessidade de ação. Ele já havia lidado com a rotulagem em tempo quase real à medida que as issues chegavam, incluindo uma execução em 12 de abril onde rotulou corretamente uma issue recém-aberta com `enhancement`, `mcp`, `compiler` e `security` em uma única passada. Quatro labels, zero hesitação.

Esse label "security" está trabalhando muito — o fluxo de trabalho notou preocupações com MCP e compilador que realmente mereciam o label, não apenas combinou palavras-chave nele. Aceitamos.

💡 **Dica de uso**: Combine `auto-triage-issues` com regras de notificação baseadas em label (ex: `security` ou `needs-repro`) para que as pessoas certas sejam pingadas automaticamente sem que ninguém precise assistir ao rastreador de issues.

→ [Ver o fluxo de trabalho no GitHub](https://github.com/github/gh-aw/blob/main/.github/workflows/auto-triage-issues.md)

## Experimente

Atualize para a [v0.68.1](https://github.com/github/gh-aw/releases/tag/v0.68.1) hoje para obter a correção da CLI do Copilot e o novo controle `engine.bare`. Como sempre, contribuições e feedback são bem-vindos em [github/gh-aw](https://github.com/github/gh-aw).
