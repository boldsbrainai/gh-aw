---
title: "Atualização Semanal – 18 de março de 2026"
description: "Sete versões em sete dias: revisão da política de proteção, novos gatilhos, melhorias no GHE e uma dose saudável de correções de qualidade de vida."
authors:
  - copilot
date: 2026-03-18
---

Tem sido uma semana movimentada em [github/gh-aw](https://github.com/github/gh-aw) — sete versões lançadas entre 13 e 17 de março, cobrindo tudo, desde uma revisão do modelo de segurança até um novo gatilho baseado em label e uma correção de redimensionamento de terminal que já deveria ter sido feita. Vamos analisar.

## Lançamentos desta Semana

### [v0.61.0](https://github.com/github/gh-aw/releases/tag/v0.61.0) — 17 de março

A versão mais recente foca em confiabilidade e experiência do desenvolvedor:

- **Registro automático de depuração** ([#21406](https://github.com/github/gh-aw/pull/21406)): Defina `ACTIONS_RUNNER_DEBUG=true` no seu runner e o registro completo de depuração será ativado automaticamente — não é mais necessário adicionar `DEBUG=*` manualmente a cada execução de solução de problemas.
- **Atualizações de itens de projeto cross-repo** ([#21404](https://github.com/github/gh-aw/pull/21404)): `update_project` agora aceita um parâmetro `target_repo`, para que quadros de projeto em nível de organização possam atualizar campos em itens de qualquer repositório.
- **Suporte à residência de dados do GHE Cloud** ([#21408](https://github.com/github/gh-aw/pull/21408)): Fluxos de trabalho compilados agora auto-injetam um passo `GH_HOST`, corrigindo falhas da CLI `gh` em instâncias `*.ghe.com`.
- **Artefatos de build de CI** ([#21440](https://github.com/github/gh-aw/pull/21440)): O job de CI `build` agora faz upload do binário compilado `gh-aw` como um artefato baixável — útil para testar PRs sem um build local.

### [v0.60.0](https://github.com/github/gh-aw/releases/tag/v0.60.0) — 17 de março

Este lançamento reconfigura o modelo de segurança. **Mudança importante (breaking change)**: a configuração automática `lockdown=true` não existe mais. Em vez disso, o tempo de execução agora auto-configura políticas de proteção no servidor MCP do GitHub — `min_integrity=approved` para repos públicos, `min_integrity=none` para privados/internos. Remova qualquer `lockdown: false` explícito do seu frontmatter; não é mais necessário.

Outros destaques:

- **Auto-permissão de domínios GHES** ([#21301](https://github.com/github/gh-aw/pull/21301)): Quando `engine.api-target` aponta para uma instância GHES, o compilador adiciona automaticamente os hostnames da API GHES ao firewall. Sem mais bloqueios silenciosos após cada recompilação.
- **Auth `github-app:` em dependências APM** ([#21286](https://github.com/github/gh-aw/pull/21286)): `dependencies:` do APM agora podem usar auth `github-app:` para acesso a pacotes privados cross-org.

### [v0.59.0](https://github.com/github/gh-aw/releases/tag/v0.59.0) — 16 de março

Um lançamento repleto de recursos com duas mudanças importantes (renomeação de campos em `safe-outputs.allowed-domains`) e várias novas capacidades:

- **Gatilho de Comando de Label** ([#21118](https://github.com/github/gh-aw/pull/21118)): Ative um fluxo de trabalho adicionando um label a uma issue, PR ou discussão. O label é removido automaticamente para que possa ser reaplicado para disparar novamente.
- **Comando `gh aw domains`** ([#21086](https://github.com/github/gh-aw/pull/21086)): Inspecione a configuração efetiva de domínios de rede para todos os seus fluxos de trabalho, com anotações de ecossistema por domínio.
- **Injeção de passo de pré-ativação** — Novos campos de frontmatter `on.steps` e `on.permissions` permitem que você injete passos e permissões personalizados no job de ativação para cenários avançados.

### Anteriormente na Semana

- [v0.58.3](https://github.com/github/gh-aw/releases/tag/v0.58.3) (15 de março): Política de proteção de sink de escrita MCP para servidores MCP não GitHub, diagnóstico de pré-voo do Copilot para GHES e um resumo de passo de detalhes de execução mais rico.
- [v0.58.2](https://github.com/github/gh-aw/releases/tag/v0.58.2) (14 de março): Autodetecção GHES em `audit` e `add-wizard`, suporte a `excluded-files` para `create-pull-request` e erros de comando `run` mais claros.
- [v0.58.1](https://github.com/github/gh-aw/releases/tag/v0.58.1) / [v0.58.0](https://github.com/github/gh-aw/releases/tag/v0.58.0) (13 de março): Safe output `call-workflow` para encadear fluxos de trabalho, `checkout: false` para jobs de agente, endpoints de API OpenAI/Anthropic personalizados e 92 PRs mesclados somente na v0.58.0.

## Pull Requests Notáveis

- **[Fallback de `github-app` de nível superior](https://github.com/github/gh-aw/pull/21510)** ([#21510](https://github.com/github/gh-aw/pull/21510)): Defina sua configuração de GitHub App uma vez no nível superior e deixe-a propagar para safe-outputs, checkout, MCP, APM e ativação — em vez de repeti-la em cada seção.
- **[Escopos de permissão apenas para GitHub App](https://github.com/github/gh-aw/pull/21511)** ([#21511](https://github.com/github/gh-aw/pull/21511)): 31 novas constantes `PermissionScope` cobrem permissões de GitHub App em nível de repositório, org e usuário (ex: `administration`, `members`, `environments`).
- **[Tema Huh personalizado](https://github.com/github/gh-aw/pull/21557)** ([#21557](https://github.com/github/gh-aw/pull/21557)): Todos os 11 formulários CLI interativos agora usam um tema inspirado em Dracula, consistente com o resto da identidade visual da CLI.
- **[Fluxo de trabalho de redator de postagem de blog semanal](https://github.com/github/gh-aw/pull/21575)** ([#21575](https://github.com/github/gh-aw/pull/21575)): Sim, o fluxo de trabalho que escreveu este post foi ele mesmo mesclado esta semana. Meta!
- **[Limites de tempo para job de CI](https://github.com/github/gh-aw/pull/21601)** ([#21601](https://github.com/github/gh-aw/pull/21601)): Todos os 25 jobs de CI que dependiam do padrão de 6 horas do GitHub agora têm limites de tempo explícitos, evitando que um teste travado queime silenciosamente a computação do runner.

## 🤖 Agente da Semana: auto-triage-issues

O primeiro Agente da Semana vai para o fluxo de trabalho que lida com o trabalho inglório, mas essencial, de evitar que o rastreador de issues se torne um pântano.

`auto-triage-issues` roda em uma agenda e dispara em cada nova issue, lendo cada uma e decidindo como categorizá-la. Esta semana rodou cinco vezes — três execuções bem-sucedidas e duas que foram disparadas por eventos de push em um branch de recurso (que aparentemente disparam o fluxo de trabalho, mas não lhe dão muito com o que trabalhar). Em sua execução agendada desta manhã, não encontrou nenhuma issue aberta no repositório, então criou uma discussão de resumo organizada para anunciar o estado limpo, conforme instruído. Em uma execução anterior disparada por issues, tentou triar a issue [#21572](https://github.com/github/gh-aw/pull/21572), mas obteve resultados vazios das ferramentas MCP do GitHub em todas as três tentativas de leitura — então ele graciosamente chamou `missing_data` e seguiu em frente em vez de alucinar um label.

Em suas execuções recentes, fez 131 chamadas de `search_repositories`. Não temos certeza de por que ele acha as buscas de repositório tão atraentes, mas claramente ele é muito minucioso em conhecer sua vizinhança antes de tomar qualquer decisão.

💡 **Dica de uso**: Combine `auto-triage-issues` com um fluxo de trabalho de notificação em labels específicos (ex: `security` ou `needs-repro`) para que as pessoas certas sejam pingadas automaticamente sem que ninguém precise assistir à caixa de entrada.

→ [Ver o fluxo de trabalho no GitHub](https://github.com/github/gh-aw/blob/main/.github/workflows/auto-triage-issues.md)

## Experimente

Atualize para a [v0.61.0](https://github.com/github/gh-aw/releases/tag/v0.61.0) para obter todas as melhorias desta semana movimentada. Se você roda fluxos de trabalho no GHES ou no GHE Cloud, os novos recursos de autodetecção e injeção de `GH_HOST` valem especialmente a pena tentar. Como sempre, contribuições e feedback são bem-vindos em [github/gh-aw](https://github.com/github/gh-aw).
