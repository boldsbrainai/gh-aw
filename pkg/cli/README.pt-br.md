# Pacote cli

> Implementações de comandos CLI para a extensão `gh aw` — a principal interface de usuário para criação, compilação, execução e monitoramento de fluxos de trabalho agentistas (agentic workflows) do GitHub.

## Visão Geral

O pacote `cli` implementa todos os comandos expostos através da extensão CLI `gh aw`. Cada comando é implementado como um comando Cobra com um construtor `New*Command()` dedicado e uma função `Run*()` que encapsula a lógica de negócio testável.

O pacote é intencionalmente decomposto em muitos arquivos pequenos agrupados por domínio de funcionalidade (ex: `compile_*.go`, `audit_*.go`, `run_*.go`, `mcp_*.go`). Esta estrutura mantém arquivos individuais abaixo de 300 linhas e promove testes independentes de cada subdomínio.

Toda a saída diagnóstica DEVE ir para `stderr` usando auxiliares de formatação do `console`. Saída estruturada (JSON, hashes, grafos) vai para `stdout`.

## Grupos de Comandos

| Comando | Ponto de Entrada | Descrição |
|---------|-------------|-------------|
| `gh aw add` | `NewAddCommand` | Adiciona fluxos de trabalho remotos ou locais ao repositório |
| `gh aw add-wizard` | `NewAddWizardCommand` | Assistente interativo para adicionar fluxos de trabalho |
| `gh aw new` | `newCmd` (main.go) | Cria um novo arquivo de fluxo de trabalho (suporta `--force`, `--interactive`, `--engine`) |
| `gh aw compile` | Cobra `compileCmd` (`cmd/gh-aw/main.go`); orquestração via `CompileWorkflows` (`compile_orchestrator.go`) | Compila arquivos de fluxo de trabalho `.md` em GitHub Actions `.lock.yml` |
| `gh aw enable` | `enableCmd` (main.go) | Habilita um fluxo de trabalho |
| `gh aw disable` | `disableCmd` (main.go) | Desabilita um fluxo de trabalho |
| `gh aw run` | `RunWorkflowOnGitHub` (main.go) | Despacha e monitora execuções de fluxo de trabalho |
| `gh aw audit` | `NewAuditCommand` | Audita uma execução de fluxo de trabalho específica pelo ID de execução |
| `gh aw audit diff` | `NewAuditDiffSubcommand` | Compara dados de auditoria entre múltiplas execuções |
| `gh aw logs` | `NewLogsCommand` | Baixa e analisa logs de execução de fluxo de trabalho |
| `gh aw mcp` | `NewMCPCommand` | Gerencia configurações de servidor MCP |
| `gh aw mcp add` | `NewMCPAddSubcommand` | Adiciona uma ferramenta MCP a um fluxo de trabalho |
| `gh aw mcp inspect` | `NewMCPInspectSubcommand` | Inspeciona servidores MCP em um fluxo de trabalho |
| `gh aw mcp list` | `NewMCPListSubcommand` | Lista fluxos de trabalho que usam servidores MCP |
| `gh aw mcp list-tools` | `NewMCPListToolsSubcommand` | Lista ferramentas para un servidor MCP específico |
| `gh aw mcp server` | `NewMCPServerCommand` | Executa como um servidor MCP (para integração com IDE) |
| `gh aw update` | `NewUpdateCommand` | Atualiza fluxos de trabalho de fontes upstream |
| `gh aw upgrade` | `NewUpgradeCommand` | Atualiza fluxos de trabalho para o formato mais recente |
| `gh aw validate` | `NewValidateCommand` | Valida arquivos de fluxo de trabalho sem compilar |
| `gh aw fix` | `NewFixCommand` | Aplica codemods automáticos para corrigir padrões obsoletos |
| `gh aw status` | `NewStatusCommand` | Mostra o status dos fluxos de trabalho no repositório |
| `gh aw health` | `NewHealthCommand` | Computa métricas de saúde entre execuções de fluxo de trabalho |
| `gh aw checks` | `NewChecksCommand` | Mostra resultados de verificações de CI para um PR |
| `gh aw domains` | `NewDomainsCommand` | Lista domínios usados pelos fluxos de trabalho |
| `gh aw hash` | `NewHashCommand` | Imprime o hash do frontmatter de um arquivo de fluxo de trabalho |
| `gh aw init` | `NewInitCommand` | Inicializa um repositório para fluxos de trabalho agentistas |
| `gh aw list` | `NewListCommand` | Lista fluxos de trabalho instalados |
| `gh aw pr` | `NewPRCommand` | Auxiliares de pull request |
| `gh aw pr transfer` | `NewPRTransferSubcommand` | Transfere um pull request para outro repositório |
| `gh aw project` | `NewProjectCommand` | Auxiliares de gerenciamento de projeto |
| `gh aw project new` | `NewProjectNewCommand` | Cria um novo quadro do GitHub Project V2 |
| `gh aw remove` | `RemoveWorkflows` (main.go) | Remove arquivos de fluxo de trabalho do repositório |
| `gh aw secrets` | `NewSecretsCommand` | Gerencia segredos de fluxo de trabalho |
| `gh aw secrets set` | (secret_set_command.go) | Cria ou atualiza um segredo de repositório |
| `gh aw secrets bootstrap` | (secret_set_command.go) | Valida e configura todos os segredos necessários para fluxos de trabalho |
| `gh aw lint` | `NewLintCommand` | Executa lint em fluxos de trabalho `.lock.yml` existentes com actionlint |
| `gh aw experiments` | `NewExperimentsCommand` | Explora experimentos A/B em andamento no repositório (oculto) |
| `gh aw experiments list` | `NewExperimentsListSubcommand` | Lista todos as branches de fluxos de trabalho de experimento |
| `gh aw experiments analyze` | `NewExperimentsAnalyzeSubcommand` | Analisa um fluxo de trabalho de experimento específico em detalhes |
| `gh aw forecast` | `NewForecastCommand` | Preve o uso de tokens e custos para fluxos de trabalho agentistas (experimental) |
| `gh aw trial` | `NewTrialCommand` | Executa execuções de teste (trial) de fluxo de trabalho |
| `gh aw deploy` | `NewDeployCommand` | Faz o deploy de fluxos de trabalho agentistas para um repositório de destino usando um pull request |
| `gh aw outcomes` | `NewOutcomesCommand` | Verifica o que aconteceu com as saídas seguras (safe-outputs) de uma execução de fluxo de trabalho |
| _Sem comando `gh aw deps`_ | `deps_*.go` (utilitários internos) | Auxiliares de relatório/consultoria de dependência usados por outros comandos |
| `gh aw version` | `versionCmd` (main.go) | Mostra informações de versão |
| `gh aw completion` | `NewCompletionCommand` | Gera scripts de autocompletar para shell |

## API Pública

### Tipos Chave

| Tipo | Arquivo | Descrição |
|------|------|-------------|
| `CompileConfig` | `compile_config.go` | Configuração para `CompileWorkflows` — lista de arquivos, flags, opções de validação |
| `ValidationResult` | `compile_config.go` | Resultado de uma passagem de validação de compilação |
| `AddOptions` | `add_command.go` | Opções que controlam o comportamento de adição de fluxo de trabalho |
| `AddWorkflowsResult` | `add_command.go` | Resultado de `AddWorkflows` / `AddResolvedWorkflows` |
| `ResolvedWorkflow` | `add_workflow_resolution.go` | Um único fluxo de trabalho resolvido com metadados de origem |
| `ResolvedWorkflows` | `add_workflow_resolution.go` | Coleção de fluxos de trabalho resolvidos |
| `RunOptions` | `run_workflow_execution.go` | Opções para `RunWorkflowOnGitHub` |
| `WorkflowRunResult` | `run_workflow_execution.go` | Resultado de uma execução de fluxo de trabalho disparada |
| `AuditData` | `audit_report.go` | Estrutura completa de dados de auditoria para uma execução de fluxo de trabalho |
| `AuditDiff` | `audit_diff.go` | Diferença (diff) entre duas execuções de auditoria |
| `CrossRunAuditReport` | `audit_cross_run.go` | Análise de tendência entre execuções |
| `HealthConfig` | `health_command.go` | Configuração para computação de saúde |
| `WorkflowHealth` | `health_metrics.go` | Métricas de saúde por fluxo de trabalho |
| `HealthSummary` | `health_metrics.go` | Resumo de saúde agregado de todos os fluxos de trabalho |
| `DependencyReport` | `deps_report.go` | Relatório completo de dependências |
| `OutdatedDependency` | `deps_outdated.go` | Uma entrada de dependência desatualizada |
| `SecurityAdvisory` | `deps_security.go` | Uma entrada de comunicado de segurança |
| `WorkflowStatus` | `status_command.go` | Status de execução para um único fluxo de trabalho |
| `MCPRegistryClient` | `mcp_registry.go` | Cliente para a API do registro MCP |
| `ToolGraph` | `tool_graph.go` | Grafo de dependência de ferramentas MCP |
| `DependencyGraph` | `dependency_graph.go` | Grafo de dependência entre fluxos de trabalho |
| `FileTracker` | `file_tracker.go` | Rastreia arquivos modificados durante uma operação |
| `RepeatOptions` | `retry.go` | Opções para o loop de consulta `ExecuteWithRepeat` |
| `PollOptions` | `signal_aware_poll.go` | Opções para `PollWithSignalHandling` |
| `FixConfig` | `fix_command.go` | Configuração para codemods `RunFix` |
| `ForecastConfig` | `forecast_command.go` | Configuração para `NewForecastCommand` (previsão experimental de uso de tokens) |
| `TrialOptions` | `trial_types.go` | Opções para `RunWorkflowTrials` |
| `WorkflowTrialResult` | `trial_types.go` | Resultado de uma execução de teste (trial) |
| `UpgradeConfig` | `upgrade_command.go` | Configuração para `NewUpgradeCommand` |
| `ChecksConfig` | `checks_command.go` | Configuração para `RunChecks` |
| `ChecksResult` | `checks_command.go` | Resultado de `FetchChecksResult` |
| `OutcomesConfig` | `outcomes_command.go` | Configuração para avaliação de resultados de saídas seguras `RunOutcomes` |
| `OutcomesData` | `outcomes_command.go` | Dados de resultados avaliados retornados por `RunOutcomes` |

### Funções Chave

| Função | Assinatura | Descrição |
|----------|-----------|-------------|
| `CompileWorkflows` | `func(ctx, CompileConfig) ([]*workflow.WorkflowData, error)` | Orquestra a compilação de um ou mais arquivos de fluxo de trabalho |
| `CompileWorkflowWithValidation` | `func(*workflow.Compiler, filePath string, ...) error` | Compila e valida um único arquivo de fluxo de trabalho |
| `AddWorkflows` | `func([]string, AddOptions) (*AddWorkflowsResult, error)` | Adiciona fluxos de trabalho a partir de especificações de string |
| `ResolveWorkflows` | `func([]string, bool) (*ResolvedWorkflows, error)` | Resolve especificações de fluxo de trabalho para caminhos locais e metadados |
| `RunWorkflowOnGitHub` | `func(ctx, string, RunOptions) error` | Despacha uma única execução de fluxo de trabalho no GitHub |
| `RunWorkflowsOnGitHub` | `func(ctx, []string, RunOptions) error` | Despacha múltiplos fluxos de trabalho |
| `AuditWorkflowRun` | `func(ctx, runID int64, ...) error` | Baixa e renderiza um relatório de auditoria para uma execução |
| `RunAuditDiff` | `func(ctx, baseRunID, compareRunIDs, ...) error` | Renderiza uma diferença entre execuções de auditoria |
| `DownloadWorkflowLogs` | `func(ctx, workflowName string, ...) error` | Baixa e analisa logs de fluxo de trabalho |
| `RunListWorkflows` | `func(repo, path, pattern string, ...) error` | Lista fluxos de trabalho instalados |
| `StatusWorkflows` | `func(pattern string, ...) error` | Imprime o status de execução do fluxo de trabalho |
| `GetWorkflowStatuses` | `func(pattern, ref, ...) ([]WorkflowStatus, error)` | Busca status de fluxo de trabalho |
| `RunHealth` | `func(HealthConfig) error` | Computa e renderiza métricas de saúde do fluxo de trabalho |
| `CalculateWorkflowHealth` | `func(string, []WorkflowRun, float64) WorkflowHealth` | Computação pura de saúde para um único fluxo de trabalho |
| `CalculateHealthSummary` | `func([]WorkflowHealth, string, float64) HealthSummary` | Computação de resumo de saúde agregada |
| `RunFix` | `func(FixConfig) error` | Aplica codemods automáticos |
| `GetAllCodemods` | `func() []Codemod` | Retorna todos os codemods disponíveis |
| `InitRepository` | `func(InitOptions) error` | Inicializa um repositório com a configuração `gh-aw` |
| `CreateWorkflowMarkdownFile` | `func(string, bool, bool, string) error` | Cria um novo arquivo markdown de fluxo de trabalho |
| `IsRunnable` | `func(string) (bool, error)` | Verifica se um arquivo de fluxo de trabalho é executável |
| `RunWorkflowInteractively` | `func(ctx, ...) error` | Seleção e despacho de fluxo de trabalho interativo |
| `RunSpecificWorkflowInteractively` | `func(ctx, string, ...) error` | Despacho interativo para um fluxo de trabalho nomeado |
| `RunAddInteractive` | `func(ctx, []string, ...) error` | Assistente interativo para adicionar fluxos de trabalho |
| `RunWorkflowTrials` | `func(ctx, []string, TrialOptions) error` | Executa execuções de teste (trial) de fluxo de trabalho |
| `RunUpdateWorkflows` | `func(ctx, []string, ...) error` | Atualiza fluxos de trabalho de fontes upstream |
| `RunChecks` | `func(ChecksConfig) error` | Busca e renderiza resultados de verificação de CI para um PR |
| `RunProjectNew` | `func(ctx, ProjectConfig) error` | Cria um novo quadro do GitHub Project V2 |
| `RunListDomains` | `func(bool) error` | Lista todos os domínios usados em todos os fluxos de trabalho |
| `RunWorkflowDomains` | `func(string, bool) error` | Lista domínios para um fluxo de trabalho específico |
| `RunHashFrontmatter` | `func(string) error` | Imprime o hash do frontmatter para um arquivo de fluxo de trabalho |
| `RunActionlintOnFiles` | `func([]string, bool, bool) error` | Executa linter actionlint em arquivos lock compilados |
| `RunZizmorOnFiles` | `func([]string, bool, bool) error` | Executa linter zizmor em arquivos lock compilados |
| `RunPoutineOnDirectory` | `func(string, bool, bool) error` | Executa scanner de cadeia de suprimentos poutine no diretório de fluxo de trabalho |
| `RunRunnerGuardOnDirectory` | `func(string, bool, bool) error` | Executa scanner runner-guard no diretório de fluxo de trabalho |
| `AddMCPTool` | `func(string, string, ...) error` | Adiciona um servidor MCP a um arquivo de fluxo de trabalho |
| `InspectWorkflowMCP` | `func(string, ...) error` | Inspeciona configurações de servidor MCP |
| `ListWorkflowMCP` | `func(string, bool) error` | Lista informações de servidor MCP para um fluxo de trabalho |
| `UpdateActions` | `func(bool, bool, bool, time.Duration) error` | Atualiza em massa versões de GitHub Actions em fluxos de trabalho |
| `ActionsBuildCommand` | `func() error` | Constrói todas as ações customizadas em `actions/` |
| `ActionsValidateCommand` | `func() error` | Valida todos os arquivos `action.yml` em `actions/` |
| `ActionsCleanCommand` | `func() error` | Remove artefatos de build de ação gerados |
| `GenerateActionMetadataCommand` | `func() error` | Gera metadados `action.yml` e README para módulos de ação selecionados |
| `UpdateWorkflows` | `func([]string, ...) error` | Atualiza fluxos de trabalho de fontes upstream |
| `RemoveWorkflows` | `func(string, bool, string) error` | Remove arquivos de fluxo de trabalho |
| `ValidateWorkflowName` | `func(string) error` | Valida um identificador de nome de fluxo de trabalho |
| `GetBinaryPath` | `func() (string, error)` | Retorna o caminho para o binário `gh-aw` |
| `GetCurrentRepoSlug` | `func() (string, error)` | Retorna `dono/repositorio` para o diretório atual |
| `GetVersion` | `func() string` | Retorna a versão atual da CLI |
| `SetVersionInfo` | `func(string)` | Define a versão na inicialização |
| `EnableWorkflowsByNames` | `func([]string, string) error` | Habilita fluxos de trabalho do GitHub Actions |
| `DisableWorkflowsByNames` | `func([]string, string) error` | Desabilita fluxos de trabalho do GitHub Actions |
| `CheckOutdatedDependencies` | `func(bool) ([]OutdatedDependency, error)` | Verifica dependências desatualizadas |
| `CheckSecurityAdvisories` | `func(bool) ([]SecurityAdvisory, error)` | Verifica CVEs conhecidos |
| `GenerateDependencyReport` | `func(bool) (*DependencyReport, error)` | Relatório completo de análise de dependência |
| `InstallShellCompletion` | `func(bool, CommandProvider) error` | Instala autocompletar para shell |
| `PollWithSignalHandling` | `func(PollOptions) error` | Consulta um predicado com tratamento de SIGINT |
| `ExecuteWithRepeat` | `func(RepeatOptions) error` | Repete uma operação com atraso |
| `IsRunningInCI` | `func() bool` | Detecta ambiente de CI |
| `DetectShell` | `func() ShellType` | Detecta o shell atual do usuário |
| `AddResolvedWorkflows` | `func([]string, *ResolvedWorkflows, AddOptions) (*AddWorkflowsResult, error)` | Adiciona fluxos de trabalho pré-resolvidos |
| `FetchWorkflowFromSource` | `func(*WorkflowSpec, bool) (*FetchedWorkflow, error)` | Busca um fluxo de trabalho de uma fonte remota ou local |
| `FetchIncludeFromSource` | `func(string, *WorkflowSpec, bool) ([]byte, string, error)` | Busca um alvo `@include` da fonte |
| `MergeWorkflowContent` | `func(base, current, new, oldSpec, newSpec, localPath string, bool) (string, bool, error)` | Mesclagem de três vias (three-way merge) de conteúdo de fluxo de trabalho |
| `CompileWorkflowDataWithValidation` | `func(*workflow.Compiler, *workflow.WorkflowData, string, ...) error` | Compila um WorkflowData pré-carregado e executa validadores de segurança |
| `ResolveWorkflowPath` | `func(string) (string, error)` | Resolve um nome de fluxo de trabalho para seu caminho de arquivo absoluto |
| `ExtractWorkflowDescription` | `func(string) string` | Extrai o campo `description` do conteúdo markdown do fluxo de trabalho |
| `ExtractWorkflowDescriptionFromFile` | `func(string) string` | Extrai o campo `description` de um arquivo de fluxo de trabalho |
| `ExtractWorkflowEngine` | `func(string) string` | Extrai o campo `engine` do conteúdo markdown do fluxo de trabalho |
| `ExtractWorkflowPrivate` | `func(string) bool` | Retorna true se o fluxo de trabalho estiver marcado como privado |
| `UpdateFieldInFrontmatter` | `func(content, fieldName, fieldValue string) (string, error)` | Define um campo no YAML do frontmatter |
| `SetFieldInOnTrigger` | `func(content, fieldName, fieldValue string) (string, error)` | Define um campo dentro do bloco de gatilho `on:` |
| `RemoveFieldFromOnTrigger` | `func(content, fieldName string) (string, error)` | Remove um campo do bloco de gatilho `on:` |
| `UpdateScheduleInOnBlock` | `func(content, scheduleExpr string) (string, error)` | Atualiza o agendamento cron no bloco `on:` |
| `ScanWorkflowsForMCP` | `func(workflowsDir, serverFilter string, verbose bool) ([]WorkflowMCPMetadata, error)` | Escaneia todos os fluxos de trabalho para configurações de servidor MCP |
| `ListToolsForMCP` | `func(workflowFile, mcpServerName string, verbose bool) error` | Lista ferramentas para um servidor MCP específico em um fluxo de trabalho |
| `CollectLockFileManifests` | `func(workflowsDir string) map[string]*workflow.GHAWManifest` | Lê todos os manifestos `*.lock.yml` de um diretório |
| `WritePriorManifestFile` | `func(map[string]*workflow.GHAWManifest) (string, error)` | Escreve o cache do manifesto em um arquivo temporário |
| `GroupRunsByWorkflow` | `func([]WorkflowRun) map[string][]WorkflowRun` | Agrupa um slice plano de execuções por nome de fluxo de trabalho |
| `WaitForWorkflowCompletion` | `func(ctx, repoSlug, runID string, timeoutMinutes int, verbose bool) error` | Consulta até que uma execução de fluxo de trabalho termine ou expire |
| `ValidArtifactSetNames` | `func() []string` | Retorna as strings de nomes de conjunto de artefatos válidas |
| `ResolveArtifactFilter` | `func([]string) []string` | Expande aliases de conjunto de artefatos para nomes de artefatos concretos |
| `ValidateArtifactSets` | `func([]string) error` | Valida que todos os nomes de conjunto de artefatos fornecidos são conhecidos |
| `ParseCopilotCodingAgentLogMetrics` | `func(logContent string, verbose bool) workflow.LogMetrics` | Analisa logs do coding-agent do Copilot em métricas |
| `ExtractLogMetricsFromRun` | `func(ProcessedRun) workflow.LogMetrics` | Extrai métricas de log de uma execução processada |
| `TrainDrain3Weights` | `func([]ProcessedRun, outputDir string, verbose bool) error` | Treina pesos de detecção de anomalias Drain3 a partir do histórico de execuções |
| `DisplayOutdatedDependencies` | `func([]OutdatedDependency, int)` | Renderiza uma tabela de dependências desatualizadas para stdout |
| `DisplayDependencyReport` | `func(*DependencyReport)` | Renderiza um relatório de dependência completo para stdout |
| `DisplayDependencyReportJSON` | `func(*DependencyReport) error` | Renderiza um relatório de dependência como JSON para stdout |
| `DisplaySecurityAdvisories` | `func([]SecurityAdvisory)` | Renderiza uma tabela de comunicados de segurança para stdout |
| `IsDockerAvailable` | `func() bool` | Retorna true se o daemon do Docker estiver acessível |
| `IsDockerImageAvailable` | `func(string) bool` | Retorna true se uma imagem Docker estiver presente localmente |
| `IsDockerImageDownloading` | `func(string) bool` | Retorna true se um download de imagem estiver em andamento |
| `StartDockerImageDownload` | `func(ctx, image string) bool` | Inicia um download de imagem em background; retorna false se já estiver baixando |
| `CheckAndPrepareDockerImages` | `func(ctx, useZizmor, usePoutine, useActionlint, useRunnerGuard bool) error` | Pré-baixa imagens Docker de scanner de segurança |
| `UpdateContainerPins` | `func(ctx, workflowDir string, verbose bool) error` | Atualiza os pins SHA de imagem de container em arquivos de fluxo de trabalho |
| `CreatePRWithChanges` | `func(branchPrefix, commitMessage, prTitle, prBody string, verbose bool) (string, error)` | Cria um PR do GitHub a partir de mudanças não commitadas |
| `AutoMergePullRequestsCreatedAfter` | `func(repoSlug string, createdAfter time.Time, verbose bool) error` | Faz o auto-merge de PRs elegíveis criados após um determinado tempo |
| `PreflightCheckForCreatePR` | `func(bool) error` | Valida pré-requisitos antes de criar um PR |
| `DisableAllWorkflowsExcept` | `func(repoSlug string, exceptWorkflows []string, verbose bool) error` | Desabilita todos os fluxos de trabalho em um repositório exceto os nomeados |
| `GetEngineSecretNameAndValue` | `func(engine string, existingSecrets map[string]bool) (string, string, bool, error)` | Solicita e valida um segredo de API de engine |
| `CheckForUpdatesAsync` | `func(ctx, noCheckUpdate, verbose bool)` | Verifica por uma versão mais nova do `gh-aw` em background |
| `FetchChecksResult` | `func(repoOverride, prNumber string) (*ChecksResult, error)` | Busca resultados de verificação de CI para um pull request |
| `ValidEngineNames` | `func() []string` | Retorna os nomes de engine suportados para autocompletar shell |
| `CompleteWorkflowNames` | `func(*cobra.Command, []string, string) ([]string, cobra.ShellCompDirective)` | Provedor de autocompletar para nomes de fluxo de trabalho |
| `CompleteEngineNames` | `func(*cobra.Command, []string, string) ([]string, cobra.ShellCompDirective)` | Provedor de autocompletar para nomes de engine |
| `CompleteDirectories` | `func(*cobra.Command, []string, string) ([]string, cobra.ShellCompDirective)` | Provedor de autocompletar para caminhos de diretório |
| `RegisterEngineFlagCompletion` | `func(*cobra.Command)` | Registra autocompletar para a flag `--engine` |
| `RegisterDirFlagCompletion` | `func(*cobra.Command, string)` | Registra autocompletar para uma flag de diretório |
| `UninstallShellCompletion` | `func(verbose bool) error` | Desinstala scripts de autocompletar para shell |
| `IsCommitSHA` | `func(string) bool` | Retorna true se a string for um SHA de commit Git completo |
| `ValidateWorkflowIntent` | `func(string) error` | Valida a string de intenção do fluxo de trabalho |

### Tipos Exportados Adicionais

O pacote `cli` exporta muitos tipos usados em suas implementações de comando. O seguinte complementa a tabela principal de "Tipos Chave" acima:

| Tipo | Espécie | Descrição |
|------|------|-------------|
| `AccessLogEntry` | struct | Uma única entrada de um log de acesso à rede AWF |
| `AccessLogSummary` | struct | Resumo agregado de entradas de log de acesso |
| `ActionInput` | struct | Uma definição de parâmetro de entrada do `action.yml` |
| `ActionMetadata` | struct | Metadados analisados (parsed) do `action.yml` para uma ação composta |
| `ActionOutput` | struct | Uma definição de saída do `action.yml` |
| `ActionlintStats` | struct | Estatísticas de análise estática de uma execução do actionlint |
| `AddInteractiveConfig` | struct | Configuração para o comando interativo `add-wizard` |
| `AgenticAssessment` | struct | Avaliação de comportamento agentista derivada de logs de auditoria |
| `AmbientContextMetrics` | struct | Métricas de token para contexto ambiente (contagens de tokens de entrada, em cache, efetivos) |
| `Argument` | struct | Uma definição de argumento de linha de comando da API do registro MCP |
| `ArtifactSet` | string alias | Conjunto nomeado de artefatos (ex: `"agent"`, `"detection"`) |
| `AuditComparisonClassification` | struct | Um rótulo de classificação e códigos de motivo para uma comparação de auditoria |
| `AuditComparisonData` | struct | Comparação completa entre duas execuções de auditoria |
| `AuditComparisonBaseline` | struct | Métricas de linha de base para uma comparação de auditoria |
| `AuditComparisonDelta` | struct | Delta numérico entre a linha de base e a execução comparada |
| `AuditComparisonIntDelta` | struct | Delta com valor inteiro em uma comparação de auditoria |
| `AuditComparisonMCPFailureDelta` | struct | Delta na contagem de falhas MCP em uma comparação de auditoria |
| `AuditComparisonRecommendation` | struct | Uma recomendação produzida por uma comparação de auditoria |
| `AuditComparisonStringDelta` | struct | Delta com valor de string em uma comparação de auditoria |
| `AuditEngineConfig` | struct | Configuração de engine capturada em uma execução de auditoria |
| `AuditLogEntry` | struct | Uma entrada estruturada do log de auditoria do agente |
| `AwContext` | struct | Contexto de fluxo de trabalho agentista analisado da execução |
| `AwInfo` | struct | Bloco de metadados `gh-aw` de nível superior de um artefato de auditoria |
| `AwInfoSteps` | struct | Metadados de nível de passo em `aw_info.json` (ex: tipo de firewall) |
| `BashCommandsDiff` | struct | Diferença (diff) por comando de chamadas de ferramentas bash entre duas execuções de auditoria |
| `BehaviorFingerprint` | struct | Impressão digital de padrão do comportamento do agente ao longo dos turnos |
| `CheckState` | string alias | Estado de verificação de CI (`"success"`, `"failure"`, `"pending"`, ...) |
| `CodemodResult` | struct | Resultado de uma única transformação codemod |
| `CommandProvider` | interface | Interface implementada pelos comandos raiz Cobra para auxiliares de autocompletar shell |
| `CompilationStats` | struct | Estatísticas de uma execução de compilação (arquivos, erros, avisos) |
| `CompileValidationError` | struct | Um erro de validação emitido durante a compilação |
| `CombinedTrialResult` | struct | Resultados combinados de múltiplas execuções de teste (trial) |
| `ContinuationData` | struct | Estado para continuações de agente de múltiplos turnos |
| `CopilotCodingAgentDetector` | struct | Detector para padrões de log do coding-agent do Copilot |
| `CopilotWorkflowStep` | struct | Um único passo de um arquivo YAML setup-steps do Copilot |
| `CreatedItemReport` | struct | Relatório de um item criado por uma ação safe-output (tipo, URL, número, repositório) |
| `CrossRunSummary` | struct | Resumo de métricas entre execuções através de múltiplas execuções de fluxo de trabalho |
| `DependencyInfo` | struct | Metadados para uma única dependência no `go.mod` ou `package.json` |
| `DependencyInfoWithIndirect` | struct | `DependencyInfo` estendido com uma flag `Indirect` |
| `DevcontainerBuild` | struct | Seção de configuração de build do `devcontainer.json` |
| `DevcontainerCodespaces` | struct | Configurações específicas do GitHub Codespaces no `devcontainer.json` |
| `DevcontainerConfig` | struct | Configuração analisada do `.devcontainer/devcontainer.json` |
| `DevcontainerCustomizations` | struct | Bloco de customizações do VSCode no `devcontainer.json` |
| `DevcontainerRepoPermissions` | struct | Bloco de permissões de repositório no `devcontainer.json` |
| `DevcontainerVSCode` | struct | Bloco de configurações específicas do VSCode no `devcontainer.json` |
| `DifcFilteredEvent` | struct | Um evento filtrado por DIFC do log do gateway MCP |
| `DockerUnavailableError` | struct | Erro retornado quando o daemon do Docker não está acessível |
| `DomainAnalysis` | struct | Análise agregada de requisições de rede por domínio |
| `DomainBuckets` | struct | Requisições de domínio agrupadas por categoria (permitir, negar, desconhecido) |
| `DomainDiffEntry` | struct | Diferença (diff) por domínio entre duas execuções |
| `DownloadResult` | struct | Resultado de um download de artefato de log |
| `EpisodeData` | struct | Um único episódio de agente (um turno de chamada de ferramenta) |
| `ErrorInfo` | struct | Erro estruturado capturado de uma execução de agente |
| `ErrorSummary` | struct | Resumo de erros agregado para uma execução de fluxo de trabalho |
| `FetchedWorkflow` | struct | Um fluxo de trabalho buscado de uma fonte remota ou local com metadados |
| `FileInfo` | struct | Metadados de arquivo capturados durante uma execução de fluxo de trabalho |
| `Finding` | struct | Um achado de um scanner de segurança (Zizmor/Poutine/Actionlint) |
| `FirewallAnalysis` | struct | Análise de logs do firewall de rede AWF |
| `FirewallDiff` | struct | Diferença (diff) de acesso a domínios de firewall entre duas execuções de auditoria |
| `FirewallDiffSummary` | struct | Estatísticas de resumo para um diff de firewall |
| `FirewallLogEntry` | struct | Uma única entrada do log do firewall AWF |
| `GatewayLogEntry` | struct | Uma entrada de log do proxy do gateway MCP |
| `GatewayMetrics` | struct | Métricas agregadas dos logs do gateway MCP |
| `GatewayServerMetrics` | struct | Métricas por servidor do gateway MCP |
| `GatewayToolMetrics` | struct | Métricas por ferramenta do gateway MCP |
| `GitHubRateLimitDiff` | struct | Diferença (diff) de consumo de limite de taxa (rate-limit) da API do GitHub entre duas execuções de auditoria |
| `GitHubRateLimitEntry` | struct | Um instantâneo (snapshot) do limite de taxa da API do GitHub da execução do agente |
| `GitHubWorkflow` | struct | Metadados mínimos de fluxo de trabalho do GitHub Actions |
| `GuardPolicyEvent` | struct | Um único evento de avaliação de política de guarda (guard-policy) do log do gateway MCP |
| `GuardPolicySummary` | struct | Resumo das avaliações de política de guarda durante uma execução |
| `InitOptions` | struct | Opções para `InitRepository` |
| `JobData` | struct | Dados para um único job do GitHub Actions |
| `JobInfo` | struct | Metadados para um job do GitHub Actions |
| `JobInfoWithDuration` | struct | `JobInfo` estendido com uma string de duração legível por humanos |
| `ListWorkflowRunsOptions` | struct | Opções para listar execuções de fluxo de trabalho |
| `LockFileStatus` | struct | Status de um arquivo `.lock.yml` compilado |
| `LogsData` | struct | Dados de log completos baixados para uma execução de fluxo de trabalho |
| `LogsSummary` | struct | Visualização resumida dos dados de log baixados |
| `MCPConfig` | struct | Configuração do servidor MCP conforme analisada de um fluxo de trabalho |
| `MCPFailureReport` | struct | Relatório de falhas do servidor MCP durante uma execução |
| `MCPLogsGuardrailResponse` | struct | Resposta de avaliação de grade de proteção (guardrail) da análise de log MCP |
| `MCPPackage` | struct | Uma entrada de pacote npm/pip usada por um servidor MCP |
| `MCPRegistryServerForProcessing` | struct | Entrada de servidor recuperada do registro MCP |
| `MCPServerHealth` | struct | Métricas de saúde para um único servidor MCP |
| `MCPServerHealthDetail` | struct | Detalhamento de saúde detalhado para um único servidor MCP |
| `MCPSlowestToolCall` | struct | A chamada de ferramenta mais lenta registrada para um servidor MCP |
| `MCPToolCall` | struct | Uma única invocação de ferramenta MCP de um turno de agente |
| `MCPToolDiffEntry` | struct | Entrada de diff por ferramenta entre duas execuções de auditoria |
| `MCPToolSummary` | struct | Resumo de uso de ferramentas MCP agregado |
| `MCPToolUsageData` | struct | Contagens de uso e latências por ferramenta |
| `MCPToolUsageSummary` | struct | Resumo de uso de ferramentas MCP agregado para uma execução |
| `MCPToolsDiff` | struct | Diferença (diff) completa de chamadas de ferramentas MCP entre duas execuções de auditoria |
| `MCPToolsDiffSummary` | struct | Estatísticas de resumo para um diff de ferramentas MCP |
| `MetricsData` | struct | Métricas de desempenho principais para uma execução de fluxo de trabalho |
| `MetricsTrendData` | struct | Dados de tendência para uma métrica através de múltiplas execuções |
| `MissingDataReport` | struct | Relatório de dados esperados ausentes em uma execução |
| `MissingDataSummary` | struct | Resumo agregado de relatórios de dados ausentes |
| `MissingToolReport` | struct | Relatório de uma ferramenta MCP ausente durante uma execução |
| `MissingToolSummary` | struct | Resumo agregado de relatórios de ferramentas ausentes |
| `ModelTokenUsage` | struct | Uso de tokens para um único modelo de IA |
| `ModelTokenUsageRow` | struct | Uma única linha em uma tabela de uso de tokens de modelo |
| `NoopReport` | struct | Relatório para um evento de saída segura sem operação (noop safe-output) |
| `ObservabilityInsight` | struct | Um insight derivado de dados de observabilidade |
| `OverviewData` | struct | Dados de visão geral de alto nível para uma execução de fluxo de trabalho |
| `PRCheckRun` | struct | Uma única execução de verificação de CI anexada a um pull request |
| `PRCommitStatus` | struct | Um contexto de status de commit para um pull request |
| `PRInfo` | struct | Metadados de pull request usados pelos comandos `gh aw pr` |
| `PerRunFirewallBreakdown` | struct | Detalhamento de domínio de firewall por execução em um relatório de várias execuções |
| `PerformanceMetrics` | struct | Contadores de desempenho para uma execução de fluxo de trabalho |
| `PolicyAnalysis` | struct | Análise de resultados de avaliação de política de guarda |
| `PolicyManifest` | struct | Um manifesto de políticas de guarda aplicadas durante uma execução |
| `PolicyRule` | struct | Uma única regra de política de firewall do manifesto de política |
| `PolicySummaryDisplay` | struct | Resumo amigável para exibição de resultados de avaliação de política |
| `PollResult` | int alias | Código de resultado retornado por `PollWithSignalHandling` |
| `ProcessedRun` | struct | Uma execução de fluxo de trabalho totalmente processada com artefatos analisados |
| `ProjectConfig` | struct | Configuração para `gh aw project new` |
| `PromptAnalysis` | struct | Análise do prompt enviado ao agente |
| `ProxyInfo` | struct | Configuração do servidor proxy para requisições de rede |
| `PullRequest` | struct | Um pull request do GitHub |
| `RPCMessageEntry` | struct | Uma única mensagem RPC dos logs do gateway MCP |
| `Recommendation` | struct | Uma recomendação acionável derivada de dados de auditoria |
| `RedactedDomainsAnalysis` | struct | Análise de entradas de domínio redigidas em logs de firewall |
| `RedactedDomainsLogSummary` | struct | Dados de log de domínios redigidos resumidos |
| `Release` | struct | Uma entrada de release do GitHub |
| `Remote` | struct | Um remote Git |
| `RepoSpec` | struct | Um especificador de repositório analisado (`dono/repositorio[@ref]`) |
| `Repository` | struct | Um repositório do GitHub |
| `RuleHitStats` | struct | Estatísticas para uma única regra de firewall AWF |
| `RunData` | struct | Todos os dados coletados para uma única execução de fluxo de trabalho |
| `RunMetricsDiff` | struct | Diferença (diff) de métricas principais entre duas execuções de auditoria |
| `RunSummary` | struct | Resumo de uma execução de fluxo de trabalho |
| `SafeOutputChainMetrics` | struct | Métricas para cadeias de ações safe-output em uma execução |
| `SafeOutputSummary` | struct | Resumo de eventos safe-output em uma execução |
| `SafeOutputTypeDetail` | struct | Informações detalhadas para um único tipo de safe-output |
| `SecretInfo` | struct | Metadados para um segredo de repositório configurado |
| `SecretRequirement` | struct | Um segredo necessário para um fluxo de trabalho |
| `ServerDetail` | struct | Detalhes completos para um servidor da API do registro MCP |
| `ServerListResponse` | struct | Envelope de resposta do endpoint `/v0.1/servers` do registro MCP |
| `ServerResponse` | struct | Envelope de resposta envolvendo dados do servidor e metadados do registro |
| `SessionAnalysis` | struct | Análise de metadados de sessão do agente |
| `ShellType` | string alias | Tipo de shell detectado por `DetectShell` (ex: `"bash"`, `"zsh"`) |
| `SourceSpec` | struct | Um especificador de origem de fluxo de trabalho analisado (local, remoto ou registro) |
| `TaskDomainInfo` | struct | Informações de domínio associadas a uma tarefa específica do agente |
| `TokenUsageDiff` | struct | Diferença (diff) de uso de tokens entre duas execuções de auditoria |
| `TokenUsageEntry` | struct | Uso de tokens por requisição do agente |
| `TokenUsageSummary` | struct | Uso de tokens agregado para uma execução de fluxo de trabalho |
| `ToolCallDiffEntry` | struct | Entrada de diff por chamada de ferramenta entre duas execuções de auditoria |
| `ToolCallInfo` | type alias | Alias para `workflow.ToolCallInfo` — um único registro de chamada de ferramenta |
| `ToolCallsDiff` | struct | Diferença (diff) completa de chamadas de ferramenta entre duas execuções de auditoria |
| `ToolCallsDiffSummary` | struct | Estatísticas de resumo para um diff de chamadas de ferramenta |
| `ToolTransition` | struct | Uma transição entre chamadas de ferramenta em um episódio de agente |
| `ToolUsageInfo` | struct | Informações de uso para uma única ferramenta |
| `ToolUsageSummary` | struct | Estatísticas de uso de ferramentas agregadas |
| `Transport` | struct | Configuração de transporte do servidor MCP |
| `TrendDirection` | int alias | Direção de uma tendência de métrica (`Subindo`, `Descendo`, `Estável`) |
| `TrialArtifacts` | struct | Artefatos gerados durante uma execução de teste (trial) |
| `TrialRepoContext` | struct | Contexto de repositório usado durante uma execução de teste (trial) |
| `VSCodeMCPServer` | struct | Uma entrada de servidor MCP em `.vscode/mcp.json` |
| `VSCodeSettings` | struct | Configuração `.vscode/settings.json` analisada |
| `ValidationResult` | struct | Resultado de uma passagem de validação de compilação de fluxo de trabalho |
| `Workflow` | struct | Metadados mínimos de fluxo de trabalho usados em operações de listagem |
| `WorkflowDomainsDetail` | struct | Informações detalhadas de domínio por fluxo de trabalho |
| `WorkflowDomainsSummary` | struct | Resumo de domínios usados em todos os fluxos de trabalho |
| `WorkflowFailure` | struct | Um registro de falha de fluxo de trabalho |
| `WorkflowFileStatus` | struct | Status de um arquivo de fluxo de trabalho (existe, desatualizado, etc.) |
| `WorkflowJob` | struct | Um job do GitHub Actions dentro de uma execução de fluxo de trabalho |
| `WorkflowListItem` | struct | Um único item na saída de `gh aw list` |
| `WorkflowMCPMetadata` | struct | Metadados de servidor MCP escaneados de um arquivo de fluxo de trabalho |
| `WorkflowNode` | struct | Um nó no grafo de dependência de fluxo de trabalho |
| `WorkflowOption` | struct | Uma opção de fluxo de trabalho selecionável para prompts interativos |
| `WorkflowRun` | struct | Um registro de execução de fluxo de trabalho do GitHub Actions |
| `WorkflowRunInfo` | struct | Resumo de uma execução de fluxo de trabalho da API do GitHub |
| `WorkflowSpec` | struct | Uma especificação de fluxo de trabalho totalmente resolvida com metadados de origem |
| `WorkflowStats` | struct | Estatísticas agregadas para um fluxo de trabalho |
| `LogMetrics` | type alias | Alias para `workflow.LogMetrics` — métricas de análise de log |
| `PostTransformFunc` | func type | Uma função de transformação pós-compilação |
| `LogParser[T]` | generic func type | Tipo de função analisadora de log genérica parametrizada no resultado da análise |

## Exemplos de Uso

### Compilando um fluxo de trabalho

```go
data, err := cli.CompileWorkflows(ctx, cli.CompileConfig{
    MarkdownFiles: []string{".github/workflows/my-workflow.md"},
    Verbose:       true,
    Validate:      true,
    Strict:        false,
})
```

### Executando um fluxo de trabalho

```go
err := cli.RunWorkflowOnGitHub(ctx, "my-workflow", cli.RunOptions{
    Repo:    "owner/repo",
    Verbose: true,
})
```

### Auditando uma execução

```go
err := cli.AuditWorkflowRun(ctx, runID, cli.AuditOptions{
    Owner:     "owner",
    Repo:      "repo",
    Hostname:  "github.com",
    OutputDir: "/tmp/output",
    Verbose:   true,
    Parse:     true,
})
```

### Verificando a saúde do fluxo de trabalho

```go
err := cli.RunHealth(cli.HealthConfig{
    Pattern:   "*.md",
    Threshold: 0.8,
    Period:    "30d",
})
```

## Decisões de Design

- **Decomposição de arquivo por funcionalidade**: Grandes domínios de funcionalidades (compile, audit, logs, run) são divididos em múltiplos arquivos (`_command.go`, `_config.go`, `_helpers.go`, `_orchestrator.go`, etc.) para manter cada arquivo focado e abaixo de 300 linhas.
- **Funções Run testáveis**: Todo comando tem um `New*Command()` para fiação Cobra e uma função `Run*()` com parâmetros explícitos para testes unitários sem sobrecarga de análise de argumentos da CLI.
- **Stderr para diagnósticos**: Todas as mensagens visíveis ao usuário usam auxiliares `console.Format*Message` e escrevem para `stderr`, preservando `stdout` para saída estruturada legível por máquina.
- **Propagação de contexto**: Operações de longa duração aceitam `context.Context` para suportar cancelamento (SIGINT, timeouts).
- **Structs de configuração**: As opções de comando são coletadas em structs dedicadas `*Config` ou `*Options` em vez de serem passadas como longas listas de argumentos, melhorando a legibilidade e testabilidade.

## Dependências

**Internas**:
- `github.com/github/gh-aw/pkg/workflow` — compilação de fluxo de trabalho e tipos de dados
- `github.com/github/gh-aw/pkg/parser` — análise de frontmatter markdown
- `github.com/github/gh-aw/pkg/console` — formatação de saída do terminal
- `github.com/github/gh-aw/pkg/logger` — log de depuração estruturado
- `github.com/github/gh-aw/pkg/testutil` — fixtures de teste compartilhadas e auxiliares de asserção usados pelos testes do pacote CLI
- `github.com/github/gh-aw/pkg/constants` — nomes de engine, nomes de job, flags de funcionalidade
- `github.com/github/gh-aw/pkg/agentdrain` — detecção de anomalias de log Drain para análise de auditoria
- `github.com/github/gh-aw/pkg/envutil` — leitura de variáveis de ambiente com validação de limites
- `github.com/github/gh-aw/pkg/errorutil` — auxiliares compartilhados de classificação de erros para respostas do GitHub e da CLI gh
- `github.com/github/gh-aw/pkg/semverutil` — comparação de versão semântica para verificações de dependência
- `github.com/github/gh-aw/pkg/sliceutil` — utilitários de slice
- `github.com/github/gh-aw/pkg/stats` — estatísticas incrementais para métricas de saúde
- `github.com/github/gh-aw/pkg/styles` — estilos de cor de terminal e configuração lipgloss
- `github.com/github/gh-aw/pkg/timeutil` — formatação de duração legível por humanos
- `github.com/github/gh-aw/pkg/tty` — detecção de terminal
- `github.com/github/gh-aw/pkg/types` — tipos de configuração de servidor MCP compartilhados
- `github.com/github/gh-aw/pkg/typeutil` — auxiliares de conversão de tipo para valores de frontmatter dinâmicos
- `github.com/github/gh-aw/pkg/fileutil` — auxiliares de sistema de arquivos
- `github.com/github/gh-aw/pkg/gitutil` — auxiliares de Git e GitHub CLI
- `github.com/github/gh-aw/pkg/repoutil` — análise e normalização de nome de repositório
- `github.com/github/gh-aw/pkg/stringutil` — utilitários de manipulação e sanitização de string

**Externas**:
- `github.com/spf13/cobra` — framework de CLI
- `github.com/cli/go-gh/v2` — integração com GitHub CLI

## Segurança de Threads (Thread Safety)

Funções `Run*` de comandos individuais não são seguras para concorrência, a menos que explicitamente documentado. O orquestrador `CompileWorkflows` serializa a compilação por padrão; a compilação paralela é controlada por flags de `CompileConfig`.

---

*Esta especificação é mantida automaticamente pelo fluxo de trabalho [spec-extractor](../../.github/workflows/spec-extractor.md).*
