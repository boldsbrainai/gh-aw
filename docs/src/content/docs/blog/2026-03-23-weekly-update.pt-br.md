---
title: "Atualização Semanal – 23 de março de 2026"
description: "Oito lançamentos esta semana: endurecimento de segurança, ações personalizadas como ferramentas de safe-output, um aumento de velocidade de 20 segundos e suporte a fuso horário para fluxos de trabalho agendados."
authors:
  - copilot
date: 2026-03-23
---

Mais uma semana, outra enxurrada de lançamentos em [github/gh-aw](https://github.com/github/gh-aw). Oito versões lançadas entre 18 e 21 de março, impulsionando o endurecimento de segurança, extensibilidade e melhorias de desempenho em todos os níveis. Aqui está o que você precisa saber.

## Lançamentos desta Semana

### [v0.62.5](https://github.com/github/gh-aw/releases/tag/v0.62.5) — 21 de março

O lançamento mais recente lidera com duas correções de segurança importantes:

- **Proteção da cadeia de suprimentos**: A ação do scanner de vulnerabilidade Trivy foi removida após a descoberta de um comprometimento na cadeia de suprimentos ([#22007](https://github.com/github/gh-aw/pull/22007), [#22065](https://github.com/github/gh-aw/pull/22065)). O escaneamento foi substituído por uma alternativa mais segura.
- **Endurecimento da integridade de repos públicos** ([#21969](https://github.com/github/gh-aw/pull/21969)): A autenticação de GitHub App não isenta mais repositórios públicos da política de proteção de integridade mínima, fechando uma lacuna onde conteúdo não confiável poderia contornar verificações de integridade.

Do lado dos recursos:

- **Suporte a fuso horário para `on.schedule`** ([#22018](https://github.com/github/gh-aw/pull/22018)): Entradas cron agora aceitam um campo `timezone` opcional — finalmente, chega de aritmética UTC mental quando você quiser que seu fluxo de trabalho rode "às 9 da manhã no Pacífico".
- **Otimizador de expressão booleana** ([#22025](https://github.com/github/gh-aw/pull/22025)): Árvores de condição são otimizadas em tempo de compilação, gerando expressões `if:` mais limpas em fluxos de trabalho compilados.
- **`target-repo` curinga em manipuladores de safe-output** ([#21877](https://github.com/github/gh-aw/pull/21877)): Use `target-repo: "*"` para escrever uma definição de manipulador única que funciona em qualquer repositório.

### [v0.62.3](https://github.com/github/gh-aw/releases/tag/v0.62.3) — 20 de março

Este é um destaque para extensibilidade e velocidade:

- **Ações Personalizadas como Ferramentas de Safe Output** ([#21752](https://github.com/github/gh-aw/pull/21752)): Você agora pode expor qualquer GitHub Action como uma ferramenta MCP através do novo bloco `safe-outputs.actions`. O compilador resolve `action.yml` em tempo de compilação para derivar o esquema da ferramenta e injetá-lo no agente — sem necessidade de cabeamento personalizado. Isso abre as portas para todo um ecossistema de manipuladores de safe-output reutilizáveis construídos a partir de Actions padrão.
- **~20 segundos mais rápido por execução de fluxo de trabalho** ([#21873](https://github.com/github/gh-aw/pull/21873)): Um bump para `DefaultFirewallVersion` v0.24.5 elimina um atraso de desligamento de 10 segundos para o container do agente e para o container de detecção de ameaças. São 20 segundos livres em cada execução.
- **Suporte a `trustedBots` no MCP Gateway** ([#21865](https://github.com/github/gh-aw/pull/21865)): Passe uma lista de permissão de identidades de bots adicionais do GitHub para o MCP Gateway, permitindo colaboração segura cross-bot em ambientes protegidos.
- **`gh-aw-metadata` v3** ([#21899](https://github.com/github/gh-aw/pull/21899)): Arquivos de trava agora incorporam o ID/modelo do agente configurado no comentário `gh-aw-metadata`, tornando as auditorias muito mais fáceis.

### [v0.62.2](https://github.com/github/gh-aw/releases/tag/v0.62.2) — 19 de março

⚠️ **Alerta de mudança importante (breaking change)**: `lockdown: true` acabou. Foi substituído pelo campo `min-integrity`, mais expressivo. Se você tiver `lockdown: false` no seu frontmatter, remova-o — não é mais reconhecido. O novo sistema de nível de integridade oferece controle mais refinado sobre qual conteúdo pode disparar seus fluxos de trabalho.

Este lançamento também introduz **filtragem de integridade para análise de logs** — o comando `gh aw logs` agora pode filtrar apenas execuções onde eventos de integridade DIFC foram disparados, tornando investigações de segurança muito mais rápidas.

### [v0.62.0](https://github.com/github/gh-aw/releases/tag/v0.62.0) — 19 de março

A política de proteção MCP do GitHub chega à **disponibilidade geral (GA)**. A política configura automaticamente controles de acesso apropriados no servidor MCP do GitHub em tempo de execução — nenhuma configuração manual de `lockdown` é necessária. Também novo: **scripts de safe-output personalizados em linha**, permitindo definir manipuladores JavaScript diretamente no frontmatter do seu fluxo de trabalho sem um arquivo separado.

### [v0.61.x](https://github.com/github/gh-aw/releases/tag/v0.61.2) — 18 de março

Três lançamentos de patch cobriram:
- Suporte a commits assinados para branches protegidos ([v0.61.1](https://github.com/github/gh-aw/releases/tag/v0.61.1))
- Cobertura de domínio de ecossistema mais ampla para registros de pacotes de linguagem ([v0.61.2](https://github.com/github/gh-aw/releases/tag/v0.61.2))
- Correção crítica de avaliação de expressão `workflow_dispatch` ([v0.61.2](https://github.com/github/gh-aw/releases/tag/v0.61.2))

## Pull Requests Notáveis

Várias correções importantes desembarcaram hoje (23 de março):

- **[Propagar falhas de `assign_copilot` para comentário de falha do agente](https://github.com/github/gh-aw/pull/22371)** ([#22371](https://github.com/github/gh-aw/pull/22371)): Quando `assign_copilot_to_created_issues` falha (ex: credenciais incorretas), o contexto da falha agora é exibido na issue de falha do agente para que você possa diagnosticá-la.
- **[Postar comentário de falha quando atribuição de agente falha](https://github.com/github/gh-aw/pull/22347)** ([#22347](https://github.com/github/gh-aw/pull/22347)): Um acompanhamento do anterior — a falha agora também posta um comentário diretamente na issue ou PR alvo para visibilidade imediata.
- **[Eliminação de regexp de caminho crítico e parse de YAML](https://github.com/github/gh-aw/pull/22359)** ([#22359](https://github.com/github/gh-aw/pull/22359)): Compilações redundantes de regexp e re-parses de YAML no caminho crítico foram eliminados, melhorando o throughput para execução de fluxo de trabalho de alto volume.
- **[`blocked-users` e `approval-labels` na política de proteção](https://github.com/github/gh-aw/pull/22360)** ([#22360](https://github.com/github/gh-aw/pull/22360)): A política de proteção `tools.github` agora suporta campos `blocked-users` e `approval-labels`, dando a você controle mais granular sobre quem pode disparar fluxos de trabalho protegidos.
- **[Puxar arquivos de fluxo de trabalho mesclados após o GitHub confirmar prontidão](https://github.com/github/gh-aw/pull/22335)** ([#22335](https://github.com/github/gh-aw/pull/22335)): Uma condição de corrida onde arquivos de fluxo de trabalho mesclados eram puxados antes que o GitHub relatasse o fluxo de trabalho como pronto foi corrigida.

## 🤖 Agente da Semana: contribution-check

Seu incansável guardião da qualidade de PR a cada quatro horas — lê cada pull request aberto e o avalia em relação ao `CONTRIBUTING.md` quanto à conformidade e completude.

`contribution-check` rodou cinco vezes esta semana (uma vez a cada quatro horas, conforme agendado) e processou um fluxo constante de PRs recebidos, criando issues para contribuidores que precisavam de orientação, adicionando labels e deixando comentários de revisão. Quatro das cinco execuções foram concluídas em menos de 5 minutos com 6–9 turnos. A quinta execução, no entanto, aparentemente achou a tarefa de revisar PRs durante um domingo à noite particularmente ativo tão intelectualmente estimulante que passou por 50 turnos e consumiu 1,55 milhão de tokens — cerca de 5× seu apetite habitual — antes que o passo safe_outputs educadamente encerrasse a noite. Ele ainda conseguiu abrir issues, rotular PRs e postar comentários na saída. Exagerado.

Uma execução anterior também encontrou um pequeno obstáculo: o passo de filtro de pré-ativação esqueceu de escrever seu arquivo de saída, deixando o agente sem nada para avaliar. Em vez de fabricar uma lista de PRs para revisar, ele relatou com dever o "missing data" e seguiu em frente em vez de alucinar. Às vezes, a coisa mais corajosa é saber quando não há nada a fazer.

💡 **Dica de uso**: O padrão `contribution-check` funciona melhor quando seu `CONTRIBUTING.md` é explícito e opinativo — quanto mais específicas forem suas diretrizes, mais acionável será o feedback para os contribuidores.

→ [Ver o fluxo de trabalho no GitHub](https://github.com/github/gh-aw/blob/main/.github/workflows/contribution-check.md)

## Experimente

Atualize para a [v0.62.5](https://github.com/github/gh-aw/releases/tag/v0.62.5) hoje para obter as correções de segurança e o suporte a fuso horário. Se você estava adiando a migração de `lockdown: true`, agora é a hora — verifique as [notas de lançamento da v0.62.2](https://github.com/github/gh-aw/releases/tag/v0.62.2) para o caminho de migração. Como sempre, contribuições e feedback são bem-vindos em [github/gh-aw](https://github.com/github/gh-aw).
