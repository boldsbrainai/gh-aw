---
name: console-rendering
description: Use tags de estrutura Go para renderizar saída de terminal estilizada no gh-aw.
---

# Uso do Sistema de Renderização de Console

Use este guia para o sistema de renderização de console baseado em tags de estrutura.

## Suporte a Tags de Estrutura

Use a tag de estrutura `console` para controlar o comportamento de renderização:

- **`header:"Nome"`** - Define o nome de exibição para campos (usado em estruturas e tabelas)
- **`title:"Título da Seção"`** - Define o título para estruturas aninhadas, fatias (slices) ou mapas
- **`format:"tipo"`** - Define o tipo de formatação para o valor do campo
  - `format:number` - Formata inteiros como números legíveis por humanos (ex: "1k", "1.2M")
  - `format:cost` - Formata floats como moeda com prefixo $ (ex: "$1.234")
- **`omitempty`** - Pula o campo se ele tiver um valor zero
- **`"-"`** - Sempre pula o campo

## Exemplo de Uso

```go
type Overview struct {
    RunID    int64  `console:"header:Run ID"`
    Workflow string `console:"header:Workflow"`
    Status   string `console:"header:Status"`
    Duration string `console:"header:Duration,omitempty"`
}

data := Overview{
    RunID:    12345,
    Workflow: "test-workflow",
    Status:   "completed",
    Duration: "5m30s",
}

// Renderização simples
fmt.Print(console.RenderStruct(data))

// Saída:
//   Run ID  : 12345
//   Workflow: test-workflow
//   Status  : completed
//   Duration: 5m30s
```

## Exemplos de Tag de Formato

### Formatação de Número

```go
type Metrics struct {
    TokenUsage int `console:"header:Token Usage,format:number"`
    Errors     int `console:"header:Errors"`
}

data := Metrics{
    TokenUsage: 250000,
    Errors:     5,
}

// Renderiza como:
//   Token Usage: 250k
//   Errors     : 5
```

### Formatação de Custo

```go
type Billing struct {
    Cost float64 `console:"header:Estimated Cost,format:cost"`
}

data := Billing{
    Cost: 1.234,
}

// Renderiza como:
//   Estimated Cost: $1.234
```

## Comportamento de Renderização

### Estruturas (Structs)
Estruturas são renderizadas como pares chave-valor com alinhamento adequado.

### Fatias (Slices)
Fatias de estruturas são renderizadas automaticamente como tabelas:

```go
type Job struct {
    Name       string `console:"header:Name"`
    Status     string `console:"header:Status"`
    Conclusion string `console:"header:Conclusion,omitempty"`
}

jobs := []Job{
    {Name: "build", Status: "completed", Conclusion: "success"},
    {Name: "test", Status: "in_progress", Conclusion: ""},
}

fmt.Print(console.RenderStruct(jobs))
```

Renderiza como:

```
Name  | Status      | Conclusion
----- | ----------- | ----------
build | completed   | success
test  | in_progress | -
```

### Mapas
Mapas são renderizados como cabeçalhos estilo markdown com pares chave-valor.

### Manipulação de Tipo Especial

#### time.Time
Campos `time.Time` são formatados automaticamente como `"2006-01-02 15:04:05"`. Valores de tempo zero são considerados vazios quando usados com `omitempty`.

#### Campos não exportados
O sistema de renderização manipula com segurança campos de estrutura não exportados verificando `CanInterface()` antes de tentar acessar os valores dos campos.
