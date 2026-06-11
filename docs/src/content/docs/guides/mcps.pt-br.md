---
title: Usando MCPs
description: Como usar servidores Model Context Protocol (MCP) com GitHub Agentic Workflows para conectar agentes de IA ao GitHub, bancos de dados e serviços externos.
sidebar:
  order: 2
---

[Model Context Protocol](/gh-aw/reference/glossary/#mcp-model-context-protocol) (MCP) é um padrão para integração de ferramentas de IA, permitindo que agentes se conectem de forma segura a ferramentas externas, bancos de dados e serviços. O GitHub Agentic Workflows inclui integração nativa com o GitHub MCP e suporta servidores MCP personalizados para serviços externos.

## Início Rápido

Coloque sua primeira integração MCP para rodar em menos de 5 minutos.

### Passo 1: Adicionar Ferramentas do GitHub

Crie um arquivo de fluxo de trabalho em `.github/workflows/meu-fluxo-de-trabalho.md`:

```aw wrap
---
on:
  issues:
    types: [opened]
permissions:
  contents: read
  issues: read
tools:
  github:
    toolsets: [default]
---

# Agente de Análise de Issue

Analise a issue e forneça um resumo de issues existentes similares.
```

A configuração `toolsets: [default]` fornece ao seu fluxo de trabalho agentico acesso a ferramentas de repositório, issue e pull request.

### Passo 2: Compilar e Testar

```bash
gh aw compile meu-fluxo-de-trabalho
gh aw mcp inspect meu-fluxo-de-trabalho
```

## Servidor MCP do GitHub

O servidor MCP do GitHub é embutido em fluxos de trabalho agenticos e fornece acesso abrangente à API do GitHub.

### Conjuntos de Ferramentas Disponíveis (Toolsets)

| Toolset | Descrição | Ferramentas |
|---------|-------------|-------|
| `context` | Informações de usuário e equipe | `get_teams`, `get_team_members` |
| `repos` | Operações de repositório | `get_repository`, `get_file_contents`, `list_commits` |
| `issues` | Gerenciamento de issues | `list_issues`, `create_issue`, `update_issue` |
| `pull_requests` | Operações de PR | `list_pull_requests`, `create_pull_request` |
| `actions` | Execuções de fluxo de trabalho e artefatos | `list_workflows`, `list_workflow_runs` |
| `discussions` | GitHub Discussions | `list_discussions`, `create_discussion` |
| `code_security` | Alertas de segurança | `list_code_scanning_alerts` |
| `users` | Perfis de usuário | `get_me`, `get_user`, `list_users` |

O toolset `default` inclui: `context`, `repos`, `issues`, `pull_requests`. Quando usado em fluxos de trabalho, `[default]` expande-se para toolsets amigáveis à ação que funcionam com tokens do GitHub Actions. Nota: O toolset `users` não está incluído por padrão, pois os tokens do GitHub Actions não suportam operações de usuário.

### Modos de Operação

O modo remoto (`mode: remote`) conecta-se a um servidor hospedado para inicialização mais rápida sem necessidade de Docker. O modo local (`mode: local`) executa no Docker, permitindo a fixação de versão para ambientes offline ou restritos. Veja [Modos de Acesso Remoto vs Local](/gh-aw/reference/github-tools/#github-tools-access-modes).

O servidor MCP do GitHub opera sempre em modo somente leitura. As operações de escrita são tratadas através de [saídas seguras (safe outputs)](/gh-aw/reference/safe-outputs/), que executam em um job separado com permissões controladas.

## Configurando Manualmente um Servidor MCP Personalizado

> [!IMPORTANT]
>
> Servidores MCP personalizados devem ser **somente leitura**. As operações de escrita devem passar por [saídas seguras](/gh-aw/reference/safe-outputs/) ou [Saídas Seguras Personalizadas](/gh-aw/reference/custom-safe-outputs/). Certifique-se de que seu servidor MCP implemente autenticação e autorização para evitar acesso de escrita não autorizado.

Adicione servidores MCP ao frontmatter do seu fluxo de trabalho usando a seção `mcp-servers:`:

```aw wrap
---
on: issues

permissions:
  contents: read

mcp-servers:
  microsoftdocs:
    url: "https://learn.microsoft.com/api/mcp"
    allowed: ["*"]
  
  notion:
    container: "mcp/notion"
    env:
      NOTION_TOKEN: "${{ secrets.NOTION_TOKEN }}"
    allowed:
      - "search_pages"
      - "get_page"
      - "get_database"
      - "query_database"
---

# Seu conteúdo de fluxo de trabalho aqui
```

## Tipos de Servidor MCP Personalizado

### Servidores MCP Stdio

Execute comandos com comunicação stdin/stdout para módulos Python, scripts Node.js e executáveis locais:

```yaml wrap
mcp-servers:
  serena:
    command: "uvx"
    args: ["--from", "git+https://github.com/oraios/serena", "serena"]
    allowed: ["*"]
```

### Servidores MCP em Contêiner Docker

Execute servidores MCP em contêineres com variáveis de ambiente, montagens de volume e restrições de rede:

```yaml wrap
mcp-servers:
  custom-tool:
    container: "mcp/custom-tool:v1.0"
    args: ["-v", "/host/data:/app/data"]  # Montagens de volume antes da imagem
    entrypointArgs: ["serve", "--port", "8080"]  # Args do app após a imagem
    env:
      API_KEY: "${{ secrets.API_KEY }}"
    allowed: ["tool1", "tool2"]

network:
  allowed:
    - defaults
    - api.example.com
```

O campo `container` gera `docker run --rm -i <args> <image> <entrypointArgs>`. 

### Servidores MCP HTTP

Servidores MCP remotos acessíveis via HTTP. Configure a autenticação usando o campo `headers` para chaves de API estáticas, ou o campo `auth` para aquisição dinâmica de tokens:

```yaml wrap
mcp-servers:
  deepwiki:
    url: "https://mcp.deepwiki.com/sse"
    allowed:
      - read_wiki_structure
      - read_wiki_contents
      - ask_question

  authenticated-api:
    url: "https://api.example.com/mcp"
    headers:
      Authorization: "Bearer ${{ secrets.API_TOKEN }}"
    allowed: ["*"]
```

#### Autenticação OIDC do GitHub Actions

Para servidores MCP que aceitam tokens OIDC do GitHub Actions, use o campo `auth` em vez de um valor estático em `headers`. O gateway adquire um JWT de curta duração do endpoint OIDC do GitHub Actions e o injeta como um header `Authorization: Bearer` em cada solicitação de saída.

```yaml wrap
permissions:
  id-token: write   # necessário para aquisição de token OIDC

mcp-servers:
  meu-servidor-seguro:
    url: "https://meu-servidor.example.com/mcp"
    auth:
      type: github-oidc
      audience: "https://meu-servidor.example.com"  # opcional; padrão é a URL do servidor
    allowed: ["*"]
```

O campo `auth.type: github-oidc` é válido apenas em servidores HTTP. O servidor MCP é responsável por validar o token; o gateway atua como um encaminhador de token. Veja [MCP Gateway — Autenticação Upstream](/gh-aw/reference/mcp-gateway/#76-upstream-authentication-oidc) para detalhes completos da especificação.

### Servidores MCP Baseados em Registro

Referencie servidores MCP do registro GitHub MCP (o campo `registry` fornece metadados para ferramentas e não é imposto pelo gh-aw):

```yaml wrap
mcp-servers:
  markitdown:
    registry: https://api.mcp.github.com/v0/servers/microsoft/markitdown
    container: "ghcr.io/microsoft/markitdown"
    allowed: ["*"]
```

## Filtragem de Ferramenta MCP

Use `allowed:` para especificar quais ferramentas estão disponíveis, ou `["*"]` para permitir todas:

```yaml wrap
mcp-servers:
  notion:
    container: "mcp/notion"
    allowed: ["search_pages", "get_page"]  # ou ["*"] para permitir todas
```

O filtro `allowed:` é imposto no **nível do gateway MCP** — o gateway expõe apenas as ferramentas listadas ao agente. Essa imposição aplica-se independentemente de qual engine de IA ou modo de permissão esteja em uso.

## Configurações MCP Compartilhadas

Especificações de servidor MCP pré-configuradas estão disponíveis em [`.github/workflows/shared/mcp/`](https://github.com/github/gh-aw/tree/main/.github/workflows/shared/mcp) e podem ser copiadas ou importadas diretamente. Exemplos incluem:

| Servidor MCP | Caminho de Importação | Principais Capacidades |
|------------|-------------|------------------|
| **Jupyter** | `shared/mcp/jupyter.md` | Executar código, gerenciar notebooks, visualizar dados |
| **Drain3** | `shared/mcp/drain3.md` | Mineração de padrões de log com 8 ferramentas incluindo `index_file`, `list_clusters`, `find_anomalies` |
| **AgentDB** | `shared/mcp/agentdb.md` | Recuperação semântica e híbrida sobre corpora coletados pelo agente (por exemplo, discussões, issues), com suporte por armazenamento em tempo de execução em `AGENTDB_PATH` |
| **Outros** | `shared/mcp/*.md` | AST-Grep, Azure, Brave Search, Context7, DataDog, DeepWiki, Fabric RTI, MarkItDown, Microsoft Docs, Notion, Sentry, Serena, Server Memory, Slack, Tavily |

## Adicionando Servidores MCP do Registro

Use `gh aw mcp add` para navegar e adicionar servidores do registro GitHub MCP (padrão: `https://api.mcp.github.com/v0`):

```bash wrap
gh aw mcp add                                                                    # Listar servidores disponíveis
gh aw mcp add meu-fluxo-de-trabalho makenotion/notion-mcp-server                 # Adicionar servidor
gh aw mcp add meu-fluxo-de-trabalho makenotion/notion-mcp-server --transport stdio         # Especificar transporte
gh aw mcp add meu-fluxo-de-trabalho makenotion/notion-mcp-server --tool-id meu-notion       # ID de ferramenta personalizado
gh aw mcp add meu-fluxo-de-trabalho nome-servidor --registry https://meu.registro.com/v1  # Registro personalizado
```

## Exemplos Práticos

### Exemplo 1: Triagem Básica de Issue

```aw wrap
---
on:
  issues:
    types: [opened]
permissions:
  contents: read
  issues: read
tools:
  github:
    toolsets: [default]
safe-outputs:
  add-comment:
---

# Agente de Triagem de Issue

Analise a issue #${{ github.event.issue.number }} e adicione um comentário com categoria, issues relacionadas e labels sugeridos.
```

### Exemplo 2: Auditoria de Segurança com Discussões

```aw wrap
---
on: weekly on sunday
permissions:
  contents: read
  security-events: read
  discussions: write
tools:
  github:
    toolsets: [default, code_security, discussions]
safe-outputs:
  create-discussion:
    category: "Security"
    title-prefix: "[security-scan] "
---

# Agente de Auditoria de Segurança

Revise alertas de varredura de código e crie discussões de segurança semanais com as descobertas.
```

## Depuração e Resolução de Problemas

Inspecione configurações MCP com comandos da CLI: `gh aw mcp inspect meu-fluxo-de-trabalho` (adicione `--server <nome> --verbose` para detalhes) ou `gh aw mcp list-tools <servidor> meu-fluxo-de-trabalho`.

Para depuração avançada, importe `shared/mcp-debug.md` para acessar ferramentas de diagnóstico e a saída segura personalizada `report_diagnostics_to_pull_request`.

**Problemas comuns**: Falhas de conexão (verifique sintaxe, variáveis de ambiente, rede) ou ferramenta não encontrada (verifique a configuração de toolsets ou a lista `allowed` com `gh aw mcp inspect`).

## Documentação Relacionada

- [Scripts MCP](/gh-aw/reference/mcp-scripts/) - Defina ferramentas inline personalizadas sem servidores MCP externos
- [Ferramentas](/gh-aw/reference/tools/) - Referência completa de ferramentas
- [Comandos da CLI](/gh-aw/setup/cli/) - Comandos da CLI incluindo `mcp inspect`
- [Importações](/gh-aw/reference/imports/) - Modularizando fluxos de trabalho com inclusões
- [Frontmatter](/gh-aw/reference/frontmatter/) - Todas as opções de configuração
- [Estrutura do Fluxo de Trabalho](/gh-aw/reference/workflow-structure/) - Organização de diretório
- [Especificação do Model Context Protocol](https://github.com/modelcontextprotocol/specification)
- [Servidor MCP do GitHub](https://github.com/github/github-mcp-server)
