---
title: Monitoramento com Projetos
description: Utilize GitHub Projects + safe-outputs para rastrear e monitorar itens de trabalho e o progresso de fluxos de trabalho.
---

Use este padrão quando desejar uma “fonte de verdade” durável sobre o que seus fluxos de trabalho agenticos descobriram, decidiram e executaram.

## O que é este padrão

- **Projetos** são o painel: um quadro do GitHub Projects v2 contém issues/PRs e campos personalizados.
- **Monitoramento** é o comportamento: fluxos de trabalho adicionam/atualizam itens continuamente e postam atualizações de status periodicamente.

## Blocos de construção

### 1) Rastrear itens com `update-project`

Habilite a saída segura (safe output) e aponte-a para a URL do seu projeto:

```yaml
safe-outputs:
  update-project:
    project: https://github.com/orgs/myorg/projects/123
    max: 10
    github-token: ${{ secrets.GH_AW_PROJECT_GITHUB_TOKEN }}
```

- Adiciona issues/PRs ao quadro e atualiza campos personalizados.
- Também pode criar visualizações e campos personalizados quando configurado.

Veja a referência completa: [/reference/safe-outputs/#project-board-updates-update-project](/gh-aw/reference/safe-outputs/#project-board-updates-update-project)

### 2) Postar resumos de execução com `create-project-status-update`

Use atualizações de status de projeto para comunicar o progresso e os próximos passos:

```yaml
safe-outputs:
  create-project-status-update:
    project: https://github.com/orgs/myorg/projects/123
    max: 1
    github-token: ${{ secrets.GH_AW_PROJECT_GITHUB_TOKEN }}
```

Isso é útil para fluxos de trabalho agendados (diários/semanais) ou fluxos de trabalho orquestradores.

Veja a referência completa: [/reference/safe-outputs/#project-status-updates-create-project-status-update](/gh-aw/reference/safe-outputs/#project-status-updates-create-project-status-update)

### 3) Correlacionar trabalho com um campo de ID de Rastreador (Tracker Id)

Se desejar correlacionar múltiplas execuções, adicione um campo personalizado como **Tracker Id** (texto) e preencha-o a partir do prompt/saída do seu fluxo de trabalho (por exemplo, um ID de execução, número de issue ou chave de “iniciativa”).

## Problemas de falha na execução

Quando uma execução de fluxo de trabalho falha, o sistema automaticamente posta uma notificação de falha na issue ou pull request que a disparou. Para rastrear falhas como issues pesquisáveis do GitHub, habilite `create-issue` em `safe-outputs`:

```yaml wrap
safe-outputs:
  create-issue:
    title-prefix: "[falhou] "
    labels: [automacao, falhou]
```

O corpo da issue inclui o nome do fluxo de trabalho, a URL da execução e o status da falha, facilitando a localização e triagem de falhas recorrentes.

### Agrupar falhas como sub-issues

Quando múltiplas execuções de fluxo de trabalho falham, a opção `group-reports` vincula cada relatório de falha como uma sub-issue sob uma issue pai compartilhada intitulada "[aw] Failed runs". Isso é útil para fluxos de trabalho agendados ou de alta frequência onde as falhas podem se acumular.

```yaml wrap
safe-outputs:
  create-issue:
    title-prefix: "[falhou] "
    labels: [automacao, falhou]
  group-reports: true   # Agrupar relatórios de falha sob uma issue pai compartilhada (padrão: false)
```

Quando `group-reports` está habilitado:

- Uma issue pai "[aw] Failed runs" é criada e gerenciada automaticamente.
- Cada relatório de execução com falha é vinculado como uma sub-issue sob a pai.
- Até 64 sub-issues são rastreadas por issue pai.

Veja a referência completa: [/reference/safe-outputs/#group-reports-group-reports](/gh-aw/reference/safe-outputs/#group-reports-group-reports)

## Relatórios de execução no-op

Quando um agente determina que nenhuma ação é necessária (por exemplo, nenhuma issue foi encontrada), ele gera uma mensagem no-op. Por padrão, essa mensagem é postada como um comentário na issue ou pull request que a disparou, mantendo um registro visível das execuções que intencionalmente não fizeram nada.

Para desabilitar a postagem de mensagens no-op como comentários de issue:

```yaml wrap
safe-outputs:
  create-issue:
  noop:
    report-as-issue: false  # Desabilitar a postagem de mensagens noop como comentários de issue
```

As mensagens no-op ainda aparecem no resumo do passo do fluxo de trabalho mesmo quando `report-as-issue` é `false`.

Para desabilitar a saída no-op completamente:

```yaml wrap
safe-outputs:
  create-issue:
  noop: false   # Desabilitar saída noop completamente
```

Veja a referência completa: [/reference/safe-outputs/#no-op-logging-noop](/gh-aw/reference/safe-outputs/#no-op-logging-noop)

## Monitoramento operacional

Use `gh aw status` para ver quais fluxos de trabalho estão habilitados e seu estado de execução mais recente.

Para uma investigação mais profunda, os comandos de auditoria são a principal ferramenta de monitoramento para fluxos de trabalho agenticos:

- `gh aw audit <run-id>` — relatório de execução única com uso de ferramentas, falhas de MCP, atividade de firewall e métricas de custo
- `gh aw audit <run-id-1> <run-id-2>` — compara duas execuções para detectar regressões comportamentais ou novos acessos à rede (passe IDs adicionais para comparar a base contra múltiplas execuções)
- `gh aw logs --format markdown [workflow]` — relatório de segurança e desempenho entre execuções para monitoramento de tendências

```bash
# Auditar a execução mais recente
gh aw audit 12345678

# Comparar duas execuções em busca de regressões
gh aw audit 12345678 12345679

# Comparar a base contra múltiplas execuções ao mesmo tempo
gh aw audit 12345678 12345679 12345680

# Relatório de tendência através das últimas 10 execuções de um fluxo de trabalho
gh aw logs my-workflow --format markdown --count 10
```

> [!TIP]
> Use `gh aw logs --format markdown` dentro de um agente de fluxo de trabalho agendado para automatizar o monitoramento de tendências e identificar regressões de custo ou segurança sem intervenção manual.

Veja [Comandos de Auditoria](/gh-aw/reference/audit/) para documentação completa de flags, e [Referência da CLI](/gh-aw/setup/cli/) para todos os comandos disponíveis.
