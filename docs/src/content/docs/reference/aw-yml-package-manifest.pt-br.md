---
title: Manifesto de pacote aw.yml
description: Referência para o manifesto de pacote aw.yml usado pelo gh aw add e gh aw compile.
sidebar:
  order: 320
---

Use `aw.yml` para descrever um pacote de fluxo de trabalho agentic instalável.
`gh aw add` usa este manifesto ao instalar pacotes, e
`gh aw compile` valida manifestos na raiz do repositório antes da compilação.

Para a definição normativa do formato de arquivo, veja a
[especificação do manifesto de pacote de repositório aw.yml](/gh-aw/reference/repository-package-manifest-specification/).

## Formatos de referência de pacote

Referências de repositório suportam duas formas:

- `PROPRIETÁRIO/REPO`
- `PROPRIETÁRIO/REPO/CAMINHO/PARA/PACOTE`

A raiz do pacote é a pasta que contém `aw.yml`.

## Campos

| Campo | Tipo | Obrigatório | Notas |
| --- | --- | --- | --- |
| `manifest-version` | string | Não | Valor atual suportado: `"1"`. Assume `"1"` quando omitido. |
| `min-version` | string | Não | Versão mínima compatível do `gh aw` na forma `vMAJOR.minor.patch`, como `v0.38.0`. |
| `name` | string | Sim | Nome do pacote legível por humanos. Deve ser não vazio após remover espaços em branco. |
| `emoji` | string | Não | Emoji opcional do pacote para exibição nos metadados do pacote. |
| `description` | string | Não | Descrição opcional do pacote. `gh aw add` avisa quando excede 255 caracteres. |
| `files` | array de strings | Não | Arquivos markdown relativos à raiz do pacote em `workflows/` ou `.github/workflows/`. |

## Fluxos de trabalho instaláveis

Se `files` estiver presente, entradas válidas tornam-se o pacote de instalação.

Se `files` for omitido, ou se não restarem entradas válidas após a filtragem,
`gh aw add` descobre arquivos markdown instaláveis em:

- `workflows/`
- `.github/workflows/`

Se nenhum arquivo de fluxo de trabalho instalável for resolvido, a validação falha.

## Documentação do pacote

A documentação do pacote deve ser `README.md` na raiz do pacote.
O manifesto não suporta um campo `docs`.

A falta de `README.md` faz com que a validação do pacote falhe.

## Exemplo

```yaml
manifest-version: "1"
min-version: v0.38.0
name: Repo Assist
emoji: 🤖
description: Automação amigável de repositório para revisão e triagem de issues
files:
  - workflows/review.md
  - .github/workflows/nightly-review.md
```
