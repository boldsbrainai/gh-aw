---
title: Atualizando Fluxos de Trabalho Agenticos
description: Guia passo a passo para atualizar seu repositório para a versão mais recente dos fluxos de trabalho agenticos, incluindo atualização de extensões, aplicação de codemods, compilação de fluxos de trabalho e validação de alterações.
sidebar:
  order: 100
---

Este guia orienta você na atualização dos fluxos de trabalho agenticos. `gh aw upgrade` lida com todo o processo: atualização do arquivo do agente dispatcher, migração de sintaxe de fluxo de trabalho obsoleta e recompilação de todos os fluxos de trabalho.

> [!TIP]
> Atualização Rápida
>
> Para a maioria dos usuários, a atualização é um comando único:
>
> ```bash wrap
> gh aw upgrade
> ```
>
> Isso atualiza arquivos de agente, aplica codemods e compila todos os fluxos de trabalho.

## Pré-requisitos

Antes de atualizar, certifique-se de ter o GitHub CLI (`gh`) v2.0.0+, a extensão gh-aw mais recente e um diretório de trabalho limpo em seu repositório Git. Verifique com `gh --version`, `gh extension list | grep gh-aw` e `git status`.

Crie um branch de backup antes de atualizar para que você possa recuperar caso algo dê errado:

```bash wrap
git checkout -b backup-antes-da-atualizacao
git checkout -  # retorne para o seu branch anterior
```

## Passo 1: Atualizar a Extensão

Atualize a extensão `gh aw` para obter os recursos e codemods mais recentes:

```bash wrap
gh extension upgrade gh-aw
```

Verifique sua versão com `gh aw version` e compare com a [última versão](https://github.com/github/gh-aw/releases). Se encontrar problemas, tente uma reinstalação limpa com `gh extension remove gh-aw` seguido por `gh extension install github/gh-aw`.

## Passo 2: Executar o Comando de Atualização

Execute o comando de atualização a partir da raiz do seu repositório:

```bash wrap
gh aw upgrade
```

Este comando realiza três operações principais:

### 2.1 Atualiza o Arquivo do Agente Dispatcher

Atualiza `.github/agents/agentic-workflows.agent.md` para o modelo mais recente. Arquivos de prompt de fluxo de trabalho (`.github/aw/*.md`) são resolvidos diretamente do GitHub pelo agente — eles não são mais gerenciados pela CLI.

### 2.2 Aplica Codemods a Todos os Fluxos de Trabalho

A atualização aplica automaticamente codemods para corrigir campos obsoletos em todos os arquivos de fluxo de trabalho (`.github/workflows/*.md`).

### 2.3 Compila Todos os Fluxos de Trabalho

A atualização compila automaticamente todos os fluxos de trabalho para gerar ou atualizar arquivos `.lock.yml`, garantindo que estejam prontos para executar no GitHub Actions.

### Opções de Comando

```bash wrap
gh aw upgrade                       # atualiza arquivos de agente + codemods + compila
gh aw upgrade -v                    # saída detalhada (verbose)
gh aw upgrade --no-fix              # pula codemods e compilação
gh aw upgrade --dir custom/workflows
```

## Passo 3: Revisar as Alterações

Execute `git diff .github/workflows/` para verificar as alterações. Migrações típicas incluem `sandbox: false` → `sandbox.agent: false`, `app:` → `github-app:`, `safe-inputs:` → `mcp-scripts:`, `daily at` → `daily around`, e remoção de campos obsoletos `network.firewall` e `mcp-scripts.mode`.

## Passo 4: Commitar e Dar Push

Prepare (stage) e commite suas alterações:

```bash wrap
git add .github/workflows/ .github/agents/
git commit -m "Atualizar fluxos de trabalho agenticos para a versão mais recente"
git push origin main
```

Sempre commite arquivos `.md` e `.lock.yml` juntos.

## Resolução de Problemas

**A atualização da extensão falha:** Tente uma reinstalação limpa com `gh extension remove gh-aw && gh extension install github/gh-aw`.

**Codemods não aplicados:** Aplique manualmente com `gh aw fix --write -v`.

**Erros de compilação:** Revise os erros com `gh aw compile meu-fluxo-de-trabalho --validate` e corrija a sintaxe YAML nos arquivos de origem.

**Fluxos de trabalho não executando:** Verifique se os arquivos `.lock.yml` estão commitados, verifique o status com `gh aw status` e confirme se os segredos são válidos com `gh aw secrets bootstrap`.

**Alterações que quebram o fluxo (Breaking changes):** Reverta com `git checkout backup-antes-da-atualizacao` e revise as [notas de lançamento](https://github.com/github/gh-aw/releases).

## Tópicos Avançados

**Atualizando entre versões:** Revise o [changelog](https://github.com/github/gh-aw/blob/main/CHANGELOG.md) para alterações cumulativas ao atualizar entre múltiplos lançamentos.

Veja o [guia de resolução de problemas](/gh-aw/troubleshooting/common-issues/) se você encontrar problemas.
