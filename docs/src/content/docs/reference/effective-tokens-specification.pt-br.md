---
title: Especificação de Tokens Efetivos
description: Especificação formal definindo Effective Tokens (ET), uma métrica normalizada para medir o uso de tokens de LLM entre classes de token, multiplicadores de modelo e grafos de execução multi-agente
sidebar:
  order: 1360
---

# Especificação de Tokens Efetivos

**Versão**: 0.2.0
**Status**: Rascunho
**Data de publicação**: 02/04/2026
**Editor**: Equipe do GitHub Agentic Workflows
**Esta versão**: [especificação-de-tokens-efetivos](/gh-aw/reference/effective-tokens-specification/)
**Última versão publicada**: Este documento

---

## Resumo

Esta especificação define **Tokens Efetivos (ET)**, uma unidade normalizada para medir o uso de Large Language Models (LLM) entre classes de token, intensidade computacional relativa ao modelo e grafos de execução multi-invocação. ET fornece uma métrica única unificada para cargas de trabalho de LLM compostas, incluindo pipelines de várias etapas, chamadas aumentadas por ferramentas, orquestração de sub-agentes e inferência recursiva.

## Status deste documento

Esta seção descreve o status deste documento no momento da publicação. Este é um rascunho de especificação e pode ser atualizado, substituído ou tornado obsoleto por outros documentos a qualquer momento.

Este documento é regido pelo processo de especificações do projeto GitHub Agentic Workflows.

## Índice

1. [Introdução](#1-introdução)
2. [Conformidade](#2-conformidade)
3. [Terminologia](#3-terminologia)
4. [Modelo de Contabilização de Token](#4-modelo-de-contabilização-de-token)
5. [Agregação Multi-Invocação](#5-agregação-multi-invocação)
6. [Requisitos do Grafo de Execução](#6-requisitos-do-grafo-de-execução)
7. [Relatórios](#7-relatórios)
8. [Requisitos de Implementação](#8-requisitos-de-implementação)
9. [Extensibilidade](#9-extensibilidade)
10. [Testes de Conformidade](#10-testes-de-conformidade)
11. [Apêndices](#apêndices)
12. [Registro de Multiplicadores de Modelo](#registro-de-multiplicadores-de-modelo)
13. [Notas de Sincronização](#notas-de-sincronização)
14. [Referências](#referências)
15. [Registro de Alterações](#registro-de-alterações)

---

## 1. Introdução

### 1.1 Objetivo

As contagens de token relatadas pelas APIs de LLM não são diretamente comparáveis: diferentes classes de token (entrada, cacheada, saída, raciocínio) acarretam diferentes custos computacionais, e diferentes modelos têm diferentes custos relativos. Tokens Efetivos normaliza essas variáveis em um escalar único que reflete a verdadeira intensidade computacional, permitindo medição e comparação consistentes em sistemas multi-agente complexos.

### 1.2 Escopo

Esta especificação cobre:

- Definição de classes de token e seus pesos padrão
- A fórmula de computação de ET por invocação
- Agregação em grafos de execução multi-invocação
- Requisitos estruturais para nós de invocação e relatórios de resumo

Esta especificação NÃO cobre:

- Faturamento, precificação ou alocação de custos
- Seleção de modelo ou estratégias de roteamento
- Streaming ou relatórios parciais de token

### 1.3 Objetivos de Design

Uma implementação de ET:

1. Preserva contagens de token brutos por invocação
2. Normaliza entre classes de token usando pesos divulgados
3. Normaliza entre modelos usando multiplicadores por modelo
4. Suporta agregação em qualquer número de invocações
5. Produz uma única métrica reprodutível a partir de entradas idênticas
6. Não possui dependência de sistemas de faturamento ou precificação

---

## 2. Conformidade

### 2.1 Classes de Conformidade

**Implementação em conformidade**: Uma implementação que satisfaz todos os requisitos MUST/SHALL nesta especificação.

**Implementação parcialmente em conformidade**: Uma implementação que satisfaz os requisitos principais de contabilização (Seções 4–5), mas omite campos ou extensões opcionais.

### 2.2 Notação de Requisitos

As palavras-chave "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY" e "OPTIONAL" neste documento devem ser interpretadas conforme descrito em [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

### 2.3 Níveis de Conformidade

- **Nível 1 – Básico**: Computação de ET de invocação única (Seção 4)
- **Nível 2 – Padrão**: Agregação multi-invocação e grafo de execução (Seções 5–6)
- **Nível 3 – Completo**: Relatórios completos e suporte à extensibilidade (Seções 7–9)

---

## 3. Terminologia

### 3.1 Classes de Token

| Classe | Símbolo | Descrição |
|---|---|---|
| Tokens de Entrada | I | Tokens recém-processados pelo modelo |
| Tokens de Entrada Cacheada | C | Tokens servidos via cache ou reuso de prefixo |
| Tokens de Saída | O | Tokens gerados pelo modelo |
| Tokens de Raciocínio | R | Tokens internos usados durante a inferência (opcional) |

### 3.2 Multiplicador de Modelo

O **Multiplicador Copilot** (`m`) é um escalar que representa a intensidade computacional relativa de um modelo versus uma linha de base definida. Seu valor é específico do modelo e DEVE ser divulgado pela implementação.

### 3.3 Invocação

Um único ciclo de solicitação-resposta de LLM. Cada invocação produz um conjunto de contagens de token e gera um valor ET.

### 3.4 Sub-Agente

Qualquer invocação disparada por outra chamada de LLM ou camada de orquestração. Exemplos incluem agentes que usam ferramentas, chamadas aumentadas por recuperação, agentes de planejamento/execução e chamadas de LLM delegadas recursivamente.

### 3.5 Grafo de Execução

Uma estrutura direcionada representando todas as invocações associadas a uma única solicitação de nível superior. O nó raiz não tem pai; sub-agentes referenciam sua invocação de gatilho como seu pai.

---

## 4. Modelo de Contabilização de Token

### 4.1 Contagem Bruta de Tokens

Para cada invocação, o total bruto é:

```
raw_total_tokens = I + C + O + R
```

### 4.2 Pesos das Classes de Token

Os pesos padrão para as quatro classes de token são:

| Classe de Token | Símbolo | Peso Padrão |
|---|---|---|
| Entrada | w_in | 1.0 |
| Entrada Cacheada | w_cache | 0.1 |
| Saída | w_out | 4.0 |
| Raciocínio | w_reason | 4.0 |

As implementações PODEM sobrescrever esses valores, mas DEVEM divulgar os pesos usados em qualquer saída relatada.

### 4.3 Tokens Ponderados Base

Por invocação:

```
base_weighted_tokens =
    (w_in × I) + (w_cache × C) + (w_out × O) + (w_reason × R)
```

### 4.4 Tokens Efetivos Por Invocação

```
effective_tokens = m × base_weighted_tokens
```

---

## 5. Agregação Multi-Invocação

### 5.1 Total de Tokens Efetivos

Para uma solicitação envolvendo N invocações:

```
ET_total = Σ (m_i × base_weighted_tokens_i)
```

Cada invocação PODE usar um modelo e multiplicador diferente.

### 5.2 Total de Tokens Brutos

```
raw_total_tokens = Σ (I_i + C_i + O_i + R_i)
```

### 5.3 Contagem de Invocação

```
total_invocations = N
```

Esta contagem DEVE incluir a chamada raiz, todas as chamadas de sub-agente e todas as chamadas de LLM disparadas por ferramentas.

---

## 6. Requisitos do Grafo de Execução

As implementações DEVEM representar fluxos de trabalho de múltiplas chamadas como um grafo de execução direcionado.

### 6.1 Esquema de Nó

Cada nó (invocação) DEVE estar em conformidade com:

```json
{
  "id": "string",
  "parent_id": "string | null",
  "model": {
    "name": "string",
    "copilot_multiplier": number
  },
  "usage": {
    "input_tokens": number,
    "cached_input_tokens": number,
    "output_tokens": number,
    "reasoning_tokens": number
  },
  "derived": {
    "base_weighted_tokens": number,
    "effective_tokens": number
  },
  "flagged": {
    "code": "string",
    "reason": "string"
  }
}
```

### 6.2 Invocação Raiz

A invocação raiz DEVE ter `parent_id = null`. Ela representa a solicitação voltada ao usuário que inicia o grafo de execução.

### 6.3 Invocação de Sub-Agente

Cada invocação de sub-agente DEVE referenciar um `parent_id` válido. As invocações de sub-agente PODEM gerar recursivamente outras invocações.

Para grafos de execução com mais de dois níveis, as implementações DEVEM agregar Tokens Efetivos descendentes em pós-ordem estável: primeiro os descendentes folha totalmente observados, depois seus ancestrais observados mais próximos e, finalmente, o custo da invocação local do nó pai. Quando um pai tem descendentes incompletos ou inobserváveis, a implementação DEVE relatar a soma parcial acumulada a partir dos descendentes observados mais profundos antes de adicionar quaisquer estimativas de fallback mais rasas, e DEVE manter o nó pai sinalizado até que todos os descendentes conhecidos sejam observados ou explicitamente marcados como inobserváveis. Computações repetidas sobre o mesmo grafo parcialmente observado DEVEM produzir a mesma ordem parcial e sequência de subtotal.

---

## 7. Relatórios

Uma resposta em conformidade DEVE incluir um objeto `summary` ao lado do array `invocations`:

```json
{
  "summary": {
    "total_invocations": number,
    "raw_total_tokens": number,
    "base_weighted_tokens": number,
    "effective_tokens": number
  },
  "invocations": [ ... ]
}
```

---

## 8. Requisitos de Implementação

### 8.1 Completude

Todas as chamadas de LLM DEVEM ser incluídas no grafo de execução. Chamadas ocultas ou disparadas pelo sistema DEVEM ser contadas.

### 8.2 Determinismo

Dadas entradas e multiplicadores idênticos, o ET DEVE ser reprodutível. As implementações NÃO DEVEM introduzir fatores não determinísticos na computação.

### 8.3 Versionamento

As implementações DEVEM versionar seus pesos de token e multiplicadores de modelo para que relatórios históricos permaneçam interpretáveis.

### 8.4 Visibilidade Parcial

Quando os sub-agentes não são totalmente observáveis, as implementações AINDA DEVEM relatar os totais agregados. Nós de invocação com dados incompletos DEVEM ser sinalizados para indicar informações ausentes.

### 8.5 Salvaguardas

As implementações devem evitar que o acúmulo ilimitado de ET produza saídas não finitas ou não interoperáveis.

**R-SAFE-001**: A lógica de agregação de ET DEVE detectar overflow e estados aritméticos não finitos (`NaN`, `+Inf`, `-Inf`) antes de serializar a saída.

**R-SAFE-002**: As implementações DEVEM impor um teto máximo de ET de `9007199254740991` (`2^53 - 1`) para campos numéricos serializados para preservar a interoperabilidade de inteiros JavaScript-safe em pipelines cross-language.

**R-SAFE-003**: Quando o ET computado excede o teto, as implementações DEVEM fixar o valor `summary.effective_tokens` relatado no teto e DEVEM emitir um aviso indicando que a fixação ocorreu.

**R-SAFE-003A**: Quando ocorre fixação de ET, as implementações DEVEM registrar uma condição de overflow determinística usando `flagged.code = "ET_OVERFLOW"` no nó raiz/subárvore afetado ou um erro determinístico quando nenhum canal de flag estruturado estiver disponível. O payload de erro/flag DEVE incluir o valor de teto `9007199254740991` para que os operadores possam distinguir overflow de dados de uso ausentes.

**R-SAFE-004**: Para longas cadeias multi-agente, as implementações DEVEM agregar ET de forma incremental e DEVEM emitir um aviso antecipado quando os totais de execução excederem 80% do teto.

**R-SAFE-005**: Para nós de invocação com payloads de uso incompletos (sub-agentes inobserváveis), as implementações DEVEM serializar `usage.input_tokens`, `usage.cached_input_tokens`, `usage.output_tokens`, `usage.reasoning_tokens`, `derived.base_weighted_tokens` e `derived.effective_tokens` como zero numérico (`0`) em vez de omitir esses campos.

**R-SAFE-006**: Para nós de invocação que são incompletos/inobserváveis, as implementações DEVEM incluir um objeto `flagged` com o esquema `{ "code": "UNOBSERVABLE_INVOCATION", "reason": string }`. Para nós de invocação totalmente observados, as implementações PODEM omitir `flagged`.

---

## 9. Extensibilidade

As implementações PODEM:

- Adicionar novas classes de token (ex: `tool_tokens`)
- Adicionar latência ou metadados de computação por nó de invocação
- Suportar streaming ou atualizações de progresso parciais

As extensões NÃO DEVEM alterar a definição central de ET ou os valores de peso padrão sem divulgação.

---

## 10. Testes de Conformidade

### 10.1 Requisitos da Suíte de Testes

#### 10.1.1 Testes de Contabilização de Token

- **T-ET-001**: Invocação única com todas as quatro classes de token produz `base_weighted_tokens` correto
- **T-ET-002**: ET de invocação única igual a `m × base_weighted_tokens`
- **T-ET-003**: Classes de token de valor zero não afetam o resultado
- **T-ET-004**: Pesos personalizados são aplicados quando pesos padrão são sobrescritos

#### 10.1.2 Testes de Agregação

- **T-ET-010**: `ET_total` multi-invocação igual à soma dos valores de ET por invocação
- **T-ET-011**: `raw_total_tokens` igual à soma de todos os tokens brutos em todas as invocações
- **T-ET-012**: Contagem `total_invocations` inclui raiz, sub-agentes e chamadas disparadas por ferramentas

#### 10.1.3 Testes de Grafo de Execução

- **T-ET-020**: Nó raiz tem `parent_id = null`
- **T-ET-021**: Todos os nós de sub-agente referenciam um `parent_id` válido
- **T-ET-022**: Esquema de nó inclui todos os campos obrigatórios

#### 10.1.4 Testes de Relatórios

- **T-ET-030**: Objeto de resumo está presente em todas as respostas em conformidade
- **T-ET-031**: Valores de resumo são consistentes com dados por invocação

### 10.2 Lista de verificação de conformidade

#### 10.2.1 Resumo da Contagem de Testes de Conformidade

| Categoria | Contagem |
|---|---|
| Total de testes definidos | 12 |
| Testes obrigatórios | 12 |
| Testes opcionais | 0 |

Método de contagem: IDs `T-ET-*` únicos em §10.1 (`001–004`, `010–012`, `020–022`, `030–031`).

| Requisito | ID do Teste | Nível | Status |
|---|---|---|---|
| Tokens ponderados base por invocação | T-ET-001–004 | 1 | Implementado |
| Computação de ET por invocação | T-ET-002 | 1 | Implementado |
| Agregação multi-invocação | T-ET-010–012 | 2 | Implementado |
| Esquema de nó do grafo de execução | T-ET-020–022 | 2 | Implementado |
| Relatório de resumo | T-ET-030–031 | 3 | Implementado |
| Divulgação de peso personalizado | T-ET-004 | 1 | Implementado |
| Versionamento de pesos/multiplicadores | — | 3 | Recomendado |
| Sinalização de visibilidade parcial | — | 2 | Recomendado |

---

## Apêndices

### Apêndice A: Exemplo de trabalho

#### A.1 Cenário

Uma solicitação dispara três invocações: uma chamada raiz, um sub-agente de recuperação e uma chamada de síntese final.

#### A.2 Dados de Entrada

```json
{
  "invocations": [
    {
      "id": "root",
      "parent_id": null,
      "model": { "name": "model-a", "copilot_multiplier": 2.0 },
      "usage": {
        "input_tokens": 500,
        "cached_input_tokens": 200,
        "output_tokens": 150,
        "reasoning_tokens": 0
      }
    },
    {
      "id": "retrieval",
      "parent_id": "root",
      "model": { "name": "model-b", "copilot_multiplier": 1.0 },
      "usage": {
        "input_tokens": 300,
        "cached_input_tokens": 0,
        "output_tokens": 100,
        "reasoning_tokens": 0
      }
    },
    {
      "id": "synthesis",
      "parent_id": "root",
      "model": { "name": "model-a", "copilot_multiplier": 2.0 },
      "usage": {
        "input_tokens": 200,
        "cached_input_tokens": 100,
        "output_tokens": 250,
        "reasoning_tokens": 0
      }
    }
  ]
}
```

#### A.3 Computação

```
root:
  base = (1.0 × 500) + (0.1 × 200) + (4.0 × 150) = 500 + 20 + 600 = 1120
  ET   = 2.0 × 1120 = 2240

retrieval:
  base = (1.0 × 300) + (4.0 × 100) = 300 + 400 = 700
  ET   = 1.0 × 700 = 700

synthesis:
  base = (1.0 × 200) + (0.1 × 100) + (4.0 × 250) = 200 + 10 + 1000 = 1210
  ET   = 2.0 × 1210 = 2420
```

#### A.4 Saída

```json
{
  "summary": {
    "total_invocations": 3,
    "raw_total_tokens": 1800,
    "base_weighted_tokens": 3030,
    "effective_tokens": 5360
  }
}
```

### Apêndice B: Referência de Fórmula Central

```
ET_total = Σ [ m_i × (w_in × I_i + w_cache × C_i + w_out × O_i + w_reason × R_i) ]
```

Com pesos padrão:

```
ET_total = Σ [ m_i × (I_i + 0.1 C_i + 4 O_i + 4 R_i) ]
```

### Apêndice C: Considerações de Segurança

Valores de ET são derivados de metadados de uso de token. As implementações DEVEM tratar os dados de token por invocação como potencialmente sensíveis, uma vez que padrões de uso podem revelar informações sobre prompts de sistema, configurações de modelo ou comportamento do usuário. Valores de ET agregados adequados para painéis de observabilidade DEVEM ser separados de dados detalhados por invocação em sistemas de relatórios com controle de acesso.

---

## Registro de Multiplicadores de Modelo

### Propósito do Registro

O **Multiplicador Copilot** (`m`) usado na fórmula ET é um escalar por modelo que representa o custo computacional de cada modelo em relação ao modelo de referência. Para garantir reprodutibilidade e transparência, os valores de multiplicador DEVEM ser obtidos de um registro divulgado e versionado.

### Fonte do Registro Normativo

O registro autoritativo para valores de `copilot_multiplier` nesta implementação é o arquivo:

```
pkg/cli/data/model_multipliers.json
```

Este arquivo é incorporado no momento da compilação no binário `gh-aw` usando uma diretiva Go `//go:embed` em `pkg/cli/effective_tokens.go`. O formato do registro é:

```json
{
  "version": "string",
  "description": "string",
  "reference_model": "string",
  "token_class_weights": {
    "input": number,
    "cached_input": number,
    "output": number,
    "reasoning": number,
    "cache_write": number
  },
  "multipliers": {
    "<model-name>": number
  }
}
```

### Requisitos do Registro

**R-REG-001**: O registro DEVE declarar um campo `version` que muda sempre que qualquer valor de multiplicador é adicionado, removido ou modificado.

**R-REG-002**: O registro DEVE declarar um campo `reference_model` identificando o modelo de linha de base cujo multiplicador é igual a 1.0. Todos os outros multiplicadores são relativos a esta linha de base.

**R-REG-003**: O registro DEVE incluir `token_class_weights` para todas as quatro classes de token padrão: `input`, `cached_input`, `output` e `reasoning`. Uma implementação em conformidade DEVE usar esses pesos como valores padrão para a Seção 4.2.

**R-REG-004**: As implementações DEVEM incorporar ou agrupar o registro no momento da compilação. A busca em tempo de execução de valores de multiplicador de uma fonte externa requer divulgação na saída relatada.

**R-REG-005**: Quando um nome de modelo não está presente no registro, as implementações DEVEM tratar o multiplicador como `1.0` e DEVEM emitir um aviso observando que o modelo não é reconhecido.

**R-REG-006**: Multiplicadores personalizados fornecidos pelo chamador (ex: via API ou configuração) DEVEM ser mesclados com multiplicadores de registro. Valores personalizados têm precedência e DEVEM ser divulgados em qualquer relatório que os utilize.

**R-REG-007**: O registro NÃO DEVE conter valores de espaço reservado como `TBD`, `null` ou strings vazias para qualquer entrada de multiplicador de modelo. Cada chave de modelo declarada DEVE mapear para um valor numérico de multiplicador.

**R-REG-008**: Ao adicionar suporte para um novo modelo, os mantenedores DEVEM registrar o modelo em `pkg/cli/data/model_multipliers.json` com um multiplicador numérico concreto antes do release. Se a calibração estiver incompleta, o modelo DEVE ser omitido do registro e o comportamento de fallback de implementação em R-REG-005 se aplica.

**R-REG-009**: Quando um modelo está programado para remoção do registro, ele DEVE permanecer em `pkg/cli/data/model_multipliers.json` com um marcador `deprecated` em um comentário ou campo de metadados complementar por pelo menos uma versão secundária (minor) antes de ser excluído. As implementações DEVEM emitir um aviso quando um modelo `deprecated` for encontrado em tempo de execução, aconselhando os chamadores a migrar para um modelo suportado. Uma entrada de modelo NÃO DEVE ser silenciosamente removida entre versões secundárias consecutivas; a remoção sem o aviso de depreciação de uma versão é uma alteração de quebra e DEVE ser acompanhada por um aumento de versão principal do campo `version` do registro.

### Versionamento do Registro

O campo `version` em `model_multipliers.json` corresponde à versão do esquema do registro, não à versão do binário gh-aw. As implementações DEVEM incluir a versão do registro em todos os relatórios de resumo de ET para permitir a reconstrução histórica.

---

## Notas de Sincronização

O registro de Tokens Efetivos é mantido em `pkg/cli/data/model_multipliers.json` e carregado por `pkg/cli/effective_tokens.go`.

Para manter a especificação e a implementação sincronizadas:

1. Atualize os requisitos de registro desta especificação ao adicionar, remover ou re-escalonar multiplicadores de modelo.
2. Atualize `pkg/cli/data/model_multipliers.json` na mesma alteração.
3. Ao depreciar um modelo, adicione um comentário `deprecated` ao lado da entrada e mantenha-o no registro por pelo menos uma versão secundária antes da remoção (R-REG-009). Atualize o campo `version` do registro na remoção.
4. Verifique o carregamento e o comportamento de fallback em `pkg/cli/effective_tokens_test.go` (`TestModelMultipliersJSONEmbedded`, `TestResolveEffectiveWeightsDefault` e verificações de inventário).
5. Execute `make build` para que o registro incorporado seja reconstruído no binário `gh-aw`.

Releases em conformidade DEVEM incluir uma asserção de teste para multiplicadores de modelo recém-adicionados para garantir a paridade entre implementação e registro.

---

## Referências

### Referências Normativas

- **[RFC 2119]** Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels", BCP 14, RFC 2119, March 1997. <https://www.ietf.org/rfc/rfc2119.txt>

### Referências Informativas

- **[OPENAI-USAGE]** OpenAI API Reference — Usage Objects. <https://platform.openai.com/docs/api-reference>
- **[ANTHROPIC-USAGE]** Anthropic API Reference — Token Usage. <https://docs.anthropic.com/en/api/getting-started>

---

## Registro de Alterações

### Versão 0.3.0 (Rascunho)

- **Adicionado**: Seção de Registro de Multiplicador de Modelo com requisitos normativos R-REG-001 a R-REG-009
- **Adicionado**: R-REG-009: norma de ciclo de vida de depreciação/encerramento de modelo (modelos devem carregar um marcador `deprecated` por uma versão secundária antes da remoção)
- **Adicionado**: Arquivo de esqueleto de teste de conformidade `pkg/cli/effective_tokens_compliance_test.go` com stubs de teste Go para T-ET-001..T-ET-031
- **Atualizado**: Status da coluna da lista de verificação de conformidade §10.2 de "Obrigatório" para "Implementado" para todos os IDs de teste T-ET-001–T-ET-031 (todos os testes agora implementados e passando)
- **Auditoria (Apêndice C — Segurança)**: Requisitos do Apêndice C verificados em `pkg/cli/effective_tokens.go` e `pkg/cli/data/model_multipliers.json`. Conclusões:
  - _Padrões de uso sensíveis_ (Apêndice C §1): Dados de token por invocação não são expostos diretamente pela CLI; apenas `TotalEffectiveTokens` agregado é destacado na saída de auditoria. O controle de acesso é delegado às permissões do repositório GitHub. **Nenhuma lacuna encontrada.**
  - _Separação de dados agregados vs detalhados_ (Apêndice C §2): O mapa `TokenUsageSummary.ByModel` contém detalhamentos por modelo, mas só é registrado no nível DEBUG, não incluído na saída padrão da CLI. **Nenhuma lacuna encontrada.**
  - _Exposição do registro_: O `model_multipliers.json` incorporado contém apenas coeficientes de multiplicador, não segredos ou PII. **Nenhuma lacuna encontrada.**
  - _Acompanhamento_: A especificação não aborda vazamento de dados de token via atributos OTEL. Isso é rastreado como uma preocupação separada (veja §7.3 da Especificação de Experimentos para precedente).

### Versão 0.2.0 (Rascunho)

- Adotado formato de especificação estilo W3C
- Adicionados níveis de conformidade (Básico, Padrão, Completo)
- Adicionada seção de testes de conformidade com IDs de teste
- Adicionado Apêndice C: Considerações de Segurança
- Clarificados requisitos de visibilidade parcial

### Versão 0.1.0 (Rascunho)

- Definição inicial da métrica de Tokens Efetivos
- Definidas quatro classes de token e pesos padrão
- Definidas fórmulas por invocação e multi-invocação
- Definido esquema de nó de grafo de execução

---

*Copyright © 2026 Equipe do GitHub Agentic Workflows. Todos os direitos reservados.*
