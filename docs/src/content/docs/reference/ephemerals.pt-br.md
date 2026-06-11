---
title: Efêmeros
description: Funcionalidades para expirar automaticamente recursos de fluxo de trabalho e reduzir o ruído em seus repositórios
sidebar:
  order: 9
---

O GitHub Agentic Workflows inclui diversas funcionalidades "efêmeras" que expiram automaticamente recursos e reduzem o ruído em seus repositórios. Elas controlam custos ao interromper fluxos de trabalho agendados em prazos, fechar automaticamente issues e discussões, ocultar comentários antigos e isolar automação por meio do padrão [SideRepoOps](/gh-aw/patterns/side-repo-ops/).

## Funcionalidades de Expiração

### Workflow Stop-After

Desativa automaticamente o disparo de fluxos de trabalho após um prazo, para controlar custos e evitar execuções indefinidas.

```yaml wrap
on: weekly on monday
  stop-after: "+25h"  # 25 horas a partir do tempo de compilação
```

**Formatos aceitos**:
- **Datas absolutas**: `YYYY-MM-DD`, `MM/DD/YYYY`, `DD/MM/YYYY`, `January 2 2006`, `1st June 2025`, ISO 8601
- **Deltas relativos**: `+7d`, `+25h`, `+1d12h30m` (calculados a partir do tempo de compilação)

A granularidade mínima é de horas - unidades apenas de minutos (ex: `+30m`) não são permitidas. Recompilar o fluxo de trabalho redefine o tempo de interrupção.

No prazo limite, novas execuções são impedidas enquanto as execuções existentes são concluídas. O tempo de interrupção persiste após a recompilação; use `gh aw compile --refresh-stop-time` para redefini-lo. Usos comuns: períodos de teste, funcionalidades experimentais, iniciativas orquestradas e agendas com controle de custos.

Veja [Referência de Triggers](/gh-aw/reference/triggers/#stop-after-configuration-stop-after) para documentação completa.

### Expiração de Safe Output

Fecha automaticamente issues, discussões e pull requests após um período de tempo especificado. Isso gera um fluxo de trabalho de manutenção que é executado automaticamente em intervalos apropriados.

#### Expiração de Issue

```yaml wrap
safe-outputs:
  create-issue:
    expires: 7  # Fecha automaticamente após 7 dias
    labels: [automation, agentic]
```

#### Expiração de Discussão

```yaml wrap
safe-outputs:
  create-discussion:
    expires: 3  # Fecha automaticamente após 3 dias como "OUTDATED"
    category: "general"
```

#### Expiração de Pull Request

```yaml wrap
safe-outputs:
  create-pull-request:
    expires: 14  # Fecha automaticamente após 14 dias (apenas no mesmo repositório)
    draft: true
```

**Formatos suportados**:
- **Inteiro**: Número de dias (ex: `7` = 7 dias)
- **Tempo relativo**: `2h`, `7d`, `2w`, `1m`, `1y`

Horas inferiores a 24 são tratadas como 1 dia de mínimo para cálculo de expiração.

**Frequência do fluxo de trabalho de manutenção**: O fluxo de trabalho `agentics-maintenance.yml` gerado é executado na frequência mínima necessária com base no menor tempo de expiração entre todos os fluxos de trabalho:

| Menor Expiração | Frequência de Manutenção |
|---------------------|----------------------|
| 1 dia ou menos | A cada 2 horas |
| 2 dias | A cada 6 horas |
| 3-4 dias | A cada 12 horas |
| 5+ dias | Diariamente |

**Marcadores de expiração**: O sistema adiciona uma linha de checkbox visível com um comentário XML ao corpo dos itens criados:
```markdown
- [x] expires <!-- gh-aw-expires: 2026-01-14T15:30:00.000Z --> em 14 de jan. de 2026, 15:30 UTC
```

O fluxo de trabalho de manutenção procura itens com esse formato de expiração (checkbox marcado com o comentário XML) e os fecha automaticamente com comentários apropriados e motivos de resolução. Os usuários podem desmarcar a checkbox para evitar a expiração automática.

Veja [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/) para documentação completa.

### Limpeza de Cache-Memory

O fluxo de trabalho de manutenção limpa automaticamente entradas de [cache-memory](/gh-aw/reference/cache-memory/) obsoletas a cada execução agendada. As chaves de cache seguem o padrão `memory-{workflow}-{run-id}`, e o job de limpeza agrupa caches pelo prefixo do fluxo de trabalho, mantém o ID de execução mais recente por grupo e exclui entradas mais antigas. Isso impede que o armazenamento de cache cresça indefinidamente à medida que os fluxos de trabalho são executados repetidamente.

A limpeza inclui reconhecimento de limite de taxa (rate-limit) — ela pausa antecipadamente se o limite de taxa da API do GitHub estiver baixo — e produz uma tabela de resumo do job mostrando quantos caches foram encontrados, mantidos e excluídos.

Você também pode acionar a limpeza manualmente usando a operação `clean_cache_memories` (veja [Operações de manutenção manual](#manual-maintenance-operations) abaixo).

### Operações de Manutenção Manual

O fluxo de trabalho `agentics-maintenance.yml` gerado suporta operações manuais em lote via `workflow_dispatch`. Usuários administradores ou mantenedores podem acionar operações a partir da interface de GitHub Actions ou da CLI. Todas as operações são restritas a funções de administrador e mantenedor e não estão disponíveis em forks.

Operações disponíveis:

| Operação | Descrição |
|-----------|-------------|
| `disable` | Desativa todos os fluxos de trabalho agentic no repositório |
| `enable` | Reativa todos os fluxos de trabalho agentic no repositório |
| `update` | Recompila fluxos de trabalho e cria um PR se os arquivos mudarem |
| `upgrade` | Atualiza fluxos de trabalho agentic para a versão mais recente e cria um PR se os arquivos mudarem |
| `safe_outputs` | Repete safe outputs de uma execução de fluxo de trabalho específica (requer uma URL ou ID de execução) |
| `create_labels` | Cria quaisquer labels de repositório referenciados em safe-outputs que ainda não existam |
| `clean_cache_memories` | Limpa entradas obsoletas de cache-memory (o mesmo que a limpeza agendada automatizada) |
| `validate` | Executa validação completa do fluxo de trabalho com todos os linters e abre uma issue se descobertas forem detectadas |
| `activity_report` | Gera um relatório de atividade do repositório nas últimas 24 horas, semana e mês, e cria uma issue com os resultados |
| `forecast` | Executa uma previsão de uso de token de fluxo de trabalho e cria uma issue com os resultados em JSON |

**Detalhes para operações selecionadas:**

- **`update` / `upgrade`**: Executa `gh aw update` ou `gh aw upgrade`, prepara (stage) arquivos alterados e abre um pull request para revisão. Após o merge, recompile arquivos de bloqueio (lock files) com `gh aw compile`. Veja [Atualizando Fluxos de Trabalho Agentic](/gh-aw/guides/upgrading/) para o processo de atualização manual.
- **`safe_outputs`**: Repete o processamento de safe output de uma execução de fluxo de trabalho anterior. Forneça uma URL de execução ou ID numérico de execução no campo de entrada `run_url`. Útil quando safe outputs não foram aplicados corretamente na execução original.
- **`create_labels`**: Executa `gh aw compile --json --no-emit`, coleta todos os nomes de label exclusivos em fluxos de trabalho e cria os ausentes com cores pastel determinísticas. Requer permissão `issues: write`.
- **`validate`**: Executa `gh aw compile --validate --no-emit --zizmor --actionlint --poutine --verbose`. Se erros ou avisos forem encontrados, cria ou atualiza uma issue do GitHub intitulada `[aw] workflow validation findings` com a saída completa.
- **`activity_report`**: Executa `gh aw logs --format markdown` nas últimas 24 horas, 7 dias e 30 dias (até 1000 execuções cada), então cria uma issue intitulada `[aw] agentic status report` com todas as três seções de intervalo de tempo como blocos `<details>` recolhíveis. Os logs baixados são armazenados em cache em `./.cache/gh-aw/activity-report-logs`. O job tem um timeout de 2 horas e pula a consulta de 30 dias quando a API do GitHub atinge o limite de taxa.
- **`forecast`**: Executa `gh aw forecast --repo <owner/repo> --json`, grava a saída em `./.cache/gh-aw/forecast/report.json`, então cria uma issue intitulada `[aw] workflow forecast report` com o payload JSON incorporado em um bloco cercado.

### Configuração de Manutenção

Você pode personalizar o runner do fluxo de trabalho de manutenção ou desativar a manutenção inteiramente usando o arquivo de configuração `aw.json` em `.github/workflows/aw.json`.

**Personalizar o runner:**

```json
{
  "maintenance": {
    "runs_on": "ubuntu-latest",
    "action_failure_issue_expires": 72
  }
}
```

O campo `runs_on` aceita uma única string ou um array de strings para runners com múltiplas labels (ex: `["self-hosted", "linux"]`). O runner padrão é `ubuntu-slim`.

O campo `action_failure_issue_expires` controla a expiração (em horas) para issues de falha abertas pelo job de conclusão (incluindo issues pai agrupadas quando `group-reports: true`). O padrão é `168` (7 dias).

Veja [Runners Auto-Hospedados](/gh-aw/guides/self-hosted-runners/#configuring-the-maintenance-workflow-runner) para mais detalhes.

**Desativar manutenção inteiramente:**

```json
{
  "maintenance": false
}
```

Quando a manutenção é desativada, o compilador exclui qualquer arquivo `agentics-maintenance.yml` existente e emite um aviso para fluxos de trabalho que usam o campo `expires`, uma vez que a expiração depende do fluxo de trabalho de manutenção para ser executada.

> [!WARNING]
> Desativar a manutenção impede a expiração automática de issues, discussões e pull requests. Qualquer configuração `expires` em seus fluxos de trabalho se tornará um no-op até que a manutenção seja reativada.

### Fechar Issues Antigas

Fecha automaticamente issues antigas com o mesmo marcador de workflow-id ao criar novas. Isso mantém suas issues focadas nas informações mais recentes.

```yaml wrap
safe-outputs:
  create-issue:
    close-older-issues: true  # Fecha relatórios anteriores
```

Quando uma nova issue é criada, até 10 issues mais antigas com o mesmo marcador de workflow-id são fechadas como "not planned" com um comentário contendo link para a nova issue. Requer que `GH_AW_WORKFLOW_ID` esteja definido e permissões de repositório apropriadas. Ideal para relatórios semanais e análises recorrentes onde apenas o resultado mais recente importa.

## Funcionalidades de Redução de Ruído

### Ocultar Comentários Antigos

Minimiza comentários anteriores do mesmo fluxo de trabalho antes de postar novos. Útil para fluxos de trabalho de atualização de status onde apenas as informações mais recentes importam.

```yaml wrap
safe-outputs:
  add-comment:
    hide-older-comments: true
    allowed-reasons: [outdated]  # Opcional: restringir motivos de ocultação
```

Antes de postar, o sistema encontra e minimiza comentários anteriores do mesmo fluxo de trabalho (identificado por `GITHUB_WORKFLOW`). Comentários são ocultados, não excluídos. Use `allowed-reasons` para restringir qual motivo de minimização é aplicado: `spam`, `abuse`, `off_topic`, `outdated` (padrão), `resolved` ou `low_quality`.

Veja [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/#hide-older-comments) para documentação completa.

### Padrão SideRepoOps

Execute fluxos de trabalho agentic a partir de um repositório "side" separado que aponta para sua base de código principal. Isso isola issues, comentários e execuções de fluxo de trabalho gerados por IA de seu repositório principal, mantendo a infraestrutura de automação separada do código de produção.

Veja [SideRepoOps](/gh-aw/patterns/side-repo-ops/) para configuração completa e documentação de uso.

### Sanitização de Texto

Controle quais referências de repositório do GitHub (`#123`, `owner/repo#456`) são permitidas no texto de saída do fluxo de trabalho. Quando configurado, referências a repositórios não listados são escapadas com crases para impedir que o GitHub crie itens na timeline.

```yaml wrap
safe-outputs:
  allowed-github-references: []  # Escapa todas as referências
  create-issue:
    target-repo: "my-org/main-repo"
```

Veja [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/) para documentação completa.

### Usar Discussões em vez de Issues

Para conteúdo efêmero, use discussões em vez de issues. Elas têm menor peso de busca e não desorganizam os boards de projeto, tornando-as ideais para relatórios recorrentes e atualizações de status.

```yaml wrap
safe-outputs:
  create-discussion:
    category: "Status Updates"
    expires: 14  # Fecha após 2 semanas
    close-older-discussions: true  # Substitui relatórios anteriores
```

## Documentação Relacionada

- [Referência de Triggers](/gh-aw/reference/triggers/) - Configuração completa de trigger, incluindo `stop-after`
- [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/) - Todos os tipos de safe output e opções de expiração
- [SideRepoOps](/gh-aw/patterns/side-repo-ops/) - Configuração completa para operações em repositório side
