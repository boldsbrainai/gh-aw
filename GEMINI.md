# GEMINI.md - GitHub Agentic Workflows (gh-aw)

Foundational mandates and context for software engineering tasks in the `gh-aw` repository.

## Project Overview
`gh-aw` (GitHub Agentic Workflows) is a framework for writing AI-driven workflows in natural language (Markdown) and executing them securely within GitHub Actions.

- **Primary Language:** Go 1.25.8
- **Core Technologies:** GitHub Actions, Model Context Protocol (MCP), Charm Bracelet (bubbles, tea, huh), Cobra (CLI), Astro (Docs).
- **AI Engines:** Supports GitHub Copilot, Claude (Anthropic), Codex (OpenAI), and Gemini (Google).
- **Safety Philosophy:** Read-only by default. Write operations occur through sanitized `safe-outputs`. Implements sandboxing, network isolation, and human-in-the-loop approvals.

## Architecture & File Organization
- **`cmd/`**: CLI entry points. `cmd/gh-aw` is the main binary.
- **`pkg/workflow/`**: Core compiler logic.
    - `create_*.go`: Handlers for GitHub entity creation (Safe Outputs).
    - `*_engine.go`: AI engine-specific implementations.
    - `compiler*.go`: Orchestration, YAML generation, and job construction.
    - `expressions.go`: Tree-based condition/expression parser.
- **`pkg/cli/`**: Cobra commands and CLI-specific logic.
    - `*_command.go`: Command definitions.
    - `flags.go`: Standardized CLI flags.
- **`actions/`**: Source code for custom GitHub Actions used by compiled workflows.
- **`internal/`**: Build-time tools and internal utilities.
- **`docs/`**: Astro-based documentation project.

## Key Development Commands
| Task | Command |
| :--- | :--- |
| **Build Binary** | `make build` |
| **Fast Unit Tests** | `make test-unit` |
| **Full Test Suite** | `make test` |
| **All Tests (Go+JS)** | `make test-all` |
| **Lint & Format** | `make lint` |
| **Auto-Format Code** | `make fmt` |
| **Recompile Workflows** | `make recompile` |
| **Install Extension** | `make install` |
| **Security Scan** | `make security-scan` |
| **Agent Finish** | `make agent-finish` (Run before concluding a task) |
| **PR Validation** | `make agent-report-progress` |

## Engineering Standards & Conventions

### Coding Style
- **Go Standards:** Adhere to standard Go idioms and `golangci-lint` rules.
- **CLI Output:** All user-facing output must go to **stderr** (except raw JSON). Use `pkg/console` for stylized formatting.
- **Error Handling:** Always wrap errors with context: `fmt.Errorf("failed to [action]: %w", err)`.
- **File Sizing:** Aim for focused files under 500 lines. Split complex logic into `_config.go`, `_helpers.go`, or `_orchestrator.go`.
- **Naming:** Safe output handlers follow `create_<entity>.go`. Engines follow `<engine>_engine.go`.

### Testing Practices
- **Table-Driven Tests:** Preferred for all logic and CLI commands.
- **Golden Files:** Used for console output and complex serialization. Use `go test ./... -update` to refresh.
- **Collocation:** Tests must live next to the code they test (`*_test.go`).
- **Wasm Testing:** Wasm-specific golden tests exist in `pkg/workflow`.

### Workflow Compilation
- **Standalone Workflows:** Must have an `on:` trigger.
- **Shared Components:** Found in `.github/workflows/shared/`. These lack triggers and are imported. Do not attempt to compile them directly.
- **Recompilation:** Always run `make recompile` after modifying compiler logic to ensure `.lock.yml` files are up to date.

### Security
- **Safe Outputs:** Never implement direct write operations in the engine logic. Use the `safe-outputs` pattern.
- **Credentials:** Rigorously avoid logging or exposing secrets. Use `pkg/logger` which is configured for safe output.

## Change Process
- **Versioning:** Handled via Changesets (`.changeset/` directory).
- **Commits:** Conventional commits are recommended.
- **Validation:** `make agent-finish` is the mandatory final check for any non-trivial change.
