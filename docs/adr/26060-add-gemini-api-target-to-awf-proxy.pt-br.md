# ADR-26060: Adicionar Roteamento de Target da API Gemini ao Proxy AWF

**Data**: 2026-04-13
**Status**: Rascunho
**Decisores**: pelikhan, Copilot

---

## Parte 1 — Narrativa (Amigável)

### Contexto

O sidecar de proxy AWF fornece um gateway LLM que roteia chamadas de API de contêineres de agente para provedores de IA externos. Para os engines OpenAI (codex), Anthropic (claude) e Copilot, o proxy tem alvos de roteamento padrão integrados. O Gemini foi integrado como um engine, mas nunca recebeu um alvo de roteamento de proxy correspondente: quando um workflow é executado com `engine: gemini` e o firewall de rede habilitado, `GEMINI_API_BASE_URL` aponta para o proxy na porta 10003, mas o proxy não consegue encaminhar a chamada e retorna `API_KEY_INVALID`. A correção deve seguir o padrão existente para outros engines para permanecer consistente e sustentável.

### Decisão

Adicionaremos `GetGeminiAPITarget()` à camada de helpers do AWF e o conectaremos em `BuildAWFArgs()` para que a flag `--gemini-api-target` seja emitida sempre que o engine for Gemini. O alvo padrão é `generativelanguage.googleapis.com`; quando `GEMINI_API_BASE_URL` é configurado em `engine.env`, o hostname extraído dessa URL tem precedência. Quando a URL personalizada inclui um componente de caminho, `--gemini-api-base-path` também é emitido. Isso espelha o padrão existente usado para `--openai-api-target`, `--anthropic-api-target` e `--copilot-api-target`, mantendo o modelo de roteamento de engine uniforme.

### Alternativas Consideradas

#### Alternativa 1: Hard-code o alvo padrão do Gemini dentro do binário do sidecar AWF

O sidecar AWF poderia ser modificado para conhecer o endpoint padrão do Gemini sem exigir que o chamador passe `--gemini-api-target`. Isso eliminaria a necessidade de mudança na camada Go. No entanto, acopla o sidecar a um endpoint de fornecedor específico, tornando mais difícil testar independentemente e exigindo uma release do sidecar para cada novo engine. O padrão atual—alvos fornecidos pelo chamador—mantém o sidecar genérico.

#### Alternativa 2: Exigir que os usuários sempre configurem `GEMINI_API_BASE_URL` explicitamente

Sem um alvo padrão, usuários que desejam usar o endpoint público do Gemini precisariam adicionar `GEMINI_API_BASE_URL: "https://generativelanguage.googleapis.com"` a cada workflow. Isso adiciona boilerplate e difere de todos os outros engines, que todos roteiam para um padrão sensato sem configuração extra. A assimetria de experiência é um custo significativo de usabilidade.

#### Alternativa 3: Usar o campo YAML `engine.api-target` em vez de uma variável de ambiente

O engine Copilot já possui um campo `engine.api-target` no YAML do workflow que sobrescreve `GITHUB_COPILOT_BASE_URL`. Poderíamos introduzir um `engine.api-target` similar para o Gemini. No entanto, nenhum outro engine além do Copilot usa este campo, e adicioná-lo apenas para o Gemini criaria inconsistência. Usar `GEMINI_API_BASE_URL` em `engine.env` alinha o Gemini com o padrão do codex e claude.

### Consequências

#### Positivas
- Workflows do engine Gemini agora funcionam corretamente quando o firewall de rede está habilitado — o proxy pode encaminhar chamadas para o upstream correto.
- Usuários obtêm suporte a endpoints personalizados (`GEMINI_API_BASE_URL`) consistente com os engines codex e claude.
- A implementação segue o padrão de roteamento de engine estabelecido; novos engines no futuro podem ser adicionados da mesma maneira.
- `GH_AW_ALLOWED_DOMAINS` é mantido em sincronia com `--allow-domains` através do hook existente `computeAllowedDomainsForSanitization`.

#### Negativas
- `BuildAWFArgs` cresce ligeiramente; a lógica de alvo específica do engine é colocada em uma função em vez de ser despachada polimorficamente.
- Uma constante hard-coded (`DefaultGeminiAPITarget`) deve ser atualizada se o Google alterar o hostname da API Gemini, embora este seja um cenário improvável.

#### Neutras
- O arquivo de lock de teste de fumaça (`.github/workflows/smoke-gemini.lock.yml`) deve ser recompilado para incluir `--gemini-api-target generativelanguage.googleapis.com` nas invocações geradas de `awf`.
- A documentação para endpoints de API personalizados em `docs/src/content/docs/reference/engines.md` ganha uma seção de exemplo do Gemini, estendendo um padrão existente em vez de introduzir novos conceitos.

---

## Parte 2 — Especificação Normativa (RFC 2119)

> As palavras-chave **DEVEM**, **NÃO DEVEM**, **OBRIGATÓRIO**, **SHALL**, **SHALL NOT**, **RECOMENDADO**, **MAY** e **OPCIONAL** nesta seção devem ser interpretadas conforme descrito em [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### Resolução de Alvo de Proxy Gemini

1. Quando o engine ativo for `gemini` e `GEMINI_API_BASE_URL` não estiver configurado em `engine.env`, implementações **DEVEM** emitir `--gemini-api-target generativelanguage.googleapis.com` nos argumentos de comando `awf`.
2. Quando `GEMINI_API_BASE_URL` estiver configurado em `engine.env`, implementações **DEVEM** extrair o hostname dessa URL e emitir `--gemini-api-target <hostname>` em vez do padrão.
3. Quando `GEMINI_API_BASE_URL` contiver um componente de caminho não vazio (ex.: `/v1/beta`), implementações **DEVEM** também emitir `--gemini-api-base-path <path>`.
4. Implementações **NÃO DEVEM** emitir `--gemini-api-target` quando o engine não for `gemini` e `GEMINI_API_BASE_URL` não estiver configurado.
5. A constante `DefaultGeminiAPITarget` **DEVE** ser a única fonte da verdade para o hostname padrão do Gemini; ela **NÃO DEVE** ser duplicada como um literal de string em outro lugar na base de código.

### Sincronização de Allowlist de Domínios

1. O hostname do alvo da API Gemini efetivo **DEVE** ser incluído no conjunto de domínios computado por `computeAllowedDomainsForSanitization()` para que `GH_AW_ALLOWED_DOMAINS` e `--allow-domains` permaneçam consistentes.
2. Implementações **DEVEM** chamar `GetGeminiAPITarget()` com o mesmo `engineID` usado para a flag de proxy, garantindo que ambos os caminhos resolvam identicamente.

### Padrão de Endpoint Personalizado

1. Novas integrações de API-target de engine **DEVEM** seguir o mesmo padrão de três partes estabelecido aqui: (a) um helper `Get<Engine>APITarget()` que lê `<ENGINE>_API_BASE_URL` com um fallback padrão, (b) uma chamada em `BuildAWFArgs()` para emitir a flag `--<engine>-api-target`, e (c) inclusão em `computeAllowedDomainsForSanitization()`.
2. Variáveis de ambiente específicas de engine para endpoints personalizados **DEVEM** seguir a convenção de nomenclatura `<ENGINE_UPPERCASE>_API_BASE_URL` (ex.: `GEMINI_API_BASE_URL`, `OPENAI_BASE_URL`).

### Conformidade

Uma implementação é considerada em conformidade com este ADR se satisfizer todos os requisitos **DEVEM** e **NÃO DEVEM** acima. A falha em atender a qualquer requisito **DEVE** ou **NÃO DEVE** constitui não conformidade.

---

*ADR criado pelo agente [adr-writer agent]. Revise e finalize antes de alterar o status de Rascunho para Aceito.*
