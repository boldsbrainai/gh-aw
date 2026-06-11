---
title: "Atualização Semanal – 20 de abril de 2026"
description: "Esta semana traz cinco lançamentos repletos de um novo mecanismo OpenCode, passos pré-agente, endurecimento de segurança da cache-memory e muito mais."
authors:
  - copilot
date: 2026-04-20
---

Que semana para [github/gh-aw](https://github.com/github/gh-aw)! Cinco lançamentos ocorreram entre 13 e 17 de abril, entregando um novo mecanismo de I.A., melhorias importantes de segurança e uma onda de correções de confiabilidade. Aqui está o que você precisa saber.

## Destaques do Lançamento

### [v0.68.7](https://github.com/github/gh-aw/releases/tag/v0.68.7) — 17 de abril

Um lançamento de correção e polimento com uma nova adição de destaque:

- **Suporte a string única para `on.roles`** ([#26789](https://github.com/github/gh-aw/pull/26789)): Agora você pode escrever `roles: write` em vez de `roles: [write]`. Anteriormente, isso produzia um erro confuso do compilador — agora simplesmente funciona.
- **Correção de chroot do Codex** ([#26787](https://github.com/github/gh-aw/pull/26787)): Fluxos de trabalho do Codex em sistemas de arquivos restritos falhavam silenciosamente. O estado de tempo de execução agora reside em `/tmp`, onde realmente pode ser gravado.
- **Verificações de compatibilidade cross-repo** ([#26802](https://github.com/github/gh-aw/pull/26802)): Um novo fluxo de trabalho diário do Claude descobre automaticamente repositórios usando gh-aw e executa verificações de compilação em relação ao build mais recente. Regressões de compatibilidade agora são detectadas antes de chegarem aos usuários.

### [v0.68.6](https://github.com/github/gh-aw/releases/tag/v0.68.6) — 17 de abril

O lançamento de destaque da semana, com um mecanismo totalmente novo e melhorias importantes de segurança:

- **Mecanismo OpenCode** — Defina `engine: opencode` para usar [OpenCode](https://opencode.ai) como seu mecanismo agentic, juntando-se ao Copilot, Claude e Codex como opções de primeira classe.
- **Modo `engine.bare`** — Defina `engine.bare: true` para pular o carregamento de `AGENTS.md`. Perfeito para triagem, relatórios e fluxos de trabalho de ops onde o contexto do código do repositório apenas adiciona ruído.
- **Passos pré-agente** — O novo campo de frontmatter `pre-agent-steps` permite que você execute passos personalizados de GitHub Actions antes que o agente de I.A. comece — ótimo para autenticação, configuração de ambiente ou qualquer trabalho pré-requisito.
- **Sanitização da árvore de trabalho do `cache-memory`** — Antes de cada execução do agente, a árvore de trabalho agora é escaneada e limpa de executáveis plantados e arquivos não permitidos da memória cache. Isso fecha um vetor real de ataque à cadeia de suprimentos.

### [v0.68.5](https://github.com/github/gh-aw/releases/tag/v0.68.5) — 16 de abril

Melhorias de qualidade de vida e mais endurecimento de segurança:

- **Configuração de MCP em `.github/mcp.json`** ([#26665](https://github.com/github/gh-aw/pull/26665)): O arquivo de configuração MCP mudou de `.mcp.json` (raiz do repositório) para `.github/mcp.json`, alinhando-se com as convenções padrão de configuração do GitHub. O fluxo `init` cria o novo caminho automaticamente.
- **Bundle de importação `shared/reporting-otlp.md`** ([#26655](https://github.com/github/gh-aw/pull/26655)): Um import agora substitui dois para fluxos de trabalho de relatórios com telemetria habilitada.
- **Segredos em nível de ambiente corrigidos** ([#26650](https://github.com/github/gh-aw/pull/26650)): O campo de frontmatter `environment:` agora propaga corretamente para o job de ativação.

### [v0.68.4](https://github.com/github/gh-aw/releases/tag/v0.68.4) — 16 de abril

Um patch substancial resolvendo 21 problemas relatados pela comunidade:

- **Modo BYOK Copilot** ([#26544](https://github.com/github/gh-aw/pull/26544)): Novo sinalizador de recurso `byok-copilot` conecta suporte ao Copilot offline.
- **Fluxo de trabalho de manutenção SideRepoOps** ([#26382](https://github.com/github/gh-aw/pull/26382)): O compilador agora gera automaticamente `agentics-maintenance.yml` para repositórios alvo em padrões SideRepoOps.
- **Servidores MCP como CLIs locais** ([#25928](https://github.com/github/gh-aw/pull/25928)): Servidores MCP agora podem ser montados como comandos CLI locais após o gateway iniciar, permitindo integrações de ferramentas mais ricas.

### [v0.68.3](https://github.com/github/gh-aw/releases/tag/v0.68.3) — 14 de abril

Melhorias de observabilidade e confiabilidade:

- **Detecção de modelo não suportado** ([#26229](https://github.com/github/gh-aw/pull/26229)): Quando um modelo está indisponível para seu plano, o fluxo de trabalho agora para de tentar novamente e exibe um erro claro em vez de girar indefinidamente.
- **Métrica Tempo Entre Turnos (TBT)** ([#26321](https://github.com/github/gh-aw/pull/26321)): `gh aw audit` e `gh aw logs` agora relatam TBT — um indicador chave se o cache de prompt de LLM está funcionando para seus fluxos de trabalho.
- **Campos `env` e `checkout` em imports compartilhados** ([#26113](https://github.com/github/gh-aw/pull/26113), [#26292](https://github.com/github/gh-aw/pull/26292)): Fluxos de trabalho importáveis compartilhados agora suportam campos `env:` e `checkout:`, eliminando soluções alternativas comuns.

## 🤖 Agente da Semana: auto-triage-issues

O sentinela incansável do rastreador de issues — lê cada issue aberta e a classifica para que as pessoas certas a vejam, automaticamente, em uma agenda.

Esta semana `auto-triage-issues` rodou **três vezes em um único dia** (apenas em 27 de abril), escanear fielmente em busca de issues não triadas a cada vez de forma agendada. Em suas execuções, ele teve uma média de apenas 4-6 turnos por execução, mantendo as coisas enxutas enquanto ainda fazia 6 chamadas de API do GitHub por execução. O fluxo de trabalho até melhorou sua própria eficiência no meio do dia — caindo de 6 turnos na execução da manhã para 4 turnos à tarde, aparentemente aprendendo a chegar ao ponto mais rápido. As métricas de observabilidade notaram educadamente que ele poderia ser "parcialmente redutível à automação determinística", mas, honestamente, onde está a diversão nisso?

Uma de suas execuções ganhou uma menção honrosa do sistema de avaliação agentic: "Esta execução de Triagem parece estável o suficiente para que a automação determinística possa ser um ajuste mais simples." O fluxo de trabalho respondeu rodando novamente uma hora depois, exatamente da mesma forma que antes. Icônico.

💡 **Dica de uso**: Combine `auto-triage-issues` com um fluxo de trabalho de notificação baseado em label para que os membros certos da equipe sejam chamados no momento em que uma nova issue for categorizada.

→ [Ver o fluxo de trabalho no GitHub](https://github.com/github/gh-aw/blob/main/.github/workflows/auto-triage-issues.md)

## Experimente

Atualize para a [v0.68.7](https://github.com/github/gh-aw/releases/tag/v0.68.7) hoje e confira todas as correções. Feedback e contribuições são muito bem-vindos em [github/gh-aw](https://github.com/github/gh-aw).
