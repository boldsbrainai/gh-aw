---
title: Especificação do Gateway MCP
description: Especificação formal para a implementação do Gateway do Protocolo de Contexto do Modelo (MCP) seguindo convenções W3C
sidebar:
  order: 1350
---

# Especificação do Gateway MCP

**Versão**: 1.14.0  
**Status**: Especificação de Rascunho  
**Versão Mais Recente**: [mcp-gateway](/gh-aw/reference/mcp-gateway/)  
**Esquema JSON**: [mcp-gateway-config.schema.json](/gh-aw/schemas/mcp-gateway-config.schema.json)  
**Editor**: Equipe do GitHub Agentic Workflows

---

## Resumo

Esta especificação define o Gateway do Protocolo de Contexto do Modelo (MCP), um serviço de proxy transparente que permite acesso HTTP unificado a múltiplos servidores MCP. O gateway suporta servidores MCP containerizados, servidores MCP baseados em HTTP e tipos de servidor personalizados. O gateway fornece tradução de protocolo, isolamento de servidor, autenticação, monitoramento de integridade e extensibilidade para implementações de servidor especializadas.

## Status deste Documento

Esta seção descreve o status deste documento no momento da publicação. Este é um rascunho de especificação e pode ser atualizado, substituído ou tornado obsoleto por outros documentos a qualquer momento.

Este documento é regido pelo processo de especificações do projeto GitHub Agentic Workflows.

## Índice

1. [Introdução](#1-introdução)
2. [Conformidade](#2-conformidade)
3. [Arquitetura](#3-arquitetura)
4. [Configuração](#4-configuração)
5. [Comportamento do Protocolo](#5-comportamento-do-protocolo)
6. [Isolamento de Servidor](#6-isolamento-de-servidor)
7. [Autenticação](#7-autenticação)
8. [Monitoramento de Integridade](#8-monitoramento-de-integridade)
9. [Tratamento de Erros](#9-tratamento-de-erros)
10. [Política de Proteção](#10-política-de-proteção)
11. [Testes de Conformidade](#11-testes-de-conformidade)

---

## 1. Introdução

### 1.1 Objetivo

O Gateway MCP serve como uma camada de tradução de protocolo entre clientes MCP que esperam comunicação baseada em HTTP e servidores MCP executados em containers ou acessíveis via HTTP. Ele permite:

- **Tradução de Protocolo**: Conversão entre servidores stdio containerizados e transportes HTTP
- **Acesso Unificado**: Endpoint HTTP único para múltiplos servidores MCP
- **Isolamento de Servidor**: Aplicação de limites entre instâncias de servidor por meio de conteinerização
- **Autenticação**: Controle de acesso baseado em token
- **Monitoramento de Integridade**: Endpoints de disponibilidade de serviço

O gateway requer que servidores MCP baseados em stdio SEJAM containerizados. A execução direta de comando (stdio+comando sem conteinerização) NÃO é suportada porque não pode fornecer as garantias necessárias de isolamento e portabilidade.

### 1.2 Escopo

Esta especificação abrange:

- Formato e semântica de configuração do gateway
- Comportamento de tradução de protocolo
- Gerenciamento do ciclo de vida do servidor
- Mecanismos de autenticação
- Interfaces de monitoramento de integridade
- Requisitos de tratamento de erros

Esta especificação NÃO abrange:

- Semântica do protocolo principal do Protocolo de Contexto do Modelo (MCP)
- Implementações individuais de servidor MCP
- Implementações MCP do lado do cliente
- Interfaces de usuário ou funcionalidades interativas (ex: elicitação)

### 1.3 Objetivos de Design

O gateway DEVE ser projetado para:

- **Operação Headless**: Nenhuma interação do usuário necessária durante o runtime
- **Comportamento Fail-Fast**: Falha imediata com informações de diagnóstico
- **Compatibilidade Avançada**: Rejeição graciosa de funcionalidades de configuração desconhecidas
- **Segurança**: Isolamento entre servidores e manuseio seguro de credenciais

---

## 2. Conformidade

### 2.1 Classes de Conformidade

Uma **implementação de Gateway MCP conforme** é aquela que satisfaz todos os requisitos MUST, REQUIRED e SHALL nesta especificação.

Uma **implementação de Gateway MCP parcialmente conforme** é aquela que satisfaz todos os requisitos MUST, mas PODE não ter suporte para funcionalidades opcionais marcadas com SHOULD ou MAY.

### 2.2 Notação de Requisitos

As palavras-chave "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY" e "OPTIONAL" neste documento devem ser interpretadas como descrito em [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

### 2.3 Níveis de Conformidade

Implementações DEVEM suportar:

- **Nível 1 (Requerido)**: Funcionalidade básica de proxy, transporte stdio, análise de configuração
- **Nível 2 (Padrão)**: Transporte HTTP, autenticação, endpoints de integridade
- **Nível 3 (Completo)**: Todas as funcionalidades opcionais, incluindo expressões de variável, configuração de timeout

---

## 3. Arquitetura

### 3.1 Modelo de Gateway

```
┌─────────────────────────────────────────────────────────┐
│                      Cliente MCP                        │
│                    (Transporte HTTP)                     │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/JSON-RPC
                       ▼
┌─────────────────────────────────────────────────────────┐
│                    Gateway MCP                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Camada de Autenticação e Autorização             │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Camada de Tradução de Protocolo                  │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Isolamento de Servidor e Gerenciamento de Ciclo  │  │
│  └───────────────────────────────────────────────────┘  │
└──────┬──────────────┬──────────────┬───────────────────┘
       │              │              │
       │ stdio        │ HTTP         │ stdio
       ▼              ▼              ▼
  ┌─────────┐   ┌─────────┐   ┌─────────┐
  │ Servidor│   │ Servidor│   │ Servidor│
  │ MCP 1   │   │ MCP 2   │   │ MCP N   │
  └─────────┘   └─────────┘   └─────────┘
```

### 3.2 Suporte a Transporte

O gateway MUST suportar os seguintes mecanismos de transporte:

- **stdio (containerizado)**: Servidores MCP executando em containers com comunicação baseada em entrada/saída padrão
- **HTTP**: Servidores MCP diretos baseados em HTTP

O gateway MUST traduzir todos os transportes upstream para HTTP para comunicação com o cliente.

#### 3.2.1 Requisito de Conteinerização

Servidores MCP baseados em stdio DEVEM ser containerizados. O gateway NÃO SHALL suportar a execução direta de comando sem conteinerização (stdio+comando) porque:

1. A conteinerização fornece isolamento de processo necessário e limites de segurança
2. Containers permitem ambientes reproduzíveis entre diferentes contextos de implantação
3. Imagens de container fornecem versionamento e gerenciamento de dependência
4. A conteinerização garante portabilidade e comportamento consistente

A execução direta de comando de servidores stdio (ex: `command: "node server.js"` sem um container) não é explicitamente SUPORTADA por esta especificação.

### 3.3 Modelo Operacional

O gateway opera em modo headless:

1. A configuração é fornecida via **stdin** (formato JSON)
2. Segredos são fornecidos via **variáveis de ambiente**
3. A saída de inicialização é escrita para **stdout** (configuração reescrita)
4. Mensagens de erro são escritas para **stdout** como payloads de erro
5. O servidor HTTP aceita solicitações do cliente na porta configurada

---

## 4. Configuração

### 4.1 Formato de Configuração

O gateway MUST aceitar configuração via stdin no formato JSON em conformidade com o esquema de arquivo de configuração MCP.

**Esquema JSON**: [mcp-gateway-config.schema.json](/gh-aw/schemas/mcp-gateway-config.schema.json)

#### 4.1.1 Estrutura de Configuração

```json
{
  "mcpServers": {
    "server-name": {
      "container": "string",
      "entrypoint": "string",
      "entrypointArgs": ["string"],
      "mounts": ["source:dest:mode"],
      "env": {
        "VAR_NAME": "value"
      },
      "type": "stdio" | "http",
      "url": "string",
      "tools": ["*"] | ["tool1", "tool2"],
      "headers": {
        "Authorization": "Bearer ${TOKEN}"
      }
    }
  },
  "gateway": {
    "port": 8080,
    "apiKey": "string",
    "domain": "string",
    "startupTimeout": 30,
    "toolTimeout": 60
  },
  "customSchemas": {
    "custom-type": "https://example.com/schema.json"
  }
}
```

#### 4.1.2 Campos de Configuração do Servidor

Cada configuração de servidor MUST suportar:

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|----------|-------------|
| `container` | string | Condicional* | Imagem de container para o servidor MCP (necessário para servidores stdio) |
| `entrypoint` | string | Não | Sobrescrita de entrypoint opcional para container (equivalente a `docker run --entrypoint`) |
| `entrypointArgs` | array[string] | Não | Argumentos passados para entrypoint do container (apenas container) |
| `mounts` | array[string] | Não | Montagens de volume para servidores stdio containerizados (formato: "host:container:mode" onde mode é "ro" (somente leitura) ou "rw" (leitura e escrita)). Aplica-se apenas a servidores stdio. Veja Seção 4.1.5 para detalhes. |
| `env` | objeto | Não | Variáveis de ambiente para o processo do servidor |
| `type` | string | Não | Tipo de transporte: "stdio" ou "http" (padrão: "stdio") |
| `url` | string | Condicional** | URL do endpoint HTTP para servidores HTTP |
| `registry` | string | Não | URI para a localização da instalação quando o MCP é instalado a partir de um registro. Este é um campo informativo usado para documentação e descoberta de ferramentas. Aplica-se a servidores stdio e HTTP. Exemplo: `"https://api.mcp.github.com/v0/servers/microsoft/markitdown"` |
| `tools` | array[string] | Não | Filtro de ferramenta para o servidor MCP. Use `["*"]` para permitir todas as ferramentas (padrão) ou especifique uma lista de nomes de ferramenta para permitir. Este campo é repassado para configurações de agente e aplica-se a servidores stdio e http. |
| `headers` | objeto | Não | Cabeçalhos HTTP para incluir em solicitações (apenas servidores HTTP). Comumente usados para autenticação em servidores HTTP externos. Valores podem conter expressões variáveis. |
| `auth` | objeto | Não | Configuração de autenticação upstream para servidores HTTP. Veja [Seção 7.6](#76-upstream-authentication-oidc). |

*Necessário para servidores stdio (execução containerizada)  
**Necessário para servidores HTTP

**Nota**: O campo `command` NÃO é suportado. Servidores stdio DEVEM usar o campo `container` para especificar um servidor MCP containerizado. A execução direta de comando não é suportada por esta especificação.

#### 4.1.3 Campos de Configuração do Gateway

A seção `gateway` é obrigatória e configura o comportamento específico do gateway:

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|----------|-------------|
| `port` | inteiro | Sim | Porta do servidor HTTP |
| `domain` | string | Sim | Domínio do gateway (localhost ou host.docker.internal) |
| `apiKey` | string | Sim | Chave de API para autenticação |
| `startupTimeout` | inteiro | Não | Timeout de inicialização do servidor em segundos (padrão: 30) |
| `toolTimeout` | inteiro | Não | Timeout de invocação de ferramenta em segundos (padrão: 60) |
| `payloadDir` | string | Não | Caminho do diretório para armazenar arquivos JSON de payload grandes para clientes autenticados |
| `payloadPathPrefix` | string | Não | Prefixo de caminho para remapear caminhos de payload para containers de agente (ex: /workspace/payloads) |
| `payloadSizeThreshold` | inteiro | Não | Limite de tamanho em bytes para armazenar payloads em disco (padrão: 524288 = 512KB) |
| `trustedBots` | array[string] | Não | Strings de identidade de bot adicionais do GitHub (ex: `github-actions[bot]`) passadas para o gateway e mescladas com sua lista de identidade confiável embutida. Este campo é aditivo — ele estende a lista interna, mas não pode remover entradas embutidas. |
| `keepaliveInterval` | inteiro | Não | Intervalo de ping keepalive em segundos para backends MCP HTTP. Impede a expiração de sessão durante tarefas de longa duração. Use `-1` para desabilitar, `0` ou não definido para o padrão do gateway (1500s = 25 min), ou um inteiro positivo para um intervalo personalizado. |
| `sessionTimeout` | string | Não | Timeout de sessão para sessões do gateway MCP como uma string de duração Go (ex: `"30m"`, `"4h"`, `"24h"`). Vazio ou omitido usa o padrão do gateway (6h). Deve ser pelo menos 5m quando definido pelo compilador de fluxo de trabalho (sem limite superior; operadores de infraestrutura podem sobrescrever via variável de ambiente `MCP_GATEWAY_SESSION_TIMEOUT`). |
| `opentelemetry` | objeto | Não | Configuração OpenTelemetry para emitir eventos de rastreamento distribuído para chamadas MCP. Veja Seção 4.1.3.7 para detalhes. |

#### 4.1.3.1 Validação de Caminho do Diretório de Payload

Quando o campo opcional `payloadDir` é fornecido na configuração do gateway, ele especifica um caminho de diretório onde o gateway armazena arquivos JSON de payload grandes para clientes autenticados. Isso permite o manuseio eficiente de payloads de resposta grandes, descarregando-os para o sistema de arquivos.

**Requisitos de Caminho**:

Se `payloadDir` for especificado, os seguintes requisitos se aplicam:

1. O caminho DEVE ser um caminho absoluto (pathname completo)
2. Em sistemas tipo Unix (Linux, macOS), caminhos absolutos DEVEM começar com `/`
3. Em sistemas Windows, caminhos absolutos DEVEM começar com uma letra de unidade seguida por `:` e `\` (ex: `C:\`, `D:\`)
4. O caminho NÃO DEVE ser uma string vazia
5. O caminho SHOULD ser gravável pelo processo do gateway
6. O caminho SHOULD existir ou ser criável pelo processo do gateway

**Exemplos de Validação**:

Caminhos absolutos válidos:

```
Unix/Linux/macOS:
- "/var/lib/mcp-gateway/payloads"
- "/tmp/gateway-payloads"
- "/opt/mcp/data/payloads"

Windows:
- "C:\Program Files\MCP Gateway\payloads"
- "D:\gateway\payloads"
- "C:\temp\payloads"
```

Caminhos inválidos (DEVEM ser rejeitados):

```
Caminhos relativos:
- "payloads" (sem barra inicial ou letra de unidade)
- "./payloads" (relativo ao diretório atual)
- "../data/payloads" (caminho relativo com referência de pai)
- "data/payloads" (caminho relativo)

Vazio ou malformado:
- "" (string vazia)
- " " (apenas espaço em branco)
```

**Considerações de Segurança**:

- Implementações de gateway DEVEM garantir o isolamento adequado entre os arquivos de payload de diferentes clientes
- O gateway SHOULD usar permissões de arquivo apropriadas para evitar acesso não autorizado
- O gateway SHOULD implementar mecanismos de limpeza para arquivos de payload antigos
- O gateway SHOULD validar que o caminho não escapa limites de diretório pretendidos por meio de links simbólicos ou outros mecanismos

**Teste de Conformidade**: T-CFG-005 - Validação de Caminho do Diretório de Payload

#### 4.1.3.2 Prefixo de Caminho de Payload para Containers de Agente

Quando o campo opcional `payloadPathPrefix` é fornecido na configuração do gateway, ele especifica um prefixo de caminho usado para remapear caminhos de arquivo de payload retornados aos clientes. Isso permite que agentes executando em containers acessem arquivos de payload via volumes montados.

**Como funciona**:

1. Gateway salva o payload no sistema de arquivos real: `/tmp/jq-payloads/session123/query456/payload.json`
2. Gateway retorna caminho remapeado ao cliente: `/workspace/payloads/session123/query456/payload.json`
3. Container do agente monta o volume: `-v /tmp/jq-payloads:/workspace/payloads`
4. Agente agora pode acessar o arquivo no caminho retornado ✅

**Exemplo de Configuração**:

```toml
[gateway]
payload_dir = "/tmp/jq-payloads"
payload_path_prefix = "/workspace/payloads"
port = 8080
domain = "localhost"
apiKey = "secret"
```

**Casos de Uso**:
- Agentes executando em containers com layouts de sistema de arquivos diferentes
- Cenários Docker-in-Docker onde caminhos de host precisam de remapeamento
- Ambientes com montagens de volume controladas para segurança

**Requisitos**:
- Se especificado, o prefixo de caminho SHOULD corresponder a um volume montado no container do agente
- O gateway MUST usar este prefixo ao retornar `payloadPath` para clientes
- O gateway MUST ainda salvar arquivos no caminho do sistema de arquivos real (`payloadDir`)

#### 4.1.3.3 Limite de Tamanho de Payload

O campo `payloadSizeThreshold` (padrão: 524288 bytes = 512KB) controla quando payloads de resposta são armazenados em disco versus retornados inline.

**Comportamento**:
- Payloads **menores ou iguais** ao limite: Retornados inline na resposta
- Payloads **maiores** que o limite: Armazenados em disco, metadados retornados com `payloadPath`

**Valor Padrão**: 524288 bytes (512KB)

**Racional**: O padrão de 512KB acomoda respostas de ferramenta MCP típicas, incluindo consultas da API do GitHub (list_commits, list_issues etc.), sem disparar armazenamento em disco. Isso evita problemas de loop de agente quando `payloadPath` não está acessível em containers de agente.

**Exemplo de Configuração**:

```toml
[gateway]
payload_size_threshold = 1048576  # 1MB - minimizar armazenamento em disco
# OU
payload_size_threshold = 262144   # 256KB - armazenamento em disco mais agressivo
```

**Métodos de Configuração**:
- Flag CLI: `--payload-size-threshold <bytes>`
- Variável de ambiente: `MCP_GATEWAY_PAYLOAD_SIZE_THRESHOLD=<bytes>`
- Arquivo de configuração TOML: `payload_size_threshold = <bytes>` na seção `[gateway]`
- Padrão se não especificado: 524288 bytes (512KB)

**Requisitos**:
- O limite MUST ser um número inteiro positivo representando bytes
- O gateway MUST comparar o tamanho real do payload com o limite antes de decidir o método de armazenamento
- O limite MAY ser ajustado com base nas necessidades de implantação (trade-offs de memória vs I/O de disco)

#### 4.1.3.4 Configuração de Identidade de Bot Confiável

O campo opcional `trustedBots` na configuração do gateway passa uma lista adicional de strings de identidade de bot do GitHub para o gateway. O gateway mescla essa lista com sua própria lista de identidade confiável embutida para formar o conjunto efetivo de identidades que reconhece.

> **Importante**: `trustedBots` é **aditivo**. O gateway mantém sua própria lista interna de identidades de bot confiáveis. O campo `trustedBots` estende essa lista interna com identidades adicionais; ele não pode remover ou sobrescrever as identidades confiáveis embutidas do gateway.

**Exemplo de Configuração**:

```json
{
  "gateway": {
    "port": 8080,
    "domain": "localhost",
    "apiKey": "${MCP_GATEWAY_API_KEY}",
    "trustedBots": [
      "github-actions[bot]",
      "copilot-swe-agent[bot]"
    ]
  }
}
```

**Exemplo de Frontmatter** (autor do fluxo de trabalho):

```yaml
sandbox:
  mcp:
    trusted-bots:
      - github-actions[bot]
      - copilot-swe-agent[bot]
```

**Requisitos**:
- `trustedBots` MUST ser um array de strings não vazio quando presente
- Cada entrada MUST ser uma string não vazia (tipicamente um nome de usuário do GitHub como `github-actions[bot]`)
- Entradas de `trustedBots` são **mescladas** com as identidades confiáveis embutidas do gateway para formar a lista efetiva passada ao gateway
- `trustedBots` NÃO DEVEM ser usados para remover ou sobrescrever entradas na lista de identidades confiáveis embutidas do gateway

**Teste de Conformidade**: T-AUTH-006 - Configuração de Identidade de Bot Confiável

#### 4.1.3.5 Configuração de Intervalo Keepalive

O campo opcional `keepaliveInterval` na configuração do gateway controla com que frequência o gateway envia pings de keepalive periódicos para backends MCP HTTP. Isso evita a expiração de sessão inativa durante tarefas de agente de longa duração.

| Valor | Comportamento |
|-------|----------|
| Não definido / `0` | Padrão do gateway: 1500 segundos (25 minutos) |
| `> 0` | Intervalo keepalive personalizado em segundos |
| `-1` | Desabilitar pings keepalive inteiramente |

**Exemplo de configuração (JSON)**:

```json
{
  "gateway": {
    "port": 8080,
    "domain": "localhost",
    "apiKey": "${MCP_GATEWAY_API_KEY}",
    "keepaliveInterval": 300
  }
}
```

**Frontmatter do fluxo de trabalho** (via `sandbox.mcp.keepalive-interval`):

```yaml
sandbox:
  mcp:
    keepalive-interval: 300   # keepalive de 5 minutos para backends com timeouts de inatividade curtos
```

**Regras de conformidade**:

- `keepaliveInterval` MUST ser um inteiro quando presente
- Um valor de `0` é tratado como não definido pelo gateway (silenciosamente assume o padrão de 1500 segundos)
- Um valor de `-1` desabilita pings keepalive inteiramente
- Qualquer inteiro positivo define o intervalo keepalive em segundos

#### 4.1.3.6 Configuração de Timeout de Sessão

O campo opcional `sessionTimeout` na configuração do gateway controla por quanto tempo sessões MCP com estado sobrevivem em ambos os modos unificado e roteado.

| Valor | Comportamento |
|-------|----------|
| Não definido / `""` | Padrão do gateway: 6 horas (ou variável de ambiente `MCP_GATEWAY_SESSION_TIMEOUT`) |
| String de duração Go | Tempo de vida da sessão personalizado (ex: `"30m"`, `"4h"`, `"6h"`, `"12h"`) |

**Precedência**: `sessionTimeout` no JSON de configuração stdin **>** variável de ambiente `MCP_GATEWAY_SESSION_TIMEOUT` **>** padrão embutido do gateway (6h).

**Exemplo de configuração (JSON)**:

```json
{
  "gateway": {
    "port": 8080,
    "domain": "localhost",
    "apiKey": "${MCP_GATEWAY_API_KEY}",
    "sessionTimeout": "4h"
  }
}
```

**Frontmatter do fluxo de trabalho** (via `engine.mcp.session-timeout`):

```yaml
engine:
  id: copilot
  mcp:
    session-timeout: 4h   # sessões de 4 horas para migrações de longa duração
```

**Regras de conformidade**:

- `sessionTimeout` MUST ser uma string de duração Go válida quando presente (ex: `"30m"`, `"4h"`)
- O compilador de fluxo de trabalho impõe um mínimo de `5m` para valores especificados pelo autor (sem limite superior)
- Operadores de infraestrutura PODEM definir `MCP_GATEWAY_SESSION_TIMEOUT` no container do gateway para substituir o padrão para todos os fluxos de trabalho; um `sessionTimeout` por fluxo de trabalho na configuração JSON stdin tem precedência
- Quando não definido, o gateway usa seu padrão embutido (6h)

#### 4.1.3.7 Configuração OpenTelemetry

O objeto opcional `opentelemetry` na configuração do gateway habilita o gateway a emitir eventos de rastreamento distribuído para chamadas MCP usando o padrão [OpenTelemetry](https://opentelemetry.io/). Quando configurado, o gateway cria spans para cada invocação de ferramenta MCP e os exporta para o endpoint do coletor designado.

**Campos de Configuração**:

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|----------|-------------|
| `endpoint` | string | Sim (quando `opentelemetry` está presente) | URL do endpoint OTLP/HTTP para o coletor OpenTelemetry (ex: `https://collector.example.com:4318/v1/traces`). MUST usar HTTPS. Suporta expressões variáveis. |
| `traceId` | string | Não | ID de rastreamento pai para propagação de contexto. Quando definido, o gateway anexa todos os spans emitidos como filhos deste rastreamento, permitindo correlação com um rastreamento distribuído existente. MUST ser uma string hexadecimal minúscula de 32 caracteres (formato de ID de rastreamento W3C de 128 bits). Suporta expressões variáveis. |
| `spanId` | string | Não | ID de span pai para propagação de contexto. Quando definido junto com `traceId`, o gateway define este span como pai direto do seu span raiz. MUST ser uma string hexadecimal minúscula de 16 caracteres (formato de ID de span W3C de 64 bits). Ignorado quando `traceId` não está definido. Suporta expressões variáveis. |
| `serviceName` | string | Não | Nome de serviço lógico relatado no atributo de recurso `service.name` de todos os spans emitidos. Identifica o gateway no backend de rastreamento. Padrão para `"mcp-gateway"` quando não especificado. |

> [!NOTE]
> Cabeçalhos de autenticação (ex: `Authorization: Bearer <token>`) para o coletor OTLP DEVEM ser fornecidos via variável de ambiente `OTEL_EXPORTER_OTLP_HEADERS`, não por meio da configuração JSON. Isso segue a [convenção de variável de ambiente do SDK OTel](https://opentelemetry.io/docs/specs/otel/protocol/exporter/#configuration-options) padrão e mantém as credenciais fora do pipe de configuração JSON stdin. O formato é uma lista de pares `chave=valor` separados por vírgula (ex: `Authorization=Bearer meu-token,X-Custom=valor`) conforme definido pela [especificação do exportador OTLP do OpenTelemetry](https://opentelemetry.io/docs/specs/otel/protocol/exporter/#configuration-options). Quando o gh-aw compila um fluxo de trabalho com `observability.otlp.headers`, o valor é encaminhado automaticamente para o container do gateway via `-e OTEL_EXPORTER_OTLP_HEADERS`.

**Exemplo de Configuração**:

```json
{
  "gateway": {
    "port": 8080,
    "domain": "localhost",
    "apiKey": "${MCP_GATEWAY_API_KEY}",
    "opentelemetry": {
      "endpoint": "https://collector.example.com:4318/v1/traces",
      "serviceName": "my-mcp-gateway"
    }
  }
}
```

**Comportamento de Rastreamento**:

Quando `opentelemetry` é configurado, o gateway MUST:

1. Criar um span raiz para o tempo de vida do processo do gateway com `service.name` definido como o `serviceName` configurado
2. Criar um span filho para cada invocação de ferramenta MCP com os seguintes atributos:
   - `mcp.server`: o nome do servidor conforme configurado em `mcpServers`
   - `mcp.method`: o nome do método JSON-RPC (ex: `tools/call`)
   - `mcp.tool`: o nome da ferramenta quando o método é `tools/call`
   - `http.status_code`: o código de status HTTP da resposta proxy
3. Registrar timestamps de início e fim de span com precisão
4. Exportar spans concluídos para o `endpoint` configurado usando o protocolo OTLP/HTTP
5. Aplicar quaisquer cabeçalhos de `OTEL_EXPORTER_OTLP_HEADERS` (quando definidos) a cada solicitação de exportação
6. Propagar contexto W3C `traceparent` quando `traceId` e `spanId` forem fornecidos

Quando `traceId` é fornecido, o gateway MUST construir um cabeçalho W3C `traceparent` válido e usá-lo como o contexto pai para o span raiz. O campo de flags de rastreamento SHOULD ser definido como `01` (amostrado) quando o gateway não tiver decisão de amostragem upstream disponível; implementações PODEM propagar flags de amostragem upstream quando estiverem disponíveis. Quando apenas `traceId` é fornecido sem `spanId`, o gateway MUST gerar um `spanId` aleatório para o cabeçalho `traceparent`.

**Tratamento de Falha**:

O gateway NÃO DEVE falhar ao iniciar se o endpoint do coletor OpenTelemetry estiver inacessível. Falhas de exportação SHOULD ser registradas como avisos e NÃO DEVEM afetar o processamento de solicitações MCP. O gateway SHOULD implementar uma estratégia de nova tentativa com back-off exponencial para exportações falhas.

**Requisitos**:

- `endpoint` MUST estar presente quando o objeto `opentelemetry` for configurado
- `endpoint` MUST ser uma URL HTTPS
- `traceId`, quando fornecido, MUST ser uma string hexadecimal minúscula de 32 caracteres
- `spanId`, quando fornecido, MUST ser uma string hexadecimal minúscula de 16 caracteres
- `spanId` SHOULD ser definido apenas quando `traceId` também estiver definido; se `spanId` for fornecido sem `traceId`, o gateway SHOULD registrar um aviso e ignorar `spanId`
- Falhas de exportação NÃO DEVEM propagar erros para clientes MCP
- Cabeçalhos de autenticação DEVEM ser fornecidos via variável de ambiente `OTEL_EXPORTER_OTLP_HEADERS`; o campo `headers` não é mais aceito na configuração JSON

**Teste de Conformidade**: T-OTEL-001 até T-OTEL-010 (Seção 11.1.10)

#### 4.1.3a Campos de Configuração de Nível Superior

Os seguintes campos PODEM ser especificados no nível superior da configuração:

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|----------|-------------|
| `customSchemas` | objeto | Não | Mapa de nomes de tipo de servidor personalizados para URLs JSON Schema para validação. Veja Seção 4.1.4 para detalhes. |

#### 4.1.4 Tipos de Servidor Personalizados

O gateway PODE suportar tipos de servidor personalizados além dos tipos padrão "stdio" e "http". Tipos de servidor personalizados permitem extensibilidade para implementações de servidor MCP especializadas com requisitos de configuração adicionais.

**Mecanismo de Registro**:

Tipos de servidor personalizados DEVEM ser registrados no campo `customSchemas` no nível superior da configuração, que mapeia nomes de tipo para URLs JSON Schema:

```json
{
  "mcpServers": {
    "my-custom-server": {
      "type": "safeinputs"
    }
  },
  "gateway": {
    "port": 8080,
    "domain": "localhost",
    "apiKey": "secret"
  },
  "customSchemas": {
    "safeinputs": "https://docs.github.com/gh-aw/schemas/mcp-scripts-config.schema.json"
  }
}
```

**Comportamento de Validação**:

Quando uma configuração de servidor inclui um campo `type` com um valor não em `["stdio", "http"]`:

1. O gateway MUST verificar se o tipo está registrado em `customSchemas`
2. Se registrado com uma URL HTTPS, o gateway MUST buscar e aplicar o JSON Schema correspondente para validação
3. Se registrado com uma string vazia, o gateway MUST pular a validação de esquema para esse tipo
4. Se não registrado, o gateway MUST rejeitar a configuração com um erro indicando o tipo desconhecido
5. Schemas personalizados DEVEM ser JSON Schema Draft 7 ou posterior válido
6. Schemas personalizados PODEM estender campos de configuração de servidor base

**Exemplo com Tipo Personalizado**:

```json
{
  "mcpServers": {
    "my-custom-server": {
      "type": "safeinputs",
      "tools": {
        "greet": {
          "description": "Cumprimentar usuário",
          "script": "return { message: 'Hello!' };"
        }
      }
    }
  },
  "gateway": {
    "port": 8080,
    "domain": "localhost",
    "apiKey": "secret"
  },
  "customSchemas": {
    "safeinputs": "https://docs.github.com/gh-aw/schemas/mcp-scripts-config.schema.json"
  }
}
```

**Requisitos**:

- Tipos personalizados NÃO DEVEM entrar em conflito com tipos reservados ("stdio", "http")
- URLs de schema personalizado DEVEM ser apenas URLs HTTPS (por razões de segurança)
- URLs de schema personalizado PODEM ser strings vazias para pular validação
- Implementações SHOULD armazenar em cache schemas buscados para desempenho
- Falhas na busca de schema DEVEM resultar em erros de validação de configuração
- Configurações de servidor personalizado DEVEM validar em relação aos seus schemas registrados quando uma URL de schema for fornecida

#### 4.1.5 Montagens de Volume para Servidores Stdio

Servidores MCP (containerizados) stdio PODEM especificar montagens de volume para fornecer acesso a caminhos do sistema de arquivos host. Montagens de volume permitem que servidores leiam arquivos de configuração, acessem diretórios de dados ou gravem arquivos de saída mantendo o isolamento do container.

**Formato de Montagem**:

Montagens de volume DEVEM usar o formato:

```
"host:container:mode"
```

Onde:
- **host**: Caminho absoluto no sistema de arquivos do host
- **container**: Caminho absoluto dentro do container
- **mode**: Modo de acesso, ou "ro" (somente leitura) ou "rw" (leitura e escrita)

**Exemplo de Configuração**:

```json
{
  "mcpServers": {
    "data-processor": {
      "container": "ghcr.io/example/data-mcp:latest",
      "type": "stdio",
      "mounts": [
        "/var/data/input:/app/input:ro",
        "/var/data/output:/app/output:rw",
        "/etc/config/app.json:/app/config.json:ro"
      ]
    }
  }
}
```

**Requisitos**:

- O campo `mounts` MUST ser especificado apenas para servidores stdio (servidores com `type: "stdio"` ou servidores sem um tipo explícito, já que stdio é o padrão)
- Cada string de montagem MUST estar em conformidade com o formato "host:container:mode"
- O caminho do host MUST ser um caminho absoluto
- O caminho do container MUST ser um caminho absoluto
- O modo MUST ser "ro" (somente leitura) ou "rw" (leitura e escrita)
- O gateway MUST validar o formato da montagem durante a análise da configuração
- Formatos de montagem inválidos DEVEM resultar em erros de validação de configuração

**Considerações de Segurança**:

- Montagens somente leitura ("ro") SHOULD ser preferidas quando o servidor só precisa ler dados
- Montagens de leitura e escrita ("rw") SHOULD ser limitadas a diretórios específicos necessários para saída
- Implementações SHOULD documentar quaisquer restrições em caminhos de host (ex: não permitir diretórios do sistema)
- Montagens de volume fornecem acesso ao sistema de arquivos do host enquanto mantêm o isolamento do processo do container

**Casos de Uso**:

1. **Arquivos de Configuração**: Montar arquivos de configuração somente leitura em containers
   ```json
   "mounts": ["/etc/app/config.yaml:/app/config.yaml:ro"]
   ```

2. **Diretórios de Dados**: Fornecer acesso a grandes datasets sem copiar para containers
   ```json
   "mounts": ["/var/data/corpus:/data:ro"]
   ```

3. **Diretórios de Saída**: Permitir que containers gravem resultados no sistema de arquivos do host
   ```json
   "mounts": ["/var/output:/results:rw"]
   ```

4. **Cache Compartilhado**: Compartilhar diretórios de cache entre container e host
   ```json
   "mounts": ["/tmp/cache:/app/cache:rw"]
   ```

### 4.2 Renderização de Expressão Variável

#### 4.2.1 Sintaxe

Valores de configuração PODEM conter expressões variáveis com a sintaxe:

```
"${VARIABLE_NAME}"
```

#### 4.2.2 Comportamento de Resolução

O gateway MUST:

1. Detectar expressões variáveis em valores de configuração
2. Substituir expressões por valores de variáveis de ambiente de processo
3. FALHAR IMEDIATAMENTE se uma variável referenciada não estiver definida
4. Registrar o nome da variável indefinida para stdout como payload de erro
5. Sair com código de status diferente de zero

#### 4.2.3 Exemplo

Configuração:

```json
{
  "mcpServers": {
    "github": {
      "container": "ghcr.io/github/github-mcp-server:latest",
      "env": {
        "GITHUB_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

Se `GITHUB_PERSONAL_ACCESS_TOKEN` não estiver definido no ambiente:

```
Erro: variável de ambiente não definida referenciada: GITHUB_PERSONAL_ACCESS_TOKEN
Requerido por: mcpServers.github.env.GITHUB_TOKEN
```

### 4.3 Validação de Configuração

#### 4.3.1 Funcionalidades Desconhecidas

O gateway MUST rejeitar configurações contendo campos não reconhecidos no nível superior com uma mensagem de erro indicando:

- O nome do campo não reconhecido
- A localização na configuração
- Uma sugestão para verificar a versão da especificação

#### 4.3.2 Validação de Esquema

O gateway MUST validar:

- Campos obrigatórios estão presentes
- Tipos de campo correspondem aos tipos esperados
- Restrições de valor são satisfeitas (ex: faixas de porta)
- Campos mutuamente exclusivos não estão ambos presentes

#### 4.3.3 Requisitos de Fail-Fast

Se a configuração for inválida, o gateway MUST:

1. Escrever mensagem de erro detalhada para stdout como um payload de erro incluindo:
   - O erro de validação específico
   - A localização na configuração (caminho JSON)
   - Ação corretiva sugerida
2. Sair com código de status 1
3. NÃO iniciar o servidor HTTP
4. NÃO inicializar nenhum servidor MCP

---

## 5. Comportamento do Protocolo

Para detalhes completos sobre o Model Context Protocol, veja a [Especificação do Protocolo de Contexto do Modelo](https://spec.modelcontextprotocol.io/).

### 5.1 Interface do Servidor HTTP

#### 5.1.1 Estrutura de Endpoint

O gateway MUST expor os seguintes endpoints HTTP:

```
POST /mcp/{server-name}
GET  /health
POST /close
```

#### 5.1.2 Comportamento do Endpoint RPC

**Formato da Solicitação**:

```http
POST /mcp/{server-name} HTTP/1.1
Content-Type: application/json
Authorization: <apiKey>

{
  "jsonrpc": "2.0",
  "method": "string",
  "params": {},
  "id": "string|number"
}
```

**Nota**: O formato do cabeçalho `Authorization` é dependente da implementação. Consulte a documentação da implementação do seu gateway para o formato esperado.

**Formato da Resposta**:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "result": {},
  "id": "string|number"
}
```

**Resposta de Erro**:

```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Internal error",
    "data": {}
  },
  "id": "string|number"
}
```

#### 5.1.3 Comportamento do Endpoint Close

O gateway MUST fornecer um endpoint `/close` para desligamento gracioso e limpeza de recursos.

**Formato da Solicitação**:

```http
POST /close HTTP/1.1
Authorization: <apiKey>
```

**Nota**: O formato do cabeçalho `Authorization` é dependente da implementação. Consulte a documentação da implementação do seu gateway para o formato esperado.

**Resposta de Sucesso**:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "closed",
  "message": "Gateway shutdown initiated",
  "serversTerminated": 3
}
```

**Resposta de Já Fechado**:

```http
HTTP/1.1 410 Gone
Content-Type: application/json

{
  "error": "Gateway has already been closed"
}
```

**Requisitos de Comportamento**:

O gateway MUST realizar as seguintes ações quando o endpoint `/close` for chamado:

1. **Parar de Aceitar Novas Solicitações**: Rejeitar imediatamente quaisquer novas solicitações RPC para endpoints `/mcp/{server-name}` com HTTP 503 Service Unavailable
2. **Completar Solicitações em Trânsito**: Permitir que solicitações atualmente sendo processadas sejam concluídas (com um timeout razoável, ex: 30 segundos)
3. **Encerrar Todos os Containers**: Parar todos os containers de servidor MCP em execução:
   - Enviar SIGTERM para cada processo de container
   - Aguardar até 10 segundos para desligamento gracioso
   - Enviar SIGKILL se o container não parar dentro do timeout
   - Registrar o status de término para cada servidor
4. **Liberar Recursos**:
   - Fechar todos os descritores de arquivo e sockets de rede
   - Limpar arquivos temporários e logs
   - Liberar montagens de volume
   - Liberar memória alocada
5. **Retornar Resposta**: Enviar resposta de sucesso antes que o processo saia
6. **Sair do Processo**: Sair do processo do gateway com código de status 0

**Idempotência**:

O endpoint `/close` MUST ser idempotente:
- Primeira chamada: Inicia desligamento e retorna HTTP 200
- Chamadas subsequentes: Retorna HTTP 410 Gone indicando que o gateway já está fechado

**Autenticação**:

O endpoint `/close` MUST exigir autenticação quando `gateway.apiKey` estiver configurado. Solicitações sem autenticação válida DEVEM ser rejeitadas com HTTP 401 Unauthorized.

#### 5.1.4 Roteamento de Solicitação

O gateway MUST:

1. Extrair nome do servidor do caminho da URL
2. Validar se o servidor existe na configuração
3. Rotear solicitação para o servidor backend apropriado
4. Traduzir protocolos se necessário (stdio ↔ HTTP)
5. Retornar resposta para o cliente

### 5.2 Tradução de Protocolo

#### 5.2.1 Stdio (Containerizado) para HTTP

Para servidores stdio containerizados, o gateway MUST:

1. Iniciar o container na primeira solicitação (inicialização lazy)
2. Gravar solicitação JSON-RPC no stdin do container
3. Ler resposta JSON-RPC do stdout do container
4. Retornar resposta HTTP ao cliente
5. Manter container para solicitações subsequentes
6. Bufferizar respostas parciais até que o JSON completo seja recebido

O gateway SHALL NOT suportar execução de comando não containerizada. Todos os servidores stdio DEVEM ser containerizados.

#### 5.2.2 HTTP para HTTP

Para servidores baseados em HTTP, o gateway MUST:

1. Encaminhar a solicitação JSON-RPC para a URL do servidor
2. Aplicar quaisquer cabeçalhos ou autenticação configurados
3. Retornar a resposta do servidor para o cliente
4. Lidar com erros de nível HTTP apropriadamente

**Manipulação de Falha de Conexão**:

Quando uma conexão com um servidor MCP baseado em HTTP falha, o gateway MUST:

1. **Passar adiante o erro**: Retornar uma resposta de erro apropriada ao cliente indicando que o servidor não está disponível (ex: HTTP 503 Service Unavailable ou erro JSON-RPC -32001 "Server unavailable")
2. **Lidar com fallback**: Implementar um mecanismo de fallback (ex: lógica de nova tentativa, servidor alternativo, resposta em cache) e retornar um resultado para o cliente

O gateway NÃO DEVE ignorar silenciosamente falhas de conexão. Todas as falhas de conexão DEVEM resultar em uma resposta de erro para o cliente ou tratamento bem-sucedido de fallback.

#### 5.2.3 Preservação de Assinatura de Ferramenta

O gateway SHOULD NOT modificar:

- Nomes de ferramenta
- Parâmetros de ferramenta
- Valores de retorno de ferramenta
- Assinaturas de método

Isso garante proxy transparente sem mangling de nome ou transformação de esquema.

### 5.3 Manipulação de Timeout

#### 5.3.1 Timeout de Inicialização

O gateway SHOULD aplicar `startupTimeout` para inicialização do servidor:

1. Iniciar timer quando o container do servidor for iniciado
2. Aguardar sinal de pronto do servidor (stdio) ou verificação de integridade bem-sucedida (HTTP)
3. Se o timeout expirar, encerrar o container do servidor e retornar erro
4. Registrar erro de timeout com nome do servidor e tempo decorrido

#### 5.3.2 Timeout de Ferramenta

O gateway SHOULD aplicar `toolTimeout` para invocações de ferramenta individuais:

1. Iniciar timer quando a solicitação RPC for enviada para o servidor
2. Aguardar resposta completa
3. Se o timeout expirar, retornar erro de timeout para o cliente
4. Registrar timeout com nome do servidor, método e tempo decorrido

### 5.4 Saída de Configuração Stdout

Após inicialização bem-sucedida, o gateway MUST:

1. Gravar uma configuração completa de servidor MCP para stdout
2. Incluir detalhes de conexão do gateway para cada servidor MCP configurado:
   - `type`: MUST ser definido como "http"
   - `url`: MUST ser a URL do gateway no formato "http://{domain}:{port}/mcp/{server-name}"
   - `headers`: SHOULD incluir cabeçalhos de autorização necessários para se conectar ao gateway
     - `Authorization`: Contém as credenciais de autenticação em um formato dependente da implementação
   - `tools`: MAY ser incluído para especificar filtros de ferramenta da configuração original
   
   Exemplo de configuração de saída:
   ```json
   {
     "mcpServers": {
       "server-name": {
         "type": "http",
         "url": "http://{domain}:{port}/mcp/server-name",
         "headers": {
           "Authorization": "{apiKey}"
         },
         "tools": ["*"]
       }
     }
   }
   ```
   
   O objeto `headers` SHOULD estar presente em cada configuração de servidor quando a autenticação for necessária. O gateway é responsável por gerar e incluir credenciais de autenticação apropriadas. O formato específico de cabeçalhos de autenticação é dependente da implementação.
   
   O campo `tools` MAY ser incluído na configuração de saída para preservar a filtragem de ferramenta da configuração de entrada. Quando presente, especifica quais ferramentas são permitidas para o servidor (`["*"]` para todas as ferramentas, ou uma lista de nomes de ferramenta específicos).

3. Gravar configuração como um único documento JSON
4. Limpar buffer de stdout
5. Continuar atendendo solicitações

Isso permite que clientes descubram dinamicamente endpoints de gateway e credenciais de autenticação.

---

## 6. Isolamento de Servidor

### 6.1 Isolamento de Container

Para servidores stdio, o gateway MUST:

1. Iniciar cada servidor em um container separado
2. Manter fluxos de stdin/stdout/stderr isolados
3. Impedir comunicação entre containers
4. Encerrar containers no desligamento do gateway (via endpoint `/close` ou término de processo)
5. Aplicar montagens de volume conforme configurado no campo `mounts` do servidor (Seção 4.1.5)

Todos os servidores MCP baseados em stdio DEVEM ser containerizados para garantir:

- **Isolamento de Processo**: Cada container fornece um namespace de processo separado
- **Isolamento de Recurso**: Containers impõem limites de CPU, memória e sistema de arquivos
- **Isolamento de Rede**: Containers fornecem namespaces de rede isolados
- **Limites de Segurança**: Runtimes de container impõem políticas de segurança e capacidades
- **Isolamento de Sistema de Arquivos**: Sistemas de arquivos de container são isolados, com acesso controlado a caminhos do host via montagens de volume

O gateway SHALL NOT suportar execução de processo não containerizado para servidores stdio.

**Isolamento de Montagem de Volume**:

Quando montagens de volume são configuradas (Seção 4.1.5):

- O gateway MUST montar os caminhos de host especificados no container nos caminhos de container configurados
- O gateway MUST aplicar o modo de acesso especificado ("ro" somente leitura ou "rw" leitura e escrita)
- As montagens de cada container DEVEM ser independentes; montagens configuradas para um servidor NÃO DEVEM afetar outros servidores
- Montagens de volume fornecem acesso controlado ao sistema de arquivos do host enquanto mantêm o isolamento do processo do container
- O gateway MUST validar caminhos e modos de montagem antes da inicialização do container

### 6.2 Isolamento de Recurso

O gateway MUST garantir:

- Cada servidor tem variáveis de ambiente isoladas dentro de seu container
- Descritores de arquivo não são compartilhados entre containers
- Sockets de rede não são compartilhados (para servidores HTTP)
- Falhas de container não afetam outros containers

### 6.3 Limites de Segurança

O gateway NÃO DEVE:

- Permitir que servidores acessem a configuração uns dos outros
- Compartilhar credenciais de autenticação entre servidores
- Expor detalhes de implementação de servidor para clientes
- Permitir invocações de ferramenta entre servidores

---

## 7. Autenticação

### 7.1 Formato do Cabeçalho de Autorização

O Gateway MCP usa um esquema simples de autenticação por chave de API. Quando `gateway.apiKey` está configurado:

- O cabeçalho `Authorization` contém o valor da chave de API
- Implementações PODEM usar formatos diferentes (ex: valor direto ou esquema Bearer)
- O formato específico é dependente da implementação

> [!WARNING]
> A chave de API do gateway não deve ser tratada como um bloqueio seguro contra código já executando dentro do container do agente. Um agente suficientemente capaz pode extraí-la do estado de processo em memória ou outros canais de runtime. Trate esta chave como vazada por design e confie no isolamento de container, controles de rede e limites de permissão em estágios para defesa em profundidade.

**Exemplos de formatos**:

```http
Authorization: my-secret-api-key-12345
```

ou

```http
Authorization: Bearer my-secret-api-key-12345
```

Este esquema de autenticação oferece flexibilidade para diferentes requisitos de implementação.

### 7.2 Autenticação por Chave de API

Quando `gateway.apiKey` está configurado, o gateway MUST:

1. Exigir cabeçalho `Authorization` em todas as solicitações RPC para endpoints `/mcp/{server-name}` e `/close`
   - O formato específico do cabeçalho Authorization é dependente da implementação
   - Implementações SHOULD documentar o formato esperado
2. Rejeitar solicitações com tokens ausentes ou inválidos (HTTP 401)
3. Rejeitar solicitações com cabeçalhos Authorization malformados (HTTP 400)
4. NÃO registrar chaves de API em texto simples

### 7.3 Chave de API Temporária Ideal

O gateway SHOULD suportar chaves de API temporárias:

1. Gerar uma chave de API aleatória na inicialização se não fornecida
2. Incluir a chave na saída de configuração stdout

### 7.4 Isenções de Autenticação

Os seguintes endpoints NÃO DEVEM exigir autenticação:

- `/health`

### 7.5 Configuração de Identidade de Bot Confiável

O campo `gateway.trustedBots` permite que autores de fluxo de trabalho passem strings de identidade de bot adicionais do GitHub para o gateway por meio do arquivo de configuração do gateway gerado. O gateway mescla estas entradas com sua própria lista de identidade confiável embutida.

`gateway.trustedBots` é **aditivo** — ele estende a lista embutida do gateway, mas não pode remover entradas dela.

Autores de fluxo de trabalho definem isso via campo de frontmatter `sandbox.mcp.trusted-bots`; o compilador o traduz para a array `trustedBots` na seção `gateway` gerada do arquivo de configuração MCP.

---

### 7.6 Autenticação Upstream (OIDC)

Servidores MCP HTTP PODEM configurar autenticação upstream usando o campo `auth`. Quando presente, o gateway adquire tokens dinamicamente e os injeta como cabeçalhos `Authorization: Bearer` em cada solicitação de saída para o servidor.

#### 7.6.1 OIDC do GitHub Actions

Quando `auth.type` é `"github-oidc"`, o gateway adquire JWTs de curta duração do endpoint OIDC do GitHub Actions. Isso requer que o fluxo de trabalho tenha `permissions: { id-token: write }`.

**Configuração**:

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|----------|-------------|
| `type` | string | Sim | Deve ser `"github-oidc"` |
| `audience` | string | Não | O público-alvo pretendido (claim `aud`) para o token OIDC. Padrão para a `url` do servidor se omitido. |

**Variáveis de Ambiente** (definidas automaticamente pelo GitHub Actions):

| Variável | Descrição |
|----------|-------------|
| `ACTIONS_ID_TOKEN_REQUEST_URL` | URL do endpoint de token OIDC |
| `ACTIONS_ID_TOKEN_REQUEST_TOKEN` | Token Bearer para autenticação no endpoint OIDC |

**Comportamento**:

1. Na inicialização, o gateway verifica `ACTIONS_ID_TOKEN_REQUEST_URL`. Se definido, um provedor OIDC é inicializado.
2. Se um servidor tiver `auth.type: "github-oidc"`, mas as variáveis de ambiente OIDC estiverem ausentes, o gateway MUST registrar um erro na inicialização e MUST retornar um erro quando o servidor for acessado pela primeira vez.
3. Tokens são armazenados em cache por público e atualizados proativamente antes da expiração (margem de 60 segundos).
4. O cabeçalho OIDC `Authorization: Bearer` sobrescreve qualquer cabeçalho `Authorization` estático do campo `headers`. Outros cabeçalhos estáticos passam normalmente.
5. O gateway NÃO verifica assinaturas JWT — ele atua como um adquirente/encaminhador de token. O servidor MCP downstream é a parte confiável e MUST validar o token.

**Exemplo** (formato stdin JSON):

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "type": "http",
      "url": "https://my-server.example.com/mcp",
      "auth": {
        "type": "github-oidc",
        "audience": "https://my-server.example.com"
      }
    }
  }
}
```

**Exemplo com público padronizado para URL**:

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "type": "http",
      "url": "https://my-server.example.com/mcp",
      "auth": {
        "type": "github-oidc"
      }
    }
  }
}
```

Neste caso, o público padrão é `"https://my-server.example.com/mcp"`.

**Exemplo de Frontmatter** (autor do fluxo de trabalho):

```yaml
tools:
  mcp-servers:
    my-mcp-server:
      type: http
      url: "https://my-server.example.com/mcp"
      auth:
        type: github-oidc
        audience: "https://my-server.example.com"
```

#### 7.6.2 Interação com Cabeçalhos Estáticos

Quando `headers` e `auth` estão configurados:

- Cabeçalhos estáticos de `headers` são aplicados primeiro
- O token OIDC sobrescreve o cabeçalho `Authorization`
- Todos os outros cabeçalhos estáticos (ex: `X-Custom-Header`) passam inalterados

Isso permite combinar autenticação OIDC com cabeçalhos sem autenticação:

```json
{
  "type": "http",
  "url": "https://my-server.example.com/mcp",
  "headers": {
    "X-Custom-Header": "custom-value"
  },
  "auth": {
    "type": "github-oidc"
  }
}
```

#### 7.6.3 Regras de Validação

- `auth` é válido apenas em servidores HTTP (`type: "http"`). Servidores stdio com `auth` DEVEM ser rejeitados com um erro de validação.
- `auth.type` é obrigatório quando `auth` está presente. Tipo vazio MUST ser rejeitado.
- Valores de `auth.type` não suportados DEVEM ser rejeitados com um erro descritivo.

---

## 8. Monitoramento de Integridade

### 8.1 Endpoints de Monitoramento de Integridade

#### 8.1.1 Integridade Geral (`/health`)

```http
GET /health HTTP/1.1
```

**Formato da Resposta**:

```json
{
  "status": "healthy" | "unhealthy",
  "specVersion": "string",
  "gatewayVersion": "string",
  "servers": {
    "server-name": {
      "status": "running" | "stopped" | "error",
      "uptime": 12345
    }
  }
}
```

**Campos da Resposta**:

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|----------|-------------|
| `status` | string | Sim | Status de integridade geral do gateway: "healthy" ou "unhealthy" |
| `specVersion` | string | Sim | Versão da Especificação do Gateway MCP (ex: "1.3.0") |
| `gatewayVersion` | string | Sim | Versão da implementação do gateway (ex: "0.1.0") |
| `servers` | objeto | Sim | Mapa de nomes de servidor para seu status de integridade |
| `servers[name].status` | string | Sim | Status do servidor: "running", "stopped" ou "error" |
| `servers[name].uptime` | inteiro | Não | Uptime do servidor em segundos |

**Requisitos**:

O gateway MUST incluir as seguintes informações de versão na resposta do endpoint `/health`:

1. **`specVersion`**: A versão desta Especificação de Gateway MCP à qual a implementação está em conformidade. Este campo MUST usar versionamento semântico (formato MAIOR.MENOR.PATCH).
2. **`gatewayVersion`**: A versão da própria implementação do gateway. Este campo MUST usar versionamento semântico e representa a versão específica de build ou release do software do gateway.

Esses campos de versão permitem que clientes:
- Verifiquem a compatibilidade da especificação
- Detectem versões de implementação para depuração
- Rastreadam versões de implantação entre ambientes
- Garantam a disponibilidade de recursos com base na versão da especificação

### 8.2 Comportamento de Verificação de Integridade

O gateway SHOULD:

1. Verificar periodicamente a integridade do servidor (a cada 30 segundos)
2. Reiniciar servidores stdio containerizados com falha automaticamente
3. Marcar servidores HTTP como insalubres se inacessíveis
4. Incluir status de integridade na resposta `/health`
5. Atualizar prontidão com base no status do servidor crítico

> [!TIP]
> Para inspecionar a integridade do servidor MCP para uma execução de fluxo de trabalho específica em tempo de execução, use `gh aw audit <run-id>`. A seção **MCP Server Health** do relatório de auditoria mostra falhas de conexão, erros de timeout, contagens de chamadas de ferramenta e taxas de erro por servidor — fornecendo uma visão pós-execução do comportamento do gateway. Para falhas recorrentes de MCP, passe dois IDs de execução para `gh aw audit` (ex: `gh aw audit <base-id> <compare-id>`) para comparar o uso de ferramenta MCP entre execuções e identificar regressões. Veja [Comandos de Auditoria](/gh-aw/reference/audit/).

---

## 9. Tratamento de Erros

### 9.1 Falhas de Inicialização

Se qualquer servidor configurado falhar ao iniciar, o gateway MUST:

1. Escrever erro detalhado para stdout como um payload de erro incluindo:
   - Nome do servidor
   - Imagem do container ou URL tentada
   - Mensagem de erro do container do servidor
   - Status da variável de ambiente
   - Stdout/stderr do container falho
2. Sair com código de status 1
3. NÃO iniciar o servidor HTTP

### 9.2 Erros de Runtime

Para erros de runtime, o gateway MUST:

1. Registrar erros para stdout como payloads de erro com:
   - Timestamp
   - Nome do servidor
   - ID da solicitação
   - Detalhes do erro
2. Retornar resposta de erro JSON-RPC ao cliente
3. Continuar atendendo outras solicitações
4. Tentar reiniciar servidores stdio containerizados com falha

### 9.3 Formato de Resposta de Erro

Erros JSON-RPC DEVEM seguir esta estrutura:

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "Server error",
    "data": {
      "server": "server-name",
      "detail": "Informações de erro específicas"
    }
  },
  "id": "request-id"
}
```

Códigos de erro:

- `-32700`: Erro de análise
- `-32600`: Solicitação inválida
- `-32601`: Método não encontrado
- `-32603`: Erro interno
- `-32000` a `-32099`: Erros do servidor

### 9.4 Degradação Graciosa

O gateway SHOULD:

1. Continuar atendendo servidores íntegros quando outros falharem
2. Retornar erros específicos para servidores indisponíveis
3. Tentar recuperação automática para falhas transitórias
4. Fornecer feedback claro ao cliente sobre o status do servidor

---

## 10. Política de Proteção

### 10.1 Visão Geral

A política de proteção controla qual conteúdo do GitHub o gateway expõe ao agente com base na **integridade** — um nível de confiança derivado da associação do autor do conteúdo com o repositório e o status de mesclagem do conteúdo. A configuração da política de proteção é específica para o servidor MCP do GitHub e é passada para o gateway juntamente com a configuração padrão do servidor.

Esta seção especifica os campos da política de proteção suportados pelo gateway, suas semânticas e o algoritmo usado para computar a integridade efetiva de cada item. Para documentação de configuração voltada para o usuário, veja a [Referência de Filtragem de Integridade do GitHub](/gh-aw/reference/integrity/).

### 10.2 Níveis de Integridade

O gateway reconhece os seguintes níveis de integridade, ordenados do mais alto para o mais baixo:

```text
merged > approved > unapproved > none > blocked
```

| Nível | Significado |
|-------|---------|
| `merged` | Pull requests mesclados no branch de destino; commits alcançáveis a partir do branch padrão |
| `approved` | Conteúdo de `OWNER`, `MEMBER` ou `COLLABORATOR`; PRs não-fork em repos públicos; todos os itens em repos privados; bots de plataforma reconhecidos; usuários em `trusted-users` |
| `unapproved` | Conteúdo de `CONTRIBUTOR` ou `FIRST_TIME_CONTRIBUTOR` |
| `none` | Todo o outro conteúdo, incluindo `FIRST_TIMER` e usuários sem associação |
| `blocked` | Conteúdo de usuários em `blocked-users` — sempre negado, não pode ser promovido |

`blocked` não é um valor de `min-integrity` configurável. Ele é atribuído automaticamente a itens de usuários em `blocked-users` e é sempre negado independentemente do limite configurado.

### 10.3 Campos da Política de Proteção

Campos da política de proteção são passados ao gateway como parte da configuração do servidor MCP do GitHub sob um objeto de política de proteção dedicado. Os seguintes campos são suportados:

| Campo | Tipo | Obrigatório | Padrão | Descrição |
|-------|------|----------|---------|-------------|
| `min-integrity` | string | Condicional | `approved` (repos públicos) | Limite de integridade mínimo: `merged`, `approved`, `unapproved` ou `none`. Obrigatório quando qualquer outro campo da política de proteção é usado. |
| `allowed-repos` | string ou array | Não | `"all"` | Escopo do repositório: `"all"`, `"public"` ou array de padrões (ex: `["myorg/*"]`) |
| `blocked-users` | array ou expressão | Não | `[]` | Nomes de usuário do GitHub negados incondicionalmente, independentemente de qualquer outra política |
| `trusted-users` | array ou expressão | Não | `[]` | Nomes de usuário do GitHub elevados para integridade `approved` independentemente da associação de seu autor |
| `approval-labels` | array ou expressão | Não | `[]` | Nomes de label do GitHub que promovem itens para integridade `approved` |
| `refusal-labels` | array ou expressão | Não | `[]` | Nomes de label do GitHub que rebaixam itens para integridade `none`, substituindo qualquer promoção |

### 10.4 Computação de Integridade Efetiva

O gateway MUST computar a integridade efetiva de cada item na seguinte ordem:

1. **Integridade base**: Derivada de metadados do GitHub (associação do autor, status de mesclagem, visibilidade do repositório).
2. **Verificação `blocked-users`**: Se o autor do conteúdo estiver listado em `blocked-users`, integridade efetiva → `blocked` (negado incondicionalmente; pular etapas restantes).
3. **Verificação `refusal-labels`**: Se o item carregar qualquer label presente em `refusal-labels`, integridade efetiva → `none` (rebaixado, substitui qualquer promoção das etapas 4–5).
4. **Verificação `trusted-users`**: Se o autor do conteúdo estiver listado em `trusted-users`, integridade efetiva → max(base, `approved`).
5. **Verificação `approval-labels`**: Se o item carregar qualquer label presente em `approval-labels`, integridade efetiva → max(base, `approved`).
6. **Padrão**: integridade efetiva → base.

A verificação do limite `min-integrity` é aplicada após esta computação. Itens cuja integridade efetiva está abaixo do limite DEVEM ser removidos antes que a resposta seja retornada ao agente.

**Principais restrições**:

- `blocked-users` MUST ter precedência sobre todos os outros campos de política. Itens bloqueados DEVEM ser negados mesmo que carreguem uma label `approval-labels` ou o autor esteja em `trusted-users`.
- `refusal-labels` MUST substituir a promoção de `trusted-users` e `approval-labels`. Um item com uma label de recusa e uma label de aprovação simultaneamente MUST ter integridade efetiva `none`.
- `trusted-users` e `approval-labels` são **apenas promoção** — eles NÃO DEVEM diminuir a integridade. `max(base, approved)` garante que a integridade mais alta existente (`merged`) seja preservada.
- `refusal-labels` é **apenas rebaixamento** — ele define a integridade para `none` e NÃO DEVE afetar itens `blocked`.

### 10.5 Campo `approval-labels`

`approval-labels` lista nomes de label do GitHub que promovem itens que carregam qualquer uma dessas labels para integridade `approved`.

**Semântica**:

- Quando um item carrega uma label presente em `approval-labels`, sua integridade efetiva é definida como `max(base, approved)`.
- A promoção não diminui a integridade: um item já em `merged` permanece em `merged`.
- `blocked-users` sempre tem precedência: itens de um usuário bloqueado permanecem bloqueados mesmo se rotulados.
- `refusal-labels` substitui `approval-labels`: um item com uma label de recusa e uma label de aprovação tem integridade efetiva `none`.

**Caso de uso**: Fluxos de trabalho de gate de revisão humana onde um revisor confiável etiqueta o conteúdo para sinalizar que é seguro para o agente.

**Exemplo de Configuração**:

```yaml
tools:
  github:
    min-integrity: approved
    approval-labels:
      - "human-reviewed"
      - "safe-for-agent"
```

**Teste de Conformidade**: T-GP-003 — Promoção de label de aprovação

### 10.6 Campo `refusal-labels`

`refusal-labels` é o inverso de `approval-labels`. Itens que carregam qualquer label do GitHub listada têm sua integridade efetiva rebaixada para `none`, independentemente da associação do autor ou de qualquer promoção de `trusted-users` ou `approval-labels`.

**Semântica**:

- Quando um item carrega uma label presente em `refusal-labels`, sua integridade efetiva MUST ser definida como `none`.
- `refusal-labels` substitui a promoção: se tanto uma label de recusa quanto uma label de aprovação estiverem presentes no mesmo item, a integridade efetiva MUST ser `none`.
- `refusal-labels` substitui `trusted-users`: se um autor estiver em `trusted-users`, mas o item tiver uma label de recusa, a integridade efetiva MUST ser `none`.
- `blocked-users` ainda tem precedência: itens de um usuário bloqueado permanecem `blocked` e não são afetados por `refusal-labels`.
- `refusal-labels` não diminui a integridade abaixo de `none`; itens de usuários bloqueados não são afetados.

**Caso de uso**: Suprimir itens específicos do agente — por exemplo, issues sinalizadas para revisão de segurança ou pull requests pendentes de uma verificação de conformidade manual — mesmo quando a `min-integrity` do fluxo de trabalho permitiria caso contrário.

**Exemplo de Configuração**:

```yaml
tools:
  github:
    min-integrity: approved
    refusal-labels:
      - "needs-security-review"
      - "do-not-automate"
```

**Exemplo Combinado** (labels de aprovação e recusa juntas):

```yaml
tools:
  github:
    min-integrity: approved
    approval-labels:
      - "human-reviewed"
    refusal-labels:
      - "needs-security-review"
```

Nesta configuração:
- Itens rotulados `human-reviewed` (sem `needs-security-review`) são promovidos para `approved`.
- Itens rotulados `needs-security-review` são rebaixados para `none`, mesmo se também rotulados `human-reviewed`.

**Requisitos**:

- O gateway MUST aplicar verificações de `refusal-labels` antes das verificações de `trusted-users` e `approval-labels` na computação da integridade efetiva.
- O gateway MUST definir a integridade efetiva para `none` para qualquer item que carregue uma label presente em `refusal-labels`.
- O valor de `refusal-labels` MUST suportar tanto um array literal de strings quanto uma expressão do GitHub Actions que resolva para uma lista separada por vírgula ou nova linha.
- O gateway MUST tratar uma lista `refusal-labels` vazia como um no-op (nenhum item é rebaixado).

**Testes de Conformidade**: T-GP-004 através de T-GP-008

### 10.7 Gerenciamento Centralizado via Variáveis do GitHub

Cada campo de lista por item (`blocked-users`, `trusted-users`, `approval-labels`, `refusal-labels`) PODE ser estendido centralmente usando variáveis de repositório ou organização do GitHub. O runtime DEVE unir os valores por fluxo de trabalho com a variável correspondente no momento da execução:

| Campo do Fluxo de Trabalho | Variável do GitHub |
|----------------|----------------|
| `blocked-users` | `GH_AW_GITHUB_BLOCKED_USERS` |
| `trusted-users` | `GH_AW_GITHUB_TRUSTED_USERS` |
| `approval-labels` | `GH_AW_GITHUB_APPROVAL_LABELS` |
| `refusal-labels` | `GH_AW_GITHUB_REFUSAL_LABELS` |

Por exemplo, se um fluxo de trabalho declara `blocked-users: ["spam-bot"]` e a variável de organização `GH_AW_GITHUB_BLOCKED_USERS` está definida como `compromised-acct,old-bot`, a lista efetiva de blocked-users no tempo de execução é `["spam-bot", "compromised-acct", "old-bot"]`.

Variáveis são divididas por vírgulas e novas linhas, aparadas de espaços em branco e deduplicadas. A união dos valores declarados no fluxo de trabalho e valores das variáveis forma a lista efetiva usada no momento da execução.

---

## 11. Testes de Conformidade

### 11.1 Requisitos da Suíte de Testes

Uma implementação conforme DEVE passar nas seguintes categorias de teste:

#### 11.1.1 Testes de Configuração

- **T-CFG-001**: Configuração de servidor stdio válida
- **T-CFG-002**: Configuração de servidor HTTP válida
- **T-CFG-003**: Resolução de expressão variável
- **T-CFG-004**: Detecção de erro de variável indefinida
- **T-CFG-005**: Validação de caminho do diretório de payload (caminhos absolutos)
- **T-CFG-006**: Rejeição de campo desconhecido
- **T-CFG-007**: Detecção de campo obrigatório ausente
- **T-CFG-008**: Detecção de tipo inválido
- **T-CFG-009**: Validação de faixa de porta
- **T-CFG-010**: Tipo de servidor personalizado válido com esquema registrado
- **T-CFG-011**: Rejeitar tipo personalizado sem registro de esquema
- **T-CFG-012**: Validar configuração personalizada em relação ao esquema registrado
- **T-CFG-013**: Rejeitar tipo personalizado em conflito com tipos reservados (stdio/http)
- **T-CFG-014**: Busca e cache de URL de esquema personalizado
- **T-CFG-015**: Formato de montagem de volume válido (host:container:mode)
- **T-CFG-016**: Rejeitar formato de montagem inválido (componentes ausentes)
- **T-CFG-017**: Rejeitar modo de montagem inválido (não "ro" ou "rw")
- **T-CFG-018**: Múltiplas montagens para um único servidor stdio
- **T-CFG-019**: Rejeitar montagens para servidores HTTP (apenas stdio)

#### 11.1.2 Testes de Tradução de Protocolo

- **T-PTL-001**: Ciclo de solicitação/resposta stdio
- **T-PTL-002**: Passthrough HTTP
- **T-PTL-003**: Preservação de assinatura da ferramenta
- **T-PTL-004**: Manipulação de solicitação simultânea
- **T-PTL-005**: Manipulação de payload grande
- **T-PTL-006**: Bufferização de resposta parcial
- **T-PTL-007**: Resposta de erro de falha de conexão HTTP
- **T-PTL-008**: Falha de conexão HTTP não é ignorada silenciosamente

#### 11.1.3 Testes de Isolamento

- **T-ISO-001**: Verificação de isolamento de container
- **T-ISO-002**: Verificação de isolamento de ambiente
- **T-ISO-003**: Verificação de isolamento de credencial
- **T-ISO-004**: Prevenção de comunicação entre containers
- **T-ISO-005**: Isolamento de falha de container
- **T-ISO-006**: Isolamento de montagem de volume (montagens não afetam outros containers)
- **T-ISO-007**: Aplicação de modo de acesso de montagem de volume (ro vs rw)
- **T-ISO-008**: Independência do caminho de montagem de volume entre containers

#### 11.1.4 Testes de Autenticação

- **T-AUTH-001**: Aceitação de token válido
- **T-AUTH-002**: Rejeição de token inválido
- **T-AUTH-003**: Rejeição de token ausente
- **T-AUTH-004**: Isenção de endpoint de integridade
- **T-AUTH-005**: Suporte a rotação de token
- **T-AUTH-006**: Configuração de identidade de bot confiável — entradas `trustedBots` estão presentes na configuração do gateway gerada e mescladas com a lista embutida do gateway

#### 11.1.5 Testes de Timeout

- **T-TMO-001**: Aplicação de timeout de inicialização
- **T-TMO-002**: Aplicação de timeout de ferramenta
- **T-TMO-003**: Mensagem de erro de timeout
- **T-TMO-004**: Timeout de resposta parcial
- **T-TMO-005**: Tratamento de timeout simultâneo

#### 11.1.6 Testes de Monitoramento de Integridade

- **T-HLT-001**: Disponibilidade de endpoint de integridade
- **T-HLT-002**: Precisão da sonda de liveness
- **T-HLT-003**: Precisão da sonda de prontidão
- **T-HLT-004**: Relatório de status do servidor
- **T-HLT-005**: Comportamento de reinicialização automática
- **T-HLT-006**: Resposta de integridade inclui campo specVersion
- **T-HLT-007**: Resposta de integridade inclui campo gatewayVersion
- **T-HLT-008**: specVersion usa formato de versionamento semântico
- **T-HLT-009**: gatewayVersion usa formato de versionamento semântico

#### 11.1.7 Testes de Saída de Configuração

- **T-OUT-001**: Gateway gera configuração JSON válida para stdout
- **T-OUT-002**: Configuração de saída inclui todos os servidores configurados
- **T-OUT-003**: Cada configuração de servidor tem "type": "http"
- **T-OUT-004**: Cada configuração de servidor tem formato "url" correto
- **T-OUT-005**: Cada configuração de servidor inclui objeto "headers" quando a autenticação é necessária
- **T-OUT-006**: Cabeçalho de autorização está presente quando a autenticação está configurada
- **T-OUT-007**: Configuração de saída está completa antes que o endpoint de integridade se torne disponível

#### 11.1.8 Testes de Tratamento de Erro

- **T-ERR-001**: Relatório de falha de inicialização
- **T-ERR-002**: Tratamento de erro de runtime
- **T-ERR-003**: Tratamento de solicitação inválida
- **T-ERR-004**: Recuperação de falha do servidor
- **T-ERR-005**: Qualidade da mensagem de erro

#### 11.1.9 Testes do Ciclo de Vida do Gateway

- **T-LIFE-001**: Autenticação de endpoint Close
- **T-LIFE-002**: Resposta de sucesso de endpoint Close
- **T-LIFE-003**: Idempotência de endpoint Close (retorna 410 em chamadas subsequentes)
- **T-LIFE-004**: Término do container no Close
- **T-LIFE-005**: Limpeza de recursos no Close
- **T-LIFE-006**: Manipulação de solicitação em trânsito durante o desligamento
- **T-LIFE-007**: Novas solicitações rejeitadas após o início do Close

#### 11.1.10 Testes OpenTelemetry

- **T-OTEL-001**: Gateway inicia com sucesso quando `opentelemetry` é omitido
- **T-OTEL-002**: Gateway inicia com sucesso quando `opentelemetry` está configurado com um endpoint válido
- **T-OTEL-003**: Rejeitar configuração de `opentelemetry` com campo `endpoint` ausente
- **T-OTEL-004**: Rejeitar configuração de `opentelemetry` com endpoint não HTTPS
- **T-OTEL-005**: Span emitido para cada invocação de ferramenta MCP com atributos necessários (`mcp.server`, `mcp.method`, `mcp.tool`, `http.status_code`)
- **T-OTEL-006**: Quando variável de ambiente `OTEL_EXPORTER_OTLP_HEADERS` é definida, cabeçalhos são enviados com cada solicitação de exportação OTLP
- **T-OTEL-007**: Contexto W3C `traceparent` propagado quando `traceId` e `spanId` são configurados
- **T-OTEL-008**: Gateway gera `spanId` aleatório em `traceparent` quando apenas `traceId` é fornecido
- **T-OTEL-009**: Falha de exportação não afeta processamento de solicitação MCP ou disponibilidade do gateway
- **T-OTEL-010**: `serviceName` é refletido no atributo de recurso `service.name` de spans emitidos

#### 11.1.11 Testes de Política de Proteção (Guard Policy)

- **T-GP-001**: Itens de `blocked-users` são negados independentemente da configuração de `min-integrity`
- **T-GP-002**: Itens de `trusted-users` recebem integridade efetiva `approved` quando base é menor
- **T-GP-003**: Itens carregando uma label `approval-labels` recebem integridade efetiva `approved` quando base é menor
- **T-GP-004**: Itens carregando uma label `refusal-labels` recebem integridade efetiva `none`
- **T-GP-005**: `refusal-labels` substitui `approval-labels` — um item com tanto uma label de recusa quanto uma label de aprovação tem integridade efetiva `none`
- **T-GP-006**: `refusal-labels` substitui `trusted-users` — um item de um usuário confiável com uma label de recusa tem integridade efetiva `none`
- **T-GP-007**: `blocked-users` tem precedência sobre `refusal-labels` — itens bloqueados permanecem `blocked`
- **T-GP-008**: Lista `refusal-labels` vazia resulta em nenhum item sendo rebaixado
- **T-GP-009**: `refusal-labels` aceita uma expressão do GitHub Actions (lista separada por vírgula ou nova linha)
- **T-GP-010**: `min-integrity: none` permite que itens com integridade `none` passem; itens rebaixados por `refusal-labels` para `none` são visíveis quando `min-integrity: none`

---

*Copyright © 2026 GitHub, Inc. Todos os direitos reservados.*
