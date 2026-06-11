---
title: IssueOps
description: Automatize a triagem, categorização e respostas de issues quando elas são abertas - gerenciamento de issues totalmente automatizado
sidebar:
  badge: { text: 'Disparado por evento', variant: 'success' }
---

IssueOps transforma issues do GitHub em gatilhos de automação que analisam, categorizam e respondem a issues automaticamente. Use-o para auto-triagem, roteamento inteligente, respostas iniciais e verificações de qualidade. O GitHub Agentic Workflows torna isso natural através de gatilhos de issue e [safe-outputs](/gh-aw/reference/safe-outputs/) que lidam com respostas automatizadas de forma segura, sem a necessidade de permissões de escrita para o job principal da IA.

Quando issues são criadas, fluxos de trabalho são ativados automaticamente. A IA analisa o conteúdo e fornece respostas inteligentes através de comentários automatizados.

```aw wrap
---
on:
  issues:
    types: [opened]
permissions:
  contents: read
  actions: read
safe-outputs:
  add-comment:
    max: 2
---

# Assistente de Triagem de Issue

Analise o conteúdo de novas issues e forneça orientações úteis. Examine o título e a descrição em busca de relatórios de bugs que precisam de informações, solicitações de funcionalidades para categorizar, perguntas a serem respondidas ou possíveis duplicatas. Responda com um comentário orientando os próximos passos ou fornecendo assistência imediata.
```

Isso cria um sistema de triagem inteligente que responde a novas issues com orientação contextual.

## Arquitetura de Safe Output

Fluxos de trabalho de IssueOps usam o safe output `add-comment` para garantir a criação segura de comentários com permissões mínimas. O job principal é executado com `contents: read`, enquanto a criação do comentário acontece em um job separado com permissões `issues: write`, sanitizando automaticamente o conteúdo da IA e prevenindo spam:

```yaml wrap
safe-outputs:
  add-comment:
    max: 3                    # Opcional: permitir múltiplos comentários (padrão: 1)
    target: "triggering"      # Padrão: comentar na issue/PR que acionou
```

## Acessando o Contexto da Issue

Acesse o conteúdo sanitizado da issue através de `steps.sanitized.outputs.text`, que combina o título e a descrição enquanto remove riscos de segurança (@mentions, URIs, injeções):

```yaml wrap
Analise esta issue: "${{ steps.sanitized.outputs.text }}"
```

## Padrões Comuns de IssueOps

### Triagem Automatizada de Relatório de Bug

```aw wrap
---
on:
  issues:
    types: [opened]
permissions:
  contents: read
  actions: read
safe-outputs:
  add-labels:
    allowed: [bug, needs-info, enhancement, question, documentation]  # Restringir a labels específicas
    max: 2                                                            # Máximo de 2 labels por issue
---

# Triagem de Relatório de Bug

Analise novas issues e adicione as labels apropriadas: "bug" (com passos de reprodução), "needs-info" (detalhes ausentes), "enhancement" (funcionalidades), "question" ou "documentation" (ajuda/docs). Máximo de 2 labels da lista permitida.
```

## Organizando Trabalho com Sub-Issues

Divida grandes trabalhos em tarefas prontas para agentes usando hierarquias de issue pai-filho. Crie hierarquias com o campo `parent` e IDs temporários, ou vincule issues existentes com `link-sub-issue`:

```aw wrap
---
on:
  command:
    name: plan
safe-outputs:
  create-issue:
    title-prefix: "[tarefa] "
    max: 6
---

# Assistente de Planejamento

Crie uma issue de rastreamento pai, então sub-issues vinculadas via campo parent:

{"type": "create_issue", "temporary_id": "aw_abc123", "title": "Funcionalidade X", "body": "Issue de rastreamento"}
{"type": "create_issue", "parent": "aw_abc123", "title": "Tarefa 1", "body": "Primeira tarefa"}
```

> [!TIP]
> Ocultar sub-issues
> Filtre sub-issues de `/issues` com `no:parent-issue`: `/issues?q=no:parent-issue`

Atribua sub-issues ao Copilot com `assignees: copilot` para execução paralela.
