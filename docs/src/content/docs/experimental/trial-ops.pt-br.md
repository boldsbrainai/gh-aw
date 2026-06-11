---
title: TrialOps
description: Teste e valide fluxos de trabalho agenticos em repositórios de teste isolados antes de implantar em produção
sidebar:
  badge: { text: 'Testing', variant: 'tip' }
---

O TrialOps usa repositórios de teste temporários para validar e iterar com segurança em fluxos de trabalho antes da implantação em repositórios de destino. O comando `trial` cria repositórios privados isolados onde os fluxos de trabalho são executados e capturam saídas seguras (issues, PRs, comentários) sem afetar sua base de código real.

## Como o modo Trial funciona

```bash
gh aw trial githubnext/agentics/weekly-research
```

A CLI cria um repositório privado temporário (padrão: `gh-aw-trial`), instala e executa o fluxo de trabalho via `workflow_dispatch`. Os resultados são salvos localmente em `trials/weekly-research.DATETIME-ID.json`, no repositório de teste no GitHub e resumidos no console.

## Modos de repositório

| Modo | Flag | Descrição |
|------|------|-------------|
| Padrão | (nenhum) | `github.repository` aponta para seu repo; saídas vão para o repo de teste |
| Direto | `--repo myorg/test-repo` | Executa no repo especificado; cria issues/PRs reais lá |
| Lógico | `--logical-repo myorg/target-repo` | Simula a execução contra o repo especificado; saídas no repo de teste |
| Clone | `--clone-repo myorg/real-repo` | Clona o conteúdo do repo para que os fluxos de trabalho possam analisar o código real |

## Uso básico

### Modo de simulação (Dry-Run)

Visualize o que aconteceria sem executar fluxos de trabalho ou criar repositórios:

```bash
gh aw trial ./my-workflow.md --dry-run
```

### Fluxo de trabalho único

```bash
gh aw trial githubnext/agentics/weekly-research  # Do GitHub
gh aw trial ./my-workflow.md                      # Arquivo local
```

### Vários fluxos de trabalho

Compare fluxos de trabalho lado a lado com resultados combinados:

```bash
gh aw trial githubnext/agentics/daily-plan githubnext/agentics/weekly-research
```

Saídas: arquivos de resultado individuais mais `trials/combined-results.DATETIME.json`.

### Tentativas repetidas

Teste a consistência executando várias vezes:

```bash
gh aw trial githubnext/agentics/my-workflow --repeat 3
```

### Repositório de teste personalizado

```bash
gh aw trial githubnext/agentics/my-workflow --host-repo my-custom-trial
gh aw trial ./my-workflow.md --host-repo .  # Usar repo atual
```

## Padrões avançados

### Contexto de Issue

Forneça contexto de issue para fluxos de trabalho disparados por issue:

```bash
gh aw trial githubnext/agentics/triage-workflow \
  --trigger-context "https://github.com/myorg/repo/issues/123"
```

### Acrescentar instruções

Teste respostas de fluxo de trabalho a restrições adicionais sem modificar a fonte:

```bash
gh aw trial githubnext/agentics/my-workflow \
  --append "Foque em problemas de segurança e crie relatórios detalhados."
```

### Opções de limpeza

```bash
gh aw trial ./my-workflow.md --delete-host-repo-after        # Excluir após a conclusão
gh aw trial ./my-workflow.md --force-delete-host-repo-before # Limpar antes de executar
```

## Entendendo os resultados do Trial

Os resultados são salvos em `trials/*.json` com as execuções do fluxo de trabalho, issues, PRs e comentários visíveis nas abas de Actions e Issues do repositório de teste.

**Estrutura do arquivo de resultado:**

```json
{
  "workflow_name": "weekly-research",
  "run_id": "12345678",
  "safe_outputs": {
    "issues_created": [{
      "number": 5,
      "title": "Research quantum computing trends",
      "url": "https://github.com/user/gh-aw-trial/issues/5"
    }]
  },
  "agentic_run_info": {
    "duration_seconds": 45,
    "token_usage": 2500
  }
}
```

**Indicadores de sucesso:** Check verde, saídas esperadas criadas, sem erros nos logs.

**Problemas comuns:**

- **Falha no workflow dispatch** - Adicione o gatilho `workflow_dispatch`
- **Sem saídas seguras** - Configure saídas seguras no fluxo de trabalho
- **Erros de permissão** - Verifique as chaves de API
- **Timeout** - Use `--timeout 60` (minutos)

## Comparando vários fluxos de trabalho

Execute vários fluxos de trabalho para comparar qualidade, quantidade, desempenho e consistência:

```bash
gh aw trial v1.md v2.md v3.md --repeat 2
cat trials/combined-results.*.json | jq '.results[] | {workflow: .workflow_name, issues: .safe_outputs.issues_created | length}'
```

## Documentação relacionada

- [SideRepoOps](/gh-aw/patterns/side-repo-ops/) - Execute fluxos de trabalho de repositórios separados
- [MultiRepoOps](/gh-aw/patterns/multi-repo-ops/) - Coordene entre vários repositórios
- [Orchestration](/gh-aw/patterns/orchestration/) - Orquestre iniciativas de várias issues
- [CLI Commands](/gh-aw/setup/cli/) - Referência completa da CLI
- [Safe Outputs Reference](/gh-aw/reference/safe-outputs/) - Opções de configuração
- [Workflow Triggers](/gh-aw/reference/triggers/) - Incluindo workflow_dispatch
- [Security Best Practices](/gh-aw/introduction/architecture/) - Autenticação e segurança
