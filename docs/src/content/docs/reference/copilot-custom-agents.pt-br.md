---
title: Importando arquivos de agente Copilot
description: Importe e reutilize arquivos de agente Copilot com GitHub Agentic Workflows
sidebar:
  order: 650
---

"Agentes personalizados" é um termo usado no GitHub Copilot para prompts especializados para comportamentos em tarefas específicas. São arquivos markdown armazenados no diretório `.github/agents/` e importados via campo `imports`. O Copilot suporta arquivos de agente nativamente, enquanto outros motores (Claude, Codex) injetam o corpo markdown como um prompt.

Um arquivo de agente personalizado típico se parece com isto:

```markdown title=".github/agents/meu-agente.md"
---
name: Meu Agente Copilot
description: Prompt especializado para tarefas de revisão de código
---

# Instruções do Agente

Você é um agente especializado em revisão de código. Foque em:
- Qualidade de código e melhores práticas
- Vulnerabilidades de segurança
- Otimização de desempenho
```

## Usando arquivos de agente Copilot do Agentic Workflows

Importe arquivos de agente Copilot em seu fluxo de trabalho usando o campo `imports`. Arquivos de agente podem ser importados de diretórios locais `.github/agents/` ou de repositórios externos.

### Importação de arquivo de agente local

Importe um agente do seu repositório:

```yaml wrap
---
on: pull_request
engine: copilot
imports:
  - .github/agents/meu-agente.md
---

Revise o pull request e forneça feedback.
```

### Importação de arquivo de agente remoto

Importe um arquivo de agente de um repositório externo usando o formato `owner/repo/path@ref`:

```yaml wrap
---
on: pull_request
engine: copilot
imports:
  - acme-org/shared-agents/.github/agents/code-reviewer.md@v1.0.0
---

Realize revisão de código abrangente usando instruções de agente compartilhadas.
```

As instruções do agente são mescladas com o prompt do fluxo de trabalho, personalizando o comportamento do motor de IA para tarefas específicas.

## Requisitos do arquivo de agente

- **Localização**: Deve estar em um diretório `.github/agents/` (repositório local ou remoto)
- **Formato**: Markdown com frontmatter YAML
- **Frontmatter**: Pode incluir `name`, `description`, `tools` e `mcp-servers`
- **Um por fluxo de trabalho**: Apenas um arquivo de agente pode ser importado por fluxo de trabalho
- **Cache**: Arquivos de agente remotos são armazenados em cache por SHA de commit em `.github/aw/imports/`

## Coleções de arquivos de agente Copilot

Organizações podem criar bibliotecas de arquivos de agente personalizados especializados:

```text
acme-org/ai-agents/
└── .github/
    └── agents/
        ├── code-reviewer.md         # Revisão de código geral
        ├── security-auditor.md      # Análise focada em segurança
        ├── performance-analyst.md   # Otimização de desempenho
        ├── accessibility-checker.md # Conformidade WCAG
        └── documentation-writer.md  # Documentação técnica
```

Equipes importam arquivos de agente com base nas necessidades do fluxo de trabalho:

```yaml wrap title="Revisão de PR focada em segurança"
---
on: pull_request
engine: copilot
imports:
  - acme-org/ai-agents/.github/agents/security-auditor.md@v2.0.0
  - acme-org/ai-agents/.github/agents/code-reviewer.md@v1.5.0
---

# Revisão de Segurança

Realize revisão de segurança abrangente deste pull request.
```

## Combinando arquivos de agente Copilot com outras importações

Você pode misturar importações de arquivos de agente personalizados com configurações de ferramentas e componentes compartilhados:

```yaml wrap
---
on: pull_request
engine: copilot
imports:
  # Importar arquivo de agente personalizado especializado
  - acme-org/ai-agents/.github/agents/security-auditor.md@v2.0.0
  
  # Importar configurações de ferramenta
  - acme-org/workflow-library/shared/tools/github-standard.md@v1.0.0
  
  # Importar servidores MCP
  - acme-org/workflow-library/shared/mcp/database.md@v1.0.0
  
  # Importar políticas de segurança
  - acme-org/workflow-library/shared/config/security-policies.md@v1.0.0
permissions:
  contents: read
safe-outputs:
  create-pull-request-review-comment:
    max: 10
---

# Revisão de Segurança Abrangente

Realize análise de segurança detalhada usando arquivos de agente especializados e ferramentas.
```

## Definindo agentes inline

Em vez de (ou ao lado de) importar arquivos de agente de `.github/agents/`, você pode definir agentes diretamente dentro do arquivo markdown do fluxo de trabalho usando um cabeçalho `## agent: \`nome\``:

```markdown
## agent: `code-reviewer`
---
model: claude-sonnet-4.5
description: Analisa código em busca de qualidade e correção
---
Você é um agente de revisão de código. Analise o código fornecido em busca de bugs, questões de estilo,
e melhorias potenciais. Seja específico e acionável.
```

Em tempo de execução, cada bloco de sub-agente inline é extraído para `.agents/agents/<nome>.agent.md`. A CLI do Copilot descobre esses arquivos nativamente, então você pode invocar o agente pelo nome no seu prompt de fluxo de trabalho sem qualquer configuração adicional.

Veja [Sub-agentes inline](/gh-aw/reference/inline-sub-agents/) para a referência completa de sintaxe, incluindo restrições de nome e campos de frontmatter.

## Documentação relacionada

- [Referência de Importações](/gh-aw/reference/imports/) - Documentação completa do sistema de importação
- [Sub-agentes inline](/gh-aw/reference/inline-sub-agents/) - Definindo sub-agentes dentro de um arquivo de fluxo de trabalho
- [Reutilizando fluxos de trabalho](/gh-aw/guides/packaging-imports/) - Gerenciando importações de fluxo de trabalho
- [Frontmatter](/gh-aw/reference/frontmatter/) - Referência de opções de configuração
