---
title: Controle de Rodapé
description: Aprenda como controlar rodapés gerados por IA em operações de safe output e personalizar mensagens de rodapé para issues, pull requests, discussões e releases do GitHub.
sidebar:
  order: 805
---

Controle se rodapés gerados por IA são adicionados a itens criados e atualizados no GitHub (issues, pull requests, discussões, releases). Os rodapés fornecem atribuição e links para execuções de fluxo de trabalho, mas você pode querer omiti-los para um conteúdo mais limpo ou ao usar branding personalizado.

## Controle Global de Rodapé

Defina `footer: false` no nível de `safe-outputs` para ocultar rodapés para todos os tipos de saída:

```yaml wrap
safe-outputs:
  footer: false                      # oculta rodapés globalmente
  create-issue:
    title-prefix: "[ai] "
  create-pull-request:
    title-prefix: "[ai] "
```

Quando `footer: false` é definido, o texto de atribuição visível é omitido dos corpos dos itens, mas marcadores XML ocultos permanecem para fins de pesquisabilidade:
- `<!-- gh-aw-workflow-id: WORKFLOW_NAME -->` — para busca e rastreamento
- `<!-- gh-aw-tracker-id: unique-id -->` — para rastreamento de issue/discussão

Aplica-se a todos os tipos de saída: create-issue, create-pull-request, create-discussion, update-issue, update-pull-request, update-discussion e update-release.

### Buscando por Itens Criados por Fluxos de Trabalho

Use o marcador `gh-aw-workflow-id` (o nome do arquivo do fluxo de trabalho sem `.md`) para encontrar itens na busca do GitHub:

```
repo:owner/repo is:issue is:open "gh-aw-workflow-id: daily-team-status" in:body
repo:owner/repo "gh-aw-workflow-id: bot-responder" in:comments
```

Combine com filtros `is:open`, `created:>2024-01-01` ou `org:your-org`. Veja [busca avançada do GitHub](https://docs.github.com/en/search-github/searching-on-github/searching-issues-and-pull-requests).

## Controle de Rodapé por Handler

Substitua a configuração global para tipos de saída específicos definindo `footer` no nível do handler:

```yaml wrap
safe-outputs:
  footer: false                      # padrão global: sem rodapés
  create-issue:
    title-prefix: "[issue] "
    # herda footer: false
  create-pull-request:
    title-prefix: "[pr] "
    footer: true                     # substitui: mostra rodapé apenas para PRs
```

Configurações individuais de handler sempre têm precedência sobre a configuração global.

## Controle de Rodapé de Revisão de PR

Para revisões de PR (`submit-pull-request-review`), o campo `footer` suporta controle condicional sobre quando o rodapé é adicionado ao corpo da revisão:

```yaml wrap
safe-outputs:
  create-pull-request-review-comment:
  submit-pull-request-review:
    footer: "if-body"         # rodapé condicional baseado no corpo da revisão
```

O campo `footer` aceita `"always"` (padrão), `"none"` ou `"if-body"` (rodapé apenas quando a revisão tiver texto no corpo). Booleanos são aceitos: `true` → `"always"`, `false` → `"none"`. Use `"if-body"` para revisões de aprovação limpas — aprovações sem texto no corpo aparecem sem rodapé, enquanto revisões com comentários o incluem.

## Compatibilidade Retroativa

O valor padrão para `footer` é `true`. Para ocultar rodapés, defina explicitamente `footer: false`.

## Personalizando Mensagens de Rodapé

Em vez de ocultar rodapés completamente, você pode personalizar o texto da mensagem de rodapé usando o template `messages.footer`. Isso permite que você mantenha a atribuição enquanto usa branding personalizado:

```yaml wrap
safe-outputs:
  messages:
    footer: "> 🤖 Powered by [{workflow_name}]({agentic_workflow_url})"
  create-issue:
    title-prefix: "[bot] "
```

O template `messages.footer` suporta variáveis como `{workflow_name}`, `{agentic_workflow_url}`, `{run_url}`, `{triggering_number}`, `{effective_tokens_suffix}` e outras. `{agentic_workflow_url}` aponta diretamente para a visualização do arquivo de fluxo de trabalho agentic da execução (equivalente a `{run_url}/agentic_workflow`), enquanto `{run_url}` aponta para a página simples de execução de Actions. `{effective_tokens_suffix}` é um sufixo pré-formatado e sempre seguro (ex: `" · ● 1.2K"` ou `""`) que você pode colocar diretamente antes de `{history_link}` — o mesmo formato `●` que o rodapé padrão usa. Veja [Mensagens Personalizadas](/gh-aw/reference/safe-outputs/#custom-messages-messages) para documentação completa sobre templates de mensagem e variáveis disponíveis.

## Documentação Relacionada

- [Safe Outputs](/gh-aw/reference/safe-outputs/) - Referência completa de safe outputs
- [Mensagens Personalizadas](/gh-aw/reference/safe-outputs/#custom-messages-messages) - Templates de mensagem e variáveis
- [Frontmatter](/gh-aw/reference/frontmatter/) - Todas as opções de configuração para fluxos de trabalho
