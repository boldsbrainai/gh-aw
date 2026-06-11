---
title: "Conheça os Workflows: Melhoradores de Múltiplas Fases"
description: "Um tour curado de fluxos de trabalho de múltiplas fases que abordam projetos de longa duração"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-13T13:00:00
sidebar:
  label: "Melhoradores de Múltiplas Fases"
prev:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-tool-infrastructure/
  label: "Workflows de Ferramentas e Infraestrutura"
next:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-organization/
  label: "Workflows de Organização e Cross-Repo"
---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

Vamos continuar nossa jornada pela [Fábrica de Agentes do Peli](/gh-aw/blog/2026-01-12-welcome-to-pelis-agent-factory/)!

Em nossa [postagem anterior](/gh-aw/blog/2026-01-13-meet-the-workflows-tool-infrastructure/), exploramos fluxos de trabalho de infraestrutura - a camada de meta-monitoramento que valida servidores MCP, verifica configurações de ferramentas e garante que a plataforma permaneça saudável. Esses fluxos de trabalho observam os observadores, proporcionando visibilidade para as tubulações invisíveis.

A maioria dos fluxos de trabalho que vimos até agora roda uma vez e completa: analise este PR, trie aquela issue, teste este deploy. Eles são efêmeros - executam, produzem resultados e desaparecem. Mas e quanto aos projetos que são grandes demais para serem resolvidos em uma única execução? E quanto às iniciativas que exigem pesquisa, configuração e implementação incremental? O CI/CD tradicional é construído para execução sem estado, mas descobrimos algo poderoso: fluxos de trabalho que mantêm estado ao longo dos dias, trabalhando um pouco a cada dia como um membro da equipe persistente que nunca tira folga. Bem-vindo ao nosso experimento mais ambicioso - melhoradores de múltiplas fases que provam que os agentes de IA podem lidar com projetos complexos e de longa duração.

## Workflows de Melhoria de Múltiplas Fases

Estes são alguns dos nossos agentes mais ambiciosos - eles abordam grandes projetos ao longo de múltiplos dias:

- **[Queimador Diário de Backlog (Daily Backlog Burner)](https://github.com/githubnext/agentics/blob/main/workflows/daily-backlog-burner.md?plain=1)** - Trabalha sistematicamente em issues e PRs, um dia de cada vez
- **[Aprimorador Diário de Desempenho (Daily Perf Improver)](https://github.com/githubnext/agentics/blob/main/workflows/daily-perf-improver.md?plain=1)** - Otimização de desempenho em três fases (pesquisa, configuração, implementação)
- **[QA Diário (Daily QA)](https://github.com/githubnext/agentics/blob/main/workflows/daily-qa.md?plain=1)** - Garantia de qualidade contínua que nunca dorme
- **[Revisão Diária de Acessibilidade (Daily Accessibility Review)](https://github.com/githubnext/agentics/blob/main/workflows/daily-accessibility-review.md?plain=1)** - Verificação de conformidade WCAG com Playwright
- **[Correção de PR (PR Fix)](https://github.com/githubnext/agentics/blob/main/workflows/pr-fix.md?plain=1)** - Comando de barra sob demanda para corrigir verificações de CI com falha (super útil!)

É aqui que experimentamos com persistência de agentes e fluxos de trabalho de vários dias. As execuções de CI tradicionais são efêmeras, mas esses fluxos de trabalho mantêm o estado ao longo dos dias usando repo-memory. O Aprimorador Diário de Desempenho é executado em três fases - pesquisa (encontrar gargalos), configuração (criar infraestrutura de perfil), implementação (otimizar). É como ter um engenheiro de desempenho que trabalha um pouco a cada dia. O Queimador Diário de Backlog aborda sistematicamente nosso backlog de issues - uma issue por dia, trabalhando metodicamente na dívida técnica. Aprendemos que **o progresso incremental supera os sprints heroicos** - esses agentes nunca se cansam, nunca se distraem e nunca precisam de pausas para o café. O fluxo de trabalho de Correção de PR é nosso socorrista de emergência - quando o CI falha, invoque `/pr-fix` e ele investiga e tenta reparos.

Esses fluxos de trabalho provam que os agentes de IA podem lidar com projetos complexos e de longa duração quando recebem a arquitetura adequada.

## Usando estes Workflows

Você pode adicionar esses fluxos de trabalho ao seu próprio repositório e remixá-los. Comece com nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/), depois execute um dos seguintes:

**Queimador Diário de Backlog:**

```bash
gh aw add-wizard githubnext/agentics/workflows/daily-backlog-burner.md
```

**Aprimorador Diário de Desempenho:**

```bash
gh aw add-wizard githubnext/agentics/workflows/daily-perf-improver.md
```

**QA Diário:**

```bash
gh aw add-wizard githubnext/agentics/workflows/daily-qa.md
```

**Revisão Diária de Acessibilidade:**

```bash
gh aw add-wizard githubnext/agentics/workflows/daily-accessibility-review.md
```

**Correção de PR:**

```bash
gh aw add-wizard githubnext/agentics/workflows/pr-fix.md
```

Em seguida, edite e remixe as especificações do fluxo de trabalho para atender às suas necessidades, regenere o arquivo de bloqueio usando `gh aw compile` e envie para o seu repositório. Veja nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/) para obter mais instruções de instalação e configuração.

Você também pode [criar seus próprios fluxos de trabalho](/gh-aw/setup/creating-workflows/).

## Saiba mais

- **[GitHub Agentic Workflows](https://github.github.com/gh-aw/)** - A tecnologia por trás dos fluxos de trabalho
- **[Início Rápido](https://github.github.com/gh-aw/setup/quick-start/)** - Como escrever e compilar fluxos de trabalho

## Próximo: Workflows de Organização e Cross-Repo

Fluxos de trabalho de repositório único são poderosos, mas o que acontece quando você escala para uma organização inteira com dezenas de repositórios?

Continue lendo: [Workflows de Organização e Cross-Repo →](/gh-aw/blog/2026-01-13-meet-the-workflows-organization/)

---

*Esta é a parte 16 de uma série de 19 partes explorando os fluxos de trabalho na Fábrica de Agentes do Peli.*
