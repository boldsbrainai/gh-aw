# ADR-0001: Encaminhamento Condicional de Variáveis de Ambiente OIDC para o Contêiner do Gateway MCP

**Data**: 11/04/2026
**Status**: Rascunho (Draft)
**Decisores**: pelikhan, Copilot

---

## Parte 1 — Narrativa (Amigável para Humanos)

### Contexto

O compilador gh-aw gera um comando `docker run` que inicia o contêiner do Gateway MCP. O runner hospedeiro do GitHub Actions possui as variáveis de endpoint do token OIDC (`ACTIONS_ID_TOKEN_REQUEST_URL` e `ACTIONS_ID_TOKEN_REQUEST_TOKEN`) disponíveis em seu ambiente. A camada de firewall (gh-aw-firewall#1796) foi corrigida anteriormente para encaminhar essas variáveis para o contêiner do agente, mas o segundo salto — do contêiner do agente para o contêiner do Gateway MCP — nunca foi conectado. Como resultado, os servidores MCP HTTP que exigem autenticação GitHub OIDC (`auth.type: "github-oidc"`) falham ao gerar tokens porque o gateway não consegue alcançar o endpoint OIDC. Essas duas variáveis só têm significado quando pelo menos um servidor MCP HTTP configurado utiliza autenticação OIDC; encaminhá-las incondicionalmente exporia o endpoint do token desnecessariamente.

### Decisão

Detectaremos se algum servidor MCP HTTP na configuração de ferramentas do fluxo de trabalho (workflow) usa `auth.type: "github-oidc"` em tempo de compilação e apenas anexaremos `-e ACTIONS_ID_TOKEN_REQUEST_URL -e ACTIONS_ID_TOKEN_REQUEST_TOKEN` ao comando `docker run` do Gateway MCP quando essa condição for verdadeira. Essa detecção é realizada pela nova função auxiliar `hasGitHubOIDCAuthInTools()`, que itera sobre o mapa de ferramentas e verifica a configuração de autenticação de cada servidor MCP HTTP. Essa abordagem é consistente com o padrão existente de adicionar condicionalmente outras variáveis de ambiente (ex: variáveis de rastreamento OTEL) ao comando docker apenas quando a funcionalidade correspondente estiver ativa.

### Alternativas Consideradas

#### Alternativa 1: Sempre encaminhar as variáveis de ambiente OIDC incondicionalmente

Encaminhar `ACTIONS_ID_TOKEN_REQUEST_URL` e `ACTIONS_ID_TOKEN_REQUEST_TOKEN` para o contêiner do gateway em todos os casos, independentemente de algum servidor MCP usar autenticação OIDC. Isso é mais simples — não requer lógica de detecção. No entanto, expõe desnecessariamente o endpoint do token OIDC ao gateway em workflows que não precisam dele, o que viola o princípio do privilégio mínimo. A geração de tokens a partir desses endpoints só é segura quando a permissão específica (`id-token: write`) foi deliberadamente concedida pelo autor do workflow.

#### Alternativa 2: Deixar o usuário configurar o encaminhamento de variáveis OIDC explicitamente no frontmatter do workflow

Adicionar uma opção de alto nível `forward-oidc-vars: true` à configuração do workflow que os usuários devem definir manualmente. Isso evita heurísticas de detecção, mas cria uma armadilha: os usuários que configuram `auth.type: "github-oidc"` em um servidor MCP teriam que se lembrar separadamente de definir uma segunda flag. Dado que o compilador já tem acesso à configuração completa das ferramentas em tempo de compilação, a detecção automática oferece uma experiência de usuário (UX) estritamente melhor e elimina uma classe de erros de configuração.

#### Alternativa 3: Encaminhar variáveis OIDC apenas via camada firewall/contêiner do agente, não pelo comando docker

Confiar no firewall encaminhando as variáveis do host para o contêiner do agente e então fazer com que o Gateway MCP as herde via ambiente de processo do contêiner, em vez de flags `-e` explícitas. Isso funcionaria apenas se o processo do gateway fosse iniciado como um processo filho, o que não é o caso — ele roda dentro de um contêiner Docker separado iniciado com `docker run`. A herança de ambiente não cruza a fronteira de um `docker run` sem flags `-e` explícitas.

### Consequências

#### Positivas
- Servidores MCP HTTP configurados com `auth.type: "github-oidc"` podem gerar tokens OIDC com sucesso dentro do contêiner do gateway.
- As variáveis de endpoint do token OIDC são encaminhadas apenas quando necessário, seguindo o princípio do privilégio mínimo.
- A implementação é consistente com o padrão existente de encaminhamento condicional de variáveis de ambiente usado para rastreamento OTEL.
- Nenhuma ação do autor do workflow é necessária; a detecção é automática a partir da configuração de ferramentas existente.

#### Negativas
- A função `hasGitHubOIDCAuthInTools()` deve manter uma lista de bloqueio (blocklist) codificada de nomes de ferramentas padrão (`github`, `playwright`, `cache-memory`, `agentic-workflows`, `safe-outputs`, `mcp-scripts`) que são ignoradas durante seções de detecção. Esta lista deve ser mantida em sincronia se novas ferramentas integradas forem adicionadas.
- Se uma configuração de ferramenta estiver malformada (ex: `getMCPConfig` retorna um erro), essa ferramenta é ignorada silenciosamente em vez de causar um erro de compilação; a autenticação OIDC nessa ferramenta silenciosamente não funcionará.

#### Neutras
- O booleano `hasOIDCAuth` é computado uma vez e reutilizado tanto na seção de flags `-e` quanto na seção do mapa de deduplicação do construtor de comando docker, portanto, o custo de detecção é O(n) sobre as ferramentas e pago apenas uma vez por compilação.
- Workflows que não usam autenticação OIDC não são afetados por esta mudança.

---

## Parte 2 — Especificação Normativa (RFC 2119)

> As palavras-chave **DEVE**, **NÃO DEVE**, **OBRIGATÓRIO**, **DEVERÁ**, **NÃO DEVERÁ**, **DEVERIA**, **NÃO DEVERIA**, **RECOMENDADO**, **PODE** e **OPCIONAL** nesta seção devem ser interpretadas conforme descrito em [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### Encaminhamento de Variáveis de Ambiente OIDC

1. O compilador **DEVE** inspecionar a configuração de ferramentas em tempo de compilação para determinar se algum servidor MCP HTTP possui `auth.type` igual a `"github-oidc"`.
2. O compilador **DEVE** anexar `-e ACTIONS_ID_TOKEN_REQUEST_URL` e `-e ACTIONS_ID_TOKEN_REQUEST_TOKEN` ao comando `docker run` do Gateway MCP se, e somente se, pelo menos um servidor MCP HTTP com `auth.type: "github-oidc"` estiver presente na configuração de ferramentas.
3. O compilador **NÃO DEVE** anexar essas flags de variáveis de ambiente quando nenhum servidor MCP HTTP usar `auth.type: "github-oidc"`.
4. O compilador **DEVE** registrar `ACTIONS_ID_TOKEN_REQUEST_URL` e `ACTIONS_ID_TOKEN_REQUEST_TOKEN` no mapa de deduplicação quando forem encaminhadas, para evitar entradas `-e` duplicadas.

### Lógica de Detecção OIDC

1. O auxiliar de detecção **DEVE** ignorar ferramentas que não sejam servidores MCP HTTP configuráveis (ou seja, ferramentas integradas: `github`, `playwright`, `cache-memory`, `agentic-workflows`, `safe-outputs`, `mcp-scripts`).
2. O auxiliar de detecção **DEVE** verificar apenas ferramentas cuja configuração resulte em uma configuração MCP válida com `type: "http"`.
3. O auxiliar de detecção **DEVERIA** registrar uma mensagem no nível de log de ambiente MCP quando uma ferramenta com autenticação GitHub OIDC for encontrada, para auxiliar na depuração.
4. O auxiliar de detecção **PODE** retornar antecipadamente (`true`) assim que a primeira ferramenta correspondente for encontrada, sem inspecionar as ferramentas restantes.

### Conformidade

Uma implementação é considerada em conformidade com este ADR se satisfizer todos os requisitos **DEVE** e **NÃO DEVE** acima. Especificamente: o comando `docker run` do Gateway MCP inclui `-e ACTIONS_ID_TOKEN_REQUEST_URL -e ACTIONS_ID_TOKEN_REQUEST_TOKEN` quando, e somente quando, pelo menos um servidor MCP HTTP no workflow compilado usa `auth.type: "github-oidc"`. A falha em atender a qualquer requisito **DEVE** ou **NÃO DEVE** constitui não conformidade.

---

*ADR criado pelo [agente adr-writer]. Revise e finalize antes de alterar o status de Rascunho para Aceito.*
