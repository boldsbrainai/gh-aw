---
title: Configuração Corporativa
description: Configure o GitHub Agentic Workflows para GitHub Enterprise Server (GHES) e GitHub Enterprise Cloud (GHEC), incluindo compatibilidade de artefatos e configuração CLI.
sidebar:
  order: 51
---

# Configuração Corporativa

Esta página aborda opções de configuração específicas para implantações de GitHub Enterprise Server (GHES) e GitHub Enterprise Cloud (GHEC).

## Compatibilidade com o GitHub Enterprise Server (GHES)

### Modo de compatibilidade de artefato

Instâncias GHES executando versões anteriores ao suporte de `@actions/artifact` v2.0.0 não podem usar `actions/upload-artifact@v4+` ou `actions/download-artifact@v4+`. Tentar executar fluxos de trabalho compilados nessas instâncias produz um `GHESNotSupportedError`.

O gh-aw inclui um modo de compatibilidade GHES que instrui o compilador a emitir `upload-artifact@v3.2.2` e `download-artifact@v3.1.0` em vez das versões v4+ mais recentes.

#### Habilitar via `aw.json` (recomendado)

Defina `ghes: true` em `.github/workflows/aw.json` para aplicar a compatibilidade GHES a cada fluxo de trabalho compilado no repositório:

```json
{
  "ghes": true
}
```

#### Detecção automática com `gh aw init`

Executar `gh aw init` dentro de um repositório GHES detecta automaticamente a implantação e escreve `ghes: true` em `.github/workflows/aw.json`. Nenhuma configuração manual é necessária.

#### Habilitar via flag CLI

Passe `--ghes` para `gh aw compile` para uma compilação única sem modificar `aw.json`:

```bash
gh aw compile --ghes meu-fluxo-de-trabalho.md
```

> [!NOTE]
> A flag `--ghes` afeta apenas a compilação atual. Use `aw.json` para aplicar a compatibilidade GHES permanentemente em todos os fluxos de trabalho no repositório.

## Configuração da CLI do GitHub Enterprise Server

Para configuração da CLI `gh`, autenticação de host e configuração de `GH_HOST` no GHES, veja [Suporte ao GitHub Enterprise Server](/gh-aw/setup/cli/#github-enterprise-server-support) na referência da CLI.

## Motor Copilot no GHES

Para pré-requisitos específicos do Copilot, requisitos de licenciamento e configuração de firewall no GHES, veja [Pré-requisitos do Motor Copilot no GHES](/gh-aw/troubleshooting/common-issues/#copilot-engine-prerequisites-on-ghes).
