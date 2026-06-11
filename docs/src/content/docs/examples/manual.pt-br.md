---
title: Fluxos de Trabalho Manuais
description: Fluxos de trabalho sob demanda disparados manualmente via workflow_dispatch - pesquisa, análise e tarefas que você roda quando necessário
sidebar:
  order: 4
---

Fluxos de trabalho manuais rodam apenas quando explicitamente disparados através da UI ou CLI do GitHub Actions. Eles são perfeitos para tarefas sob demanda como pesquisa, análise ou operações que precisam de julgamento humano sobre o momento certo.

## Quando Usar Fluxos de Trabalho Manuais

- **Pesquisa sob demanda**: Pesquise e analise tópicos conforme necessário
- **Operações manuais**: Tarefas que exigem julgamento humano sobre o tempo
- **Testes e depuração**: Rode fluxos de trabalho com entradas personalizadas
- **Tarefas pontuais**: Operações que não se encaixam em uma agenda

## Exemplo de Gatilhos Manuais

```yaml
on:
  workflow_dispatch:
    inputs:
      topic:
        description: 'Tópico de pesquisa'
        required: true
        type: string
```

```yaml
on:
  workflow_dispatch:
    inputs:
      severity:
        description: 'Nível de severidade da issue'
        required: false
        type: choice
        options:
          - low
          - medium
          - high
```

## Acessando Entradas em Fluxos de Trabalho

Use `${{ github.event.inputs.INPUT_NAME }}` para acessar valores de entrada no seu fluxo de trabalho markdown:

```aw wrap
---
on:
  workflow_dispatch:
    inputs:
      topic:
        description: 'Tópico de pesquisa'
        required: true
        type: string
      depth:
        description: 'Profundidade da análise'
        type: choice
        options:
          - brief
          - detailed
        default: brief
permissions:
  contents: read
safe-outputs:
  create-discussion:
---

# Assistente de Pesquisa

Pesquise o tópico: "${{ github.event.inputs.topic }}"

Profundidade da análise: ${{ github.event.inputs.depth }}

Forneça descobertas com base no nível de profundidade solicitado.
```

## Rodando Fluxos de Trabalho Manuais

Via CLI:

```bash
gh aw run workflow
```

Via UI do GitHub Actions:

1. Vá para a aba Actions
2. Selecione o fluxo de trabalho
3. Clique em "Run workflow"
4. Preencha as entradas (se houver)
5. Clique no botão "Run workflow"

## Início Rápido

Adicione um fluxo de trabalho manual ao seu repositório:

```bash
gh aw add-wizard githubnext/agentics/weekly-research
```

Então rode-o:

```bash
gh aw run weekly-research
```
