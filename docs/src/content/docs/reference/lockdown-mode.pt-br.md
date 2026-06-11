---
title: Modo Lockdown
description: O modo lockdown do GitHub foi substituído pela Filtragem de Integridade, que oferece filtragem de conteúdo mais refinada com base na confiança do autor e no status de merge.
sidebar:
  order: 660
---

> [!NOTE]
> **O Modo Lockdown do GitHub foi substituído pela Filtragem de Integridade do GitHub.** Use a [Filtragem de Integridade](/gh-aw/reference/integrity/) em vez disso. A filtragem de integridade oferece controle mais refinado sobre qual conteúdo o agente pode ver, com base na confiança do autor e status de merge, e funciona sem exigir autenticação adicional.

## Migrando para a Filtragem de Integridade

Substitua `lockdown: true` por `min-integrity: approved`:

```yaml wrap
# Antes (obsoleto)
tools:
  github:
    lockdown: true

# Depois (recomendado)
tools:
  github:
    min-integrity: approved
```

Substitua `lockdown: false` por `min-integrity: none`:

```yaml wrap
# Antes (obsoleto)
tools:
  github:
    lockdown: false

# Depois (recomendado)
tools:
  github:
    min-integrity: none
```

## Veja Também

- [Filtragem de Integridade](/gh-aw/reference/integrity/) — Referência completa para `min-integrity`, níveis de integridade, bloqueio de usuário e labels de aprovação
- [Referência de Ferramentas GitHub](/gh-aw/reference/github-tools/) — Configuração completa de `tools.github`
