# ADR-26137: Propagar on.github-token para os Passos de Checkout e Hash Check do Lock File na Ativação

**Data**: 2026-04-14
**Status**: Rascunho
**Decisores**: pelikhan, Copilot

---

## Parte 1 — Narrativa (Amigável)

### Contexto

O compilador gh-aw gera um job de ativação que inclui vários passos usando credenciais da API do GitHub: um passo de reação, um passo de adicionar comentário, um passo de remoção de label, um passo de checkout esparso `.github/.agents` e um passo de "Verificar arquivo de lock do workflow" (hash check). O campo de frontmatter `on.github-token` já estava conectado aos passos de reação, comentário e remoção de label via `resolveActivationToken(data)`. No entanto, o passo de checkout esparso e o passo de hash check do arquivo de lock ainda usavam o `GITHUB_TOKEN` padrão do executor. Em cenários de `workflow_call` entre organizações (cross-org)—onde um workflow chamador em uma organização do GitHub invoca um workflow chamado em uma organização diferente—o `GITHUB_TOKEN` padrão não consegue acessar o conteúdo ou APIs do repositório chamado. Isso faz com que o passo de checkout falhe silenciosamente e a API de hash check retorne HTTP 404, produzindo um erro falso-positivo `ERR_CONFIG: Lock file is outdated or unverifiable`.

### Decisão

Adicionaremos um parâmetro `token string` a `GenerateGitHubFolderCheckoutStep()` e propagaremos o token de ativação resolvido—obtido via `resolveActivationToken(data)`—tanto para o passo de checkout esparso quanto para o passo de verificação de hash do arquivo de lock no job de ativação. Quando o token estiver vazio ou igual à string literal `${{ secrets.GITHUB_TOKEN }}`, nenhum campo `token:` ou `github-token:` será emitido (preservando o comportamento de token padrão para cenários da mesma organização). Este padrão é consistente com a abordagem existente usada para os passos de reação, comentário e remoção de label.

### Alternativas Consideradas

#### Alternativa 1: Sempre emitir o campo token (mesmo para o GITHUB_TOKEN padrão)

Emitir `token: ${{ secrets.GITHUB_TOKEN }}` incondicionalmente no passo de checkout e `github-token: ${{ secrets.GITHUB_TOKEN }}` no passo de hash check. Isso foi considerado porque tornaria a origem da credencial explícita em todos os YAMLs gerados. Foi rejeitada porque cria verbosidade desnecessária no YAML do workflow gerado para o caso comum da mesma organização, e porque tornar o default explícito pode mascarar erro de configuração (se um consumidor acidentalmente configurar `on.github-token` para a referência de segredo padrão, o YAML emitido ainda seria indistinguível da referência de token pretendida entre organizações).

#### Alternativa 2: Criar geradores de passo de checkout separados para cenários cross-org vs. same-org

Introduzir uma nova função (ex.: `GenerateCrossOrgGitHubFolderCheckoutStep`) que sempre emite um campo `token:`, e manter a função existente inalterada para uso na mesma organização. Foi considerada porque evita adicionar um parâmetro a uma API existente. Foi rejeitada porque duplica a lógica de geração de passo de checkout, aumentando a carga de manutenção, e porque os chamadores de `generateCheckoutGitHubFolderForActivation` ainda precisariam decidir qual variante chamar com base na mesma saída de `resolveActivationToken`—tornando a escolha implícita em vez de explícita.

#### Alternativa 3: Resolver o token no CallerSite dentro de generateCheckoutGitHubFolderForActivation apenas (não no hash check)

Aplicar a propagação de token apenas ao passo de checkout sem alterar o passo de hash check. Isso foi considerado como uma mudança mínima. Foi rejeitada porque deixa o passo de hash check vulnerável à mesma falha 404 entre organizações que a correção de checkout resolve. Ambos os passos exigem acesso à API do repositório chamado, e a correção deve ser aplicada consistentemente.

### Consequências

#### Positivas
- Cenários de `workflow_call` entre organizações usam corretamente o token configurado tanto para o checkout esparso quanto para o hash check do arquivo de lock, eliminando erros falsos-positivos de verificação de arquivo de lock.
- A propagação de token agora é consistente em todos os passos do job de ativação que acessam o conteúdo do repositório ou a API do GitHub.
- A convenção (string vazia ou `${{ secrets.GITHUB_TOKEN }}` → nenhum campo de token emitido) é imposta em um único local em `GenerateGitHubFolderCheckoutStep()`, facilitando a auditoria.

#### Negativas
- `GenerateGitHubFolderCheckoutStep()` é uma mudança de API que quebra a compatibilidade: todos os chamadores existentes devem ser atualizados para passar um argumento de token explícito (tipicamente `""` para o padrão). Isso cria churn nos locais de chamada e testes.
- A regra de supressão (`token == "" || token == "${{ secrets.GITHUB_TOKEN }}"`) codifica o conhecimento de uma string de expressão específica do GitHub Actions como um sentinela especial, o que é frágil se o formato da expressão mudar algum dia.

#### Neutras
- O YAML do workflow de lock gerado (`.github/workflows/smoke-copilot.lock.yml`) é atualizado para passar explicitamente o token do segredo equivalente ao `on.github-token`, mantendo os workflows gerados e mantidos manualmente consistentes.
- Testes existentes para `GenerateGitHubFolderCheckoutStep` exigem atualizações de assinatura (passando `""` para o novo parâmetro de token), mas suas asserções permanecem inalteradas para comportamento na mesma organização.

---

## Parte 2 — Especificação Normativa (RFC 2119)

> As palavras-chave **DEVEM**, **NÃO DEVEM**, **OBRIGATÓRIO**, **SHALL**, **SHALL NOT**, **RECOMENDADO**, **MAY** e **OPCIONAL** nesta seção devem ser interpretadas conforme descrito em [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### Parâmetro de Token em GenerateGitHubFolderCheckoutStep

1. `GenerateGitHubFolderCheckoutStep` **DEVE** aceitar um parâmetro `token string` após o parâmetro `ref` e antes da função `getActionPin`.
2. Implementações **DEVEM** emitir um campo YAML `token:` no passo de checkout se e somente se `token` for não vazio e não for igual à string literal `${{ secrets.GITHUB_TOKEN }}`.
3. Implementações **NÃO DEVEM** emitir um campo `token:` quando `token` for a string vazia `""`.
4. Implementações **NÃO DEVEM** emitir um campo `token:` quando `token` for exatamente `${{ secrets.GITHUB_TOKEN }}`.
5. Chamadores **DEVEM** passar um valor de token explícito; passar um valor não vazio que não seja `${{ secrets.GITHUB_TOKEN }}` **SHALL** resultar na inclusão do token no YAML gerado.

### Propagação de Token no Compilador do Job de Ativação

1. O compilador do job de ativação **DEVE** chamar `resolveActivationToken(data)` uma vez por construção de job de ativação e reutilizar o resultado para todos os passos que exigem acesso de credencial.
2. O token de ativação resolvido **DEVE** ser passado para `GenerateGitHubFolderCheckoutStep()` para o passo de checkout esparso `.github/.agents`.
3. O passo "Verificar arquivo de lock do workflow" **DEVE** emitir um campo `github-token:` usando o token de ativação resolvido se e somente se esse token não for igual a `${{ secrets.GITHUB_TOKEN }}`.
4. O padrão de propagação de token para o passo de checkout e passo de hash check **DEVE** permanecer consistente com o padrão de propagação para os passos de reação, comentário e remoção de label.

### Conformidade

Uma implementação é considerada em conformidade com este ADR se satisfizer todos os requisitos **DEVEM** e **NÃO DEVEM** acima. A falha em atender a qualquer requisito **DEVE** ou **NÃO DEVE** constitui não conformidade.

---

*Este é um ADR de RASCUNHO gerado pelo workflow [Design Decision Gate](https://github.com/github/gh-aw/actions/runs/24376710842). O autor do PR deve revisar, completar e finalizar este documento antes que o PR possa ser mesclado.*
