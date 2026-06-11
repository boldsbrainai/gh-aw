---
description: Guia abrangente para implementar engines agentic personalizadas em gh-aw
applyTo: "pkg/workflow/*engine*.go"
disable-model-invocation: true
---

# Guia de Implementação de Engine Agentic Personalizada

Este documento fornece um guia abrangente para implementar engines agentic personalizadas em GitHub Agentic Workflows (gh-aw). Ele cobre padrões de arquitetura, oportunidades comuns de refatoração e instruções de implementação passo a passo.

## Tabela de Conteúdo

1. [Visão Geral da Arquitetura](#visão-geral-da-arquitetura)
2. [Design da Interface da Engine](#design-da-interface-da-engine)
3. [Análise de Código Comum & Oportunidades de Refatoração](#análise-de-código-comum--oportunidades-de-refatoração)
4. [Guia de Implementação](#guia-de-implementação)
5. [Estratégia de Testes](#estratégia-de-testes)
6. [Lista de Verificação de Integração](#lista-de-verificação-de-integração)

---

## Visão Geral da Arquitetura

### Princípio de Segregação de Interface

A arquitetura de engine agentic segue o **Princípio de Segregação de Interface (ISP)** para evitar forçar implementações a depender de métodos que não utilizam. O sistema usa **composição de interfaces** para fornecer flexibilidade enquanto mantém a compatibilidade retroativa.

### Hierarquia de Interface

```
Engine (identidade central - obrigatório para todos)
├── GetID()
├── GetDisplayName()
├── GetDescription()
└── IsExperimental()

CapabilityProvider (detecção de recursos - opcional)
├── SupportsToolsAllowlist()
├── SupportsHTTPTransport()
├── SupportsMaxTurns()
├── SupportsWebFetch()
├── SupportsWebSearch()
├── SupportsFirewall()
├── SupportsPlugins()
└── SupportsLLMGateway()

WorkflowExecutor (compilação - obrigatório)
├── GetDeclaredOutputFiles()
├── GetInstallationSteps()
└── GetExecutionSteps()

MCPConfigProvider (servidores MCP - opcional)
└── RenderMCPConfig()

LogParser (análise de logs - opcional)
├── ParseLogMetrics()
├── GetLogParserScriptId()
└── GetLogFileForParsing()

SecurityProvider (recursos de segurança - opcional)
├── GetDefaultDetectionModel()
└── GetRequiredSecretNames()

CodingAgentEngine (composto - compatibilidade retroativa)
└── Compõe todas as interfaces acima
```

### Padrões Arquiteturais Chave

1. **Embedding de BaseEngine**: Todas as engines embutem `BaseEngine` que fornece implementações padrão
2. **Interfaces Focadas**: Cada interface tem uma responsabilidade única
3. **Recursos Opcionais**: Engines sobrescrevem apenas os métodos que precisam
4. **Compatibilidade Retroativa**: A interface composta `CodingAgentEngine` mantém a compatibilidade

---

## Design da Interface da Engine

### Identidade Central da Engine

Cada engine deve implementar a interface `Engine`:

```go
type Engine interface {
    GetID() string            // Identificador único (ex: "copilot", "claude", "codex")
    GetDisplayName() string   // Nome legível por humanos (ex: "GitHub Copilot CLI")
    GetDescription() string   // Descrição da capacidade
    IsExperimental() bool     // Flag de status experimental
}
```

### Detecção de Capacidade

Engines podem implementar `CapabilityProvider` para indicar suporte a recursos:

```go
type CapabilityProvider interface {
    SupportsToolsAllowlist() bool    // Lista de permissão de ferramentas MCP
    SupportsHTTPTransport() bool     // Transporte HTTP para servidores MCP
    SupportsMaxTurns() bool          // Recurso de max-turns
    SupportsWebFetch() bool          // Ferramenta web-fetch embutida
    SupportsWebSearch() bool         // Ferramenta web-search embutida
    SupportsFirewall() bool          // Firewall de rede/sandboxing
    SupportsPlugins() bool           // Instalação de plugins
    SupportsLLMGateway() int         // Porta do gateway LLM (ou -1 se não suportado)
}
```

### Compilação de Fluxo de Trabalho

Todas as engines devem implementar `WorkflowExecutor`:

```go
type WorkflowExecutor interface {
    GetDeclaredOutputFiles() []string                                    // Arquivos de saída para upload
    GetInstallationSteps(workflowData *WorkflowData) []GitHubActionStep  // Etapas de instalação
    GetExecutionSteps(workflowData *WorkflowData, logFile string) []GitHubActionStep // Etapas de execução
}
```

### Interfaces Opcionais

Engines podem implementar opcionalmente:

- **MCPConfigProvider**: Para configuração de servidor MCP
- **LogParser**: Para análise de log personalizada e extração de métricas
- **SecurityProvider**: Para recursos de segurança e gerenciamento de segredos

---

## Análise de Código Comum & Oportunidades de Refatoração

### Implementações Atuais de Engine (LOC)

```
claude_engine.go:    474 linhas
codex_engine.go:     523 linhas
copilot_engine.go:   170 linhas
custom_engine.go:    373 linhas
Total:              1540 linhas
```

### Auxiliares Compartilhados Existentes

A base de código já possui módulos auxiliares bem organizados:

#### 1. **engine_helpers.go** (501 linhas)
Funções comuns de instalação e utilitários:
- `GetBaseInstallationSteps()` - Validação de segredo + instalação npm
- `BuildStandardNpmEngineInstallSteps()` - Configuração padrão de engine npm
- `InjectCustomEngineSteps()` - Injeção de etapa personalizada
- `FormatStepWithCommandAndEnv()` - Formatação de etapa
- `FilterEnvForSecrets()` - Filtragem de env com foco em segurança
- `GetHostedToolcachePathSetup()` - Configuração de caminho de runtime
- `GetNpmBinPathSetup()` - Configuração de caminho de binário NPM
- `ResolveAgentFilePath()` - Resolução de caminho de arquivo de agente
- `ExtractAgentIdentifier()` - Extração de identificador de agente

#### 2. **awf_helpers.go** (248 linhas)
Integração AWF (firewall/sandbox):
- `BuildAWFCommand()` - Construção completa de comando AWF
- `BuildAWFArgs()` - Geração de argumentos AWF
- `GetAWFCommandPrefix()` - Determinação de comando AWF
- `WrapCommandInShell()` - Wrapper de shell para AWF

#### 3. **Configuração MCP** (Múltiplos arquivos)
- `mcp_config_builtin.go` - Configurações de servidor MCP embutidas
- `mcp_config_custom.go` - Manipulação de servidor MCP personalizado
- `mcp_config_playwright_renderer.go` - Renderização MCP Playwright
- `mcp_renderer.go` - Framework de renderização MCP unificado

### Oportunidades de Refatoração Identificadas

#### Oportunidade 1: Consolidar Padrões de Renderização MCP

**Estado Atual**: Cada engine tem seu próprio método `RenderMCPConfig()` com estrutura similar:

```go
// Engines Claude, Codex e Custom seguem este padrão
func (e *Engine) RenderMCPConfig(yaml *strings.Builder, tools map[string]any, mcpTools []string, workflowData *WorkflowData) {
    createRenderer := func(isLast bool) *MCPConfigRendererUnified {
        return NewMCPConfigRenderer(MCPRendererOptions{...})
    }
    
    RenderJSONMCPConfig(yaml, tools, mcpTools, workflowData, JSONMCPConfigOptions{
        ConfigPath: "/caminho/para/config",
        GatewayConfig: buildMCPGatewayConfig(workflowData),
        Renderers: MCPToolRenderers{...},
    })
}
```

**Recomendação de Refatoração**:
- Extrair padrão de fábrica de renderizador MCP comum
- Criar auxiliar `BuildStandardJSONMCPConfig()`
- Reduzir duplicação entre engines

#### Oportunidade 2: Padronizar Geração de Etapas de Instalação

**Estado Atual**: Engines usam padrões diferentes para instalação:
- Copilot: Usa abordagem de script instalador
- Claude/Codex: Usam instalação baseada em npm
- Todas validam segredos de forma diferente

**Recomendação de Refatoração**:
- Já bem abstraído via `GetBaseInstallationSteps()`
- Considere adicionar `BuildInstallerScriptSteps()` para engines não-npm
- Padronizar integração de instalação AWF

#### Oportunidade 3: Unificar Infraestrutura de Análise de Log

**Estado Atual**: Cada engine tem arquivos dedicados de análise de log:
- `copilot_logs.go` (abrangente)
- `claude_logs.go` (análise JSON estruturada)
- `codex_logs.go` (análise baseada em regex)

**Recomendação de Refatoração**:
- Extrair padrões de análise de log comuns (contagem de turnos, uso de tokens)
- Criar `BaseLogParser` com utilitários comuns
- Manter análise específica de engine em arquivos separados

#### Oportunidade 4: Simplificar Gerenciamento de Variáveis de Ambiente

**Estado Atual**: Cada engine constrói manualmente mapas de ambiente com:
- Referências a segredos
- Configuração de saídas seguras
- Variáveis de ambiente personalizadas
- Configuração de modelo

**Recomendação de Refatoração**:
- Criar auxiliar `BuildBaseEngineEnv()` para variáveis de ambiente comuns
- Padronizar filtragem de segredos via `FilterEnvForSecrets()` (já existe)
- Extrair lógica de variável de ambiente de modelo

---

## Guia de Implementação

### Passo 1: Definir Estrutura da Engine

```go
package workflow

import (
    "github.com/github/gh-aw/pkg/logger"
)

var myEngineLog = logger.New("workflow:my_engine")

// MyEngine representa a engine agentic personalizada My
type MyEngine struct {
    BaseEngine
}

func NewMyEngine() *MyEngine {
    return &MyEngine{
        BaseEngine: BaseEngine{
            id:                     "my-engine",
            displayName:            "Minha Engine Personalizada",
            description:            "Engine de IA personalizada com capacidades XYZ",
            experimental:           false, // Defina como true se experimental
            supportsToolsAllowlist: true,
            supportsHTTPTransport:  true,
            supportsMaxTurns:       false,
            supportsWebFetch:       false,
            supportsWebSearch:      false,
            supportsFirewall:       true,
            supportsPlugins:        false,
            supportsLLMGateway:     false, // Sobrescreva SupportsLLMGateway() se true
        },
    }
}
```

### Passo 2: Implementar Segredos Necessários

```go
func (e *MyEngine) GetRequiredSecretNames(workflowData *WorkflowData) []string {
    secrets := []string{"MY_ENGINE_API_KEY"}
    
    // Adicione chave de API do gateway MCP se servidores MCP estiverem presentes
    if HasMCPServers(workflowData) {
        secrets = append(secrets, "MCP_GATEWAY_API_KEY")
    }
    
    // Adicione segredos de safe-inputs se habilitado
    if IsSafeInputsEnabled(workflowData.SafeInputs, workflowData) {
        safeInputsSecrets := collectSafeInputsSecrets(workflowData.SafeInputs)
        for varName := range safeInputsSecrets {
            secrets = append(secrets, varName)
        }
    }
    
    return secrets
}
```

### Passo 3: Implementar Etapas de Instalação

```go
func (e *MyEngine) GetInstallationSteps(workflowData *WorkflowData) []GitHubActionStep {
    myEngineLog.Printf("Gerando etapas de instalação: workflow=%s", workflowData.Name)
    
    // Pule a instalação se o comando personalizado for especificado
    if workflowData.EngineConfig != nil && workflowData.EngineConfig.Command != "" {
        myEngineLog.Printf("Pulando instalação: comando personalizado especificado (%s)", workflowData.EngineConfig.Command)
        return []GitHubActionStep{}
    }
    
    // Use etapas de instalação base (validação de segredo + instalação npm)
    steps := GetBaseInstallationSteps(EngineInstallConfig{
        Secrets:         []string{"MY_ENGINE_API_KEY"},
        DocsURL:         "https://example.com/docs/my-engine",
        NpmPackage:      "@company/my-engine",
        Version:         "1.0.0", // Use constante: string(constants.DefaultMyEngineVersion)
        Name:            "My Engine",
        CliName:         "my-engine",
        InstallStepName: "Instalar CLI My Engine",
    }, workflowData)
    
    // Adicione instalação AWF se firewall estiver habilitado
    if isFirewallEnabled(workflowData) {
        firewallConfig := getFirewallConfig(workflowData)
        agentConfig := getAgentConfig(workflowData)
        var awfVersion string
        if firewallConfig != nil {
            awfVersion = firewallConfig.Version
        }
        
        awfInstall := generateAWFInstallationStep(awfVersion, agentConfig)
        if len(awfInstall) > 0 {
            steps = append(steps, awfInstall)
        }
    }
    
    return steps
}
```

### Passo 4: Implementar Etapas de Execução

```go
func (e *MyEngine) GetExecutionSteps(workflowData *WorkflowData, logFile string) []GitHubActionStep {
    modelConfigured := workflowData.EngineConfig != nil && workflowData.EngineConfig.Model != ""
    firewallEnabled := isFirewallEnabled(workflowData)
    
    myEngineLog.Printf("Construindo etapas de execução: workflow=%s, model=%s, firewall=%v",
        workflowData.Name, getModel(workflowData), firewallEnabled)
    
    // Lide com etapas personalizadas se existirem na configuração da engine
    steps := InjectCustomEngineSteps(workflowData, e.convertStepToYAML)
    
    // Construir argumentos de comando da engine
    var engineArgs []string
    
    // Adicione modelo se especificado
    if modelConfigured {
        engineArgs = append(engineArgs, "--model", workflowData.EngineConfig.Model)
    }
    
    // Adicione configuração MCP se servidores estiverem presentes
    if HasMCPServers(workflowData) {
        engineArgs = append(engineArgs, "--mcp-config", "/tmp/gh-aw/mcp-config/mcp-servers.json")
    }
    
    // Construir o comando
    commandName := "my-engine"
    if workflowData.EngineConfig != nil && workflowData.EngineConfig.Command != "" {
        commandName = workflowData.EngineConfig.Command
    }
    
    engineCommand := fmt.Sprintf("%s %s \"$(cat /tmp/gh-aw/aw-prompts/prompt.txt)\"",
        commandName, shellJoinArgs(engineArgs))
    
    // Construir o comando completo com wrapping AWF se habilitado
    var command string
    if firewallEnabled {
        allowedDomains := GetMyEngineAllowedDomainsWithToolsAndRuntimes(
            workflowData.NetworkPermissions, 
            workflowData.Tools, 
            workflowData.Runtimes,
        )
        
        npmPathSetup := GetNpmBinPathSetup()
        engineCommandWithPath := fmt.Sprintf("%s && %s", npmPathSetup, engineCommand)
        
        command = BuildAWFCommand(AWFCommandConfig{
            EngineName:     "my-engine",
            EngineCommand:  engineCommandWithPath,
            LogFile:        logFile,
            WorkflowData:   workflowData,
            UsesTTY:        false,
            UsesAPIProxy:   false,
            AllowedDomains: allowedDomains,
        })
    } else {
        command = fmt.Sprintf(`set -o pipefail
%s 2>&1 | tee %s`, engineCommand, logFile)
    }
    
    // Construir variáveis de ambiente
    env := map[string]string{
        "MY_ENGINE_API_KEY":  "${{ secrets.MY_ENGINE_API_KEY }}",
        "GH_AW_PROMPT":       "/tmp/gh-aw/aw-prompts/prompt.txt",
        "GITHUB_WORKSPACE":   "${{ github.workspace }}",
    }
    
    // Adicione env var de configuração MCP se necessário
    if HasMCPServers(workflowData) {
        env["GH_AW_MCP_CONFIG"] = "/tmp/gh-aw/mcp-config/mcp-servers.json"
    }
    
    // Adicione env de saídas seguras
    applySafeOutputEnvToMap(env, workflowData)
    
    // Adicione env var de modelo se não configurado explicitamente
    if !modelConfigured {
        isDetectionJob := workflowData.SafeOutputs == nil
        if isDetectionJob {
            env["GH_AW_MODEL_DETECTION_MY_ENGINE"] = "${{ vars.GH_AW_MODEL_DETECTION_MY_ENGINE || '' }}"
        } else {
            env["GH_AW_MODEL_AGENT_MY_ENGINE"] = "${{ vars.GH_AW_MODEL_AGENT_MY_ENGINE || '' }}"
        }
    }
    
    // Gerar a etapa de execução
    stepLines := []string{
        "      - name: Executar My Engine",
        "        id: agentic_execution",
    }
    
    // Filtrar variáveis de ambiente para segurança
    allowedSecrets := e.GetRequiredSecretNames(workflowData)
    filteredEnv := FilterEnvForSecrets(env, allowedSecrets)
    
    // Formatar etapa com comando e ambiente
    stepLines = FormatStepWithCommandAndEnv(stepLines, command, filteredEnv)
    
    steps = append(steps, GitHubActionStep(stepLines))
    return steps
}
```

### Passo 5: Implementar Configuração MCP (Opcional)

```go
func (e *MyEngine) RenderMCPConfig(yaml *strings.Builder, tools map[string]any, mcpTools []string, workflowData *WorkflowData) {
    myEngineLog.Printf("Renderizando configuração MCP: tool_count=%d, mcp_tool_count=%d", len(tools), len(mcpTools))
    
    // Criar renderizador unificado com opções específicas da engine
    createRenderer := func(isLast bool) *MCPConfigRendererUnified {
        return NewMCPConfigRenderer(MCPRendererOptions{
            IncludeCopilotFields: false,
            InlineArgs:           false,
            Format:               "json", // ou "toml" para estilo Codex
            IsLast:               isLast,
            ActionMode:           GetActionModeFromWorkflowData(workflowData),
        })
    }
    
    // Usar renderizador de configuração JSON MCP compartilhado
    _ = RenderJSONMCPConfig(yaml, tools, mcpTools, workflowData, JSONMCPConfigOptions{
        ConfigPath:    "/tmp/gh-aw/mcp-config/mcp-servers.json",
        GatewayConfig: buildMCPGatewayConfig(workflowData),
        Renderers: MCPToolRenderers{
            RenderGitHub: func(yaml *strings.Builder, githubTool any, isLast bool, workflowData *WorkflowData) {
                renderer := createRenderer(isLast)
                renderer.RenderGitHubMCP(yaml, githubTool, workflowData)
            },
            RenderPlaywright: func(yaml *strings.Builder, playwrightTool any, isLast bool) {
                renderer := createRenderer(isLast)
                renderer.RenderPlaywrightMCP(yaml, playwrightTool)
            },
            RenderSerena: func(yaml *strings.Builder, serenaTool any, isLast bool) {
                renderer := createRenderer(isLast)
                renderer.RenderSerenaMCP(yaml, serenaTool)
            },
            RenderCacheMemory: e.renderCacheMemoryMCPConfig,
            RenderAgenticWorkflows: func(yaml *strings.Builder, isLast bool) {
                renderer := createRenderer(isLast)
                renderer.RenderAgenticWorkflowsMCP(yaml)
            },
            RenderSafeOutputs: func(yaml *strings.Builder, isLast bool, workflowData *WorkflowData) {
                renderer := createRenderer(isLast)
                renderer.RenderSafeOutputsMCP(yaml, workflowData)
            },
            RenderSafeInputs: func(yaml *strings.Builder, safeInputs *SafeInputsConfig, isLast bool) {
                renderer := createRenderer(isLast)
                renderer.RenderSafeInputsMCP(yaml, safeInputs, workflowData)
            },
            RenderWebFetch: func(yaml *strings.Builder, isLast bool) {
                renderMCPFetchServerConfig(yaml, "json", "              ", isLast, false)
            },
            RenderCustomMCPConfig: func(yaml *strings.Builder, toolName string, toolConfig map[string]any, isLast bool) error {
                return renderCustomMCPConfigWrapperWithContext(yaml, toolName, toolConfig, isLast, workflowData)
            },
        },
    })
}

func (e *MyEngine) renderCacheMemoryMCPConfig(yaml *strings.Builder, isLast bool, workflowData *WorkflowData) {
    // Cache-memory é um compartilhamento de arquivo simples, não um servidor MCP
    // Nenhuma configuração MCP necessária
}
```

### Passo 6: Implementar Análise de Log (Opcional)

```go
func (e *MyEngine) ParseLogMetrics(logContent string, verbose bool) LogMetrics {
    myEngineLog.Printf("Analisando métricas de log: log_size=%d bytes", len(logContent))
    
    var metrics LogMetrics
    lines := strings.Split(logContent, "\n")
    
    for _, line := range lines {
        // Analisar formato de log específico da engine
        // Extrair: turnos, uso de tokens, chamadas de ferramenta, erros
    }
    
    return metrics
}

func (e *MyEngine) GetLogParserScriptId() string {
    return "parse_my_engine_log"
}

func (e *MyEngine) GetLogFileForParsing() string {
    return "/tmp/gh-aw/agent-stdio.log"
}
```

### Passo 7: Registrar Engine

```go
// Em agentic_engine.go, adicione a NewEngineRegistry():
func NewEngineRegistry() *EngineRegistry {
    registry := &EngineRegistry{
        engines: make(map[string]CodingAgentEngine),
    }
    
    registry.Register(NewClaudeEngine())
    registry.Register(NewCodexEngine())
    registry.Register(NewCopilotEngine())
    registry.Register(NewCustomEngine())
    registry.Register(NewMyEngine()) // Adicione sua engine aqui
    
    return registry
}
```

---

## Estratégia de Testes

### Testes Unitários

Crie `my_engine_test.go`:

```go
package workflow

import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func TestMyEngine(t *testing.T) {
    engine := NewMyEngine()
    
    t.Run("identidade da engine", func(t *testing.T) {
        assert.Equal(t, "my-engine", engine.GetID())
        assert.Equal(t, "Minha Engine Personalizada", engine.GetDisplayName())
        assert.NotEmpty(t, engine.GetDescription())
    })
    
    t.Run("capacidades", func(t *testing.T) {
        assert.True(t, engine.SupportsToolsAllowlist())
        assert.True(t, engine.SupportsHTTPTransport())
        assert.True(t, engine.SupportsFirewall())
    })
    
    t.Run("segredos necessários", func(t *testing.T) {
        workflowData := &WorkflowData{Name: "test"}
        secrets := engine.GetRequiredSecretNames(workflowData)
        assert.Contains(t, secrets, "MY_ENGINE_API_KEY")
    })
}

func TestMyEngineInstallation(t *testing.T) {
    engine := NewMyEngine()
    workflowData := &WorkflowData{
        Name: "test-workflow",
    }
    
    steps := engine.GetInstallationSteps(workflowData)
    require.NotEmpty(t, steps, "Deve gerar etapas de instalação")
    
    // Verifique se a etapa de validação de segredo existe
    hasSecretValidation := false
    for _, step := range steps {
        for _, line := range step {
            if strings.Contains(line, "validate-secret") {
                hasSecretValidation = true
                break
            }
        }
    }
    assert.True(t, hasSecretValidation, "Deve incluir validação de segredo")
}

func TestMyEngineExecution(t *testing.T) {
    engine := NewMyEngine()
    workflowData := &WorkflowData{
        Name: "test-workflow",
        EngineConfig: &EngineConfig{
            ID: "my-engine",
        },
    }
    
    steps := engine.GetExecutionSteps(workflowData, "/tmp/test.log")
    require.NotEmpty(t, steps, "Deve gerar etapas de execução")
    
    // Verifique se o comando inclui invocação da engine
    hasEngineCommand := false
    for _, step := range steps {
        for _, line := range step {
            if strings.Contains(line, "my-engine") {
                hasEngineCommand = true
                break
            }
        }
    }
    assert.True(t, hasEngineCommand, "Deve incluir comando da engine")
}
```

### Testes de Integração

Crie `my_engine_integration_test.go`:

```go
//go:build integration

package workflow

import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func TestMyEngineWorkflowCompilation(t *testing.T) {
    compiler := NewCompiler()
    workflowPath := "testdata/my-engine-workflow.md"
    
    workflow, err := compiler.Compile(workflowPath)
    require.NoError(t, err)
    assert.NotNil(t, workflow)
    
    // Verifique a estrutura do fluxo de trabalho
    assert.Equal(t, "my-engine", workflow.EngineID)
    assert.NotEmpty(t, workflow.InstallationSteps)
    assert.NotEmpty(t, workflow.ExecutionSteps)
}
```

---

## Lista de Verificação de Integração

### Alterações de Código

- [ ] Criar `my_engine.go` com a implementação da engine
- [ ] Criar `my_engine_test.go` com testes unitários
- [ ] Criar `my_engine_integration_test.go` com testes de integração
- [ ] Adicionar registro da engine em `agentic_engine.go`
- [ ] Adicionar constantes da engine em `pkg/constants/constants.go`
- [ ] Criar `my_engine_logs.go` se análise de log personalizada for necessária
- [ ] Criar `my_engine_mcp.go` se renderização MCP personalizada for necessária

### Documentação

- [ ] Adicionar documentação da engine em `docs/src/content/docs/reference/engines/`
- [ ] Atualizar tabela comparativa de engines
- [ ] Adicionar instruções de configuração (chaves de API, configuração)
- [ ] Documentar segredos necessários e variáveis de ambiente
- [ ] Adicionar fluxos de trabalho de exemplo usando a nova engine

### Testes

- [ ] Executar `make test-unit` - todos os testes unitários passam
- [ ] Executar `make test` - todos os testes de integração passam
- [ ] Executar `make lint` - nenhum erro de linting
- [ ] Executar `make fmt` - código formatado corretamente
- [ ] Testar compilação de fluxo de trabalho com a nova engine
- [ ] Testar execução de fluxo de trabalho (manual ou CI)

### CI/CD

- [ ] Adicionar fluxo de trabalho de CI específico para a engine, se necessário
- [ ] Atualizar matriz de CI para incluir testes da nova engine
- [ ] Verificar se a imagem Docker inclui dependências da engine
- [ ] Testar em ambiente limpo (sem dependências em cache)

### Validação Final

- [ ] Executar `make agent-finish` - validação completa passa
- [ ] Criar PR com descrição abrangente
- [ ] Solicitar revisão dos mantenedores
- [ ] Abordar feedback da revisão
- [ ] Mesclar quando aprovado

---

## Melhores Práticas

### 1. Usar Auxiliares Compartilhados

Sempre prefira auxiliares existentes em vez de duplicar código:
- `GetBaseInstallationSteps()` para instalação padrão
- `BuildAWFCommand()` para integração com firewall
- `FormatStepWithCommandAndEnv()` para formatação de etapas
- `FilterEnvForSecrets()` para segurança

### 2. Seguir Convenções de Nomenclatura

- ID da Engine: minúsculo com hifens (ex: `my-engine`)
- Logger: `workflow:engine_name` (ex: `workflow:my_engine`)
- Arquivos: `engine_name_*.go` (ex: `my_engine.go`, `my_engine_logs.go`)
- Constantes: `DefaultMyEngineVersion`, `MyEngineLLMGatewayPort`

### 3. Segurança em Primeiro Lugar

- Sempre filtre variáveis de ambiente com `FilterEnvForSecrets()`
- Valide segredos antes da execução
- Use firewall AWF quando `isFirewallEnabled()` retornar true
- Nunca registre informações sensíveis

### 4. Manter Compatibilidade Retroativa

- Use composição de interface, não alterações incompatíveis
- Sobrescreva métodos de `BaseEngine`, não os substitua
- Suporte formatos de configuração legados
- Documente caminhos de migração

### 5. Testar Exaustivamente

- Testes unitários para funcionalidade central
- Testes de integração para compilação de fluxo de trabalho
- Testar com servidores MCP habilitados/desabilitados
- Testar com firewall habilitado/desabilitado
- Testar cenários de configuração personalizados

---

## Armadilhas Comuns

### 1. Esquecer de Registrar a Engine

Sempre adicione sua engine a `NewEngineRegistry()` em `agentic_engine.go`.

### 2. Não Lidar com Comandos Personalizados

Suporte comandos personalizados via `workflowData.EngineConfig.Command`:

```go
commandName := "my-engine"
if workflowData.EngineConfig != nil && workflowData.EngineConfig.Command != "" {
    commandName = workflowData.EngineConfig.Command
}
```

### 3. Configuração de PATH Incorreta

Use `GetNpmBinPathSetup()` para CLIs instaladas por npm dentro do AWF:

```go
npmPathSetup := GetNpmBinPathSetup()
engineCommandWithPath := fmt.Sprintf("%s && %s", npmPathSetup, engineCommand)
```

### 4. Filtragem de Segredos Faltando

Sempre filtre variáveis de ambiente:

```go
allowedSecrets := e.GetRequiredSecretNames(workflowData)
filteredEnv := FilterEnvForSecrets(env, allowedSecrets)
```

### 5. Hardcoding de Caminhos

Use constantes e configuração:

```go
// ❌ RUIM
logFile := "/tmp/my-log.txt"

// ✅ BOM
logFile := workflowData.LogFile // ou passado como parâmetro
```

---

## Resumo

Implementar uma engine agentic personalizada envolve:

1. **Entender a arquitetura**: Segregação de interface com responsabilidades focadas
2. **Aproveitar auxiliares existentes**: Não reinvente a roda
3. **Seguir padrões**: Aprenda com engines existentes (Copilot, Claude, Codex)
4. **Testar exaustivamente**: Testes unitários, testes de integração, validação manual
5. **Documentar completamente**: Ajude os usuários a entender e usar sua engine

A base de código gh-aw fornece excelente infraestrutura para desenvolvimento de engine. Use os auxiliares compartilhados, siga os padrões e foque nas capacidades únicas da sua engine.

Para perguntas ou esclarecimentos, consulte as implementações de engine existentes:
- **Copilot** (`copilot_engine*.go`): Bem modularizada, separação limpa
- **Claude** (`claude_engine.go`): Abrangente, rica em recursos
- **Codex** (`codex_engine.go`): Análise de log baseada em regex
- **Personalizada** (`custom_engine.go`): Implementação mínima e flexível

Boa codificação! 🚀
