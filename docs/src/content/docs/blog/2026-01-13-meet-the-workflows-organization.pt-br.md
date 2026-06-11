---
title: "Conheça os Workflows: Organização e Cross-Repo"
description: "Um tour curado de fluxos de trabalho que operam em escala organizacional"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-13T14:00:00
sidebar:
  label: "Organização e Cross-Repo"
prev:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-multi-phase/
  label: "Workflows de Melhoria de Múltiplas Fases"
next:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-advanced-analytics/
  label: "Workflows de Analytics Avançado e ML"
---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

Vamos reduzir o zoom na [Fábrica de Agentes do Peli](/gh-aw/blog/2026-01-12-welcome-to-pelis-agent-factory/)!

Em nossa [postagem anterior](/gh-aw/blog/2026-01-13-meet-the-workflows-multi-phase/), exploramos fluxos de trabalho de melhoria de múltiplas fases - nossos agentes mais ambiciosos que abordam grandes projetos ao longo de vários dias, mantendo o estado e fazendo progresso incremental. Esses fluxos de trabalho provaram que os agentes de IA podem lidar com iniciativas complexas e de longa duração quando recebem a arquitetura adequada.

Mas toda essa funcionalidade sofisticada concentrou-se em um único repositório. O que acontece quando você reduz o zoom para a escala da organização? Que insights emergem quando você analisa dezenas ou centenas de repositórios juntos? O que parece perfeitamente normal em um repo pode ser uma bandeira vermelha em toda a organização. Os fluxos de trabalho de organização e cross-repo operam em escala empresarial, exigindo gerenciamento cuidadoso de permissões, limitação de taxa (rate limiting) criteriosa e diferentes lentes analíticas. Vamos explorar fluxos de trabalho que veem a floresta, não apenas as árvores.

## Workflows de Organização e Cross-Repo

Estes agentes trabalham em escala organizacional, em múltiplos repositórios:

- **[Relatório de Saúde da Organização (Org Health Report)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/org-health-report.md?plain=1)** - Métricas de saúde de repositórios em toda a organização - **4 discussões de saúde organizacional** criadas
- **[Identificador de Repo Estagnado (Stale Repo Identifier)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/stale-repo-identifier.md?plain=1)** - Identifica repositórios inativos - **2 issues** sinalizando repositórios verdadeiramente estagnados
- **[Analisador de Imagem Ubuntu (Ubuntu Image Analyzer)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/ubuntu-image-analyzer.md?plain=1)** - Documenta ambientes de runner do GitHub Actions - **4 PRs mesclados de 8 propostos (taxa de mesclagem de 50%)**

Escalar agentes em toda uma organização muda o jogo. O Relatório de Saúde da Organização criou **4 discussões de saúde organizacional** analisando dezenas de repositórios em escala - por exemplo, [#6777](https://github.com/github/gh-aw/discussions/6777) com o relatório de saúde da organização de dezembro de 2025. Ele identifica padrões e discrepâncias ("estes três repos não têm testes, estes cinco não foram atualizados há meses").

O Identificador de Repo Estagnado criou **2 issues** sinalizando repositórios verdadeiramente estagnados para higiene organizacional - por exemplo, [#5384](https://github.com/github/gh-aw/issues/5384) identificando Skills-Based-Volunteering-Public como verdadeiramente estagnado. Ele ajuda a encontrar projetos abandonados que deveriam ser arquivados ou transferidos.

Aprendemos que **insights cross-repo são diferentes** - o que parece bem em um repositório pode ser uma discrepância em toda a organização. Esses fluxos de trabalho exigem gerenciamento cuidadoso de permissões (ler em repos precisa de tokens de nível de organização) e limitação de taxa criteriosa (você pode atingir os limites de API rapidamente ao analisar 50+ repos).

O Analisador de Imagem Ubuntu contribuiu com **4 PRs mesclados de 8 propostos (taxa de mesclagem de 50%)**, documentando ambientes de runner do GitHub Actions para manter a equipe informada sobre as ferramentas e versões disponíveis. É maravilhosamente meta - documenta o próprio ambiente que executa nossos agentes.

## Usando estes Workflows

Você pode adicionar esses fluxos de trabalho ao seu próprio repositório e remixá-los. Comece com nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/), depois execute um dos seguintes:

**Relatório de Saúde da Organização:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/org-health-report.md
```

**Identificador de Repo Estagnado:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/stale-repo-identifier.md
```

**Analisador de Imagem Ubuntu:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/ubuntu-image-analyzer.md
```

Em seguida, edite e remixe as especificações do fluxo de trabalho para atender às suas necessidades, regenere o arquivo de bloqueio usando `gh aw compile` e envie para o seu repositório. Veja nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/) para obter mais instruções de instalação e configuração.

Você também pode [criar seus próprios fluxos de trabalho](/gh-aw/setup/creating-workflows/).

## Saiba mais

- **[GitHub Agentic Workflows](https://github.github.com/gh-aw/)** - A tecnologia por trás dos fluxos de trabalho
- **[Início Rápido](https://github.github.com/gh-aw/setup/quick-start/)** - Como escrever e compilar fluxos de trabalho

## Próximo: Workflows de Analytics Avançado e ML

Insights cross-repo revelam padrões, mas queríamos ir ainda mais fundo - usando aprendizado de máquina para entender o comportamento do agente.

Continue lendo: [Workflows de Analytics Avançado e ML →](/gh-aw/blog/2026-01-13-meet-the-workflows-advanced-analytics/)

---

*Esta é a parte 17 de uma série de 19 partes explorando os fluxos de trabalho na Fábrica de Agentes do Peli.*
