---
title: TrialOps
description: Teste e valide fluxos de trabalho agenticos em repositórios de teste isolados antes de implantar em produção
sidebar:
  badge: { text: 'Testing', variant: 'tip' }
---

O TrialOps utiliza repositórios de teste temporários para validar e iterar com segurança em fluxos de trabalho antes da implantação em repositórios de destino. O comando `trial` cria repositórios privados isolados onde os fluxos de trabalho executam e capturam saídas seguras (issues, PRs, comentários) sem afetar sua base de código real.

## Como o Modo Trial Funciona

```bash
gh aw trial githubnext/agentics/weekly-research
```

A CLI cria um repositório privado temporário (padrão: `gh-aw-trial`), instala e executa o fluxo de trabalho via `workflow_dispatch`. Os resultados são salvos localmente em `trials/weekly-research.DATETIME-ID.json`, no repositório de teste no GitHub e resumidos no console.

## Modos de Repositório

| Modo | Flag | Descrição |
|------|------|-------------|
| Padrão | (nenhum) | `github.repository` aponta para seu repo; saídas vão para o repo de teste |
| Direto | `--repo meuorg/repo-teste` | Executa no repo especificado; cria issues/PRs reais lá |
| Lógico | `--logical-repo meuorg/repo-destino` | Simula a execução contra o repo especificado; saídas no repo de teste |
| Clone | `--clone-repo meuorg/repo-real` | Clona o conteúdo do repo para que os fluxos de trabalho possam analisar o código real |

## Uso Básico

### Modo Dry-Run (Simulação)

Visualize o que aconteceria sem executar fluxos de trabalho ou criar repositórios:

```bash
gh aw trial ./meu-fluxo-de-trabalho.md --dry-run
```

### Fluxo de Trabalho Único

```bash
gh aw trial githubnext/agentics/weekly-research  # Do GitHub
gh aw trial ./meu-fluxo-de-trabalho.md           # Arquivo local
```

### Múltiplos Fluxos de Trabalho

Compare fluxos de trabalho lado a lado com resultados combinados:

```bash
gh aw trial githubnext/agentics/daily-plan githubnext/agentics/weekly-research
```

Saídas: arquivos de resultados individuais mais `trials/combined-results.DATETIME.json`.

### Ensaios Repetidos

Teste a consistência executando múltiplas vezes:

```bash
gh aw trial githubnext/agentics/meu-fluxo-de-trabalho --repeat 3
```

### Repositório de Teste Personalizado

```bash
gh aw trial githubnext/agentics/meu-fluxo-de-trabalho --host-repo meu-teste-personalizado
gh aw trial ./meu-fluxo-de-trabalho.md --host-repo .  # Use o repo atual
```

## Padrões Avançados

### Contexto de Issue

Forneça contexto de issue para fluxos de trabalho disparados por issue:

```bash
gh aw trial githubnext/agentics/triage-workflow \
  --trigger-context "https://github.com/meuorg/repo/issues/123"
```

### Acrescentar Instruções

Teste respostas de fluxo de trabalho a restrições adicionais sem modificar a fonte:

```bash
gh aw trial githubnext/agentics/meu-fluxo-de-trabalho \
  --append "Foque em problemas de segurança e crie relatórios detalhados."
```

### Opções de Limpeza

```bash
gh aw trial ./meu-fluxo-de-trabalho.md --delete-host-repo-after        # Deletar após conclusão
gh aw trial ./meu-fluxo-de-trabalho.md --force-delete-host-repo-before # Limpar antes de executar
```

## Entendendo os Resultados do Trial

Os resultados são salvos em `trials/*.json` com execuções de fluxo de trabalho, issues, PRs e comentários visíveis nas abas Actions e Issues do repositório de teste.

**Estrutura do arquivo de resultado:**

```json
{
  "workflow_name": "weekly-research",
  "run_id": "12345678",
  "safe_outputs": {
    "issues_created": [{
      "number": 5,
      "title": "Pesquisar tendências de computação quântica",
      "url": "https://github.com/usuario/gh-aw-trial/issues/5"
    }]
  },
  "agentic_run_info": {
    "duration_seconds": 45,
    "token_usage": 2500
  }
}
```

**Indicadores de sucesso:** Checkmark verde, saídas esperadas criadas, sem erros nos logs.

**Problemas comuns:**

- **Falha no disparo do fluxo de trabalho (workflow dispatch)** - Adicione o gatilho `workflow_dispatch`
- **Sem saídas seguras** - Configure saídas seguras no fluxo de trabalho
- **Erros de permissão** - Verifique as chaves de API
- **Tempo limite (Timeout)** - Use `--timeout 60` (minutos)

## Comparando Múltiplos Fluxos de Trabalho

Execute múltiplos fluxos de trabalho para comparar qualidade, quantidade, desempenho e consistência:

```bash
gh aw trial v1.md v2.md v3.md --repeat 2
cat trials/combined-results.*.json | jq '.results[] | {workflow: .workflow_name, issues: .safe_outputs.issues_created | length}'
```

## Documentação Relacionada

- [SideRepoOps](/gh-aw/patterns/side-repo-ops/) - Executar fluxos de trabalho de repositórios separados
- [MultiRepoOps](/gh-aw/patterns/multi-repo-ops/) - Coordenar através de múltiplos repositórios
- [Orquestração](/gh-aw/patterns/orchestration/) - Orquestrar iniciativas de múltiplas issues
- [Comandos da CLI](/gh-aw/setup/cli/) - Referência completa da CLI
- [Referência de Saídas Seguras](/gh-aw/reference/safe-outputs/) - Opções de configuração
- [Gatilhos de Fluxo de Trabalho](/gh-aw/reference/triggers/) - Incluindo workflow_dispatch
- [Melhores Práticas de Segurança](/gh-aw/introduction/architecture/) - Autenticação e segurança
