---
title: Especificação de Experimentos A/B
description: Especificação formal estilo W3C para o sistema de experimento A/B do GitHub Agentic Workflows — esquema de frontmatter, seleção de variante, persistência de estado, integração de expressão, CLI de auditoria e relatórios estatísticos.
sidebar:
  order: 220
---

# Especificação de Experimentos A/B

**Versão**: 1.0.0  
**Status**: Rascunho  
**Versão Mais Recente**: [especificacao-experimentos](/gh-aw/practices/experiments-specification/)  
**Editores**: mantenedores do gh-aw

---

## Abstract

Esta especificação define o sistema de experimento A/B para GitHub Agentic Workflows (gh-aw).
Ela cobre o esquema de frontmatter `experiments:`, algoritmos de seleção de variante, backends
de persistência de estado, integração de expressão e template, estrutura de job de ativação,
integração com a CLI de auditoria e requisitos de análise estatística. Implementações conformes
fornecem aos operadores um mecanismo de infraestrutura zero para realizar experimentos
controlados sobre o comportamento do fluxo de trabalho agentico usando apenas declarações de
frontmatter de fluxo de trabalho, sem dependência de serviço externo.

Este documento consolida e substitui as seções normativas de ADR-29534,
ADR-29618, ADR-29628, ADR-29985 e ADR-29996. Ele também incorpora requisitos corretivos
identificados durante uma revisão especializada da implementação em maio de 2026.

---

## Status deste Documento

Este é um **Rascunho** de especificação. Ele pode ser atualizado, substituído ou tornado obsoleto a qualquer momento.
Uma revisão futura promoverá este documento a Recomendação Candidata uma vez que a
implementação de referência (gh-aw v1.x) satisfizer todos os requisitos de conformidade abaixo.

A promoção de **Rascunho** para **Recomendação Candidata** requer tudo o seguinte:

1. **Completude da implementação de referência**: 100% dos requisitos normativos em §§4–12 são
   implementados no `gh-aw` e mapeados para arquivos de implementação concretos (**issue de rastreamento**:
   [#31983](https://github.com/github/gh-aw/issues/31983)).
2. **Cobertura de conformidade**: Pelo menos 95% dos requisitos normativos têm testes automatizados, e
   todos os requisitos MUST/MUST NOT têm pelo menos um teste automatizado que passa (**issue de rastreamento**:
   [#31983](https://github.com/github/gh-aw/issues/31983)).
3. **Janela de estabilidade de CI**: A suíte de testes relacionada a experimentos passa no branch padrão por
   30 dias consecutivos sem regressão não resolvida na seleção de variante, persistência ou
   comportamento de relatório (**issue de rastreamento**: [#31983](https://github.com/github/gh-aw/issues/31983)).
4. **Evidência de interoperabilidade**: Pelo menos dois fluxos de trabalho de produção usando `experiments:` executam por
   um mínimo de 500 atribuições totais cada com artefatos de atribuição válidos e saída de auditoria reprodutível
   (**issue de rastreamento**: [#31983](https://github.com/github/gh-aw/issues/31983)).
5. **Aprovação de revisão**: Aprovação por escrito de pelo menos dois mantenedores do gh-aw de que as Seções 10–14
   estão completas, internamente consistentes e adequadas para publicação como Recomendação Candidata
   (**issue de rastreamento**: [#31983](https://github.com/github/gh-aw/issues/31983)).

### Sincronização

- **Quem revisa**: Os editores da especificação de experimentos (`mantenedores do gh-aw`) realizam a
  revisão primária; um proprietário de release para a versão menor atual realiza a aprovação final.
- **Quando**: A revisão ocorre no primeiro dia útil de cada mês e durante cada corte de
  release menor.
- **O que dispara uma atualização de sincronização imediata**:
  1. Qualquer mudança nos campos do esquema ou comportamento de validação de `experiments:` (§4)
  2. Qualquer mudança na seleção de variante, gating ou lógica de persistência (§§5–7)
  3. Qualquer mudança nos contratos de saída de auditoria/relatório (§§10–11)
  4. Qualquer postmortem de incidente que identifique deriva entre especificação/implementação

Quando um gatilho ocorre, as atualizações de especificação **SHOULD** (devem) ser mescladas no mesmo PR da mudança
de implementação ou em um PR de acompanhamento vinculado dentro de 3 dias úteis.

Feedback deve ser registrado como issues do GitHub contra o repositório `github/gh-aw` com a
label `experiments`.

---

## Tabela de Conteúdos

1. [Introdução](#1-introdução)
2. [Conformidade](#2-conformidade)
3. [Definições](#3-definições)
4. [Esquema de Frontmatter](#4-esquema-de-frontmatter)
5. [Algoritmos de Seleção de Variante](#5-algoritmos-de-seleção-de-variante)
6. [Gating por Intervalo de Datas](#6-gating-por-intervalo-de-datas)
7. [Persistência de Estado](#7-persistência-de-estado)
8. [Integração de Expressão e Template](#8-integração-de-expressão-e-template)
9. [Estrutura de Job de Ativação](#9-estrutura-de-job-de-ativação)
10. [Integração com a CLI de Auditoria](#10-integração-com-a-cli-de-auditoria)
11. [Análise Estatística e Relatórios](#11-análise-estatística-e-relatórios)
12. [Experimentos Simultâneos e Efeitos de Interação](#12-experimentos-simultâneos-e-efeitos-de-interação)
13. [Considerações de Segurança](#13-considerações-de-segurança)
14. [Testes de Conformidade](#14-testes-de-conformidade)
15. [Referências](#15-referências)
16. [Apêndices](#apêndices)
17. [Log de Mudanças](#log-de-mudanças)

---

## 1. Introdução

### 1.1 Objetivo

Fluxos de trabalho agenticos compilados pelo gh-aw usam um modelo de configuração baseado em frontmatter.
As equipes que executam esses fluxos de trabalho precisam de um mecanismo de primeira classe para testar diferentes variantes de prompt
(tom, verbosidade, persona, flags de funcionalidade embutidas no prompt) em execuções de fluxo de trabalho sucessivas.
Sem tal mecanismo, o teste de variante é ad-hoc, não rastreado e estatisticamente desequilibrado.

Esta especificação define um sistema de experimento A/B autocontido que não requer serviço externo,
não requer coordenação manual e não requer mudanças fora do frontmatter do fluxo de trabalho.

### 1.2 Escopo

Esta especificação cobre:

- O esquema de frontmatter `experiments:` e suas duas formas sintáticas (bare-array, rich-object).
- Algoritmos de seleção de variante: round-robin balanceado (menos usado), aleatório ponderado e fallback com gating de data.
- Backends de persistência de estado: git-branch (`repo`) e cache do GitHub Actions (`cache`).
- Integração de expressão e template Handlebars no prompt do fluxo de trabalho compilado.
- A estrutura do job de ativação gerada pelo compilador.
- A interface de filtragem da CLI `gh aw audit` para execuções anotadas com experimentos.
- Requisitos para fluxos de trabalho de análise estatística e relatório que consomem artefatos de experimento.

Esta especificação **não** cobre:

- A arquitetura interna do compilador além do que é observável na fronteira do YAML compilado.
- Dashboards de análise externos ou plataformas de experimento de terceiros.
- Algoritmos de bandit multi-armado ou alocação adaptativa (considerado trabalho futuro).

### 1.3 Metas de Design

1. **Zero dependências externas** — todo estado é armazenado dentro do repositório ou infraestrutura do GitHub Actions.
2. **Declarativo** — a configuração completa do experimento vive no frontmatter do fluxo de trabalho.
3. **Retrocompatível** — adicionar `experiments:` a um fluxo de trabalho existente NÃO DEVE quebrar nenhuma saída compilada existente; removê-lo DEVE restaurar a saída original exatamente.
4. **Estatisticamente sólido** — o algoritmo de seleção padrão garante balanço de variante aproximado no número mínimo de execuções.
5. **Observável** — cada execução produz um artefato durável registrando a atribuição de variante, e atributos OTEL propagam atribuições para backends de tracing distribuído automaticamente.

---

## 2. Conformidade

### 2.1 Notação de Requisitos

As palavras-chave **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**,
**SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY** e **OPTIONAL** neste documento
devem ser interpretadas conforme descrito na [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### 2.2 Classes de Conformidade

Esta especificação define três classes de conformidade:

| Classe | Requisitos |
|---|---|
| **Nível 1 — Básico** | Satisfaz todos os requisitos MUST/MUST NOT em §4, §5, §8 e §9 |
| **Nível 2 — Padrão** | Nível 1 mais §6 (gating de data), §7 (persistência de estado), §10 (CLI de auditoria) |
| **Nível 3 — Completo** | Nível 2 mais §11 (análise estatística e relatórios) e §12 (experimentos simultâneos) |

Uma implementação é considerada **não-conforme** se falhar em qualquer requisito MUST ou MUST NOT
no nível que ela alega implementar.

### 2.3 Conteúdo Normativo vs. Informativo

Seções contendo requisitos numerados (por exemplo, "R-SCHEMA-001") são **normativas**.
Notas, blocos de racionalização e apêndices são **informativos** e não carregam peso de conformidade.

---

## 3. Definições

| Termo | Definição |
|---|---|
| **Experimento** | Um teste A/B nomeado declarado no frontmatter do fluxo de trabalho, associando um identificador a duas ou mais strings de variante. |
| **Variante** | Um valor de string nomeado que representa um braço de tratamento em um experimento. |
| **Variante de controle** | A primeira variante na array `variants` declarada; usada como linha de base e como fallback durante o gating de data. |
| **Contador de invocação** | Um inteiro por experimento e por variante armazenado em `state.json` que registra o número cumulativo de vezes que uma variante foi selecionada. |
| **state.json** | O arquivo JSON que armazena contadores de invocação e histórico de atribuição por execução para todos os experimentos em um único fluxo de trabalho. |
| **Registro de execução** | Uma entrada no array `runs` de `state.json` registrando o ID da execução, timestamp e atribuições de variante para uma execução de fluxo de trabalho. |
| **ID de fluxo de trabalho sanitizado** | O nome base do fluxo de trabalho (sem `.md`) com hífens removidos e minúsculo, usado como um componente de chave de cache/branch. |
| **Job de ativação** | O job `activation` do GitHub Actions gerado pelo compilador que escolhe variantes e as expõe para jobs a jusante. |
| **Artefato de experimento** | Um artefato do GitHub Actions chamado `{sanitizedID}-experiment` carregado pelo job de ativação e contendo `state.json` e `assignments.json`. |
| **assignments.json** | Um arquivo no artefato de experimento contendo apenas as atribuições de variante da execução atual como um objeto JSON plano. |

---

## 4. Esquema de Frontmatter

### 4.1 Declaração de Campo

**R-SCHEMA-001**: O frontmatter do fluxo de trabalho **MAY** (pode) incluir um campo `experiments`. Sua ausência
**MUST** (deve) produzir nenhuma mudança na saída compilada.

**R-SCHEMA-002**: O valor de `experiments` **MUST** ser um mapa YAML. Valores que não são mapas
**MUST** ser rejeitados em tempo de compilação com um erro descritivo.

**R-SCHEMA-003**: Cada chave no mapa `experiments`, exceto a chave reservada `storage`
(§7.1), **MUST** ser um nome de experimento que corresponda à expressão regular
`^[a-zA-Z_][a-zA-Z0-9_]*$`. Chaves que não correspondem **MUST** ser silenciosamente ignoradas com um
aviso de tempo de compilação emitido para stderr.

> **Nota (informativa)**: O padrão de identificador garante que nomes de experimento possam ser usados como
> nomes de saída de step do GitHub Actions e embutidos em expressões `${{ experiments.<name> }}`
> sem notação de colchetes.

### 4.2 Forma Bare-Array

**R-SCHEMA-004**: Cada valor de experimento **MAY** ser declarado como uma sequência YAML de duas ou
mais strings:

```yaml
experiments:
  prompt_style: [concise, detailed]
```

**R-SCHEMA-005**: Um valor bare-array com menos de duas entradas **MUST NOT** ser aceito;
o compilador **MUST** emitir um erro de tempo de compilação.

### 4.3 Forma de Objeto Rico

**R-SCHEMA-006**: Cada valor de experimento **MAY** alternativamente ser declarado como um objeto YAML
com um campo obrigatório `variants` e campos de metadados opcionais. As duas formas **MUST** ser
aceitas no mesmo mapa `experiments` sem conflito.

**R-SCHEMA-007**: O campo `variants` **MUST** ser uma array de duas ou mais strings não vazias.
A mesma restrição de mínimo de duas variantes de R-SCHEMA-005 se aplica.

**R-SCHEMA-008**: Os campos opcionais seguintes são definidos para a forma de objeto:

| Campo | Tipo | Descrição |
|---|---|---|
| `description` | string | Explicação legível por humanos do que o experimento testa. |
| `hypothesis` | string | Declarações de hipótese nula e alternativa. |
| `metric` | string | Nome da métrica primária a observar (ex: `effective_tokens`). |
| `secondary_metrics` | string[] | Métricas adicionais a coletar. |
| `guardrail_metrics` | object[] | Limites que não devem degradar (veja §4.4). |
| `min_samples` | integer ≥ 1 | Execuções mínimas por variante antes que a análise seja confiável. Padrão 20. |
| `weight` | integer[] | Pesos de probabilidade por variante (veja §5.2). |
| `issue` | integer ≥ 1 | Número da issue do GitHub rastreando este experimento. |
| `start_date` | string (YYYY-MM-DD) | Experimento inativo antes desta data (veja §6). |
| `end_date` | string (YYYY-MM-DD) | Experimento inativo após esta data (veja §6). |
| `analysis_type` | string enum | Teste estatístico para relatórios automatizados (veja §11.2). |
| `tags` | string[] | Labels de forma livre para filtragem de dashboard. |
| `notify` | object | Destino de alerta de significância (veja §4.5). |

**R-SCHEMA-009**: Os campos `weight`, `issue`, `min_samples`, `start_date`, `end_date`, `analysis_type`,
`tags` e `notify` não exercem efeito na atribuição de variante fora de suas subseções documentadas. `description`, `hypothesis`, `metric`, `secondary_metrics` e `tags` são
puramente informativos em tempo de execução.

**R-SCHEMA-010**: Implementações **MUST NOT** introduzir propriedades adicionais na forma de objeto
sem uma atualização de esquema correspondente; o compilador **MUST** rejeitar chaves desconhecidas sob
modo estrito.

### 4.4 Métricas de Guardrail

**R-SCHEMA-011**: Cada entrada em `guardrail_metrics` **MUST** ser um objeto com exatamente dois
campos de string: `name` e `threshold`. O `threshold` **MUST** corresponder ao padrão
`^(>=|<=|==|>|<)-?\d+(\.\d+)?$` (ex: `>=0.95`, `==0`, `<=0.05`).

**R-SCHEMA-012**: A avaliação de guardrail é **INFORMATIVA** no nível de esquema — o compilador
não impõe guardrails em tempo de compilação. Ferramentas de relatório (§11) **MUST** avaliar cada
guardrail e incluir o status de aprovado/reprovado em sua saída.

### 4.5 Objeto de Notificação

**R-SCHEMA-013**: O objeto `notify` **MUST** conter apenas as chaves `discussion` e/ou
`issue`, cada uma das quais **MUST** ser um inteiro positivo (mínimo 1). Chaves desconhecidas em `notify`
**MUST** ser rejeitadas pela validação de esquema.

**R-SCHEMA-014**: Quando `notify.issue` é definido e o fluxo de trabalho de relatório posta um comentário nessa issue, o fluxo de trabalho compilado **MUST** declarar `permissions: issues: write`. Implementações
que geram fluxos de trabalho de relatório **MUST** adicionar automaticamente essa permissão quando `notify.issue`
estiver presente em qualquer configuração de experimento dentro do escopo desse fluxo de trabalho.

> **Nota (informativa)**: Falha em incluir `issues: write` faz com que a postagem de comentário
> falhe silenciosamente com uma resposta 403. Isso foi identificado como um defeito no
> fluxo de trabalho `daily-experiment-report` (revisão de maio de 2026).

---

## 5. Algoritmos de Seleção de Variante

### 5.1 Round-Robin Balanceado (Menos Usado)

**R-SELECT-001**: Quando `weight` está ausente ou inválido (§5.2), implementações **MUST** selecionar
a variante com a contagem de invocação cumulativa mais baixa armazenada em `state.json`.

**R-SELECT-002**: Quando duas ou mais variantes compartilham a contagem mais baixa — incluindo o
estado inicial onde todas as contagens são zero — implementações **MUST** quebrar empates selecionando
uniformemente ao acaso entre as variantes empatadas. Nenhuma variante **MUST** ser sistematicamente favorecida por posição.

**R-SELECT-003**: Após selecionar uma variante via round-robin, implementações **MUST** incrementar
o contador de invocação para essa variante em `state.json` antes de persistir o estado.

> **Nota (informativa)**: Round-robin garante que ao longo de K×N execuções cada variante apareça
> aproximadamente N vezes, atingindo balanço em muito menos execuções do que a seleção aleatória. O
> desempate aleatório na primeira execução garante que nenhuma variante seja sistematicamente favorecida.

### 5.2 Seleção Aleatória Ponderada

**R-SELECT-004**: Quando `weight` é fornecido e seu comprimento é igual ao comprimento de `variants`,
implementações **MUST** usar seleção aleatória ponderada: cada variante é escolhida com probabilidade
proporcional ao seu valor de peso.

**R-SELECT-005**: Quando todos os valores de peso são zero, implementações **MUST** retornar a
variante de controle (primeira entrada em `variants`) sem erro.

**R-SELECT-006**: A seleção aleatória ponderada **MUST** incrementar o contador de invocação para a
variante selecionada antes de persistir o estado.

> **Nota (correção normativa)**: ADR-29618 Regra 9 declarou incorretamente que a seleção ponderada
> "NÃO DEVE incrementar nenhum contador de variante." Esta regra é, por meio deste, substituída. Incrementos de
> contador para seleção ponderada são necessários para permitir o acompanhamento de progresso de `min_samples` e histórico
> preciso por execução. A implementação de referência (`pick_experiment.cjs`) já implementa
> este comportamento correto chamando `recordVariant` incondicionalmente após ambos os caminhos de seleção.

**R-SELECT-007**: Quando `weight` é fornecido mas seu comprimento não é igual ao comprimento de
`variants`, implementações **MUST** tratar `weight` como ausente e cair para a seleção
round-robin (R-SELECT-001).

> **Nota (estatística, informativa)**: Cálculos de potência padrão assumem alocações balanceadas.
> Quando pesos não são uniformes (ex: `[70, 30]`), o tamanho efetivo da amostra é reduzido.
> O alvo `min_samples` deve ser interpretado como o mínimo necessário para o **grupo menor**. Para uma divisão 70/30, os experimentadores devem definir `min_samples` para a contagem desejada para o braço de 30% e esperar que o braço de 70% acumule proporcionalmente mais observações.

### 5.3 Exposição de Variante

**R-SELECT-008**: Implementações **MUST** expor cada variante selecionada como uma saída de step nomeada
`steps.pick-experiment.outputs.<experiment-name>` e **MUST** também definir uma saída de step JSON combinada
`steps.pick-experiment.outputs.experiments` contendo todas as atribuições de variante como um
objeto JSON serializado.

**R-SELECT-009**: Nomes de experimento **MUST** ser ordenados alfabeticamente ao construir a
saída JSON `experiments` para produzir saída determinística e reprodutível entre execuções com
estado idêntico.

---

## 6. Gating por Intervalo de Datas

**R-DATE-001**: Quando `start_date` é fornecido e a data atual (UTC, formato `YYYY-MM-DD`)
é estritamente anterior a `start_date`, implementações **MUST** retornar a variante de controle
sem incrementar qualquer contador.

**R-DATE-002**: Quando `end_date` é fornecido e a data atual (UTC, formato `YYYY-MM-DD`)
é estritamente posterior a `end_date`, implementações **MUST** retornar a variante de controle
sem incrementar qualquer contador.

**R-DATE-003**: A comparação de data **MUST** usar data UTC. Deslocamentos de fuso horário local **MUST NOT**
afetar o resultado.

**R-DATE-004**: Quando tanto `start_date` quanto `end_date` são fornecidos e a data UTC atual está
dentro do intervalo inclusivo `[start_date, end_date]`, o experimento está ativo e a seleção
normal de variante (§5) se aplica.

**R-DATE-005**: Se `start_date` ou `end_date` não corresponderem ao padrão `YYYY-MM-DD`,
implementações **SHOULD** (deveriam) tratá-los como ausentes (ignorar silenciosamente) em vez de falhar,
para preservar compatibilidade futura.

---

## 7. Persistência de Estado

### 7.1 Configuração de Armazenamento

**R-STORE-001**: O mapa `experiments:` **MUST** suportar uma chave reservada `storage` cujo valor
é um entre `"repo"` (padrão) ou `"cache"`. Qualquer outro valor **MUST** produzir um aviso de tempo de compilação
e cair para `"repo"`.

**R-STORE-002**: Quando `storage` está ausente, implementações **MUST** comportar-se como se
`storage: repo` tivesse sido especificado.

**R-STORE-003**: A chave `storage` **MUST NOT** ser tratada como um nome de experimento; ela **MUST** ser
excluída da extração de configuração de experimento.

### 7.2 Formato de `state.json`

**R-STORE-004**: O arquivo `state.json` **MUST** ser um objeto JSON válido com a seguinte
estrutura de nível superior:

```json
{
  "counts": {
    "<experiment_name>": {
      "<variant>": <integer>
    }
  },
  "runs": [
    {
      "run_id": "<string>",
      "timestamp": "<ISO-8601 UTC string>",
      "assignments": {
        "<experiment_name>": "<variant>"
      }
    }
  ]
}
```

**R-STORE-005**: O array `runs` **MUST** ser podado para no máximo 512 entradas (mantendo as mais
recentes) para evitar crescimento ilimitado.

**R-STORE-006**: Ao carregar um `state.json` que não possui campo `runs` (formato legado),
implementações **MUST** inicializar `runs` para uma array vazia e continuar normalmente.

**R-STORE-007**: Quando pelo menos um experimento é atribuído em uma execução, implementações **MUST**
anexar um registro de execução a `state.runs` antes de persistir. Cada registro **MUST** conter:
- `run_id`: o valor de `GITHUB_RUN_ID`, ou `""` quando ausente.
- `timestamp`: um timestamp UTC ISO-8601 do momento da seleção.
- `assignments`: um objeto mapeando cada nome de experimento atribuído para sua variante selecionada.

**R-STORE-008**: Quando nenhum experimento é atribuído (ex: todos os experimentos estão fora de sua
janela de data), implementações **MUST NOT** anexar um registro de execução ou reescrever `state.json`.

### 7.3 Modo de Armazenamento `repo`

**R-STORE-REPO-001**: Quando `storage: repo` está ativo, o job de ativação **MUST** carregar
estado do experimento buscando `state.json` do branch git nomeado
`experiments/{sanitizedWorkflowID}` via API REST do GitHub (GET /repos/{owner}/{repo}/contents/{path}).

**R-STORE-REPO-002**: Uma resposta 404 (branch ou arquivo não existe) **MUST** ser tratada como um
estado inicial vazio; o job de ativação **MUST NOT** falhar.

**R-STORE-REPO-003**: Após a conclusão do job de ativação, um job dedicado `push_experiments_state`
**MUST** ser gerado. Este job **MUST**:
- Baixar o artefato de experimento da execução atual.
- Commitar o `state.json` e `assignments.json` atualizados para o branch git de experimentos.
- Declarar `permissions: contents: write`.
- Ser listado como uma dependência do job de conclusão para garantir que o estado seja persistido antes que o
  fluxo de trabalho termine.

**R-STORE-REPO-004**: O commit **SHOULD** ser feito via mutação `createCommitOnBranch`
do GraphQL do GitHub (produzindo um commit verificado e assinado). Um `git push` simples
**MAY** ser usado como fallback quando a mutação GraphQL estiver indisponível.

**R-STORE-REPO-005**: A etapa de push **SHOULD** implementar lógica de nova tentativa com backoff exponencial
(mínimo 3 tentativas, atraso base ≥ 1 segundo) para lidar com falhas de API transitórias e conflitos de push concorrentes.

> **Nota (condição de corrida, informativa)**: Quando duas execuções de fluxo de trabalho começam concorrentemente, ambas lerão o mesmo `state.json` do branch antes que qualquer uma tenha commitado sua atualização. Ambas as execuções, portanto, selecionarão a mesma variante menos usada. A lógica de nova tentativa em R-STORE-REPO-005
> lida com conflitos de escrita no momento do push, mas não impede seleções de variante duplicadas no momento da leitura. Em fluxos de trabalho de baixa frequência (cron diário) isso efetivamente nunca é um problema.
> Em fluxos de trabalho de alta frequência (a cada hora ou a cada commit), experimentadores devem considerar uma
> pequena probabilidade de execuções temporariamente desbalanceadas. Uma revisão futura desta especificação
> **MAY** abordar isso com uma guarda de concorrência otimista na etapa de busca.

### 7.4 Modo de Armazenamento `cache`

**R-STORE-CACHE-001**: Quando `storage: cache` está explicitamente definido, o job de ativação **MUST**
restaurar o estado do experimento do cache do GitHub Actions usando uma chave da forma
`experiments-{sanitizedWorkflowID}-{GITHUB_RUN_ID}` e um prefixo de chave de restauração
`experiments-{sanitizedWorkflowID}-`.

**R-STORE-CACHE-002**: O job de ativação **MUST** salvar o estado do experimento de volta no cache após
a seleção de variante usando `if: always()`.

**R-STORE-CACHE-003**: Quando `storage: cache` está ativo, nenhum job `push_experiments_state`
**SHALL** ser gerado.

**R-STORE-CACHE-004**: Implementações **MUST NOT** exigir permissão `contents: write` quando
`storage: cache` está configurado.

> **Nota (informativa)**: O cache do GitHub Actions tem uma política de despejo por inatividade de 7 dias. O estado
> acumulado durante um experimento pode ser perdido silenciosamente durante feriados ou entre execuções infrequentes. Por
> este motivo, `repo` é o modo de armazenamento padrão. Use `cache` apenas quando
> `contents: write` não puder ser concedido ao fluxo de trabalho.

### 7.5 Artefato de Experimento

**R-STORE-ARTIFACT-001**: O job de ativação **MUST** carregar o diretório de estado do experimento
como um artefato do GitHub Actions chamado `{sanitizedWorkflowID}-experiment` (ou `experiment` para
gatilhos `workflow_call`) com `if: always()` e um período de retenção de pelo menos 30 dias.

**R-STORE-ARTIFACT-002**: Quando `assignments.json` existe no diretório de estado, ele **MUST**
ser incluído no artefato ao lado de `state.json`.

---

## 8. Integração de Expressão e Template

### 8.1 Reescrita de Expressão do Compilador

**R-EXPR-001**: O compilador **MUST** reescrever cada expressão `${{ experiments.<name> }}` no
frontmatter ou fonte de prompt para `steps.pick-experiment.outputs.<name>` durante a
fase de extração de expressão, para que o valor de tempo de execução seja injetado pelo motor de expressão do GitHub Actions.

**R-EXPR-002**: Cada experimento **MUST** ser mapeado para uma variável de ambiente chamada
`GH_AW_EXPERIMENTS_<NAME>` (em maiúsculas) que resolve para `steps.pick-experiment.outputs.<name>`.
Esta variável de ambiente **MUST** ser definida em cada etapa do fluxo de trabalho que realiza interpolação de prompt ou substituição de template.

### 8.2 Integração de Template Handlebars

**R-EXPR-003**: Implementações **MUST** substituir placeholders `__GH_AW_EXPERIMENTS_<NAME>__`
no texto do prompt bruto **antes** da renderização do template Handlebars, para que
condicionais `{{#if experiments.<name> == "value" }}` avaliem a variante de tempo de execução real.

**R-EXPR-004**: Implementações **MUST NOT** passar placeholders `__GH_AW_EXPERIMENTS_*__` brutos
para o motor de renderização Handlebars; todas as substituições **MUST** ocorrer em uma etapa anterior.

**R-EXPR-005**: O helper `isTruthy` usado em condicionais Handlebars **MUST** tratar a
string `"no"` como falsy, além dos valores falsy padrão `""`, `"false"`, `"0"`,
`undefined` e `null`. Isso permite experimentos de flag sim/não onde
`{{#if experiments.feature }}` avalia como falso quando a variante `no` está ativa.

> **Nota (informativa)**: O comportamento falsy `"no"` é uma escolha de design deliberada que permite
> experimentos simples de flag booleana (`feature: [yes, no]`). Ele difere da veracidade
> padrão do JavaScript e deve ser claramente documentado para colaboradores.

---

## 9. Estrutura de Job de Ativação

**R-JOB-001**: Quando o campo `experiments` está presente no frontmatter, o job de ativação
compilado **MUST** incluir as etapas de experimento definidas em §9.1 ou §9.2 conforme apropriado.

**R-JOB-002**: Implementações **MUST NOT** injetar etapas de experimento em fluxos de trabalho que não
declaram o campo `experiments` no frontmatter.

**R-JOB-003**: O job de ativação **MUST** expor uma saída `needs.activation.outputs.experiments`
contendo o objeto completo de atribuição de variante JSON para que jobs a jusante possam
referenciá-lo via `needs.activation.outputs.experiments`.

### 9.1 Ordem de Etapa de Armazenamento `cache`

Quando `storage: cache`, o job de ativação **MUST** incluir as seguintes etapas em ordem:

1. **Restaurar estado do experimento** — `actions/cache/restore` com a chave específica do fluxo de trabalho.
2. **Escolher variantes de experimento** — `pick_experiment.cjs` via `actions/github-script`.
3. **Salvar estado do experimento** — `actions/cache/save` com `if: always()`.
4. **Carregar artefato de experimento** — `actions/upload-artifact` com `if: always()`.

### 9.2 Ordem de Etapa de Armazenamento `repo`

Quando `storage: repo` (padrão), o job de ativação **MUST** incluir as seguintes etapas em ordem:

1. **Restaurar estado do experimento do git** — `load_experiment_state_from_repo.cjs` via `actions/github-script`.
2. **Escolher variantes de experimento** — `pick_experiment.cjs` via `actions/github-script`.
3. **Carregar artefato de experimento** — `actions/upload-artifact` com `if: always()`.

Um job `push_experiments_state` separado (R-STORE-REPO-003) commit o estado atualizado após
o job de ativação ser concluído.

### 9.3 Atributos de Recurso OTEL

**R-JOB-004**: Após a seleção de variante, quando pelo menos um experimento é atribuído,
`pick_experiment.cjs` **MUST** chamar `core.exportVariable("OTEL_RESOURCE_ATTRIBUTES", …)`
com pares chave-valor da forma `experiment.<name>=<variant>`, separados por vírgula quando múltiplos
experimentos estão ativos.

**R-JOB-005**: Quando `OTEL_RESOURCE_ATTRIBUTES` já está definido, implementações **MUST** anexar
os atributos de experimento ao valor existente com um separador de vírgula em vez de sobrescrever.

**R-JOB-006**: Quando nenhum experimento é atribuído, implementações **MUST NOT** modificar
`OTEL_RESOURCE_ATTRIBUTES`.

---

## 10. Integração com a CLI de Auditoria

### 10.1 Flags de Filtro

**R-AUDIT-001**: O comando `gh aw audit` **MUST** aceitar uma flag `--experiment <name>` que
filtra execuções para aquelas com uma atribuição de variante para o experimento nomeado.

**R-AUDIT-002**: O comando `gh aw audit` **MUST** aceitar uma flag `--variant <value>` que,
quando combinada com `--experiment`, restringe ainda mais os resultados para execuções atribuídas a esse valor exato de variante.

**R-AUDIT-003**: `--variant` usado sem `--experiment` **MUST** causar um código de saída não-zero
com uma mensagem de erro que inclui uma sugestão para adicionar `--experiment`.

**R-AUDIT-004**: Quando uma execução é ignorada pelo filtro, uma mensagem informativa **MUST** ser
emitida para stderr identificando o ID da execução, o nome do experimento e (quando aplicável) a
variante necessária.

### 10.2 Exibição de Visão Geral de Execução

**R-AUDIT-005**: A seção Overview da execução **MUST** incluir um campo `Experiment` quando o
artefato de experimento da execução contiver uma ou mais atribuições.

**R-AUDIT-006**: O label de experimento **MUST** ser formatado como uma lista separada por vírgula,
ordenada alfabeticamente de pares `name=variant` (ex: `caveman=yes, style=concise`).

**R-AUDIT-007**: O campo `Experiment` **MUST** ser omitido da saída de console e JSON quando
nenhuma atribuição de experimento estiver presente (semântica `omitempty`).

### 10.3 Busca de Atribuição por Execução

**R-AUDIT-008**: Quando `state.runs` não está vazio e o mapa `assignments` do último registro
não está vazio, o relator de auditoria **MUST** usar as atribuições desse registro diretamente como os
dados de experimento da execução atual.

**R-AUDIT-009**: Quando `state.runs` está vazio, ausente ou o mapa `assignments` do último registro
está vazio, o relator de auditoria **MUST** cair para a heurística de contagem máxima: a variante com a
contagem cumulativa mais alta é assumida como tendo sido selecionada na execução mais recente; empates são
quebrados pela ordem de variante ordenada.

### 10.4 Aplicação de Filtro

**R-AUDIT-010**: Implementações **MUST** aplicar o filtro de experimento/variante antes de chamar
qualquer código de renderização de relatório. Uma execução filtrada **MUST** retornar `nil`, não um erro.

**R-AUDIT-011**: Implementações **MUST** aplicar o filtro tanto no caminho de resumo em cache quanto
no caminho de processamento fresco para comportamento consistente.

**R-AUDIT-012**: Implementações **SHOULD** extrair dados de experimento no máximo uma vez por
invocação de `AuditWorkflowRun` para evitar leituras de artefato redundantes.

**R-AUDIT-013**: Quando nem `--experiment` nem `--variant` estão definidos, implementações **MUST NOT**
ler o artefato de experimento apenas para fins de filtragem.

---

## 11. Análise Estatística e Relatórios

Esta seção aplica-se à classe de conformidade **Nível 3 — Completo** (§2.2) e a qualquer
fluxo de trabalho automatizado que relata sobre resultados de experimento.

### 11.1 Fonte de Atribuição por Execução

**R-STAT-001**: Ferramentas de relatório que consomem arquivos `state.json` **MUST** derivar atribuições de variante por execução
do array `state.runs` quando estiver presente e não vazio.

**R-STAT-002**: Ferramentas de relatório **MUST NOT** usar o método de inferência de delta de contagem cumulativa
(comparando snapshots consecutivos) como a fonte de atribuição primária quando `state.runs` estiver
disponível. O método delta **MAY** ser usado como um fallback para arquivos de estado legados sem
array `runs`.

> **Nota (informativa)**: O método delta é frágil — ele falha quando múltiplas execuções terminam
> entre snapshots baixados, quando execuções são canceladas antes da etapa de experimento, ou quando
> `state.json` é buscado de diferentes pontos no histórico de artefatos. O array `runs`,
> introduzido na v1.1.0 (ADR-29985), fornece registros de atribuição por execução exatos e auditáveis.

### 11.2 Testes Estatísticos

**R-STAT-003**: Quando `analysis_type` é declarado para um experimento, ferramentas de relatório **SHOULD**
usar o teste especificado para análise de significância:

| valor `analysis_type` | Teste a aplicar |
|---|---|
| `t_test` | Teste t de Welch para duas amostras (não assume variância igual) |
| `mann_whitney` | Teste de classificação não paramétrico U de Mann-Whitney |
| `proportion_test` | Teste z para duas proporções |
| `bayesian_ab` | Análise A/B bayesiana (probabilidade posterior de superioridade) |

**R-STAT-004**: Quando `analysis_type` está ausente, ferramentas de relatório **SHOULD**
padronizar para o teste z para duas proporções para resultados binários (sucesso/falha) e teste t de Welch para métricas contínuas (ex: duração).

### 11.3 Correção de Comparações Múltiplas

**R-STAT-005**: Quando um experimento declara K ≥ 3 variantes e ferramentas de relatório realizam
comparações pareadas contra o controle, o limite de significância **SHOULD** ser ajustado
usando a correção de Bonferroni: `α_ajustado = 0.05 / (K − 1)`.

> **Nota (informativa)**: Sem correção, a probabilidade de pelo menos um falso positivo
> entre K−1 testes pareados em α = 0.05 é aproximadamente 1 − (1 − 0.05)^(K−1). Para K = 3
> isso é ~9.75%; para K = 5 excede 18%. A correção de Bonferroni é conservadora mas
> simples. O procedimento step-down de Holm-Bonferroni é uma alternativa menos conservadora.

**R-STAT-006**: Quando uma correção de comparação múltipla é aplicada, ferramentas de relatório **MUST**
declarar o método de correção e o limite α ajustado na saída do relatório.

### 11.4 Gatilho de Tamanho de Amostra Mínimo

**R-STAT-007**: Ferramentas de relatório **MUST NOT** emitir uma recomendação de PROMOTE para qualquer variante
até que todas as variantes no experimento tenham acumulado pelo menos `min_samples` execuções (ou 20 se
`min_samples` não for declarado). Quando qualquer variante está abaixo do limite, a recomendação
**MUST** ser EXTEND.

**R-STAT-008**: Quando pesos não são uniformes (§5.2), o alvo `min_samples` aplica-se ao
**menor grupo esperado**. Para um experimento de divisão `weight: [70, 30]` com `min_samples: 30`, o
braço de controle não é elegível para análise até que o braço de 30% tenha pelo menos 30 observações,
mesmo que o braço de 70% tenha acumulado muito mais observações.

### 11.5 Avaliação de Guardrail

**R-STAT-009**: Ferramentas de relatório que avaliam `guardrail_metrics` **MUST** emitir um status
`GUARDRAIL_FAILED` para qualquer variante que viole um limite declarado, e **MUST** sobrescrever a
recomendação para ABANDON independentemente do p-value da métrica primária.

**R-STAT-010**: Experimentos com múltiplas variantes **MUST** mostrar status de aprovado/reprovado de guardrail por variante,
não agregado através do experimento.

### 11.6 Permissões do Fluxo de Trabalho de Relatório

**R-STAT-011**: Qualquer fluxo de trabalho automatizado que posta comentários em issues (ex: via `notify.issue`
ou criação de comentário de issue baseado em etapa) **MUST** declarar `permissions: issues: write` em seu
frontmatter.

**R-STAT-012**: Qualquer fluxo de trabalho automatizado que posta discussões **MUST** declarar
`permissions: discussions: write`.

---

## 12. Experimentos Simultâneos e Efeitos de Interação

**R-MULTI-001**: Cada experimento no mapa `experiments` **MUST** ser atribuído independentemente.
O algoritmo de seleção para um experimento **MUST NOT** depender da variante selecionada de
qualquer outro experimento.

**R-MULTI-002**: Implementações **SHOULD NOT** executar mais de três experimentos simultaneamente
em um único fluxo de trabalho. Quando mais de três experimentos estão ativos, um aviso de tempo de compilação
**SHOULD** ser emitido.

> **Nota (estatística, informativa)**: Quando dois ou mais experimentos estão ativos simultaneamente,
> diferenças observadas em métricas de resultado podem ser causadas por qualquer experimento individualmente ou
> pela interação deles (i.e., uma combinação específica de valores de variante). Essa violação do
> Stable Unit Treatment Value Assumption (SUTVA) infla o risco de má atribuição.
> Por exemplo, se `prompt_style=concise` e `emoji_density=heavy` estão ambos ativos, é
> impossível determinar a partir da análise pareada sozinha se uma mudança na qualidade
> de saída foi causada por verbosidade, uso de emoji ou a combinação. Experimentadores que precisam medir
> interações **MUST** usar um design fatorial completo e garantir tamanho de amostra suficiente para
> todas as combinações de células K₁ × K₂ × ….

**R-MULTI-003**: Ferramentas de relatório **MUST** notar em sua saída quando múltiplos experimentos estavam
ativos simultaneamente em execuções incluídas na janela de análise, para alertar revisores sobre possíveis confusões.

**R-MULTI-004**: Experimentos que alteram a chave `engine:` do frontmatter **MUST NOT** ser
implementados dentro de um único arquivo de fluxo de trabalho. Experimentos de troca de motor
**MUST** usar arquivos de fluxo de trabalho compilados separados (um por variante), que podem então ser comparados via suas respectivas métricas de execução do GitHub Actions.

**R-MULTI-005**: Quando dois ou mais experimentos estão ativos simultaneamente na mesma
janela de análise, ferramentas de relatório **MUST** detectar e limitar o risco de interação preservando o vetor de atribuição
completo por execução e avaliando se cada célula de combinação observada tem cobertura de amostra suficiente.
Se efeitos de interação não puderem ser limitados (por exemplo, células esparsas abaixo de
`min_samples`), o relatório **MUST** emitir um status explícito de risco de interação e **MUST NOT**
recomendar PROMOTE para variantes afetadas.

### 12.1 Normas de Resolução de Conflitos

Um **conflito** ocorre quando dois ou mais experimentos ativos simultaneamente atribuiriam
configurações incompatíveis à mesma execução de fluxo de trabalho. Esta subseção define comportamento normativo para cada modo de armazenamento.

**R-CONFLICT-001 (geral)**: Quando dois experimentos atribuem variantes que juntas produzem uma
configuração de fluxo de trabalho logicamente inválida (ex: duas variantes `engine:` via chaves de
experimento separadas), o compilador **MUST** rejeitar o fluxo de trabalho em tempo de compilação com um
erro descritivo. A detecção de conflito em tempo de execução **NÃO** é um substituto para validação de tempo de compilação.

#### 12.1.1 Resolução de Conflitos para Modo de Armazenamento `repo`

**R-CONFLICT-REPO-001**: Sob armazenamento `repo`, a seleção de variante de cada experimento lê e
escreve uma chave independente em `state.json`. Não há estado mutável compartilhado entre
experimentos na camada de seleção. Atribuições de variante para o experimento A **MUST NOT** bloquear
ou sobrescrever atribuições de variante para o experimento B, mesmo quando ambos os experimentos estão ativos na
mesma execução.

**R-CONFLICT-REPO-002**: Quando um conflito de escrita concorrente é detectado no momento do push (ex: uma
rejeição non-fast-forward da API do GitHub), a etapa de push **MUST** tentar novamente com o
estado mesclado de ambas as execuções. A nova tentativa **MUST NOT** descartar o registro de atribuição de qualquer execução.

**R-CONFLICT-REPO-003**: Se duas execuções concorrentes selecionarem a mesma variante menos usada para o
mesmo experimento (uma corrida no momento da leitura), ambas as seleções são consideradas válidas. Os registros de execução
**MUST** refletir a variante independentemente selecionada de cada execução. Nenhum erro de conflito é levantado para
esta condição.

#### 12.1.2 Resolução de Conflitos para Modo de Armazenamento `cache`

**R-CONFLICT-CACHE-001**: Sob armazenamento `cache`, o cache do GitHub Actions é eventualmente
consistente através de execuções concorrentes. Quando duas execuções tentam salvar entradas de cache conflitantes
sob a mesma chave, o GitHub Actions armazenará uma entrada e descartará silenciosamente a outra.
Implementações **MUST** tratar isso como uma perda de dados aceitável (veja nota informativa em §7.4 sobre
despejo de cache) e **MUST NOT** tratar uma restauração de cache ausente como uma condição de erro.

**R-CONFLICT-CACHE-002**: Porque o armazenamento `cache` não fornece semântica atômica de read-modify-write,
implementações usando modo `cache` **MUST** documentar aos usuários que fluxos de trabalho de alta concorrência
podem experimentar desequilíbrio de variante elevado comparado ao modo `repo`.

#### 12.1.3 Resolução de Conflitos para Modo de Armazenamento Misto

**R-CONFLICT-MIX-001**: Todos os experimentos dentro de um único fluxo de trabalho **MUST** compartilhar o mesmo
modo de `storage`. Configurações de modo misto (alguns experimentos em `repo`, outros em `cache`)
**NÃO SÃO SUPORTADAS** e **MUST** produzir um erro de tempo de compilação.

**R-CONFLICT-MIX-002**: Esta restrição existe porque a chave `storage` é um único campo de nível superior no mapa
`experiments` que se aplica uniformemente a todos os experimentos nesse mapa. Autores de fluxo de trabalho que exigem modos de armazenamento diferentes para experimentos diferentes **MUST** dividi-los em arquivos de fluxo de trabalho separados.

---

## 13. Considerações de Segurança

### 13.1 Integridade de Arquivo de Estado

O estado do experimento é armazenado em um branch git (modo `repo`) ou cache do GitHub Actions
(modo `cache`). Ambos os backends são protegidos por controles de acesso de repositório. Contudo:

- Qualquer usuário com acesso de escrita ao repositório pode modificar `state.json` no branch de experimentos,
  possivelmente manipulando contadores de variante ou falsificando registros de execução.
- Implementações que exigem estado à prova de violação **SHOULD** (deveriam) usar commits assinados via
  mutação `createCommitOnBranch` do GraphQL do GitHub (R-STORE-REPO-004).

### 13.2 Injeção de Prompt via Valores de Variante

Strings de variante declaradas no frontmatter são strings estáticas definidas pelo autor do fluxo de trabalho.
Elas não derivam de entrada fornecida pelo usuário e, portanto, não introduzem risco de injeção de prompt no nível do frontmatter. Autores de fluxo de trabalho **MUST NOT** usar entrada de usuário em tempo de execução (ex: títulos de issue, corpos de PR) como valores de variante.

### 13.3 Vazamento de Atributo OTEL

Atribuições de experimento exportadas como atributos de recurso OTEL (§9.3) podem ser visíveis em
backends de tracing distribuído. Nomes de variante e nomes de experimento **SHOULD NOT** embutir
informação sensível.

### 13.4 Minimização de Permissão

- O modo de armazenamento `repo` requer `contents: write`. Fluxos de trabalho **SHOULD** limitar todas as outras
  permissões para `read` para minimizar o raio de explosão de um token comprometido.
- Fluxos de trabalho de relatório que postam comentários requerem `issues: write` ou `discussions: write`
  (§11.6). Estas permissões **SHOULD** ser concedidas apenas ao fluxo de trabalho de relatório específico,
  não ao próprio fluxo de trabalho de execução de experimento.

---

## 14. Testes de Conformidade

### 14.1 Requisitos de Suíte de Testes

A conformidade em cada nível é verificada pelas categorias de teste seguintes.

#### 14.1.1 Testes de Esquema (Nível 1)

| ID de Teste | Requisito | Descrição |
|---|---|---|
| T-SCHEMA-001 | R-SCHEMA-005 | Rejeitar bare-array com menos de 2 variantes |
| T-SCHEMA-002 | R-SCHEMA-003 | Ignorar e avisar sobre nome de experimento inválido |
| T-SCHEMA-003 | R-SCHEMA-007 | Rejeitar forma de objeto com `variants` contendo < 2 entradas |
| T-SCHEMA-004 | R-SCHEMA-011 | Rejeitar guardrail com padrão de limite inválido |
| T-SCHEMA-005 | R-SCHEMA-013 | Rejeitar objeto `notify` com chaves desconhecidas |
| T-SCHEMA-006 | R-SCHEMA-001 | Compilar fluxo de trabalho sem campo `experiments:` — saída inalterada |

#### 14.1.2 Testes de Seleção de Variante (Nível 1)

| ID de Teste | Requisito | Descrição |
|---|---|---|
| T-SELECT-001 | R-SELECT-001 | Round-robin: selecionar variante com contagem mais baixa |
| T-SELECT-002 | R-SELECT-002 | Round-robin: desempate aleatório na primeira execução |
| T-SELECT-003 | R-SELECT-003 | Round-robin: contador incrementado após seleção |
| T-SELECT-004 | R-SELECT-004 | Ponderado: probabilidade de seleção proporcional aos pesos |
| T-SELECT-005 | R-SELECT-006 | Ponderado: contador incrementado após seleção |
| T-SELECT-006 | R-SELECT-005 | Ponderado: todos os pesos zero retornam variante de controle |
| T-SELECT-007 | R-SELECT-007 | Ponderado: comprimento incompatível cai para round-robin |

#### 14.1.3 Testes de Integração de Expressão (Nível 1)

| ID de Teste | Requisito | Descrição |
|---|---|---|
| T-EXPR-001 | R-EXPR-001 | `${{ experiments.x }}` reescrito para referência de saída de step |
| T-EXPR-002 | R-EXPR-003 | Placeholder substituído antes da renderização Handlebars |
| T-EXPR-003 | R-EXPR-005 | `"no"` tratado como falsy em `isTruthy` |
| T-EXPR-004 | R-EXPR-004 | Placeholder bruto não passado para motor Handlebars |

#### 14.1.4 Testes de Persistência de Estado (Nível 2)

| ID de Teste | Requisito | Descrição |
|---|---|---|
| T-STORE-001 | R-STORE-REPO-002 | Estado vazio na primeira execução (branch 404) |
| T-STORE-002 | R-STORE-004 | Estrutura `state.json` válida escrita após execução |
| T-STORE-003 | R-STORE-007 | Registro de execução anexado com campos corretos |
| T-STORE-004 | R-STORE-005 | `runs` podado para ≤ 512 entradas |
| T-STORE-005 | R-STORE-006 | Estado legado (sem campo `runs`) inicializado para array vazia |
| T-STORE-006 | R-STORE-CACHE-004 | Nenhum `contents: write` necessário para modo de cache |

#### 14.1.5 Testes da CLI de Auditoria (Nível 2)

| ID de Teste | Requisito | Descrição |
|---|---|---|
| T-AUDIT-001 | R-AUDIT-003 | `--variant` sem `--experiment` retorna erro |
| T-AUDIT-002 | R-AUDIT-008 | Atribuição lida de `state.runs` quando disponível |
| T-AUDIT-003 | R-AUDIT-009 | Fallback para heurística de contagem máxima para estado legado |
| T-AUDIT-004 | R-AUDIT-005 | Campo Overview `Experiment` presente quando atribuições existem |
| T-AUDIT-005 | R-AUDIT-007 | Campo `Experiment` omitido quando nenhuma atribuição está presente |

#### 14.1.6 Testes de Relatório Estatístico (Nível 3)

| ID de Teste | Requisito | Descrição |
|---|---|---|
| T-STAT-001 | R-STAT-001 | Atribuições derivadas de `state.runs`, não inferência de delta de contagem |
| T-STAT-002 | R-STAT-005 | Correção de Bonferroni aplicada para K ≥ 3 variantes |
| T-STAT-003 | R-STAT-007 | PROMOTE retido até que todas as variantes atinjam `min_samples` |
| T-STAT-004 | R-STAT-009 | GUARDRAIL_FAILED força recomendação ABANDON |
| T-STAT-005 | R-STAT-011 | Fluxo de trabalho de relatório declara `issues: write` |

### 14.2 Checklist de Conformidade

| Requisito | ID de Teste | Nível | Status |
|---|---|---|---|
| R-SCHEMA-001 | T-SCHEMA-006 | 1 | Obrigatório |
| R-SCHEMA-005 | T-SCHEMA-001 | 1 | Obrigatório |
| R-SELECT-001 | T-SELECT-001 | 1 | Obrigatório |
| R-SELECT-002 | T-SELECT-002 | 1 | Obrigatório |
| R-SELECT-003 | T-SELECT-003 | 1 | Obrigatório |
| R-SELECT-006 | T-SELECT-005 | 1 | Obrigatório |
| R-EXPR-001 | T-EXPR-001 | 1 | Obrigatório |
| R-EXPR-005 | T-EXPR-003 | 1 | Obrigatório |
| R-STORE-002 | — | 2 | Obrigatório |
| R-STORE-REPO-002 | T-STORE-001 | 2 | Obrigatório |
| R-STORE-007 | T-STORE-003 | 2 | Obrigatório |
| R-AUDIT-003 | T-AUDIT-001 | 2 | Obrigatório |
| R-AUDIT-008 | T-AUDIT-002 | 2 | Obrigatório |
| R-STAT-001 | T-STAT-001 | 3 | Obrigatório |
| R-STAT-005 | T-STAT-002 | 3 | Recomendado |
| R-STAT-007 | T-STAT-003 | 3 | Obrigatório |
| R-STAT-011 | T-STAT-005 | 3 | Obrigatório |

---

## 15. Referências

### Referências Normativas

- **[RFC 2119]** Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels", RFC 2119, March 1997. <https://www.ietf.org/rfc/rfc2119.txt>
- **[ADR-29534]** mantenedores do gh-aw, "Frontmatter A/B Experiments with Balanced Variant Selection", 2026-05-01. `docs/adr/29534-frontmatter-ab-experiments-variant-selection.md`
- **[ADR-29618]** mantenedores do gh-aw, "Rich Experiment Metadata Schema Extension with Weighted Selection and Date Gating", 2026-05-01. `docs/adr/29618-rich-experiment-metadata-schema-extension.md` *(seções normativas substituídas por §5.2 deste documento)*
- **[ADR-29628]** mantenedores do gh-aw, "Add `--experiment` and `--variant` Filter Flags to `gh aw audit`", 2026-05-01. `docs/adr/29628-experiment-variant-filter-flags-for-audit.md`
- **[ADR-29985]** mantenedores do gh-aw, "Experiment Per-Run State, OTEL Integration, and Schema Extensions", 2026-05-03. `docs/adr/29985-experiment-per-run-state-otel-integration-and-schema-extensions.md`
- **[ADR-29996]** mantenedores do gh-aw, "Experiment State Storage — Git Branch as Default, Cache as Fallback", 2026-05-03. `docs/adr/29996-experiment-state-git-branch-storage.md`

### Referências Informativas

- **[SUTVA]** Rubin, D. B., "Estimating Causal Effects of Treatments in Randomized and Nonrandomized Studies", *Journal of Educational Psychology*, 66(5):688–701, 1974. (Stable Unit Treatment Value Assumption)
- **[BONFERRONI]** Dunn, O. J., "Multiple Comparisons Among Means", *Journal of the American Statistical Association*, 56(293):52–64, 1961.
- **[WELCH-TTEST]** Welch, B. L., "The Generalization of Student's Problem When Several Different Population Variances are Involved", *Biometrika*, 34(1/2):28–35, 1947.
- **[GitHub Actions Cache]** Docs do GitHub, "Caching dependencies to speed up workflows". <https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/caching-dependencies-to-speed-up-workflows>

---

## Appendices

### Apêndice A: Exemplo completo de forma de objeto

```yaml
---
on:
  schedule: daily on weekdays
engine: copilot
permissions:
  contents: read
  pull-requests: read

experiments:
  storage: repo
  prompt_style:
    variants: [concise, detailed, step_by_step]
    description: "Teste se o nível de verbosidade afeta a qualidade da saída"
    hypothesis: "H0: nenhuma mudança em effective_tokens. H1: conciso reduz em >=15%"
    metric: effective_tokens
    secondary_metrics: [duration_ms, discussion_word_count]
    guardrail_metrics:
      - name: success_rate
        threshold: ">=0.95"
      - name: empty_output_rate
        threshold: "==0"
    weight: [40, 40, 20]
    min_samples: 30
    start_date: "2026-05-01"
    end_date: "2026-08-01"
    issue: 1234
    analysis_type: t_test
    tags: [cost, prompting, verbosity]
    notify:
      issue: 1234
---

Resuma os pull requests mesclados hoje.

{{#if experiments.prompt_style == "concise" }}
Escreva no máximo 5 bullet points.
{{#else if experiments.prompt_style == "detailed" }}
Escreva um relatório estruturado com seções para novas funcionalidades, correções de bug, refatorações e docs.
{{#else}}
Escreva um walkthrough passo a passo numerado de cada mudança com justificativa.
{{#endif}}
```

### Apêndice A2: Seleção de Variante Ponderada — Exemplo Trabalhado

Este apêndice percorre a matemática de probabilidade para um experimento `weighted` de três variantes para
ilustrar como a array `weight` mapeia para a probabilidade de seleção, como contadores são atualizados e
como o balanço é mantido ao longo de muitas execuções.

#### A2.1 Configuração do Cenário

Um experimento nomeado `response_tone` tem três variantes com pesos não uniformes:

```yaml
experiments:
  storage: repo
  response_tone:
    variants: [formal, casual, neutral]
    weight: [20, 50, 30]
```

Os valores de peso são **proporções relativas**, não porcentagens absolutas. A implementação
normaliza-os para calcular probabilidades:

```
total_weight = 20 + 50 + 30 = 100

P(formal)  = 20 / 100 = 0.20  (20%)
P(casual)  = 50 / 100 = 0.50  (50%)
P(neutral) = 30 / 100 = 0.30  (30%)
```

Para uma sequência de experimento de 10 execuções, a distribuição de variante **esperada** é:

| Variante | Peso | Execuções esperadas (de 10) |
|---------|--------|-----------------------|
| formal  | 20     | 2                     |
| casual  | 50     | 5                     |
| neutral | 30     | 3                     |

#### A2.2 Algoritmo de Seleção (Aleatório Ponderado)

O algoritmo `weighted` sorteia um número aleatório uniforme `r ∈ [0, 1)` e mapeia-o
para uma variante via peso cumulativo:

```
Intervalos cumulativos:
  [0.00, 0.20)  →  formal
  [0.20, 0.70)  →  casual
  [0.70, 1.00)  →  neutral
```

Exemplos de sorteios:

| r      | Variante selecionada |
|--------|-----------------|
| 0.11   | formal           |
| 0.45   | casual           |
| 0.72   | neutral          |
| 0.19   | formal           |
| 0.68   | casual           |

#### A2.3 Atualizações de Contador

Após cada execução, o contador para a variante selecionada é incrementado em `state.json`.
Após 10 execuções com a distribuição acima, um objeto `counts` típico é:

```json
{
  "counts": {
    "response_tone": {
      "formal":  2,
      "casual":  5,
      "neutral": 3
    }
  }
}
```

Conforme R-SELECT-006, o algoritmo `weighted` **MUST** (deve) incrementar contadores de invocação após cada
seleção. Isso permite que a CLI de auditoria e fluxos de trabalho de relatório verifiquem se as
frequências de variante observadas aproximam-se dos pesos declarados ao longo do tempo.

#### A2.4 Verificação de Balanço de Longo Prazo

Ao longo de N execuções, a frequência observada para a variante v deve convergir para `weight[v] / total_weight`
pela Lei dos Grandes Números. Fluxos de trabalho de relatório SHOULD (deveriam) sinalizar experimentos onde a frequência observada de qualquer variante
desvia-se do seu peso alvo em mais de ±10 pontos percentuais ao longo de pelo menos 30 execuções, já que isso pode indicar uma array `weight` mal configurada ou um bug na
implementação de seleção.

Para o exemplo acima, após 100 execuções:

| Variante | Execuções esperadas | Faixa aceitável (±10 pp) |
|---------|--------------|--------------------------|
| formal  | 20           | 10 – 30                  |
| casual  | 50           | 40 – 60                  |
| neutral | 30           | 20 – 40                  |

#### A2.5 Contraste com Round-Robin Balanceado

O algoritmo `balanced` (menos usado) ignora pesos e seleciona a variante menos executada
 deterministicamente. Use `weighted` quando você intencionalmente quiser alocação de tráfego desigual
(ex: expor menos usuários a uma variante experimental enquanto ainda coleta
dados comparativos). Use `balanced` quando você quiser alocação igual e eficiência estatística máxima
por contagem total de execução.

### Apêndice B: Esquema de `state.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["counts"],
  "properties": {
    "counts": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "additionalProperties": { "type": "integer", "minimum": 0 }
      }
    },
    "runs": {
      "type": "array",
      "maxItems": 512,
      "items": {
        "type": "object",
        "required": ["run_id", "timestamp", "assignments"],
        "properties": {
          "run_id": { "type": "string" },
          "timestamp": { "type": "string", "format": "date-time" },
          "assignments": {
            "type": "object",
            "additionalProperties": { "type": "string" }
          }
        }
      }
    }
  }
}
```

### Apêndice C: Referência de Tamanho de Amostra

Para um teste de duas proporções com 80% de poder estatístico e α = 0.05 (bicaudal), as
execuções mínimas aproximadas por variante são:

| Efeito Mínimo Detectável (pp) | Execuções por variante |
|---|---|
| 5 | ~620 |
| 10 | ~160 |
| 15 | ~70 |
| 20 | ~40 |
| 30 | ~20 |

> **Nota para experimentos ponderados**: Quando `weight` não é uniforme, aplique estes valores
> ao **menor grupo**. Para uma divisão 70/30 visando detectar um efeito de 10 pp, você precisa
> de ~160 execuções no braço de 30% (≈ 533 execuções totais).

### Apêndice D: Limitações Conhecidas

1. **Condição de corrida no momento da leitura**: Execuções concorrentes com armazenamento `repo` podem ler estado obsoleto e
   selecionar a mesma variante. Veja R-STORE-REPO-005 e a nota informativa em §7.3.

2. **Efeitos de interação**: Executar múltiplos experimentos simultaneamente pode produzir resultados
   inatributáveis. Veja §12 e R-MULTI-002.

3. **Experimentos de troca de motor**: Alterar a chave `engine:` requer arquivos de fluxo de trabalho separados;
   veja R-MULTI-004.

4. **`analysis_type` apenas consultivo**: Fluxos de trabalho de relatório que não implementam todos os quatro
   testes estatísticos cairão para padrões. O campo documenta intenção; ele não
   impõe um caminho de computação específico.

5. **Crescimento do branch de estado**: O branch git de experimentos cresce monotonicamente. Operadores
   **MAY** (podem) podar commits antigos do branch de experimentos sem afetar o estado atual.

### Acompanhamentos de Sincronização (Revisão Especializada de Maio de 2026)

Este item de apêndice lista acompanhamentos corretivos referenciados no abstract.

- **FR-001 (implementado via R-SELECT-006)**: Seleção ponderada incrementa contadores de invocação após cada seleção.
- **FR-002 (implementado via R-STAT-001/R-STAT-002)**: Relatórios usam registros de atribuição `state.runs` em vez de inferência de delta de contagem.
- **FR-003 (implementado via R-STAT-011/R-STAT-012)**: Fluxos de trabalho de relatório que escrevem issues/discussões declaram permissões de escrita explícitas.
- **FR-004 (implementado via R-MULTI-005)**: Efeitos de interação de experimentos concorrentes são detectados e limitados explicitamente antes de decisões de promoção.
- **FR-005 (implementado via atualização do fluxo de trabalho daily-experiment-report)**: Orientação de relatório agora inclui um helper de interação fatorial para saída de significância de célula de nível K₁×K₂ e exposição de risco de célula esparsa.
- **FR-006 (implementado via diagnósticos de compilador)**: O compilador agora emite um aviso quando mais de um experimento está ativo e tráfego ponderado está configurado, indicando possíveis células de interação esparsas.

---

## Log de Mudanças

### Versão 1.1.0 (Rascunho) — 2026-05-12

- **Adicionado**: Orientação de helper de relatório diário para saída de significância de célula de interação fatorial K₁×K₂.
- **Adicionado**: Requisito de aviso do compilador para risco de célula de interação esparsa quando múltiplos experimentos e tráfego ponderado estão configurados.
- **Atualizado**: Apêndice de Acompanhamentos de Sincronização para substituir TODOs da v1.1.0 por itens corretivos implementados.

### Versão 1.0.1 (Rascunho) — 2026-05-07

- **Adicionado**: R-MULTI-005 exigindo detecção/limitação de risco de interação para experimentos simultâneos.
- **Adicionado**: Apêndice de Acompanhamentos de Sincronização com itens corretivos de revisão especializada de maio de 2026 e TODOs de propriedade.

### Versão 1.0.0 (Rascunho) — 2026-05-03

- **Publicação inicial** consolidando ADR-29534, ADR-29618, ADR-29628, ADR-29985 e ADR-29996.
- **Correção**: R-SELECT-006 substitui ADR-29618 Regra 9 — seleção ponderada MUST incrementar contadores de invocação (foi declarado incorretamente como MUST NOT; a implementação de referência já implementa o comportamento correto).
- **Adicionado**: R-STAT-001/R-STAT-002 — ferramentas de relatório MUST usar `state.runs` para busca de atribuição por execução, não o método frágil de inferência de delta-contagem.
- **Adicionado**: R-STAT-005/R-STAT-006 — correção de Bonferroni SHOULD ser aplicada para K ≥ 3 variantes para controlar a taxa de erro familiar.
- **Adicionado**: R-STAT-007 — `min_samples` aplica-se ao menor grupo esperado quando pesos não são uniformes.
- **Adicionado**: R-STAT-011/R-STAT-012 — fluxos de trabalho de relatório MUST declarar `issues: write` / `discussions: write` ao postar comentários.
- **Adicionado**: R-MULTI-002/R-MULTI-003 — aviso para > 3 experimentos simultâneos; efeitos de interação devem ser notados em relatórios.
- **Adicionado**: §13 Considerações de Segurança — integridade de estado, injeção de prompt, vazamento OTEL, minimização de permissão.
- **Adicionado**: Apêndice C (referência de tamanho de amostra) e Apêndice D (limitações conhecidas).
- **Nota informativa**: `storage: cache` padrão mudou para `storage: repo` em ADR-29996; quaisquer documentações ou modelos de issue que ainda se refiram a atribuição "baseada em cache" devem ser atualizados.

---

*Copyright © 2026 GitHub, Inc. Todos os direitos reservados. Esta especificação é mantida pela
equipe do projeto gh-aw.*
