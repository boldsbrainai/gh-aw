---
title: "Conheça os Workflows: Coordenação de Projetos"
description: "Um tour curado de fluxos de trabalho que coordenam projetos multi-agente"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-13T16:00:00
sidebar:
  label: "Campanhas e Projetos"
prev:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-advanced-analytics/
  label: "Workflows de Analytics Avançado e ML"
# next:
#   link: /gh-aw/blog/2026-01-21-twelve-lessons/
#   label: 12 Lições
---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

Meus caros amigos, chegamos ao *grand finale* - a sala mais espetacular de todas na [Fábrica de Agentes do Peli](/gh-aw/blog/2026-01-12-welcome-to-pelis-agent-factory/)!

Percorremos 18 categorias de fluxos de trabalho - desde bots de triagem a melhoradores de qualidade de código, de guardas de segurança a poetas criativos, culminando em [analytics avançados](/gh-aw/blog/2026-01-13-meet-the-workflows-advanced-analytics/) que usam aprendizado de máquina para entender padrões de comportamento dos agentes. Cada fluxo de trabalho lida com sua tarefa individual admiravelmente.

Mas aqui está o desafio final: como você coordena *múltiplos* agentes trabalhando em direção a um objetivo compartilhado? Como você decompõe uma grande iniciativa como "migrar todos os fluxos de trabalho para um novo mecanismo" em subtarefas rastreáveis que diferentes agentes podem abordar? Como você monitora o progresso, alerta sobre atrasos e garante que o todo seja maior que a soma das partes? Esta postagem final explora fluxos de trabalho de planejamento, decomposição de tarefas e coordenação de projetos - a camada de orquestração que prova que os agentes de IA podem lidar não apenas com tarefas individuais, mas com projetos inteiros e estruturados que exigem coordenação cuidadosa e rastreamento de progresso.

## Workflows de Planejamento e Coordenação de Projetos

Estes agentes coordenam planos e projetos multi-agente:

- **[Comando de Plano (Plan Command)](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/plan.md?plain=1)** - Decompõe issues em subtarefas acionáveis via comando `/plan` - **514 PRs mesclados de 761 propostos (taxa de mesclagem de 67%)**
- **[Minerador de Tarefas de Discussão (Discussion Task Miner)](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/discussion-task-miner.md?plain=1)** - Extrai tarefas acionáveis de threads de discussão - **60 PRs mesclados de 105 propostos (taxa de mesclagem de 57%)**

O Comando de Plano contribuiu com **514 PRs mesclados de 761 propostos (taxa de mesclagem de 67%)**, fornecendo decomposição de tarefas sob demanda que divide issues complexas em subtarefas acionáveis. Este é o **fluxo de trabalho de maior volume por atribuição** em toda a fábrica. Os desenvolvedores podem comentar `/plan` em qualquer issue para obter uma decomposição gerada por IA em sub-issues acionáveis nas quais os agentes podem trabalhar. Um exemplo verificado de cadeia causal: [Discussão #7631](https://github.com/github/gh-aw/discussions/7631) → [Issue #8058](https://github.com/github/gh-aw/issues/8058) → [PR #8110](https://github.com/github/gh-aw/pull/8110).

O Minerador de Tarefas de Discussão contribuiu com **60 PRs mesclados de 105 propostos (taxa de mesclagem de 57%)**, escaneando continuamente as discussões para extrair tarefas acionáveis que, de outra forma, poderiam ser perdidas. O fluxo de trabalho demonstra uma atribuição de cadeia causal perfeita: quando ele cria uma issue a partir de uma discussão, e o Assistente de Codificação Copilot corrige essa issue posteriormente, o PR resultante é atribuído corretamente ao Minerador de Tarefas de Discussão. Um exemplo verificado: [Discussão #13934](https://github.com/github/gh-aw/discussions/13934) → [Issue #14084](https://github.com/github/gh-aw/issues/14084) → [PR #14129](https://github.com/github/gh-aw/pull/14129). Exemplos mesclados recentes incluem [correção da extração de campos SSL-bump do firewall](https://github.com/github/gh-aw/pull/13920) e [adição de justificativa de segurança à documentação de permissões](https://github.com/github/gh-aw/pull/13918).

Aprendemos que agentes individuais são ótimos em tarefas focadas, mas orquestrar múltiplos agentes em direção a um objetivo compartilhado exige uma arquitetura cuidadosa. A coordenação de projetos não trata apenas de dividir o trabalho - trata de descobrir trabalho (Minerador de Tarefas), planejar trabalho (Comando de Plano) e rastrear trabalho (Gerenciador de Saúde do Fluxo de Trabalho).

Esses fluxos de trabalho implementam padrões como issues épicas, rastreamento de progresso e gerenciamento de prazos. Eles provam que os agentes de IA podem lidar não apenas com tarefas individuais, mas com projetos inteiros quando recebem a infraestrutura de coordenação adequada.

## Usando estes Workflows

Você pode adicionar esses fluxos de trabalho ao seu próprio repositório e remixá-los. Comece com nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/), depois execute um dos seguintes:

**Comando de Plano:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/plan.md
```

**Minerador de Tarefas de Discussão:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/discussion-task-miner.md
```

Em seguida, edite e remixe as especificações do fluxo de trabalho para atender às suas necessidades, regenere o arquivo de bloqueio usando `gh aw compile` e envie para o seu repositório. Veja nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/) para obter mais instruções de instalação e configuração.

Você também pode [criar seus próprios fluxos de trabalho](/gh-aw/setup/creating-workflows/).

## Saiba mais

- **[GitHub Agentic Workflows](https://github.github.com/gh-aw/)** - A tecnologia por trás dos fluxos de trabalho
- **[Início Rápido](https://github.github.com/gh-aw/setup/quick-start/)** - Como escrever e compilar fluxos de trabalho

---

## O que aprendemos

Ao longo desta jornada de 19 partes, exploramos fluxos de trabalho que vão desde bots de triagem simples a melhoradores sofisticados de múltiplas fases, de guardas de segurança a poetas criativos, desde a automação de tarefas individuais à orquestração em toda a organização.

O insight chave? **Os agentes de IA são mais poderosos quando são especializados, bem coordenados e projetados para seu contexto específico.** Nenhum agente faz tudo - em vez disso, temos um ecossistema onde cada agente se destaca em seu trabalho específico, e eles trabalham juntos por meio de uma orquestração cuidadosa.

Aprendemos que a observabilidade é essencial, que o progresso incremental supera esforços heroicos, que a segurança precisa de limites cuidadosos e que até fluxos de trabalho "divertidos" podem impulsionar um engajamento significativo. Descobrimos que os agentes de IA podem manter documentação, gerenciar campanhas, analisar seu próprio comportamento e melhorar continuamente bases de código - quando recebem a arquitetura e os mecanismos de proteção adequados.

Ao construir seus próprios fluxos de trabalho agentic, lembre-se: comece pequeno, meça tudo, itere com base no uso real e não tenha medo de experimentar. Os fluxos de trabalho que mostramos evoluíram por meio de experimentação e uso no mundo real. Os seus também evoluirão.

*Esta é a parte 19 (final) de uma série de 19 partes explorando os fluxos de trabalho na Fábrica de Agentes do Peli.*
