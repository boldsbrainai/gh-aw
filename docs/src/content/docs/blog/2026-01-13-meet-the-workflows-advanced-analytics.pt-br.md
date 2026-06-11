---
title: "Conheça os Workflows: Analytics Avançado e ML"
description: "Um tour curado de fluxos de trabalho que usam ML para extrair insights do comportamento do agente"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-13T15:00:00
sidebar:
  label: "Analytics Avançado e ML"
prev:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-organization/
  label: "Workflows de Organização e Cross-Repo"
next:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-campaigns/
  label: "Workflows de Coordenação de Projetos"
---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

*Ooh!* Hora de mergulhar no *país das maravilhas dos dados* na [Fábrica de Agentes do Peli](/gh-aw/blog/2026-01-12-welcome-to-pelis-agent-factory/)! Onde os números dançam e os padrões cantam!

Em nossa [postagem anterior](/gh-aw/blog/2026-01-13-meet-the-workflows-organization/), exploramos fluxos de trabalho de organização e cross-repo que operam em escala empresarial - analisando dezenas de repositórios juntos para encontrar padrões e discrepâncias que a análise de repo único perderia. Aprendemos que a perspectiva importa: o que parece normal isoladamente pode sinalizar desvio em escala.

Além de rastrear métricas básicas (tempo de execução, custo, taxa de sucesso), queríamos insights mais profundos sobre *como* nossos agentes realmente se comportam e *como* os desenvolvedores interagem com eles. Que padrões emergem de milhares de prompts de agentes? O que torna algumas conversas de PR mais eficazes do que outras? Como os padrões de uso revelam oportunidades de melhoria? É aqui que trouxemos as armas pesadas: aprendizado de máquina, processamento de linguagem natural, análise de sentimento e algoritmos de agrupamento. Fluxos de trabalho de analytics avançado não apenas contam coisas - eles as entendem, encontrando padrões e insights que a observação direta nunca revelaria.

## Workflows de Analytics Avançado e ML

Estes agentes usam técnicas de análise sofisticadas para extrair insights:

- **[Copilot Session Insights](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/copilot-session-insights.md?plain=1)** - Analisa padrões de uso e métricas do agente de codificação Copilot - **32 discussões de análise**
- **[Copilot PR NLP Analysis](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/copilot-pr-nlp-analysis.md?plain=1)** - Processamento de linguagem natural em conversas de PR
- **[Prompt Clustering Analysis](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/prompt-clustering-analysis.md?plain=1)** - Agrupa e categoriza prompts de agentes usando ML - **27 discussões de análise**
- **[Copilot Agent Analysis](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/copilot-agent-analysis.md?plain=1)** - Análise profunda de padrões de comportamento do agente - **48 discussões de análise diária**

A Análise de Agrupamento de Prompts (Prompt Clustering Analysis) criou **27 discussões de análise** usando ML para categorizar milhares de prompts de agentes - por exemplo, [#6918](https://github.com/github/gh-aw/discussions/6918) agrupando prompts de agentes para identificar padrões e oportunidades de otimização. Revelou padrões que nunca notamos ("oh, 40% dos nossos prompts são sobre tratamento de erros").

A Análise de PR NLP do Copilot (Copilot PR NLP Analysis) aplica processamento de linguagem natural às conversas de PR, realizando análise de sentimento e identificando padrões linguísticos nas interações dos agentes. Descobriu-se que PRs com perguntas no título recebem revisões mais rápidas.

O Copilot Session Insights criou **32 discussões de análise** examinando padrões de uso e métricas do agente de codificação Copilot em todo o ecossistema de fluxo de trabalho. Ele identifica padrões comuns e modos de falha.

A Análise do Agente de Codificação Copilot criou **48 discussões de análise diária** fornecendo uma análise profunda dos padrões de comportamento do agente - por exemplo, [#6913](https://github.com/github/gh-aw/discussions/6913) com a análise diária do agente de codificação Copilot.

O que aprendemos: **meta-análise é poderosa** - usar IA para analisar sistemas de IA revela insights que a observação direta perde. Esses fluxos de trabalho nos ajudaram a entender não apenas o que nossos agentes fazem, mas *como* eles se comportam e como os usuários interagem com eles.

## Usando estes Workflows

Você pode adicionar esses fluxos de trabalho ao seu próprio repositório e remixá-los da seguinte forma:

**Copilot Session Insights:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/copilot-agent-analysis.md
```

**Copilot PR NLP Analysis:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/copilot-pr-nlp-analysis
```

**Prompt Clustering Analysis:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/prompt-clustering-analysis.md
```

**Copilot Agent Analysis:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/copilot-agent-analysis.md
```

Em seguida, edite e remixe as especificações do fluxo de trabalho para atender às suas necessidades, regenere o arquivo de bloqueio usando `gh aw compile` e envie para o seu repositório. Veja nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/) para obter mais instruções de instalação e configuração.

Você também pode [criar seus próprios fluxos de trabalho](/gh-aw/setup/creating-workflows/).

## Saiba mais

- **[GitHub Agentic Workflows](https://github.github.com/gh-aw/)** - A tecnologia por trás dos fluxos de trabalho
- **[Início Rápido](https://github.github.com/gh-aw/setup/quick-start/)** - Como escrever e compilar fluxos de trabalho

## Próximo: Workflows de Coordenação de Projetos

Chegamos à parada final: coordenar múltiplos agentes em direção a objetivos compartilhados e complexos em cronogramas estendidos.

Continue lendo: [Workflows de Coordenação de Projetos →](/gh-aw/blog/2026-01-13-meet-the-workflows-campaigns/)

---

*Esta é a parte 18 de uma série de 19 partes explorando os fluxos de trabalho na Fábrica de Agentes do Peli.*
