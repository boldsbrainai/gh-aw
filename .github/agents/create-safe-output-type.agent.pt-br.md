---
description: Adicionando um Novo Tipo de Saída Segura aos GitHub Agentic Workflows
disable-model-invocation: true
---

# Adicionar Novo Tipo de Saída Segura

Este guia cobre a adição de um novo tipo de saída segura para processar saídas de agentes de IA no formato JSONL através de um pipeline de validação (tipos TypeScript → esquema JSON → coleção JavaScript).

## Passos de Implementação

### 1. Atualizar Esquema JSON (`schemas/agent-output.json`)

Adicione a definição do objeto na seção `$defs`:
   ```json
   "YourNewTypeOutput": {
     "title": "Saída de Novo Tipo",
     "description": "Saída para sua nova funcionalidade",
     "type": "object",
     "properties": {
       "type": {
         "const": "your-new-type"
       },
       "required_field": {
         "type": "string",
         "description": "Descrição do campo obrigatório",
         "minLength": 1
       },
       "optional_field": {
         "type": "string", 
         "description": "Descrição do campo opcional"
       }
     },
     "required": ["type", "required_field"],
     "additionalProperties": false
   }
   ```

Adicione ao array `oneOf` de `SafeOutput`: `{"$ref": "#/$defs/YourNewTypeOutput"}`

**Notas de Validação**: Use `const` para o campo type, `minLength: 1` para strings obrigatórias, `additionalProperties: false`, `oneOf` para tipos de união.

### 2. Atualizar Tipos TypeScript

**Arquivo**: `pkg/workflow/js/types/safe-outputs.d.ts`
   ```typescript
   /**
    * Item JSONL para [descrição]
    */
   interface YourNewTypeItem extends BaseSafeOutputItem {
     type: "your-new-type";
     /** Descrição do campo obrigatório */
     required_field: string;
     /** Descrição do campo opcional */
     optional_field?: string;
   }
   ```

Adicione ao tipo de união `SafeOutputItem` e à lista de exportação.

**Arquivo**: `pkg/workflow/js/types/safe-outputs-config.d.ts` - Adicione a interface de configuração, adicione à união `SpecificSafeOutputConfig`, exporte.

### 3. Atualizar JSON de Ferramentas de Saídas Seguras (`pkg/workflow/js/safe_outputs_tools.json`)

Adicione a assinatura da ferramenta para expor aos agentes de IA:

```json
{
  "name": "your_new_type",
  "description": "Breve descrição do que esta ferramenta faz (use underscores no nome, não hifens)",
  "inputSchema": {
    "type": "object",
    "required": ["required_field"],
    "properties": {
      "required_field": {
        "type": "string",
        "description": "Descrição do campo obrigatório"
      },
      "optional_field": {
        "type": "string",
        "description": "Descrição do campo opcional"
      },
      "numeric_field": {
        "type": ["number", "string"],
        "description": "Campo numérico que aceita tipos number e string"
      }
    },
    "additionalProperties": false
  }
}
```

**Diretrizes**: Use underscores no `name` da ferramenta, corresponda com o campo type, defina `additionalProperties: false`, use `"type": ["number", "string"]` para campos numéricos.

**Importante**: O arquivo é incorporado via `//go:embed` - **deve reconstruir** com `make build` após alterações.

### 4. Atualizar Servidor MCP JavaScript (Se um manipulador personalizado for necessário) (`pkg/workflow/js/safe_outputs_mcp_server.cjs`)

A maioria dos tipos usa o manipulador JSONL padrão. Adicione um manipulador personalizado apenas se necessário para operações de arquivo, comandos git ou validação complexa:

```javascript
/**
 * Manipulador para saída segura your_new_type
 * @param {Object} args - Argumentos passados para a ferramenta
 * @returns {Object} Resposta da ferramenta MCP
 */
const yourNewTypeHandler = args => {
  // Execute qualquer validação personalizada
  if (!args.required_field || typeof args.required_field !== "string") {
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            error: "required_field é obrigatório e deve ser uma string",
          }),
        },
      ],
      isError: true,
    };
  }

  // Execute operações personalizadas (ex: operações de sistema de arquivo, comandos git)
  try {
    // Sua lógica personalizada aqui
    const result = performCustomOperation(args);
    
    // Escreva a entrada JSONL
    const entry = {
      type: "your_new_type",
      required_field: args.required_field,
      optional_field: args.optional_field,
      // Adicione quaisquer campos adicionais do processamento personalizado
      result_data: result,
    };
    
    appendSafeOutput(entry);
    
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            success: true,
            message: "Seu novo tipo foi processado com sucesso",
            result: result,
          }),
        },
      ],
    };
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            error: error instanceof Error ? error.message : String(error),
          }),
        },
      ],
      isError: true,
    };
  }
};
```

2. **Anexe o manipulador à ferramenta** (por volta da linha 570-580):

```javascript
// Anexe manipuladores às ferramentas que precisam deles
ALL_TOOLS.forEach(tool => {
  if (tool.name === "create_pull_request") {
    tool.handler = createPullRequestHandler;
  } else if (tool.name === "push_to_pull_request_branch") {
    tool.handler = pushToPullRequestBranchHandler;
  } else if (tool.name === "upload_asset") {
    tool.handler = uploadAssetHandler;
  } else if (tool.name === "your_new_type") {
    tool.handler = yourNewTypeHandler;  // Adicione seu manipulador aqui
  }
});
```

**Manipulador padrão**: Normaliza o campo type, lida com conteúdo grande (>16000 tokens), escreve JSONL, retorna sucesso.

### 5. Atualizar JavaScript de Coleta (`pkg/workflow/js/collect_ndjson_output.ts`)

Adicione validação no switch statement principal (~linha 700):

```typescript
case "your-new-type":
  // Valide campos obrigatórios
  if (!item.required_field || typeof item.required_field !== "string") {
    errors.push(`Linha ${i + 1}: your-new-type requer um campo de string 'required_field'`);
    continue;
  }
  
  // Sanitizar conteúdo de texto
  item.required_field = sanitizeContent(item.required_field);
  
  // Validar campos opcionais
  if (item.optional_field !== undefined) {
    if (typeof item.optional_field !== "string") {
      errors.push(`Linha ${i + 1}: o 'optional_field' do your-new-type deve ser uma string`);
      continue;
    }
    item.optional_field = sanitizeContent(item.optional_field);
  }
  break;
```

**Padrões**: Verifique campos obrigatórios primeiro, use `sanitizeContent()` para strings, use auxiliares de validação para números, continue o loop em erros.

### 6. Atualizar Função de Filtro Go (`pkg/workflow/safe_outputs.go`)

Adicione ao mapa `enabledTools` em `generateFilteredToolsJSON` (~linha 1120):

```go
// generateFilteredToolsJSON filtra o array ALL_TOOLS com base em saídas seguras habilitadas
// Retorna uma string JSON contendo apenas as ferramentas que estão habilitadas no fluxo de trabalho
func generateFilteredToolsJSON(data *WorkflowData) (string, error) {
	if data.SafeOutputs == nil {
		return "[]", nil
	}

	safeOutputsLog.Print("Gerando JSON de ferramentas filtradas para fluxo de trabalho")

	// Carrega o JSON completo de ferramentas
	allToolsJSON := GetSafeOutputsToolsJSON()

	// Analisa o JSON para obter todas as ferramentas
	var allTools []map[string]any
	if err := json.Unmarshal([]byte(allToolsJSON), &allTools); err != nil {
		return "", fmt.Errorf("falha ao analisar JSON de ferramentas de saídas seguras: %w", err)
	}

	// Cria um conjunto de nomes de ferramentas habilitadas
	enabledTools := make(map[string]bool)

	// Verifica quais saídas seguras estão habilitadas e adiciona seus nomes de ferramenta correspondentes
	if data.SafeOutputs.CreateIssues != nil {
		enabledTools["create_issue"] = true
	}
	// ... verificações existentes ...
	if data.SafeOutputs.YourNewType != nil {
		enabledTools["your_new_type"] = true  // Adicione seu novo tipo aqui
	}

	// Filtra ferramentas para incluir apenas as habilitadas
	var filteredTools []map[string]any
	for _, tool := range allTools {
		toolName, ok := tool["name"].(string)
		if !ok {
			continue
		}
		if enabledTools[toolName] {
			filteredTools = append(filteredTools, tool)
		}
	}

	// Serializa ferramentas filtradas para JSON
	filteredJSON, err := json.Marshal(filteredTools)
	if err != nil {
		return "", fmt.Errorf("falha ao realizar o marshal das ferramentas filtradas: %w", err)
	}

	return string(filteredJSON), nil
}
```

**Fluxo**: Configuração de fluxo de trabalho → analisa para struct → filtra ferramentas → escreve JSON → servidor MCP expõe para agentes.

### 7. Criar Implementação do Manipulador (`actions/setup/js/your_new_type.cjs`)

Crie uma fábrica de manipulador que retorna uma função de processamento de mensagem. O gerenciador de manipuladores chamará esta fábrica uma vez durante a inicialização e usará a função retornada para processar cada mensagem.

```javascript
// @ts-check
/// <reference types="@actions/github-script" />

const { getErrorMessage } = require("./error_helpers.cjs");
const { generateTemporaryId } = require("./temporary_id.cjs");

/**
 * @typedef {import('./types/handler-factory').HandlerFactoryFunction} HandlerFactoryFunction
 */

/** @type {string} Tipo de saída segura manipulado por este módulo */
const HANDLER_TYPE = "your_new_type";

/**
 * Fábrica principal do manipulador para your_new_type
 * Retorna uma função de manipulador de mensagem que processa mensagens individuais de your_new_type
 * @type {HandlerFactoryFunction}
 */
async function main(config = {}) {
  // Extraia e registre a configuração
  const customOption = config.custom_option || "";
  const maxCount = config.max || 10;
  const isStaged = process.env.GH_AW_SAFE_OUTPUTS_STAGED === "true";

  core.info(`Opção personalizada: ${customOption}`);
  core.info(`Contagem máxima: ${maxCount}`);
  core.info(`Modo staged: ${isStaged}`);

  // Rastreie o estado do manipulador
  let processedCount = 0;
  const processedItems = [];

  /**
   * Função manipuladora de mensagem que processa uma única mensagem de your_new_type
   * @param {Object} message - A mensagem de your_new_type a ser processada
   * @param {Object} resolvedTemporaryIds - Mapa de IDs temporários para {repo, número}
   * @returns {Promise<Object>} Resultado com status de sucesso/erro
   */
  return async function handleYourNewType(message, resolvedTemporaryIds) {
    // Verifique a contagem máxima
    if (processedCount >= maxCount) {
      core.warning(`Pulando your_new_type: contagem máxima de ${maxCount} atingida`);
      return {
        success: false,
        error: `Contagem máxima de ${maxCount} atingida`,
      };
    }

    processedCount++;

    const item = message;

    // Validar campos obrigatórios
    if (!item.required_field) {
      core.warning("Pulando your_new_type: required_field está ausente");
      return {
        success: false,
        error: "required_field é obrigatório",
      };
    }

    // Gere ID temporário se não fornecido
    const temporaryId = item.temporary_id || generateTemporaryId();
    core.info(`Processando your_new_type: required_field=${item.required_field}, temporaryId=${temporaryId}`);

    // Modo staged: coletar para visualização
    if (isStaged) {
      processedItems.push({
        required_field: item.required_field,
        optional_field: item.optional_field,
        temporaryId,
      });

      return {
        success: true,
        staged: true,
        temporaryId,
      };
    }

    // Processar a mensagem
    try {
      // Implemente sua chamada de API do GitHub ou lógica personalizada aqui
      core.info(`Processando your-new-type: ${item.required_field}`);
      
      // Exemplo de padrão de API do GitHub:
      // const result = await github.rest.yourApi.yourMethod({
      //   owner: context.repo.owner,
      //   repo: context.repo.repo,
      //   your_field: item.required_field,
      // });
      
      // Simular processamento bem-sucedido
      const resultId = 123; // Substitua pelo ID do resultado real
      const resultUrl = `https://github.com/example/result/${resultId}`;

      core.info(`✓ Processado com sucesso your-new-type: ${resultUrl}`);

      return {
        success: true,
        temporaryId,
        resultId,
        resultUrl,
      };
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      core.error(`✗ Falha ao processar your-new-type: ${errorMessage}`);
      return {
        success: false,
        error: errorMessage,
      };
    }
  };
}

module.exports = { main };
```

**Padrões de Fábrica de Manipulador**:

1. **Função de Fábrica**: `main(config)` é chamada uma vez durante a inicialização
2. **Estado de Fechamento**: Variáveis no escopo da fábrica persistem entre mensagens (ex: `processedCount`)
3. **Manipulador de Mensagem**: A fábrica retorna uma função assíncrona que processa mensagens individuais
4. **Assinatura do Manipulador**: `async (message, resolvedTemporaryIds) => { success, error?, ... }`
5. **Aplicação de Contagem Máxima**: Verifique `processedCount` antes de processar cada mensagem
6. **Modo Staged**: Colete itens para visualização em vez de executar operações
7. **IDs Temporários**: Gere ou use IDs temporários fornecidos para referência cruzada
8. **Tratamento de Erros**: Retorne `{ success: false, error }` em vez de lançar
9. **Objeto de Resultado**: Inclua campos necessários para saídas ou resolução de ID temporário

**Módulos Auxiliares Disponíveis**:
- `error_helpers.cjs` - `getErrorMessage(error)` para formatação consistente de erros
- `temporary_id.cjs` - `generateTemporaryId()`, `isTemporaryId()`, `normalizeTemporaryId()`
- `repo_helpers.cjs` - `parseRepoSlug()`, `validateRepo()`, `getDefaultTargetRepo()`
- `sanitize_label_content.cjs` - `sanitizeLabelContent()` para validação de label
- `generate_footer.cjs` - `generateFooter()` para rodapé de mensagem gerado por IA

### 8. Criar Testes

**Arquivo**: `pkg/workflow/js/your_new_type.test.cjs` - Teste entrada vazia, processamento válido, modo staged, erros. Use vitest.

**Arquivo**: `pkg/workflow/js/collect_ndjson_output.test.cjs` - Teste validação com campos válidos/inválidos.

### 9. Criar Fluxos de Trabalho de Teste

Crie para cada engine (claude/codex/copilot) em `pkg/cli/workflows/`:

**Exemplo**: `test-claude-your-new-type.md`

```markdown
---
on: workflow_dispatch
permissions:
  contents: read
  actions: read
engine: claude
safe-outputs:
  your-new-type:
    max: 3
    custom-option: "test"
timeout-minutes: 5
---

# Testar Seu Novo Tipo

Teste a funcionalidade do novo tipo de saída segura.

Crie uma saída your-new-type com:
- required_field: "Olá Mundo"  
- optional_field: "Isto é opcional"

Saída no formato JSONL.
```

### 10. Integrar com o Gerenciador de Manipuladores

A maioria dos tipos de saída segura agora é processada através da arquitetura do **gerenciador de manipuladores**, que fornece despacho centralizado de mensagens, resolução de ID temporário e tratamento de erros consistente. O gerenciador de manipuladores carrega manipuladores de mensagem individuais para cada tipo de saída segura habilitado e orquestra sua execução.

#### Visão Geral da Arquitetura

O gerenciador de manipuladores (`actions/setup/js/safe_output_handler_manager.cjs`) atua como um despachante:
1. Carrega a configuração da variável de ambiente `GH_AW_SAFE_OUTPUTS_HANDLER_CONFIG`
2. Inicializa fábricas de manipuladores para tipos de saída segura habilitados
3. Lê e valida mensagens de saída do agente
4. Despacha mensagens para manipuladores apropriados
5. Gerencia a resolução de ID temporário entre manipuladores
6. Coleta resultados e saídas

#### Padrão de Fábrica de Manipulador

Cada tipo de saída segura implementa uma **função de fábrica** que retorna um manipulador de mensagem:

```javascript
/**
 * Fábrica principal do manipulador para your_new_type
 * Retorna uma função de manipulador de mensagem que processa mensagens individuais de your_new_type
 * @param {Object} config - Objeto de configuração do YAML do fluxo de trabalho
 * @returns {Promise<Function>} Função de manipulador de mensagem
 */
async function main(config = {}) {
  // 1. Extrair e registrar configuração
  const customOption = config.custom_option || "";
  const maxCount = config.max || 10;
  
  core.info(`Opção personalizada: ${customOption}`);
  core.info(`Contagem máxima: ${maxCount}`);
  
  // 2. Inicializar estado do manipulador (se necessário)
  let processedCount = 0;
  const temporaryIdMap = new Map();
  
  // 3. Retornar a função de manipulador de mensagem
  return async function handleYourNewType(message, resolvedTemporaryIds) {
    // Verifique a contagem máxima
    if (processedCount >= maxCount) {
      core.warning(`Pulando your_new_type: contagem máxima de ${maxCount} atingida`);
      return {
        success: false,
        error: `Contagem máxima de ${maxCount} atingida`,
      };
    }
    
    processedCount++;
    
    // Processar a mensagem
    try {
      // Sua implementação aqui
      const result = await processYourNewType(message);
      
      // Retornar sucesso com quaisquer saídas
      return {
        success: true,
        // Adicione quaisquer saídas necessárias para resolução de ID temporário ou saídas de passo
        temporaryId: message.temporary_id,
        // ... outros campos
      };
    } catch (error) {
      core.error(`Falha ao processar your_new_type: ${error.message}`);
      return {
        success: false,
        error: error.message,
      };
    }
  };
}

module.exports = { main };
```

#### Passos de Integração

**Passo 1: Adicionar Tipo de Configuração** em `pkg/workflow/frontmatter_types.go` ou criar um novo arquivo (ex: `pkg/workflow/your_new_type.go`):

```go
// YourNewTypeConfig contém a configuração para seu novo tipo a partir da saída do agente
type YourNewTypeConfig struct {
	BaseSafeOutputConfig `yaml:",inline"`
	CustomOption         string `yaml:"custom-option,omitempty"`
}
```

**Passo 2: Adicionar Analisador de Configuração** (no mesmo arquivo do tipo de configuração):

```go
// parseYourNewTypeConfig lida com a configuração your-new-type
func (c *Compiler) parseYourNewTypeConfig(outputMap map[string]any) *YourNewTypeConfig {
	if configData, exists := outputMap["your-new-type"]; exists {
		yourNewTypeConfig := &YourNewTypeConfig{}
		yourNewTypeConfig.Max = 1 // Máximo padrão é 1

		if configMap, ok := configData.(map[string]any); ok {
			// Analisar campos base comuns
			c.parseBaseSafeOutputConfig(configMap, &yourNewTypeConfig.BaseSafeOutputConfig)

			// Analisar campos personalizados
			yourNewTypeConfig.CustomOption = ParseStringFromConfig(configMap, "custom-option")
		}

		return yourNewTypeConfig
	}

	return nil
}
```

**Passo 3: Registrar no Gerenciador de Manipuladores** em `actions/setup/js/safe_output_handler_manager.cjs`:

Adicione seu manipulador ao `HANDLER_MAP`:

```javascript
const HANDLER_MAP = {
  create_issue: "./create_issue.cjs",
  add_comment: "./add_comment.cjs",
  // ... manipuladores existentes ...
  your_new_type: "./your_new_type.cjs",  // Adicione seu manipulador aqui
};
```

**Passo 4: Adicionar Configuração do Manipulador ao Compilador** em `pkg/workflow/compiler_safe_outputs_config.go`:

Atualize `addHandlerManagerConfigEnvVar()` para incluir sua configuração:

```go
if data.SafeOutputs.YourNewType != nil {
	handlerConfig := map[string]any{
		"custom_option": data.SafeOutputs.YourNewType.CustomOption,
		"max":           data.SafeOutputs.YourNewType.Max,
	}
	config["your_new_type"] = handlerConfig
}
```

**Passo 5: Adicionar à Verificação do Job Consolidado** em `pkg/workflow/compiler_safe_outputs_job.go`:

Atualize a condição `hasHandlerManagerTypes`:

```go
hasHandlerManagerTypes := data.SafeOutputs.CreateIssues != nil ||
	data.SafeOutputs.AddComments != nil ||
	// ... verificações existentes ...
	data.SafeOutputs.YourNewType != nil
```

Adicione permissões:

```go
if data.SafeOutputs.YourNewType != nil {
	permissions.Merge(NewPermissionsContentsReadYourPermissions())
}
```

#### Alternativa de Passo Autônomo

Se o seu tipo de saída segura exigir operações **antes ou depois** do processamento da mensagem (ex: checkout git, operações de arquivo), use um passo autônomo em vez disso:

```go
// Em pkg/workflow/compiler_safe_outputs_specialized.go ou um novo arquivo
func (c *Compiler) buildYourNewTypeStepConfig(data *WorkflowData, mainJobName string, threatDetectionEnabled bool) SafeOutputStepConfig {
	cfg := data.SafeOutputs.YourNewType

	var customEnvVars []string
	customEnvVars = append(customEnvVars, c.buildStepLevelSafeOutputEnvVars(data, "")...)

	condition := BuildSafeOutputType("your_new_type")

	return SafeOutputStepConfig{
		StepName:      "Executar Seu Novo Tipo",
		StepID:        "your_new_type",
		ScriptName:    "your_new_type",
		Script:        getYourNewTypeScript(),
		CustomEnvVars: customEnvVars,
		Condition:     condition,
		Token:         cfg.GitHubToken,
	}
}
```

Então integre em `buildConsolidatedSafeOutputsJob()`:

```go
if data.SafeOutputs.YourNewType != nil {
	stepConfig := c.buildYourNewTypeStepConfig(data, mainJobName, threatDetectionEnabled)
	stepYAML := c.buildConsolidatedSafeOutputStep(data, stepConfig)
	steps = append(steps, stepYAML...)
	safeOutputStepNames = append(safeOutputStepNames, stepConfig.StepID)

	outputs["your_new_type_result"] = "${{ steps.your_new_type.outputs.result }}"
	permissions.Merge(NewPermissionsContentsReadYourPermissions())
}
```

Adicione a `STANDALONE_STEP_TYPES` no gerenciador de manipuladores:

```javascript
const STANDALONE_STEP_TYPES = new Set([
  "assign_to_agent",
  "create_agent_task", 
  "update_project",
  "upload_asset",
  "your_new_type",  // Adicione se usar passo autônomo
]);
```

#### Pontos de Integração Chave

1. **Tipo de Configuração**: Defina em `pkg/workflow/*.go` com embutimento de `BaseSafeOutputConfig`
2. **Analisador de Configuração**: Analise a configuração YAML e extraia campos tipados
3. **Registro do Manipulador**: Adicione ao `HANDLER_MAP` no gerenciador de manipuladores
4. **Configuração do Manipulador**: Adicione a `addHandlerManagerConfigEnvVar()` para configuração em tempo de execução
5. **Integração de Job**: Adicione à verificação `hasHandlerManagerTypes` e permissões
6. **Implementação do Manipulador**: Crie função de fábrica em `actions/setup/js/your_new_type.cjs`

#### Auxiliares Compartilhados

**Tipos de Configuração**:
- `BaseSafeOutputConfig` - Campos comuns (max, github-token, staged)
- `SafeOutputTargetConfig` - Configuração do repositório alvo

**Analisadores**:
- `ParseStringFromConfig()` - Analisar campo de string
- `ParseTargetConfig()` - Analisar target/target-repo
- `parseBaseSafeOutputConfig()` - Analisar campos base

**Auxiliares do Manipulador** (em `actions/setup/js/`):
- `load_agent_output.cjs` - Carregar e analisar saída do agente
- `temporary_id.cjs` - Geração e resolução de ID temporário
- `repo_helpers.cjs` - Análise e validação de repositório
- `error_helpers.cjs` - Formatação de mensagem de erro
- `sanitize_label_content.cjs` - Sanitização de label
- `generate_footer.cjs` - Rodapé de mensagem gerado por IA

### 11. Compilar e Testar

```bash
make js fmt-cjs lint-cjs test-unit recompile agent-finish
```

### 12. Validação Manual

Teste o fluxo de trabalho com modos staged/não staged, tratamento de erros, validação de esquema JSON, todas as engines.

## Critérios de Sucesso

- [ ] Esquema JSON valida corretamente
- [ ] Tipos TypeScript compilam
- [ ] JSON de ferramentas inclui assinatura da ferramenta  
- [ ] Servidor MCP manipula tipo (manipulador personalizado, se necessário)
- [ ] Filtro Go inclui tipo em `generateFilteredToolsJSON`
- [ ] Coleta valida campos
- [ ] Fábrica de manipulador implementada (retorna manipulador de mensagem)
- [ ] Manipulador registrado no HANDLER_MAP ou STANDALONE_STEP_TYPES
- [ ] Configuração do manipulador adicionada a `addHandlerManagerConfigEnvVar()`
- [ ] Permissões adicionadas ao job consolidado
- [ ] Testes passam com boa cobertura
- [ ] Fluxos de trabalho compilam
- [ ] Validação manual confirma funcionalidade

## Armadilhas Comuns

1. Nomenclatura inconsistente entre arquivos (kebab-case/camelCase/underscores)
2. Atualização de tools.json faltando (agentes não podem chamar sem isso)
3. Atualização de filtro Go faltando (MCP não exporá a ferramenta)
4. Validação/sanitização de campo faltando
5. Não adicionar a tipos de união
6. Não exportar interfaces
7. Lacunas na cobertura de testes
8. Violações de sintaxe de esquema
9. Tratamento de erro da API do GitHub
10. Implementação do modo staged faltando
11. Esquecer `make build` após modificar arquivos embutidos
12. Fábrica de manipulador não retornando uma função (deve retornar manipulador de mensagem assíncrono)
13. Esquecer de adicionar manipulador ao HANDLER_MAP em safe_output_handler_manager.cjs
14. Não adicionar configuração de manipulador a addHandlerManagerConfigEnvVar() no compilador
15. Verificação hasHandlerManagerTypes faltando para integração de job consolidado

## Referências

- JSON Schema: https://json-schema.org/draft-07/schema
- GitHub Actions Core: https://github.com/actions/toolkit/tree/main/packages/core  
- GitHub REST API: https://docs.github.com/en/rest
- Vitest: https://vitest.dev/
- Gerenciador de Manipuladores: `actions/setup/js/safe_output_handler_manager.cjs`
- Implementações de Manipulador Existentes: `actions/setup/js/create_issue.cjs`, `actions/setup/js/add_comment.cjs`, etc.
- Integração do Compilador: `pkg/workflow/compiler_safe_outputs_*.go`
