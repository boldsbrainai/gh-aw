# ADR-25830: Adicionar OpenCode como um Agentic Engine "BYOK" Agnóstico ao Provedor

**Data**: 2026-04-11
**Status**: Aceito — O suporte ao OpenCode está ativo como um engine built-in experimental (`engine: id: opencode`).
**Decisores**: pelikhan, Copilot

---

## Parte 1 — Narrativa (Amigável)

### Contexto

O gh-aw suporta vários engines de agente de primeira linha (Copilot, Claude, Codex, Gemini) que se vinculam a um único provedor de IA e exigem uma chave de API de fornecedor correspondente. Usuários que desejam executar modelos de múltiplos provedores — ou que preferem ferramentas de código aberto — não possuem um caminho hoje sem escrever um engine totalmente personalizado. O OpenCode é um agente de codificação de IA de código aberto, agnóstico ao provedor (BYOK — Bring Your Own Key) que suporta mais de 75 modelos via uma interface de CLI unificada usando um formato `provedor/modelo` (ex.: `anthropic/claude-sonnet-4-20250514`). Como o endpoint da API de cada provedor é diferente, adicionar o OpenCode também introduz um novo desafio: a lista de permissões (allowlist) do firewall da rede não pode ser uma lista estática e deve ser calculada dinamicamente a partir do provedor de modelo selecionado em tempo de compilação.

### Decisão

Integraremos o OpenCode como um quinto engine de agente built-in (`id: "opencode"`) seguindo o padrão `BaseEngine` existente usado pelo Claude, Codex e Gemini. O engine é instalado via npm (`opencode-ai@1.2.14`), executado em modo headless via `opencode run` e comunica-se com o proxy de gateway LLM em uma porta dedicada (10004). Domínios de API específicos do provedor para a allowlist do firewall são resolvidos em tempo de compilação fazendo o parse do prefixo da string `provedor/modelo`; o provedor padrão é a Anthropic. Todas as permissões de ferramenta dentro do sandbox do OpenCode são pré-configuradas para `allow` via um arquivo de configuração `opencode.jsonc` gravado antes da execução, o que impede que o executor de CI trave em prompts de permissão interativos.

### Alternativas Consideradas

#### Alternativa 1: Wrapper de engine personalizado via `engine.command`

Os usuários já podem especificar `engine.command: opencode run` como um override de comando personalizado no frontmatter do workflow, o que lhes permite invocar o OpenCode sem qualquer suporte nativo de engine. Isso evita adicionar código ao engine, mas força cada usuário a especificar manualmente os passos de instalação, configurar o arquivo de permissões `opencode.jsonc` e gerenciar os domínios do firewall por conta própria. Para uma ferramenta de código aberto mantida pela comunidade com adoção crescente, o suporte nativo oferece uma experiência de usuário (UX) substancialmente melhor com defaults corretos out-of-the-box.

#### Alternativa 2: Estender um engine existente (ex.: Claude) com roteamento de modelo multiprovedor

Em vez de adicionar um novo engine, o engine do Claude poderia ser estendido para aceitar prefixos de modelo `openai/` ou `google/` e roteá-los para provedores alternativos através do gateway LLM. Isso evita manter uma abstração de engine separada, mas confunde duas CLIs distintas (CLI do Claude Code vs. CLI do OpenCode) sob o mesmo ID de engine, gerando confusão para os usuários finais e tornando a lógica de firewall e instalação mais complexa. O OpenCode possui seu próprio artefato de instalação, formato de configuração (`opencode.jsonc`) e binário — eles são genuinamente engines diferentes, não variantes de modelo.

#### Alternativa 3: Allowlist de domínios estática multiprovedor

Em vez de fazer o parse da string do modelo para derivar o domínio do firewall em tempo de compilação, incluir todos os endpoints de API de provedores conhecidos em `OpenCodeDefaultDomains` estaticamente. Isso é mais simples, mas viola o princípio do privilégio mínimo: um workflow que usa apenas o provedor Anthropic teria desnecessariamente `api.openai.com` e `generativelanguage.googleapis.com` na sua allowlist. A implementação atual inclui os três provedores mais comuns no default estático (`OpenCodeDefaultDomains`) como um fallback amplo, enquanto `GetDefaultDomainsForEngine(constants.OpenCodeEngine, model)` fornece uma lista mais restrita por provedor quando um modelo é explicitamente configurado.

### Consequências

#### Positivas
- Usuários podem executar qualquer um dos mais de 75 modelos de múltiplos provedores (Anthropic, OpenAI, Google, Groq, Mistral, DeepSeek, xAI) através de um único seletor de engine.
- O modelo BYOK remove a dependência de entitlements do GitHub Copilot; qualquer usuário com uma chave de API de provedor direto pode executar fluxos de trabalho de agente.
- A resolução dinâmica de domínio por provedor mantém as allowlists do firewall o mais restritas possível, dado o modelo selecionado.
- Os padrões existentes de `BaseEngine` e registro de engine são reutilizados sem modificação, mantendo o diff pequeno e coerente.

#### Negativas
- O engine está marcado como `experimental: true` até que os testes de fumaça (smoke tests) passem consistentemente; a prontidão para produção foi adiada.
- O OpenCode ainda não suporta `--max-turns` ou a abstração de ferramenta de pesquisa web neutra do gh-aw (`supportsMaxTurns: false`, `supportsWebSearch: false`), limitando a paridade com outros engines.
- O mapa `openCodeProviderDomains` em `domains.go` deve ser mantido manualmente em sincronia conforme o OpenCode adiciona ou remove provedores suportados; não há detecção automática de drift.
- Pré-configurar todas as permissões para `allow` no `opencode.jsonc` desativa os guardrails de segurança interativos do OpenCode em CI. Isso é intencional (CI não pode responder prompts), mas significa que o agente é executado com permissões de ferramenta elevadas dentro do sandbox.

#### Neutras
- Uma porta de gateway LLM separada (10004) é alocada para o OpenCode, distinta de outros engines. Isso adiciona mais uma constante de porta conhecida em `pkg/constants/version_constants.go`.
- A integração de configuração MCP segue o mesmo caminho `renderStandardJSONMCPConfig` que outros engines baseados em JSON; nenhum novo formato de configuração MCP é introduzido.
- 22 testes unitários cobrem o novo engine (identidade, capacidades, segredos, instalação, execução, firewall e extração de provedor). Estes estão colocados junto com outros testes de engine em `pkg/workflow/`.

---

## Parte 2 — Especificação Normativa (RFC 2119)

> As palavras-chave **DEVEM**, **NÃO DEVEM**, **OBRIGATÓRIO**, **SHALL**, **SHALL NOT**, **RECOMENDADO**, **MAY** e **OPCIONAL** nesta seção devem ser interpretadas conforme descrito em [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### Registro de Engine

1. O engine OpenCode **DEVE** ser registrado em `NewEngineRegistry()` sob o identificador `"opencode"`.
2. O engine OpenCode **DEVE** implementar a interface `AgenticEngine` via embedding de `BaseEngine`, consistente com todos os outros engines built-in.
3. O engine OpenCode **DEVE** ser incluído em `AgenticEngines` e `EngineOptions` para que as ferramentas que enumeram engines built-in o descubram automaticamente.

### Instalação

1. O engine **DEVE** instalar a OpenCode CLI via npm usando a versão do pacote fixada (pinned) definida por `DefaultOpenCodeVersion` em `pkg/constants/version_constants.go`.
2. O engine **DEVE** pular os passos de instalação quando `engine.command` for explicitamente sobrescrito na configuração do workflow.
3. O engine **DEVE** usar `BuildStandardNpmEngineInstallSteps` para gerar os passos de instalação, garantindo que quaisquer mudanças futuras no padrão de instalação npm padrão sejam aplicadas automaticamente.

### Execução

1. O engine **DEVE** gravar um arquivo de configuração `opencode.jsonc` no `$GITHUB_WORKSPACE` antes de executar o agente, com todas as permissões de ferramenta (`bash`, `edit`, `read`, `glob`, `grep`, `write`, `webfetch`, `websearch`) definidas como `"allow"`.
2. O engine **DEVE** mesclar a config de permissões com qualquer `opencode.jsonc` existente encontrado no workspace (usando `jq` deep merge), em vez de sobrescrevê-lo incondicionalmente.
3. O engine **DEVE** invocar o OpenCode via `opencode run <prompt>` em modo headless, passando `--print-logs` e `--log-level DEBUG` para observabilidade de CI.
4. O engine **DEVE** rotear chamadas de API LLM através do proxy de gateway local na porta `OpenCodeLLMGatewayPort` (10004) definindo `ANTHROPIC_BASE_URL` quando o firewall estiver habilitado.
5. O engine **NÃO DEVE** passar `--max-turns` para a CLI do OpenCode, já que essa flag não é suportada.

### Allowlisting de Domínios de Firewall

1. Quando um modelo for explicitamente configurado em `engine.model`, o compilador **DEVE** chamar `GetDefaultDomainsForEngine(constants.OpenCodeEngine, model)` para resolver domínios de API específicos do provedor a partir do prefixo `provedor/modelo`.
2. A função `extractProviderFromModel` **DEVE** fazer o parse da string do modelo dividindo no primeiro caractere `/` e retornando o token à esquerda, em minúsculas.
3. Quando nenhum separador `/` for encontrado na string do modelo, `extractProviderFromModel` **DEVE** retornar `"anthropic"` como o provedor padrão.
4. O mapa `openCodeProviderDomains` **DEVE** ser a única fonte da verdade para mapear nomes de provedores para seus hostnames de API; os chamadores **NÃO DEVEM** hardcodear strings de domínio de provedor fora deste mapa.
5. O mapa `engineDefaultDomains` em `domains.go` **DEVE** incluir uma entrada para `constants.OpenCodeEngine` para garantir que `GetAllowedDomainsForEngine` funcione corretamente para o engine OpenCode.

### Coleta de Segredos

1. O engine **DEVE** incluir `ANTHROPIC_API_KEY` na lista de segredos necessários como o segredo de provedor padrão.
2. O engine **DEVE** incluir segredos adicionais de `engine.env` cujos nomes de chave terminem em `_API_KEY` ou `_KEY`, para suportar configurações de provedor não padrão.
3. O engine **DEVE** coletar segredos MCP comuns via `collectCommonMCPSecrets` e segredos de cabeçalho MCP HTTP via `collectHTTPMCPHeaderSecrets`, consistente com outros engines.

### Conformidade

Uma implementação é considerada em conformidade com este ADR se satisfizer todos os requisitos **DEVEM** e **NÃO DEVEM** acima. Especificamente: o engine OpenCode **DEVE** ser registrado, instalado via npm em uma versão fixa, gravar uma config de permissões completa antes da execução, invocar `opencode run` em modo headless e resolver domínios de firewall dinamicamente a partir do prefixo do provedor de modelo. A falha em atender a qualquer requisito **DEVE** ou **NÃO DEVE** constitui não conformidade.

---

*ADR criado pelo agente [adr-writer agent] e atualizado para refletir o suporte atual ao engine aceito.*
