# Referência de Padrões Funcionais

Este documento contém implementações de referência e diretrizes para o fluxo de trabalho **Pragmático Funcional** (Functional Pragmatist). O agente lê este arquivo ao implementar melhorias funcionais/de imutabilidade.

## Implementações Auxiliares (Helpers)

### Auxiliares de Slice (`pkg/fp/`)

```go
// pkg/fp/slice.go - Exemplos de auxiliares para operações comuns
package fp

// Map transforma cada elemento em um slice
// Nota: usa var+append para evitar violações do CodeQL de make([]U, len(slice))
func Map[T, U any](slice []T, fn func(T) U) []U {
    var result []U
    for _, v := range slice {
        result = append(result, fn(v))
    }
    return result
}

// Filter retorna elementos que correspondem ao predicado
func Filter[T any](slice []T, fn func(T) bool) []T {
    var result []T
    for _, v := range slice {
        if fn(v) {
            result = append(result, v)
        }
    }
    return result
}

// Reduce agrega elementos de um slice
func Reduce[T, U any](slice []T, initial U, fn func(U, T) U) U {
    result := initial
    for _, v := range slice {
        result = fn(result, v)
    }
    return result
}
```

### Invólucros (Wrappers) de Lógica Reutilizáveis

```go
// Invólucro de Retry com backoff exponencial
func Retry[T any](attempts int, delay time.Duration, fn func() (T, error)) (T, error) {
    var result T
    var err error
    for i := 0; i < attempts; i++ {
        result, err = fn()
        if err == nil {
            return result, nil
        }
        if i < attempts-1 {
            time.Sleep(delay * time.Duration(1<<i))  // Backoff exponencial
        }
    }
    return result, fmt.Errorf("failed after %d attempts: %w", attempts, err)
}

// Uso:
data, err := Retry(3, time.Second, func() ([]byte, error) {
    return fetchFromAPI(url)
})
```

```go
// Invólucro de temporização para registro de desempenho (logs)
func WithTiming[T any](name string, logger Logger, fn func() T) T {
    start := time.Now()
    result := fn()
    logger.Printf("%s took %v", name, time.Since(start))
    return result
}

// Uso:
result := WithTiming("database query", logger, func() []Record {
    return db.Query(sql)
})
```

```go
// Invólucro de Memoização para cache
func Memoize[K comparable, V any](fn func(K) V) func(K) V {
    cache := make(map[K]V)
    var mu sync.RWMutex

    return func(key K) V {
        mu.RLock()
        if val, ok := cache[key]; ok {
            mu.RUnlock()
            return val
        }
        mu.RUnlock()

        val := fn(key)

        mu.Lock()
        cache[key] = val
        mu.Unlock()

        return val
    }
}

// Uso:
expensiveCalc := Memoize(func(n int) int {
    // computação cara
    return fibonacci(n)
})
```

```go
// Invólucro para tratamento de erro
func Must[T any](val T, err error) T {
    if err != nil {
        panic(err)
    }
    return val
}

// Uso na inicialização:
config := Must(LoadConfig("config.yaml"))
```

```go
// Invólucro para execução condicional
func When[T any](condition bool, fn func() T, defaultVal T) T {
    if condition {
        return fn()
    }
    return defaultVal
}

// Uso:
result := When(useCache, func() Data { return cache.Get(key) }, fetchFromDB(key))
```

## Exemplos de Transformação

### Melhorias de Imutabilidade

```go
// Antes: Múltiplas mutações
var config Config
config.Host = getHost()
config.Port = getPort()
config.Timeout = getTimeout()

// Depois: Inicialização única
config := Config{
    Host:    getHost(),
    Port:    getPort(),
    Timeout: getTimeout(),
}
```

### Padrões de Inicialização Funcional

```go
// Antes: Construção imperativa
result := make(map[string]string)
result["name"] = name
result["version"] = version
result["status"] = "active"

// Depois: Inicialização declarativa
result := map[string]string{
    "name":    name,
    "version": version,
    "status":  "active",
}
```

### Operações de Transformação

```go
// Antes: Filtragem e mapeamento imperativos
var activeNames []string
for _, item := range items {
    if item.Active {
        activeNames = append(activeNames, item.Name)
    }
}

// Depois: Pipeline funcional
activeItems := sliceutil.Filter(items, func(item Item) bool { return item.Active })
activeNames := sliceutil.Map(activeItems, func(item Item) string { return item.Name })

// Nota: Às vezes, o código inline é mais claro — use o bom senso!
```

### Padrão de Opções Funcionais (Functional Options)

```go
// Antes: Construtor com muitos parâmetros
func NewClient(host string, port int, timeout time.Duration, retries int, logger Logger) *Client {
    return &Client{
        host:    host,
        port:    port,
        timeout: timeout,
        retries: retries,
        logger:  logger,
    }
}

// Depois: Padrão de opções funcionais
type ClientOption func(*Client)

func WithTimeout(d time.Duration) ClientOption {
    return func(c *Client) {
        c.timeout = d
    }
}

func WithRetries(n int) ClientOption {
    return func(c *Client) {
        c.retries = n
    }
}

func WithLogger(l Logger) ClientOption {
    return func(c *Client) {
        c.logger = l
    }
}

func NewClient(host string, port int, opts ...ClientOption) *Client {
    c := &Client{
        host:    host,
        port:    port,
        timeout: 30 * time.Second,  // padrão sensato
        retries: 3,                  // padrão sensato
        logger:  defaultLogger,      // padrão sensato
    }
    for _, opt := range opts {
        opt(c)
    }
    return c
}

// Uso: client := NewClient("localhost", 8080, WithTimeout(time.Minute), WithRetries(5))
```

### Eliminando Estado Mutável Compartilhado

```go
// Antes: Estado mutável global
var (
    globalConfig *Config
    configMutex  sync.RWMutex
)

func GetSetting(key string) string {
    configMutex.RLock()
    defer configMutex.RUnlock()
    return globalConfig.Settings[key]
}

// Depois: Passagem explícita de parâmetros
type Service struct {
    config *Config  // Imutável após a construção
}

func NewService(config *Config) *Service {
    return &Service{config: config}
}

func (s *Service) ProcessRequest(req Request) Response {
    setting := s.config.Settings["timeout"]
    // ... usar setting
}
```

### Extraindo Funções Puras

```go
// Antes: Lógica mista (pura e impura)
func ProcessOrder(order Order) error {
    log.Printf("Processing order %s", order.ID)  // Efeito colateral

    total := 0.0
    for _, item := range order.Items {
        total += item.Price * float64(item.Quantity)
    }

    if total > 1000 {
        total *= 0.9  // 10% de desconto
    }

    db.Save(order.ID, total)  // Efeito colateral
    return nil
}

// Depois: Cálculo puro extraído
func CalculateOrderTotal(items []OrderItem) float64 {
    total := 0.0
    for _, item := range items {
        total += item.Price * float64(item.Quantity)
    }
    return total
}

func ApplyDiscounts(total float64) float64 {
    if total > 1000 {
        return total * 0.9
    }
    return total
}

// Orquestração impura - efeitos colaterais são explícitos e isolados
func ProcessOrder(order Order, db Database, logger Logger) error {
    logger.Printf("Processing order %s", order.ID)
    total := ApplyDiscounts(CalculateOrderTotal(order.Items))
    return db.Save(order.ID, total)
}
```

## Diretrizes

### Refatoração Orientada a Testes (TDD)

**CRÍTICO: Sempre verifique a cobertura de testes antes de refatorar:**

```bash
go test -cover ./pkg/caminho/para/pacote/
```

**Fluxo de Trabalho:**
1. **Verificar cobertura** - Confirme se os testes existem (cobertura mínima de 60%)
2. **Escrever testes primeiro** - Se a cobertura for baixa, adicione testes para o comportamento atual
3. **Verificar se os testes passam** - Testes em verde antes de refatorar
4. **Refatorar** - Realizar as melhorias funcionais/de imutabilidade
5. **Verificar se os testes passam** - Testes em verde após a refatoração

**Para novas funções auxiliares (`pkg/fp/`):** Escreva os testes PRIMEIRO, visando >80% de cobertura, use testes baseados em tabelas (table-driven tests).

### Equilibrar Pragmatismo e Pureza

- **FAÇA** os dados imutáveis quando isso melhorar a segurança e a clareza.
- **USE** padrões funcionais para transformações de dados.
- **USE** opções funcionais para APIs extensíveis.
- **EXTRAIA** funções puras para melhorar a testabilidade.
- **ELIMINE** o estado mutável compartilhado onde for prático.
- **NÃO** force padrões funcionais onde o estilo imperativo for mais claro.
- **NÃO** crie abstrações excessivamente complexas para operações simples.
- **NÃO** adicione invólucros desnecessários para operações únicas.

### Diretrizes para o Padrão de Opções Funcionais

**Use quando:** O construtor tem 4+ parâmetros opcionais, a API precisa ser estendida sem alterações que quebrem a compatibilidade, a configuração tem padrões sensatos.

**Não use quando:** Todos os parâmetros são obrigatórios, o construtor tem 1-2 parâmetros simples, a configuração provavelmente não mudará.

```go
// Convenção de tipo Option
type Option func(*Config)

// Nomeação de função Option: prefixo With*
func WithTimeout(d time.Duration) Option

// Parâmetros obrigatórios permanecem posicionais
func New(required1 string, required2 int, opts ...Option) *T
```

### Diretrizes para Funções Puras

**Características:** Mesma entrada → mesma saída, sem efeitos colaterais, sem dependência de estado mutável externo.

**Quando extrair:** Lógica de negócio, lógica de validação, formatação/parsing, qualquer computação sem E/S (I/O).

```go
// Padrão núcleo puro (pure core), casca impura (impure shell)
func ProcessOrder(order Order, db Database, logger Logger) error {
    validated := ValidateOrder(order)      // Pura
    total := CalculateTotal(validated)     // Pura
    discounted := ApplyDiscounts(total)    // Pura
    return db.Save(order.ID, discounted)   // Efeito colateral isolado aqui
}
```

### Evitando Estado Mutável Compartilhado

**Estratégias:**
1. Passar dependências através de construtores.
2. Carregar a configuração uma única vez, nunca modificar.
3. Usar contexto para dados por solicitação.
4. Manter o estado mutável nas extremidades (edges).

```go
// ❌ Estado mutável global
var config *Config
var cache = make(map[string]Result)

// ✅ Dependência explícita
type Service struct { config *Config }

// ✅ Estado encapsulado
type Cache struct {
    mu   sync.RWMutex
    data map[string]Result
}
```

### Diretrizes para Invólucros Reutilizáveis

**Crie quando:** O padrão aparecer 3+ vezes, for uma preocupação transversal (cross-cutting concern), a lógica complexa se beneficiar da abstração.

**Não crie quando:** For um uso único, o código inline simples for mais claro, o invólucro ocultar detalhes importantes.

**Design:** Mantenha o foco em uma única preocupação, use genéricos (generics) para segurança de tipos, trate os erros adequadamente.

### Quando Usar Inline vs Auxiliares

**Use inline quando:** A operação for simples e usada uma única vez, a versão inline for mais clara.

**Use auxiliar (helper) quando:** O padrão aparecer 3+ vezes, o auxiliar melhorar significativamente a clareza, a operação for complexa.

### Considerações Específicas de Go

- O Go não tem map/filter/reduce integrados — tudo bem!
- Loops inline costumam ser mais claros que auxiliares genéricos.
- Use parâmetros de tipo (generics) para auxiliares para evitar o uso de reflection.
- Evite `make([]T, len(input))` — use `var result []T` + `append` (o CodeQL sinaliza alocação derivada do comprimento).
- Loops `for` simples são idiomáticos em Go — não force o estilo funcional.
- Opções funcionais é um padrão Go bem estabelecido — use-o com confiança.
- A passagem explícita de parâmetros é idiomática em Go — prefira-a em vez de globais.

### Immutabilidade por Convenção

```go
// Campos não exportados sinalizam "não modifique"
type Config struct {
    host string
    port int
}

// Getters exportados, sem setters
func (c *Config) Host() string { return c.host }

// Aplicação no construtor
func NewConfig(host string, port int) (*Config, error) {
    if host == "" {
        return nil, errors.New("host required")
    }
    return &Config{host: host, port: port}, nil
}

// Cópia defensiva
func (s *Service) GetItems() []Item {
    return slices.Clone(s.items)
}
```

### Gerenciamento de Riscos

**Baixo Risco (Priorize):**
- Converter `var x T; x = valor` para `x := valor`.
- Substituir a inicialização de slice/map vazio por literais.
- Tornar a inicialização de structs mais declarativa.
- Extrair funções auxiliares puras (sem alteração na API).

**Médio Risco (Revise com cuidado):**
- Converter loops de intervalo (range) para padrões funcionais.
- Adicionar novas funções auxiliares.
- Aplicar opções funcionais a construtores internos.
- Extrair funções puras de funções maiores.

**Alto Risco (Evite ou verifique minuciosamente):**
- Alterações em APIs públicas.
- Modificações em padrões de concorrência.
- Alterações que afetam o fluxo de tratamento de erros.
- Eliminação de estado compartilhado usado entre pacotes.
- Adição de invólucros que alteram o fluxo de controle.
