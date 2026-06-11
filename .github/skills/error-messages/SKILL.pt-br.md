---
name: error-messages
description: Escreva mensagens de erro de validação consistentes e acionáveis em gh-aw.
---


# Guia de Estilo de Mensagens de Erro

Use este formato para erros de validação do gh-aw. Mantenha as mensagens claras, acionáveis e orientadas por exemplos.

## Modelo de Mensagem de Erro

```
[o que está errado]. [o que é esperado]. [exemplo de uso correto]
```

Faça com que cada mensagem de erro responda a três perguntas:
1. **O que está errado?** - Declare claramente o erro de validação
2. **O que é esperado?** - Explique o formato ou valores válidos
3. **Como corrigir?** - Forneça um exemplo concreto de uso correto

## Bons Exemplos

Estes exemplos seguem o modelo e fornecem orientação acionável:

### Validação de Delta de Tempo (de time_delta.go)
```go
return nil, fmt.Errorf("formato de delta de tempo inválido: +%s. Formato esperado como +25h, +3d, +1w, +1mo, +1d12h30m", deltaStr)
```
✅ **Por que é bom:**
- Identifica claramente a entrada inválida
- Lista múltiplos exemplos de formato válido
- Mostra formatos combinados (+1d12h30m)

### Validação de Tipo com Exemplo
```go
return "", fmt.Errorf("o valor de manual-approval deve ser uma string, recebido %T. Exemplo: manual-approval: \"production\"", val)
```
✅ **Por que é bom:**
- Mostra o tipo real recebido (%T)
- Fornece exemplo YAML concreto
- Usa sintaxe YAML adequada com aspas

### Validação de Enum com Opções
```go
return fmt.Errorf("engine inválida: %s. Engines válidas são: copilot, claude, codex, custom. Exemplo: engine: copilot", engineID)
```
✅ **Por que é bom:**
- Lista todas as opções válidas
- Fornece exemplo mais simples
- Usa formatação consistente

### Configuração MCP
```go
return fmt.Errorf("a configuração MCP da ferramenta '%s' deve especificar 'command' ou 'container'. Exemplo:\ntools:\n  %s:\n    command: \"npx @my/tool\"", toolName, toolName)
```
✅ **Por que é bom:**
- Explica a exclusividade mútua
- Mostra nome de ferramenta realista
- Formata exemplo YAML de múltiplas linhas

## Maus Exemplos

Estes exemplos carecem de clareza ou orientação acionável:

### Vago Demais
```go
return fmt.Errorf("formato inválido")
```
❌ **Problemas:**
- Não especifica qual formato é inválido
- Não explica o formato esperado
- Nenhum exemplo fornecido

### Exemplo Faltante
```go
return fmt.Errorf("o valor de manual-approval deve ser uma string")
```
❌ **Problemas:**
- Declara requisito, mas sem exemplo
- Usuário não sabe a sintaxe YAML adequada
- Poderia ser mais claro sobre o tipo recebido

### Informação Incompleta
```go
return fmt.Errorf("engine inválida: %s", engineID)
```
❌ **Problemas:**
- Não lista opções válidas
- Nenhuma orientação para corrigir o erro
- Usuário deve procurar na documentação

## Quando Incluir Exemplos

Sempre inclua exemplos para:

1. **Erros de Formato/Sintaxe** - Mostre a sintaxe correta
   ```go
   fmt.Errorf("formato de data inválido. Esperado: YYYY-MM-DD HH:MM:SS. Exemplo: 2024-01-15 14:30:00")
   ```

2. **Campos Enum/Escolha** - Liste todas as opções válidas
   ```go
   fmt.Errorf("nível de permissão inválido: %s. Níveis válidos: read, write, none. Exemplo: permissions:\n  contents: read", level)
   ```

3. **Incompatibilidades de Tipo** - Mostre o tipo esperado e exemplo
   ```go
   fmt.Errorf("timeout-minutes deve ser um inteiro, recebido %T. Exemplo: timeout-minutes: 10", value)
   ```

4. **Configurações Complexas** - Forneça exemplo válido completo
   ```go
   fmt.Errorf("configuração de servidor MCP inválida. Exemplo:\nmcp-servers:\n  my-server:\n    command: \"node\"\n    args: [\"server.js\"]")
   ```

## Quando Exemplos Podem Ser Opcionais

Exemplos podem ser omitidos quando:

1. **Erro advindo de erro encapsulado (wrapped)** - Ao encapsular outro erro com contexto
   ```go
   return fmt.Errorf("falha ao analisar configuração: %w", err)
   ```

2. **Erro é autoexplicativo com contexto claro**
   ```go
   return fmt.Errorf("unidade duplicada '%s' no delta de tempo: +%s", unit, deltaStr)
   ```

3. **Erro aponta para documentação específica**
   ```go
   return fmt.Errorf("funcionalidade não suportada. Veja https://docs.example.com/features")
   ```

## Diretrizes de Formatação

### Use Verbos de Tipo para Conteúdo Dinâmico
- `%s` - strings
- `%d` - inteiros
- `%T` - tipo de valor
- `%v` - valor geral
- `%w` - erros encapsulados (wrapped)

### Exemplos de Múltiplas Linhas
Para exemplos de configuração YAML abrangendo múltiplas linhas:
```go
fmt.Errorf("configuração inválida. Exemplo:\ntools:\n  github:\n    mode: \"remote\"")
```

### Aspas em Exemplos
Use sintaxe YAML adequada em exemplos:
```go
// Bom - mostra aspas quando necessário
fmt.Errorf("Exemplo: name: \"my-workflow\"")

// Bom - mostra sem aspas para valores simples
fmt.Errorf("Exemplo: timeout-minutes: 10")
```

### Terminologia Consistente
Use os mesmos nomes de campo que no YAML:
```go
// Bom - corresponde ao nome de campo YAML
fmt.Errorf("timeout-minutes deve ser positivo")

// Ruim - usa nome diferente
fmt.Errorf("timeout deve ser positivo")
```

## Testando Mensagens de Erro

Todas as mensagens de erro melhoradas devem ter testes correspondentes:

```go
func TestQualidadeMensagemErro(t *testing.T) {
    err := validateSomething(invalidInput)
    require.Error(t, err)
    
    // Erro deve explicar o que está errado
    assert.Contains(t, err.Error(), "inválido")
    
    // Erro deve incluir formato ou valores esperados
    assert.Contains(t, err.Error(), "Esperado")
    
    // Erro deve incluir exemplo
    assert.Contains(t, err.Error(), "Exemplo:")
}
```

## Estratégia de Migração

Ao melhorar mensagens de erro existentes:

1. **Identifique o erro** - Encontre erro de validação que carece de clareza
2. **Analise o contexto** - Entenda o que está sendo validado
3. **Aplique o modelo** - Adicione o que está errado + esperado + exemplo
4. **Adicione testes** - Verifique o conteúdo da mensagem de erro
5. **Atualize comentários** - Documente a lógica de validação

## Exemplos por Categoria

### Validação de Formato
```go
// Deltas de tempo
fmt.Errorf("formato de delta de tempo inválido: +%s. Formato esperado como +25h, +3d, +1w, +1mo, +1d12h30m", input)

// Datas
fmt.Errorf("formato de data inválido: %s. Esperado: YYYY-MM-DD ou relativo como -1w. Exemplo: 2024-01-15 ou -7d", input)

// URLs
fmt.Errorf("formato de URL inválido: %s. Esperado: URL https://. Exemplo: https://api.example.com", input)
```

### Validação de Tipo
```go
// Booleano esperado
fmt.Errorf("read-only deve ser um booleano, recebido %T. Exemplo: read-only: true", value)

// String esperada
fmt.Errorf("nome do fluxo de trabalho deve ser uma string, recebido %T. Exemplo: name: \"my-workflow\"", value)

// Objeto esperado
fmt.Errorf("permissões devem ser um objeto, recebido %T. Exemplo: permissions:\n  contents: read", value)
```

### Validação de Escolha/Enum
```go
// Seleção de Engine
fmt.Errorf("engine inválida: %s. Engines válidas: copilot, claude, codex, custom. Exemplo: engine: copilot", id)

// Níveis de permissão
fmt.Errorf("nível de permissão inválido: %s. Níveis válidos: read, write, none. Exemplo: contents: read", level)

// Modos de ferramenta
fmt.Errorf("modo inválido: %s. Modos válidos: local, remote. Exemplo: mode: \"remote\"", mode)
```

### Validação de Configuração
```go
// Campo obrigatório ausente
fmt.Errorf("ferramenta '%s' faltando campo obrigatório 'command'. Exemplo:\ntools:\n  %s:\n    command: \"node server.js\"", name, name)

// Campos mutuamente exclusivos
fmt.Errorf("não é possível especificar 'command' e 'container' ao mesmo tempo. Escolha um. Exemplo: command: \"node server.js\"")

// Combinação inválida
fmt.Errorf("servidores MCP HTTP não podem usar o campo 'container'. Exemplo:\ntools:\n  my-http:\n    type: http\n    url: \"https://api.example.com\"")
```

## Referências

- **Excelente exemplo para seguir**: `pkg/workflow/time_delta.go`
- **Inspiração de padrão**: Mensagens de erro da biblioteca padrão do Go
- **Exemplos de teste**: `pkg/workflow/*_test.go`

## Ferramentas

Ao escrever mensagens de erro, considere:
- A perspectiva do usuário (o que eles precisam para corrigir?)
- O contexto (onde no fluxo de trabalho está o erro?)
- A documentação (devemos referenciar documentos específicos?)
- A complexidade (é necessário exemplo de múltiplas linhas?)
---
