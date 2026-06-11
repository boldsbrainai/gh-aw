---
title: Especificação de Scripts MCP
description: Especificação formal para ferramentas MCP personalizadas de Scripts MCP seguindo convenções W3C
sidebar:
  order: 1360
---

# Especificação de Scripts MCP

**Versão**: 1.1.0  
**Status**: Especificação de Rascunho  
**Versão Mais Recente**: [mcp-scripts-specification](/gh-aw/reference/mcp-scripts-specification/)  
**JSON Schema**: [mcp-scripts-config.schema.json](/gh-aw/schemas/mcp-scripts-config.schema.json)  
**Editor**: Equipe do GitHub Agentic Workflows

---

## Resumo

Esta especificação define Scripts MCP, uma extensão do Gateway MCP que permite a definição inline de ferramentas MCP personalizadas diretamente no frontmatter do fluxo de trabalho usando JavaScript, scripts shell, Python ou Go. Scripts MCP fornece execução de ferramenta efêmera e containerizada com acesso controlado a segredos através de uma interface de ferramentas MCP padronizada. A execução da ferramenta é stateless e independente de sessão, fornecendo isolamento de processo e limites de segurança para funcionalidade personalizada.

## Status deste Documento

Esta seção descreve o status deste documento no momento da publicação. Este é um rascunho de especificação e pode ser atualizado, substituído ou tornado obsoleto por outros documentos a qualquer momento.

Este documento é regido pelo processo de especificações do projeto GitHub Agentic Workflows.

## Índice

1. [Introdução](#1-introdução)
2. [Conformidade](#2-conformidade)
3. [Arquitetura](#3-arquitetura)
4. [Formato de Configuração](#4-formato-de-configuração)
5. [Execução de Ferramenta](#5-execução-de-ferramenta)
6. [Suporte a Linguagem](#6-suporte-a-linguagem)
7. [Modelo de Segurança](#7-modelo-de-segurança)
8. [Manipulação de Saída Grande](#8-manipulação-de-saída-grande)
9. [Integração com Gateway MCP](#9-integração-com-gateway-mcp)
10. [Testes de Conformidade](#10-testes-de-conformidade)
11. [Notas de Sincronização](#sync-notes)

---

## 1. Introdução

### 1.1 Objetivo

Scripts MCP permite que desenvolvedores definam ferramentas MCP personalizadas inline no frontmatter do fluxo de trabalho sem exigir implementações de servidor MCP externas. Ele resolve os seguintes problemas:

- **Desenvolvimento Rápido de Ferramentas**: Defina ferramentas diretamente no fluxo de trabalho sem criar serviços separados
- **Isolamento de Segredo**: Forneça acesso controlado a segredos por meio de mapeamento explícito de variáveis de ambiente
- **Flexibilidade de Linguagem**: Suporte a múltiplas linguagens de implementação (JavaScript, Shell, Python, Go)
- **Isolamento de Processo**: Execute ferramentas em ambientes containerizados com limites de segurança
- **Execução Efêmera**: Invocações de ferramenta stateless sem sobrecarga de gerenciamento de sessão

### 1.2 Escopo

Esta especificação abrange:

- Formato de configuração de Scripts MCP no frontmatter do fluxo de trabalho
- Estrutura de definição de ferramenta e regras de validação
- Linguagens de implementação suportadas e seus modelos de execução
- Acesso a segredos e manipulação de variáveis de ambiente
- Esquemas de entrada/saída de ferramentas e validação
- Mecanismos de manipulação de saída grande
- Integração com a infraestrutura do Gateway MCP

Esta especificação NÃO abrange:

- Protocolo principal do Gateway MCP (veja [Especificação do Gateway MCP](/gh-aw/reference/mcp-gateway/))
- Semântica do protocolo MCP (veja [Especificação do Protocolo de Contexto do Modelo](https://spec.modelcontextprotocol.io/))
- Implementações de servidor MCP externas
- Implementações de cliente de agente
- Funcionalidades de UI ou interativas (ex: elicitação)

### 1.3 Objetivos de Design

Scripts MCP foi projetado para:

- **Conveniência do Desenvolvedor**: Sobrecarga mínima de configuração para padrões de ferramenta comuns
- **Segurança por Padrão**: Acesso explícito a segredos, isolamento de processo, sanitização de saída
- **Execução Stateless**: Sem gerenciamento de sessão, cada invocação é independente
- **Linguagem Agnóstica**: Suporte a múltiplas linguagens de implementação com comportamento consistente
- **Integração com Gateway**: Integração perfeita com o Gateway MCP como uma extensão de configuração

### 1.4 Relação com o Gateway MCP

Scripts MCP é uma **extensão** da Especificação do Gateway MCP. O Gateway MCP permite campos adicionais em seu formato de configuração, e Scripts MCP aproveita essa extensibilidade para fornecer definições de ferramenta inline. As configurações de Scripts MCP são processadas durante a compilação do fluxo de trabalho e traduzidas em configurações de servidor MCP que são roteadas pela infraestrutura do Gateway MCP.

---

## 2. Conformidade

### 2.1 Classes de Conformidade

Uma **implementação conforme de Scripts MCP** é aquela que satisfaz todos os requisitos MUST, REQUIRED e SHALL nesta especificação.

Uma **implementação parcialmente conforme de Scripts MCP** é aquela que satisfaz todos os requisitos MUST para ferramentas JavaScript, mas PODE não ter suporte para implementações em Shell, Python ou Go.

### 2.2 Notação de Requisitos

As palavras-chave "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY" e "OPTIONAL" neste documento devem ser interpretadas como descrito em [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

### 2.3 Níveis de Conformidade

Implementações DEVEM suportar:

- **Nível 1 (Requerido)**: Ferramentas JavaScript, validação de entrada básica, transporte HTTP
- **Nível 2 (Padrão)**: Ferramentas Shell e Python, tratamento de timeout, isolamento de segredo
- **Nível 3 (Completo)**: Ferramentas Go, manipulação de saída grande, todas as funcionalidades opcionais

---

## 3. Arquitetura

### 3.1 Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────┐
│                 Frontmatter do Fluxo de Trabalho        │
│                  (mcp-scripts:)                         │
└──────────────────────┬──────────────────────────────────┘
                       │ Compilação
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Servidor de Scripts MCP                    │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Carregador de Configuração e Registro de Ferramenta|  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Servidor MCP HTTP (JSON-RPC sobre HTTP)         │  │
│  └───────────────────────────────────────────────────┘  │
└──────┬──────────────┬──────────────┬───────────────────┘
       │              │              │
       │ JavaScript   │ Shell        │ Python/Go
       ▼              ▼              ▼
  ┌─────────┐   ┌─────────┐   ┌─────────┐
  │ Em      │   │ Container│   │ Container│
  │ Processo│   │ Docker   │   │ Docker   │
  │         │   │         │   │         │
  └─────────┘   └─────────┘   └─────────┘
```

### 3.2 Modelo de Execução

Scripts MCP opera com o seguinte modelo de execução:

1. **Fase de Compilação**: O frontmatter do fluxo de trabalho é analisado e validado
2. **Inicialização do Servidor**: O servidor de Scripts MCP é iniciado com configurações de ferramenta
3. **Registro de Ferramenta**: Cada ferramenta é registrada no servidor MCP
4. **Invocação**: O agente invoca a ferramenta via protocolo MCP (transporte HTTP)
5. **Execução**: O manipulador da ferramenta é executado no ambiente de runtime apropriado
6. **Resposta**: O resultado é retornado via resposta JSON-RPC
7. **Limpeza**: Recursos efêmeros são limpos após a invocação

### 3.3 Modelo de Transporte

Scripts MCP DEVE usar transporte HTTP para comunicação MCP. A arquitetura de transporte é:

- **Cliente → Gateway**: HTTP com payloads JSON-RPC
- **Gateway → Servidor de Scripts MCP**: HTTP com payloads JSON-RPC
- **Servidor de Scripts MCP**: Servidor HTTP na porta configurável (padrão: 3000)
- **Autenticação**: Autenticação baseada em chave de API via cabeçalho Authorization

O transporte stdio NÃO é suportado para Scripts MCP.

---

## 4. Formato de Configuração

### 4.1 Estrutura do Frontmatter

A configuração de Scripts MCP DEVE ser definida na seção `mcp-scripts:` do frontmatter do fluxo de trabalho:

```yaml
mcp-scripts:
  tool-name:
    description: "Descrição da ferramenta"
    inputs:
      param-name:
        type: string
        required: true
        description: "Descrição do parâmetro"
        default: "valor-padrão"
    script: |
      // Implementação JavaScript
    env:
      SECRET_NAME: "${{ secrets.SECRET_NAME }}"
    timeout: 30
```

**Esquema JSON**: [mcp-scripts-config.schema.json](/gh-aw/schemas/mcp-scripts-config.schema.json)

### 4.2 Campos de Configuração da Ferramenta

Cada configuração de ferramenta DEVE conter:

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|----------|-------------|
| `description` | string | Sim | Descrição da ferramenta legível por humanos mostrada aos agentes |

Cada configuração de ferramenta PODE conter:

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|----------|-------------|
| `inputs` | objeto | Não | Definições de parâmetro de entrada (formato JSON Schema) |
| `script` | string | Condicional* | Implementação JavaScript (CommonJS) |
| `run` | string | Condicional* | Implementação de script shell |
| `py` | string | Condicional* | Implementação de script Python |
| `go` | string | Condicional* | Implementação de código Go |
| `env` | objeto | Não | Variáveis de ambiente (tipicamente segredos) |
| `timeout` | inteiro | Não | Timeout de execução em segundos (padrão: 30, aplica-se apenas a run/py/go) |
| `dependencies` | array[string] | Não | Dependências de pacote para instalar no ambiente de execução (específico do runtime) |

*Exatamente UMA de `script`, `run`, `py` ou `go` DEVE ser fornecida por ferramenta.

### 4.3 Dependências

O campo `dependencies` permite a especificação de dependências de runtime que DEVEM ser instaladas antes da execução da ferramenta. O gerenciador de pacotes é inferido a partir da linguagem de implementação:

- **JavaScript (`script:`)**: Dependências instaladas via `npm install`
- **Shell (`run:`)**: Dependências instaladas via gerenciador de pacotes apropriado (apt, yum, etc.)
- **Python (`py:`)**: Dependências instaladas via `pip install`
- **Go (`go:`)**: Dependências instaladas via `go get`

**Exemplo**:

```yaml
mcp-scripts:
  analyze-json:
    description: "Analise JSON com jq"
    inputs:
      json:
        type: string
        required: true
    run: |
      echo "$INPUT_JSON" | jq '.data | length'
    dependencies:
      - jq
    timeout: 30
```

**Exemplo de Dependências Python**:

```yaml
mcp-scripts:
  fetch-url:
    description: "Buscar URL com biblioteca requests"
    inputs:
      url:
        type: string
        required: true
    py: |
      import requests
      import json
      response = requests.get(inputs.get('url'))
      print(json.dumps({"status": response.status_code, "content_length": len(response.text)}))
    dependencies:
      - requests
    timeout: 60
```

**Requisitos**:
- Implementações DEVEM instalar dependências antes da primeira invocação de ferramenta
- Dependências SHOULD ser armazenadas em cache para invocações subsequentes
- Falhas na instalação de dependência DEVEM resultar em erros de execução de ferramenta
- Nomes de pacotes DEVEM ser válidos para o gerenciador de pacotes de destino
- Implementações PODE impor políticas de segurança em pacotes permitidos

### 4.4 Esquema de Parâmetro de Entrada

Os parâmetros de entrada seguem as convenções do JSON Schema:

```yaml
inputs:
  param-name:
    type: string|number|boolean|array|object
    description: "Descrição do parâmetro"
    required: true|false
    default: valor
    enum: [valor1, valor2, ...]
```

**Tipos suportados**:
- `string` - Valores de texto
- `number` - Valores numéricos (inteiro ou float)
- `boolean` - Valores verdadeiro/falso
- `array` - Lista de valores
- `object` - Dados estruturados

**Opções de validação**:
- `required: true` - Parâmetro deve ser fornecido pelo agente
- `default: valor` - Valor padrão se não for fornecido
- `enum: [...]` - Restringir a valores específicos
- `description: "..."` - Texto de ajuda para seleção de ferramenta do agente

### 4.5 Variáveis de Ambiente

Variáveis de ambiente fornecem acesso a segredos para ferramentas:

```yaml
env:
  API_KEY: "${{ secrets.SERVICE_API_KEY }}"
  DATABASE_URL: "${{ secrets.DATABASE_URL }}"
```

**Requisitos**:
- Valores de variável de ambiente PODEM conter expressões de segredo do GitHub Actions (`${{ secrets.NAME }}`)
- Expressões de segredo DEVEM ser resolvidas durante a compilação
- Segredos DEVEM ser mascarados nos logs
- Apenas variáveis de ambiente declaradas explicitamente estão disponíveis para ferramentas

### 4.6 Configuração de Timeout

O timeout aplica-se a ferramentas Shell (`run:`), Python (`py:`) e Go (`go:`):

```yaml
timeout: 120  # 2 minutos
```

**Comportamento**:
- Timeout padrão: 60 segundos
- Timeout mínimo: 1 segundo
- Timeout máximo: Dependente da implementação (SHOULD ser pelo menos 600 segundos)
- Aplicação de timeout: O processo DEVE ser encerrado com SIGTERM, então SIGKILL após o período de carência
- Ferramentas JavaScript (`script:`) executam em-processo e NÃO possuem aplicação de timeout

### 4.7 Requisitos de Validação

Implementações DEVEM validar:

1. **Campos Obrigatórios**: campo `description` está presente e não vazio
2. **Implementações Mutuamente Exclusivas**: Exatamente uma de `script`, `run`, `py`, `go` é fornecida
3. **Esquema de Entrada**: Definições de entrada seguem convenções do JSON Schema
4. **Faixa de Timeout**: Valor de timeout é um número inteiro positivo (mínimo 1 segundo)
5. **Variáveis de Ambiente**: Nomes de variáveis de ambiente são identificadores válidos (alfanumérico maiúsculo com sublinhados)
6. **Nomes de Ferramenta**: Nomes de ferramenta correspondem ao padrão `^[a-zA-Z][a-zA-Z0-9_-]*$`
7. **Dependências**: Nomes de dependência são válidos para o gerenciador de pacotes de destino

Implementações SHOULD validar:

1. **Sintaxe de Script**: Erros de sintaxe no código de implementação (específico da linguagem)
2. **Tipos de Entrada**: Tipos de parâmetro de entrada são tipos JSON Schema suportados
3. **Nomes Reservados**: Nomes de ferramenta não entram em conflito com métodos MCP embutidos
4. **Comprimento da Descrição**: Descrições de ferramenta são claras e concisas (recomendado 10-200 caracteres)
5. **Razoabilidade de Timeout**: Valores de timeout são razoáveis para o propósito da ferramenta (avisar se >600 segundos)

---

## 5. Execução de Ferramenta

### 5.1 Fluxo de Invocação

1. Agente envia solicitação JSON-RPC ao servidor de Scripts MCP
2. Servidor valida o formato da solicitação e autenticação
3. Servidor valida as entradas da ferramenta em relação ao esquema
4. Servidor despacha para o manipulador de linguagem apropriado
5. Manipulador executa a implementação da ferramenta
6. Manipulador captura saída e erros
7. Servidor retorna resposta JSON-RPC ao agente

### 5.2 Validação de Entrada

Implementações DEVEM:

1. Validar se todos os parâmetros necessários são fornecidos
2. Rejeitar solicitações com parâmetros necessários ausentes (erro JSON-RPC -32602)
3. Aplicar valores padrão para parâmetros opcionais
4. Validar restrições de enum se especificadas
5. Coerção de tipos onde possível (ex: string para número)

### 5.3 Tratamento de Erros

Implementações DEVEM retornar erros JSON-RPC para:

- **Ferramenta Ausente** (-32601): Nome da ferramenta não encontrado no registro
- **Parâmetros Inválidos** (-32602): Parâmetro necessário ausente ou tipo inválido
- **Erro de Execução** (-32603): Falha na execução da ferramenta (erro de sintaxe, erro de runtime, timeout)
- **Erro Interno** (-32603): Erro do lado do servidor durante o processamento

As respostas de erro DEVEM incluir:
- Estrutura de erro JSON-RPC padrão
- Mensagem de erro legível por humanos
- Detalhes do erro no campo `data` (stack trace, números de linha etc.)
- Um booleano `data.recoverable` indicando se uma nova tentativa PODE ter sucesso (§5.7)

O campo `data.recoverable` DEVE estar em conformidade com os seguintes requisitos:

1. O campo **DEVE** estar presente e **DEVE** ser um booleano JSON (`true` ou `false`) para todos os erros de execução (`-32603`).
2. `recoverable: true` **DEVE** apenas ser usado para falhas transitórias onde a mesma invocação PODE ter sucesso em uma tentativa subsequente (ex: timeout, falha temporária de inicialização de runtime).
3. `recoverable: false` **DEVE** ser usado para falhas permanentes onde a nova tentativa não alteraria o resultado (ex: sintaxe de script inválida, dependência de runtime não suportada, falha de validação de entrada determinística detectada durante a execução).
4. Implementações **NÃO DEVEM** inferir a capacidade de nova tentativa apenas a partir do código JSON-RPC; clientes **DEVEM** usar `data.recoverable` como o sinal autoritativo de capacidade de nova tentativa em conjunto com a política de nova tentativa em §5.7.

### 5.4 Isolamento de Execução

Cada invocação de ferramenta DEVE ser isolada:

- **Isolamento de Processo**: Ferramentas Shell/Python/Go executam em containers separados
- **Isolamento de Ambiente**: Apenas variáveis de ambiente declaradas estão disponíveis
- **Isolamento de Sistema de Arquivos**: Ferramentas têm acesso apenas ao seu ambiente de execução
- **Isolamento de Rede**: Acesso à rede controlado pela configuração do fluxo de trabalho

Ferramentas JavaScript executam em-processo, mas DEVEM ter:
- Escopo de módulo isolado
- Sem acesso aos internos do servidor
- Tempo de execução limitado (via V8 isolates ou similar)

### 5.5 Captura de Saída

Implementações DEVEM:

1. Capturar stdout da execução da ferramenta
2. Analisar saída JSON, se possível
3. Retornar saída no campo de resultado JSON-RPC
4. Lidar com saídas grandes de acordo com a Seção 8 (Manipulação de Saída Grande)

Para ferramentas Shell/Python/Go:
- Stdout contém o resultado da ferramenta (DEVE ser JSON válido)
- Stderr é registrado, mas não retornado ao agente
- Código de saída 0 indica sucesso
- Código de saída diferente de zero indica falha

Para ferramentas JavaScript:
- O valor de retorno é o resultado da ferramenta
- Erros lançados indicam falha
- Funções assíncronas são esperadas (await)

### 5.6 Requisitos de Timeout de Runtime

Cada manipulador de runtime (`script`, `run`, `py` e `go`) **DEVE** aplicar um timeout de execução configurável e **DEVE** encerrar a execução da ferramenta quando o timeout for atingido.

Implementações **SHOULD** definir este timeout como 30 segundos ou menos, a menos que o autor do fluxo de trabalho configure explicitamente um valor diferente.

Quando ocorrer um timeout, o servidor **DEVE** retornar um erro de execução JSON-RPC (`-32603`) que identifica explicitamente o encerramento por timeout.

### 5.7 Política de Nova Tentativa (Retry)

O comportamento de nova tentativa é controlado pelo chamador e usa o sinal `data.recoverable` de §5.3.
Nesta seção, **orçamento de nova tentativa** significa o número máximo de tentativas totais (tentativa inicial mais novas tentativas) permitidas para uma única invocação.

1. Servidores de Scripts MCP **NÃO DEVEM** repetir automaticamente invocações de ferramenta com falha.
2. Um chamador **DEVE** tratar `data.recoverable: false` de §5.3 como terminal para aquela invocação e **NÃO DEVE** repetir a tentativa, a menos que a política do operador substitua explicitamente este requisito.
3. Um chamador **PODE** repetir quando `data.recoverable: true` de §5.3. Ao repetir, chamadores **SHOULD** usar exponential backoff com jitter:
   - Delay inicial: 250 ms (ou superior)
   - Multiplicador de backoff: 2x
   - Delay máximo: 5 s
4. O orçamento padrão de nova tentativa para falhas recuperáveis **SHOULD NOT** exceder 3 tentativas no total
   (tentativa inicial + até 2 novas tentativas), a menos que requisitos de confiabilidade específicos do fluxo de trabalho justifiquem um orçamento maior.
5. Como invocações de ferramenta podem não ser idempotentes, chamadores **DEVEM** tratar a segurança de nova tentativa como responsabilidade do chamador e **DEVEM** aplicar salvaguardas de idempotência (ex: chaves de idempotência ou verificações de efeito colateral) antes de repetir ferramentas que alteram o estado.

---

## 6. Suporte a Linguagem

### 6.1 Ferramentas JavaScript (`script:`)

#### 6.1.1 Ambiente de Execução

Ferramentas JavaScript DEVEM:
- Executar em ambiente Node.js
- Usar formato de módulo CommonJS
- Ser encapsuladas em função async com entradas desestruturadas
- Ter acesso a `process.env` para segredos
- Ter acesso a objetos globais do GitHub Actions (`github`, `context`, `core`, `io`, `exec`, `glob`, `artifact`)

#### 6.1.2 Objetos Globais Disponíveis

Ferramentas JavaScript têm acesso a bibliotecas JavaScript padrão do GitHub Actions sem importação explícita:

- **`github`**: Cliente API do GitHub a partir de `@actions/github`
- **`context`**: Informações de contexto do fluxo de trabalho a partir de `@actions/github`
- **`core`**: Utilitários principais de Actions a partir de `@actions/core`
- **`io`**: Utilitários de E/S de arquivo a partir de `@actions/io`
- **`exec`**: Utilitários de execução de comando a partir de `@actions/exec`
- **`glob`**: Correspondência de padrão de arquivo a partir de `@actions/glob`
- **`artifact`**: Gerenciamento de artefatos a partir de `@actions/artifact`

**Exemplo usando objetos globais**:

```yaml
mcp-scripts:
  create-issue:
    description: "Criar uma issue no GitHub"
    inputs:
      title:
        type: string
        required: true
      body:
        type: string
        required: true
    script: |
      const octokit = github.getOctokit(process.env.GITHUB_TOKEN);
      const { data } = await octokit.rest.issues.create({
        owner: context.repo.owner,
        repo: context.repo.repo,
        title,
        body
      });
      return { number: data.number, url: data.html_url };
    env:
      GITHUB_TOKEN: "${{ secrets.GITHUB_TOKEN }}"
```

**Requisitos**:
- Objetos globais DEVEM estar disponíveis sem declarações `require()`
- Ferramentas PODEM usar esses globais juntamente com código do usuário
- Implementações DEVEM fornecer a mesma versão de bibliotecas que o runtime do GitHub Actions
- Sem restrições sobre onde as ferramentas são executadas (em-processo ou containerizado)

#### 6.1.3 Encapsulamento de Código

O código de implementação é encapsulado como:

```javascript
async function execute(inputs) {
  const { param1, param2 } = inputs;
  // Código do usuário aqui
}
```

#### 6.1.4 Exemplo

```yaml
mcp-scripts:
  greet-user:
    description: "Cumprimentar um usuário pelo nome"
    inputs:
      name:
        type: string
        required: true
    script: |
      return { message: `Hello, ${name}!` };
```

### 6.2 Ferramentas Shell (`run:`)

#### 6.2.1 Ambiente de Execução

Ferramentas Shell DEVEM:
- Executar em shell bash
- Executar em ambiente containerizado (Docker)
- Ter entradas como variáveis de ambiente com prefixo `INPUT_`
- Saída JSON válida para stdout

#### 6.2.2 Mapeamento de Entrada

Parâmetros de entrada são mapeados para variáveis de ambiente:
- Parâmetro `repo` torna-se `$INPUT_REPO`
- Parâmetro `state` torna-se `$INPUT_STATE`
- Convenção de nomenclatura: `INPUT_${UPPERCASE_PARAM_NAME}`

#### 6.2.3 Exemplo

```yaml
mcp-scripts:
  list-prs:
    description: "Listar pull requests"
    inputs:
      repo:
        type: string
        required: true
      state:
        type: string
        default: "open"
    run: |
      #!/bin/bash
      set -euo pipefail
      
      gh pr list --repo "$INPUT_REPO" --state "$INPUT_STATE" --json number,title
    env:
      GH_TOKEN: "${{ secrets.GITHUB_TOKEN }}"
    timeout: 30
```

### 6.3 Ferramentas Python (`py:`)

#### 6.3.1 Ambiente de Execução

Ferramentas Python DEVEM:
- Executar usando interpretador Python 3.10+
- Executar em ambiente containerizado (Docker)
- Ter acesso a módulos da biblioteca padrão
- Receber entradas como variável de dicionário `inputs`
- Saída JSON válida para stdout

#### 6.3.2 Acesso à Entrada

Parâmetros de entrada estão disponíveis via dicionário `inputs`:
- `inputs.get('param_name')` - Acessar valor de parâmetro
- `inputs.get('param_name', default)` - Acessar com padrão
- Parâmetros usam nomes originais (não maiúsculos)

#### 6.3.3 Exemplo

```yaml
mcp-scripts:
  analyze-data:
    description: "Analisar dados numéricos"
    inputs:
      data:
        type: string
        description: "Números separados por vírgula"
        required: true
    py: |
      import json
      from collections import defaultdict
      
      # Analisar dados de entrada
      data_str = inputs.get('data', '[]')
      data = json.loads(data_str)
      group_by = inputs.get('group_by', 'category')
      
      # Agrupar e agregar
      groups = defaultdict(list)
      for item in data:
        key = item.get(group_by, 'unknown')
        groups[key].append(item)
      
      # Calcular estatísticas
      result = {}
      for key, items in groups.items():
        values = [item.get('value', 0) for item in items]
        result[key] = {
          'count': len(items),
          'sum': sum(values),
          'avg': sum(values) / len(values) if values else 0,
          'min': min(values) if values else 0,
          'max': max(values) if values else 0
        }
      
      print(json.dumps(result))
    timeout: 120
```

### 6.4 Ferramentas Go (`go:`)

#### 6.4.1 Ambiente de Execução

Ferramentas Go DEVEM:
- Executar usando comando `go run`
- Executar em ambiente containerizado (Docker)
- Ter acesso a importações da biblioteca padrão
- Receber entradas como `map[string]any` de stdin
- Saída JSON válida para stdout

#### 6.4.2 Encapsulamento de Código

O código de implementação é encapsulado em:

```go
package main

import (
    "encoding/json"
    "fmt"
    "io"
    "os"
)

func main() {
    // Analisar entradas de stdin
    var inputs map[string]any
    decoder := json.NewDecoder(os.Stdin)
    if err := decoder.Decode(&inputs); err != nil {
        fmt.Fprintf(os.Stderr, "Erro ao analisar entradas: %v\n", err)
        os.Exit(1)
    }
    
    // Código do usuário aqui
}
```

#### 6.4.3 Importações Disponíveis

As seguintes importações são incluídas automaticamente:
- `encoding/json` - Codificação/decodificação JSON
- `fmt` - I/O formatado
- `io` - Primitivas de I/O
- `os` - Funcionalidade do sistema operacional

Importações adicionais PODEM ser adicionadas pelo usuário em seu código.

#### 6.4.4 Exemplo

```yaml
mcp-scripts:
  calculate:
    description: "Realizar cálculos"
    inputs:
      a:
        type: number
        required: true
      b:
        type: number
        required: true
    go: |
      a := inputs["a"].(float64)
      b := inputs["b"].(float64)
      result := map[string]any{
          "sum": a + b,
          "product": a * b,
      }
      json.NewEncoder(os.Stdout).Encode(result)
    timeout: 30
```

---

## 7. Modelo de Segurança

### 7.1 Isolamento de Segredo

Implementações DEVEM:

1. **Acesso Explícito**: Apenas variáveis de ambiente declaradas em `env:` estão disponíveis para ferramentas
2. **Mascaramento de Segredo**: Segredos referenciados via `${{ secrets.NAME }}` são mascarados nos logs
3. **Sem Acesso Global**: Ferramentas não podem acessar segredos de fluxo de trabalho não declarados explicitamente
4. **Isolamento de Ambiente**: Cada ferramenta tem um namespace de variável de ambiente isolado

### 7.2 Isolamento de Processo

Implementações DEVEM fornecer:

1. **Containerização**: Ferramentas Shell, Python e Go executam em containers Docker
2. **Limites de Processo**: Cada invocação é um processo separado
3. **Limites de Recurso**: Containers aplicam limites de CPU, memória e sistema de arquivos
4. **Restrições de Rede**: Acesso à rede controlado pela configuração do fluxo de trabalho

Ferramentas JavaScript SHOULD fornecer:

1. **Isolamento de Módulo**: Ferramentas executam em escopo de módulo isolado
2. **Execução Limitada**: Usar V8 isolates ou similar para limites de CPU/memória
3. **Sem Acesso ao Servidor**: Ferramentas não podem acessar internos do servidor ou outras ferramentas

### 7.3 Sanitização de Entrada

Implementações DEVEM:

1. Validar tipos de entrada em relação ao esquema antes da execução
2. Rejeitar solicitações que não estejam em conformidade com o esquema
3. Impedir injeção de código via validação de entrada
4. Aplicar limites de comprimento a entradas de string (SHOULD ser pelo menos 10KB)

### 7.4 Sanitização de Saída

Implementações DEVEM:

1. Analisar e validar saída JSON de ferramentas
2. Rejeitar saída não JSON de ferramentas Shell/Python/Go
3. Aplicar limites de tamanho à saída (veja Seção 8)
4. Remover ou mascarar qualquer exposição acidental de segredo na saída

### 7.5 Aplicação de Timeout

Implementações DEVEM:

1. Aplicar timeout para ferramentas Shell/Python/Go
2. Encerrar processos que excedem o timeout
3. Enviar SIGTERM, aguardar período de carência (5 segundos), então SIGKILL
4. Retornar erro de timeout para agente
5. Limpar recursos do container após timeout

---

## 8. Manipulação de Saída Grande

### 8.1 Limite de Tamanho

Quando a saída da ferramenta excede 500 caracteres, as implementações DEVEM:

1. Salvar a saída completa em um arquivo
2. Gerar nome de arquivo único em localização acessível
3. Retornar resposta de metadados em vez de conteúdo completo

### 8.2 Formato de Resposta de Metadados

```json
{
  "content": {
    "type": "file",
    "path": "/tmp/tool-output-abc123.json",
    "size": 15234,
    "message": "Saída muito grande (15234 bytes). Salva em arquivo."
  },
  "preview": {
    "schema": {
      "type": "array",
      "items": { "type": "object" }
    },
    "first_item": { ... },
    "item_count": 42
  }
}
```

**Campos Obrigatórios**:
- `content.type`: MUST ser "file"
- `content.path`: Caminho do arquivo acessível ao agente
- `content.size`: Tamanho do arquivo em bytes
- `content.message`: Explicação legível por humanos

**Campos Opcionais**:
- `preview.schema`: Esquema JSON do conteúdo
- `preview.first_item`: Primeiro item na array/lista
- `preview.item_count`: Número de itens na coleção

### 8.3 Acesso a Arquivo

Implementações DEVEM:

1. Armazenar arquivos de saída em localização acessível ao agente
2. Usar nomes de arquivo únicos e não previsíveis
3. Limpar arquivos após a conclusão do fluxo de trabalho
4. Aplicar limites de tamanho de arquivo (SHOULD ser pelo menos 10MB)

---

## 9. Integração com Gateway MCP

### 9.1 Extensão de Configuração

Scripts MCP estende o formato de configuração do Gateway MCP. Durante a compilação do fluxo de trabalho:

1. Ferramentas Scripts MCP são compiladas em configuração de servidor MCP
2. A configuração é passada para o Gateway MCP como servidor adicional
3. O gateway roteia solicitações para o servidor Scripts MCP
4. O servidor Scripts MCP manipula a execução da ferramenta

### 9.2 Comunicação do Gateway

O servidor Scripts MCP DEVE:

1. Expor endpoint HTTP para comunicação MCP
2. Aceitar solicitações JSON-RPC do gateway
3. Exigir autenticação via cabeçalho Authorization
4. Retornar respostas JSON-RPC ao gateway

### 9.3 Geração de Configuração

No momento da compilação, Scripts MCP gera:

```json
{
  "mcpServers": {
    "safeinputs": {
      "type": "http",
      "url": "http://localhost:3000",
      "headers": {
        "Authorization": "generated-api-key"
      }
    }
  }
}
```

Esta configuração é mesclada com outros servidores MCP e passada para o gateway.

### 9.4 Ciclo de Vida do Servidor

Servidor Scripts MCP:

1. **Inicialização**: O servidor inicia durante a inicialização do fluxo de trabalho
2. **Registro de Ferramenta**: Todas as ferramentas são registradas na inicialização
3. **Runtime**: O servidor aceita solicitações durante a execução do fluxo de trabalho
4. **Encerramento**: O servidor termina quando o fluxo de trabalho é concluído
5. **Limpeza**: Todos os recursos efêmeros são limpos

---

## 10. Testes de Conformidade

### 10.1 Requisitos da Suíte de Testes

Uma implementação conforme DEVE passar nas seguintes categorias de teste:

#### 10.1.1 Testes de Configuração

- **T-CFG-001**: Ferramenta válida com implementação JavaScript
- **T-CFG-002**: Ferramenta válida com implementação Shell
- **T-CFG-003**: Ferramenta válida com implementação Python
- **T-CFG-004**: Ferramenta válida com implementação Go
- **T-CFG-005**: Ferramenta com todos os tipos de parâmetro de entrada
- **T-CFG-006**: Ferramenta com variáveis de ambiente
- **T-CFG-007**: Ferramenta com timeout personalizado
- **T-CFG-008**: Rejeitar ferramenta sem descrição
- **T-CFG-009**: Rejeitar ferramenta com múltiplas implementações
- **T-CFG-010**: Rejeitar ferramenta com timeout inválido

#### 10.1.2 Testes de Validação de Entrada

- **T-VAL-001**: Validação de parâmetro obrigatório
- **T-VAL-002**: Parâmetro opcional com padrão
- **T-VAL-003**: Validação de restrição de enum
- **T-VAL-004**: Coerção de tipo (string para número)
- **T-VAL-005**: Rejeição de tipo inválido
- **T-VAL-006**: Erro de parâmetro obrigatório ausente

#### 10.1.3 Testes de Execução

- **T-EXE-001**: Execução bem-sucedida da ferramenta JavaScript
- **T-EXE-002**: Execução bem-sucedida da ferramenta Shell
- **T-EXE-003**: Execução bem-sucedida da ferramenta Python
- **T-EXE-004**: Execução bem-sucedida da ferramenta Go
- **T-EXE-005**: Ferramenta com acesso a segredo
- **T-EXE-006**: Aplicação de timeout da ferramenta
- **T-EXE-007**: Tratamento de erro de execução da ferramenta
- **T-EXE-008**: Ferramenta com análise de saída JSON

#### 10.1.4 Testes de Segurança

- **T-SEC-001**: Verificação de isolamento de segredo
- **T-SEC-002**: Isolamento de variável de ambiente
- **T-SEC-003**: Isolamento de processo (Shell/Python/Go)
- **T-SEC-004**: Sanitização de entrada
- **T-SEC-005**: Sanitização de saída
- **T-SEC-006**: Mascaramento de segredo em logs
- **T-SEC-007**: Segurança da instalação de dependência
- **T-SEC-008**: Controle de acesso a objetos globais do GitHub Actions

#### 10.1.5 Testes de Saída Grande

- **T-OUT-001**: Saída abaixo de 500 caracteres (retorno direto)
- **T-OUT-002**: Saída acima de 500 caracteres (salvamento de arquivo)
- **T-OUT-003**: Formato de resposta de metadados
- **T-OUT-004**: Acessibilidade de arquivo ao agente
- **T-OUT-005**: Geração de visualização de esquema JSON

#### 10.1.6 Testes de Dependências

- **T-DEP-001**: Instalação de dependência npm para ferramentas JavaScript
- **T-DEP-002**: Instalação de dependência pip para ferramentas Python
- **T-DEP-003**: Instalação de dependência go get para ferramentas Go
- **T-DEP-004**: Instalação de dependência apt/yum para ferramentas shell
- **T-DEP-005**: Comportamento de cache de dependência
- **T-DEP-006**: Tratamento de falha de instalação de dependência

#### 10.1.7 Testes de Integração

- **T-INT-001**: Geração de configuração do Gateway MCP
- **T-INT-002**: Inicialização do servidor MCP HTTP
- **T-INT-003**: Autenticação com gateway
- **T-INT-004**: Tratamento de solicitação JSON-RPC
- **T-INT-005**: Formato de resposta de erro

### 10.2 Checklist de Conformidade

| Requisito | ID de Teste | Nível | Status |
|-------------|---------|-------|--------|
| Ferramentas JavaScript | T-CFG-001, T-EXE-001 | 1 | Requerido |
| Ferramentas Shell | T-CFG-002, T-EXE-002 | 2 | Padrão |
| Ferramentas Python | T-CFG-003, T-EXE-003 | 2 | Padrão |
| Ferramentas Go | T-CFG-004, T-EXE-004 | 3 | Completo |
| Validação de entrada | T-VAL-* | 1 | Requerido |
| Isolamento de segredo | T-SEC-001, T-SEC-002 | 1 | Requerido |
| Isolamento de processo | T-SEC-003 | 2 | Padrão |
| Tratamento de timeout | T-EXE-006 | 2 | Padrão |
| Manipulação de saída grande | T-OUT-* | 3 | Completo |
| Suporte a dependências | T-DEP-* | 2 | Padrão |
| Globais do GitHub Actions | T-SEC-008 | 1 | Requerido |
| Integração com Gateway MCP | T-INT-* | 1 | Requerido |

### 10.3 Execução de Teste

Implementações SHOULD fornecer:

1. Runner de teste automatizado para suíte de conformidade
2. Relatório de resultados de teste em formato padrão
3. Fixtures de teste para cenários comuns
4. Configuração de ambiente de teste de integração
5. Geração de relatório de conformidade

---

## Notas de Sincronização

Esta seção mapeia cada seção normativa da Especificação de Scripts MCP para os arquivos de código-fonte Go em `pkg/workflow/` que a implementam. Este mapeamento é mantido para ajudar os contribuidores a verificar se as alterações de especificação são refletidas na implementação e vice-versa.

Após qualquer alteração nesta especificação, execute `make recompile` para regenerar arquivos de bloqueio compilados, e execute `go test ./pkg/workflow/...` para verificar a conformidade.

| Seção | Título | Arquivo(s) Fonte Primário(s) |
|---------|-------|------------------------|
| §3 | Arquitetura | `pkg/workflow/mcp_scripts_parser.go` (definições de tipo, `MCPScriptsConfig`, `MCPScriptToolConfig`), `pkg/workflow/mcp_scripts_renderer.go` (renderização de configuração do gateway) |
| §4 | Formato de Configuração | `pkg/workflow/mcp_scripts_parser.go` (`parseMCPScriptsMap`, `parseMCPScriptToolConfig`), `pkg/parser/` (análise de YAML de frontmatter) |
| §5 | Execução de Ferramenta | `pkg/workflow/mcp_scripts_generator.go` (`GenerateMCPScriptJavaScriptToolScript`, `GenerateMCPScriptShellToolScript`, `GenerateMCPScriptPythonToolScript`), `actions/setup/js/` (harness de execução JS em runtime) |
| §6 | Suporte a Linguagem | `pkg/workflow/mcp_scripts_generator.go` (geração de script por linguagem), `actions/setup/sh/` (harness de shell), `pkg/workflow/mcp_scripts_parser.go` (`parseTimeoutString`) |
| §7 | Modelo de Segurança | `pkg/workflow/mcp_scripts_renderer.go` (`collectMCPScriptsSecrets`, `renderMCPScriptsMCPConfigWithOptions`), `pkg/workflow/mcp_scripts_parser.go` (análise de campo de env/segredo) |
| §8 | Manipulação de Saída Grande | `pkg/workflow/mcp_scripts_generator.go` (lógica de truncamento de saída), `actions/setup/js/mcp_scripts_mcp_server_http.cjs` (streaming de saída de transporte HTTP) |
| §9 | Integração com Gateway MCP | `pkg/workflow/mcp_scripts_renderer.go` (`renderMCPScriptsMCPConfigWithOptions`), `pkg/workflow/mcp_scripts_generator.go` (`GenerateMCPScriptsMCPServerScript`, `GenerateMCPScriptsToolsConfig`) |
