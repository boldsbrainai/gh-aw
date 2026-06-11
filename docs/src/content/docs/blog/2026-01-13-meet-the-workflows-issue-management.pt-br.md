---
title: "Conheça os Workflows: Gerenciamento de Issues e PR"
description: "Um tour curado de fluxos de trabalho que aprimoram a colaboração no GitHub"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-13T04:00:00
sidebar:
  label: "Gerenciamento de Issues e PR"
prev:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-documentation/
  label: "Conheça os Workflows: Documentação Contínua"
next:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-quality-hygiene/
  label: "Workflows de Investigação de Falhas"
---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

*Ah!* Vamos discutir a arte de gerenciar issues e pull requests na [Fábrica de Agentes do Peli](/gh-aw/blog/2026-01-12-welcome-to-pelis-agent-factory/)! Um tópico muito delicioso, de fato!

Em nossa [postagem anterior](/gh-aw/blog/2026-01-13-meet-the-workflows-documentation/), exploramos fluxos de trabalho de documentação e conteúdo - agentes que mantêm glossários, docs técnicos, decks de slides e conteúdo de blog. Aprendemos como adotamos uma abordagem heterogênea para agentes de documentação - alguns fluxos de trabalho geram conteúdo, outros o mantêm e outros validam.

Agora vamos falar sobre os rituais diários do desenvolvimento de software: gerenciar issues e pull requests. O GitHub fornece primitivas excelentes para colaboração, mas há cerimônia envolvida - vincular issues relacionadas, mesclar a main nos branches de PR, atribuir trabalho, fechar sub-issues concluídas, otimizar modelos. Esses são pequenos cortes de papel individualmente, mas podem somar um atrito significativo.

## Workflows de Gerenciamento de Issues e PR

Estes agentes aprimoram os fluxos de trabalho de issue e pull request:

- **[Arborista de Issues (Issue Arborist)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/issue-arborist.md?plain=1)** - Vincula issues relacionadas como sub-issues - **77 relatórios de discussão** e **18 issues pai** criadas
- **[Monstro de Issues (Issue Monster)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/issue-monster.md?plain=1)** - Atribui issues ao [agente de codificação do GitHub Copilot](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent) assíncrono, uma de cada vez - **dispatcher de tarefas** para todo o sistema
- **[Mergefest](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/mergefest.md?plain=1)** - Mescla automaticamente a branch main nas branches de PR - **fluxo de trabalho orquestrador**
- **[Fechador de Sub-issues (Sub Issue Closer)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/sub-issue-closer.md?plain=1)** - Fecha sub-issues concluídas automaticamente - **fluxo de trabalho orquestrador**

O Arborista de Issues é um **fluxo de trabalho organizacional** que criou **77 relatórios de discussão** (intitulados "[Issue Arborist] Issue Arborist Report") e **18 issues pai** para agrupar sub-issues relacionadas. Ele mantém o rastreador de issues organizado vinculando automaticamente issues relacionadas, construindo uma árvore de dependência que nunca manteríamos manualmente. Por exemplo, [#12037](https://github.com/github/gh-aw/issues/12037) agrupou atualizações de documentação do mecanismo.

O Monstro de Issues é o **dispatcher de tarefas** - ele atribui issues ao [agente de codificação](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent) assíncrono do GitHub uma de cada vez. Ele não cria PRs, mas permite o trabalho de todos os outros agentes alimentando-os com tarefas. Isso evita o caos de trabalho paralelo na mesma base de código.

Mergefest é um **fluxo de trabalho orquestrador** que mescla automaticamente a main nas branches de PR, mantendo PRs de longa duração atualizados sem intervenção manual. Ele elimina a dança do "por favor, mescle a main".

O Fechador de Sub-issues fecha automaticamente sub-issues concluídas quando sua issue pai é resolvida, mantendo o rastreador de issues limpo.

Os fluxos de trabalho de gerenciamento de issues e PR não substituem os recursos do GitHub; eles os aprimoram, removendo a cerimônia e tornando a colaboração mais tranquila.

## Usando estes Workflows

Você pode adicionar esses fluxos de trabalho ao seu próprio repositório e remixá-los. Comece com nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/), depois execute um dos seguintes:

**Arborista de Issues:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/issue-arborist.md
```

**Monstro de Issues:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/issue-monster.md
```

**Mergefest:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/mergefest.md
```

**Fechador de Sub-issues:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/sub-issue-closer.md
```

Em seguida, edite e remixe as especificações do fluxo de trabalho para atender às suas necessidades, regenere o arquivo de bloqueio usando `gh aw compile` e envie para o seu repositório. Veja nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/) para obter mais instruções de instalação e configuração.

Você também pode [criar seus próprios fluxos de trabalho](/gh-aw/setup/creating-workflows/).

## Saiba mais

- **[GitHub Agentic Workflows](https://github.github.com/gh-aw/)** - A tecnologia por trás dos fluxos de trabalho
- **[Início Rápido](https://github.github.com/gh-aw/setup/quick-start/)** - Como escrever e compilar fluxos de trabalho

## Próximo: Workflows de Investigação de Falhas

A seguir, veremos agentes que mantêm a saúde da base de código - detectando problemas antes que eles escalem.

Continue lendo: [Workflows de Investigação de Falhas →](/gh-aw/blog/2026-01-13-meet-the-workflows-quality-hygiene/)

---

*Esta é a parte 7 de uma série de 19 partes explorando os fluxos de trabalho na Fábrica de Agentes do Peli.*
