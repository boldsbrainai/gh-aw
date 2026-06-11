---
name: error-pattern-safety
description: Aplique regras de segurança de correspondência de padrão de erro para engines agentic.
---


# Diretrizes de Segurança para Padrões de Erro

Use estas regras de segurança regex em engines agentic para evitar loops infinitos em JavaScript.

## O Problema

Com a flag global do JavaScript (`/pattern/g`), correspondências de largura zero podem causar loops infinitos porque:

1. O `regex.exec()` do JavaScript com a flag `g` usa `lastIndex` para rastrear a posição
2. Quando um padrão corresponde a uma largura zero, `lastIndex` não avança
3. A mesma posição é correspondida repetidamente, causando um loop infinito

## Exemplos de Padrões Perigosos

**❌ NUNCA USE ESTES PADRÕES:**

```javascript
// Apenas .* - corresponde a tudo, incluindo string vazia no final
/.*/g

// Caractere único com * - corresponde a zero ou mais (incluindo zero)
/a*/g

// Padrões que podem corresponder a uma string vazia
/(x|y)*/g
```

## Exemplos de Padrões Seguros

**✅ SEMPRE USE PADRÕES COMO ESTES:**

```javascript
// Prefixo obrigatório antes de .*
/error.*/gi
/error.*permission.*denied/gi

// Estrutura específica com conteúdo obrigatório
/\[(\d{4}-\d{2}-\d{2})\]\s+(ERROR):\s+(.+)/g

// Caracteres obrigatórios por toda parte
/access denied.*user.*not authorized/gi
```

## Regras de Segurança de Padrão

1. **Sempre exija pelo menos uma correspondência de caractere**
   - Use `.+` em vez de `.*` quando precisar de "algo"
   - Garanta que o padrão tenha prefixo/sufixo obrigatório

2. **Nunca use `.*` puro como o padrão inteiro**
   - Sempre combine com texto obrigatório: `error.*`
   - Nunca apenas `.*` ou `.*?`

3. **Teste padrões contra string vazia**

   ```javascript
   const regex = /seu-padrao/g;
   if (regex.test("")) {
     throw new Error("Padrão corresponde a string vazia - PERIGOSO!");
   }
   ```

4. **Use âncoras específicas quando possível**
   - Início: `^error.*`
   - Fim: `.*error$`
   - Limites de palavra: `\berror\b`

## Testes de Validação

Todos os padrões de erro devem passar nestes testes:

### Testes Go (pkg/workflow/engine_error_patterns_infinite_loop_test.go)

```go
// Teste que o padrão não corresponde a string vazia
func TestSegurancaPadrao(t *testing.T) {
    pattern := "seu-padrao"
    regex := regexp.MustCompile(pattern)
    
    if regex.MatchString("") {
        t.Error("Padrão corresponde a string vazia!")
    }
}
```

### Testes JavaScript (pkg/workflow/js/validate_errors.test.cjs)

```javascript
test("não deve corresponder a string vazia", () => {
  const regex = new RegExp("seu-padrao", "g");
  expect(regex.test("")).toBe(false);
});
```

## Mecanismos de Segurança em validate_errors.cjs

O script `validate_errors.cjs` possui proteções integradas:

1. **Detecção de largura zero**: Verifica se `regex.lastIndex` para de avançar
2. **Aviso de iteração**: Avisa em 1000 iterações
3. **Limite rígido**: Para em 10.000 iterações para evitar travamento

```javascript
// Verificação de segurança em validate_errors.cjs
if (regex.lastIndex === lastIndex) {
  core.error(`Loop infinito detectado! Padrão: ${pattern.pattern}`);
  break;
}
```

## Adicionando Novos Padrões de Erro

Ao adicionar novos padrões de erro a engines:

1. **Escreva o padrão com conteúdo obrigatório**
   ```go
   {
       Pattern:      `(?i)error.*permission.*denied`,
       LevelGroup:   0,
       MessageGroup: 0,
       Description:  "Erro de permissão negada",
   }
   ```

2. **Teste contra string vazia**
   - Execute: `make test-unit`
   - Verificações: `TestAllEnginePatternsSafe`

3. **Teste com amostras de log reais**
   - Garanta que corresponda a erros reais
   - Garanta que não corresponda a texto informativo

4. **Documente o padrão**
   - Adicione descrição clara
   - Observe o que foi projetado para capturar

## Conversão de Padrão: Go para JavaScript

Padrões são convertidos de Go para JavaScript:

```go
// Padrão Go (flag de ignorar maiúsculas/minúsculas)
Pattern: `(?i)error.*permission.*denied`

// Convertido para JavaScript
new RegExp("error.*permission.*denied", "gi")
```

O prefixo `(?i)` é removido porque o JavaScript usa a flag `i` em vez disso.

## Exemplos da Base de Código Atual

### ✅ Padrões Seguros

```go
// Requer prefixo "error"
Pattern: `(?i)error.*permission.*denied`

// Requer formato de timestamp específico
Pattern: `(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)\s+\[(ERROR)\]\s+(.+)`

// Requer prefixo "access denied"
Pattern: `(?i)access denied.*user.*not authorized`
```

### Como Corrigir Padrões Inseguros

Se você encontrar um padrão que corresponde a uma string vazia:

**Antes (inseguro):**
```go
Pattern: `.*error.*`  // Pode corresponder a vazio no início/fim
```

**Depois (seguro):**
```go
Pattern: `error.*`     // Requer "error" no início
// OU
Pattern: `.*error.+`   // Requer "error" e pelo menos um caractere depois
// OU
Pattern: `\berror\b.*` // Requer palavra "error"
```

## Lista de Verificação de Testes

Antes de commitar mudanças de padrão:

- [ ] Execute `make test-unit`
- [ ] Verifique se `TestAllEnginePatternsSafe` passa
- [ ] Verifique se `TestErrorPatternsNoInfiniteLoopPotential` passa
- [ ] Execute testes JavaScript: `cd pkg/workflow/js && npm test`
- [ ] Verifique se o padrão corresponde às mensagens de erro pretendidas
- [ ] Verifique se o padrão não corresponde a texto informativo

## Referências

- Sintaxe de regex Go: https://pkg.go.dev/regexp/syntax
- Regex JavaScript: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions
- Arquivos de teste:
  - `pkg/workflow/engine_error_patterns_infinite_loop_test.go`
  - `pkg/workflow/js/validate_errors.test.cjs`
  - `pkg/workflow/error_pattern_tuning_test.go`
---
