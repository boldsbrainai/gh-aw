---
name: debugging-workflows
description: Depure fluxos de trabalho gh-aw usando logs de execução, auditorias e triagem de falhas.
---


# Depuração de Fluxos de Trabalho Agentic do GitHub

Use este guia para depurar Fluxos de Trabalho Agentic do GitHub: baixe e analise logs, audite execuções e rastreie o comportamento do fluxo de trabalho.

## Índice

- [Início Rápido](#início-rápido)
- [Baixando Logs de Fluxo de Trabalho](#baixando-logs-de-fluxo-de-trabalho)
- [Auditando Execuções Específicas](#auditando-execuções-específicas)
- [Como Funcionam os Fluxos de Trabalho Agentic](#como-funcionam-os-fluxos-de-trabalho-agentic)
- [Problemas Comuns e Soluções](#problemas-comuns-e-soluções)
- [Técnicas Avançadas de Depuração](#técnicas-avançadas-de-depuração)
- [Comandos de Referência](#comandos-de-referência)

## Início Rápido

### Baixe Logs de Execuções Recentes

```bash
# Baixe logs das últimas 24 horas
gh aw logs --start-date -1d -o /tmp/workflow-logs

# Baixe logs para um fluxo de trabalho específico
gh aw logs weekly-research --start-date -1d

# Baixe logs com saída JSON para análise programática
gh aw logs --json
```

### Audite uma Execução Específica

```bash
# Audite pelo ID da execução
gh aw audit 1234567890

# Audite a partir de uma URL de GitHub Actions
gh aw audit https://github.com/owner/repo/actions/runs/1234567890

# Audite com saída JSON
gh aw audit 1234567890 --json
```

## Baixando Logs de Fluxo de Trabalho

O comando `gh aw logs` baixa artefatos e logs de execução de fluxo de trabalho do GitHub Actions para análise.

### Uso Básico

```bash
# Baixe logs para todos os fluxos de trabalho (últimas 10 execuções)
gh aw logs

# Baixe logs para um fluxo de trabalho específico
gh aw logs <workflow-name>

# Baixe com diretório de saída personalizado
gh aw logs -o ./my-logs
```

### Opções de Filtro

```bash
# Filtre por intervalo de datas
gh aw logs --start-date 2024-01-01 --end-date 2024-01-31
gh aw logs --start-date -1w                    # Última semana
gh aw logs --start-date -1mo                   # Último mês

# Filtre por engine de IA
gh aw logs --engine copilot
gh aw logs --engine claude
gh aw logs --engine codex

# Filtre por contagem
gh aw logs -c 5                                # Últimas 5 execuções

# Filtre por branch/tag
gh aw logs --ref main
gh aw logs --ref feature-xyz

# Filtre por intervalo de ID de execução
gh aw logs --after-run-id 1000 --before-run-id 2000

# Filtre execuções com firewall habilitado
gh aw logs --firewall                          # Apenas com firewall habilitado
gh aw logs --no-firewall                       # Apenas sem firewall
```

### Opções de Saída

```bash
# Gere resumo JSON
gh aw logs --json

# Analise logs de agente e gere relatórios Markdown
gh aw logs --parse

# Gere gráfico de sequência de ferramentas Mermaid
gh aw logs --tool-graph

# Defina tempo limite de download
gh aw logs --timeout 300                       # Tempo limite de 5 minutos
```

### Artefatos Baixados

Ao executar `gh aw logs`, os seguintes artefatos são baixados para cada execução:

| Arquivo | Descrição |
|------|-------------|
| `aw_info.json` | Configuração do engine e metadados do fluxo de trabalho |
| `safe_output.jsonl` | Conteúdo final da saída do agente (quando não vazio) |
| `agent_output/` | Diretório de logs do agente |
| `agent-stdio.log` | Logs de saída/erro padrão do agente |
| `aw.patch` | Patch git das alterações feitas durante a execução |
| `workflow-logs/` | Logs de jobs do GitHub Actions (organizados por job) |
| `summary.json` | Métricas completas e dados de execução para todas as execuções |

### Exemplo: Analise Falhas Recentes

```bash
# Baixe execuções falhas da última semana
gh aw logs --start-date -1w -o /tmp/debug-logs

# Verifique o resumo para padrões
cat /tmp/debug-logs/summary.json | jq '.runs[] | select(.conclusion == "failure")'
```

## Auditando Execuções Específicas

O comando `gh aw audit` investiga uma única execução de fluxo de trabalho em detalhes, baixando artefatos, detectando erros e gerando um relatório.

### Uso Básico

```bash
# Audite pelo ID numérico da execução
gh aw audit 1234567890

# Audite a partir da URL do GitHub Actions
gh aw audit https://github.com/owner/repo/actions/runs/1234567890

# Audite a partir da URL do job (extrai o primeiro passo com falha)
gh aw audit https://github.com/owner/repo/actions/runs/1234567890/job/9876543210

# Audite a partir da URL do job com passo específico
gh aw audit https://github.com/owner/repo/actions/runs/1234567890/job/9876543210#step:7:1
```

### Opções de Saída

```bash
# Saída JSON para análise programática
gh aw audit 1234567890 --json

# Diretório de saída personalizado
gh aw audit 1234567890 -o ./audit-reports

# Analise logs de agente e logs de firewall
gh aw audit 1234567890 --parse

# Saída detalhada (verbose)
gh aw audit 1234567890 -v
```

### Conteúdo do Relatório de Auditoria

O comando de auditoria fornece:

- **Detecção de Erros**: Erros e avisos dos logs do fluxo de trabalho
- **Uso de Ferramenta MCP**: Estatísticas sobre chamadas de ferramenta pelo agente de IA
- **Ferramentas Faltantes**: Ferramentas que o agente tentou usar, mas não estavam disponíveis
- **Métricas de Execução**: Informações de duração, uso de tokens e custo
- **Análise de Saída Segura (Safe Output)**: Quais operações do GitHub foram tentadas

### Exemplo: Investigar uma Execução com Falha

```bash
# Obtenha relatório detalhado de auditoria
gh aw audit 1234567890 --json > audit.json

# Extraia informações principais
cat audit.json | jq '{
  status: .status,
  conclusion: .conclusion,
  errors: .errors,
  missing_tools: .missing_tools,
  tool_usage: .tool_usage
}'
```

## Como Funcionam os Fluxos de Trabalho Agentic

Compreender a arquitetura do fluxo de trabalho ajuda na depuração.

### Estrutura do Fluxo de Trabalho

Fluxos de trabalho agentic usam um formato de **markdown + YAML frontmatter**:

```markdown
---
on:
  issues:
    types: [opened]
permissions:
  issues: write
timeout-minutes: 10
engine: copilot
tools:
  github:
    mode: remote
    toolsets: [default]
safe-outputs:
  create-issue:
    labels: [ai-generated]
---

# Título do Fluxo de Trabalho

Instruções em linguagem natural para o agente de IA.

Use o contexto do GitHub como ${{ github.event.issue.number }}.
```

### Fluxo de Execução

```
1. Evento de Acionamento (issue aberta, PR criado, agendamento, etc.)
     ↓
2. Job de Ativação
   - Valida permissões
   - Processa mcp-scripts
   - Sanitiza contexto
     ↓
3. Job do Agente de IA
   - Carrega servidores e ferramentas MCP
   - Executa o agente de IA com o prompt
   - Agente faz chamadas de ferramenta
   - Agente produz saída
     ↓
4. Job de Saídas Seguras (Safe Outputs)
   - Processa saída do agente
   - Cria recursos do GitHub (issues, PRs, etc.)
   - Aplica etiquetas, comentários
     ↓
5. Conclusão
   - Resumo do fluxo de trabalho gerado
   - Artefatos enviados
```

### Componentes Principais

| Componente | Objetivo | Configuração |
|-----------|---------|---------------|
| **Engine** | Modelo de IA a ser usado | `engine: copilot`, `claude`, `codex` |
| **Tools** | APIs disponíveis para o agente | Seção `tools:` com servidores MCP |
| **MCP Scripts** | Contexto passado para o agente | `mcp-scripts:` com expressões do GitHub |
| **Safe-Outputs** | Recursos que o agente pode criar | `safe-outputs:` com operações permitidas |
| **Permissions** | Permissões de token do GitHub | Bloco `permissions:` |
| **Network** | Acesso de rede permitido | `network:` com listas de domínio/ecossistema |

### Processo de Compilação

```bash
# Compile o fluxo de trabalho para YAML do GitHub Actions
gh aw compile <workflow-name>

# Resultado: .github/workflows/<name>.md → .github/workflows/<name>.lock.yml
```

O arquivo `.lock.yml` é o fluxo de trabalho real do GitHub Actions que é executado.

## Problemas Comuns e Soluções

### Erros de Ferramenta Faltante

**Sintomas**:
- Erro: "Tool 'github:read_issue' not found"
- Agente não consegue acessar APIs do GitHub

**Solução**: Adicione a configuração do servidor MCP do GitHub:

```yaml
tools:
  github:
    mode: remote
    toolsets: [default]
```

### Erros de Permissão

**Sintomas**:
- Erros HTTP 403 (Proibido)
- Erros "Resource not accessible"

**Solução**: Adicione as permissões necessárias:

```yaml
permissions:
  contents: read
  issues: write
  pull-requests: write
```

### Erros de Safe-Input

**Sintomas**:
- "missing tool configuration for mcpscripts-gh"
- Variável de ambiente não disponível

**Solução**: Configure mcp-scripts:

```yaml
mcp-scripts:
  issue:
    script: |
      return { title: process.env.ISSUE_TITLE, body: process.env.ISSUE_BODY };
    env:
      ISSUE_TITLE: ${{ github.event.issue.title }}
      ISSUE_BODY: ${{ github.event.issue.body }}
```

### Erros de Safe-Output

**Sintomas**:
- Agente tenta criar recursos, mas falha
- Erros "Safe output not enabled"

**Solução**: Habilite safe-outputs:

```yaml
safe-outputs:
  staged: false  # Defina como false para criar recursos de fato
  create-issue:
    labels: [ai-generated]
```

### Erros de Acesso à Rede

**Sintomas**:
- Negações de firewall
- URLs aparecendo como "(redacted)"

**Solução**: Configure o acesso à rede:

```yaml
network:
  allowed:
    - defaults
    - python    # Para PyPI
    - node      # Para npm
    - "api.example.com"  # Domínios personalizados
```

### Erros de Tempo Limite (Timeout)

**Sintomas**:
- Fluxo de trabalho excede limite de tempo
- Agente entra em loop ou trava

**Solução**: Aumente o tempo limite ou otimize o prompt:

```yaml
timeout-minutes: 30  # Aumente a partir do padrão
```

## Técnicas Avançadas de Depuração

### Pesquisando Execuções em Andamento

Quando uma execução ainda está em andamento:

```bash
# Faça polling até a conclusão
while true; do
  output=$(gh aw audit <run-id> --json 2>&1)
  if echo "$output" | grep -q '"status":.*"\(completed\|failure\|cancelled\)"'; then
    echo "$output"
    break
  fi
  echo "⏳ Execução ainda em andamento. Aguardando 45 segundos..."
  sleep 45
done
```

### Inspecionando Configuração MCP

```bash
# Inspecione servidores MCP para um fluxo de trabalho
gh aw mcp inspect <workflow-name>

# Liste todos os fluxos de trabalho com servidores MCP
gh aw mcp list
```

### Verificando Status do Fluxo de Trabalho

```bash
# Mostre status de todos os fluxos de trabalho agentic
gh aw status
```

### Baixando Artefatos Específicos

```bash
# Baixe apenas o artefato de log do agente
GH_REPO=owner/repo gh run download <run-id> -n agent-stdio.log
```

### Inspecionando Logs de Job

```bash
# Veja logs de job específicos
gh run view <run-id>
gh run view --job <job-id> --log
```

### Analisando Logs de Firewall

```bash
# Analise logs de firewall para problemas de rede
gh aw logs --parse

# Verifique execuções com firewall habilitado
gh aw logs --firewall
```

### Compilação em Modo de Depuração

```bash
# Compile com saída detalhada
gh aw compile --verbose

# Compile com verificações de segurança rigorosas
gh aw compile --strict

# Execute scanners de segurança
gh aw compile --actionlint --zizmor --poutine
```

## Comandos de Referência

### Comandos de Análise de Log

| Comando | Descrição |
|---------|-------------|
| `gh aw logs` | Baixe logs para todos os fluxos de trabalho |
| `gh aw logs <workflow>` | Baixe logs para fluxo de trabalho específico |
| `gh aw logs --json` | Saída como JSON |
| `gh aw logs --start-date -1d` | Filtre por data |
| `gh aw logs --engine copilot` | Filtre por engine |
| `gh aw logs --parse` | Gere relatórios Markdown |

### Comandos de Auditoria

| Comando | Descrição |
|---------|-------------|
| `gh aw audit <run-id>` | Audite execução específica |
| `gh aw audit <url>` | Audite a partir de URL do GitHub |
| `gh aw audit <run-id> --json` | Saída como JSON |
| `gh aw audit <run-id> --parse` | Analise logs para Markdown |

### Comandos MCP

| Comando | Descrição |
|---------|-------------|
| `gh aw mcp list` | Liste fluxos de trabalho com servidores MCP |
| `gh aw mcp inspect <workflow>` | Inspecione configuração MCP |

### Comandos de Status

| Comando | Descrição |
|---------|-------------|
| `gh aw status` | Mostre status de todo fluxo de trabalho |
| `gh aw compile` | Compile todos os fluxos de trabalho |
| `gh aw compile <workflow>` | Compile fluxo de trabalho específico |
| `gh aw compile --strict` | Compile com verificações de segurança |

### Comandos de Execução de Fluxo de Trabalho

| Comando | Descrição |
|---------|-------------|
| `gh aw run <workflow>` | Acione fluxo de trabalho manualmente |
| `gh workflow run <name>.lock.yml` | Método de acionamento alternativo |
| `gh run watch <run-id>` | Monitore fluxo de trabalho em execução |

## Recursos Adicionais

- [Runbook de Monitoramento de Saúde do Fluxo de Trabalho](../../aw/runbooks/workflow-health.md) - Procedimentos de investigação passo a passo
- [Referência de Problemas Comuns](../../../docs/src/content/docs/troubleshooting/common-issues.md) - Problemas encontrados frequentemente
- [Referência de Erros](../../../docs/src/content/docs/troubleshooting/errors.md) - Códigos de erro e soluções
- [Documentação do Servidor MCP do GitHub](../../../skills/github-mcp-server/SKILL.md) - Referência de configuração de ferramentas
