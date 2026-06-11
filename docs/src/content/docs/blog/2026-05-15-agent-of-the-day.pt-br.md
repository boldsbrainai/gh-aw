---
title: "Agente do Dia – 15 de maio de 2026"
description: "Conheça o Moderador de I.A.: um fluxo de trabalho movido a Codex que revisa cada PR, issue e comentário quanto à conformidade de política — automaticamente."
authors:
  - copilot
date: 2026-05-15
metadata:
  seoDescription: "Moderador de I.A. movido a Codex em gh-aw revisa automaticamente pull requests, issues e comentários quanto à conformidade de política — rotulando, ocultando e sinalizando em segundos."
  linkedPostText: "Como o Moderador de I.A. aplica conformidade de política em cada PR e issue"
---

Todo repositório de código aberto tem o mesmo imposto invisível: alguém tem que vigiar a porta. Rotular o PR. Verificar se o comentarista é um membro ou um estranho. Ocultar a violação de política antes que ela se espalhe. Sinalizar o caso ambíguo para um humano. É repetitivo, importante e fácil de perder às 2 da manhã quando o CI está verde e você está tentando lançar uma versão.

Essa é a lacuna que o fluxo de trabalho Moderador de I.A. preenche — automaticamente, em cada evento, antes mesmo que um humano abra suas notificações.

---

## Agente do Dia: Moderador de I.A.

O Moderador de I.A. é um fluxo de trabalho agentic movido a Codex no repositório `github/gh-aw`. Ele dispara em pull requests, novas issues e comentários — executando uma investigação estruturada a cada vez para determinar quem está batendo, o que trouxeram e qual ação tomar. Rotule-o. Oculte-o. Escale-o. Ou aguarde.

Não é um simples bot baseado em regras. Ele raciocina.

Em uma execução recente — [Execução de Actions 25924881974](https://github.com/github/gh-aw/actions/runs/25924881974) — o agente acordou quando o [PR #32406](https://github.com/github/gh-aw/pull/32406) desembarcou: um branch de trabalho em progresso intitulado *"Experiment with output format in daily compiler quality"* de `copilot/ab-advisorexperiment-output-format`. Dezesseis turnos depois, ele tinha feito seu trabalho.

### O que ele realmente fez

O agente não adivinhou. Ele buscou informações.

Ele começou se orientando — chamando `github___get_me` para confirmar sua própria identidade, depois `github-search_repositories` para verificar o contexto do repositório em que estava operando. A partir daí, ele se espalhou: `github-list_branches`, `github-list_tags`, `github-list_releases`, `github-get_teams`, `github-get_team_members`. Ele estava construindo uma imagem de quem pertence aqui e como é o repositório agora.

Então ele se voltou para o PR em si. Ele puxou os detalhes do PR com `github___pull_request_read`, pesquisou issues relacionadas com `github___search_issues` e `github___search_pull_requests`, revisou o histórico de commits via `github___list_commits` e leu qualquer contexto de issue vinculada através de `github-issue_read`. Esse é um escopo amplo — o tipo que um revisor humano faria informalmente, mas de forma inconsistente. O agente fez isso todas as vezes, na mesma ordem, com um registro logado de cada passo.

A conclusão: `action_required`. O agente aplicou labels através de `safeoutputs-add_labels`, ocultou pelo menos um comentário usando `safeoutputs___hide_comment` e levantou uma flag com `safeoutputs-report_incomplete` para sinalizar que o acompanhamento era necessário. Onde as verificações passaram limpas, ele chamou `safeoutputs-noop` — confirmação explícita de que nada justificava ação, não apenas silêncio.

### Dezesseis turnos, e isso é notável

O sistema de auditoria rastreia linhas de base comportamentais. No mesmo dia, uma execução de referência ([25924730956](https://github.com/github/gh-aw/actions/runs/25924730956)) foi concluída com zero turnos e uma conclusão de `success`. Esta execução levou 16. O delta foi marcado automaticamente como um `turns_increase` que exigia revisão.

Essa flag importa. Significa que o sistema detectou um desvio significativo em como o agente se comportou — não uma falha, mas um sinal que vale a pena inspecionar. O PR tinha características incomuns? A busca por associação de equipe foi mais complexa do que o normal? A trilha de auditoria está lá. A observação já está logada.

É isso que torna os fluxos de trabalho agentic diferentes de scripts: o comportamento muda com a entrada, e o monitoramento tem que levar isso em conta.

### Por que vale a pena assistir

A moderação comunitária é um daqueles problemas onde o custo de subinvestir é invisível até que não seja mais. Um label perdido significa um PR encaminhado incorretamente. Um comentário que deveria ter sido ocultado permanece. Um colaborador externo é tratado da mesma forma que um mantenedor quando não deveria.

O Moderador de I.A. fecha essa lacuna sem exigir que um humano esteja de plantão para isso. Ele verifica a associação da equipe — não apenas presumida por um nome de usuário, mas verificada contra `github-get_team_members`. Ele aplica saídas estruturadas através da interface `safeoutputs`, o que significa que cada ação é auditável. E quando ele não consegue resolver um caso com confiança, ele diz isso explicitamente via `report_incomplete`, em vez de silenciosamente não fazer nada.

Rápido também. Esta execução foi concluída em segundos.

### Experimente

O fluxo de trabalho é parte do projeto de fluxos de trabalho agentic `github/gh-aw` — uma coleção crescente de agentes movidos a Codex construídos para automatizar as partes inglórias da engenharia de software. Se sua equipe mantém um repositório e você está cansado de fazer o papel de porteiro manualmente, este é um bom lugar para começar.

Vá para [github.com/github/gh-aw](https://github.com/github/gh-aw) para ver os fluxos de trabalho, ler as especificações e explorar o que já está rodando em produção.

---

*Agente do Dia é um olhar recorrente sobre fluxos de trabalho agentic construídos e executados dentro da org de engenharia do GitHub.*
