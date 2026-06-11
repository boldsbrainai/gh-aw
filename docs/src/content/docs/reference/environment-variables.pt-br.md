---
title: Variáveis de ambiente
description: Referência para todas as variáveis de ambiente no GitHub Agentic Workflows — configuração da CLI, sobrescritas de modelo, fallbacks de política de proteção e precedência de escopo em nível de fluxo de trabalho
sidebar:
  order: 650
---

Variáveis de ambiente no GitHub Agentic Workflows podem ser definidas em vários escopos, cada um servindo a um propósito específico no ciclo de vida do fluxo de trabalho. Variáveis definidas em escopos mais específicos sobrescrevem aquelas em escopos mais gerais, seguindo as convenções do GitHub Actions enquanto adiciona contextos específicos do AWF.

## Escopos de variáveis de ambiente

O GitHub Agentic Workflows suporta variáveis de ambiente em 13 contextos distintos:

| Escopo | Sintaxe | Contexto | Uso Típico |
| ------- | -------- | --------- | ------------- |
| **Nível de fluxo de trabalho** | `env:` | Todos os jobs | Configuração compartilhada |
| **Nível de Job** | `jobs.<job_id>.env` | Todas as etapas no job | Configuração específica do job |
| **Nível de etapa** | `steps[*].env` | Etapa única | Configuração específica da etapa |
| **Motor** | `engine.env` | Motor de IA | Secrets do motor, timeouts |
| **Contêiner** | `container.env` | Runtime do contêiner | Configurações do contêiner |
| **Serviços** | `services.<id>.env` | Contêineres de serviço | Credenciais de banco de dados |
| **Agente de Sandbox** | `sandbox.agent.env` | Runtime do sandbox | Configuração do sandbox |
| **MCP de Sandbox** | `sandbox.mcp.env` | Gateway Model Context Protocol (MCP) | Depuração MCP |
| **Ferramentas MCP** | `tools.<name>.env` | Processo do servidor MCP | Secrets do servidor MCP |
| **Scripts MCP** | `mcp-scripts.<name>.env` | Execução de script MCP | Tokens específicos da ferramenta |
| **Global Safe Outputs** | `safe-outputs.env` | Todos os jobs de safe-output | Configuração compartilhada de safe-output |
| **Safe Outputs de Job** | `safe-outputs.jobs.<name>.env` | Job de safe-output específico | Configuração específica do job |
| **Etapa do GitHub Actions** | `githubActionsStep.env` | Etapas pré-definidas | Configuração da etapa |

### Exemplos de Configurações

**Configuração compartilhada em nível de fluxo de trabalho:**

```yaml wrap
---
env:
  NODE_ENV: production
  API_ENDPOINT: https://api.example.com
---
```

**Sobrescritas específicas de job:**

```yaml wrap
---
jobs:
  validation:
    env:
      VALIDATION_MODE: strict
    steps:
      - run: npm run build
        env:
          BUILD_ENV: production  # Sobrescreve os níveis de job e fluxo de trabalho
---
```

**Contextos específicos do AWF:**

```yaml wrap
---
# Configuração do motor
engine:
  id: copilot
  env:
    OPENAI_API_KEY: ${{ secrets.CUSTOM_KEY }}

# Servidor MCP com secrets
tools:
  database:
    command: npx
    args: ["-y", "mcp-server-postgres"]
    env:
      DATABASE_URL: ${{ secrets.DATABASE_URL }}

# Safe outputs com PAT personalizado
safe-outputs:
  create-issue:
  env:
    GITHUB_TOKEN: ${{ secrets.CUSTOM_PAT }}
---
```

## Resumo de etapa do agente (`GITHUB_STEP_SUMMARY`)

Agentes podem gravar conteúdo markdown na variável de ambiente `$GITHUB_STEP_SUMMARY` para publicar um resumo formatado visível na visualização de execução do GitHub Actions.

Dentro do sandbox do AWF, `$GITHUB_STEP_SUMMARY` é redirecionado para um arquivo em `/tmp/gh-aw/agent-step-summary.md`. Após a conclusão da execução do agente, o framework anexa automaticamente o conteúdo desse arquivo ao resumo real da etapa do GitHub. A redação de secrets é executada antes que o conteúdo seja publicado.

> [!NOTE]
> Os primeiros 2000 caracteres do resumo são anexados. Se o conteúdo for mais longo, um aviso `[truncated: ...]` é incluído. Escreva seu conteúdo mais importante primeiro.

Exemplo: um agente gravando um resultado de análise breve no resumo da etapa:

```bash
echo "## Análise concluída" >> "$GITHUB_STEP_SUMMARY"
echo "Encontradas 3 questões em 12 arquivos." >> "$GITHUB_STEP_SUMMARY"
```

A saída aparece na guia **Resumo** da execução do fluxo de trabalho do GitHub Actions.

## Variáveis de Runtime Injetadas pelo Sistema

O GitHub Agentic Workflows injeta automaticamente as seguintes variáveis de ambiente em cada etapa de execução do motor agentic (tanto na execução principal do agente quanto na execução de detecção de ameaças). Essas variáveis são somente leitura da perspectiva do agente e são úteis para escrever fluxos de trabalho ou agentes que precisam detectar seu contexto de execução.

| Variável | Valor | Descrição |
| ---------- | ------- | ------------- |
| `GITHUB_AW` | `"true"` | Presente em cada etapa de execução do motor gh-aw. Agentes podem verificar esta variável para confirmar que estão sendo executados dentro de um GitHub Agentic Workflow. |
| `GH_AW_PHASE` | `"agent"` ou `"detection"` | Identifica qual fase de execução está ativa. `"agent"` para a execução principal; `"detection"` para a execução de verificação de segurança de detecção de ameaças que precede a execução principal. |
| `GH_AW_VERSION` | e.g. `"0.40.1"` | A versão do compilador gh-aw que gerou o fluxo de trabalho. Útil para lógica condicional que depende de uma versão mínima de recurso. |

Essas variáveis aparecem ao lado de outras variáveis de contexto `GH_AW_*` no fluxo de trabalho compilado:

```yaml
env:
  GITHUB_AW: "true"
  GH_AW_PHASE: agent        # ou "detection"
  GH_AW_VERSION: "0.40.1"
  GH_AW_PROMPT: /tmp/gh-aw/aw-prompts/prompt.txt
```

> [!NOTE]
> Essas variáveis são injetadas pelo compilador e não podem ser sobrescritas por blocos `env:` definidos pelo usuário no frontmatter do fluxo de trabalho.

## Variáveis de Configuração CLI

Estas variáveis configuram a ferramenta CLI `gh aw`. Defina-as em seu ambiente de shell local ou como variáveis de repositório/organização no GitHub Actions.

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `DEBUG` | desabilitado | Logs de depuração de namespace estilo npm. `DEBUG=*` habilita toda a saída; `DEBUG=cli:*,workflow:*` seleciona namespaces específicos. Exclusões são suportadas: `DEBUG=*,-workflow:test`. Também ativado quando `ACTIONS_RUNNER_DEBUG=true`. |
| `DEBUG_COLORS` | `1` (habilitado) | Defina como `0` para desabilitar cores ANSI na saída de depuração. Cores são desabilitadas automaticamente quando a saída não é um TTY. |
| `ACCESSIBLE` | vazio | Qualquer valor não vazio habilita o modo de acessibilidade, que desabilita spinners e animações. Também habilitado quando `TERM=dumb` ou `NO_COLOR` é definido. |
| `NO_COLOR` | vazio | Qualquer valor não vazio desabilita a saída colorida e habilita o modo de acessibilidade. Segue o padrão [no-color.org](https://no-color.org/). |
| `GH_AW_ACTION_MODE` | auto-detectado | Sobrescreve como o JavaScript é incorporado em fluxos de trabalho compilados. Valores válidos: `dev`, `release`, `script`, `action`. Quando não definido, a CLI auto-detecta o modo apropriado. |
| `GH_AW_FEATURES` | vazio | Lista separada por vírgula de flags de recursos experimentais para habilitar globalmente. Valores no frontmatter `features:` do fluxo de trabalho têm precedência sobre esta variável. |
| `GH_AW_MAX_CONCURRENT_DOWNLOADS` | `10` | Número máximo de downloads paralelos de logs e artefatos para `gh aw logs`. Faixa válida: `1`–`100`. |
| `GH_AW_MCP_SERVER` | não definido | Quando definido, desabilita a verificação de atualização automática. Definido automaticamente quando `gh aw` é executado como um subprocesso de servidor MCP — nenhuma configuração manual necessária. |

**Habilitando logs de depuração:**

```bash
# Todos os namespaces
DEBUG=* gh aw compile

# Namespaces específicos
DEBUG=cli:*,workflow:* gh aw compile

# Sem cores
DEBUG_COLORS=0 DEBUG=* gh aw compile
```

---

## Variáveis de Sobrescrita de Modelo

Estas variáveis sobrescrevem o modelo de IA padrão usado para execuções de agente e detecção de ameaças. Defina-as como variáveis de repositório ou organização do GitHub Actions para aplicar padrões em toda a organização sem modificar o frontmatter do fluxo de trabalho.

> [!NOTE]
> O campo `engine.model:` no frontmatter do fluxo de trabalho tem precedência sobre essas variáveis.

### Execuções de agente

| Variável | Motor |
| --- | --- |
| `GH_AW_MODEL_AGENT_COPILOT` | GitHub Copilot |
| `GH_AW_MODEL_AGENT_CLAUDE` | Anthropic Claude |
| `GH_AW_MODEL_AGENT_CODEX` | OpenAI Codex |
| `GH_AW_MODEL_AGENT_GEMINI` | Google Gemini |
| `GH_AW_MODEL_AGENT_CRUSH` | Crush |
| `GH_AW_MODEL_AGENT_CUSTOM` | Motor personalizado |

### Execuções de detecção

| Variável | Motor |
| --- | --- |
| `GH_AW_MODEL_DETECTION_COPILOT` | GitHub Copilot |
| `GH_AW_MODEL_DETECTION_CLAUDE` | Anthropic Claude |
| `GH_AW_MODEL_DETECTION_CODEX` | OpenAI Codex |
| `GH_AW_MODEL_DETECTION_GEMINI` | Google Gemini |
| `GH_AW_MODEL_DETECTION_CRUSH` | Crush |

Defina uma sobrescrita de modelo como uma variável de organização:

```bash
gh variable set GH_AW_MODEL_AGENT_COPILOT --org my-org --body "gpt-5"
```

Veja [Motores](/gh-aw/reference/engines/) para identificadores de motor disponíveis e opções de configuração de modelo.

---

## Variáveis de Fallback de Política de Proteção

Estas variáveis fornecem valores de fallback para campos de política de proteção quando a configuração `tools.github.*` correspondente está ausente do frontmatter do fluxo de trabalho. Defina-as como variáveis de organização ou repositório do GitHub Actions para impor uma política consistente em todos os fluxos de trabalho.

> [!NOTE]
> Valores explícitos `tools.github.*` no frontmatter do fluxo de trabalho sempre têm precedência sobre essas variáveis.

| Variável | Campo de frontmatter | Formato | Descrição |
| --- | --- | --- | --- |
| `GH_AW_GITHUB_BLOCKED_USERS` | `tools.github.blocked-users` | Nomes de usuário separados por vírgula ou nova linha | Nomes de usuário do GitHub bloqueados de disparar execuções de agente |
| `GH_AW_GITHUB_APPROVAL_LABELS` | `tools.github.approval-labels` | Nomes de label separados por vírgula ou nova linha | Labels que promovem conteúdo para integridade "aprovada" para verificações de proteção |
| `GH_AW_GITHUB_TRUSTED_USERS` | `tools.github.trusted-users` | Nomes de usuário separados por vírgula ou nova linha | Nomes de usuário do GitHub elevados para integridade "aprovada", ignorando verificações de proteção |

Defina uma lista de usuários bloqueados em toda a organização:

```bash
gh variable set GH_AW_GITHUB_BLOCKED_USERS --org my-org --body "conta-bot1,conta-bot2"
```

Veja [Referência de Ferramentas](/gh-aw/reference/tools/) para documentação completa de política de proteção.

---

## Regras de Precedência

As variáveis de ambiente seguem um modelo de **o mais específico vence**, consistente com o GitHub Actions. Variáveis em escopos mais específicos sobrescrevem completamente variáveis com o mesmo nome em escopos menos específicos.

### Precedência Geral (Mais Alta para Mais Baixa)

1. **Nível de etapa** (`steps[*].env`, `githubActionsStep.env`)
2. **Nível de Job** (`jobs.<job_id>.env`)
3. **Nível de fluxo de trabalho** (`env:`)

### Precedência de Safe Outputs

1. **Específico de job** (`safe-outputs.jobs.<job_name>.env`)
2. **Global** (`safe-outputs.env`)
3. **Nível de fluxo de trabalho** (`env:`)

### Escopos Específicos de Contexto

Estes escopos são independentes e operam em contextos diferentes: `engine.env`, `container.env`, `services.<id>.env`, `sandbox.agent.env`, `sandbox.mcp.env`, `tools.<tool>.env`, `mcp-scripts.<tool>.env`.

### Exemplo de Sobrescrita

```yaml wrap
---
env:
  API_KEY: default-key
  DEBUG: "false"

jobs:
  test:
    env:
      API_KEY: test-key    # Sobrescreve o nível de fluxo de trabalho
      EXTRA: "value"
    steps:
      - run: |
          # API_KEY = "test-key" (sobrescrita de nível de job)
          # DEBUG = "false" (herdado do nível de fluxo de trabalho)
          # EXTRA = "value" (nível de job)
---
```

## Documentação relacionada

- [Referência de Frontmatter](/gh-aw/reference/frontmatter/) - Configuração completa de frontmatter
- [Safe Outputs](/gh-aw/reference/safe-outputs/) - Configuração de ambiente de safe output
- [Sandbox](/gh-aw/reference/sandbox/) - Variáveis de ambiente do sandbox
- [Ferramentas](/gh-aw/reference/tools/) - Configuração de ferramenta MCP e políticas de proteção
- [Scripts MCP](/gh-aw/reference/mcp-scripts/) - Configuração da ferramenta de script MCP
- [Motores](/gh-aw/reference/engines/) - Configuração do motor de IA e seleção de modelo
- [Variáveis de Ambiente do GitHub Actions](https://docs.github.com/en/actions/learn-github-actions/variables) - Documentação do GitHub Actions
