---
title: Especificação do Comando Forecast
description: Especificação formal estilo W3C para o comando gh aw forecast — projeção de uso de tokens via Monte Carlo, análise de episódios, descoberta de fluxos de trabalho e formatos de saída para GitHub Agentic Workflows
sidebar:
  order: 1355
---

# Especificação do Comando Forecast

**Versão**: 0.1.0  
**Status**: Rascunho Experimental  
**Versão Mais Recente**: [forecast-specification](/gh-aw/reference/forecast-specification/)  
**Editor**: Equipe do GitHub Agentic Workflows

> ⚠️ **Experimental**: Esta especificação descreve uma funcionalidade que está em desenvolvimento ativo. A interface do comando, o esquema de saída e os parâmetros algorítmicos estão sujeitos a alterações sem aviso prévio. Não dependa desta interface em fluxos de trabalho de produção.

---

## Resumo

Esta especificação define o comando `gh aw forecast` para o projeto GitHub Agentic Workflows (gh-aw). O comando realiza amostragem histórica de execuções de fluxos de trabalho agentic concluídas e aplica um motor de simulação de Monte Carlo para projetar o consumo futuro de Effective Token (ET) em um horizonte de tempo configurável. A especificação abrange descoberta de fluxo de trabalho (modos local e remoto), amostragem de dados via API do GitHub Actions, o algoritmo de projeção de Monte Carlo Poisson–bootstrap, análise de nível de episódio e formatos de saída de tabela de console e JSON legível por máquina. Implementações em conformidade com esta especificação fornecem aos operadores previsões probabilísticas de consumo de token adequadas para planejamento de capacidade, estimativa de custos e governança de orçamento.

---

## Status deste Documento

Esta seção descreve o status deste documento no momento da publicação. Este é um **Rascunho Experimental** de especificação e pode ser atualizado, substituído ou tornado obsoleto por outros documentos a qualquer momento. A funcionalidade que descreve é experimental e ainda não está sujeita às garantias de estabilidade que se aplicam a outros comandos do gh-aw.

Este documento é regido pelo processo de especificações do projeto GitHub Agentic Workflows.

O feedback deve ser enviado como GitHub issues no repositório `github/gh-aw`.

---

## Índice

1. [Introdução](#1-introdução)
2. [Conformidade](#2-conformidade)
3. [Terminologia](#3-terminologia)
4. [Interface do Comando](#4-interface-do-comando)
5. [Descoberta de Fluxo de Trabalho](#5-descoberta-de-fluxo-de-trabalho)
6. [Amostragem de Dados](#6-amostragem-de-dados)
7. [Motor de Projeção de Monte Carlo](#7-motor-de-projeção-de-monte-carlo)
8. [Análise de Episódio](#8-análise-de-episódio)
9. [Formatos de Saída](#9-formatos-de-saída)
10. [Tratamento de Erros](#10-tratamento-de-erros)
11. [Requisitos de Implementação](#11-requisitos-de-implementação)
12. [Testes de Conformidade](#12-testes-de-conformidade)
13. [Notas de Sincronização](#13-notas-de-sincronização)
14. [Apêndices](#14-apêndices)
15. [Referências](#15-referências)
16. [Log de Alterações](#16-log-de-alterações)

---

## 1. Introdução

### 1.1 Objetivo

O comando `gh aw forecast` atende à necessidade operacional de prever gastos futuros com tokens de Large Language Model (LLM) para fluxos de trabalho agentic gerenciados pelo gh-aw. O consumo de token é um dos principais direcionadores de custo para sistemas agentic; a capacidade de projetar o uso futuro a partir de observações históricas permite:

- **Planejamento de Capacidade**: Antecipar a demanda por tokens antes que os limites de orçamento sejam atingidos.
- **Governança de Custos**: Fornecer intervalos de confiança P10/P50/P90 para planejamento financeiro.
- **Comparação de Fluxo de Trabalho**: Classificar fluxos de trabalho por custo projetado de token em um período de tempo compartilhado.
- **Avaliação de Experimentos**: Medir o impacto de variantes de experimentos A/B no consumo de tokens.

O comando combina bootstrapping empírico de observações históricas de tokens com um modelo de contagem de execuções distribuído por Poisson para produzir projeções estatisticamente sólidas sem exigir suposições de distribuição paramétrica sobre o uso de tokens.

### 1.2 Escopo

Esta especificação abrange:

- Interface de linha de comando: flags, argumentos posicionais e modos de invocação
- Descoberta de fluxo de trabalho em modos local (`.github/workflows/`) e remoto (`--repo`)
- Amostragem de execuções históricas e derivação de métricas por execução
- O algoritmo de simulação de Monte Carlo produzindo estimativas de percentil P10, P50, P90
- Agrupamento de episódios e computação de métricas em nível de episódio
- Formato de saída de tabela de console
- Esquema de saída JSON legível por máquina (`--json`)
- Condições de erro e comportamento de degradação suave

Esta especificação NÃO abrange:

- O algoritmo de computação de Effective Tokens (ET) (definido na [Especificação de Effective Tokens](/gh-aw/reference/effective-tokens-specification/))
- O esquema do artefato `aw_info.json`
- O esquema de frontmatter de experimento A/B (definido na [Especificação de Experimentos A/B](/gh-aw/practices/experiments-specification/))
- Faturamento, precificação ou modelagem financeira além de projeções de tokens
- Relatórios de consumo de token em tempo real ou streaming

### 1.3 Objetivos de Design

Uma implementação conforme do `gh aw forecast` DEVE ser projetada para:

- **Precisão Empírica**: Projeções derivadas de dados históricos observados em vez de distribuições assumidas.
- **Relatórios Probabilísticos**: Intervalos de incerteza P10/P50/P90 comunicados aos chamadores.
- **Degradação Suave**: Dados ausentes (sem execuções, sem artefatos, sem frontmatter) DEVEM produzir resultados parciais em vez de falhas.
- **Modos Duais**: Operação tanto em repositório local quanto remoto sem exigir um checkout.
- **Interoperabilidade**: Esquema de saída JSON estável o suficiente para consumo por máquina por ferramentas a jusante.

---

## 2. Conformidade

### 2.1 Classes de Conformidade

Uma **implementação de forecast conforme** é aquela que satisfaz todos os requisitos MUST, REQUIRED e SHALL nesta especificação.

Uma **implementação de forecast parcialmente conforme** é aquela que satisfaz todos os requisitos MUST nas Seções 4, 5, 6 e 7, mas PODE não ter suporte para funcionalidades opcionais, como análise de episódios (Seção 8), relatórios de variantes de experimento ou diagnósticos detalhados.

### 2.2 Notação de Requisitos

As palavras-chave "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY" e "OPTIONAL" neste documento devem ser interpretadas como descrito no [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

### 2.3 Níveis de Conformidade

Implementações DEVEM suportar:

- **Nível 1 (Requerido)**: Invocação de comando, descoberta de fluxo de trabalho, amostragem de dados históricos e projeção de Monte Carlo com saída de console.
- **Nível 2 (Padrão)**: Saída JSON (`--json`), análise de episódios, modo de repositório remoto (`--repo`) e relatórios de variante de experimento.
- **Nível 3 (Completo)**: Todas as funcionalidades opcionais, incluindo diagnósticos `--verbose`, relatórios de limite de simultaneidade e enriquecimento de metadados de frontmatter.

---

## 3. Terminologia

### 3.1 Effective Tokens (ET)

Uma unidade normalizada de consumo de token de LLM definida na [Especificação de Effective Tokens](/gh-aw/reference/effective-tokens-specification/). O ET contabiliza pesos de classe de token e multiplicadores de modelo para produzir um único escalar comparável entre invocações heterogêneas de LLM.

### 3.2 Workflow Run (Execução de Fluxo de Trabalho)

Uma única execução de um fluxo de trabalho do GitHub Actions. Uma execução tem um ID de execução numérico único, um tipo de evento, um status (`completed`, `in_progress`, `queued`), uma conclusão (`success`, `failure`, `cancelled` etc.) e um SHA de commit de cabeça (head commit).

### 3.3 Janela Histórica

O intervalo de tempo `[agora − dias, agora]` usado para limitar o conjunto de execuções concluídas elegíveis para amostragem. Controlado pela flag `--days`.

### 3.4 Amostra

O subconjunto de execuções de fluxo de trabalho concluídas dentro da janela histórica selecionado para derivação de métricas. O tamanho máximo da amostra por fluxo de trabalho é controlado pela flag `--sample`.

### 3.5 Tentativa de Monte Carlo (Trial)

Uma única simulação independente que extrai valores estocásticos para contagem de execuções, uso de token por execução e sucesso por execução, combinando-os para produzir um total projetado de Effective Token para o período de projeção.

### 3.6 Período de Projeção

O intervalo de tempo futuro para o qual o consumo de token é projetado. Controlado pela flag `--period`; ou uma semana calendário (`week`) ou um mês calendário (`month`).

### 3.7 Execuções Observadas Por Período

A taxa de execuções de fluxo de trabalho observadas na janela histórica, extrapolada para o comprimento do período de projeção:

```
observed_runs_per_period = (sampled_run_count / history_days) × period_days
```

Onde `period_days` é 7 para `week` e 30 para `month`.

### 3.8 Episódio

Um agrupamento lógico de uma ou mais execuções de fluxo de trabalho que coletivamente representam uma única tentativa de tarefa. Episódios são identificados agrupando execuções que compartilham o mesmo `headSha` e `headBranch`, ou por vinculação `workflow_dispatch`/`workflow_call` onde disponível.

### 3.9 Rendimento (Yield)

A taxa de throughput efetiva: o número esperado de execuções bem-sucedidas por período de projeção, computado como o produto da frequência de execução observada e a taxa de sucesso histórica:

```
yield = observed_runs_per_period × success_rate
```

Onde `success_rate = successful_run_count / total_sampled_run_count`.

### 3.10 Reamostragem Bootstrap

Uma técnica de reamostragem empírica onde observações individuais são extraídas com reposição da amostra observada. Usada na Seção 7 para modelar o uso de token por execução sem suposições de distribuição paramétrica.

### 3.11 Arquivo de Bloqueio (Lock File)

Um arquivo `.lock.yml` localizado em `.github/workflows/` que declara um fluxo de trabalho agentic compilado e seus metadados associados. Arquivos de bloqueio são a fonte autoritativa de identificadores de fluxo de trabalho no modo local.

---

## 4. Interface do Comando

### 4.1 Sinopse

```
gh aw forecast [workflow_id...] [flags]
```

### 4.2 Argumentos Posicionais

| Argumento | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `workflow_id` | string (repetível) | Não | Zero ou mais identificadores de fluxo de trabalho para prever. Se omitido, todos os fluxos de trabalho agentic descobertos são previstos. |

Identificadores de fluxo de trabalho DEVEM ser correspondidos sem distinção entre maiúsculas e minúsculas contra:
1. O nome de exibição do fluxo de trabalho
2. O nome base do caminho do arquivo do fluxo de trabalho (sem extensão)

Se um `workflow_id` fornecido não corresponder a nenhum fluxo de trabalho descoberto, a implementação DEVE emitir uma mensagem de erro identificando o identificador não correspondente e DEVE sair com um status diferente de zero.

### 4.3 Flags

| Flag | Tipo | Padrão | Descrição |
|---|---|---|---|
| `--days` | int | `30` | Comprimento da janela de amostragem histórica em dias. Valores permitidos: `7`, `30`. |
| `--period` | string | `"month"` | Comprimento do período de projeção. Valores permitidos: `"week"`, `"month"`. |
| `--sample` | int | `100` | Número máximo de execuções concluídas para amostrar por fluxo de trabalho. MUST ser ≥ 1. |
| `--max-age` | int | `90` | Idade máxima em dias para execuções históricas elegíveis para amostragem. Implementações SHOULD descartar execuções mais antigas que este limite, a menos que o chamador as substitua. MUST ser ≥ 1. |
| `--repo` | string | (nenhum) | Destina um repositório diferente do diretório de trabalho atual, no formato `owner/repo`. Habilita o modo remoto. |
| `--json` | bool | `false` | Emite saída JSON legível por máquina em vez de tabelas de console. |
| `--verbose` | bool | `false` | Emite saída de diagnóstico detalhada para stderr durante o processamento. |

### 4.4 Validação de Flags

Implementações DEVEM validar todos os valores de flag antes de iniciar quaisquer chamadas de API ou operações de sistema de arquivos:

- **R-CLI-001**: Se `--days` não for um dos `{7, 30}`, a implementação DEVE sair com um status diferente de zero e uma mensagem de erro especificando os valores permitidos.
- **R-CLI-002**: Se `--period` não for um dos `{"week", "month"}`, a implementação DEVE sair com um status diferente de zero e uma mensagem de erro especificando os valores permitidos.
- **R-CLI-003**: Se `--sample` for menor que 1, a implementação DEVE sair com um status diferente de zero.
- **R-CLI-004**: Se `--repo` for fornecido, ele DEVE corresponder ao padrão `owner/repo` (dois componentes não vazios separados por `/`). Um formato inválido DEVE produzir uma saída diferente de zero com um erro descritivo.
- **R-CLI-005**: Se `--max-age` for fornecido e for menor que 1, a implementação DEVE sair com um status diferente de zero e um erro descritivo.

### 4.5 Códigos de Saída

| Código | Significado |
|---|---|
| `0` | Previsão concluída com sucesso. |
| `1` | Erro de uso (flags inválidas, IDs de fluxo de trabalho sem correspondência). |
| `2` | Falha na autenticação da API do GitHub. |
| `3` | Nenhum fluxo de trabalho descoberto. |

### 4.6 Exemplos de Invocação

```sh
# Prever todos os fluxos de trabalho agentic no repositório atual para o próximo mês
gh aw forecast

# Prever dois fluxos de trabalho específicos e comparar
gh aw forecast ci-doctor daily-planner

# Usar uma janela de 7 dias e projetar para a próxima semana
gh aw forecast --period week --days 7

# Emitir JSON legível por máquina
gh aw forecast --json

# Prever fluxos de trabalho em um repositório remoto
gh aw forecast --repo owner/repo

# Prever um fluxo de trabalho específico em um repositório remoto
gh aw forecast --repo owner/repo ci-doctor

# Ignorar execuções históricas com mais de 90 dias (padrão)
gh aw forecast --max-age 90
```

---

## 5. Descoberta de Fluxo de Trabalho

### 5.1 Modos

O comando forecast opera em um dos dois modos de descoberta, determinados pela presença da flag `--repo`:

- **Modo Local**: `--repo` está ausente; fluxos de trabalho são descobertos a partir do diretório `.github/workflows/` do repositório atual.
- **Modo Remoto**: `--repo` está presente; fluxos de trabalho são descobertos via API do GitHub Actions.

### 5.2 Descoberta em Modo Local

No modo local, a implementação DEVE:

1. **R-DISC-001**: Enumerar todos os arquivos correspondentes a `*.lock.yml` dentro de `.github/workflows/` do repositório de trabalho atual.
2. **R-DISC-002**: Analisar cada arquivo de bloqueio para extrair o identificador do fluxo de trabalho e o nome de exibição.
3. **R-DISC-003**: Se o diretório `.github/workflows/` não existir ou não contiver arquivos de bloqueio, a implementação DEVE emitir uma mensagem informativa e sair com o código `3`.

A implementação PODE adicionalmente ler metadados de frontmatter dos arquivos de origem do fluxo de trabalho correspondentes para enriquecer registros por fluxo de trabalho com:

- Tipos de trigger ativos (`active_triggers`)
- Configuração de simultaneidade (`concurrency_limit`)
- Declarações de variante de experimento A/B (`experiment_variants`)

O enriquecimento de frontmatter é OPCIONAL; a ausência de um arquivo de origem correspondente NÃO DEVE impedir a descoberta ou projeção do fluxo de trabalho.

### 5.3 Descoberta em Modo Remoto

No modo remoto (quando `--repo owner/repo` é especificado), a implementação DEVE:

1. **R-DISC-010**: Chamar a API do GitHub Actions (`GET /repos/{owner}/{repo}/actions/workflows`) para enumerar fluxos de trabalho no repositório de destino. Se a descoberta de fluxo de trabalho atingir um limite de taxa primário ou secundário da API do GitHub, a implementação SHOULD recuar (back off) e tentar novamente antes de falhar.
2. **R-DISC-011**: Filtrar os fluxos de trabalho retornados para aqueles identificados como agentic (ex: inspecionando convenções de caminho de arquivo, labels ou outras heurísticas definidas pela implementação).
3. **R-DISC-012**: Corresponder quaisquer argumentos posicionais `workflow_id` fornecidos pelo chamador contra nomes de exibição de fluxo de trabalho e nomes base de caminho de arquivo usando comparação de strings sem distinção entre maiúsculas e minúsculas.
4. **R-DISC-013**: Se ocorrer esgotamento do limite de taxa após pelo menos um identificador de fluxo de trabalho fornecido pelo chamador ainda poder ser tentado, a implementação DEVE continuar com esse subconjunto como um conjunto de resultados parcial e DEVE emitir um aviso identificando o modo de descoberta degradado.

No modo remoto, metadados de frontmatter (triggers, simultaneidade, variantes de experimento) estão INDISPONÍVEIS porque os arquivos de origem do fluxo de trabalho não são acessíveis. A implementação DEVE degradar graciosamente: campos que dependem de frontmatter DEVEM ser omitidos da saída ou relatados como seus valores zero/vazios em vez de causar um erro.

### 5.4 Correspondência de ID de Fluxo de Trabalho

A correspondência de ID de fluxo de trabalho DEVE não distinguir entre maiúsculas e minúsculas. Um identificador fornecido pelo chamador corresponde a um fluxo de trabalho descoberto se, e somente se, for igual (ignorando maiúsculas/minúsculas) a:

- O nome de exibição do fluxo de trabalho, OU
- O nome base do caminho do arquivo do fluxo de trabalho (sem extensão de arquivo)

A correspondência DEVE ser realizada após a descoberta ser concluída; correspondências de prefixo parcial NÃO SÃO suficientes para conformidade.

---

## 6. Amostragem de Dados

### 6.1 Procedimento de Amostragem

Para cada fluxo de trabalho descoberto (ou cada fluxo de trabalho no conjunto filtrado), a implementação DEVE realizar o seguinte procedimento de amostragem:

1. **R-SAMP-001**: Consultar execuções de fluxo de trabalho concluídas dentro da janela histórica usando o equivalente a `gh run list --workflow <id> --status completed --limit <sample> --created >=<cutoff>`.
2. **R-SAMP-002**: Limitar o conjunto de execuções retornadas a no máximo `--sample` execuções.
3. **R-SAMP-003**: Implementações SHOULD descartar execuções históricas com mais de 90 dias por padrão, mesmo quando uma janela de amostragem mais ampla for solicitada, e SHOULD expor esse limite por meio de uma flag `--max-age` para que os operadores possam optar por amostras mais antigas quando necessário.
4. **R-SAMP-004**: Para cada execução na amostra, derivar as métricas por execução definidas na Seção 6.2.
5. **R-SAMP-005**: Registrar a contagem de execuções com uma conclusão bem-sucedida separadamente da contagem total amostrada.

Se a janela histórica render zero execuções concluídas para um fluxo de trabalho, a implementação DEVE:

- **R-SAMP-006**: Retornar `nil` (ou um resultado vazio sentinela) para a projeção de Monte Carlo desse fluxo de trabalho.
- **R-SAMP-007**: Incluir o fluxo de trabalho na saída com `sampled_runs: 0` e todos os campos de projeção definidos como zero.
- **R-SAMP-008**: SHOULD emitir um aviso indicando que nenhum dado histórico está disponível para o fluxo de trabalho.

### 6.2 Derivação de Métricas por Execução

Para cada execução amostrada, a implementação DEVE derivar:

| Métrica | Fonte | Descrição |
|---|---|---|
| `effective_tokens` | artefato `aw_info.json` | ET total para esta execução conforme definido na Especificação de Effective Tokens. |
| `duration_seconds` | Timestamps de início/fim da execução | Duração em tempo real (wall-clock) da execução em segundos. |
| `success` | Campo de conclusão da execução | `true` se a conclusão for `"success"`, `false` caso contrário. |

#### 6.2.1 Recuperação de Effective Tokens

Contagens de effective tokens são obtidas de resumos de execução armazenados em cache localmente quando disponíveis. O comando `gh aw logs` armazena um arquivo `run_summary.json` para cada execução processada em `{output_dir}/run-{run_id}/`. Durante a previsão, a implementação:

- **R-SAMP-010**: DEVE tentar carregar o `run_summary.json` armazenado em cache para cada execução amostrada usando o diretório de saída de logs padrão (`.github/aw/logs`).
- **R-SAMP-011**: DEVE extrair o campo `TotalEffectiveTokens` do resumo `TokenUsage` armazenado em cache quando presente.
- **R-SAMP-012**: Se nenhum resumo em cache existir ou o campo ET for zero, a contribuição ET da execução DEVE ser tratada como zero e a execução DEVE ainda ser contada em `sampled_runs`. A implementação SHOULD registrar um aviso de nível de depuração (debug).

Esta abordagem leve evita o download repetido de artefatos, fornecendo observações de ET precisas para execuções que já foram processadas localmente por `gh aw logs`.

#### 6.2.2 Derivação de Duração

A duração DEVE ser computada como:

```
duration_seconds = run.updated_at − run.started_at
```

Ambos os timestamps DEVEM ser provenientes do objeto de execução da API do GitHub Actions. Se qualquer um dos timestamps for zero ou indisponível, a contribuição de duração da execução SHOULD ser tratada como zero.

### 6.3 Computação da Taxa Observada

Após a amostragem, a implementação DEVE computar:

```
observed_runs_per_period = (sampled_run_count / history_days) × period_days
```

Onde:
- `history_days` é o valor de `--days`
- `period_days` é `7` para `"week"` e `30` para `"month"`

---

## 7. Motor de Projeção de Monte Carlo

### 7.1 Visão Geral

O motor de Monte Carlo executa **10.000 tentativas de simulação independentes** por fluxo de trabalho para produzir uma distribuição de probabilidade sobre o consumo projetado de Effective Token no próximo período de projeção. O motor modela três fontes independentes de incerteza por tentativa.

Implementações DEVEM usar exatamente 10.000 tentativas. A contagem de tentativas é um requisito normativo para garantir a consistência das estimativas P10/P50/P90 entre implementações.

### 7.2 Fontes de Incerteza

Cada tentativa extrai de forma independente de três componentes estocásticos:

#### 7.2.1 Contagem de Execuções (Modelo Poisson)

O número de execuções no período de projeção é modelado como uma variável aleatória de Poisson com parâmetro de taxa:

```
λ = observed_runs_per_period
```

A implementação DEVE usar:

- **Algoritmo exato de Knuth** quando `λ ≤ 15`:

  ```
  L ← e^(−λ)
  k ← 0; p ← 1
  repeat:
    k ← k + 1
    p ← p × Uniform(0, 1)
  until p ≤ L
  return k − 1
  ```

- **Aproximação Normal** quando `λ > 15`:

  ```
  k ← round(Normal(μ=λ, σ=sqrt(λ)))
  k ← max(0, k)
  return k
  ```

- **R-MC-001**: Para `λ = 0`, a implementação DEVE retornar um total de token projetado de 0 para aquela tentativa sem invocar nenhum dos algoritmos.
- **R-FC-060**: Implementações DEVEM usar `λ = 15` como o limite de crossover: algoritmo exato de Knuth para `λ ≤ 15` e aproximação Normal apenas para `λ > 15`. Implementações NÃO DEVEM aumentar esse limite acima de 15 sem uma revisão da especificação, porque o erro documentado e as suposições de comparabilidade são calibrados para esse crossover.

#### 7.2.2 Uso de Token por Execução (Reamostragem Bootstrap)

O uso de token por execução é modelado empiricamente usando reamostragem bootstrap:

- **R-MC-010**: Para cada execução em uma tentativa, a implementação DEVE extrair uma observação uniformemente ao acaso **com reposição** do conjunto de observações históricas de ET na amostra.
- **R-MC-011**: Se a amostra contiver zero observações de ET (todas as execuções tiveram artefatos ausentes), a extração de token por execução DEVE retornar 0.

Essa abordagem não paramétrica preserva a distribuição empírica do uso de token, incluindo distribuições multimodais e caudas pesadas, sem impor uma forma paramétrica.

#### 7.2.3 Sucesso por Execução (Modelo Bernoulli)

Se uma dada execução na tentativa é bem-sucedida, é modelado como uma extração Bernoulli:

```
P(sucesso) = taxa_de_sucesso = contagem_de_execuções_bem_sucedidas / contagem_total_de_execuções_amostradas
```

- **R-MC-020**: Cada execução em uma tentativa DEVE extrair independentemente de `Bernoulli(taxa_de_sucesso)`.
- **R-MC-021**: Apenas execuções bem-sucedidas contribuem com sua extração de token para o total projetado da tentativa. Execuções com falha contribuem com zero tokens para a projeção.
- **R-MC-022**: Se `contagem_total_de_execuções_amostradas = 0`, `taxa_de_sucesso` DEVE ser tratada como 0. A implementação DEVE retornar uma projeção zero para todas as tentativas.

### 7.3 Agregação de Tentativa

Para uma dada tentativa com `k` execuções extraídas:

```
trial_tokens = Σ_{i=1}^{k} (sucesso_i × extração_de_token_i)
```

Onde:
- `sucesso_i` é `1` se a extração Bernoulli para a execução `i` for bem-sucedida, `0` caso contrário
- `extração_de_token_i` é a observação de ET bootstrapped para a execução `i`

### 7.4 Estatísticas de Saída

Após completar todas as 10.000 tentativas, a implementação DEVE computar e relatar:

| Estatística | Definição |
|---|---|
| `mean_projected_effective_tokens` | Média aritmética de todos os totais de tentativa |
| `std_dev_effective_tokens` | Desvio padrão populacional ou amostral de todos os totais de tentativa |
| `p10_projected_effective_tokens` | 10º percentil de todos os totais de tentativa (limite inferior do IC de 80%) |
| `p50_projected_effective_tokens` | 50º percentil de todos os totais de tentativa (projeção mediana) |
| `p90_projected_effective_tokens` | 90º percentil de todos os totais de tentativa (limite superior do IC de 80%) |

A computação de percentil DEVE usar o método de posto mais próximo (nearest-rank) ou um método equivalente que produza resultados consistentes com um array ordenado de 10.000 elementos.

O campo de nível superior `projected_effective_tokens` DEVE ser igual a `p50_projected_effective_tokens`.

### 7.5 Condição de Projeção Nil

Se nenhuma execução histórica estiver disponível para um fluxo de trabalho, a implementação DEVE retornar uma projeção nil (vazia/zero) para esse fluxo de trabalho. Projeções nil DEVEM ser representadas na saída JSON como valores zero para todos os campos numéricos de Monte Carlo. A implementação NÃO DEVE executar tentativas quando a amostra estiver vazia.

---

## 8. Análise de Episódio

### 8.1 Objetivo

Um **episódio** é um agrupamento lógico de uma ou mais execuções de fluxo de trabalho que coletivamente representam uma única tentativa de tarefa. A análise de episódio computa métricas por episódio para revelar quantas execuções, em média, são necessárias para concluir uma tarefa com sucesso.

### 8.2 Construção de Episódio

A implementação DEVE agrupar execuções amostradas em episódios usando o motor `buildEpisodeData` e `classifyEpisode`:

- **R-EP-001**: Execuções que compartilham o mesmo `headSha` e `headBranch` DEVEM ser agrupadas no mesmo episódio.
- **R-EP-002**: Execuções vinculadas por relacionamentos `workflow_dispatch` ou `workflow_call` (reconstruídas a partir de resumos de execução em cache) SHOULD ser mescladas no episódio da execução de disparo (triggering).

#### 8.2.1 Limitações no Contexto de Previsão

Durante a previsão, dados de artefato completos podem não estar disponíveis para todas as execuções amostradas. Quando dados de resumo em cache estiverem indisponíveis:

- **R-EP-010**: A vinculação `workflow_dispatch`/`workflow_call` DEVE ser omitida da construção do episódio.
- **R-EP-011**: A contagem resultante `sampled_episodes` DEVE ser tratada como uma **estimativa de limite inferior**. Implementações DEVEM comunicar essa limitação na saída (ex: por meio de uma nota na saída do console ou um campo booleano `episode_count_is_lower_bound` no JSON).

Para fluxos de trabalho orquestradores que recebem principalmente gatilhos `workflow_call`, a subestimação da contagem de episódios pode ser significativa. Implementações SHOULD emitir um aviso quando o tipo de gatilho dominante for `workflow_call` ou `workflow_dispatch`.

### 8.3 Métricas de Episódio

Para cada fluxo de trabalho, a implementação DEVE computar:

| Métrica | Definição |
|---|---|
| `sampled_episodes` | Contagem de episódios distintos identificados na amostra |
| `runs_per_episode` | `sampled_run_count / sampled_episodes` |
| `avg_effective_tokens_per_episode` | ET média somada em todas as execuções dentro de cada episódio |
| `observed_episodes_per_period` | `(sampled_episodes / history_days) × period_days` |

### 8.4 Exibição de Tabela de Episódio

A implementação DEVE exibir a tabela de análise de episódio na saída do console quando qualquer fluxo de trabalho no conjunto de resultados tiver `runs_per_episode > 1.0`. A tabela SHOULD ser omitida quando todos os fluxos de trabalho tiverem `runs_per_episode = 1.0` (uma execução por episódio é a linha de base e não adiciona informações adicionais).

---

## 9. Formatos de Saída

### 9.1 Saída de Tabela de Console

Quando `--json` não for especificado, a implementação DEVE renderizar uma tabela de console formatada para stderr com as seguintes colunas:

| Coluna | Descrição |
|---|---|
| `Workflow` | Nome de exibição ou identificador do fluxo de trabalho |
| `Sampled Runs` | Contagem de execuções concluídas incluídas na amostra |
| `Success Rate` | Fração de execuções amostradas concluídas com `success`, formatada como porcentagem; `N/A` quando nenhuma execução foi amostrada |
| `Yield/Period` | Taxa de throughput efetiva (`success_rate × observed_runs_per_period`) formatada com uma casa decimal |
| `Avg ET` | `avg_effective_tokens` formatado como abreviações K/M (ex: `12.5K`, `1.20M`); `-` quando zero |
| `Proj. ET (P50)` | Projeção de tokens efetivos mediana de Monte Carlo (P50), formatada como abreviações K/M |
| `80% CI (P10–P90)` | Intervalo de confiança `p10–p90`, ambos formatados como abreviações K/M |
| `Triggers` | Lista separada por vírgula de nomes de eventos de gatilho ativos do frontmatter (até 3, o restante mostrado como `+N`) |

#### 9.1.1 Requisitos de Formatação de Tabela

- **R-OUT-001**: Larguras de coluna DEVEM ser ajustadas automaticamente ao valor mais largo em cada coluna.
- **R-OUT-002**: Valores de ET DEVEM ser formatados como abreviações K/M (ex: `12.5K`, `1.20M`); valores inteiros brutos de zero DEVEM ser renderizados como `-`.
- **R-OUT-003**: Linhas DEVEM ser ordenadas por tokens efetivos projetados (P50) de Monte Carlo em ordem decrescente; quando dados de Monte Carlo não estiverem disponíveis, ordenar por `projected_effective_tokens`.
- **R-OUT-004**: Um fluxo de trabalho com zero execuções amostradas DEVE aparecer na tabela com `-` nas colunas de projeção e `N/A` nas colunas de taxa.
- **R-OUT-005**: Quando a análise de episódio for aplicável (Seção 8.4), uma segunda tabela com métricas de episódio DEVE ser impressa abaixo da tabela principal, separada por uma linha em branco.

### 9.2 Esquema de Saída JSON

Quando `--json` é especificado, a implementação DEVE emitir um único objeto JSON para stdout em conformidade com o esquema a seguir. Nenhum conteúdo adicional (banners, indicadores de progresso ou saída de tabela) DEVE ser emitido para stdout. Mensagens de diagnóstico PODEM ser emitidas para stderr.

#### 9.2.1 Objeto Raiz

```json
{
  "period": "<string>",
  "as_of": "<timestamp RFC 3339>",
  "workflows": [ <WorkflowForecast>, ... ]
}
```

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `period` | string | MUST | Período de projeção: `"week"` ou `"month"`. |
| `as_of` | string | MUST | Timestamp UTC RFC 3339 no qual a previsão foi computada. |
| `workflows` | array | MUST | Array ordenado de objetos de previsão por fluxo de trabalho. DEVE ser ordenado por `projected_effective_tokens` (P50) de forma decrescente. |

#### 9.2.2 Objeto WorkflowForecast

```json
{
  "workflow_id": "<string>",
  "period": "<string>",
  "sampled_runs": <integer>,
  "history_days": <integer>,
  "observed_runs_per_period": <number>,
  "success_rate": <number>,
  "yield": <number>,
  "avg_effective_tokens": <number>,
  "avg_duration_seconds": <number>,
  "projected_effective_tokens": <number>,
  "active_triggers": [ "<string>", ... ],
  "concurrency_limit": <integer>,
  "monte_carlo": { <MonteCarlo> },
  "episode_analysis": { <EpisodeAnalysis> },
  "experiment_variants": [ <ExperimentVariant>, ... ]
}
```

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `workflow_id` | string | MUST | Identificador do fluxo de trabalho conforme usado na descoberta. |
| `period` | string | MUST | Espelha o campo raiz `period`. |
| `sampled_runs` | integer | MUST | Número de execuções incluídas na amostra. |
| `history_days` | integer | MUST | Valor de `--days` usado para esta previsão. |
| `observed_runs_per_period` | number | MUST | Taxa de execução extrapolada para o período de projeção. |
| `success_rate` | number | MUST | Fração de execuções amostradas concluídas com sucesso, em `[0.0, 1.0]`. |
| `yield` | number | MUST | Taxa de throughput efetiva: `success_rate × observed_runs_per_period`. |
| `avg_effective_tokens` | number | MUST | ET média por execução amostrada. `0` quando nenhum dado de ET está disponível. |
| `avg_duration_seconds` | number | MUST | Duração média em tempo real por execução amostrada em segundos. |
| `projected_effective_tokens` | number | MUST | Projeção P50 de Monte Carlo. Igual a `monte_carlo.p50_projected_effective_tokens`. |
| `active_triggers` | array de strings | SHOULD | Tipos de eventos de trigger do frontmatter. Array vazio quando o frontmatter está indisponível. |
| `concurrency_limit` | integer | SHOULD | Limite de grupo de simultaneidade do frontmatter. `0` indica ilimitado ou indisponível. |
| `monte_carlo` | objeto | MUST | Resultados da simulação de Monte Carlo. Veja Seção 9.2.3. |
| `episode_analysis` | objeto | SHOULD | Resultados da análise de episódio. Veja Seção 9.2.4. |
| `experiment_variants` | array | MAY | Detalhamento de variante de experimento A/B. Veja Seção 9.2.5. Array vazio quando o frontmatter está indisponível ou nenhum experimento está configurado. |

#### 9.2.3 Objeto MonteCarlo

```json
{
  "iterations": 10000,
  "mean_projected_effective_tokens": <number>,
  "std_dev_effective_tokens": <number>,
  "p10_projected_effective_tokens": <number>,
  "p50_projected_effective_tokens": <number>,
  "p90_projected_effective_tokens": <number>
}
```

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `iterations` | integer | MUST | Sempre `10000`. |
| `mean_projected_effective_tokens` | number | MUST | Média aritmética dos totais de tentativa. |
| `std_dev_effective_tokens` | number | MUST | Desvio padrão dos totais de tentativa. |
| `p10_projected_effective_tokens` | number | MUST | 10º percentil dos totais de tentativa. |
| `p50_projected_effective_tokens` | number | MUST | 50º percentil (mediana) dos totais de tentativa. |
| `p90_projected_effective_tokens` | number | MUST | 90º percentil dos totais de tentativa. |

Quando `sampled_runs = 0`, todos os campos numéricos neste objeto DEVEM ser `0` e `iterations` DEVE ser `0`.

#### 9.2.4 Objeto EpisodeAnalysis

```json
{
  "sampled_episodes": <integer>,
  "runs_per_episode": <number>,
  "avg_effective_tokens_per_episode": <number>,
  "observed_episodes_per_period": <number>
}
```

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `sampled_episodes` | integer | MUST | Contagem de episódios distintos. Estimativa de limite inferior quando a vinculação de artefato está indisponível. |
| `runs_per_episode` | number | MUST | Média de execuções por episódio. |
| `avg_effective_tokens_per_episode` | number | MUST | ET média por episódio. |
| `observed_episodes_per_period` | number | MUST | Taxa de episódios extrapolada para o período de projeção. |

#### 9.2.5 Objeto ExperimentVariant

```json
{
  "experiment_name": "<string>",
  "variant": "<string>",
  "run_count": <integer>,
  "fraction": <number>
}
```

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `experiment_name` | string | MUST | Nome do experimento A/B do frontmatter. |
| `variant` | string | MUST | Identificador da variante (ex: `"control"`, `"treatment"`). |
| `run_count` | integer | MUST | Número de execuções amostradas atribuídas a esta variante. |
| `fraction` | number | MUST | `run_count / sampled_runs` para este fluxo de trabalho; fração em `[0.0, 1.0]`. |

---

## 10. Tratamento de Erros

### 10.1 Erros de Autenticação

Se a API do GitHub retornar um erro de autenticação (HTTP 401 ou 403):

- **R-ERR-001**: A implementação DEVE emitir uma mensagem de erro descritiva para stderr indicando a falha de autenticação e orientação sobre como autenticar novamente com `gh auth login`.
- **R-ERR-002**: A implementação DEVE sair com código `2`.

### 10.2 Limites de Taxa da API (Rate Limiting)

Se a API do GitHub retornar uma resposta de limite de taxa (HTTP 429 ou um cabeçalho `X-RateLimit-Remaining: 0`):

- **R-ERR-010**: A implementação SHOULD tentar novamente a solicitação após o período indicado pelo cabeçalho `X-RateLimit-Reset`.
- **R-ERR-011**: A implementação DEVE emitir um aviso para stderr ao entrar em um estado de espera de limite de taxa.
- **R-ERR-012**: Se a tentativa não for viável, a implementação DEVE sair com um status diferente de zero e uma mensagem indicando a condição de limite de taxa.

### 10.3 Falhas Parciais

Quando um ou mais fluxos de trabalho no conjunto de descoberta encontrarem erros individuais (ex: falha no download de artefato, timeout da API para um fluxo de trabalho específico):

- **R-ERR-020**: A implementação DEVE continuar processando os fluxos de trabalho restantes em vez de abortar toda a previsão.
- **R-ERR-021**: Fluxos de trabalho que encontraram erros individuais DEVEM aparecer na saída com `sampled_runs: 0` e todos os campos de projeção zerados.
- **R-ERR-022**: A implementação DEVE emitir um aviso para stderr para cada fluxo de trabalho que encontrou um erro individual.

### 10.4 Nenhum Fluxo de Trabalho Descoberto

Se a descoberta de fluxo de trabalho resultar em zero fluxos de trabalho:

- **R-ERR-030**: A implementação DEVE emitir uma mensagem para stderr indicando que nenhum fluxo de trabalho agentic foi encontrado e descrevendo o modo de descoberta usado.
- **R-ERR-031**: A implementação DEVE sair com código `3`.

### 10.5 Diagnósticos Detalhados

Quando `--verbose` é especificado, a implementação SHOULD emitir as seguintes informações de diagnóstico adicionais para stderr:

- A lista de fluxos de trabalho descobertos e seus identificadores
- O número de execuções buscadas por fluxo de trabalho
- O número de execuções com dados de ET válidos versus artefatos ausentes
- O `λ` computado (taxa de Poisson) para cada fluxo de trabalho
- Informações de tempo para chamadas de API e execução de simulação

---

## 11. Requisitos de Implementação

### 11.1 Aleatoriedade

- **R-IMPL-001**: O motor de Monte Carlo DEVE usar um gerador de números pseudorrandômicos (PRNG) com semente criptográfica. Implementações NÃO DEVEM usar uma semente fixa, a menos que em modo de teste.
- **R-IMPL-002**: O PRNG DEVE ser semeado independentemente por invocação de previsão para garantir resultados diferentes em chamadas repetidas.

### 11.2 Desempenho

- **R-IMPL-010**: A simulação de 10.000 tentativas para um único fluxo de trabalho DEVE ser concluída dentro de 500 milissegundos em um único núcleo de CPU com um tamanho de amostra de 100 execuções.
- **R-IMPL-011**: Múltiplos fluxos de trabalho SHOULD ser previstos simultaneamente quando o ambiente de execução suportar paralelismo.
- **R-IMPL-012**: Chamadas de API para amostragem de dados SHOULD ser feitas simultaneamente entre fluxos de trabalho, sujeitas às restrições de limite de taxa da API do GitHub.

### 11.3 Saída Determinística

- **R-IMPL-020**: Dada uma amostra fixa e uma semente PRNG fixa (em modo de teste), a saída de Monte Carlo DEVE ser reprodutível. Este requisito aplica-se apenas a cenários de teste e validação; invocações de produção DEVEM usar sementes aleatórias (R-IMPL-001).

### 11.4 Precisão Numérica

- **R-IMPL-030**: Todas as computações ET intermediárias DEVEM usar aritmética de ponto flutuante de 64 bits (precisão dupla IEEE 754).
- **R-IMPL-031**: A serialização JSON de campos numéricos NÃO DEVE produzir valores não finitos (`NaN`, `+Inf`, `-Inf`). Se uma computação produzir um valor não finito, ele DEVE ser substituído por `0` e um aviso DEVE ser emitido.
- **R-IMPL-032**: Implementações NÃO DEVEM arredondar valores ET projetados em computações intermediárias; o arredondamento para fins de exibição DEVE ocorrer apenas no momento da serialização.

### 11.5 Comportamento de Status Experimental

Como o comando forecast está marcado como **Experimental**:

- **R-IMPL-040**: A implementação DEVE emitir um aviso para stderr a cada invocação indicando o status experimental do comando, a menos que `--json` seja especificado (chamadores JSON são assumidos como pipelines automatizados que lidam com avisos separadamente).
- **R-IMPL-041**: O esquema de saída JSON PODE ter novos campos adicionados em versões menores sem aviso. Chamadores DEVEM tratar campos desconhecidos como ignoráveis.

---

## 12. Testes de Conformidade

### 12.1 Requisitos da Suíte de Testes

#### 12.1.1 Testes de Interface de Comando

- **T-FC-001**: Invocação com valor `--days` inválido sai diferente de zero com erro descritivo.
- **T-FC-002**: Invocação com valor `--period` inválido sai diferente de zero com erro descritivo.
- **T-FC-003**: Invocação com `--sample < 1` sai diferente de zero.
- **T-FC-004**: Invocação com formato `--repo` inválido sai diferente de zero.
- **T-FC-005**: Argumento posicional `workflow_id` sem correspondência sai diferente de zero com identificação do valor não correspondente.

#### 12.1.2 Testes de Descoberta de Fluxo de Trabalho

- **T-FC-010**: Modo local: descobre fluxos de trabalho de `.github/workflows/*.lock.yml`.
- **T-FC-011**: Modo local: nenhum arquivo de bloqueio encontrado sai com código `3`.
- **T-FC-012**: Modo remoto: chama a API do GitHub Actions e corresponde IDs de fluxo de trabalho sem distinção entre maiúsculas e minúsculas.
- **T-FC-013**: Modo remoto: campos de frontmatter ausentes assumem zero/vazio sem erro.
- **T-FC-030**: Modo remoto: no esgotamento do limite de taxa da API do GitHub durante a descoberta de fluxo de trabalho, a implementação recua e emite um aviso antes de continuar com IDs de fluxo de trabalho fornecidos pelo chamador como resultados parciais.

#### 12.1.3 Testes de Amostragem de Dados

- **T-FC-020**: Amostragem respeita o limite `--sample`.
- **T-FC-021**: Amostragem respeita o cutoff da janela histórica `--days`.
- **T-FC-022**: Execução com artefato `aw_info.json` ausente contribui com ET zero e ainda é contada em `sampled_runs`.
- **T-FC-023**: Fluxo de trabalho com zero execuções amostradas produz projeção nil com campos zero.

#### 12.1.4 Testes do Motor de Monte Carlo

- **T-FC-031**: Com `λ ≤ 15`, o algoritmo de Knuth é usado para extração de Poisson (verificável por PRNG semeado em modo de teste).
- **T-FC-032**: Com `λ > 15`, a aproximação Normal é usada; valor extraído é não negativo.
- **T-FC-033**: Com `λ = 0`, tokens projetados são exatamente `0` para todas as tentativas.
- **T-FC-034**: Reamostragem bootstrap extrai com reposição de observações históricas de ET.
- **T-FC-035**: Apenas extrações Bernoulli bem-sucedidas contribuem ET para o total da tentativa.
- **T-FC-036**: 10.000 tentativas são executadas por fluxo de trabalho.
- **T-FC-037**: P10 ≤ P50 ≤ P90 para todas as projeções diferentes de zero.
- **T-FC-038**: `projected_effective_tokens` é igual a `p50_projected_effective_tokens`.
- **T-FC-039**: Crossover de limite: `λ = 15` usa o ramo exato de Knuth.
- **T-FC-040**: Crossover de limite: `λ > 15` usa o ramo de aproximação Normal.

#### 12.1.5 Testes de Análise de Episódio

- **T-FC-041**: Execuções compartilhando `headSha` e `headBranch` são agrupadas no mesmo episódio.
- **T-FC-042**: `runs_per_episode` é igual a `sampled_run_count / sampled_episodes`.
- **T-FC-043**: A tabela de episódio é impressa na saída do console quando qualquer fluxo de trabalho tem `runs_per_episode > 1`.
- **T-FC-044**: A tabela de episódio é suprimida quando todos os fluxos de trabalho têm `runs_per_episode = 1.0`.

#### 12.1.6 Testes de Formato de Saída

- **T-FC-050**: Saída de console contém todas as colunas necessárias.
- **T-FC-051**: Saída JSON é JSON válido em conformidade com o esquema na Seção 9.2.
- **T-FC-052**: Campo JSON `as_of` é um timestamp UTC RFC 3339 válido.
- **T-FC-053**: Array JSON `workflows` é ordenado por `projected_effective_tokens` de forma decrescente.
- **T-FC-054**: Nenhuma saída stdout (além de JSON) quando `--json` é especificado.
- **T-FC-055**: Aviso experimental emitido para stderr, a menos que `--json` seja especificado.

### 12.2 Checklist de Conformidade

| Requisito | ID de Teste | Nível | Status |
|---|---|---|---|
| Validação de flag | T-FC-001–005 | 1 | Requerido |
| Descoberta de fluxo de trabalho local | T-FC-010–011 | 1 | Requerido |
| Descoberta de fluxo de trabalho remoto | T-FC-012–013 | 2 | Requerido |
| Recuo de limite de taxa de descoberta remota e resultados parciais | T-FC-030 | 2 | Requerido |
| Amostragem de dados com limite e janela | T-FC-020–021 | 1 | Requerido |
| Tratamento gracioso de artefato ausente | T-FC-022 | 1 | Requerido |
| Projeção nil para amostra vazia | T-FC-023 | 1 | Requerido |
| Algoritmo de Poisson de Knuth (λ ≤ 15) | T-FC-031 | 1 | Requerido |
| Aproximação Normal (λ > 15) | T-FC-032 | 1 | Requerido |
| Projeção λ zero | T-FC-033 | 1 | Requerido |
| Reamostragem bootstrap | T-FC-034 | 1 | Requerido |
| Filtragem de sucesso Bernoulli | T-FC-035 | 1 | Requerido |
| Contagem de 10.000 tentativas | T-FC-036 | 1 | Requerido |
| Ordenação de percentil | T-FC-037 | 1 | Requerido |
| Consistência de campo P50 | T-FC-038 | 1 | Requerido |
| Aplicação do limite de crossover λ | T-FC-039–040 | 1 | Requerido |
| Agrupamento de episódio | T-FC-041–042 | 2 | Requerido |
| Lógica de exibição de tabela de episódio | T-FC-043–044 | 2 | Requerido |
| Colunas de saída de console | T-FC-050 | 1 | Requerido |
| Conformidade de esquema JSON | T-FC-051–054 | 2 | Requerido |
| Aviso de status experimental | T-FC-055 | 1 | Requerido |

---

## 13. Notas de Sincronização

Esta seção mapeia requisitos normativos de previsão para arquivos de implementação.

| Área Normativa | Arquivo(s) de Implementação |
|---|---|
| Motor de Monte Carlo (Poisson/Bootstrap/Bernoulli) | `pkg/cli/forecast_montecarlo.go` |
| Orquestração do comando forecast e campos de saída | `pkg/cli/forecast.go`, `pkg/cli/forecast_command.go` |
| Descoberta de fluxo de trabalho, recuo de limite de taxa e amostragem de execução | `pkg/cli/forecast.go` |
| Testes de conformidade de previsão (incluindo recuo de limite de taxa e limites λ) | `pkg/cli/forecast_montecarlo_test.go` |

Procedimento de sincronização:
1. Atualize esta especificação ao alterar algoritmos de projeção ou limites.
2. Atualize a implementação/testes Go correspondentes nos arquivos acima na mesma alteração.
3. Execute novamente os testes de previsão para verificar a paridade normativa.

---

## 14. Apêndices

### Apêndice A: Exemplo de Trabalho

#### A.1 Cenário

Um fluxo de trabalho chamado `ci-doctor` tem a seguinte amostra histórica ao longo de 30 dias:

- 42 execuções concluídas
- 5 execuções com artefato `aw_info.json` ausente (tratadas como 0 ET)
- Observações de ET (para as 37 execuções com artefatos): variam de 8.000 a 18.000, média ≈ 12.500
- 38 execuções bem-sucedidas (rendimento = 38/42 ≈ 0,905)
- Período de projeção: `month` (30 dias)

#### A.2 Taxa Observada

```
observed_runs_per_period = (42 / 30) × 30 = 42.0
λ = 42.0
```

Como λ > 15, a aproximação Normal é usada: `Normal(μ=42, σ=√42 ≈ 6,48)`.

#### A.3 Tentativa Única

Extrair `k ~ round(Normal(42, 6,48)) = 44` (exemplo).

Para cada uma das 44 execuções:
1. Extrair sucesso: `Bernoulli(0,905)` → digamos que 40 tenham sucesso.
2. Para cada uma das 40 execuções bem-sucedidas, extrair uma observação de ET do pool histórico de 37 itens (bootstrap).
3. Somar as 40 extrações de ET.

Uma tentativa pode resultar em: 40 × 12.200 (extração média) ≈ 488.000 ET.

#### A.4 Após 10.000 Tentativas

Totais de tentativa ordenados (resumo de exemplo):

```
P10 ≈ 415.000   (10º percentil — limite inferior do IC de 80%)
P50 ≈ 479.000   (mediana — projeção principal)
P90 ≈ 545.000   (90º percentil — limite superior do IC de 80%)
média ≈ 481.000
desvio_padrão ≈ 40.000
```

### Apêndice B: Racional para Seleção de Algoritmo Poisson

O algoritmo exato de Poisson de Knuth é usado para λ pequeno (≤ 15) porque produz extrações inteiras exatas da distribuição de Poisson sem viés. Para λ grande, a distribuição de Poisson converge para uma distribuição Normal (`N(λ, λ)`), tornando a aproximação Normal computacionalmente eficiente e suficientemente precisa.

O limite de λ = 15 é escolhido como o ponto de crossover onde o erro de aproximação Normal está abaixo de 1% para as caudas relevantes para a computação P10/P90. Implementações PODEM diminuir este limite (ex: para λ = 30) para maior precisão a um custo de desempenho menor.

### Apêndice C: Racional para Reamostragem Bootstrap

Modelos de projeção tradicionais assumem uma distribuição paramétrica (ex: log-normal) para o uso de token por execução. O uso de token de fluxo de trabalho agentic é frequentemente multimodal (ex: tarefas simples versus tarefas complexas de várias etapas) e exibe caudas pesadas devido a cadeias recursivas de subagentes. A reamostragem bootstrap evita a má especificação distribucional ao extrair diretamente da distribuição empírica, preservando essas características fielmente. O compromisso é que as projeções são limitadas pelos extremos observados; a extrapolação além do ET máximo observado requer suposição explícita e está fora do escopo desta especificação.

### Apêndice D: Semântica de Estimativa de Limite Inferior de Contagem de Episódio

Para fluxos de trabalho orquestradores que usam principalmente gatilhos `workflow_call` ou `workflow_dispatch`, os episódios são iniciados por chamadas de outro fluxo de trabalho, e não diretamente por eventos do GitHub. Esses links entre fluxos de trabalho estão incorporados em artefatos `aw_info.json` e estão indisponíveis durante a previsão quando os artefatos não podem ser recuperados. Como resultado, cada `workflow_call` recebido é contado como um episódio separado, fazendo com que a contagem de episódios conte episódios em excesso e subconte a vinculação. Isso significa que `runs_per_episode` pode parecer mais próximo de `1.0` do que seu valor verdadeiro. Chamadores DEVEM tratar `sampled_episodes` como uma estimativa de limite inferior neste cenário e SHOULD observar esta limitação em quaisquer documentos de planejamento de capacidade.

### Apêndice E: Considerações de Segurança

- **Escopo de credencial**: O comando forecast acessa a API do GitHub Actions usando as credenciais da CLI `gh`. Permissões de token DEVEM incluir `actions:read` para o repositório de destino. Chamadores SHOULD usar o escopo mínimo necessário.
- **Conteúdo do artefato**: O artefato `aw_info.json` PODE conter informações sensíveis, como fragmentos de prompt incorporados nos metadados de ET. Implementações NÃO DEVEM registrar payloads de artefatos em níveis de verbosidade acessíveis a usuários não administrativos.
- **Acesso ao repositório remoto**: Quando `--repo` aponta para um repositório que o chamador não possui, o chamador DEVE ter acesso de leitura explícito. A implementação NÃO DEVE tentar contornar ou circumventar controles de acesso ao repositório.
- **Saída JSON**: O esquema de saída JSON expõe padrões de consumo de token que PODEM revelar informações sobre a arquitetura do sistema e a configuração do modelo. A saída JSON SHOULD ser tratada como dados operacionais internos e não ser exposta publicamente.

---

## 15. Referências

### Referências Normativas

- **[RFC 2119]** Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels", BCP 14, RFC 2119, March 1997. <https://www.ietf.org/rfc/rfc2119.txt>
- **[RFC 3339]** Klyne, G. and Newman, C., "Date and Time on the Internet: Timestamps", RFC 3339, July 2002. <https://www.ietf.org/rfc/rfc3339.txt>
- **[ET-SPEC]** Equipe do GitHub Agentic Workflows, "Especificação de Effective Tokens". [effective-tokens-specification](/gh-aw/reference/effective-tokens-specification/)
- **[EXP-SPEC]** Equipe do GitHub Agentic Workflows, "Especificação de Experimentos A/B". [experiments-specification](/gh-aw/practices/experiments-specification/)

### Referências Informativas

- **[KNUTH-TAOCP]** Knuth, D.E., "The Art of Computer Programming, Volume 2: Seminumerical Algorithms", 3ª edição. Seção 3.4.1 (algoritmo de geração de distribuição de Poisson).
- **[BOOTSTRAP]** Efron, B. e Tibshirani, R., "An Introduction to the Bootstrap", Chapman & Hall, 1993.
- **[GH-ACTIONS-API]** GitHub, "GitHub Actions REST API Reference". <https://docs.github.com/en/rest/actions>

---

## 16. Log de Alterações

### Versão 0.1.0 (Rascunho Experimental)

- Especificação inicial para o comando `gh aw forecast`
- Definida interface de comando: flags `--days`, `--period`, `--sample`, `--repo`, `--json`, `--verbose`
- Definidos modos de descoberta de fluxo de trabalho local e remoto
- Definido procedimento de amostragem de dados e derivação de métrica por execução
- Definido motor de projeção de Monte Carlo com algoritmo de Poisson + bootstrap
- Definida análise de episódio com semântica de limite inferior para fluxos de trabalho orquestradores
- Definido formato de saída de tabela de console
- Definido esquema de saída JSON (Seções 9.2.1–9.2.6)
- Definido tratamento de erros e códigos de saída
- Definida suíte de testes de conformidade (T-FC-001 até T-FC-055)
- Adicionados apêndices: exemplo de trabalho, racional do algoritmo, considerações de segurança

---

*Copyright © 2026 Equipe do GitHub Agentic Workflows. Todos os direitos reservados.*
