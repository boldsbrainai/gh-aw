---
title: LabelOps
description: Fluxos de trabalho acionados por mudanças de label - automatize ações quando labels específicas são adicionadas ou removidas
sidebar:
  badge: { text: 'Disparado por evento', variant: 'success' }
---

LabelOps usa labels do GitHub como gatilhos de fluxo de trabalho, metadados e marcadores de estado. O GitHub Agentic Workflows suporta duas abordagens distintas para gatilhos baseados em label: `label_command` para ativação de comando de disparo único, e filtragem por `names:` para reconhecimento de estado de label persistente.

## Gatilho Label Command

O gatilho `label_command` trata uma label como um comando de disparo único: aplicar a label dispara o fluxo de trabalho, e a label é **automaticamente removida** para que possa ser aplicada novamente para re-acionar. Esta é a escolha certa quando você deseja que uma label signifique "faça isso agora" em vez de "este item tem esta propriedade".

```aw wrap
---
on:
  label_command: deploy
permissions:
  contents: read
safe-outputs:
  add-comment:
    max: 1
---

# Deploy de Preview

Uma label `deploy` foi aplicada a este pull request. Construa e implante um ambiente de preview e poste a URL como um comentário.

O nome da label correspondente está disponível como `${{ needs.activation.outputs.label_command }}` se necessário para distinguir entre múltiplos comandos de label.
```

Após a ativação, a label `deploy` é removida do pull request, para que um revisor possa aplicá-la novamente para acionar outro deploy sem qualquer etapa de limpeza.

### Sintaxe

`label_command` aceita uma string abreviada, um mapa com um nome único, ou um mapa com múltiplos nomes e uma restrição opcional de `events`:

```yaml
# Abreviado — dispara em issues, pull_request e discussion
on: "label-command deploy"

# Mapa com um único nome
on:
  label_command: deploy

# Restringir a tipos de evento específicos
on:
  label_command:
    name: deploy
    events: [issues, pull_request]

# Múltiplos nomes de label
on:
  label_command:
    names: [deploy, redeploy]
    events: [pull_request]

# Manter label após ativação (estado persistente, não comando de disparo único)
on:
  label_command:
    name: in-review
    remove_label: false
```

O campo `remove_label` (booleano, padrão `true`) controla se a label correspondente é removida após a ativação do fluxo de trabalho. Defina como `false` quando a label representar um estado persistente em vez de um comando transiente — por exemplo, para marcar que um item está sendo processado sem consumir a label.

O compilador gera eventos `issues`, `pull_request` e/ou `discussion` com `types: [labeled]`, filtrados para os nomes de label. Ele também adiciona um gatilho `workflow_dispatch` com uma entrada `item_number` para que você possa testar o fluxo de trabalho manualmente sem aplicar uma label real.

### Acessando a label correspondente

A label que acionou o fluxo de trabalho é exposta como uma saída do job de ativação:

```
${{ needs.activation.outputs.label_command }}
```

Isso é útil quando um fluxo de trabalho lida com múltiplos comandos de label e precisa ramificar com base em qual foi aplicada.

### Combinando com comandos slash

`label_command` pode ser combinado com `slash_command:` no mesmo fluxo de trabalho. Os dois gatilhos são unidos por um OU (OR) — o fluxo de trabalho ativa quando qualquer uma das condições é atendida:

```yaml
on:
  slash_command: deploy
  label_command:
    name: deploy
    events: [pull_request]
```

Isso permite que um fluxo de trabalho seja acionado tanto por um comentário `/deploy` quanto pela aplicação de uma label `deploy`, compartilhando a mesma lógica de agente.

## Filtragem por Label

Use filtragem por `names:` quando desejar que o fluxo de trabalho seja executado sempre que uma label estiver presente em um item e a label deva permanecer anexada. Isso é adequado para monitorar o estado da label em vez de reagir a um comando transiente.

O GitHub Agentic Workflows permite que você filtre eventos `labeled` e `unlabeled` para acionar apenas para nomes de label específicos usando o campo `names`:

```aw wrap
---
on:
  issues:
    types: [labeled]
    names: [bug, critical, security]
permissions:
  contents: read
  actions: read
safe-outputs:
  add-comment:
    max: 1
---

# Manipulador de Issue Crítica

Quando uma label crítica é adicionada a uma issue, analise a severidade e forneça orientação de triagem imediata.

Verifique a issue para:
- Escopo de impacto e usuários afetados
- Passos de reprodução
- Dependências ou sistemas relacionados
- Nível de prioridade recomendado

Responda com um comentário delineando os próximos passos e ações recomendadas.
```

Este fluxo de trabalho ativa apenas quando as labels `bug`, `critical` ou `security` são adicionadas a uma issue, não para outras mudanças de label. As labels permanecem na issue após a execução do fluxo de trabalho.

### Escolhendo entre `label_command` e filtragem por `names:`

| | `label_command` | Filtragem por `names:` |
|---|---|---|
| Ciclo de vida da label | Removida automaticamente após o gatilho | Permanece no item |
| Re-acionável | Sim — reaplique a label | Apenas no próximo evento `labeled` |
| Uso típico | Comandos "faça isso agora" | Roteamento baseado em estado |
| Itens suportados | Issues, pull requests, discussões | Issues, pull requests |

### Sintaxe de Filtro de Label

O campo `names` aceita uma label única (`names: urgent`) ou um array (`names: [priority, needs-review, blocked]`). Funciona com eventos `issues` e `pull_request`, e o campo é compilado em uma expressão condicional `if` no YAML final do fluxo de trabalho.

## Padrões Comuns de LabelOps

| Padrão | Labels de Gatilho | Resposta do Agente |
|---------|---------------|----------------|
| **Escalonamento de Prioridade** | `P0`, `critical`, `urgent` | Analisar severidade, notificar líderes, fornecer orientação de SLA |
| **Triagem Baseada em Label** | `needs-triage`, `triaged` | Sugerir categorização, prioridade, componentes afetados |
| **Automação de Segurança** | Labels de segurança | Verificar riscos de divulgação, acionar processo de revisão |
| **Gerenciamento de Release** | Labels de release | Analisar cronograma, identificar bloqueios, rascunhar notas de release |

## LabelOps Impulsionado por IA

- **Sugestões Automáticas de Label**: Analise issues e aplique labels para tipo, prioridade e componente. Use `safe-outputs.add-labels.allowed` para restringir quais labels podem ser aplicadas automaticamente.
- **Auto-Labeling de Componente**: Identifique componentes afetados a partir de caminhos de arquivo, APIs e elementos da UI, então aplique labels de componente relevantes.
- **Consolidação de Label**: Agende auditorias para identificar labels duplicadas, não utilizadas e com nomes inconsistentes.

## Melhores Práticas

- Use nomes de label específicos (`ready-for-review` não `ready`) para evitar gatilhos não intencionais.
- Documente significados de label em um arquivo LABELS.md ou nas descrições de label do GitHub.
- Limite o escopo de automação com labels de adesão como `automation-enabled`.
- Use safe outputs para todas as operações de escrita para manter a segurança.

## Recursos Adicionais

- [Eventos de Gatilho](/gh-aw/reference/triggers/) - Configuração completa de gatilho incluindo filtragem por label
- [IssueOps](/gh-aw/patterns/issue-ops/) - Saiba mais sobre fluxos de trabalho acionados por issue
- [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/) - Manuseio seguro de saída
- [Referência de Frontmatter](/gh-aw/reference/frontmatter/) - Opções completas de configuração de fluxo de trabalho
