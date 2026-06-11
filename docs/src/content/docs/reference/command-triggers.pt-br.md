---
title: Gatilhos de comando
description: Aprenda sobre gatilhos de comando slash e funcionalidade de texto de contexto para fluxos de trabalho agentic, incluindo gatilhos especiais @mention para automação interativa.
sidebar:
  order: 500
---

O GitHub Agentic Workflows adiciona o conveniente gatilho `slash_command:` para criar fluxos de trabalho que respondem a `/meus-bots` em issues e comentários.

```yaml wrap
on:
  slash_command:
    name: meu-bot  # Opcional: padrão é o nome do arquivo sem a extensão .md
```

Você também pode usar formatos de abreviação:

```yaml wrap
on:
  slash_command: "meu-bot"  # Abreviação: a string especifica diretamente o nome do comando
```

```yaml wrap
on: /meu-bot  # Ultra-curto: o prefixo slash expande automaticamente para slash_command + workflow_dispatch
```

## Identificadores de comando múltiplos

Um único fluxo de trabalho pode responder a vários nomes de comando slash fornecendo um array de identificadores de comando:

```yaml wrap
on:
  slash_command:
    name: ["cmd.add", "cmd.remove", "cmd.list"]
```

Quando acionado, o comando correspondente fica disponível como `needs.activation.outputs.slash_command`, permitindo que seu fluxo de trabalho determine qual comando foi usado:

```aw wrap
---
on:
  slash_command:
    name: ["resumir", "resumo", "tldr"]
---

# Manipulador de múltiplos comandos

Você invocou o fluxo de trabalho usando: `/${{ needs.activation.outputs.slash_command }}`

Agora analisando o conteúdo...
```

Este recurso permite aliases de comando e manipuladores de comando agrupados sem duplicação de fluxo de trabalho.

Isso cria automaticamente gatilhos de issue/PR (`opened`, `edited`, `reopened`), gatilhos de comentário (`created`, `edited`), e execução condicional correspondente a menções `/nome-do-comando`.

**Disponibilidade de código:** Quando um comando é acionado a partir de um corpo de pull request, comentário de PR ou comentário de revisão de PR, o agente de codificação tem acesso tanto à branch do PR quanto à branch padrão.

O comando deve ser a **primeira palavra** do comentário ou corpo do texto para acionar o fluxo de trabalho. Isso evita gatilhos acidentais quando o comando é mencionado em outro lugar no conteúdo.

Você pode combinar `slash_command:` com outros eventos como `workflow_dispatch` ou `schedule`:

```yaml wrap
on:
  slash_command:
    name: meu-bot
  workflow_dispatch:
  schedule: semanalmente na segunda-feira
```

### Estratégia de gatilho centralizado

Defina `on.slash_command.strategy: centralized` para optar um fluxo de trabalho em roteamento centralizado de slash-command.
Quando habilitado, o fluxo de trabalho compila como centrado em `workflow_dispatch`, e o compilador gera um
fluxo de trabalho `agentic_commands.yml` compartilhado que escuta eventos de slash-command mesclados e
despacha fluxos de trabalho alvo correspondentes com `aw_context`.

```yaml wrap
on:
  slash_command:
    name: meu-bot
    strategy: centralized
```

**Nota**: Com a estratégia inline padrão, você não pode combinar `slash_command` com `issues`, `issue_comment` ou `pull_request` pois eles entrariam em conflito. Com `strategy: centralized`, eventos não-slash são preservados porque a correspondência slash é tratada no fluxo de trabalho de gatilho central gerado.

**Exceção para eventos apenas de label**: Você PODE combinar `slash_command` com `issues` ou `pull_request` se esses eventos forem configurados para gatilhos apenas de label (tipos `labeled` ou `unlabeled` apenas). Isso permite que fluxos de trabalho respondam a slash commands enquanto também reagem a alterações de label.

### Combinando `slash_command` com `bots:`

:::caution[Conflito de concorrência]
Combinar `slash_command` com `on.bots:` produz um aviso em tempo de compilação. Quando um bot listado em `bots:` posta um comentário que começa com o texto do comando slash (ex: `/nome-do-comando`), a verificação do comando passa e o bot aciona o fluxo de trabalho — ocupando o slot de concorrência e potencialmente bloqueando uma invocação manual simultânea, já que `cancel-in-progress` é desabilitado para fluxos de trabalho de gatilho de comando.

Para garantir que o fluxo de trabalho seja executado apenas em comandos explícitos do usuário, remova o campo `bots:`.
:::

```yaml wrap
# Esta configuração produz um aviso em tempo de compilação:
on:
  slash_command:
    name: rust-review
    events: [pull_request, pull_request_comment]
  bots:
    - "copilot[bot]"
```

```yaml wrap
on:
  slash_command: deploy
  issues:
    types: [labeled, unlabeled]  # Válido: gatilhos apenas de label não conflitam
```

Este padrão é útil quando você deseja um fluxo de trabalho que pode ser acionado tanto manualmente via comandos quanto automaticamente quando labels são alteradas.

## Filtrando eventos de comando

Por padrão, gatilhos de comando escutam todos os eventos relacionados a comentários, o que pode criar execuções ignoradas na interface do Actions. Use o campo `events:` para restringir onde os comandos estão ativos:

```yaml wrap
on:
  slash_command:
    name: meu-bot
    events: [issues, issue_comment]  # Apenas em corpos de issue e comentários de issue
```

**Eventos suportados:** `issues`, `issue_comment`, `pull_request`, `pull_request_comment`, `pull_request_review_comment`, `discussion`, `discussion_comment`, ou `*` (todos, padrão).

:::note
Tanto `issue_comment` quanto `pull_request_comment` mapeiam para o evento `issue_comment` do GitHub Actions com filtragem automática para distinguir entre comentários de issue e PR.
:::

### Exemplo de fluxo de trabalho de comando

Comando apenas para issue (evita execuções ignoradas de eventos de PR):

```yaml wrap
on:
  slash_command:
    name: investigar
    events: [issues, issue_comment]
```

Comando apenas para PR:

```yaml wrap
on:
  slash_command:
    name: code-review
    events: [pull_request, pull_request_comment]
```

## Texto de contexto

Todos os fluxos de trabalho acessam `steps.sanitized.outputs.text`, que fornece contexto **saneado**: para issues e PRs, é `título + "\n\n" + corpo`; para comentários e revisões, é o conteúdo do corpo.

```aw wrap
# Analise este conteúdo: "${{ steps.sanitized.outputs.text }}"
```

**Por que contexto saneado?** O texto saneado neutraliza @mentions e gatilhos de bot (como `fixes #123`), protege contra injeção de XML, filtra URIs para domínios HTTPS confiáveis, limita o tamanho do conteúdo (0.5MB máx, 65k linhas) e remove sequências de escape ANSI.

**Comparação:**
```aw wrap
# RECOMENDADO: Contexto saneado seguro
Analise esta issue: "${{ steps.sanitized.outputs.text }}"

# NÃO RECOMENDADO: Valores de contexto brutos (riscos de segurança)
Título: "${{ github.event.issue.title }}"
Corpo: "${{ github.event.issue.body }}"
```

## Reações e comentários de status

Fluxos de trabalho de comando habilitam `reaction: eyes` (👀) e `status-comment: true` por padrão. A reação adiciona um indicador visual aos comentários de acionamento; o comentário de status posta uma notificação de iniciado/concluído com um link para a execução do fluxo de trabalho.

Personalize ou desabilite qualquer um:

```yaml wrap
on:
  slash_command:
    name: meu-bot
  reaction: "rocket"       # Sobrescreve o padrão "eyes"
  status-comment: false    # Desabilita o comentário de status
```

Para desabilitar a reação completamente, use `reaction: none`.

Veja [Reações e comentários de status](/gh-aw/reference/triggers/#reactions-reaction) para todas as reações disponíveis e comportamento detalhado.

## Slash Commands em SideRepoOps

O GitHub Actions apenas entrega eventos ao repositório onde eles ocorrem. Com [SideRepoOps](/gh-aw/patterns/side-repo-ops/) — onde os fluxos de trabalho vivem em um repositório lateral separado — eventos do repositório principal nunca são entregues lá. **Gatilhos de slash command não podem ser usados diretamente em um fluxo de trabalho SideRepoOps.**

A solução recomendada é um **padrão de ponte**: um fluxo de trabalho de relay fino no repositório principal recebe o slash command e o encaminha para o repositório lateral via `workflow_dispatch`.

Veja [Slash Commands em SideRepoOps](/gh-aw/patterns/side-repo-ops/#slash-commands) para um passo a passo completo com exemplos e compensações.

## Documentação relacionada

- [Frontmatter](/gh-aw/reference/frontmatter/) - Todas as opções de configuração para fluxos de trabalho
- [Estrutura do fluxo de trabalho](/gh-aw/reference/workflow-structure/) - Layout e organização de diretório
- [Comandos CLI](/gh-aw/setup/cli/) - Comandos CLI para gerenciamento de fluxo de trabalho
- [SideRepoOps](/gh-aw/patterns/side-repo-ops/) - Executando fluxos de trabalho a partir de um repositório separado
- [ChatOps](/gh-aw/patterns/chat-ops/) - Automação interativa com slash commands
