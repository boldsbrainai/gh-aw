---
title: Sub-Agentes Inline
description: Defina sub-agentes diretamente dentro de um arquivo markdown de fluxo de trabalho usando um delimitador de cabeçalho de nível 2.
sidebar:
  order: 645
---

Um sub-agente inline é uma definição de agente nomeada incorporada diretamente em um arquivo markdown de fluxo de trabalho. Em vez de criar um arquivo separado em `.github/agents/`, você define o frontmatter e as instruções do agente em uma seção dedicada do mesmo arquivo de fluxo de trabalho.

Sub-agentes inline são habilitados por padrão. `features.inline-agents` está obsoleto/sem efeito, e `inline-sub-agents: false` é recusado no momento da compilação.

## Sintaxe

Inicie um bloco de sub-agente com um cabeçalho de nível 2 na seguinte forma:

```markdown
## agent: `nome`
```

O bloco continua até o próximo cabeçalho `##` ou fim do arquivo. Não há um marcador de fechamento explícito.

### Restrições de nome

- Deve começar com uma letra minúscula (`a–z`)
- Pode conter apenas `a–z`, `0–9`, `_` e `-`
- Exemplos: `file-summarizer`, `code_reviewer`, `pr-analyst`

### Estrutura

Cada bloco de sub-agente contém:

1. **Frontmatter YAML** (opcional) — delimitado por `---`
2. **Instruções** — prompt em linguagem natural para o agente

```markdown
## agent: `file-summarizer`
---
model: claude-haiku-4.5
description: Resume o conteúdo de um arquivo em algumas frases concisas
---
Você é um assistente de sumarização de arquivos. Quando receber um caminho de arquivo, leia o arquivo
e retorne um breve resumo (2–4 frases) descrevendo seu propósito e conteúdo
principal. Seja conciso e factual.
```

## Campos de Frontmatter

| Campo | Obrigatório | Descrição |
|---|---|---|
| `model` | Não | Modelo de IA a ser usado (ex: `claude-haiku-4.5`). Padrão para o modelo do fluxo de trabalho pai. |
| `description` | Não | Descrição curta do propósito do sub-agente. |

## Comportamento em Runtime

Em tempo de execução, `actions/setup` extrai cada bloco de sub-agente inline e o grava em:

```text
.agents/agents/<nome>.agent.md
```

A CLI do Copilot descobre arquivos de agente em `.agents/agents/` nativamente. Para usar um sub-agente, instrua o prompt do fluxo de trabalho pai a invocá-lo pelo nome:

```aw wrap
## Requisitos de Teste

15. **Teste de Sub-Agente**: Use o sub-agente `file-summarizer` para resumir o
    arquivo `.github/workflows/smoke-copilot.md`. Verifique se o sub-agente retorna um
    breve resumo (2–4 frases). Marque este teste como ❌ se o sub-agente estiver
    indisponível ou retornar um erro.
```

A CLI do Copilot encontra `.agents/agents/file-summarizer.agent.md` e o invoca automaticamente.

## Exemplo Completo

O trecho a seguir mostra um fluxo de trabalho completo que define e usa um sub-agente inline.

```aw wrap
---
on:
  workflow_dispatch:
engine: copilot
---

# Tarefa de Resumo de Arquivo

Use o sub-agente `file-summarizer` para resumir o `README.md` e adicione um comentário
ao pull request atual com o resultado.

## agent: `file-summarizer`
---
model: claude-haiku-4.5
description: Resume o conteúdo de um arquivo em algumas frases concisas
---
Você é um assistente de sumarização de arquivos. Quando receber um caminho de arquivo, leia o arquivo
e retorne um breve resumo (2–4 frases) descrevendo seu propósito e conteúdo
principal. Seja conciso e factual.
```

O bloco de sub-agente no final é extraído antes que o fluxo de trabalho seja executado e não tem efeito sobre as instruções do fluxo de trabalho pai.

## Múltiplos sub-agentes

Um único arquivo de fluxo de trabalho pode conter mais de um bloco de sub-agente. Cada bloco inicia com seu próprio cabeçalho `## agent: \`nome\`` e termina no próximo cabeçalho `##` ou EOF.

```aw wrap
## agent: `summarizer`
---
model: claude-haiku-4.5
description: Resume arquivos de forma concisa
---
Resuma o arquivo fornecido em 2–4 frases.

## agent: `reviewer`
---
model: claude-sonnet-4.5
description: Revisar código em busca de problemas de qualidade
---
Revise o código fornecido em busca de bugs, problemas de estilo e possíveis melhorias.
```

## Documentação Relacionada

- [Importando Arquivos de Agente do Copilot](/gh-aw/reference/copilot-custom-agents/) — Importando agentes de `.github/agents/`
- [Markdown](/gh-aw/reference/markdown/) — Referência do corpo markdown do fluxo de trabalho
- [Estrutura do Fluxo de Trabalho](/gh-aw/reference/workflow-structure/) — Organização geral do arquivo de fluxo de trabalho
- [Frontmatter](/gh-aw/reference/frontmatter/) — Opções de configuração YAML
