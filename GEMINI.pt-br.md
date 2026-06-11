# GEMINI.md - GitHub Agentic Workflows (gh-aw)

Mandatos fundamentais e contexto para tarefas de engenharia de software no repositório `gh-aw`.

## Visão Geral do Projeto

`gh-aw` (GitHub Agentic Workflows) é um framework para escrita de fluxos de trabalho (workflows) orientados por IA em linguagem natural (Markdown) e execução segura dentro do GitHub Actions.

- **Linguagem Principal:** Go 1.25.8
- **Tecnologias Core:** GitHub Actions, Model Context Protocol (MCP), Charm Bracelet (bubbles, tea, huh), Cobra (CLI), Astro (Docs).
- **Motores de IA (AI Engines):** Suporta GitHub Copilot, Claude (Anthropic), Codex (OpenAI) e Gemini (Google).
- **Filosofia de Segurança:** Somente leitura por padrão. Operações de escrita ocorrem através de `safe-outputs` (saídas seguras) sanitizadas. Implementa sandboxing (isolamento), isolamento de rede e aprovações human-in-the-loop (intervenção humana).

## Arquitetura e Organização de Arquivos

- **`cmd/`**: Pontos de entrada da CLI. `cmd/gh-aw` é o binário principal.
- **`pkg/workflow/`**: Lógica central do compilador.
    - `create_*.go`: Manipuladores para criação de entidades do GitHub (Safe Outputs).
    - `*_engine.go`: Implementações específicas de motores de IA.
    - `compiler*.go`: Orquestração, geração de YAML e construção de jobs.
    - `expressions.go`: Analisador (parser) de condições/expressões baseado em árvore.
- **`pkg/cli/`**: Comandos Cobra e lógica específica da CLI.
    - `*_command.go`: Definições de comando.
    - `flags.go`: Flags padronizadas da CLI.
- **`actions/`**: Código-fonte para GitHub Actions personalizadas usadas por fluxos de trabalho compilados.
- **`internal/`**: Ferramentas de tempo de compilação (build-time) e utilitários internos.
- **`docs/`**: Projeto de documentação baseado em Astro.

## Comandos Principais de Desenvolvimento

| Tarefa | Comando |
| :--- | :--- |
| **Build do Binário** | `make build` |
| **Testes Unitários Rápidos** | `make test-unit` |
| **Suíte de Testes Completa** | `make test` |
| **Todos os Testes (Go+JS)** | `make test-all` |
| **Lint e Formatação** | `make lint` |
| **Autoformatação de Código** | `make fmt` |
| **Recompilar Workflows** | `make recompile` |
| **Instalar Extensão** | `make install` |
| **Varredura de Segurança** | `make security-scan` |
| **Finalizar Agente** | `make agent-finish` (Executar antes de concluir uma tarefa) |
| **Validação de PR** | `make agent-report-progress` |

## Padrões de Engenharia e Convenções

### Estilo de Codificação

- **Padrões Go:** Aderir aos idiomas padrão de Go e às regras do `golangci-lint`.
- **Saída da CLI:** Toda saída voltada ao usuário deve ir para **stderr** (exceto JSON bruto). Use `pkg/console` para formatação estilizada.
- **Tratamento de Erros:** Sempre envolva erros com contexto: `fmt.Errorf(\"failed to [action]: %w\", err)`.
- **Dimensionamento de Arquivos:** Foque em arquivos com menos de 500 linhas. Divida lógicas complexas em `_config.go`, `_helpers.go` ou `_orchestrator.go`.
- **Nomenclatura:** Manipuladores de saída segura seguem `create_<entity>.go`. Motores seguem `<engine>_engine.go`.

### Práticas de Teste

- **Testes Baseados em Tabela (Table-Driven):** Preferencial para toda a lógica e comandos da CLI.
- **Arquivos Golden:** Usados para saída de console e serialização complexa. Use `go test ./... -update` para atualizar.
- **Colocação (Collocation):** Testes devem residir ao lado do código que testam (`*_test.go`).
- **Testes Wasm:** Testes golden específicos para Wasm existem em `pkg/workflow`.

### Compilação de Workflow

- **Workflows Autônomos (Standalone):** Devem ter um gatilho (trigger) `on:`.
- **Componentes Compartilhados:** Encontrados em `.github/workflows/shared/`. Estes carecem de gatilhos e são importados. Não tente compilá-los diretamente.
- **Recompilação:** Sempre execute `make recompile` após modificar a lógica do compilador para garantir que os arquivos `.lock.yml` estejam atualizados.

### Segurança

- **Safe Outputs:** Nunca implemente operações de escrita direta na lógica do motor. Use o padrão `safe-outputs`.
- **Credenciais:** Evite rigorosamente registrar ou expor segredos. Use `pkg/logger`, que está configurado para saída segura.

## Processo de Mudança

- **Versionamento:** Gerenciado via Changesets (diretório `.changeset/`).
- **Commits:** Commits convencionais são recomendados.
- **Validação:** `make agent-finish` é a verificação final obrigatória para qualquer mudança não trivial.
