# ADR-0002: Opt-In Explícito para a Permissão GitHub App workflows:write via Campo allow-workflows

**Data**: 11/04/2026
**Status**: Rascunho (Draft)
**Decisores**: pelikhan, Copilot

---

## Parte 1 — Narrativa (Amigável para Humanos)

### Contexto

O sistema de safe-outputs (saídas seguras) do gh-aw gera tokens de GitHub App com escopo restrito para fazer push de alterações em branches de pull request e criar pull requests. Quando a configuração `allowed-files` (arquivos permitidos) atinge caminhos em `.github/workflows/`, o GitHub exige a permissão `workflows:write` no token gerado — uma permissão disponível apenas para GitHub Apps, não para o `GITHUB_TOKEN`. A função `ComputePermissionsForSafeOutputs` do compilador anteriormente não tinha conhecimento desse requisito, deixando os usuários incapazes de fazer push de arquivos de workflow através do safe-outputs sem recorrer a injeções frágeis de `sed` pós-compilação como solução alternativa. A questão era: o compilador deveria inferir automaticamente `workflows:write` a partir dos padrões de `allowed-files` ou exigir um campo de opt-in explícito?

### Decisão

Adicionaremos um campo booleano explícito `allow-workflows` em ambas as configurações de safe-outputs: `create-pull-request` e `push-to-pull-request-branch`. Quando definido como `true`, o compilador adiciona `workflows: write` às permissões do token do GitHub App computadas por `ComputePermissionsForSafeOutputs`. O campo intencionalmente não é inferido automaticamente dos padrões de `allowed-files`, mantendo a permissão elevada visível e auditável na fonte do workflow. A validação em tempo de compilação impõe que `safe-outputs.github-app` esteja configurado (com `app-id` e `private-key` não vazios) sempre que `allow-workflows: true` estiver presente, porque `workflows:write` não pode ser concedida via `GITHUB_TOKEN`.

### Alternativas Consideradas

#### Alternativa 1: Inferir automaticamente workflows:write a partir dos padrões de allowed-files

Detectar em tempo de compilação se algum padrão de `allowed-files` corresponde a um caminho em `.github/workflows/` (ex: `strings.HasPrefix(pattern, ".github/workflows/")`) e adicionar automaticamente `workflows: write` às permissões do token quando tal padrão for encontrado. Isso elimina uma etapa de configuração para o usuário. Foi rejeitada porque faz com que uma permissão elevada, exclusiva para GitHub App, apareça silenciosamente: um revisor lendo um arquivo de workflow não teria indicação de que `workflows:write` está sendo solicitado, a menos que também inspecionasse a lista de `allowed-files` e entendesse as regras de inferência do compilador. O opt-in explícito torna a permissão elevada um fato de primeira classe e auditável na fonte do workflow.

#### Alternativa 2: Conceder workflows:write globalmente para todas as operações de safe-outputs

Sempre incluir `workflows: write` no token do GitHub App do safe-outputs, independentemente de haver ou não push de arquivos de workflow. Isso simplifica o modelo de permissões ao eliminar a configuração por handler. Foi rejeitada porque viola o princípio do privilégio mínimo: a grande maioria das implantações de safe-outputs não faz push de arquivos de workflow, e conceder `workflows:write` a esses tokens expande desnecessariamente o raio de impacto de um comprometimento de token. Permissões com escopo por handler são uma propriedade de segurança deliberada do sistema de safe-outputs.

#### Alternativa 3: Manter a solução alternativa de injeção de sed pós-compilação como o caminho documentado

Documentar a solução alternativa existente (injetar `permission-workflows: write` via `sed` em uma etapa pós-compilação) como a solução oficial para usuários que precisam fazer push de arquivos de workflow. Isso não requer mudanças no compilador. Foi rejeitada porque a injeção via sed é inerentemente frágil, sensível à versão e ignora verificações de segurança em tempo de compilação. Além disso, produz uma saída compilada que diverge do que o compilador geraria a partir da fonte, quebrando a garantia de reprodutibilidade do compilador.

### Consequências

#### Positivas
- A permissão elevada `workflows:write` é explícita e visível na fonte do workflow — revisores de segurança podem vê-la rapidamente sem precisar entender as regras de inferência do compilador.
- A validação em tempo de compilação evita erros de configuração: um workflow com `allow-workflows: true`, mas sem um GitHub App configurado, falha em tempo de compilação com uma mensagem de erro clara, em vez de gerar silenciosamente um workflow quebrado.
- A implementação é consistente com o padrão existente de modo encenado (staged-mode): `allow-workflows: true` não tem efeito quando o handler está no modo encenado, pois esse modo não gera tokens reais.
- Elimina a solução alternativa frágil de `sed` pós-compilação que era o único caminho anterior para fazer push de arquivos de workflow.

#### Negativas
- Os usuários que precisam fazer push de arquivos de workflow devem adicionar um campo extra (`allow-workflows: true`) à sua configuração, mesmo quando a necessidade é óbvia a partir de seus padrões de `allowed-files`. Esta é uma troca de UX deliberada em favor da auditabilidade.
- A função de validação `validateSafeOutputsAllowWorkflows` deve ser chamada explicitamente de `validateWorkflowData` em `compiler.go`. Se futuras funções de validação não forem conectadas da mesma forma, elas serão ignoradas silenciosamente.

#### Neutras
- O campo `allow-workflows` é definido separadamente em cada handler (`create-pull-request` e `push-to-pull-request-branch`), em vez de uma única flag global de safe-outputs. Isso permite controle por handler, mas significa que usuários que visam ambos os handlers devem definir o campo em ambos os lugares.
- O JSON Schema é atualizado para ambos os esquemas de handler, mantendo o ferramental baseado em esquema (validação de IDE, linting) em sincronia com a implementação em Go.

---

## Parte 2 — Especificação Normativa (RFC 2119)

> As palavras-chave **DEVE**, **NÃO DEVE**, **OBRIGATÓRIO**, **DEVERÁ**, **NÃO DEVERÁ**, **DEVERIA**, **NÃO DEVERIA**, **RECOMENDADO**, **PODE** e **OPCIONAL** nesta seção devem ser interpretadas conforme descrito em [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### Computação de Permissão

1. As implementações **DEVEM** adicionar `workflows: write` às permissões do token do GitHub App computadas para um handler de safe-outputs se, e somente se, o campo `allow-workflows` desse handler for `true` e o handler não estiver no modo encenado (staged mode).
2. As implementações **NÃO DEVEM** adicionar `workflows: write` às permissões do token quando `allow-workflows` estiver ausente ou for `false`.
3. As implementações **NÃO DEVEM** adicionar `workflows: write` às permissões do token quando o handler estiver no modo encenado (ou seja, `Staged: true`), mesmo que `allow-workflows: true` esteja definido.
4. As implementações **NÃO DEVEM** inferir a necessidade de `workflows: write` a partir de padrões de `allowed-files` ou qualquer outro sinal implícito — a única fonte autoritativa é o campo explícito `allow-workflows`.

### Validação em Tempo de Compilação

1. As implementações **DEVEM** validar em tempo de compilação que `safe-outputs.github-app` está configurado com um `app-id` e `private-key` não vazios sempre que qualquer handler de safe-outputs tiver `allow-workflows: true`.
2. As implementações **DEVEM** produzir um erro de compilação se `allow-workflows: true` estiver presente sem uma configuração válida de GitHub App.
3. As implementações **DEVERIAM** incluir o(s) nome(s) do(s) handler(s) na mensagem de erro de compilação para ajudar os usuários a identificar qual(is) handler(s) desencadeou(aram) a falha de validação.
4. As implementações **DEVERIAM** incluir um exemplo de configuração na mensagem de erro de compilação mostrando como adicionar uma configuração de GitHub App.

### Esquema e Documentação

1. As implementações **DEVEM** declarar `allow-workflows` como um campo booleano opcional (padrão: `false`) no JSON Schema para ambos os objetos de handler `create-pull-request` e `push-to-pull-request-branch`.
2. As implementações **DEVERIAM** documentar que `allow-workflows` exige um GitHub App e não pode ser usado com o `GITHUB_TOKEN`.

### Conformidade

Uma implementação é considerada em conformidade com este ADR se satisfizer todos os requisitos **DEVE** e **NÃO DEVE** acima. Especificamente: a permissão `workflows: write` é adicionada às permissões do token do GitHub App quando, e somente quando, um handler de safe-outputs ativo (não encenado) possui `allow-workflows: true`, e a compilação falha com um erro claro quando `allow-workflows: true` é definido sem uma configuração válida de GitHub App. A falha em atender a qualquer requisito **DEVE** ou **NÃO DEVE** constitui não conformidade.

---

*Este é um rascunho de ADR gerado pelo fluxo de trabalho [Design Decision Gate](https://github.com/github/gh-aw/actions/runs/24280835716). O autor do PR deve revisar, completar e finalizar este documento antes que o PR possa ser mesclado.*
