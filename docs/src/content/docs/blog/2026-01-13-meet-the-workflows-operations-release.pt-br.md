---
title: "Conheça os Workflows: Operações e Release"
description: "Um tour curado de fluxos de trabalho de operações e release que enviam software"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-13T07:00:00
sidebar:
  label: "Operações e Release"
prev:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-metrics-analytics/
  label: "Workflows de Métricas e Analytics"
next:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-security-compliance/
  label: "Workflows relacionados à Segurança"
---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

Ah! Por aqui para nossa próxima câmara na [Fábrica de Agentes do Peli](/gh-aw/blog/2026-01-12-welcome-to-pelis-agent-factory/)! A câmara onde nossos agentes de IA aprimoram o momento mágico de *enviar software*.

Em nossa [postagem anterior](/gh-aw/blog/2026-01-13-meet-the-workflows-metrics-analytics/), exploramos fluxos de trabalho de métricas e analytics - os agentes que monitoram outros agentes, transformando dados brutos de atividade em insights acionáveis.

## Workflows de Operações e Release

Os agentes que nos ajudam a realmente enviar software:

- **[Changeset](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/changeset.md?plain=1)** - Gerencia bumps de versão e entradas de changelog para releases - **22 PRs mesclados de 28 propostos (taxa de mesclagem de 78%)**
- **[Atualizador Diário de Workflow (Daily Workflow Updater)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-workflow-updater.md?plain=1)** - Mantém GitHub Actions e dependências atualizados

Enviar software já é estressante o suficiente sem ter que se preocupar se você formatou suas notas de release corretamente.

O Gerador de Changeset contribuiu com **22 PRs mesclados de 28 propostos (taxa de mesclagem de 78%)**, automatizando bumps de versão e a geração de changelog para cada release. Ele analisa os commits desde o último release, determina o bump de versão apropriado (major, minor, patch) e atualiza o changelog de acordo.

O Atualizador Diário de Workflow mantém GitHub Actions e dependências atualizados, garantindo que os fluxos de trabalho não fiquem para trás em patches de segurança ou novos recursos.

## Usando estes Workflows

Você pode adicionar esse fluxo de trabalho ao seu próprio repositório e remixá-lo da seguinte forma:

**Changeset:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/changeset.md
```

Em seguida, edite e remixe a especificação do fluxo de trabalho para atender às suas necessidades, regenere o arquivo de bloqueio usando `gh aw compile` e envie para o seu repositório. Veja nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/) para obter mais instruções de instalação e configuração.

Você também pode [criar seus próprios fluxos de trabalho](/gh-aw/setup/creating-workflows/).

## Saiba mais

- **[GitHub Agentic Workflows](https://github.github.com/gh-aw/)** - A tecnologia por trás dos fluxos de trabalho
- **[Início Rápido](https://github.github.com/gh-aw/setup/quick-start/)** - Como escrever e compilar fluxos de trabalho

## Próximo: Workflows relacionados à Segurança

Após todo esse foco em envio, precisamos falar sobre os mecanismos de proteção: como garantimos que esses agentes poderosos operem com segurança?

Continue lendo: [Workflows relacionados à Segurança →](/gh-aw/blog/2026-01-13-meet-the-workflows-security-compliance/)

---

*Esta é a parte 10 de uma série de 19 partes explorando os fluxos de trabalho na Fábrica de Agentes do Peli.*
