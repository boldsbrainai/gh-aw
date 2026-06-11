# ADR-25948: Reações de Integridade Version-Gated para Política MCPG Allow-Only

**Data**: 2026-04-13
**Status**: Rascunho
**Decisores**: lpcox, Copilot (inferido do PR #25948)

---

## Parte 1 — Narrativa (Amigável)

### Contexto

O compilador de workflows gh-aw gera políticas de guard de gateway MCP (MCPG) que controlam quais chamadas de ferramenta os agentes podem fazer. Até agora, a promoção e despromoção de integridade eram determinadas apenas por campos estáticos (`min-integrity`, `repos`) no bloco de política `allow-only`. Uma nova funcionalidade no MCPG v0.2.18 permite sinais de integridade baseados em reação: reações do GitHub (ex.: 👍, ❤️) de mantenedores podem promover ou despromover dinamicamente o nível de integridade do conteúdo, permitindo fluxos de trabalho de aprovação leves e em banda, sem exigir gating separado baseado em labels. Introduzir essa funcionalidade requer estender o compilador de uma forma que seja retrocompatível com workflows existentes e gated para versões do MCPG que a suportem.

### Decisão

Introduziremos uma flag de funcionalidade `integrity-reactions` que os autores dos workflows devem optar explicitamente, combinada com um version gate de semver que garante que a funcionalidade só seja compilada em políticas de guard quando a versão do MCPG configurada for `>= v0.2.18`. Um helper compartilhado `injectIntegrityReactionFields()` centraliza a lógica de injeção e é chamado tanto pelo renderizador MCP (`mcp_renderer_github.go`) quanto pelo construtor de política de proxy DIFC (`compiler_difc_proxy.go`), garantindo comportamento consistente em todos os caminhos de código de política. A versão padrão do MCPG (`v0.2.17`) é deliberadamente inferior à mínima, portanto nenhum workflow existente é afetado sem um opt-in explícito.

### Alternativas Consideradas

#### Alternativa 1: Rollout Incondicional (Sem Flag de Funcionalidade)

Adicionar `endorsement-reactions` e `disapproval-reactions` à política `allow-only` para todos os workflows que já configuram `min-integrity`. Isso não exigiria infraestrutura de flag de funcionalidade, mas alteraria silenciosamente o comportamento de cada workflow existente que usa gating de integridade assim que o MCPG >= v0.2.18 fosse implantado. Campos de reação padrão para arrays vazios no MCPG, então a mudança líquida seria provavelmente benigna, mas o compilador geraria saída diferente para arquivos de workflow inalterados, violando o princípio de que `make recompile` é idempotente sem mudanças no frontmatter. Essa alternativa foi rejeitada porque quebra a garantia de lock-file estável e reprodutível.

#### Alternativa 2: Tipo de Política Separado para Integridade Baseada em Reação

Introduzir uma nova chave de política de nível superior (ex.: `reaction-integrity`) separada do bloco `allow-only` existente, exigindo que os autores dos workflows reestruturem sua política de guard ao adicionar reações. Isso seria uma evolução de esquema mais limpa em isolamento, mas quebraria a unidade conceitual da política de guard (o nível de integridade e as reações pertencem ao mesmo objeto de política no MCPG) e forçaria um churn desnecessário para adotantes que já usam `min-integrity`. Foi rejeitada porque o modelo de dados do MCPG trata reações como campos adicionais dentro do bloco `allow-only` existente, então espelhar essa estrutura no frontmatter é mais natural e menos disruptivo.

#### Alternativa 3: Version Check Inlined no Compilador em vez de Helper

Duplicar a lógica de version-gate de semver inline em cada local de chamada (renderizador MCP e construtor de política de proxy DIFC) em vez de centralizá-la em `mcpgSupportsIntegrityReactions()` e `injectIntegrityReactionFields()`. Isso eliminaria o helper compartilhado, mas espalharia a lógica de comparação de versão e a lógica de injeção de reação por múltiplos arquivos, dificultando a atualização da versão mínima ou a adição de novos campos de reação no futuro. Foi rejeitada porque a lógica de injeção não é trivial (quatro campos opcionais, dois caminhos de código) e a centralização reduz a área de superfície para bugs quando qualquer um dos caminhos de código for alterado posteriormente.

### Consequências

#### Positivas
- Workflows existentes são completamente inalterados — `make recompile` não produz diff a menos que a flag de funcionalidade `integrity-reactions` seja explicitamente habilitada no frontmatter.
- Um único helper `injectIntegrityReactionFields()` garante que tanto o renderizador MCP quanto o construtor de política de proxy DIFC permaneçam sincronizados quando campos de reação são adicionados ou modificados.
- A validação em tempo de compilação (`validateIntegrityReactions()`) captura valores de enum de conteúdo de reação inválidos e pré-requisitos de `min-integrity` ausentes antes de qualquer workflow ser executado.
- O padrão de version-gate é consistente com a decisão `version-gated-no-ask-user-flag` (ADR-25822), reforçando uma convenção de toda a repositório para introduzir funcionalidades específicas de versão do MCPG.

#### Negativas
- Autores de workflow que desejam integridade baseada em reação devem adicionar `features: integrity-reactions: true` E atualizar sua versão do MCPG para `>= v0.2.18` — um opt-in de duas partes que pode causar confusão se apenas uma for configurada (embora erros de validação guiem o autor).
- A assinatura da função `getDIFCProxyPolicyJSON` mudou de `(githubTool any)` para `(githubTool any, data *WorkflowData, gatewayConfig *MCPGatewayRuntimeConfig)`, tornando-a uma API interna ligeiramente mais complexa.
- A chamada `ensureDefaultMCPGatewayConfig(data)` foi movida para mais cedo em `buildStartDIFCProxyStepYAML` para garantir que a config do gateway esteja populada antes da injeção de política — uma dependência de ordenação sutil que mantenedores futuros devem preservar.

#### Neutras
- O conjunto de enum `validReactionContents` corresponde ao enum `ReactionContent` do GraphQL do GitHub no momento da escrita; se o GitHub adicionar novos tipos de reação, o conjunto de validação deve ser atualizado manualmente.
- A string de versão "latest" é tratada como sempre suportando a funcionalidade — uma escolha pragmática que simplifica pipelines de CI que fixam em `latest`, ao custo de semântica de versão ligeiramente mais fraca.
- O esquema JSON (`main_workflow_schema.json`) foi estendido com restrições de enum para os novos campos, fornecendo autocompletar de IDE e validação estática independente da camada de validação Go.

---

## Parte 2 — Especificação Normativa (RFC 2119)

> As palavras-chave **DEVEM**, **NÃO DEVEM**, **OBRIGATÓRIO**, **SHALL**, **SHALL NOT**, **RECOMENDADO**, **MAY** e **OPCIONAL** nesta seção devem ser interpretadas conforme descrito em [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### Flag de Funcionalidade e Version Gate

1. Implementações **NÃO DEVEM** injetar `endorsement-reactions`, `disapproval-reactions`, `disapproval-integrity` ou `endorser-min-integrity` em qualquer política de guard do MCPG a menos que a flag de funcionalidade `integrity-reactions` esteja explicitamente habilitada no frontmatter do workflow.
2. Implementações **NÃO DEVEM** injetar campos de reação se a versão efetiva do MCPG for inferior a `v0.2.18`, mesmo quando a flag de funcionalidade estiver habilitada.
3. Implementações **DEVEM** tratar a string `"latest"` (case-insensitive) como satisfazendo o requisito de versão mínima do MCPG.
4. Implementações **DEVEM** tratar qualquer string de versão do MCPG que não seja semver (exceto `"latest"`) como falha no version gate, padronizando para rejeição conservadora.
5. Implementações **DEVEM** usar `DefaultMCPGatewayVersion` quando nenhuma versão do MCPG for explicitamente configurada, que **DEVE** ser uma versão inferior a `MCPGIntegrityReactionsMinVersion` para preservar a retrocompatibilidade.

### Injeção de Campo de Reação

1. Implementações **DEVEM** injetar campos de reação via helper compartilhado `injectIntegrityReactionFields()` — a injeção inline direta em locais de chamada individuais **NÃO É RECOMENDADA**.
2. `injectIntegrityReactionFields()` **DEVE** ser chamado em todos os caminhos de código de geração de política, incluindo o renderizador MCP (`mcp_renderer_github.go`) e o construtor de política de proxy DIFC (`compiler_difc_proxy.go`).
3. Implementações **DEVEM** injetar campos de reação dentro do mapa de política `allow-only` interno, não no objeto wrapper de política externo.
4. Implementações **DEVEM** chamar `ensureDefaultMCPGatewayConfig(data)` antes de invocar `injectIntegrityReactionFields()` para garantir que a config do gateway não seja nula.

### Validação

1. Implementações **DEVEM** validar que `endorsement-reactions` e `disapproval-reactions` contenham apenas valores do enum `ReactionContent` do GitHub: `THUMBS_UP`, `THUMBS_DOWN`, `HEART`, `HOORAY`, `CONFUSED`, `ROCKET`, `EYES`, `LAUGH`.
2. Implementações **DEVEM** retornar um erro de tempo de compilação se qualquer campo de array de reação for configurado sem a flag de funcionalidade `integrity-reactions`.
3. Implementações **DEVEM** retornar um erro de tempo de compilação se a flag de funcionalidade `integrity-reactions` estiver habilitada, mas a versão do MCPG for inferior a `v0.2.18`.
4. Implementações **DEVEM** retornar um erro de tempo de compilação se `endorsement-reactions` ou `disapproval-reactions` forem configurados sem `min-integrity` ser configurado.
5. Implementações **DEVEM** validar que `disapproval-integrity`, quando configurado, é um de: `"none"`, `"unapproved"`, `"approved"`, `"merged"`.
6. Implementações **DEVEM** validar que `endorser-min-integrity`, quando configurado, é um de: `"unapproved"`, `"approved"`, `"merged"`.

### Esquema

1. O esquema JSON para frontmatter de workflow **DEVE** definir `endorsement-reactions` e `disapproval-reactions` como arrays de strings restringidos aos valores do enum `ReactionContent`.
2. O esquema JSON **DEVE** definir `disapproval-integrity` e `endorser-min-integrity` como strings restringidos aos seus respectivos conjuntos de níveis de integridade válidos.

### Conformidade

Uma implementação é considerada em conformidade com este ADR se satisfizer todos os requisitos **DEVEM** e **NÃO DEVEM** acima. A falha em atender a qualquer requisito **DEVE** ou **NÃO DEVE** constitui não conformidade. Em particular: injetar campos de reação sem a flag de funcionalidade, injetar campos de reação quando a versão do MCPG for inferior a `v0.2.18` ou omitir validação de valores de enum de reação são todos comportamentos não conformes.

---

*ADR criado pelo agente [adr-writer agent]. Revise e finalize antes de alterar o status de Rascunho para Aceito.*
