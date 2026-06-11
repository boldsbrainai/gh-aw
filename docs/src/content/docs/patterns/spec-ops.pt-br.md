---
title: SpecOps
description: Mantenha e propague especificações estilo W3C usando fluxos de trabalho agenticos
---

SpecOps é um padrão para manter especificações formais usando fluxos de trabalho agenticos. Ele utiliza o agente [`w3c-specification-writer`](https://github.com/github/gh-aw/blob/main/.github/agents/w3c-specification-writer.agent.md) para criar especificações estilo W3C com palavras-chave RFC 2119 (MUST, SHALL, SHOULD, MAY) e propaga automaticamente mudanças para implementações consumidoras entre repositórios.

## Como o SpecOps funciona

1. **Atualizar especificação** — Acione um fluxo de trabalho com o agente `w3c-specification-writer` para editar o documento de especificação (palavras-chave RFC 2119, aumento de versão, log de mudanças).
2. **Revisar mudanças** — Aprove o pull request da especificação.
3. **Propagar automaticamente** — Ao mesclar, os fluxos de trabalho detectam atualizações e criam PRs em repositórios consumidores (como [gh-aw-mcpg](https://github.com/github/gh-aw-mcpg)) para manter a conformidade.
4. **Verificar conformidade** — Fluxos de trabalho de geração de testes atualizam suítes de teste de conformidade contra os novos requisitos.

## Atualizar Especificações

Crie um fluxo de trabalho para atualizar especificações usando o agente [`w3c-specification-writer`](https://github.com/github/gh-aw/blob/main/.github/agents/w3c-specification-writer.agent.md):

```yaml
---
name: Atualizar Especificação do MCP Gateway
on:
  workflow_dispatch:
    inputs:
      change_description:
        description: 'O que precisa mudar na especificação?'
        required: true
        type: string

engine: copilot
strict: true

safe-outputs:
  create-pull-request:
    title-prefix: "[spec] "
    labels: [documentation, specification]

tools:
  edit:
  bash:
---

# Fluxo de Trabalho de Atualização de Especificação

Atualize a especificação do MCP Gateway usando o agente w3c-specification-writer.

**Solicitação de Mudança**: ${{ inputs.change_description }}

## Sua Tarefa

1. Revise a especificação atual em `docs/src/content/docs/reference/mcp-gateway.md`

2. Aplique as mudanças solicitadas seguindo as convenções W3C:
   - Use palavras-chave RFC 2119 (MUST, SHALL, SHOULD, MAY)
   - Atualize o número da versão (maior/menor/patch)
   - Adicione entrada à seção Change Log
   - Atualize Status of This Document se necessário

3. Garanta que as mudanças mantenham requisitos de conformidade claros, especificações testáveis e exemplos completos

4. Crie um pull request com a especificação atualizada
```

## Propagar Mudanças

Após a mesclagem das atualizações da especificação, propague automaticamente as mudanças para os repositórios consumidores:

```yaml
---
name: Propagar Mudanças de Spec
on:
  push:
    branches:
      - main
    paths:
      - 'docs/src/content/docs/reference/mcp-gateway.md'

engine: copilot
strict: true

safe-outputs:
  create-pull-request:
    title-prefix: "[spec-update] "
    labels: [dependencies, specification]

tools:
  github:
    toolsets: [repos, pull_requests]
  edit:
  bash:
---

# Fluxo de Trabalho de Propagação de Especificação

A especificação do MCP Gateway foi atualizada. Propague as mudanças para os repositórios consumidores.

## Repositórios Consumidores

- **gh-aw-mcpg**: Atualize conformidade de implementação, schemas e testes
- **gh-aw**: Atualize validação e documentação do MCP gateway

## Sua Tarefa

1. Leia a versão mais recente da especificação e o log de mudanças
2. Identifique mudanças que quebram (breaking changes) e novos requisitos
3. Para cada repositório consumidor:
   - Atualize a implementação para corresponder à especificação
   - Execute testes para verificar a conformidade
   - Crie pull request com as mudanças
4. Crie issue de rastreamento vinculando todos os PRs
```

## Estrutura da Especificação

Especificações estilo W3C requerem: Abstract, Status, Introduction, Conformance, seções técnicas numeradas com palavras-chave RFC 2119, Compliance testing, References e um Change log.

**Exemplo de uso de RFC 2119**:

```markdown
## 3. Configuração do Gateway

O gateway MUST validar todos os campos de configuração antes da inicialização.
O gateway SHOULD registrar erros de validação com nomes de campo.
O gateway MAY fazer cache de configurações validadas.
```

Veja o agente [`w3c-specification-writer`](https://github.com/github/gh-aw/blob/main/.github/agents/w3c-specification-writer.agent.md) para um modelo completo e diretrizes.

## Versionamento Semântico

| Bump | Quando |
|------|------|
| **Maior (X.0.0)** | Mudanças que quebram |
| **Menor (0.Y.0)** | Novas funcionalidades, compatível com versões anteriores |
| **Patch (0.0.Z)** | Correções de bug, esclarecimentos |

A [Especificação do MCP Gateway](/gh-aw/reference/mcp-gateway/) é um exemplo ao vivo — mantida pelo fluxo de trabalho `layout-spec-maintainer` e implementada em [gh-aw-mcpg](https://github.com/github/gh-aw-mcpg).

## Padrões Relacionados

- **[MultiRepoOps](/gh-aw/patterns/multi-repo-ops/)** — Coordenação entre repositórios
