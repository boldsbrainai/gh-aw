# Debugging Agentic Workflows

This prompt guides you, a coding agent, to debug workflow failures in **GitHub Agentic Workflows (gh-aw)**.

## How to Use This Prompt

There are two ways to invoke this debugging workflow:

### Option A: Through Copilot

If your repository is configured with the `agentic-workflows` agent, use Copilot Chat:

```text
/agent agentic-workflows debug https://github.com/OWNER/REPO/actions/runs/RUN_ID
```

### Option B: Self-Contained (with URL)

Share this file's URL with any AI assistant or coding agent:

```text
Debug this workflow run using https://raw.githubusercontent.com/github/gh-aw/main/debug.md

Run URL: https://github.com/OWNER/REPO/actions/runs/RUN_ID
```

The agent will follow the steps below to install `gh aw`, analyze the logs, and apply fixes.

---

## Step 1: Install GitHub Agentic Workflows CLI Extension

Check if `gh aw` is installed by running

```bash
gh aw version
```

If it is installed, run:

```bash
gh extension upgrade aw
```

to upgrade to latest. If it is not installed, run the installation script from the main branch of the gh-aw repository:

```bash
curl -sL https://raw.githubusercontent.com/github/gh-aw/main/install-gh-aw.sh | bash
```

**What this does**: Downloads and installs the gh-aw binary to `~/.local/share/gh/extensions/gh-aw/`

**Verify installation**:

```bash
gh aw version
```

You should see version information displayed. If you encounter an error, check that:

- GitHub CLI (`gh`) is installed and authenticated
- The installation script completed without errors
- `~/.local/share/gh/extensions` is in your PATH

## Step 2: Debug the Workflow Failure

Follow carefully the instructions in the appropriate prompt file. Read ALL the instructions in the prompt file before taking any action.

Below, ROOT is the location where you found this file. For example,

- if this file is at `https://raw.githubusercontent.com/github/gh-aw/main/debug.md` then the ROOT is `https://raw.githubusercontent.com/github/gh-aw/main`
- if this file is at `https://raw.githubusercontent.com/github/gh-aw/v0.35.1/debug.md` then the ROOT is `https://raw.githubusercontent.com/github/gh-aw/v0.35.1`

**Prompt file**: `ROOT/.github/aw/debug-agentic-workflow.md`

**Use cases**:

- "Why is this workflow failing?"
- "Analyze the logs for workflow X"
- "Investigate missing tool calls in run #12345"
- "Debug this workflow run: https://github.com/owner/repo/actions/runs/12345"

**If gh-aw version is in [0.68.4, 0.71.3], stop debugging and tell the user to upgrade because those versions were retired.**

## Step 3: Apply Fixes

After identifying the root cause:

1. Edit the workflow markdown file (`.github/workflows/<workflow-name>.md`)
2. Recompile the workflow:

```bash
gh aw compile <workflow-name>
```

3. Check for syntax errors or validation warnings.

## Step 4: Commit and Push Changes

Commit the changes, e.g.

```bash
git add .github/workflows/<workflow-name>.md .github/workflows/<workflow-name>.lock.yml
git commit -m "Fix agentic workflow: <describe fix>"
git push
```

Se houver proteção de ramificação na ramificação padrão, crie uma solicitação de pull e envie o link para ela.

## Resolução de problemas

Consulte os guias separados sobre como resolver problemas comuns.

## Instruções

Quando um usuário interagir com você:

1. **Extraia a URL de execução ou o nome do fluxo de trabalho** da solicitação do usuário
2. **Busque e leia o prompt de depuração** em `ROOT/.github/aw/debug-agentic-workflow.md`
3. **Siga exatamente as instruções do prompt carregado**
4. **Se estiver em dúvida**, faça perguntas para esclarecer

## Referência rápida

```bash
# Baixe e analise os logs do fluxo de trabalho
gh aw logs <nome-do-fluxo-de-trabalho>

# Auditar uma execução específica do fluxo de trabalho
gh aw audit <id-da-execução>

# Comparar duas ou mais execuções do fluxo de trabalho (modo de comparação de múltiplas execuções)
gh aw audit <id-da-execução-base> <id-da-execução-de-comparação>
gh aw audit <id-da-execução-base> <id-da-execução-de-comparação-1> <id-da-execução-de-comparação-2>

# Compilar fluxos de trabalho após correções
gh aw compile <nome-do-fluxo-de-trabalho>

# Mostrar o status de todos os fluxos de trabalho
gh aw status
```

## Principais comandos de depuração

- `gh aw audit <id-da-execução> --json` → Análise detalhada da execução com ferramentas ausentes e erros
- `gh aw audit <id-da-execução-base> <id-da-execução-de-comparação> --json` → Compara duas execuções para detectar regressões (firewall, MCP, métricas)
- `gh aw logs <nome-do-fluxo-de-trabalho> --json` → Baixa e analisa logs recentes do fluxo de trabalho
- `gh aw compile <nome-do-fluxo-de-trabalho> --strict` → Valida o fluxo de trabalho com verificações de segurança rigorosas
