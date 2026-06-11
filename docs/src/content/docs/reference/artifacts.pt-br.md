---
title: Artefatos
description: Referência completa para nomes de artefatos, estruturas de diretório e padrões de download usados pelo GitHub Agentic Workflows.
sidebar:
  order: 298
---

O GitHub Agentic Workflows carrega vários artefatos durante a execução do fluxo de trabalho. Esta referência documenta cada nome de artefato, seu conteúdo e como acessar os dados — especialmente para fluxos de trabalho a jusante que usam `gh run download` diretamente em vez de `gh aw logs`.

## Referência Rápida

| Nome do Artefato | Constante | Tipo | Descrição |
|---------------|----------|------|-------------|
| `agent` | `constants.AgentArtifactName` | Multi-arquivo | Saídas de job de agente unificadas (logs, safe outputs, resumo de uso de token) |
| `activation` | `constants.ActivationArtifactName` | Multi-arquivo | Saída de job de ativação (`aw_info.json`, `prompt.txt`, limites de taxa) |
| `firewall-audit-logs` | `constants.FirewallAuditArtifactName` | Multi-arquivo | Logs de auditoria/observabilidade de firewall AWF (uso de token, política de rede, trilha de auditoria) |
| `detection` | `constants.DetectionArtifactName` | Arquivo único | Log de detecção de ameaças (`detection.log`) |
| `safe-output` | `constants.SafeOutputArtifactName` | Legado/back-compat | Artefato de safe output autônomo histórico (`safe_output.jsonl`); em fluxos de trabalho compilados atuais este conteúdo está incluído no artefato `agent` unificado |
| `agent-output` | `constants.AgentOutputArtifactName` | Legado/back-compat | Artefato de saída de agente autônomo histórico (`agent_output.json`); em fluxos de trabalho compilados atuais este conteúdo está incluído no artefato `agent` unificado |
| `aw-info` | — | Arquivo único | Configuração do engine (`aw_info.json`) |
| `prompt` | — | Arquivo único | Prompt gerado (`prompt.txt`) |
| `experiment` | `constants.ExperimentArtifactName` | Multi-arquivo | Estado de experimento A/B (`state.json`) carregado pelo job de ativação quando experimentos são declarados no frontmatter |
| `safe-outputs-items` | `constants.SafeOutputItemsArtifactName` | Arquivo único | Manifesto de itens de safe output |
| `code-scanning-sarif` | `constants.SarifArtifactName` | Arquivo único | Arquivo SARIF para resultados de escaneamento de código |

## Conjuntos de Artefatos

Os comandos `gh aw logs` e `gh aw audit` suportam `--artifacts` para baixar apenas grupos de artefatos específicos:

| Nome do Conjunto | Artefatos Baixados | Caso de Uso |
|----------|---------------------|----------|
| `all` | Tudo | Análise completa (padrão) |
| `agent` | `agent` | Logs e saídas de agente |
| `activation` | `activation` | Dados de ativação (`aw_info.json`, `prompt.txt`) |
| `firewall` | `firewall-audit-logs` | Dados de política de rede e auditoria de firewall |
| `mcp` | `firewall-audit-logs` | Logs de tráfego do gateway MCP |
| `detection` | `detection` | Saída de detecção de ameaças |
| `experiment` | `experiment` | Estado de experimento A/B (apenas presente quando experimentos são declarados) |
| `github-api` | `activation`, `agent` | Logs de limite de taxa da API do GitHub |

```bash
# Baixar apenas artefatos de firewall
gh aw logs <run-id> --artifacts firewall

# Baixar artefatos de agente e firewall
gh aw logs <run-id> --artifacts agent --artifacts firewall

# Baixar tudo (padrão)
gh aw logs <run-id>
```

## `firewall-audit-logs`

O artefato `firewall-audit-logs` é carregado por **todos os fluxos de trabalho habilitados para firewall**. Ele contém logs de auditoria e observabilidade estruturados do AWF (Agente Workflow Firewall).

> **⚠️ Importante:** Este artefato é **separado** do artefato `agent`. Dados de uso de token (`token-usage.jsonl`) vivem aqui, não no artefato `agent`.

### Estrutura de Diretório

```
firewall-audit-logs/
├── api-proxy-logs/
│   └── token-usage.jsonl        ← Dados de uso de token (tokens de entrada/saída/cache por solicitação de API)
├── squid-logs/
│   └── access.log               ← Log de política de rede (decisões de permitir/negar domínio)
├── audit.jsonl                  ← Trilha de auditoria de firewall (correspondências de política, avaliações de regra)
└── policy-manifest.json         ← Snapshot de configuração de política
```

### Acessando Dados de Uso de Token

**Recomendado: Use `gh aw logs`**

```bash
# Baixar e analisar dados de firewall
gh aw logs <run-id> --artifacts firewall

# Saída como JSON para script
gh aw logs <run-id> --artifacts firewall --json
```

**Download direto com `gh run download`:**

```bash
# Baixar o artefato firewall-audit-logs
gh run download <run-id> -n firewall-audit-logs

# Dados de uso de token estão em:
cat firewall-audit-logs/api-proxy-logs/token-usage.jsonl

# Log de acesso de rede está em:
cat firewall-audit-logs/squid-logs/access.log

# Trilha de auditoria está em:
cat firewall-audit-logs/audit.jsonl

# Manifesto de política está em:
cat firewall-audit-logs/policy-manifest.json
```

### Erro Comum

Fluxos de trabalho a jusante às vezes baixam `agent-artifacts` ou `agent` esperando encontrar `token-usage.jsonl`. Isso retornará silenciosamente nenhum dado — o arquivo de uso de token está apenas no artefato `firewall-audit-logs`.

```bash
# ❌ ERRADO — token-usage.jsonl NÃO está no artefato de agente
gh run download <run-id> -n agent
cat agent/token-usage.jsonl  # Arquivo não encontrado!

# ✅ CORRETO — baixar de firewall-audit-logs
gh run download <run-id> -n firewall-audit-logs
cat firewall-audit-logs/api-proxy-logs/token-usage.jsonl
```

### Esquemas JSON

Os arquivos JSONL neste artefato são descritos por JSON Schemas versionados publicados por [github/gh-aw-firewall](https://github.com/github/gh-aw-firewall). Cada registro inclui um campo `_schema` (por exemplo `"audit/v0.26.0"`) para que consumidores possam identificar o tipo de registro e a versão AWF.

| Arquivo | Ativo de Schema | URL Fixada |
|------|--------------|------------|
| `audit.jsonl` | `audit.schema.json` | `https://github.com/github/gh-aw-firewall/releases/download/<tag>/audit.schema.json` |
| `api-proxy-logs/token-usage.jsonl` | `token-usage.schema.json` | `https://github.com/github/gh-aw-firewall/releases/download/<tag>/token-usage.schema.json` |

Use `releases/latest/download/` no lugar de uma tag específica para rastrear o release publicado mais recente. Schemas são versionados pela tag de release do AWF; consumidores devem corresponder `_schema` por prefixo (por exemplo `_schema.startsWith("audit/")`) para que mudanças aditivas permaneçam não quebráveis.

## `agent`

O artefato `agent` unificado contém todas as saídas de job do agente.

### Conteúdo

- Logs de execução do agente
- Dados de safe output (`agent_output.json`)
- Logs de limite de taxa da API do GitHub (`github_rate_limits.jsonl`)
- Resumo de uso de token (`agent_usage.json`) — totais agregados apenas; dados por solicitação estão em `firewall-audit-logs`
- `otel.jsonl` — Mirror de span OTLP escrito pelos exportadores de span JavaScript do gh-aw (apenas presente quando `observability.otlp` está configurado)
- `copilot-otel.jsonl` — Spans OTLP emitidos pelo Copilot CLI (apenas presente quando `observability.otlp` está configurado)

Para configuração OTLP, variáveis de ambiente de tempo de execução e semântica de span, veja
[OpenTelemetry](/gh-aw/reference/open-telemetry/).

## `activation`

O artefato `activation` contém saídas de job de ativação.

### Conteúdo

- `aw_info.json` — Configuração do engine e metadados de fluxo de trabalho
- `prompt.txt` — O prompt gerado enviado ao agente de IA
- `github_rate_limits.jsonl` — Dados de limite de taxa do job de ativação

## `detection`

O artefato `detection` contém saída de detecção de ameaças.

### Conteúdo

- `detection.log` — Resultados de análise de detecção de ameaças

Nome legado: `threat-detection.log` (ainda suportado para compatibilidade retroativa).

## `experiment`

O artefato `experiment` é carregado pelo **job de ativação** apenas quando o frontmatter do fluxo de trabalho declara uma ou mais entradas `experiments`. Ele não está presente em execuções sem experimentos.

### Conteúdo

- `state.json` — Contadores de invocação cumulativos por variante usados para balancear atribuições A/B entre execuções

### Acessando dados de experimento

```bash
# Baixar o artefato de experimento para uma execução específica
gh aw audit <run-id> --artifacts experiment

# Exibir o relatório de auditoria
gh aw audit <run-id>
```

A seção `🧪 A/B Experiments` do relatório de auditoria mostra a variante escolhida para a execução e as contagens cumulativas:

```
🧪 A/B Experiments
  • style = concise (cumulative: concise:5, detailed:4)
```

Veja [Experimentos A/B](/gh-aw/practices/experiments/) para como declarar experimentos no frontmatter do fluxo de trabalho.

## Compatibilidade de Nomes

Nomes de artefatos mudaram entre o upload-artifact v4 e v5. Os comandos `gh aw logs` e `gh aw audit` lidam com ambos os esquemas de nomeação transparentemente:

| Nome Antigo (pré-v5) | Nome Novo (v5+) | Arquivo Dentro |
|--------------------|----------------|-------------|
| `aw_info.json` | `aw-info` | `aw_info.json` |
| `safe_output.jsonl` | `safe-output` | `safe_output.jsonl` |
| `agent_output.json` | `agent-output` | `agent_output.json` |
| `prompt.txt` | `prompt` | `prompt.txt` |
| `threat-detection.log` | `detection` | `detection.log` |

Artefatos de arquivo único são automaticamente achatados para o nível raiz, independentemente do nome do seu diretório de artefato. Artefatos de múltiplos arquivos (`firewall-audit-logs`, `agent`, `activation`, `experiment`) retêm sua estrutura de diretório.

## Prefixos de Chamada de Fluxo de Trabalho

Quando fluxos de trabalho são acionados via `workflow_call`, o GitHub Actions adiciona um hash curto aos nomes dos artefatos (ex: `abc123-firewall-audit-logs`). A CLI lida com isso automaticamente correspondendo nomes de artefatos que terminam com `-{base-name}`.

```bash
# Ambos são reconhecidos como o artefato firewall:
# - firewall-audit-logs           (invocação direta)
# - abc123-firewall-audit-logs    (invocação workflow_call)
```

## Documentação Relacionada

- [Comandos de Auditoria](/gh-aw/reference/audit/) — Baixar e analisar artefatos de execução de fluxo de trabalho
- [Gerenciamento de Custo](/gh-aw/reference/cost-management/) — Rastrear uso de token e gasto de inferência
- [Rede](/gh-aw/reference/network/) — Configuração de firewall e domínio permitir/negar
- [Processo de Compilação](/gh-aw/reference/compilation-process/) — Como os fluxos de trabalho são compilados incluindo etapas de upload de artefato
