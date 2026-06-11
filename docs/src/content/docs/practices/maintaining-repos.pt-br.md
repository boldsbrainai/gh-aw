---
title: Mantendo Repositórios com Fluxos de Trabalho Agenticos
description: Como usar repo-assist, safe-outputs e filtragem de integridade para gerenciar um repositório open-source em escala — controlando o que os agentes podem fazer, filtrando entrada não confiável e depurando falhas.
sidebar:
  order: 20
---

Mantenedores de open-source enfrentam um desafio único ao executar fluxos de trabalho agenticos: qualquer pessoa pode abrir uma issue ou PR, acionando execuções de agente que consomem computação e tokens — mas nem todo contribuidor é igualmente confiável. O gh-aw aborda isso com dois mecanismos de segurança complementares:

- **Safe-outputs** — O mecanismo primário para controlar *o que um agente pode fazer*. Toda mutação no GitHub (abrir issues, comentar, criar PRs) deve ser explicitamente declarada; tudo o que não estiver listado é bloqueado.
- **Filtragem de integridade** — O mecanismo primário para controlar *o que o conteúdo o agente vê*. O conteúdo de autores não confiáveis é filtrado do contexto do agente antes da execução começar.

Juntos, eles formam um modelo de defesa em profundidade: a filtragem de integridade mantém o conteúdo não confiável fora do contexto do agente, e os safe-outputs garantem que o agente só possa produzir efeitos colaterais autorizados. Este guia mostra como usar o [🌈 Repo Assist](https://github.com/githubnext/agentics/blob/main/docs/repo-assist.md) como o ponto de entrada primário para gerenciar o trabalho recebido, e como configurar ambos os mecanismos para que seu repositório escale com segurança.

## Repo Assist como sua Camada de Triagem

O [🌈 Repo Assist](https://github.com/githubnext/agentics/blob/main/docs/repo-assist.md) é um fluxo de trabalho executado em cada nova issue ou PR, classifica o conteúdo e roteia o trabalho para o lugar certo. É o ponto de partida recomendado para qualquer repositório público porque:

- Vê todo o conteúdo recebido (incluindo o de usuários não confiáveis), para que nada seja silenciosamente ignorado.
- Aplica classificação leve e de baixo custo (labels, comentários) em vez de ações pesadas do agente.
- Atua como uma porta que agentes a jusante que modificam código dependem antes de serem executados.

## Controlando Saídas de Fluxo de Trabalho com Safe-Outputs

Safe-outputs é o mecanismo primário para controlar o que um fluxo de trabalho pode fazer. Toda ação que produz um efeito colateral no GitHub — marcar uma issue, postar um comentário, abrir um pull request, mesclar — deve ser explicitamente declarada no bloco `safe-outputs:`. Se uma ação não estiver listada, o runtime a bloqueia antes que ela chegue à API.

É isso que torna seguro executar repo-assist com `min-integrity: unapproved`: mesmo que o agente gerasse uma instrução para abrir um PR ou fechar uma issue, o runtime a rejeitaria porque essas saídas não foram declaradas.

Os safe-outputs disponíveis mapeiam diretamente para as ações do GitHub:

| Safe-output | O que ele permite |
| ------------ | --------------- |
| `label-issue` | Aplicar ou remover labels em uma issue |
| `comment-issue` | Postar um comentário em uma issue |
| `comment-pull-request` | Postar um comentário em um pull request |
| `create-pull-request` | Abrir um novo pull request |
| `merge-pull-request` | Mesclar um pull request (experimental) |
| `close-issue` | Fechar uma issue |
| `create-issue` | Abrir uma nova issue |
| `assign-issue` | Atribuir uma issue a um usuário ou equipe |

## Controlando Entradas de Fluxo de Trabalho com Filtragem de Integridade

A filtragem de integridade é o mecanismo primário para controlar o que o agente vê. Ela avalia o autor de cada issue, PR ou comentário e remove itens que não atendem ao limite de confiança configurado — antes que o contexto do agente seja montado. Todo repositório público aplica automaticamente `min-integrity: approved` como base — o repo-assist sobrescreve isso para `unapproved` para que possa ver issues de contribuidores e contribuidores de primeira viagem, não apenas membros confiáveis.

Os quatro níveis configuráveis, do mais ao menos restritivo:

| Nível | Quem qualifica |
| ------- | -------------- |
| `merged` | PRs mesclados na branch padrão; commits alcançáveis a partir da main |
| `approved` | Proprietários, membros, colaboradores; PRs que não são de fork em repos públicos; bots reconhecidos (`dependabot`, `github-actions`) |
| `unapproved` | Contribuidores que já tiveram um PR mesclado antes; contribuidores de primeira viagem |
| `none` | Todo o conteúdo, incluindo usuários sem relacionamento prévio |

Escolha com base no que o fluxo de trabalho faz:

- **Fluxos de trabalho de repo-assist / triagem**: `unapproved` — classifique conteúdo de contribuidores e de contribuidores de primeira viagem sem agir sobre eles.
- **Fluxos de trabalho que modificam código** (abrir PRs, aplicar patches, fechar issues): `approved` ou `merged` — aja apenas sobre entrada confiável.
- **Detecção de spam ou análise**: `none` — veja tudo, mas não produza mutações diretas no GitHub.

### Reações como Sinais de Confiança

Mantenedores podem usar reações do GitHub (👍, ❤️) para promover conteúdo além do filtro de integridade sem modificar labels. Isso é útil em fluxos de trabalho de repo-assist onde um mantenedor deseja acelerar uma contribuição externa.

Para habilitar reações, adicione a flag de funcionalidade `integrity-reactions`:

```aw wrap
features:
  integrity-reactions: true
tools:
  github:
    min-integrity: approved
```

O compilador cuida do resto — quando `integrity-reactions: true` é definido, ele automaticamente:

- Habilita o proxy CLI (`cli-proxy: true`), necessário para decisões de integridade baseadas em reação
- Injeta reações de endosso padrão: `THUMBS_UP`, `HEART`
- Injeta reações de desaprovação padrão: `THUMBS_DOWN`, `CONFUSED`
- Usa `endorser-min-integrity: approved` (apenas reações de proprietários, membros e colaboradores contam)
- Usa `disapproval-integrity: none` (uma reação de desaprovação rebaixa o conteúdo para `none`)

Esses padrões significam que quando um membro confiável (proprietário, membro ou colaborador) adiciona uma reação 👍 ou ❤️ a uma issue ou comentário, a integridade do item é promovida para `approved` — tornando-o visível para agentes usando `min-integrity: approved`. Por outro lado, uma reação 👎 ou 😕 de um membro confiável rebaixa o item para `none`.

Veja a [Referência de Filtragem de Integridade](/gh-aw/reference/integrity/) para detalhes completos de configuração.

## Estratégias de Escalonamento

### Consciência do Orçamento de Tokens

A filtragem de integridade reduz diretamente o consumo de tokens: itens filtrados pelo gateway nunca aparecem na janela de contexto do agente. Em um repositório público ocupado, `min-integrity: approved` em agentes a jusante pode reduzir o tamanho do contexto drasticamente em comparação com ver toda a atividade.

Use `gh aw logs --format markdown --count 20` para rastrear tendências de token ao longo do tempo. O relatório de execução cruzada expõe picos de custo, uso anômalo de token e detalhamentos por execução para que você possa detectar regressões antes que elas se acumulem.

### Limitação de Taxa

A chave de frontmatter `user-rate-limit` limita quantas vezes um fluxo de trabalho pode ser executado em uma janela deslizante, impedindo que uma enxurrada de issues recebidas esgote o orçamento de computação ou inferência:

```aw wrap
user-rate-limit:
  max-runs-per-window: 5
  window: 60
```

Veja [Controles de Limitação de Taxa](/gh-aw/reference/rate-limiting-controls/) para opções completas.

### Pulos de Associação de Autor de Pré-Ativação

Para fluxos de trabalho de moderação e triagem operados por mantenedores, você pode pular execuções antecipadamente para combinações específicas de evento/associação de autor usando `on.skip-author-associations`:

```aw wrap
on:
  issue_comment:
    types: [created]
  skip-author-associations:
    issue_comment: [owner, member, collaborator]
```

Isso compila em uma guarda `if` de nível de job de pré-ativação (usando campos de payload específicos de evento como `github.event.comment.author_association`, `github.event.issue.author_association` e `github.event.pull_request.author_association`), para que execuções correspondentes sejam puladas antes que a execução do agente comece.

### Controles de Concorrência

Fluxos de trabalho usam automaticamente controle de concorrência duplo (por fluxo de trabalho e por engine). Para repo-assist, você pode querer concorrência maior para que múltiplas issues sejam triadas em paralelo em vez de enfileiradas:

```aw wrap
concurrency:
  max-parallel: 3
```

### Escopando Acesso ao Repositório

`allowed-repos` impede leituras entre repositórios que não são necessárias para a tarefa do fluxo de trabalho:

```aw wrap
tools:
  github:
    allowed-repos: "myorg/*"
    min-integrity: approved
```

Isso é útil em configurações de monorepo ou multi-repo onde o agente só deve ler dos repositórios da própria organização.

## Depurando Fluxos de Trabalho com Falha

### Início Rápido: Depuração Assistida por IA

O caminho mais rápido para uma causa raiz é passar a URL da execução com falha para a Copilot CLI:

```bash
copilot
```

Dentro da CLI:

```text
/agent agentic-workflows

Depure esta execução: https://github.com/OWNER/REPO/actions/runs/RUN_ID
```

O agente carrega o prompt `debug-agentic-workflow`, audita a execução e explica o que deu errado. Acompanhe com perguntas específicas sobre domínios bloqueados, ferramentas ausentes ou falhas de safe-output.

No GitHub.com com [autoria agentica configurada](/gh-aw/guides/agentic-authoring/):

```text
/agent agentic-workflows debug https://github.com/OWNER/REPO/actions/runs/RUN_ID
```

### Depuração Manual com Comandos CLI

**Auditar uma execução específica:**

```bash
gh aw audit RUN_ID
gh aw audit RUN_ID --json    # saída legível por máquina
gh aw audit RUN_ID --parse   # escreve log.md e firewall.md
```

O relatório de auditoria cobre: resumo de falha, uso de ferramenta, saúde do servidor MCP, análise de firewall, métricas de token e ferramentas ausentes.

**Analisar logs através de múltiplas execuções:**

```bash
gh aw logs my-workflow
gh aw logs my-workflow --format markdown --count 10
gh aw logs --filtered-integrity    # apenas execuções com eventos filtrados por DIFC
```

**Comparar duas execuções para regressões:**

```bash
gh aw audit BASELINE_ID CURRENT_ID
```

### Padrões de Falha Comuns

| Falha | Sintoma / Causa | Correções |
| --------- | ----------------- | ------- |
| **Chamadas de ferramenta ausentes** | Ferramenta não configurada ou nome errado. Verifique `missing_tools` na auditoria. | Adicione ao `tools:` no frontmatter; corrija qualquer prefixo `safeoutputs-`; verifique conectividade MCP. |
| **Falhas de autenticação** | Permissões de token muito estreitas ou chave de API ausente. | Revise o bloco `permissions:`; garanta que segredos estejam definidos; veja [Referência de Auth](/gh-aw/reference/auth/). |
| **Filtragem de integridade bloqueando conteúdo** | Associação do autor abaixo de `min-integrity`. Eventos `DIFC_FILTERED` na auditoria mostram detalhes. | Ajuste `min-integrity`; adicione autor a `trusted-users`; use `approval-labels`; verifique `gh aw logs --filtered-integrity`. |
| **Falhas de validação de safe-output** | Agente tentou ação GitHub não declarada. Safe-outputs bloqueia tudo o que não estiver listado. | Revise `safe-outputs:`; verifique `safe_outputs.jsonl` nos artefatos de auditoria; veja [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/). |
| **Exaustão de orçamento de token** | Execução atingiu o limite de token antes de concluir. | Aumente `min-integrity` para reduzir contexto; adicione `cache-memory:`; simplifique prompt; aperte `user-rate-limit`. |
| **Bloqueios de rede** | Domínio necessário bloqueado pelo firewall. | Verifique seção de firewall da auditoria; adicione domínio a `network.allowed`; veja [Guia de Configuração de Rede](/gh-aw/guides/network-configuration/). |

### Fluxo de Trabalho de Depuração Iterativo

1. Verifique o resumo da execução do fluxo de trabalho na UI do GitHub Actions.
2. Execute `gh aw audit RUN_ID` para um detalhamento estruturado.
3. Para problemas complexos, use `/agent agentic-workflows` no Copilot Chat.
4. Edite o arquivo `.md` → execute `gh aw compile` para validar → dispare uma nova execução.
5. Compare a nova execução contra a baseline com `gh aw audit BASELINE_ID NEW_ID`.

## Documentação Relacionada

- [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/) — Documentação completa de tipo de saída e requisitos de formato
- [Referência de Filtragem de Integridade](/gh-aw/reference/integrity/) — Configuração completa de `min-integrity` e política
- [Controles de Limitação de Taxa](/gh-aw/reference/rate-limiting-controls/) — Prevenindo fluxos de trabalho descontrolados
- [Gerenciamento de Custo](/gh-aw/reference/cost-management/) — Rastreamento e otimização de orçamento de token
- [Comandos de Auditoria](/gh-aw/reference/audit/) — Referência de `gh aw audit` e `gh aw logs`
- [Depurando Fluxos de Trabalho](/gh-aw/troubleshooting/debugging/) — Procedimentos detalhados de depuração
- [Guia de Configuração de Rede](/gh-aw/guides/network-configuration/) — Configuração de firewall e domínio
- [Referência de Ferramentas GitHub](/gh-aw/reference/github-tools/) — Opções completas de `tools.github`
