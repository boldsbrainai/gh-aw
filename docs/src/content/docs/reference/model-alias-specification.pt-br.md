---
title: Especificação de Alias de Modelo
description: Especificação formal estilo W3C definindo o formato de alias de modelo, convenções de nomenclatura, codificação de parâmetro estilo URL e estratégias de resolução de fallback para GitHub Agentic Workflows
sidebar:
  order: 1360
---

# Especificação de Formato de Alias de Modelo

**Versão**: 1.1.0  
**Status**: Rascunho  
**Data de Publicação**: 03/05/2026  
**Editor**: Equipe do GitHub Agentic Workflows  
**Esta Versão**: [model-alias-specification](/gh-aw/reference/model-alias-specification/)  
**Versão Publicada Mais Recente**: Este documento

---

## Resumo

Esta especificação define o Formato de Alias de Modelo (MAF) para GitHub Agentic Workflows (AWF). Ela estabelece requisitos normativos para a sintaxe do identificador de modelo, codificação de parâmetro estilo URL para configuração de modelo (como esforço de raciocínio e temperatura) e o algoritmo de resolução de fallback de múltiplas camadas que o AWF aplica ao selecionar um modelo concreto no momento da compilação. A especificação destina-se a autores de fluxo de trabalho, implementadores de AWF e integrações de ferramentas que consomem ou produzem strings de nome de modelo.

## Status deste Documento

Esta seção descreve o status deste documento no momento da publicação. Este é um rascunho de especificação e pode ser atualizado, substituído ou tornado obsoleto por outros documentos a qualquer momento.

Este documento é regido pelo processo de especificações do projeto GitHub Agentic Workflows.

## Índice

1. [Introdução](#1-introdução)
2. [Conformidade](#2-conformidade)
3. [Terminologia](#3-terminologia)
4. [Sintaxe do Identificador de Modelo](#4-sintaxe-do-identificador-de-modelo)
5. [Codificação de Parâmetro estilo URL](#5-codificação-de-parâmetro-estilo-url)
6. [Parâmetros Definidos](#6-parâmetros-definidos)
7. [Formato do Mapa de Alias](#7-formato-do-mapa-de-alias)
8. [Algoritmo de Resolução de Fallback](#8-algoritmo-de-resolução-de-fallback)
9. [Aliases Embutidos (Builtin)](#9-aliases-embutidos)
10. [Precedência de Mesclagem](#10-precedência-de-mesclagem)
11. [Regras de Validação](#11-regras-de-validação)
12. [Testes de Conformidade](#12-testes-de-conformidade)
13. [Apêndices](#apêndices)
14. [Referências](#referências)
15. [Log de Alterações](#15-log-de-alterações)

---

## 1. Introdução

### 1.1 Objetivo

Fluxos de trabalho AWF devem especificar o modelo LLM que um agente de IA invoca durante a execução. Nomes de modelos são específicos de versão, específicos de provedor e variam substancialmente nos ecossistemas Copilot, Anthropic, OpenAI e Google. O Formato de Alias de Modelo aborda três problemas inter-relacionados:

1. **Portabilidade**: Um fluxo de trabalho escrito contra `sonnet` é executado no modelo Anthropic Sonnet atual, sem exigir edições quando os modelos são atualizados.
2. **Configurabilidade**: Knobs em nível de modelo, como esforço de raciocínio e temperatura de amostragem, devem ser expressáveis inline, sem adicionar novas chaves de frontmatter para cada parâmetro.
3. **Resiliência**: Quando um modelo preferencial não está disponível, AWF DEVE tentar candidatos alternativos em uma ordem determinística antes de falhar.

### 1.2 Escopo

Esta especificação abrange:

- Sintaxe de uma string de identificador de modelo (nome simples, nome com escopo de provedor, padrão glob, parâmetros codificados em URL)
- Regras de codificação para parâmetros de consulta estilo URL em um nome de modelo
- O formato YAML do mapa de alias usado no frontmatter do fluxo de trabalho (chave `models:`)
- O algoritmo de resolução de mesclagem e recursivo de múltiplas camadas
- Aliases embutidos (builtin) enviados com o AWF
- Regras de validação normativas aplicadas no momento da compilação e runtime

Esta especificação NÃO abrange:

- Construção de chamada de API específica do motor (como parâmetros são encaminhados para a API REST do provedor)
- Orçamentos de token, contabilidade de custos ou métrica de Effective Tokens (veja [Especificação de Effective Tokens](/gh-aw/reference/effective-tokens-specification/))
- Detecção de capacidade de modelo em runtime
- Lógica de roteamento de modelo dentro do gateway do Copilot

### 1.3 Objetivos de Design

O Formato de Alias de Modelo:

1. Usa sintaxe familiar de string de consulta URL, para que os parâmetros sejam legíveis por humanos e não exijam novas chaves YAML.
2. É compatível com versões anteriores: um nome de modelo simples sem parâmetros é um identificador válido.
3. Suporta resolução de alias recursiva para permitir abstrações em camadas (`auto` → `large` → `sonnet`).
4. É extensível: novos parâmetros PODEM ser adicionados sem alterar a sintaxe principal.
5. Preserva a convenção `fornecedor/modelo` já estabelecida na camada de motor do AWF.

---

## 2. Conformidade

### 2.1 Classes de Conformidade

**Implementação AWF conforme**: Uma implementação que satisfaz todos os requisitos MUST/SHALL nesta especificação, incluindo análise, resolução e validação corretas de strings de alias de modelo.

**Implementação parcialmente conforme**: Uma implementação que analisa e resolve corretamente identificadores de modelo, incluindo parâmetros (Seções 4–8), mas não implementa o conjunto completo de parâmetros definido na Seção 6.

### 2.2 Notação de Requisitos

As palavras-chave "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY" e "OPTIONAL" neste documento devem ser interpretadas como descrito em [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

### 2.3 Níveis de Conformidade

- **Nível 1 – Sintaxe**: Análise correta de strings de identificador de modelo incluindo parâmetros (Seções 4–5)
- **Nível 2 – Resolução**: Formato completo do mapa de alias, precedência de mesclagem e resolução de fallback (Seções 7–10)
- **Nível 3 – Completo**: Conjunto completo de parâmetros, validação e relatórios de erro (Seções 6, 11)

---

## 3. Terminologia

**Identificador de Modelo**: Uma string que nomeia um modelo LLM concreto ou abstrato. Pode incluir parâmetros estilo URL.

**Identificador Simples (Bare Identifier)**: Um identificador de modelo que não possui barra e nem string de consulta. Exemplos: `gpt-5`, `sonnet`, `auto`.

**Identificador com Escopo de Provedor**: Um identificador de modelo da forma `provedor/id-do-modelo`. O segmento do provedor é um token curto que identifica o gateway de roteamento ou fornecedor. Exemplos: `copilot/gpt-5`, `anthropic/claude-opus-4.5`.

**Padrão Glob**: Um identificador com escopo de provedor contendo um ou mais caracteres curinga `*`. Usado em entradas de lista de alias para corresponder a uma família de nomes de modelos concretos. Exemplos: `copilot/*sonnet*`, `openai/gpt-5*mini*`.

**Nome de Alias**: Um identificador simples que resolve para uma lista ordenada de padrões candidatos ou outros nomes de alias. Exemplos: `sonnet`, `large`, `auto`.

**Parâmetro de Modelo**: Um par chave=valor codificado na string de consulta do identificador de modelo que fornece configuração adicional à invocação do modelo. Exemplo: `effort=high`.

**Mapa de Alias**: O mapa YAML sob a chave de frontmatter `models:`. As chaves são nomes de alias (ou a string vazia para a política padrão). Os valores são listas ordenadas de padrões de modelo ou outros nomes de alias.

**Aliases Embutidos (Builtin)**: O conjunto de definições de alias enviadas com o AWF, cobrindo as principais famílias de modelos entre fornecedores suportados.

**Política Padrão** (`""`): A entrada de alias cuja chave é a string vazia. Quando um fluxo de trabalho não especifica um modelo, a política padrão governa qual família de modelo é selecionada.

**Resolução**: O processo de converter um identificador de modelo ou nome de alias em um nome de modelo concreto com escopo de provedor, seguindo a lista de fallback e expandindo aliases recursivamente.

---

## 4. Sintaxe do Identificador de Modelo

### 4.1 Gramática

Uma string de identificador de modelo DEVE estar em conformidade com a seguinte gramática ABNF:

```abnf
model-identifier  = base-identifier [ "?" query-string ]

base-identifier   = bare-name
                  / provider-scoped
                  / glob-pattern

bare-name         = 1*( ALPHA / DIGIT / "-" / "_" / "." )
                    ; NÃO DEVE começar com "-" ou "."

provider-scoped   = provider-token "/" model-token

provider-token    = ALPHA 0*( ALPHA / DIGIT / "-" )
                    ; começa com letra; hifens permitidos mas não no final

model-token       = model-char 0*( model-char / "." model-char )
                    ; segmentos separados por "."; cada segmento começa com ALPHA ou DIGIT

model-char        = ALPHA / DIGIT / "-" / "_"
                    ; sublinhado é permitido apenas dentro de tokens de modelo

glob-pattern      = provider-token "/" model-glob-token

model-glob-token  = 1*( model-char / "." / "*" )
                    ; "*" é um curinga que corresponde a zero ou mais caracteres não-"/"

query-string      = param *( "&" param )

param             = param-key "=" param-value

param-key         = ALPHA 0*( ALPHA / DIGIT / "-" )
                    ; começa com letra; sem dígitos ou hifens no início

param-value       = 1*( ALPHA / DIGIT / "-" / "_" / "." )
```

**Resumo do conjunto de caracteres permitido:**

| Segmento | Caracteres permitidos | Notas |
|---------|-------------------|-------|
| Token do provedor | `[A-Za-z0-9-]` | DEVE começar com letra; NÃO DEVE terminar com `-` |
| Token do modelo | `[A-Za-z0-9-_.]` | Ponto separa segmentos de versão; sublinhado permitido dentro de um segmento apenas |
| Nome simples | `[A-Za-z0-9-_.]` | NÃO DEVE começar com `-` ou `.` |
| Curinga glob | `*` | Apenas em model-glob-token; token do provedor NÃO DEVE conter `*` |
| Chave do parâmetro | `[A-Za-z0-9-]` | DEVE começar com letra |
| Valor do parâmetro | `[A-Za-z0-9-_.]` | |

Caracteres explicitamente PROIBIDOS em todos os segmentos: espaço em branco, `@`, `!`, `#`, `$`, `%`, `^`, `&` (exceto como separador), `(`, `)`, `+`, `=`, `[`, `]`, `{`, `}`, `|`, `\`, `:`, `;`, `,`, `<`, `>`, `/` (exceto como separador provedor/modelo), `?` (exceto como separador de parâmetro), `"`, `'`.

**Notas:**

- O caractere `?` separa o identificador base da string de consulta.
- Uma implementação NÃO DEVE percent-encode ou percent-decode a string do identificador de modelo; a sintaxe é autônoma.
- Múltiplos parâmetros são separados por `&`.
- Um identificador simples sem `?` e sem `/` é tratado como um nome de alias durante a resolução (veja Seção 8).

### 4.2 Exemplos

```text
# Nome de alias simples
sonnet

# Nome de alias simples com parâmetro effort
opus?effort=high

# Nome com escopo de provedor exato
copilot/gpt-5

# Nome com escopo de provedor com parâmetro effort
copilot/claude-opus-4.5?effort=medium

# Nome com escopo de provedor com múltiplos parâmetros
openai/o3?effort=high&temperature=0.2

# Padrão glob (usado apenas em entradas de lista de alias — não em engine.model)
copilot/*sonnet*
```

### 4.3 Regras de Análise

Uma implementação DEVE analisar uma string de identificador de modelo da seguinte forma:

1. Dividir na primeira ocorrência de `?`. O lado esquerdo é o `base-identifier`; o lado direito (se presente) é a `query-string`.
2. Se o `base-identifier` contiver `/`, é um identificador com escopo de provedor ou padrão glob. O segmento antes da primeira `/` é o token do provedor; o segmento depois é o token do modelo.
3. Se o `base-identifier` não contiver `/`, é um nome simples. PODE ser um nome de alias ou um nome de modelo concreto dependendo do contexto.
4. Analisar a `query-string` como uma sequência de pares `chave=valor` separados por `&`.
5. Implementações DEVEM rejeitar identificadores de modelo onde uma chave ou valor de parâmetro contenha caracteres fora do conjunto permitido, com um erro de validação de compilação.

---

## 5. Codificação de Parâmetro estilo URL

### 5.1 Motivação

Knobs de invocação de modelo, como esforço de raciocínio, temperatura e top-p, são específicos do provedor e mudam frequentemente à medida que novos modelos são lançados. Codificá-los como parâmetros de consulta no nome do modelo mantém o mapa de alias limpo, evita a proliferação de chaves frontmatter e torna os parâmetros visíveis no ponto de uso.

### 5.2 Ponto de Fixação

Parâmetros DEVEM ser anexados à string do identificador de modelo. Eles se aplicam ao modelo ao qual estão anexados após a resolução de alias terminar em um nome de modelo com escopo de provedor concreto.

Parâmetros anexados a um nome de alias DEVEM ser encaminhados para o primeiro modelo concreto resolvido com sucesso. Uma seção posterior (Seção 8.5) define a semântica de encaminhamento com precisão.

### 5.3 Herança de Parâmetro

Quando uma entrada de lista de alias carrega parâmetros (ex: `opus?effort=high`), e o chamador também especifica parâmetros (ex: `sonnet?temperature=0.3`), aplicam-se as seguintes regras de precedência:

1. Parâmetros definidos explicitamente no identificador do **chamador** (o engine.model ou entrada de lista de alias) têm a maior precedência.
2. Parâmetros herdados de um **alias resolvido** preenchem qualquer chave não definida pelo chamador.
3. Parâmetros definidos no **alias embutido** preenchem qualquer chave não definida pelas camadas 1–2.

Isso permite que os chamadores substituam parâmetros específicos enquanto herdam o restante da definição do alias.

---

## 6. Parâmetros Definidos

### 6.1 `effort`

Controla a profundidade de raciocínio ou orçamento de pensamento para modelos que suportam raciocínio estendido (ex: `claude-opus-4.*`, `o1`, `o3`, `o4` séries).

| Valor | Descrição |
|-------|-------------|
| `low` | Tokens de raciocínio mínimos; mais rápido e menos caro |
| `medium` | Orçamento de raciocínio equilibrado (padrão do provedor onde aplicável) |
| `high` | Tokens de raciocínio máximos; maior qualidade, maior custo |

**Tipo**: string enumerada  
**Valores permitidos**: `low`, `medium`, `high`  
**Padrão**: definido pelo provedor (tipicamente `medium`)

Implementações DEVEM mapear esses valores para o parâmetro de API de controle de raciocínio nativo do provedor. Para modelos Anthropic, este é o campo `thinking.budget_tokens`; para modelos OpenAI `o`-series, este é o campo `reasoning_effort`. O mapeamento exato é específico do motor e está fora do escopo desta especificação.

Uma implementação DEVE emitir um aviso de tempo de compilação quando `effort` for definido em um modelo conhecido por não suportar raciocínio estendido.

**Exemplos:**

```yaml
# Fluxo de trabalho usando opus com esforço alto
engine:
  id: copilot
  model: opus?effort=high

# Entrada do mapa de alias com effort embutido
models:
  deep-think:
    - opus?effort=high
    - gpt-5?effort=high
```

### 6.2 `temperature`

Controla a temperatura de amostragem para modelos que a suportam. Valores mais baixos produzem saída mais determinística; valores mais altos produzem saída mais variada.

| Faixa de valor | Descrição |
|-------------|-------------|
| `0.0`–`2.0` | Valor de ponto flutuante (notação decimal, ex: `0.7`) |

**Tipo**: string de ponto flutuante decimal  
**Valores permitidos**: `0.0` até `2.0` inclusive  
**Padrão**: definido pelo provedor

Implementações DEVEM converter a string para um número de ponto flutuante antes de encaminhar para a API do provedor.

Implementações DEVEM emitir um erro de tempo de compilação se o valor estiver fora da faixa `[0.0, 2.0]` ou não puder ser analisado como um ponto flutuante decimal.

**Exemplos:**

```yaml
engine:
  id: codex
  model: openai/gpt-5?temperature=0.2

models:
  deterministic:
    - gpt-5?temperature=0.0
    - sonnet?temperature=0.0
```

### 6.3 Parâmetros Futuros

Esta especificação foi projetada para ser estendida. Versões futuras PODEM definir parâmetros adicionais. Uma implementação DEVE ignorar silenciosamente chaves de parâmetro não reconhecidas, mas SHOULD emitir um aviso para ajudar os autores a identificar erros de digitação.

Os seguintes nomes de parâmetro estão reservados para uso futuro e NÃO DEVEM ser usados para outros fins:

- `top-p`
- `top-k`
- `max-tokens`
- `seed`
- `stop`

---

## 7. Formato do Mapa de Alias

### 7.1 Representação YAML

O mapa de alias é expresso sob a chave `models:` no frontmatter do fluxo de trabalho:

```yaml
models:
  <nome-do-alias>:
    - <padrão-de-modelo-ou-alias>
    - <padrão-de-modelo-ou-alias>
    ...
```

Cada chave é um nome de alias (um identificador simples). A chave especial de string vazia (`""`) define a **política padrão** — a lista ordenada tentada quando nenhum modelo é especificado.

Cada entrada de lista é:

- Um **padrão glob** (com escopo de provedor, pode conter `*`)
- Um **nome de modelo com escopo de provedor** (sem curingas)
- Outro **nome de alias** (identificador simples, resolvido recursivamente)

Qualquer um dos itens acima PODE carregar parâmetros estilo URL.

### 7.2 Exemplo

```yaml
models:
  # Substituir o alias sonnet embutido para preferir um gateway personalizado
  sonnet:
    - mygateway/*sonnet-v3*
    - copilot/*sonnet*

  # Novo alias para tarefas de raciocínio de esforço alto
  deep-think:
    - opus?effort=high
    - gpt-5?effort=high

  # Política padrão: tentar deep-think primeiro, fallback para sonnet
  "":
    - deep-think
    - sonnet
```

### 7.3 Restrições

- Nomes de alias DEVEM corresponder a `bare-name` conforme definido na Seção 4.1.
- Nomes de alias NÃO DEVEM conter `/`, `?` ou `&`.
- O mesmo nome de alias NÃO DEVE aparecer mais de uma vez como chave na mesma camada do mapa de alias. Chaves duplicadas são um erro de tempo de compilação.
- Referências de alias circulares (diretas ou transitivas) são PROIBIDAS e DEVEM ser detectadas e relatadas como erros de tempo de compilação.
- Uma lista de alias DEVE conter pelo menos uma entrada.

---

## 8. Algoritmo de Resolução de Fallback

### 8.1 Visão Geral

A resolução converte um identificador de modelo (que pode ser um alias, um glob ou um nome concreto) em um único **nome de modelo com escopo de provedor concreto** seguindo a lista de fallback até que uma correspondência seja encontrada no catálogo de modelos do motor.

### 8.2 Entrada de Resolução

O procedimento de resolução leva:

- Um **alvo**: a string do identificador de modelo de `engine.model`, ou o nome de alias `""` se nenhum modelo for especificado.
- O **mapa de alias mesclado**: o resultado da mesclagem de três camadas descrita na Seção 10.
- O **catálogo de modelos do motor**: o conjunto de nomes de modelo concretos disponíveis para o motor configurado (com escopo de provedor, sem curingas).

### 8.3 Procedimento de Resolução

```
Resolve(alvo, mapaAlias, catálogo):
  1. Remover parâmetros do alvo → (base, params)
  2. Se base for encontrado como chave em mapaAlias:
     a. Recuperar a lista ordenada L para base.
     b. Para cada entrada E em L:
        i.  Remover parâmetros de E → (eBase, eParams)
        ii. Mesclar params ← MergeParams(params, eParams)   // chamador ganha
        iii.Se eBase for chave em mapaAlias → recursão: Resolve(eBase+MarshalParams(eParams), ...)
        iv. Se eBase for padrão glob → corresponder contra catálogo; se houver correspondência, retornar primeira correspondência + params
        v.  Se eBase for nome com escopo de provedor (sem curingas) → se presente no catálogo, retornar eBase + params
     c. Se nenhuma entrada em L resolver → continuar para o próximo passo (como se alvo fosse um nome simples)
  3. Se base corresponder exatamente à entrada do catálogo → retornar base + params
  4. Resolução FALHA: emitir erro de tempo de compilação nomeando o alias/modelo não resolvido.
```

### 8.4 Correspondência Glob

Padrões Glob DEVEM ser correspondidos usando as seguintes regras:

- `*` corresponde a zero ou mais caracteres que não incluem `/`.
- A correspondência não distingue maiúsculas de minúsculas.
- O prefixo do provedor DEVE ser correspondido exatamente (sem curingas no segmento do provedor).

Quando múltiplas entradas de catálogo correspondem a um padrão glob, a implementação DEVE selecionar a entrada com a **versão semântica mais alta** — NÃO DEVE retornar a primeira correspondência lexicográfica. Isso garante que a resolução baseada em alias sempre resolva para o modelo disponível mais recente em uma família correspondida.

#### 8.4.1 Extração de Semver

Para classificar correspondências, uma implementação DEVE extrair a string de versão de uma entrada de catálogo usando o seguinte procedimento:

1. Tomar a parte do token de modelo (após a primeira `/`).
2. Escanear da direita para a esquerda pela última ocorrência de um segmento de versão correspondente ao padrão `\d+(\.\d+)*` (um ou mais inteiros separados por ponto).
3. A string de versão extraída é usada para comparação como uma tupla semver.
4. Se nenhum segmento de versão for encontrado, a entrada é tratada como versão `0.0.0` para fins de classificação.

Exemplos de extração de versão:

| Entrada de catálogo | Versão extraída |
|---------------|------------------|
| `copilot/claude-opus-4.5` | `4.5` |
| `copilot/claude-opus-4` | `4` |
| `copilot/claude-sonnet-4.5-20250514` | `4.5` (escaneia para encontrar última sequência numérica; porção de data tratada separadamente — veja §8.4.2) |
| `openai/gpt-5` | `5` |
| `copilot/gemini-2.5-pro` | `2.5` |
| `copilot/model-without-version` | `0.0.0` |

#### 8.4.2 Comparação Semver

Versões são comparadas como tuplas ordenadas de inteiros não negativos. Uma tupla mais curta é preenchida à esquerda com zeros antes da comparação. Exemplos:

- `4.5` > `4` (ou seja, `4.5` > `4.0`)
- `2.5` > `2.0`
- `5` > `4.5` (ou seja, `5.0` > `4.5`)

Quando duas entradas têm versões idênticas e sufixos de data idênticos (ou ambos carecem de datas), a implementação SHOULD preservar a ordem do catálogo como critério de desempate.

#### 8.4.3 Seleção

```
SelectLatestMatch(padrão, catálogo):
  correspondências = [ entrada for entrada in catálogo se GlobMatch(padrão, entrada) ]
  se correspondências estiver vazio → retornar nil
  ordenar correspondências decrescente por (semver, sufixo-data)
  retornar correspondências[0]
```

### 8.5 Encaminhamento de Parâmetro

Ao recursar em um alias, os parâmetros se acumulam com semântica de "chamador ganha":

```
MergeParams(parâmetrosChamador, parâmetrosAlias):
  resultado = parâmetrosAlias
  para cada (chave, valor) em parâmetrosChamador:
    resultado[chave] = valor   // chamador sobrescreve alias
  retornar resultado
```

O conjunto de parâmetros mesclado resultante é anexado ao nome do modelo com escopo de provedor concreto resolvido.

### 8.6 Detecção de Loop

Referências de alias circulares são estritamente PROIBIDAS. Uma implementação DEVE detectar e relatar ciclos tanto no tempo de compilação quanto em tempo de execução.

#### 8.6.1 Detecção em Tempo de Compilação

Quando o mapa de alias é construído (após a mesclagem de três camadas descrita na Seção 10), a implementação DEVE realizar uma verificação de ciclo completa sobre todas as chaves de alias antes que qualquer resolução seja tentada.

Algoritmo: para cada chave de alias, realizar uma travessia em profundidade (DFS) das entradas da lista. Manter um conjunto de nomes de alias no caminho DFS atual. Se qualquer travessia alcançar uma chave de alias já no caminho atual, um ciclo é detectado e DEVE ser relatado como um erro de tempo de compilação que nomeia cada alias envolvido no ciclo.

A compilação DEVE ser abortada quando um ciclo for detectado. Um fluxo de trabalho com um mapa de alias cíclico é inválido e NÃO DEVE produzir um arquivo de bloqueio.

**Exemplo de erro:**

```
Erro: referência de alias circular detectada: deep-think → opus → deep-think
  models:
    deep-think: [opus]
    opus: [deep-think]   ← ciclo de volta para deep-think
```

#### 8.6.2 Detecção em Tempo de Execução

Em tempo de execução, uma implementação DEVE também proteger contra ciclos que evitam a detecção em tempo de compilação (ex: quando mapas de alias são construídos ou estendidos dinamicamente, ou quando entradas de catálogo alias-resolvem na inicialização do motor).

O resolvedor de tempo de execução DEVE manter um conjunto de nomes de alias visitados por chamada de resolução no caminho de resolução atual. Se `Resolve` for invocado com um nome de alias já no conjunto visitado, a implementação DEVE:

1. Abortar imediatamente a resolução desse modelo.
2. Registrar um erro que inclua a cadeia de aliases que levou ao ciclo.
3. Tratar o modelo falho como indisponível (pular para a próxima entrada de fallback se houver uma).
4. Se nenhum fallback restar, falhar a execução do fluxo de trabalho com uma mensagem de erro descritiva.

A proteção de tempo de execução é uma rede de segurança adicional e NÃO substitui a detecção em tempo de compilação.

### 8.7 Política Padrão de String Vazia

Quando `engine.model` está ausente ou vazio, a implementação DEVE usar `""` (a string vazia) como alvo para resolução. Se a chave `""` não estiver presente no mapa de alias mesclado, a implementação DEVE passar para a seleção de modelo padrão do próprio motor.

---

## 9. Aliases Embutidos (Builtin)

O AWF envia os seguintes aliases embutidos. Definições de frontmatter de fluxo de trabalho (e definições de fluxo de trabalho importadas) são mescladas sobre estes; veja Seção 10 para precedência de mesclagem.

### 9.1 Aliases de Família de Fornecedor

| Alias | Padrões (em ordem) |
|-------|---------------------|
| `sonnet` | `copilot/*sonnet*`, `anthropic/*sonnet*` |
| `haiku` | `copilot/*haiku*`, `anthropic/*haiku*` |
| `opus` | `copilot/*opus*`, `anthropic/*opus*` |
| `gpt-4.1` | `copilot/gpt-4.1*`, `openai/gpt-4.1*` |
| `gpt-5` | `copilot/gpt-5*`, `openai/gpt-5*` |
| `gpt-5-mini` | `copilot/gpt-5*mini*`, `openai/gpt-5*mini*` |
| `gpt-5-nano` | `copilot/gpt-5*nano*`, `openai/gpt-5*nano*` |
| `gpt-5-codex` | `copilot/gpt-5*codex*`, `openai/gpt-5*codex*` |
| `reasoning` | `copilot/o1*`, `copilot/o3*`, `copilot/o4*`, `openai/o1*`, `openai/o3*`, `openai/o4*` |
| `gemini-flash` | `copilot/gemini-*flash*`, `google/gemini-*flash*` |
| `gemini-flash-lite` | `copilot/gemini-*flash*lite*`, `google/gemini-*flash*lite*`, `gemini/gemini-*flash*lite*` |
| `gemini-pro` | `copilot/gemini-*pro*`, `google/gemini-*pro*` |

### 9.2 Meta-Aliases

| Alias | Resolve para (em ordem) |
|-------|------------------------|
| `small` | `mini` |
| `mini` | `haiku`, `gpt-5-mini`, `gpt-5-nano`, `gemini-flash-lite` |
| `large` | `sonnet`, `gpt-5`, `gemini-pro` |
| `auto` | `large` |

Meta-aliases referenciam outros aliases e são resolvidos recursivamente. Eles permitem que autores de fluxo de trabalho expressem níveis de capacidade (`mini`, `large`) sem se comprometer com um fornecedor específico.

### 9.3 Ausência de Política Padrão

O conjunto de alias embutido NÃO define uma entrada `""`. Se um fluxo de trabalho não definir uma entrada `""` também, o modelo padrão do próprio motor é usado.

---

## 10. Precedência de Mesclagem

### 10.1 Mesclagem de Três Camadas

O mapa de alias final usado para resolução é construído a partir de três camadas, aplicadas em ordem da prioridade mais baixa para a mais alta:

| Prioridade | Camada | Regra |
|----------|-------|------|
| 1 (mais baixa) | Aliases embutidos (Builtin) | Sempre presente; enviado com AWF |
| 2 | Aliases de fluxo de trabalho importados | Primeira importação a definir uma chave vence entre as importações |
| 3 (mais alta) | Frontmatter do fluxo de trabalho principal `models:` | Sempre vence; sobrescreve qualquer entrada de camada inferior para a mesma chave |

### 10.2 Algoritmo de Mesclagem de Payload de Modelos

O pseudocódigo a seguir define o procedimento de mesclagem exato que produz o mapa de alias unificado das três camadas:

```
MergeAliasMap(builtins, importedMaps[], frontmatterMap):

  // Passo 1: Começar de builtins (camada 1 — sempre presente)
  merged = copy(builtins)

  // Passo 2: Aplicar mapas importados em ordem BFS (camada 2 — primeiro-a-vencer entre importações)
  para cada importedMap em importedMaps:         // ordem de travessia BFS
    para cada chave, lista em importedMap:
      se chave NÃO ESTIVER EM merged:               // primeira importação a definir esta chave vence
        merged[chave] = lista
      // se chave já estiver presente, ignorar a definição desta importação

  // Passo 3: Aplicar mapa de frontmatter (camada 3 — sempre vence)
  para cada chave, lista em frontmatterMap:
    merged[chave] = lista                    // sobrescreve incondicionalmente qualquer camada anterior

  return merged
```

**Principais propriedades deste algoritmo:**

- A mesclagem é realizada no **nível de chave** — a lista inteira para uma chave é substituída, nunca mesclada entrada por entrada.
- Dentro da camada importada (passo 2), a estratégia é **primeiro-a-vencer** entre pares: uma vez que uma chave é definida por uma importação anterior, importações posteriores definindo a mesma chave são silenciosamente ignoradas.
- O fluxo de trabalho principal (passo 3) usa **último-a-vencer** em relação a todas as outras camadas: ele sempre sobrescreve.
- O algoritmo é executado **uma vez no momento da compilação** após todas as importações serem resolvidas. O resultado é um mapa estável e congelado usado para todas as chamadas de resolução subsequentes.

### 10.3 Substituição em Nível de Chave

A substituição é realizada no **nível de chave**: se o fluxo de trabalho principal define `sonnet`, a lista inteira do fluxo de trabalho principal substitui a lista `sonnet` embutida inteira. Não há mesclagem em nível de lista.

### 10.4 Prioridade de Importação

Quando múltiplos fluxos de trabalho importados definem a mesma chave de alias, a primeira importação encontrada na ordem de travessia BFS vence. Isso é consistente com a semântica de mesclagem `features:` em outros lugares no AWF.

### 10.5 Transitividade

Quando uma entrada de alias resolvido referencia outro alias (ex: `"" → sonnet`), o `sonnet` resolvido é buscado no **mesmo mapa mesclado**. O mapa mesclado é computado uma vez no momento da compilação e permanece estável durante a resolução.

---

## 11. Regras de Validação

### 11.1 Validação de Sintaxe

No momento da compilação, uma implementação DEVE:

- **V-MAF-001**: Rejeitar identificadores de modelo que não estejam em conformidade com a gramática na Seção 4.1 com erro de análise.
- **V-MAF-002**: Rejeitar valores de parâmetro para `effort` que não sejam um de `low`, `medium`, `high`.
- **V-MAF-003**: Rejeitar valores de parâmetro para `temperature` que não podem ser analisados como um ponto flutuante decimal em `[0.0, 2.0]`.
- **V-MAF-004**: Rejeitar padrões glob usados em `engine.model` (padrões glob são válidos apenas em entradas de lista de alias).
- **V-MAF-005**: Rejeitar chaves de alias que contenham `/`, `?` ou `&`.
- **V-MAF-006**: Rejeitar qualquer segmento de identificador de modelo que contenha um caractere fora do conjunto permitido definido na Seção 4.1. A implementação DEVE nomear o caractere ofensivo e o tipo de segmento (provedor, modelo, alias, chave de parâmetro ou valor de parâmetro) na mensagem de erro.

### 11.2 Validação Semântica

No momento da compilação, uma implementação DEVE:

- **V-MAF-010**: Detectar e relatar todas as referências de alias circulares usando o algoritmo DFS descrito na Seção 8.6.1. A compilação DEVE ser abortada em qualquer ciclo detectado.
- **V-MAF-011**: Emitir um aviso para chaves de parâmetro não reconhecidas (após aplicar a Seção 6 parâmetros conhecidos).
- **V-MAF-012**: Emitir um aviso quando `effort` for definido em um modelo conhecido por não suportar raciocínio estendido.

Em tempo de execução, uma implementação DEVE:

- **V-MAF-013**: Proteger contra ciclos não detectados no momento da compilação usando a proteção de conjunto visitado por chamada descrita na Seção 8.6.2. Um ciclo em tempo de execução DEVE causar uma falha de resolução imediata com um erro descritivo que inclui a cadeia de alias que levou ao ciclo.

### 11.3 Validação de Resolução

No momento da compilação, uma implementação SHOULD:

- **V-MAF-020**: Avisar quando um alias de modelo resolver para zero entradas no catálogo do motor, indicando que o alias pode estar mal configurado ou que o motor não suporta esses modelos.

---

## 12. Testes de Conformidade

### 12.1 Requisitos da Suíte de Testes

Uma implementação conforme DEVE passar em todas as categorias de teste abaixo.

### 12.2 Categorias de Teste

#### 12.2.1 Testes de Sintaxe

- **T-MAF-001**: Analisar nome de alias simples `sonnet` → base=`sonnet`, params=`{}`
- **T-MAF-002**: Analisar `opus?effort=high` → base=`opus`, params=`{effort: high}`
- **T-MAF-003**: Analisar `copilot/gpt-5` → provedor=`copilot`, modelo=`gpt-5`, params=`{}`
- **T-MAF-004**: Analisar `openai/o3?effort=low&temperature=0.2` → provedor=`openai`, modelo=`o3`, params=`{effort: low, temperature: 0.2}`
- **T-MAF-005**: Rejeitar `copilot/*sonnet*` quando usado como `engine.model` (glob não permitido lá)
- **T-MAF-006**: Rejeitar `effort=extreme` (valor de effort desconhecido)
- **T-MAF-007**: Rejeitar `temperature=3.0` (fora da faixa)
- **T-MAF-008**: Rejeitar `my model` (espaço em branco no identificador)
- **T-MAF-009**: Rejeitar `my:model` (dois pontos no identificador); mensagem de erro DEVE identificar o caractere ofensivo

#### 12.2.2 Testes de Resolução

- **T-MAF-020**: `sonnet` resolve para primeira correspondência de catálogo para `copilot/*sonnet*` ou `anthropic/*sonnet*`
- **T-MAF-021**: `auto` resolve transitivamente através de `large` → `sonnet` → modelo concreto
- **T-MAF-022**: `opus?effort=high` propaga `effort=high` para o modelo concreto resolvido
- **T-MAF-023**: Chamador `opus?effort=high` + entrada de alias `opus?effort=medium` → resolvido com `effort=high` (chamador ganha)
- **T-MAF-024**: Alias personalizado `deep-think: [opus?effort=high]` resolve via alias embutido `opus`
- **T-MAF-025**: Política padrão `""` é usada quando `engine.model` está ausente
- **T-MAF-026**: Dado catálogo `[copilot/claude-opus-4, copilot/claude-opus-4.5]` e padrão `copilot/*opus*`, resolução retorna `copilot/claude-opus-4.5` (última semver vence)
- **T-MAF-027**: Dado catálogo `[copilot/claude-sonnet-4.5-20250310, copilot/claude-sonnet-4.5-20250514]` e padrão `copilot/*sonnet*`, resolução retorna `copilot/claude-sonnet-4.5-20250514` (última data vence quando versões são iguais)
- **T-MAF-028**: Dadas entradas de catálogo sem string de versão, elas são classificadas como `0.0.0` e perdem para entradas com uma versão

#### 12.2.3 Testes de Precedência de Mesclagem

- **T-MAF-030**: Chave `sonnet` do fluxo de trabalho principal sobrescreve a chave `sonnet` embutida inteiramente
- **T-MAF-031**: Primeiro fluxo de trabalho importado a definir `mini` vence sobre importações subsequentes
- **T-MAF-032**: Fluxo de trabalho principal sempre vence sobre fluxo de trabalho importado para a mesma chave
- **T-MAF-033**: Chave definida apenas nos embutidos e ausente de todas as importações e frontmatter é preservada no mapa mesclado

#### 12.2.4 Testes de Validação

- **T-MAF-040**: Alias circular `a: [b]`, `b: [a]` é detectado e relatado como erro de tempo de compilação; compilação é abortada
- **T-MAF-041**: Ciclo mais longo `a: [b]`, `b: [c]`, `c: [a]` é detectado; mensagem de erro nomeia todos os três aliases
- **T-MAF-042**: Proteção de ciclo de tempo de execução dispara quando uma expansão de alias dinâmica cria um ciclo na inicialização do motor; resolução recorre à próxima entrada se disponível
- **T-MAF-043**: Chave de parâmetro não reconhecida `?foo=bar` produz aviso de tempo de compilação
- **T-MAF-044**: Alias sem entradas de catálogo correspondentes produz aviso de tempo de compilação

### 12.3 Checklist de Conformidade

| Requisito | ID de Teste | Nível | Status |
|-------------|---------|-------|--------|
| Análise de identificador simples | T-MAF-001 | 1 | Requerido |
| Análise de parâmetro | T-MAF-002, 004 | 1 | Requerido |
| Rejeição de glob em engine.model | T-MAF-005 | 1 | Requerido |
| Rejeição de valor de esforço inválido | T-MAF-006 | 1 | Requerido |
| Validação da faixa de temperatura | T-MAF-007 | 1 | Requerido |
| Rejeição de espaço em branco (V-MAF-006) | T-MAF-008 | 1 | Requerido |
| Rejeição de caractere ilegal com mensagem | T-MAF-009 | 1 | Requerido |
| Resolução de alias de um salto | T-MAF-020 | 2 | Requerido |
| Resolução de alias transitiva | T-MAF-021 | 2 | Requerido |
| Propagação de parâmetro | T-MAF-022 | 2 | Requerido |
| Mesclagem de parâmetro chamador-ganha | T-MAF-023 | 2 | Requerido |
| Política padrão (`""`) | T-MAF-025 | 2 | Requerido |
| Seleção de glob ciente de semver (última vence) | T-MAF-026 | 2 | Requerido |
| Desempate de sufixo de data | T-MAF-027 | 2 | Requerido |
| Mesclagem de fluxo de trabalho principal vence | T-MAF-030 | 2 | Requerido |
| Detecção de alias circular em tempo de compilação | T-MAF-040, 041 | 3 | Requerido |
| Proteção de alias circular em tempo de execução | T-MAF-042 | 3 | Requerido |
| Aviso de parâmetro não reconhecido | T-MAF-043 | 3 | Recomendado |
| Aviso de catálogo vazio | T-MAF-044 | 3 | Recomendado |

---

## Apêndices

### Apêndice A: Exemplo de Resolução Completa

#### A.1 Cenário

Um fluxo de trabalho especifica:

```yaml
engine:
  id: copilot
  model: deep-think?temperature=0.1

models:
  deep-think:
    - opus?effort=high
    - gpt-5?effort=high
```

O catálogo do Copilot contém: `copilot/claude-opus-4.5`, `copilot/gpt-5`.

#### A.2 Rastreamento de Resolução

```
Resolve("deep-think?temperature=0.1", mergedMap, catalog)
  base = "deep-think", params = {temperature: 0.1}
  "deep-think" encontrado no mapa → lista: ["opus?effort=high", "gpt-5?effort=high"]

  Entrada 1: "opus?effort=high"
    eBase = "opus", eParams = {effort: high}
    MergeParams({temperature: 0.1}, {effort: high})
      → {effort: high, temperature: 0.1}   // ambas chaves, sem conflito
    "opus" encontrado no mapa → lista: ["copilot/*opus*", "anthropic/*opus*"]

    Entrada 1.1: "copilot/*opus*"
      Correspondência glob contra catálogo:
        copilot/claude-opus-4.5 corresponde a copilot/*opus*  ✓
      Retornar "copilot/claude-opus-4.5?effort=high&temperature=0.1"
```

#### A.3 Resultado

O motor é invocado com o modelo `copilot/claude-opus-4.5` e parâmetros:
- `effort = high`
- `temperature = 0.1`

### Apêndice B: Referência de Esquema

O campo `models:` no frontmatter do AWF é definido no Esquema JSON do fluxo de trabalho principal (`pkg/parser/schemas/main_workflow_schema.json`) como segue (excerto informativo):

```json
{
  "models": {
    "type": "object",
    "description": "Definições de alias de modelo nomeadas com listas de fallback ordenadas...",
    "additionalProperties": {
      "type": "array",
      "items": {
        "type": "string",
        "description": "Um padrão glob ou nome de alias de fornecedor/modelid"
      }
    }
  }
}
```

O campo `engine.model` é definido como:

```json
{
  "model": {
    "type": "string",
    "description": "Opcional modelo LLM específico a ser usado (ex: 'claude-3-5-sonnet-20241022', 'gpt-4')."
  }
}
```

Esta especificação estende ambos os campos normalizando o formato de string que eles aceitam.

### Apêndice C: Estendendo com Novos Parâmetros

Para propor um novo parâmetro de modelo para inclusão na Seção 6:

1. A chave do parâmetro DEVE ser uma `param-key` válida conforme a gramática na Seção 4.1.
2. O parâmetro DEVE ter um conjunto de valores ou faixa claramente definidos.
3. O parâmetro DEVE mapear para um campo de API de provedor concreto para pelo menos um motor suportado.
4. O nome do parâmetro NÃO DEVE entrar em conflito com nenhum nome reservado listado na Seção 6.3.

Até que um parâmetro seja formalmente adicionado a esta especificação, autores de fluxo de trabalho PODEM usar parâmetros personalizados com o entendimento de que o AWF emitirá um aviso e encaminhará o valor como está para o motor.

### Apêndice D: Considerações de Segurança

Parâmetros de modelo são valores de configuração de tempo de compilação e não são derivados de entrada de usuário não confiável durante a execução do fluxo de trabalho. No entanto, implementações DEVEM:

- Rejeitar valores de parâmetro que caiam fora de sua faixa definida para evitar comportamento de API de provedor inesperado.
- Não expor valores de parâmetro em logs públicos, pois podem revelar informações sobre a estratégia de raciocínio ou envelope de custo de um fluxo de trabalho.
- Tratar nomes de modelo e parâmetros como configuração (não executável) para evitar injeção em comandos shell.

---

## Referências

### Referências Normativas

- **[RFC 2119]** Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels", BCP 14, RFC 2119, March 1997. <https://www.ietf.org/rfc/rfc2119.txt>
- **[RFC 3986]** Berners-Lee, T. et al., "Uniform Resource Identifier (URI): Generic Syntax", RFC 3986, January 2005. <https://www.ietf.org/rfc/rfc3986.txt>
- **[AWF-SCHEMA]** Esquema JSON do Fluxo de Trabalho Principal do GitHub Agentic Workflows. `pkg/parser/schemas/main_workflow_schema.json`

### Referências Informativas

- **[AWF-ENGINES]** GitHub Agentic Workflows — Referência de Motores de IA. <https://gh-aw.pages.dev/reference/engines/>
- **[AWF-ET-SPEC]** GitHub Agentic Workflows — Especificação de Effective Tokens. <https://gh-aw.pages.dev/reference/effective-tokens-specification/>
- **[ANTHROPIC-THINKING]** Anthropic — Documentação de Extended Thinking. <https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking>
- **[OPENAI-REASONING]** OpenAI — Guia de modelos de raciocínio. <https://platform.openai.com/docs/guides/reasoning>

---

## Log de Alterações

### Versão 1.1.0 (Rascunho)

- **Adicionado**: Correspondência glob ciente de semver (§8.4): quando múltiplas entradas de catálogo correspondem a um glob, a entrada com a versão semântica mais alta é selecionada; sufixo de data usado como desempate.
- **Adicionado**: Tabela de restrição de caractere estrita e lista de caracteres proibidos para todos os segmentos de identificador (§4.1); nova regra de validação V-MAF-006 e casos de teste T-MAF-008/009.
- **Adicionado**: Detecção de ciclo de tempo de execução (§8.6.2): o resolvedor DEVE manter um conjunto visitado por chamada e falhar rapidamente na expansão de alias reentrante; adicionado V-MAF-013 e T-MAF-042.
- **Aprimorado**: Detecção de ciclo em tempo de compilação (§8.6.1): expandido de uma única frase para um algoritmo DFS completo com requisitos de mensagem de erro.
- **Adicionado**: Algoritmo de pseudocódigo de mesclagem de carga útil de modelos (§10.2) tornando explícita a mesclagem de três camadas.
- **Adicionado**: Teste de precedência de mesclagem T-MAF-033 (chaves apenas de embutidos são preservadas no mapa mesclado).

### Versão 1.0.0 (Rascunho)

- Lançamento inicial da especificação definindo sintaxe de identificador de modelo, codificação de parâmetro estilo URL, formato de mapa de alias, algoritmo de resolução de fallback, aliases embutidos, precedência de mesclagem e testes de conformidade.
- Definido parâmetro `effort` com valores `low | medium | high`.
- Definido parâmetro `temperature` com faixa `[0.0, 2.0]`.
- Nomes de parâmetro futuros reservados: `top-p`, `top-k`, `max-tokens`, `seed`, `stop`.

---

*Copyright © 2026 Equipe do GitHub Agentic Workflows. Todos os direitos reservados.*
