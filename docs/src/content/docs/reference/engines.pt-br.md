---
title: Motores de IA (também conhecidos como Agentes de Codificação)
description: Guia completo para motores de IA (agentes de codificação) utilizáveis com GitHub Agentic Workflows, incluindo Copilot, Claude, Codex, Gemini, Crush, OpenCode e Pi com suas opções de configuração específicas.
sidebar:
  order: 600
---

GitHub Agentic Workflows usam [Motores de IA](/gh-aw/reference/glossary/#engine) (normalmente um agente de codificação) para interpretar e executar instruções de linguagem natural.

## Motores de Codificação Disponíveis

Defina `engine:` no frontmatter do seu fluxo de trabalho e configure o secret correspondente:

| Motor | Valor de `engine:` | Secret Obrigatório |
|--------|-----------------|-----------------|
| [GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli) (padrão) | `copilot` | [COPILOT_GITHUB_TOKEN](/gh-aw/reference/auth/#copilot_github_token) |
| [Claude by Anthropic (Claude Code)](https://www.anthropic.com/index/claude) | `claude` | [ANTHROPIC_API_KEY](/gh-aw/reference/auth/#anthropic_api_key) |
| [OpenAI Codex](https://openai.com/blog/openai-codex) | `codex` | [OPENAI_API_KEY](/gh-aw/reference/auth/#openai_api_key) |
| [Google Gemini CLI](https://github.com/google-gemini/gemini-cli) | `gemini` | [GEMINI_API_KEY](/gh-aw/reference/auth/#gemini_api_key) |
| [Crush](https://github.com/charmbracelet/crush) (experimental) | `crush` | [COPILOT_GITHUB_TOKEN](/gh-aw/reference/auth/#copilot_github_token) |
| [OpenCode](https://opencode.ai) (experimental) | `opencode` | [COPILOT_GITHUB_TOKEN](/gh-aw/reference/auth/#copilot_github_token) |
| [Pi](https://www.npmjs.com/package/@mariozechner/pi-coding-agent) (experimental) | `pi` | [COPILOT_GITHUB_TOKEN](/gh-aw/reference/auth/#copilot_github_token) (padrão); muda para secret específico do provedor quando `model:` usa o formato `provider/model` |

Copilot CLI é o padrão — `engine:` pode ser omitido ao usar o Copilot. Veja os documentos de autenticação vinculados para instruções de configuração de secret.

## Qual motor devo escolher?

Escolha o motor que melhor se adapta às suas necessidades e conta de IA existente: O Copilot suporta o conjunto mais amplo de recursos do gh-aw, incluindo agentes personalizados e continuações no estilo piloto automático; Claude oferece controle mais forte sobre limites de turno (`max-turns`) para sessões de raciocínio longo; e Gemini ou Codex se encaixam bem quando esses modelos já fazem parte de ferramentas existentes ou decisões de orçamento. Você pode mudar mais tarde alterando apenas `engine:` e o secret correspondente.

## Comparação de Recursos do Motor

Nem todos os recursos estão disponíveis em todos os motores. A tabela abaixo resume o suporte por motor para opções de fluxo de trabalho usadas com frequência:

| Recurso | Copilot | Claude | Codex | Gemini | Crush | OpenCode | Pi |
|---------|:-------:|:------:|:-----:|:------:|:-----:|:--------:|:--:|
| `max-runs` (limite de invocação AWF) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `max-turns` | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `max-continuations` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `tools.web-fetch` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `tools.web-search` | via MCP | via MCP | ✅ (opt-in) | via MCP | via MCP | via MCP | via MCP |
| `engine.agent` (arquivo de agente personalizado) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `engine.api-target` (endpoint personalizado) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `engine.bare` (desabilitar carregamento de contexto) | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `engine.harness` (script de harness personalizado) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Allowlist de ferramentas | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |

**Notas:**
- `max-runs` é um campo de frontmatter de nível superior que mapeia para `apiProxy.maxRuns` e é suportado por todos os motores.
- `max-runs` assume como padrão `500` e `max-effective-tokens` assume como padrão `25000000` quando omitido.
- `max-turns` limita o número de iterações de chat de IA por execução (apenas Claude).
- `max-continuations` habilita o modo piloto automático com múltiplas execuções consecutivas (apenas Copilot).
- `web-search` para Codex é desabilitado por padrão; adicione `tools: web-search:` para habilitá-lo. Outros motores usam um servidor MCP de terceiros — veja [Usando Busca na Web](/gh-aw/reference/web-search/).
- `engine.agent` referencia um arquivo `.github/agents/` para comportamento personalizado do agente Copilot. Veja [Configuração Personalizada do Copilot](#copilot-custom-configuration).
- `engine.bare` desabilita o carregamento automático de contexto (arquivos de memória, instruções personalizadas). Veja [Modo Bare](#bare-mode-bare) abaixo.
- `engine.harness` permite substituir o script harness integrado do Copilot. Veja [Script de Harness Personalizado](#custom-harness-script-harness) abaixo.

## Configuração Estendida do Agente de Codificação

Fluxos de trabalho podem especificar configuração estendida para o agente de codificação:

```yaml wrap
engine:
  id: copilot
  version: latest                       # padrão é latest
  model: gpt-5                          # exemplo de sobrescrita; omita para usar o padrão do motor
  command: /usr/local/bin/copilot       # caminho do executável personalizado
  args: ["--add-dir", "/workspace"]     # argumentos CLI personalizados
  agent: agent-id                       # identificador do arquivo de agente personalizado
  api-target: api.acme.ghe.com          # hostname do endpoint de API personalizado (GHEC/GHES)
```

### Fixando uma versão específica do motor

Por padrão, os fluxos de trabalho instalam a versão mais recente disponível de cada CLI de motor. Para fixar em uma versão específica, defina `version` para o release desejado:

| Motor | `id` | Exemplo `version` |
|--------|------|-------------------|
| GitHub Copilot CLI | `copilot` | `"0.0.422"` |
| Claude Code | `claude` | `"2.1.70"` |
| Codex | `codex` | `"0.111.0"` |
| Gemini CLI | `gemini` | `"0.31.0"` |
| Crush | `crush` | `"1.2.14"` |
| OpenCode | `opencode` | `"0.1.0"` |
| Pi | `pi` | `"0.72.1"` |

```yaml wrap
engine:
  id: copilot
  version: "0.0.422"
```

A fixação é útil quando você precisa de builds reprodutíveis ou deseja evitar quebra de um novo release de CLI durante testes. Lembre-se de atualizar a versão fixada periodicamente para obter correções de bugs e novos recursos.

`version` também aceita uma string de expressão do GitHub Actions, permitindo que fluxos de trabalho reutilizáveis `workflow_call` parametrizem a versão do motor via inputs do chamador. Expressões são passadas de forma segura contra injeção através de uma variável de ambiente em vez de interpolação direta de shell:

```yaml wrap
on:
  workflow_call:
    inputs:
      engine-version:
        type: string
        default: latest

---

engine:
  id: copilot
  version: ${{ inputs.engine-version }}
```

### Configuração Personalizada do Copilot

Use `agent` para referenciar um arquivo de agente personalizado em `.github/agents/` (omita a extensão `.agent.md`):

```yaml wrap
engine:
  id: copilot
  agent: technical-doc-writer  # .github/agents/technical-doc-writer.agent.md
```

Veja [Arquivos de Agente Copilot](/gh-aw/reference/copilot-custom-agents/) para detalhes.

### Variáveis de Ambiente do Motor

Todos os motores suportam variáveis de ambiente personalizadas através do campo `env`:

```yaml wrap
engine:
  id: copilot
  env:
    DEBUG_MODE: "true"
    AWS_REGION: us-west-2
    CUSTOM_API_ENDPOINT: https://api.example.com
```

Variáveis de ambiente também podem ser definidas em fluxos de trabalho, jobs, etapas e outros escopos. Veja [Variáveis de Ambiente](/gh-aw/reference/environment-variables/) para documentação completa sobre precedência e todos os 13 escopos de env.

### Endpoint de API Corporativo (`api-target`)

O campo `api-target` especifica um hostname de endpoint de API personalizado para o motor agentic. Use isso ao executar fluxos de trabalho contra GitHub Enterprise Cloud (GHEC), GitHub Enterprise Server (GHES) ou qualquer endpoint de IA personalizado.

Para um passo a passo completo de configuração e depuração para GHE Cloud com residência de dados, veja [Depurando GHE Cloud com Residência de Dados](/gh-aw/troubleshooting/debug-ghe/).

O valor deve ser apenas um hostname — sem protocolo ou caminho (ex: `api.acme.ghe.com`, não `https://api.acme.ghe.com/v1`). O campo funciona com qualquer motor.

**Exemplo GHEC** — especifique seu endpoint do Copilot específico do tenant:

```yaml wrap
engine:
  id: copilot
  api-target: api.acme.ghe.com
network:
  allowed:
    - defaults
    - acme.ghe.com
    - api.acme.ghe.com
```

**Exemplo GHES** — use o endpoint do Copilot corporativo:

```yaml wrap
engine:
  id: copilot
  api-target: api.enterprise.githubcopilot.com
network:
  allowed:
    - defaults
    - github.company.com
    - api.enterprise.githubcopilot.com
```

O hostname especificado também deve estar listado em `network.allowed` para que o firewall permita solicitações de saída.

#### Endpoints de API personalizados via Variáveis de Ambiente

Defina uma variável de ambiente de URL base em `engine.env` para rotear chamadas de API para um roteador de LLM interno, implementação do Azure OpenAI ou proxy corporativo. O AWF extrai automaticamente o hostname e o aplica ao proxy da API. O domínio de destino também deve aparecer em `network.allowed`.

| Motor | Variável de ambiente |
|--------|---------------------|
| `codex`, `crush` | `OPENAI_BASE_URL` |
| `claude` | `ANTHROPIC_BASE_URL` |
| `copilot` | `GITHUB_COPILOT_BASE_URL` |
| `gemini` | `GEMINI_API_BASE_URL` |

```yaml wrap
engine:
  id: codex
  model: gpt-4o
  env:
    OPENAI_BASE_URL: "https://llm-router.internal.example.com/v1"
    OPENAI_API_KEY: ${{ secrets.LLM_ROUTER_KEY }}

network:
  allowed:
    - github.com
    - llm-router.internal.example.com
```

`GITHUB_COPILOT_BASE_URL` é um fallback — se ambos, ele e `engine.api-target`, estiverem definidos, `engine.api-target` tem precedência. Crush usa formato de API compatível com OpenAI; seu campo `model` usa o formato `provider/model` (ex: `openai/gpt-4o`).

### Modo Bring Your Own Key (BYOK) do Copilot

O motor Copilot suporta o roteamento de solicitações para um provedor de LLM externo em vez do roteamento padrão do GitHub. Isso é útil quando você deseja usar um modelo ou provedor diferente (ex: OpenAI, Anthropic, Azure OpenAI ou uma instância local Ollama/vLLM) enquanto ainda usa as ferramentas da CLI do Copilot.

Defina `COPILOT_PROVIDER_BASE_URL` em `engine.env` para ativar o modo BYOK. As variáveis de credencial `COPILOT_PROVIDER_BASE_URL`, `COPILOT_PROVIDER_API_KEY` e `COPILOT_PROVIDER_BEARER_TOKEN` são explicitamente permitidas para carregar referências `${{ secrets.* }}` em `engine.env` sob modo estrito — elas não vazam para o contêiner do agente. Outras variáveis `COPILOT_PROVIDER_*` contêm configurações não confidenciais e podem ser definidas como strings simples.

| Variável | Obrigatório | Descrição |
|---|---|---|
| `COPILOT_PROVIDER_BASE_URL` | ✅ para BYOK | URL base do provedor externo (ex: `https://api.openai.com/v1`) |
| `COPILOT_MODEL` | ✅ para BYOK | Modelo a usar (ex: `claude-sonnet-4`, `gpt-4o`); exigido pela maioria dos provedores |
| `COPILOT_PROVIDER_API_KEY` | Opcional | Chave de API para provedores de nuvem (OpenAI, Anthropic, etc.); não necessária para provedores locais |
| `COPILOT_PROVIDER_BEARER_TOKEN` | Opcional | Alternativa de token Bearer para `COPILOT_PROVIDER_API_KEY`; tem precedência quando definido |
| `COPILOT_PROVIDER_TYPE` | Opcional | Formato do provedor: `openai` (padrão), `azure` ou `anthropic` |
| `COPILOT_PROVIDER_WIRE_API` | Opcional | Variante da API Wire: `completions` (padrão) ou `responses` (para a série GPT-5) |
| `COPILOT_PROVIDER_MODEL_ID` | Opcional | ID do modelo enviado no wire quando difere de `COPILOT_MODEL` (ex: um nome de deployment Azure) |
| `COPILOT_PROVIDER_WIRE_MODEL` | Opcional | Alternativa a `COPILOT_PROVIDER_MODEL_ID` para sobrescrever o modelo wire |
| `COPILOT_PROVIDER_MAX_PROMPT_TOKENS` | Opcional | Sobrescrever o limite máximo de token de prompt (caso contrário resolvido do catálogo de modelos) |
| `COPILOT_PROVIDER_MAX_OUTPUT_TOKENS` | Opcional | Sobrescrever o limite máximo de token de saída |

**Exemplo: Provedor compatível com OpenAI**

```yaml wrap
engine:
  id: copilot
  env:
    # OBRIGATÓRIO — ativa o modo BYOK
    COPILOT_PROVIDER_BASE_URL: ${{ secrets.PROVIDER_BASE_URL }}

    # OBRIGATÓRIO — um modelo deve ser especificado para a maioria dos provedores externos
    COPILOT_MODEL: claude-sonnet-4

    # OPCIONAL — Chave de API para provedores de nuvem; não necessária para provedores locais
    COPILOT_PROVIDER_API_KEY: ${{ secrets.PROVIDER_API_KEY }}

    # OPCIONAL — defina como "anthropic" ou "azure" se necessário (padrão: "openai")
    # COPILOT_PROVIDER_TYPE: anthropic

network:
  allowed:
    - defaults
    - your-provider-domain.example.com
```

**Exemplo: Provedor Anthropic**

```yaml wrap
engine:
  id: copilot
  env:
    COPILOT_PROVIDER_BASE_URL: ${{ secrets.ANTHROPIC_BASE_URL }}
    COPILOT_MODEL: claude-sonnet-4
    COPILOT_PROVIDER_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    COPILOT_PROVIDER_TYPE: anthropic
```

> [!NOTE]
> `COPILOT_PROVIDER_BASE_URL`, `COPILOT_PROVIDER_API_KEY` e `COPILOT_PROVIDER_BEARER_TOKEN` são reconhecidos como credenciais de motor e têm permissão para carregar referências `${{ secrets.* }}` em `engine.env` sem disparar o aviso de "secrets in env" do modo estrito. Outras variáveis `COPILOT_PROVIDER_*` (tipo, modelo, limites de token) mantêm configurações não confidenciais e podem ser definidas como strings simples. Elas também podem usar a sintaxe `${{ secrets.* }}` se você preferir mantê-las privadas, mas isso não é necessário.

> [!NOTE]
> Credenciais passadas via variáveis `COPILOT_PROVIDER_*` são mantidas fora do contêiner do agente. Apenas a chave de API fictícia que ativa o caminho de detecção BYOK do Agentic Workflow Firewall (AWF) é visível ao processo do agente; a credencial real é isolada no sidecar de proxy da API AWF. Veja a arquitetura de sandbox AWF](/gh-aw/reference/sandbox/) para detalhes.

### Argumentos de Linha de Comando do Motor

Todos os motores suportam argumentos de linha de comando personalizados através do campo `args`, injetados antes do prompt:

```yaml wrap
engine:
  id: copilot
  args: ["--add-dir", "/workspace", "--verbose"]
```

Argumentos são adicionados em ordem e colocados antes da flag `--prompt`. Consulte a documentação da CLI do motor específico para flags disponíveis.

### Comando de Motor Personalizado

Substitua o executável do motor padrão usando o campo `command`. Útil para testar versões pré-release, builds personalizados ou instalações não padrão. Etapas de instalação são puladas automaticamente.

```yaml wrap
engine:
  id: copilot
  command: /usr/local/bin/copilot-dev  # caminho absoluto
  args: ["--verbose"]
```

### Script de Harness Personalizado (`harness`)

O campo `harness` permite que você substitua o wrapper harness Node.js integrado que o motor Copilot usa para iniciar a CLI. Use isso quando precisar personalizar o comportamento de inicialização, injetar hooks pré/pós ou testar uma implementação de harness alternativa.

```yaml wrap
engine:
  id: copilot
  harness: custom_copilot_harness.cjs
```

O valor deve ser um nome de arquivo simples — sem separadores de diretório, sem `..` e sem metacaracteres de shell. Deve terminar com `.js`, `.cjs` ou `.mjs`. Quando `harness` é definido, o AWF garante automaticamente que o Node 24 esteja disponível no ambiente do executor.

> [!NOTE]
> `engine.harness` é aplicado atualmente apenas durante a execução do motor Copilot. Defini-lo em outros motores não tem efeito.

**Regras de validação:**

| Regra | Exemplo válido | Exemplo inválido |
|------|--------------|-----------------|
| Apenas nome de arquivo simples | `my_harness.cjs` | `subdir/harness.cjs` |
| Sem travessia de caminho | `harness.mjs` | `../harness.cjs` |
| Deve começar com `[A-Za-z0-9_]` | `harness.js` | `-harness.cjs` |
| Deve terminar com `.js`, `.cjs` ou `.mjs` | `wrapper.cjs` | `harness.sh` |

### Modo Bare (`bare`)

Defina `engine.bare: true` para desabilitar o carregamento automático de contexto e instruções personalizadas pelo motor. Use isso quando o prompt do fluxo de trabalho for totalmente autônomo e você quiser impedir que o motor leia arquivos de memória, AGENTS.md ou prompts de sistema integrados que seriam carregados automaticamente.

```yaml wrap
engine:
  id: claude
  bare: true
```

O mecanismo subjacente é específico do motor:

| Motor | Efeito |
|--------|--------|
| Copilot | Passa `--no-custom-instructions` — suprime `.github/AGENTS.md` e instruções personalizadas em nível de usuário |
| Claude | Passa `--bare` — suprime arquivos de memória CLAUDE.md |
| Codex | Passa `--no-system-prompt` — suprime o prompt de sistema padrão |
| Gemini | Define `GEMINI_SYSTEM_MD=/dev/null` — sobrescreve o prompt de sistema integrado com um arquivo vazio |

O padrão é `false`.

### Pesos de Token Personalizados (`token-weights`)

Sobrescreva os multiplicadores de custo de token integrados usados ao computar [Tokens Efetivos](/gh-aw/reference/effective-tokens-specification/). Útil quando seu fluxo de trabalho usa um modelo personalizado não na lista integrada, ou quando você deseja ajustar as proporções de custo relativo para o seu caso de uso.

```yaml wrap
engine:
  id: claude
  token-weights:
    multipliers:
      my-custom-model: 2.5      # 2.5x o custo do claude-sonnet-4.5
      experimental-llm: 0.8    # Sobrescrever o multiplicador de um modelo existente
    token-class-weights:
      output: 6.0              # Sobrescrever o peso do token de saída (padrão: 4.0)
      cached-input: 0.05       # Sobrescrever o peso de entrada cacheada (padrão: 0.1)
```

`multipliers` é um mapa de nomes de modelo para multiplicadores numéricos relativos a `claude-sonnet-4.5` (= 1.0). Chaves não diferenciam maiúsculas de minúsculas e suportam correspondência de prefixo. `token-class-weights` sobrescreve os pesos por classe aplicados antes do multiplicador do modelo; os padrões são `input: 1.0`, `cached-input: 0.1`, `output: 4.0`, `reasoning: 4.0`, `cache-write: 1.0`.

Pesos personalizados são incorporados no YAML do fluxo de trabalho compilado e lidos por `gh aw logs` e `gh aw audit` ao analisar execuções.

## Configuração de Timeout

Repositórios com ciclos longos de build ou teste exigem ajuste cuidadoso de timeout em múltiplos níveis. Esta seção documenta os botões de timeout disponíveis para cada motor.

### Timeout em nível de Job (`timeout-minutes`)

`timeout-minutes` define o tempo máximo de relógio para todo o job do agente. Este é o botão primário para repositórios com longos tempos de build. O padrão é 20 minutos.

```yaml wrap
timeout-minutes: 60   # permitir até 60 minutos para o job do agente
```

Veja [Longos Tempos de Build](/gh-aw/reference/sandbox/#long-build-times) na referência do Sandbox para valores recomendados e exemplos concretos, incluindo um fluxo de trabalho C++ de 30 minutos.

### Timeout por chamada de ferramenta (`tools.timeout`)

`tools.timeout` limita por quanto tempo qualquer chamada de ferramenta individual pode ser executada, em segundos. Útil quando comandos `bash` individuais (builds, suítes de teste) levam mais tempo que o padrão de um motor:

```yaml wrap
tools:
  timeout: 300   # 5 minutos por chamada de ferramenta
```

| Motor | Timeout de ferramenta padrão |
|--------|----------------------|
| Copilot | não imposto pelo gh-aw (gerenciado pelo motor) |
| Claude | 60 s |
| Codex | 120 s |
| Gemini | não imposto pelo gh-aw (gerenciado pelo motor) |
| Crush | não imposto pelo gh-aw (gerenciado pelo motor) |

Veja [Configuração de Timeout de Ferramenta](/gh-aw/reference/tools/#tool-timeout-configuration) para documentação completa, incluindo `tools.startup-timeout`.

### Controles de Timeout por Motor

#### Copilot

O Copilot não expõe um limite de tempo de relógio por turno diretamente. Use `max-continuations` para controlar quantas execuções de agente sequenciais são permitidas no modo piloto automático, e `timeout-minutes` para o orçamento geral do job:

```yaml wrap
engine:
  id: copilot
max-continuations: 3   # até 3 execuções de piloto automático consecutivas
timeout-minutes: 60
```

#### Claude

Claude suporta `max-turns` para limitar o número de iterações de IA por execução. Defina-o junto com `tools.timeout` para controlar tanto a amplitude (número de turnos) quanto a profundidade (tempo por chamada de ferramenta):

```yaml wrap
engine:
  id: claude
max-turns: 20          # número máximo de iterações agentic
tools:
  timeout: 600         # 10 minutos por chamada bash/ferramenta
timeout-minutes: 60
```

A variável de ambiente `CLAUDE_CODE_MAX_TURNS` é um equivalente da CLI do Claude Code para `max-turns`. Quando `max-turns` é definido no frontmatter, o gh-aw o passa para a CLI do Claude automaticamente — você não precisa definir essa variável de ambiente separadamente.

#### Codex, Gemini e Crush

Esses motores não suportam `max-turns` ou `max-continuations`. Use `timeout-minutes` e `tools.timeout` para limitar a execução:

```yaml wrap
tools:
  timeout: 300
timeout-minutes: 60
```

### Tabela de Resumo

| Botão de timeout | Copilot | Claude | Codex | Gemini | Crush | OpenCode | Notas |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| `timeout-minutes` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Relógio de parede de nível de job |
| `tools.timeout` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Limite por chamada de ferramenta (segundos) |
| `tools.startup-timeout` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Limite de inicialização do servidor MCP |
| `max-turns` | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | Orçamento de iteração (apenas Claude) |
| `max-continuations` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | Orçamento de execução de piloto automático (apenas Copilot) |

## Modelo de Segurança de Aplicação de Ferramenta do Claude

O Claude Code usa um dos dois modos de permissão em tempo de execução, e o modo selecionado determina se a allowlist `tools:` declarada é aplicada:

### Modo `acceptEdits` (padrão)

Por padrão, o gh-aw inicia o Claude Code com `--permission-mode acceptEdits`. Neste modo, o Claude honra a flag `--allowed-tools`. A configuração declarada `tools:` e `mcp-servers: allowed:` do fluxo de trabalho é compilada em uma allowlist explícita e passada para a CLI do Claude. Apenas as ferramentas listadas lá são acessíveis ao agente.

### Modo `bypassPermissions` (bash irrestrito)

Quando o fluxo de trabalho concede acesso bash irrestrito — `bash: "*"`, `bash: [":*"]` ou `bash: null` — o gh-aw muda para `--permission-mode bypassPermissions`. **Neste modo, o Claude Code ignora silenciosamente `--allowed-tools`.** Toda ferramenta exposta pelo gateway MCP é alcançável independentemente da configuração de ferramenta declarada do fluxo de trabalho.

> [!WARNING]
> Não confie em `tools:` ou `mcp-servers: allowed:` para garantias de segurança quando bash irrestrito é concedido. No modo `bypassPermissions`, o agente já pode executar comandos de shell arbitrários, então `--allowed-tools` não fornece nenhum limite adicional significativo.

### Aplicação no lado do gateway

O **filtro `allowed:` do gateway MCP é o único limite de ferramenta eficaz no modo `bypassPermissions`** (e uma segunda camada de aplicação no modo `acceptEdits`). O gh-aw compila a lista `allowed:` de cada entrada `mcp-servers:` na configuração do gateway antes que o agente inicie. O gateway aplica esta lista no lado do servidor, independentemente do que o agente solicita.

```yaml wrap
mcp-servers:
  notion:
    container: "mcp/notion"
    allowed: ["search_pages", "get_page"]   # aplicado no nível do gateway
```

### Resumo

| Configuração do fluxo de trabalho | Modo de permissão | `--allowed-tools` aplicado? | Gateway `allowed:` aplicado? |
|---|---|:---:|:---:|
| Sem bash irrestrito | `acceptEdits` | ✅ Sim | ✅ Sim |
| `bash: "*"` / `bash: [":*"]` / `bash: null` | `bypassPermissions` | ❌ Não | ✅ Sim |

Para fluxos de trabalho que devem restringir quais ferramentas MCP são acessíveis, especifique sempre `allowed:` em cada entrada `mcp-servers:`. Isso se aplica independentemente de bash irrestrito ser usado ou não.

## Documentação relacionada

- [Frontmatter](/gh-aw/reference/frontmatter/) - Referência completa de configuração
- [Ferramentas](/gh-aw/reference/tools/) - Ferramentas disponíveis e servidores MCP
- [Guia de Segurança](/gh-aw/introduction/architecture/) - Considerações de segurança para motores de IA
- [MCPs](/gh-aw/guides/mcps/) - Configuração do Protocolo de Contexto de Modelo
- [Longos Tempos de Build](/gh-aw/reference/sandbox/#long-build-times) - Ajuste de timeout para repositórios grandes
- [Executores Auto-hospedados](/gh-aw/guides/self-hosted-runners/) - Hardware rápido para fluxos de trabalho de longa execução
