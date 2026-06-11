---
title: "Conheça os Workflows: Métricas e Analytics"
description: "Um tour curado de fluxos de trabalho de métricas e analytics que transformam dados em insights"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-13T06:00:00
sidebar:
  label: "Métricas e Analytics"
prev:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-quality-hygiene/
  label: "Workflows de Investigação de Falhas"
next:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-operations-release/
  label: "Workflows de Operações e Release"
---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

Excelente jornada! Agora é hora de mergulhar no *observatório* - o centro nervoso da [Fábrica de Agentes do Peli](/gh-aw/blog/2026-01-12-welcome-to-pelis-agent-factory/)!

Em nossa [postagem anterior](/gh-aw/blog/2026-01-13-meet-the-workflows-quality-hygiene/), exploramos fluxos de trabalho de qualidade e higiene - os zeladores vigilantes que investigam falhas de CI, detectam deriva de esquema e capturam mudanças de quebra antes dos usuários. Esses fluxos de trabalho mantêm a saúde da base de código identificando problemas antes que eles escalem.

Ao executar dezenas de agentes de IA, como saber se eles estão realmente funcionando bem? Como identificar problemas de desempenho, problemas de custo ou degradação de qualidade? É aí que entram os fluxos de trabalho de métricas e analytics - eles são os agentes que monitoram outros agentes. O objetivo é transformar dados de atividade brutos em insights acionáveis.

## Workflows de Métricas e Analytics

Vamos dar uma olhada nestes três fluxos de trabalho:

- **[Coletor de Métricas (Metrics Collector)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/metrics-collector.md?plain=1)** - Rastreia o desempenho diário em todo o ecossistema de agentes
- **[Analista de Portfólio (Portfolio Analyst)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/portfolio-analyst.md?plain=1)** - Identifica oportunidades de redução de custos
- **[Auditor de Workflows (Audit Workflows)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/audit-workflows.md?plain=1)** - Um meta-agente que audita todas as outras execuções de agentes

O Coletor de Métricas criou **41 discussões diárias de métricas** rastreando o desempenho em todo o ecossistema de agentes - por exemplo, [#6986](https://github.com/github/gh-aw/discussions/6986) com o relatório diário de métricas de código. Tornou-se nosso sistema nervoso central, reunindo dados de desempenho que alimentam orquestradores de nível superior.

O Analista de Portfólio criou **7 discussões de análise de portfólio** identificando oportunidades de redução de custos e padrões de otimização de tokens - por exemplo, [#6499](https://github.com/github/gh-aw/discussions/6499) com uma análise de portfólio semanal. O fluxo de trabalho identificou fluxos de trabalho que estavam nos custando dinheiro desnecessariamente (acontece que alguns agentes eram muito faladores com suas chamadas de LLM).

Auditor de Workflows é nosso agente que mais cria discussões, com **93 discussões de relatório de auditoria** e **9 issues**, agindo como um meta-agente que analisa logs, custos, erros e padrões de sucesso em todas as outras execuções de fluxos de trabalho. Quatro de suas issues levaram a PRs por agentes downstream.

A observabilidade não é opcional quando você está executando dezenas de agentes de IA - é a diferença entre uma máquina bem lubrificada e uma caixa preta cara.

## Usando estes Workflows

Você pode adicionar esses fluxos de trabalho ao seu próprio repositório e remixá-los. Comece com nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/), depois execute um dos seguintes:

**Coletor de Métricas:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/metrics-collector.md
```

**Analista de Portfólio:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/portfolio-analyst.md
```

**Auditor de Workflows:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/audit-workflows.md
```

Em seguida, edite e remixe as especificações do fluxo de trabalho para atender às suas necessidades, regenere o arquivo de bloqueio usando `gh aw compile` e envie para o seu repositório. Veja nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/) para obter mais instruções de instalação e configuração.

Você também pode [criar seus próprios fluxos de trabalho](/gh-aw/setup/creating-workflows/).

## Saiba mais

- **[GitHub Agentic Workflows](https://github.github.com/gh-aw/)** - A tecnologia por trás dos fluxos de trabalho
- **[Início Rápido](https://github.github.com/gh-aw/setup/quick-start/)** - Como escrever e compilar fluxos de trabalho

## Próximo: Workflows de Operações e Release

Agora que podemos medir e otimizar nosso ecossistema de agentes, vamos falar sobre o momento da verdade: enviar software para os usuários.

Continue lendo: [Workflows de Operações e Release →](/gh-aw/blog/2026-01-13-meet-the-workflows-operations-release/)

---

*Esta é a parte 9 de uma série de 19 partes explorando os fluxos de trabalho na Fábrica de Agentes do Peli.*
