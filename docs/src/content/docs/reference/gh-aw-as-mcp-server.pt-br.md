---
title: GH-AW como um Servidor MCP
description: Use o servidor MCP gh-aw para expor ferramentas da CLI a agentes de IA via Model Context Protocol, permitindo o gerenciamento seguro de fluxos de trabalho.
sidebar:
  order: 400
---

O comando `gh aw mcp-server` expõe comandos da CLI do GitHub Agentic Workflows como ferramentas MCP, permitindo que sistemas de chat e fluxos de trabalho gerenciem fluxos de trabalho agentic programaticamente.

Inicie o servidor:

```bash wrap
gh aw mcp-server
```

Ou configure para qualquer host de Model Context Protocol (MCP):

```yaml wrap
command: gh
args: [aw, mcp-server]
```

## Opções de Configuração

### Modo de Servidor HTTP

Execute com transporte HTTP/SSE usando `--port`:

```bash wrap
gh aw mcp-server --port 8080
```

### Validação de Ator

Controle o acesso a logs e ferramentas de auditoria com base em permissões do repositório usando `--validate-actor`:

```bash wrap
gh aw mcp-server --validate-actor
```

Quando habilitado, as ferramentas de logs e auditoria exigem acesso de escrita/manutenção/administração ao repositório. O servidor lê as variáveis de ambiente `GITHUB_ACTOR` e `GITHUB_REPOSITORY` e armazena em cache os resultados da verificação de permissão por 1 hora. Sem validação (padrão), todas as ferramentas estão disponíveis sem verificações.

## Configuração com o Agente do GitHub Copilot

Configure o Agente do GitHub Copilot para usar o servidor MCP gh-aw:

```bash wrap
gh aw init
```

Isso cria `.github/workflows/copilot-setup-steps.yml` que configura Go, GitHub CLI e a extensão gh-aw antes do início das sessões de agente, tornando as ferramentas de gerenciamento de fluxo de trabalho disponíveis para o agente. A integração do servidor MCP é habilitada por padrão. Use `gh aw init --no-mcp` para pular a configuração do MCP.

## Configuração com a CLI do Copilot

Para adicionar o servidor MCP na sessão interativa da CLI do Copilot, inicie o `copilot` e execute:

```text
/mcp add github-agentic-workflows gh aw mcp-server
```

## Configuração com VS Code

Configure o Copilot Chat do VS Code para usar o servidor MCP gh-aw:

```bash wrap
gh aw init
```

Isso cria `.github/mcp.json` e `.github/workflows/copilot-setup-steps.yml`. A integração do servidor MCP é habilitada por padrão. Use `gh aw init --no-mcp` para pular a configuração do MCP.

Alternativamente, crie `.github/mcp.json` manualmente:

```json wrap
{
  "mcpServers": {
    "github-agentic-workflows": {
      "command": "gh",
      "args": ["aw", "mcp-server"]
    }
  }
}
```

Recarregue o VS Code após fazer alterações.

## Configuração com Docker

Se `gh` não estiver instalado localmente, use a imagem Docker `ghcr.io/github/gh-aw`. A imagem vem com GitHub CLI e gh-aw pré-instalados e usa `mcp-server` como o comando padrão.

```json wrap
{
  "command": "docker",
  "args": [
    "run", "--rm", "-i",
    "-e", "GITHUB_TOKEN",
    "-e", "GITHUB_ACTOR",
    "ghcr.io/github/gh-aw:latest",
    "mcp-server"
  ]
}
```

Passe seu token do GitHub por meio da variável de ambiente `GITHUB_TOKEN`. Adicione `--validate-actor` ao array `args` para aplicar verificações de permissão com base em `GITHUB_ACTOR`.

## Ferramentas Disponíveis

O servidor MCP expõe as seguintes ferramentas para gerenciamento de fluxo de trabalho:

### `status`

Exibe o status de arquivos de fluxo de trabalho agentic e fluxos de trabalho.

- `pattern` (opcional): Filtra fluxos de trabalho por padrão de nome
- `jq` (opcional): Aplica filtro jq à saída JSON

Retorna um array JSON com os campos `workflow`, `agent`, `compiled`, `status` e `time_remaining`.

### `compile`

Compila fluxos de trabalho Markdown para YAML do GitHub Actions com análise estática opcional.

- `workflows` (opcional): Array de arquivos de fluxo de trabalho para compilar (vazio para todos)
- `strict` (opcional): Aplica validação de modo estrito (padrão: true)
- `fix` (opcional): Aplica correções automáticas de codemod antes de compilar
- `zizmor`, `poutine`, `actionlint` (opcional): Executa scanners/linters de segurança
- `jq` (opcional): Aplica filtro jq à saída JSON

Retorna um array JSON com os campos `workflow`, `valid`, `errors`, `warnings` e `compiled_file`.

> [!NOTE]
> Os scanners `actionlint`, `zizmor` e `poutine` usam imagens Docker que são baixadas no primeiro uso. Se as imagens ainda estiverem sendo baixadas, a ferramenta retorna uma mensagem "Docker images are being downloaded. Please wait and retry the compile command.". Aguarde 15–30 segundos e tente a solicitação novamente.

### `logs`

Baixa e analisa logs de fluxo de trabalho com tratamento de timeout e proteções de tamanho.

- `workflow_name` (opcional): Nome do fluxo de trabalho (vazio para todos)
- `count` (opcional): Número de execuções para baixar (padrão: 100)
- `start_date`, `end_date` (opcional): Filtro de intervalo de data (YYYY-MM-DD ou delta como `-1w`)
- `engine`, `firewall`, `no_firewall`, `branch` (opcional): Filtros de execução
- `after_run_id`, `before_run_id` (opcional): Paginação por ID de execução
- `timeout` (opcional): Segundos máximos para baixar (padrão: 50)
- `max_tokens` (opcional): Proteção de token de saída (padrão: 12000)
- `jq` (opcional): Aplica filtro jq à saída JSON

Retorna JSON com dados e métricas de execução de fluxo de trabalho, ou parâmetros de continuação se ocorreu timeout.

### `audit`

Investiga uma execução de fluxo de trabalho, job ou passo específico e gera um relatório detalhado.

- `run_id_or_url` (obrigatório): ID de execução numérico, URL de execução, URL de job ou URL de passo
- `jq` (opcional): Aplica filtro jq à saída JSON

Retorna JSON com `overview`, `metrics`, `jobs`, `downloaded_files`, `missing_tools`, `mcp_failures`, `errors`, `warnings`, `tool_usage` e `firewall_analysis`.

### `checks`

Classifica o estado de verificação de CI para um pull request e retorna um resultado normalizado.

- `pr_number` (obrigatório): Número do pull request para classificar verificações de CI
- `repo` (opcional): Repositório no formato `owner/repo` (padrão para o repositório atual)

Retorna JSON com:
- `state`: Estado de verificação agregado em todas as execuções de verificação e status de commit
- `required_state`: Estado derivado apenas de execuções de verificação e status de commit de política (ignora status de terceiros opcionais como implantações Vercel/Netlify)
- `pr_number`, `head_sha`, `check_runs`, `statuses`, `total_count`

Estados normalizados: `success`, `failed`, `pending`, `no_checks`, `policy_blocked`.

Use `required_state` como o veredito de CI autoritativo em repositórios com integrações de implantação opcionais.

### `mcp-inspect`

Inspeciona servidores MCP em fluxos de trabalho e lista ferramentas, recursos e raízes disponíveis.

- `workflow_file` (opcional): Arquivo de fluxo de trabalho para inspecionar (vazio para listar todos os fluxos de trabalho com servidores MCP)
- `server` (opcional): Filtra para servidor MCP específico
- `tool` (opcional): Mostra informações detalhadas sobre uma ferramenta específica (requer `server`)

Retorna texto formatado listando servidores MCP, suas ferramentas/recursos/raízes, disponibilidade de segredo e informações detalhadas da ferramenta quando `tool` é especificado.

### `add`

Adiciona fluxos de trabalho de repositórios remotos para `.github/workflows`.

- `workflows` (obrigatório): Array de especificações de fluxo de trabalho no formato `owner/repo/workflow-name[@version]`
- `number` (opcional): Cria múltiplas cópias numeradas
- `name` (opcional): Nome para o fluxo de trabalho adicionado (sem extensão `.md`)

### `update`

Atualiza fluxos de trabalho de seus repositórios de origem e verifica atualizações do gh-aw.

- `workflows` (opcional): Array de IDs de fluxo de trabalho para atualizar (vazio para todos)
- `major` (opcional): Permite atualizações de versão maior
- `force` (opcional): Força a atualização mesmo se nenhuma alteração for detectada

### `fix`

Aplica correções automáticas estilo codemod a arquivos de fluxo de trabalho.

- `workflows` (opcional): Array de IDs de fluxo de trabalho para corrigir (vazio para todos)
- `write` (opcional): Grava alterações nos arquivos (padrão é dry-run)
- `list_codemods` (opcional): Lista codemods disponíveis e sai

Codemods disponíveis: `timeout-minutes-migration`, `network-firewall-migration`, `sandbox-agent-false-removal`, `mcp-scripts-mode-removal`, `steps-run-secrets-to-env`.

## Usando GH-AW como um MCP a partir de um Fluxo de Trabalho Agentic

Use o servidor MCP GH-AW dentro de um fluxo de trabalho para permitir autogerenciamento (verificações de status, compilação, análise de log):

```yaml wrap
---
permissions:
  actions: read  # Requerido para a ferramenta agentic-workflows
tools:
  agentic-workflows:
---

Verifique o status do fluxo de trabalho, baixe logs e audite falhas.
```
