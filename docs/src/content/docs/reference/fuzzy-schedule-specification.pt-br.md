---
title: Especificação de Schedule Difuso
description: Especificação formal para a sintaxe de tempo de schedule difuso seguindo convenções W3C
sidebar:
  order: 1360
---

**Versão**: 1.2.0
**Status**: Especificação de Rascunho  
**Versão Mais Recente**: [fuzzy-schedule-specification](/gh-aw/reference/fuzzy-schedule-specification/)  
**Editor**: Equipe do GitHub Agentic Workflows

---

## Resumo

Esta especificação define a Sintaxe de Tempo de Schedule Difuso (Fuzzy Schedule Time Syntax), uma linguagem de agendamento amigável para humanos para GitHub Agentic Workflows que distribui automaticamente horários de execução de fluxo de trabalho para evitar picos de carga no servidor. A sintaxe suporta agendas diárias, horárias, semanais e baseadas em intervalo com restrições de tempo opcionais e conversões de fuso horário. A especificação inclui um algoritmo de dispersão determinístico que usa funções de hash para atribuir horários de execução consistentes aos fluxos de trabalho com base em seus identificadores, garantindo comportamento previsível em múltiplas compilações enquanto distribui a carga na infraestrutura de uma organização.

## Status deste Documento

Esta seção descreve o status deste documento no momento da publicação. Este é um rascunho de especificação e pode ser atualizado, substituído ou tornado obsoleto por outros documentos a qualquer momento.

Este documento é regido pelo processo de especificações do projeto GitHub Agentic Workflows.

## Índice

1. [Introdução](#1-introdução)
2. [Conformidade](#2-conformidade)
3. [Sintaxe Principal](#3-sintaxe-principal)
4. [Especificações de Tempo](#4-especificações-de-tempo)
5. [Suporte a Fuso Horário](#5-suporte-a-fuso-horário)
6. [Algoritmo de Dispersão](#6-algoritmo-de-dispersão)
7. [Geração de Expressão Cron](#7-geração-de-expressão-cron)
8. [Salvaguardas](#8-salvaguardas)
9. [Tratamento de Erros](#9-tratamento-de-erros)
10. [Testes de Conformidade](#10-testes-de-conformidade)
11. [Notas de Sincronização](#11-notas-de-sincronização)
12. [Esquema de Saída de Calendário](#12-esquema-de-saída-de-calendário)

---

## 1. Introdução

### 1.1 Objetivo

A Sintaxe de Tempo de Schedule Difuso atende ao problema de picos de carga no servidor que ocorrem quando múltiplos fluxos de trabalho são executados simultaneamente usando agendas de tempo fixo. Expressões cron tradicionais exigem especificações de tempo explícitas, levando os desenvolvedores a usarem horários convenientes (ex: meia-noite, na hora cheia) que criam concentração de carga. Esta especificação define uma sintaxe de linguagem natural que distribui automaticamente horários de execução enquanto preserva a semântica da agenda.

### 1.2 Escopo

Esta especificação abrange:

- Expressões de agenda de linguagem natural para agendas diárias, horárias, semanais e baseadas em intervalo
- Sintaxe de restrição de tempo usando modificadores `around` e `between`
- Sintaxe de conversão de fuso horário para tradução de tempo local para UTC
- Algoritmo de dispersão determinístico para distribuição de horário de execução
- Geração de expressão cron a partir da sintaxe difusa
- Requisitos de validação e tratamento de erros

Esta especificação NÃO abrange:

- Sintaxe de expressão cron padrão (tratada pelo GitHub Actions)
- Padrões de agenda mensais ou anuais
- Ajuste de agenda dinâmico com base em métricas de carga
- Resolução de conflito de agenda entre fluxos de trabalho

### 1.3 Objetivos de Design

Esta especificação prioriza:

1. **Legibilidade humana**: Expressões de linguagem natural que comunicam claramente a intenção
2. **Distribuição de carga**: A dispersão automática evita a execução simultânea de fluxos de trabalho
3. **Determinismo**: O mesmo identificador de fluxo de trabalho sempre produz o mesmo horário de execução
4. **Previsibilidade**: Horários de execução permanecem consistentes entre recompilações
5. **Consciência de fuso horário**: Suporte para especificações de tempo local com conversão UTC

---

## 2. Conformidade

### 2.1 Classes de Conformidade

Uma **implementação conforme** é um parser que satisfaz todos os requisitos MUST, MUST NOT, REQUIRED, SHALL e SHALL NOT nesta especificação.

Uma **expressão de schedule difuso conforme** é uma string de agenda que está em conformidade com a gramática definida na Seção 3 e produz um placeholder cron difuso válido.

Uma **implementação de dispersão conforme** é uma implementação que satisfaz todos os requisitos do algoritmo de dispersão na Seção 6.

### 2.2 Notação de Requisitos

As palavras-chave "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY" e "OPTIONAL" neste documento devem ser interpretadas como descrito em [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

### 2.3 Níveis de Conformidade

**Nível 1 (Básico)**: Suporta agendas diárias e semanais sem restrições de tempo

**Nível 2 (Padrão)**: Adiciona suporte para restrições de tempo (`around`, `between`) e agendas horárias

**Nível 3 (Completo)**: Inclui conversão de fuso horário, agendas de intervalo e padrões bi-semanais/tri-semanais

---

## 3. Sintaxe Principal

### 3.1 Definição de Gramática

Uma expressão de schedule difuso DEVE estar em conformidade com a seguinte gramática ABNF:

```text
fuzzy-schedule  = daily-schedule / hourly-schedule / weekly-schedule / interval-schedule

daily-schedule  = "daily" [time-constraint]
weekly-schedule = "weekly" ["on" weekday] [time-constraint]
hourly-schedule = "hourly" / ("every" hour-interval)
interval-schedule = "every" (minute-interval / hour-interval / day-interval / week-interval)

time-constraint = around-constraint / between-constraint
around-constraint = "around" time-spec
between-constraint = "between" time-spec "and" time-spec

time-spec       = (hour-24 ":" minute) [utc-offset]
                / (hour-12 am-pm) [utc-offset]
                / time-keyword [utc-offset]

time-keyword    = "midnight" / "noon"
am-pm           = "am" / "pm"
utc-offset      = "utc" ("+" / "-") (hours / hours ":" minutes)

weekday         = "sunday" / "monday" / "tuesday" / "wednesday" 
                / "thursday" / "friday" / "saturday"

hour-24         = 1*2DIGIT  ; 0-23
hour-12         = 1*2DIGIT  ; 1-12
minute          = 2DIGIT    ; 00-59
hours           = 1*2DIGIT
minutes         = 2DIGIT

minute-interval = 1*DIGIT ("m" / "minutes" / "minute")
hour-interval   = 1*DIGIT ("h" / "hours" / "hour")
day-interval    = 1*DIGIT ("d" / "days" / "day")
week-interval   = 1*DIGIT ("w" / "weeks" / "week")
```

### 3.2 Agendas Diárias

#### 3.2.1 Agenda Diária Básica

Uma expressão de agenda diária básica SHALL ter a forma:

```yaml
daily
```

Uma implementação DEVE gerar um placeholder cron difuso: `FUZZY:DAILY * * *`

O horário de execução SHALL ser disperso deterministicamente ao longo de todas as 24 horas e 60 minutos do dia.

#### 3.2.2 Diário em Torno de um Horário

Uma expressão de agenda diária em torno de um horário SHALL ter a forma:

```yaml
daily around <time-spec>
```

Uma implementação DEVE gerar um placeholder cron difuso: `FUZZY:DAILY_AROUND:HH:MM * * *`

O horário de execução SHALL ser disperso dentro de uma janela de ±60 minutos ao redor do horário especificado.

**Exemplo**:
```yaml
daily around 14:00
# Gera: FUZZY:DAILY_AROUND:14:0 * * *
# Dispersa dentro da janela: 13:00 a 15:00
```

#### 3.2.3 Diário Entre Horários

Uma expressão de agenda diária entre horários SHALL ter a forma:

```yaml
daily between <start-time> and <end-time>
```

Uma implementação DEVE gerar um placeholder cron difuso: `FUZZY:DAILY_BETWEEN:START_H:START_M:END_H:END_M * * *`

O horário de execução SHALL ser disperso uniformemente dentro do intervalo de tempo especificado, incluindo a manipulação de intervalos que cruzam a meia-noite.

**Exemplo**:
```yaml
daily between 9:00 and 17:00
# Gera: FUZZY:DAILY_BETWEEN:9:0:17:0 * * *
# Dispersa dentro da janela: 09:00 a 17:00

daily between 22:00 and 02:00
# Gera: FUZZY:DAILY_BETWEEN:22:0:2:0 * * *
# Dispersa dentro da janela: 22:00 a 02:00 (cruzando a meia-noite)
```

### 3.3 Agendas Semanais

#### 3.3.1 Agenda Semanal Básica

Uma expressão de agenda semanal básica SHALL ter a forma:

```yaml
weekly
```

Uma implementação DEVE gerar um placeholder cron difuso: `FUZZY:WEEKLY * * *`

A execução SHALL ser dispersa ao longo de todos os sete dias da semana e de todas as horas/minutos de cada dia.

#### 3.3.2 Semanal com Especificação de Dia

Uma expressão de agenda de dia semanal SHALL ter a forma:

```yaml
weekly on <weekday>
```

Uma implementação DEVE gerar um placeholder cron difuso: `FUZZY:WEEKLY:DOW * * DOW`

**Exemplo**:
```yaml
weekly on monday
# Gera: FUZZY:WEEKLY:1 * * 1
# Dispersa ao longo de todas as horas na segunda-feira
```

#### 3.3.3 Semanal com Restrições de Tempo

Uma agenda semanal PODE incluir restrições de tempo usando `around` ou `between`:

```yaml
weekly on <weekday> around <time-spec>
weekly on <weekday> between <start-time> and <end-time>
```

**Exemplo**:
```yaml
weekly on friday around 17:00
# Gera: FUZZY:WEEKLY:5:AROUND:17:0 * * 5
# Dispersa sexta-feira 16:00-18:00
```

### 3.4 Agendas Horárias

#### 3.4.1 Agenda Horária Básica

Uma expressão de agenda horária básica SHALL ter a forma:

```yaml
hourly
```

Uma implementação DEVE gerar um placeholder cron difuso: `FUZZY:HOURLY * * *`

O offset do minuto SHALL ser disperso ao longo de 0-59 minutos, mas permanecer consistente para cada hora.

**Exemplo**:
```yaml
hourly
# Gera: FUZZY:HOURLY * * *
# Pode dispersar para: 43 * * * * (executa no minuto 43 de cada hora)
```

#### 3.4.2 Agendas de Intervalo de Hora

Uma expressão de agenda de intervalo de hora SHALL ter a forma:

```yaml
every <N>h
every <N> hours
every <N> hour
```

Onde `<N>` DEVE ser um número inteiro positivo.

Uma implementação DEVE gerar um placeholder cron difuso: `FUZZY:HOURLY:<N> * * *`

Intervalos de hora válidos SHOULD ser: 1, 2, 3, 4, 6, 8, 12 (fatores de 24 para distribuição uniforme).

**Exemplo**:
```yaml
every 2h
# Gera: FUZZY:HOURLY:2 * * *
# Pode dispersar para: 53 */2 * * * (executa no minuto 53 a cada 2 horas)
```

### 3.5 Agendas de Período Especial

#### 3.5.1 Agenda Bi-semanal

Uma expressão de agenda bi-semanal SHALL ter a forma:

```yaml
bi-weekly
```

Uma implementação DEVE gerar um placeholder cron difuso: `FUZZY:BI-WEEKLY * * *`

A agenda SHALL ser executada uma vez a cada 14 dias com horário disperso.

#### 3.5.2 Agenda Tri-semanal

Uma expressão de agenda tri-semanal SHALL ter a forma:

```yaml
tri-weekly
```

Uma implementação DEVE gerar um placeholder cron difuso: `FUZZY:TRI-WEEKLY * * *`

A agenda SHALL ser executada uma vez a cada 21 dias com horário disperso.

### 3.6 Agendas de Intervalo

Uma expressão de agenda de intervalo SHALL ter a forma:

```yaml
every <N> <unit>
```

Onde:
- `<N>` DEVE ser um número inteiro positivo
- `<unit>` DEVE ser um de: `minutes`, `minute`, `m`, `hours`, `hour`, `h`, `days`, `day`, `d`, `weeks`, `week`, `w`

Uma implementação DEVE gerar expressões cron apropriadas com base na unidade:

- Minutos: `*/N * * * *` (mínimo N=5 por restrição do GitHub Actions)
- Horas: `FUZZY:HOURLY:N * * *` (minuto disperso)
- Dias: `0 0 */N * *` (meia-noite fixa)
- Semanas: `0 0 */N*7 * *` (meia-noite de domingo fixa)

**Exemplo**:
```yaml
every 5 minutes
# Gera: */5 * * * *

every 6h
# Gera: FUZZY:HOURLY:6 * * *

every 2 days
# Gera: 0 0 */2 * *
```

### 3.7 Normas de Erro para Expressões de Agenda Inválidas

A tabela a seguir especifica o comportamento normativo (requisitos MUST/SHALL) para expressões de agenda difusa malformadas ou irreconhecíveis encontradas durante a compilação. Essas normas aplicam-se no momento da análise (quando o compilador processa o frontmatter do fluxo de trabalho) e no momento do teste (quando a suíte de testes de conformidade exerce o parser com entradas inválidas).

| # | Condição de Erro | Exemplo de Entrada | Comportamento MUST/SHALL | Código de Erro |
|---|----------------|---------------|---------------------|------------|
| E-01 | Keyword de agenda desconhecida (não é um de `daily`, `weekly`, `hourly`, `bi-weekly`, `tri-weekly`, `every`) | `monthly` | A implementação DEVE rejeitar com um erro descritivo nomeando a palavra-chave não reconhecida e listando palavras-chave válidas | `UNKNOWN_KEYWORD` |
| E-02 | Hora fora da faixa no formato 24h | `daily around 25:00` | A implementação DEVE rejeitar; a mensagem de erro DEVE declarar a faixa de hora válida (0–23) e o valor ofensivo | `HOUR_OUT_OF_RANGE` |
| E-03 | Minuto fora da faixa | `daily around 14:65` | A implementação DEVE rejeitar; a mensagem de erro DEVE declarar a faixa de minuto válida (0–59) e o valor ofensivo | `MINUTE_OUT_OF_RANGE` |
| E-04 | Keyword `around` sem especificação de tempo | `daily around` | A implementação DEVE rejeitar; a mensagem de erro DEVE incluir um exemplo de uso correto de `around` | `MISSING_TIME_SPEC` |
| E-05 | Keyword `between` com apenas um argumento de tempo | `daily between 9:00` | A implementação DEVE rejeitar; a mensagem de erro DEVE declarar que `between` requer um horário de início e um de término conectados por `and` | `INCOMPLETE_RANGE` |
| E-06 | Faixa `between` onde início é igual a término | `daily between 14:00 and 14:00` | A implementação DEVE rejeitar; uma janela de duração zero não pode dispersar horários de execução | `ZERO_DURATION_RANGE` |
| E-07 | Dia da semana desconhecido em `weekly on <day>` | `weekly on mondey` | A implementação DEVE rejeitar com uma sugestão de "você quis dizer" quando a entrada diferir de um dia da semana válido por um caractere | `UNKNOWN_WEEKDAY` |
| E-08 | Unidade de intervalo inválida | `every 5 fortnights` | A implementação DEVE rejeitar; a mensagem de erro DEVE listar unidades válidas (`minutes`, `hours`, `days`, `weeks` e suas abreviações) | `UNKNOWN_UNIT` |
| E-09 | Valor de intervalo abaixo do mínimo permitido pelo GitHub Actions | `every 2 minutes` | A implementação DEVE rejeitar; a mensagem de erro DEVE declarar o intervalo mínimo permitido (5 minutos para a unidade `minutes`) e a fonte da restrição do GitHub Actions | `INTERVAL_TOO_SMALL` |
| E-10 | Valor de intervalo não inteiro | `every 1.5 hours` | A implementação DEVE rejeitar; valores de intervalo fracionários não são suportados | `NON_INTEGER_INTERVAL` |

**Notas normativas**:

- Todas as mensagens de erro DEVEM ser direcionadas ao console do usuário (stderr) e DEVEM ser legíveis por humanos.
- Implementações NÃO DEVEM silenciosamente retornar a uma agenda padrão quando a entrada for inválida; todos os erros nas linhas E-01 a E-10 DEVEM causar falha na compilação com um código de saída diferente de zero.
- Implementações NÃO DEVEM tentar a correção automática da expressão de agenda. Guia de correção acionável na mensagem de erro é preferível à correção silenciosa.

---

## 4. Especificações de Tempo

### 4.1 Requisitos de Formato de Tempo

Uma implementação DEVE suportar os seguintes formatos de tempo:

#### 4.1.1 Formato 24 Horas

O formato 24 horas SHALL usar o padrão `HH:MM`:

- Horas DEVEM estar na faixa 0-23
- Minutos DEVEM estar na faixa 0-59
- Zeros à esquerda PODEM ser omitidos para horas
- Minutos DEVEM usar dois dígitos com zero à esquerda, se necessário

**Exemplos válidos**: `00:00`, `9:30`, `14:00`, `23:59`

#### 4.1.2 Formato 12 Horas

O formato 12 horas SHALL usar o padrão `H[H]am` ou `H[H]pm`:

- Horas DEVEM estar na faixa 1-12
- Indicador AM/PM DEVE ser `am` ou `pm` em minúsculas
- Minutos PODEM ser omitidos (padrão para :00)
- Dois pontos e minutos PODEM ser incluídos (ex: `3:30pm`)

**Exemplos válidos**: `1am`, `12pm`, `11pm`, `9am`, `3:30pm`

**Regras de conversão**:
- `12am` converte para 00:00 (meia-noite)
- `12pm` converte para 12:00 (meio-dia)
- `1am-11am` converte para 01:00-11:00
- `1pm-11pm` converte para 13:00-23:00

#### 4.1.3 Keywords de Tempo

Uma implementação DEVE suportar as seguintes keywords de tempo:

- `midnight`: Representa 00:00 (início do dia)
- `noon`: Representa 12:00 (meio do dia)

Keywords DEVEM não distinguir entre maiúsculas e minúsculas.

### 4.2 Requisitos de Faixa de Tempo

#### 4.2.1 Especificação de Janela

Ao usar `around <time>`, a implementação DEVE usar uma janela de ±60 minutos centrada no horário especificado.

A janela DEVE manipular limites de dia corretamente:
- `around 00:30` cria janela: 23:30 (dia anterior) a 01:30
- `around 23:30` cria janela: 22:30 a 00:30 (próximo dia)

#### 4.2.2 Especificação de Faixa

Ao usar `between <start> and <end>`, a implementação DEVE:

1. Aceitar faixas dentro de um único dia (ex: `9:00` a `17:00`)
2. Aceitar faixas que cruzam a meia-noite (ex: `22:00` a `02:00`)
3. Calcular o tamanho da faixa corretamente para faixas que cruzam a meia-noite
4. Distribuir horários dispersos uniformemente dentro da faixa

Para faixas que cruzam a meia-noite onde início > término:
- Tamanho da faixa = (24*60 - minutos_início) + minutos_término

**Exemplo**:
```yaml
between 22:00 and 02:00
# Faixa: 22:00, 22:01, ..., 23:59, 00:00, ..., 02:00
# Duração: 4 horas (240 minutos)
```

---

## 5. Suporte a Fuso Horário

### 5.1 Sintaxe de Offset UTC

Uma implementação DEVE suportar especificações de offset UTC usando o formato:

```text
utc-offset = "utc" ("+" / "-") valor-offset
valor-offset = horas / horas ":" minutos
```

Onde:
- `horas` PODE ter 1 ou 2 dígitos
- `minutos` DEVE ter 2 dígitos quando especificado
- Offset DEVE estar na faixa UTC-12:00 a UTC+14:00

**Exemplos válidos**: `utc+9`, `utc-5`, `utc+05:30`, `utc-08:00`

### 5.2 Conversão de Fuso Horário

#### 5.2.1 Algoritmo de Conversão

Quando um offset UTC é especificado, a implementação DEVE:

1. Analisar o valor de tempo local
2. Analisar o valor de offset UTC (em minutos)
3. Subtrair o offset do tempo local para obter o tempo UTC
4. Manipular a quebra de dia corretamente

**Fórmula**: `Tempo_UTC = tempo_local - offset`

**Exemplo**:
```
tempo_local = 14:00 (2 PM)
offset = +9 horas (JST)
Tempo_UTC = 14:00 - 9:00 = 05:00 (5 AM UTC)
```

#### 5.2.2 Manipulação de Limite de Dia

A implementação DEVE manipular limites de dia ao converter horários:

- Resultados negativos DEVEM quebrar para o dia anterior (adicionar 24 horas)
- Resultados ≥24:00 DEVEM quebrar para o dia seguinte (subtrair 24 horas)
- Operações de quebra DEVEM preservar a precisão do minuto

**Exemplo**:
```
tempo_local = 02:00 (2 AM)
offset = +9 horas
Tempo_UTC = 02:00 - 9:00 = -7:00 → 17:00 (dia anterior)
```

### 5.3 Abreviações de Fuso Horário Comuns

Uma implementação SHOULD reconhecer abreviações de fuso horário comuns:

| Abreviação | Offset UTC | Notas |
|--------------|------------|-------|
| PST | UTC-8 | Pacific Standard Time |
| PDT | UTC-7 | Pacific Daylight Time |
| EST | UTC-5 | Eastern Standard Time |
| EDT | UTC-4 | Eastern Daylight Time |
| JST | UTC+9 | Japan Standard Time |
| IST | UTC+5:30 | India Standard Time |

Implementações PODEM emitir avisos para abreviações ambíguas (ex: "PT" poderia ser PST ou PDT).

---

## 6. Algoritmo de Dispersão

### 6.1 Objetivo do Algoritmo

O algoritmo de dispersão DEVE fornecer:

1. **Determinismo**: O mesmo identificador de fluxo de trabalho produz o mesmo horário disperso
2. **Distribuição**: Horários dispersos distribuem-se uniformemente ao longo da faixa permitida
3. **Estabilidade**: Horários dispersos permanecem constantes entre recompilações
4. **Unicidade**: Diferentes identificadores de fluxo de trabalho produzem diferentes horários dispersos

O algoritmo de dispersão usa as seguintes entidades de entrada formais:

| Entidade | Tipo | Restrições | Descrição |
|---|---|---|---|
| `workflow_identifier` | string | MUST ser não vazio; SHOULD usar formato `owner/repo/path/to/workflow.md` | Identificador canônico hasheado para seleção de dispersão determinística |
| `schedule_string` | string | MUST corresponder a uma forma de placeholder difuso suportada (`FUZZY:*`) | Expressão de agenda analisada que determina o ramo do algoritmo |
| `seed` | unsigned 32-bit integer | MUST ser derivado deterministicamente de `workflow_identifier` usando a função de hash configurada | Semente derivada de hash usada para operações de módulo |
| `window_minutes` | integer | MUST ser positivo; NÃO DEVE exceder 1440 | Janela de busca de minuto candidato para dispersão around/between |

### 6.2 Requisitos da Função de Hash

#### 6.2.1 Seleção de Algoritmo de Hash

Uma implementação DEVE usar uma função de hash que satisfaça os seguintes requisitos:

1. **Determinismo**: A função de hash DEVE produzir a mesma saída para a mesma entrada em todas as plataformas e execuções
2. **Distribuição**: A função de hash SHOULD produzir saídas uniformemente distribuídas em todo o espaço de hash
3. **Estabilidade**: A função de hash NÃO DEVE alterar o comportamento entre diferentes versões da implementação
4. **Saída inteira**: A função de hash DEVE produzir uma saída inteira adequada para operações de módulo

Uma implementação SHOULD usar o algoritmo de hash FNV-1a (Fowler-Noll-Vo) de 32 bits como implementação de referência:

```
hash = FNV_offset_basis
for each byte in input:
    hash = hash XOR byte
    hash = hash * FNV_prime
return hash

Onde:
    FNV_offset_basis = 2166136261 (0x811c9dc5)
    FNV_prime = 16777619 (0x01000193)
```

Outras funções de hash adequadas PODEM ser usadas, como MurmurHash, xxHash ou CityHash, desde que atendam aos requisitos acima.

#### 6.2.2 Formato do Identificador de Fluxo de Trabalho

O identificador de fluxo de trabalho usado para hashing DEVE ser construído como:

```
workflow_identifier = repository_slug + "/" + workflow_file_path
```

Onde:
- `repository_slug` é o formato `owner/repo`
- `workflow_file_path` é o caminho relativo a partir da raiz do repositório

**Exemplo**: `github/gh-aw/.github/workflows/daily-report.md`

Este formato garante que fluxos de trabalho com o mesmo nome de arquivo em repositórios diferentes recebam horários de execução diferentes.

### 6.3 Faixas de Dispersão

#### 6.3.1 Dispersão de Agenda Diária

Para `FUZZY:DAILY * * *` e `FUZZY:DAILY_WEEKDAYS * * *`, uma implementação DEVE usar o **pool ponderado de slot de tempo diário** para selecionar o horário de execução:

1. Construir um pool ponderado de slots de tempo (hora, minuto) usando três níveis de preferência:
   - **BEST** (peso 3): horas 02–05 UTC, minutos ímpares `{7, 13, 23, 37, 43, 53}` → 72 slots
   - **GOOD** (peso 2): horas 10–12 UTC, minutos `[5, 54]` → 300 slots
   - **OK** (peso 1): horas 19–23 UTC, minutos `[5, 54]` → 250 slots
   - Tamanho total do pool: 622 slots
2. Selecionar slot: `index = hash(workflow_identifier) % pool_size`
3. Extrair `(hora, minuto)` do slot selecionado
4. Gerar cron: `<minuto> <hora> * * *`  (ou `* * 1-5` para variante de dia da semana)

O pool é pré-computado uma vez. Como cada nível aparece proporcionalmente no pool, um slot selecionado aleatoriamente tem 3× mais probabilidade de cair na janela BEST do que na janela OK.

**Exemplo**:
```
pool_size = 622
hash("github/gh-aw/workflow.md") % 622 = 84
slot[84] = (hora=2, minuto=23)  # nível BEST
cron = "23 2 * * *"  (2:23 AM UTC)
```

#### 6.3.2 Dispersão Diária Around

Para `FUZZY:DAILY_AROUND:HH:MM * * *`:

1. Calcular horário de destino em minutos: `target_minutes = HH * 60 + MM`
2. Definir janela: `[-60, +59]` minutos do destino
3. Calcular hash módulo 120 (tamanho da janela)
4. Calcular offset: `offset = hash_result - 60`
5. Calcular horário disperso: `scattered_minutes = target_minutes + offset`
6. Manipular quebra de dia (manter dentro de 0-1439)
7. Converter para hora e minuto

**Exemplo**:
```
target = 14:00 (840 minutos)
hash % 120 = 73
offset = 73 - 60 = 13
scattered = 840 + 13 = 853 minutos
hora = 853 / 60 = 14
minuto = 853 % 60 = 13
cron = "13 14 * * *"  (2:13 PM, dentro da janela 13:00-15:00)
```

#### 6.3.3 Dispersão Diária Between

Para `FUZZY:DAILY_BETWEEN:START_H:START_M:END_H:END_M * * *`:

1. Calcular horários de início e término em minutos
2. Calcular tamanho da faixa (manipulando cruzamento da meia-noite)
3. Calcular hash módulo range_size
4. Adicionar hash_result aos start_minutes
5. Manipular quebra de dia
6. Converter para hora e minuto

**Para faixas que cruzam a meia-noite** (início > término):
```
range_size = (24 * 60 - start_minutes) + end_minutes
```

**Exemplo**:
```
range = 9:00 a 17:00
start_minutes = 540, end_minutes = 1020
range_size = 1020 - 540 = 480 minutos (8 horas)
hash % 480 = 217
scattered = 540 + 217 = 757 minutos
hora = 757 / 60 = 12
minuto = 757 % 60 = 37
cron = "37 12 * * *"  (12:37 PM)
```

#### 6.3.4 Dispersão de Agenda Horária

Para `FUZZY:HOURLY * * *`:

1. Calcular hash módulo 60
2. Usar o resultado como offset de minuto
3. Gerar cron: `<minuto> * * * *`

**Exemplo**:
```
hash % 60 = 43
cron = "43 * * * *"  (executa no minuto 43 de cada hora)
```

Para `FUZZY:HOURLY:N * * *`:

1. Calcular hash módulo 60
2. Usar o resultado como offset de minuto
3. Gerar cron: `<minuto> */N * * *`

**Exemplo**:
```
interval = 2 horas
hash % 60 = 53
cron = "53 */2 * * *"  (executa no minuto 53 a cada 2 horas)
```

#### 6.3.5 Dispersão de Agenda Semanal

Para `FUZZY:WEEKLY * * *` e `FUZZY:WEEKLY:DOW * * *`:

1. Selecionar dia da semana: `weekday = hash(workflow_identifier) % 7` (0=Domingo, 6=Sábado)  
   Para `FUZZY:WEEKLY:DOW`, o dia é fixado na expressão em vez disso.
2. Selecionar horário do **pool ponderado de slot de tempo diário** (Seção 6.3.1)
3. Gerar cron: `<minuto> <hora> * * <dia>`

Ambos os padrões usam o mesmo pool ponderado da agenda diária, garantindo que os horários de execução prefiram os níveis BEST/GOOD/OK em vez de distribuir de forma plana ao longo do dia inteiro.

**Exemplo**:
```
weekly on monday
dia = 1 (Segunda-feira)
seleção de pool → (hora=2, minuto=23)  # nível BEST
cron = "23 2 * * 1"  (Segunda-feira 2:23 AM UTC)
```

#### 6.3.6 Dispersão Bi-semanal e Tri-semanal

Para `FUZZY:BI-WEEKLY * * *` e `FUZZY:TRI-WEEKLY * * *`:

1. Selecionar horário do **pool ponderado de slot de tempo diário** (Seção 6.3.1)
2. Gerar cron: `<minuto> <hora> */14 * *` (bi-semanal) ou `<minuto> <hora> */21 * *` (tri-semanal)

Ambos os padrões usam o mesmo pool ponderado para garantir a execução durante janelas preferenciais de baixo tráfego.

### 6.4 Evitar Minutos de Pico

Para reduzir colisões de agendamento com outros jobs cron comumente agendados, implementações DEVEM aplicar dois passes de prevenção de minuto após computar o valor de minuto disperso bruto.

#### 6.4.1 Prevenção de Limite de Hora (`avoidHourBoundary`)

Minutos próximos ao limite da hora (0–4 e 55–59) estão sujeitos a carga elevada na infraestrutura do GitHub Actions, especialmente às 00:00 UTC.

Uma implementação DEVE remapear valores de minuto da seguinte forma:

| Faixa de Entrada | Saída |
|-------------|--------|
| [0, 4] | minuto + 5 |
| [55, 59] | minuto − 5 |
| [5, 54] | inalterado |

Isso garante que todos os valores de minuto gerados estejam em [5, 54].

**Escopo**: Aplicado a TODOS os padrões de dispersão direcionada (DAILY_AROUND, DAILY_BETWEEN, WEEKLY_AROUND e suas variantes de dia da semana).

#### 6.4.2 Prevenção de Minutos de Pico (`avoidPeakMinutes`)

Períodos conhecidos de alto tráfego exigem a prevenção de minutos que caem dentro de ±3 dos valores de minuto de pico.

Uma implementação DEVE aplicar o seguinte remapeamento **após** `avoidHourBoundary`:

| Condição | Faixa de Prevenção | Substituição |
|-----------|-------------|-------------|
| hora ∈ [6, 9] E minuto ∈ [27, 33] | [27, 33] | 34 |
| hora ∈ [14, 18] E minuto ∈ [12, 18] | [12, 18] | 19 |
| hora ∈ [14, 18] E minuto ∈ [42, 48] | [42, 48] | 49 |

**Racional**:
- **Pico matinal da UE** (06:00–09:59 UTC): `:30` é um minuto cron comumente usado. Ficar a 3 minutos de distância (evitando [27,33]) reduz colisões.
- **Horário comercial dos EUA** (14:00–18:59 UTC): `:15` e `:45` são marcas de quarto de hora amplamente usadas por jobs cron de monitoramento e relatórios. Ficar a 3 minutos de distância (evitando [12,18] e [42,48]) reduz colisões.

**Ordem de aplicação**: `avoidHourBoundary` DEVE ser aplicado antes de `avoidPeakMinutes`.

**Escopo**: `avoidPeakMinutes` aplica-se apenas a padrões de dispersão direcionada. Padrões de dispersão de dia inteiro que usam o pool ponderado (Seção 6.3.1) já evitam janelas de pico por construção, uma vez que o pool não inclui horas de pico da UE (06–09) ou horas de pico dos EUA (14–18).

**Exemplo**:
```
FUZZY:DAILY_AROUND:14:00, fluxo de trabalho "my-scanner"
  Horário disperso bruto: 14:28
  Passo 1 (avoidHourBoundary): 28 → 28  (sem alteração; 28 ∈ [5,54])
  Passo 2 (avoidPeakMinutes):  28 → 34  (deslocado; hora ∈ [14,18], minuto 28 ∈ [27,33]
                                          — espere, hora=14, então a regra da UE não se aplica;
                                          regra :15 dos EUA: 28 ∉ [12,18]; regra :45: 28 ∉ [42,48])
  → sem deslocamento necessário; resultado: 14:28

FUZZY:DAILY_AROUND:15:00, fluxo de trabalho "my-monitor"
  Horário disperso bruto: 15:13
  Passo 1 (avoidHourBoundary): 13 → 13  (sem alteração)
  Passo 2 (avoidPeakMinutes):  13 → 19  (deslocado; hora ∈ [14,18], minuto 13 ∈ [12,18])
  → resultado: 15:19
```

### 6.5 Requisitos do Algoritmo

Uma implementação DEVE garantir:

1. A função de hash produz a mesma saída para a mesma entrada em todas as plataformas
2. Operações de módulo usam divisão inteira consistente
3. Quebra de dia usa regras de adição/subtração consistentes
4. Extração de minuto e hora usa divisão e operações de módulo consistentes
5. `avoidHourBoundary` é aplicado antes de `avoidPeakMinutes` para todos os padrões de dispersão direcionada
6. Padrões de dispersão de dia inteiro usam o pool ponderado de slot de tempo diário (Seção 6.3.1)

---

## 7. Geração de Expressão Cron

### 7.1 Placeholders Cron Difusos

Uma implementação DEVE gerar placeholders cron difusos que possam ser resolvidos posteriormente pelo algoritmo de dispersão. Placeholders DEVEM usar o formato:

```
FUZZY:<TIPO>[:<PARAMS>] <campos-cron>
```

Onde:
- `<TIPO>` identifica o tipo de agenda
- `<PARAMS>` fornece parâmetros opcionais (tempo, dia, faixa)
- `<campos-cron>` inclui campos cron restantes (tipicamente `* * *`)

### 7.2 Formatos de Placeholder

| Tipo de Agenda | Formato de Placeholder |
|---------------|-------------------|
| Diária | `FUZZY:DAILY * * *` |
| Diária em torno de | `FUZZY:DAILY_AROUND:HH:MM * * *` |
| Diária entre | `FUZZY:DAILY_BETWEEN:SH:SM:EH:EM * * *` |
| Horária | `FUZZY:HOURLY * * *` |
| Intervalo de hora | `FUZZY:HOURLY:N * * *` |
| Semanal | `FUZZY:WEEKLY * * *` |
| Semanal com dia | `FUZZY:WEEKLY:DOW * * DOW` |
| Dia semanal em torno de | `FUZZY:WEEKLY:DOW:AROUND:HH:MM * * DOW` |
| Dia semanal entre | `FUZZY:WEEKLY:DOW:BETWEEN:SH:SM:EH:EM * * DOW` |
| Bi-semanal | `FUZZY:BI-WEEKLY * * *` |
| Tri-semanal | `FUZZY:TRI-WEEKLY * * *` |

### 7.3 Resolução de Placeholder

Uma implementação DEVE fornecer um mecanismo para resolver placeholders difusos para expressões cron concretas usando o algoritmo de dispersão e o identificador do fluxo de trabalho.

O processo de resolução DEVE:

1. Detectar o formato do placeholder difuso
2. Extrair o tipo de agenda e parâmetros
3. Aplicar o algoritmo de dispersão apropriado
4. Gerar expressão cron de 5 campos válida
5. Validar a expressão cron resultante

### 7.4 Validação de Expressão Cron

Expressões cron geradas DEVEM estar em conformidade com a sintaxe cron do GitHub Actions:

- 5 campos: `minuto hora dia-do-mês mês dia-da-semana`
- Minutos: 0-59 ou `*` ou `*/N`
- Horas: 0-23 ou `*` ou `*/N`
- Dia-do-mês: 1-31 ou `*` ou `*/N`
- Mês: 1-12 ou `*` ou `*/N`
- Dia-da-semana: 0-6 (Domingo=0) ou `*`

---

## 8. Salvaguardas

As salvaguardas a seguir são normativas e aplicam-se a todas as implementações de dispersão.

**R-SAFE-001**: Implementações **MUST** aplicar janelas de dispersão finitas. Para agendas `around`, a janela de jitter efetiva **MUST NOT** exceder ±60 minutos a partir do horário de ancoragem solicitado. Para agendas `between`, o horário disperso **MUST** permanecer dentro do intervalo fechado declarado.

**R-SAFE-002**: Implementações **MUST** aplicar normalização de prevenção de colisão antes de retornar o valor final de minuto. No mínimo, a implementação **MUST** evitar hotspots de limite de hora e picos conhecidos de quarto de hora conforme definido pela Seção 6.4. Essa garantia é determinística para um dado identificador de fluxo de trabalho e expressão de agenda.

**R-SAFE-003**: Se o material de entrada de hash estiver vazio (por exemplo, identificador de fluxo de trabalho ausente), a implementação **MUST** falhar com um erro descritivo e **NÃO DEVE** recorrer à dispersão aleatória.

**R-SAFE-004**: Se a entrada de hash não única causar colisões repetidas em fluxos de trabalho, a implementação **MUST** preservar o comportamento determinístico e **SHOULD** emitir um aviso indicando qualidade de distribuição reduzida. Implementações **NÃO DEVEM** recorrer silenciosamente a fallbacks não determinísticos para ocultar colisões.

---

## 9. Tratamento de Erros

### 9.1 Erros de Sintaxe

Uma implementação DEVE rejeitar expressões inválidas com mensagens de erro claras:

#### 9.1.1 Tipo de Agenda Inválido

```
Erro: Tipo de agenda desconhecido 'monthly'
Tipos válidos: daily, weekly, hourly, bi-weekly, tri-weekly, every
```

#### 9.1.2 Formato de Tempo Inválido

```
Erro: Formato de tempo inválido '25:00' em 'daily around 25:00'
Tempo deve estar no formato 24 horas (HH:MM, 0-23 horas) ou formato 12 horas com am/pm
```

#### 9.1.3 Dia da Semana Inválido

```
Erro: Dia da semana desconhecido 'mondey' em 'weekly on mondey'
Dias da semana válidos: sunday, monday, tuesday, wednesday, thursday, friday, saturday
```

#### 9.1.4 Intervalo Inválido

```
Erro: Intervalo inválido '5' em 'every 5h'
Intervalos de hora válidos: 1h, 2h, 3h, 4h, 6h, 8h, 12h
```

### 9.2 Erros Semânticos

#### 9.2.1 Componentes Obrigatórios Ausentes

```
Erro: 'around' requer uma especificação de tempo
Exemplo: daily around 14:00
```

#### 9.2.2 Sintaxe não Suportada

```
Erro: sintaxe 'daily at <time>' não é suportada
Use 'daily around <time>' para agendamento difuso dentro da janela de ±1 hora
```

### 9.3 Mensagens de Aviso

Uma implementação SHOULD emitir avisos para padrões válidos, mas subótimos:

```
Aviso: Considere usar 'every 2h' em vez de intervalo fixo
Intervalos fixos criam picos de carga quando muitos fluxos de trabalho são executados simultaneamente
```

### 9.4 Recuperação de Erros

Uma implementação SHOULD NOT tentar corrigir erros de sintaxe automaticamente. Todos os erros DEVEM ser relatados ao usuário com orientação de correção acionável.

### 9.5 Requisitos de Conformidade de Caso Limite

As normas de caso limite a seguir são obrigatórias além de §§9.1–9.4:

1. **Semente de dispersão inválida**: Se a derivação da semente produzir um valor vazio, negativo ou não inteiro, a implementação **MUST** falhar na compilação com um erro descritivo e **MUST NOT** recorrer a uma semente aleatória ou padrão.
2. **Valores de tempo fora da faixa**: Entradas contendo valores de hora fora de `0..23` (24 horas), valores de minuto fora de `0..59` ou valores de 12 horas fora de `1..12` **MUST** ser rejeitadas com um erro que inclui o token ofensivo e a faixa válida.
3. **Entrada de gramática malformada**: Expressões que violam o ABNF em §3.1 (ex: `and` ausente em `between`, modificadores pendentes, tokens extras após uma produção válida) **MUST** falhar na análise e **NÃO DEVEM** ser corrigidas automaticamente.
4. **Estabilidade do código de erro**: Para a mesma classe de entrada malformada, implementações **DEVEM** retornar uma categoria de código de erro estável entre execuções para suportar testes de conformidade determinísticos.

---

## 10. Testes de Conformidade

### 10.1 Requisitos da Suíte de Testes

Uma implementação conforme DEVE passar em todos os testes de Nível 1. Implementações que reivindicam conformidade de Nível 2 ou 3 DEVEM passar em todos os testes de seu nível reivindicado e de todos os níveis inferiores.

### 10.2 Categorias de Teste

#### 10.2.1 Testes de Análise de Sintaxe (Nível 1)

- **T-SYNTAX-001**: Analisar `daily` para `FUZZY:DAILY * * *`
- **T-SYNTAX-002**: Analisar `weekly` para `FUZZY:WEEKLY * * *`
- **T-SYNTAX-003**: Analisar `weekly on monday` para `FUZZY:WEEKLY:1 * * 1`
- **T-SYNTAX-004**: Analisar todos os nomes de dias da semana corretamente
- **T-SYNTAX-005**: Rejeitar tipos de agenda inválidos
- **T-SYNTAX-006**: Rejeitar nomes de dias da semana inválidos
- **T-SYNTAX-007**: Analisar tokens sem distinção entre maiúsculas e minúsculas

#### 10.2.2 Testes de Formato de Tempo (Nível 2)

- **T-TIME-001**: Analisar formato 24 horas `14:00`
- **T-TIME-002**: Analisar formato 12 horas `3pm`
- **T-TIME-003**: Analisar formato 12 horas `11am`
- **T-TIME-004**: Analisar keyword `midnight` como 00:00
- **T-TIME-005**: Analisar keyword `noon` como 12:00
- **T-TIME-006**: Converter `12am` para 00:00 (meia-noite)
- **T-TIME-007**: Converter `12pm` para 12:00 (meio-dia)
- **T-TIME-008**: Rejeitar horas inválidas (>23 ou <0)
- **T-TIME-009**: Rejeitar minutos inválidos (>59 ou <0)
- **T-TIME-010**: Lidar com zeros à esquerda ausentes (ex: `9:30`)

#### 10.2.3 Testes de Restrição de Tempo (Nível 2)

- **T-CONSTRAINT-001**: Analisar `daily around 14:00`
- **T-CONSTRAINT-002**: Analisar `daily between 9:00 and 17:00`
- **T-CONSTRAINT-003**: Analisar `weekly on friday around 17:00`
- **T-CONSTRAINT-004**: Lidar com faixas que cruzam a meia-noite (`22:00 and 02:00`)
- **T-CONSTRAINT-005**: Rejeitar `around` sem especificação de tempo
- **T-CONSTRAINT-006**: Rejeitar `between` com apenas um horário
- **T-CONSTRAINT-007**: Rejeitar sintaxe `daily at <time>`

#### 10.2.4 Testes de Fuso Horário (Nível 3)

- **T-TZ-001**: Analisar offset `utc+9`
- **T-TZ-002**: Analisar offset `utc-5`
- **T-TZ-003**: Analisar formato de offset `utc+05:30`
- **T-TZ-004**: Converter `14:00 utc+9` para `05:00` UTC
- **T-TZ-005**: Converter `3pm utc-5` para `20:00` UTC
- **T-TZ-006**: Lidar com conversão UTC negativa (quebra para o dia anterior)
- **T-TZ-007**: Lidar com conversão UTC >24:00 (quebra para o dia seguinte)
- **T-TZ-008**: Rejeitar offsets inválidos (ex: `utc+25`)

#### 10.2.5 Testes de Horários e Intervalos (Nível 2/3)

- **T-HOURLY-001**: Analisar `hourly` para `FUZZY:HOURLY * * *`
- **T-HOURLY-002**: Analisar `every 2h` para `FUZZY:HOURLY:2 * * *`
- **T-HOURLY-003**: Analisar `every 6 hours` para `FUZZY:HOURLY:6 * * *`
- **T-INTERVAL-001**: Analisar `every 5 minutes` para `*/5 * * * *`
- **T-INTERVAL-002**: Analisar `every 2 days` para `0 0 */2 * *`
- **T-INTERVAL-003**: Rejeitar `every 3 minutes` (abaixo do mínimo de 5 minutos)
- **T-INTERVAL-004**: Analisar `bi-weekly` para `FUZZY:BI-WEEKLY * * *`
- **T-INTERVAL-005**: Analisar `tri-weekly` para `FUZZY:TRI-WEEKLY * * *`

#### 10.2.6 Testes de Algoritmo de Dispersão (Nível 1-3)

- **T-SCATTER-001**: Hash produz mesma saída para a mesma entrada
- **T-SCATTER-002**: Entradas diferentes produzem saídas diferentes
- **T-SCATTER-003**: Valor do hash está dentro da faixa de módulo (0 a modulo-1)
- **T-SCATTER-004**: Agenda diária seleciona horário do pool ponderado (apenas níveis BEST/GOOD/OK)
- **T-SCATTER-005**: Agenda `around` permanece dentro da janela de ±60 minutos
- **T-SCATTER-006**: Agenda `between` permanece dentro da faixa especificada
- **T-SCATTER-007**: Faixa que cruza meia-noite manipula a quebra de dia corretamente
- **T-SCATTER-008**: Agenda horária produz minuto em [5, 54]
- **T-SCATTER-009**: Agenda semanal seleciona dia válido 0-6
- **T-SCATTER-010**: Mesmo fluxo de trabalho obtém mesmo horário entre compilações
- **T-SCATTER-011**: Agenda diária cai na janela BEST (02–05), GOOD (10–12) ou OK (19–23)
- **T-SCATTER-012**: Valores de minuto em [5, 54] para todos os padrões (prevenção de limite de hora)
- **T-SCATTER-013**: Dispersão DAILY_AROUND caindo nas horas de pico da UE (06–09) evita minutos [27, 33]
- **T-SCATTER-014**: Dispersão DAILY_AROUND caindo no horário comercial dos EUA (14–18) evita minutos [12, 18] e [42, 48]
- **T-SCATTER-015**: Agenda semanal usa pool de tempo diário ponderado (janelas preferenciais)
- **T-SCATTER-016**: Agendas bi-semanal e tri-semanal usam pool de tempo diário ponderado

#### 10.2.7 Testes de Geração Cron (Nível 1-3)

- **T-CRON-001**: Cron gerado tem exatamente 5 campos
- **T-CRON-002**: Campo de minuto está na faixa 0-59
- **T-CRON-003**: Campo de hora está na faixa 0-23
- **T-CRON-004**: Campo de dia-da-semana está na faixa 0-6 ou `*`
- **T-CRON-005**: Mês e dia-do-mês são válidos
- **T-CRON-006**: Expressões de intervalo usam sintaxe `*/N` válida

### 10.3 Checklist de Conformidade

| Requisito | ID de Teste | Nível | Status |
|-------------|---------|-------|--------|
| Analisar diário básico | T-SYNTAX-001 | 1 | Requerido |
| Analisar semanal básico | T-SYNTAX-002 | 1 | Requerido |
| Analisar especificação de dia | T-SYNTAX-003 | 1 | Requerido |
| Analisar todos os nomes de dias da semana | T-SYNTAX-004 | 1 | Requerido |
| Rejeitar tipos inválidos | T-SYNTAX-005 | 1 | Requerido |
| Análise insensível a maiúsculas/minúsculas | T-SYNTAX-007 | 1 | Requerido |
| Analisar formato 24 horas | T-TIME-001 | 2 | Requerido |
| Analisar formato 12 horas | T-TIME-002, 003 | 2 | Requerido |
| Analisar keywords de tempo | T-TIME-004, 005 | 2 | Requerido |
| Lidar corretamente com 12am/12pm | T-TIME-006, 007 | 2 | Requerido |
| Validar faixas de tempo | T-TIME-008, 009 | 2 | Requerido |
| Analisar restrições around | T-CONSTRAINT-001 | 2 | Requerido |
| Analisar restrições between | T-CONSTRAINT-002 | 2 | Requerido |
| Lidar com cruzamento da meia-noite | T-CONSTRAINT-004 | 2 | Requerido |
| Analisar offsets UTC | T-TZ-001, 002, 003 | 3 | Requerido |
| Converter fusos horários corretamente | T-TZ-004, 005 | 3 | Requerido |
| Lidar com quebra de dia de fuso horário | T-TZ-006, 007 | 3 | Requerido |
| Analisar agendas horárias | T-HOURLY-001, 002, 003 | 2 | Requerido |
| Analisar agendas de intervalo | T-INTERVAL-001, 002 | 3 | Requerido |
| Determinismo de hash | T-SCATTER-001, 002 | 1 | Requerido |
| Distribuição de dispersão | T-SCATTER-004-009 | 1-3 | Requerido |
| Pool diário ponderado | T-SCATTER-011, 015, 016 | 1-3 | Requerido |
| Prevenção de pico (limite de hora) | T-SCATTER-012 | 1-3 | Requerido |
| Prevenção de pico (pico matinal da UE) | T-SCATTER-013 | 2-3 | Requerido |
| Prevenção de pico (horário comercial dos EUA) | T-SCATTER-014 | 2-3 | Requerido |
| Colunas de saída de console | T-CRON-001-006 | 1-3 | Requerido |

---

## Apêndices

### Apêndice A: Exemplos Completos

#### A.1 Exemplos de Agenda Diária

```yaml
# Diário básico (disperso ao longo do dia inteiro)
schedule: daily
# Fuzzy: FUZZY:DAILY * * *
# Pode gerar: 43 5 * * * (5:43 AM)

# Diário em torno de um horário específico
schedule: daily around 14:00
# Fuzzy: FUZZY:DAILY_AROUND:14:0 * * *
# Pode gerar: 13 14 * * * (2:13 PM, dentro da janela 1-3 PM)

# Diário durante o horário comercial
schedule: daily between 9:00 and 17:00
# Fuzzy: FUZZY:DAILY_BETWEEN:9:0:17:0 * * *
# Pode gerar: 37 12 * * * (12:37 PM, dentro das 9 AM-5 PM)

# Diário com conversão de fuso horário (JST para UTC)
schedule: daily around 14:00 utc+9
# Fuzzy: FUZZY:DAILY_AROUND:5:0 * * *
# Converte para 5:00 AM UTC, dispersa na janela 4-6 AM UTC
```

#### A.2 Exemplos de Agenda Semanal

```yaml
# Semanal básico (qualquer dia, qualquer horário)
schedule: weekly
# Fuzzy: FUZZY:WEEKLY * * *
# Pode gerar: 43 5 * * 1 (Segunda-feira 5:43 AM)

# Semanal em um dia específico
schedule: weekly on monday
# Fuzzy: FUZZY:WEEKLY:1 * * 1
# Pode gerar: 18 14 * * 1 (Segunda-feira 2:18 PM)

# Semanal com restrição de tempo
schedule: weekly on friday around 17:00
# Fuzzy: FUZZY:WEEKLY:5:AROUND:17:0 * * 5
# Pode gerar: 42 16 * * 5 (Sexta-feira 4:42 PM, dentro das 4-6 PM)
```

#### A.3 Exemplos de Intervalo e Horários

```yaml
# Cada hora com minuto disperso
schedule: hourly
# Fuzzy: FUZZY:HOURLY * * *
# Pode gerar: 43 * * * * (a cada hora no minuto 43)

# A cada 2 horas
schedule: every 2h
# Fuzzy: FUZZY:HOURLY:2 * * *
# Pode gerar: 53 */2 * * * (a cada 2 horas no minuto 53)

# A cada 5 minutos (fixo, não difuso)
schedule: every 5 minutes
# Gera: */5 * * * * (intervalo fixo)

# Bi-semanal
schedule: bi-weekly
# Fuzzy: FUZZY:BI-WEEKLY * * *
# Pode gerar: 43 5 */14 * * (a cada 14 dias às 5:43 AM)
```

#### A.4 Exemplos de Conversão de Fuso Horário

```yaml
# Horário comercial JST (UTC+9) para UTC
schedule: daily between 9am utc+9 and 5pm utc+9
# Converte para: daily between 0:00 and 8:00 (UTC)
# Fuzzy: FUZZY:DAILY_BETWEEN:0:0:8:0 * * *

# Reunião da tarde EST (UTC-5)
schedule: weekly on monday around 3pm utc-5
# Converte para: weekly on monday around 20:00 (UTC)
# Fuzzy: FUZZY:WEEKLY:1:AROUND:20:0 * * 1

# Standup matinal IST (UTC+5:30)
schedule: daily around 9:30am utc+05:30
# Converte para: daily around 4:00 (UTC)
# Fuzzy: FUZZY:DAILY_AROUND:4:0 * * *
```

### Apêndice B: Referência de Código de Erro

| Código de Erro | Descrição | Exemplo |
|------------|-------------|---------|
| ERR-SYNTAX-001 | Tipo de agenda desconhecido | `monthly` (não suportado) |
| ERR-SYNTAX-002 | Formato de tempo inválido | `25:00` (hora fora da faixa) |
| ERR-SYNTAX-003 | Dia da semana inválido | `mondey` (erro de digitação) |
| ERR-SYNTAX-004 | Componente obrigatório ausente | `daily around` (sem tempo) |
| ERR-SYNTAX-005 | Padrão de sintaxe não suportado | `daily at 14:00` (use `around`) |
| ERR-TIME-001 | Hora fora da faixa | `25` (>23) |
| ERR-TIME-002 | Minuto fora da faixa | `60` (>59) |
| ERR-TIME-003 | Formato 12 horas inválido | `13pm` (hora >12) |
| ERR-TZ-001 | Offset UTC inválido | `utc+25` (>14) |
| ERR-TZ-002 | Sintaxe de offset malformada | `utc9` (falta +/-) |
| ERR-INTERVAL-001 | Valor de intervalo inválido | `every 0h` (deve ser >0) |
| ERR-INTERVAL-002 | Intervalo não suportado | `every 5h` (não fator de 24) |

### Apêndice C: Considerações de Segurança

#### C.1 Resistência à Colisão de Hash

O hash FNV-1a de 32 bits fornece resistência à colisão adequada para fins de dispersão de fluxo de trabalho. O paradoxo do aniversário sugere aproximadamente 77.000 fluxos de trabalho necessários para uma probabilidade de colisão de 50%. Para organizações com menos fluxos de trabalho, colisões são improváveis.

Se ocorrer colisão (dois fluxos de trabalho recebem horários de execução idênticos), isso não cria uma vulnerabilidade de segurança, mas reduz a eficácia da distribuição de carga.

#### C.2 Previsibilidade

A natureza determinística do algoritmo de dispersão significa que os horários de execução são previsíveis dado o identificador do fluxo de trabalho. Isso é intencional para consistência, mas significa que:

- Atacantes não podem causar DOS disparando execução simultânea
- Horários de execução não podem ser usados como segredos
- Distribuição de carga é transparente e auditável

#### C.3 Manipulação de Fuso Horário

Implementações DEVEM manipular offsets de fuso horário com aritmética de números inteiros para evitar erros de arredondamento de ponto flutuante que poderiam causar horários de execução inconsistentes.

Implementações SHOULD validar que offsets UTC estão dentro de faixas razoáveis (UTC-12 a UTC+14) para evitar estouro nas computações de tempo.

#### C.4 Validação de Entrada

Implementações DEVEM validar todas as entradas do usuário antes de processar:

- Tipo de agenda DEVE ser do conjunto permitido
- Valores de tempo DEVEM estar dentro de faixas válidas
- Valores de intervalo DEVEM ser números inteiros positivos
- Todas as entradas de string DEVEM ser sanitizadas para evitar ataques de injeção

---

## 11. Notas de Sincronização

Esta seção mapeia a especificação de agenda difusa para arquivos de implementação.

| Área Normativa | Arquivo(s) de Implementação |
|---|---|
| Análise de agenda de frontmatter e manipulação de gramática | `pkg/parser/schedule_parser.go` |
| Dispersão difusa determinística e prevenção de minuto de pico | `pkg/parser/schedule_fuzzy_scatter.go` |
| Testes de conformidade de parser/dispersão | `pkg/parser/schedule_parser_test.go`, `pkg/parser/schedule_fuzzy_scatter_test.go` |
| Suporte a visualização de calendário/cron para ferramentas de compilação (ver §12) | `pkg/cli/compile_schedule_calendar.go` |

Após alterar a semântica de agenda difusa:
1. Atualize esta seção da especificação e quaisquer cláusulas normativas afetadas.
2. Atualize a implementação de parser/dispersão nos arquivos mapeados.
3. Execute novamente os testes de parser/dispersão para verificar se o comportamento permanece determinístico.

---

## 12. Esquema de Saída de Calendário

O calendário de agenda em tempo de compilação emitido por `pkg/cli/compile_schedule_calendar.go` documenta a densidade de disparo UTC agregada de fluxos de trabalho agendados. Uma implementação conforme DEVE tratar o calendário como um artefato de console legível por humanos em vez de um formato de arquivo legível por máquina.

| Elemento | Requisito |
|---|---|
| Stream de saída | DEVE ser gravado apenas em `stderr` e NÃO DEVE ser emitido no modo de saída JSON. |
| Condição de emissão | DEVE ser omitido quando não houver fluxos de trabalho agendados. |
| Linha de título | DEVE renderizar o cabeçalho `Schedule Heatmap (UTC)`. |
| Cabeçalho de hora | DEVE conter 24 labels de hora UTC de `00` a `23`, em ordem crescente. |
| Linhas de dia | DEVE renderizar exatamente sete linhas na ordem `Mon`, `Tue`, `Wed`, `Thu`, `Fri`, `Sat`, `Sun`. |
| Células | DEVE renderizar um glifo por slot de hora usando o mapeamento de intensidade da implementação (`·`, `░`, `▒`, `▓`, `█`). |
| Legenda | DEVE explicar os buckets de contagem de disparos para cada glifo após a grade. |
| Saída de arquivo | NÃO DEVE criar um arquivo separado; o calendário é apenas uma renderização inline em stderr. |

Implementações SHOULD preservar uma grade de largura fixa para que as células adjacentes permaneçam alinhadas visualmente em terminais de texto puro. Estilização ANSI PODE ser aplicada quando stderr é um terminal, mas o conteúdo de texto sem estilo DEVE preservar a mesma estrutura de linha/coluna.

### Versão 1.2.0 (Rascunho) — 12/05/2026

- **Alterado**: Dispersão diária, semanal, bi-semanal e tri-semanal agora compartilham o pool ponderado de 622 slots introduzido nas Seções 6.3.1 e 6.3.5–6.3.6.
- **Adicionado**: Regras de prevenção de minuto de pico na Seção 6.4 para direcionar agendas para longe dos minutos de hotspot `:00`, `:15`, `:30` e `:45` durante janelas de pico documentadas.
- **Adicionado**: Requisitos de esquema de saída de calendário (Seção 12) para o heatmap de tempo de compilação renderizado por `compile_schedule_calendar.go`.

---

## Referências

### Referências Normativas

- **[RFC 2119]** S. Bradner. "Key words for use in RFCs to Indicate Requirement Levels". RFC 2119, March 1997. [https://www.ietf.org/rfc/rfc2119.txt](https://www.ietf.org/rfc/rfc2119.txt)

- **[ABNF]** D. Crocker, P. Overell. "Augmented BNF for Syntax Specifications: ABNF". RFC 5234, January 2008. [https://tools.ietf.org/html/rfc5234](https://tools.ietf.org/html/rfc5234)

### Referências Informativas

- **[FNV]** G. Fowler, L. C. Noll, K.-P. Vo. "FNV Hash". [http://www.isthe.com/chongo/tech/comp/fnv/](http://www.isthe.com/chongo/tech/comp/fnv/)

- **[GitHub Actions Cron]** Documentação do GitHub. "Events that trigger workflows - schedule". [https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule)

- **[ISO 8601]** International Organization for Standardization. "Data elements and interchange formats – Information interchange – Representation of dates and times". ISO 8601:2004.

---

*Copyright © 2024 GitHub. Todos os direitos reservados.*
