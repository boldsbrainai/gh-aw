---
title: Editando Fluxos de Trabalho
description: Aprenda quando você pode editar fluxos de trabalho diretamente no GitHub.com versus quando a recompilação é necessária, e melhores práticas para iterar em fluxos de trabalho agênticos.
sidebar:
  order: 5
---

Os fluxos de trabalho agênticos consistem em duas partes: o **YAML frontmatter** (compilado no arquivo de lock; as alterações exigem recompilação) e o **corpo em markdown** (carregado em tempo de execução; as alterações entram em vigor imediatamente). Isso permite que você itere nas instruções de IA sem recompilação, mantendo um controle rigoroso sobre a configuração sensível à segurança.

Veja [Criando Fluxos de Trabalho Agênticos](/gh-aw/setup/creating-workflows/) para orientação sobre a criação de fluxos de trabalho com assistência de IA.

## Editando Sem Recompilação

Você pode editar o **corpo em markdown** diretamente no GitHub.com ou em qualquer editor sem recompilar. As alterações entram em vigor na próxima execução do fluxo de trabalho.

### O Que Você Pode Editar

O corpo em markdown é carregado em tempo de execução a partir do arquivo `.md` original. Você pode editar livremente instruções de tarefa, modelos de saída, lógica condicional ("Se X, então faça Y"), explicações de contexto e exemplos.

### Exemplo: Adicionando Instruções

**Antes** (em `.github/workflows/issue-triage.md`):
```markdown
---
on:
  issues:
    types: [opened]
---

# Triagem de Issues

Leia a issue #${{ github.event.issue.number }} e adicione os labels apropriados.
```

**Depois** (editado no GitHub.com):
```markdown
---
on:
  issues:
    types: [opened]
---

# Triagem de Issues

Leia a issue #${{ github.event.issue.number }} e adicione os labels apropriados.

## Critérios de Labeling

Aplique estes labels com base no conteúdo:
- `bug`: Issues descrevendo comportamento incorreto com passos para reprodução
- `enhancement`: Solicitações de recursos ou melhorias
- `question`: Solicitações de ajuda ou esclarecimentos necessários
- `documentation`: Atualizações ou correções de documentação

Para prioridade, considere:
- `high-priority`: Problemas de segurança, bugs críticos, problemas bloqueantes
- `medium-priority`: Recursos importantes, bugs não críticos
- `low-priority`: Melhorias desejáveis, melhorias menores
```

✅ Esta alteração entra em vigor imediatamente sem recompilação.

## Editando Com Recompilação Necessária

> [!WARNING]
> Alterações no **YAML frontmatter** sempre exigem recompilação. Estas são opções de configuração sensíveis à segurança.

### O Que Exige Recompilação

Quaisquer alterações na configuração do frontmatter entre os marcadores `---`:

- **Gatilhos** (`on:`): Tipos de evento, filtros, agendamentos
- **Permissões** (`permissions:`): Níveis de acesso ao repositório
- **Ferramentas** (`tools:`): Configurações de ferramentas, servidores MCP, ferramentas permitidas
- **Rede** (`network:`): Domínios permitidos, regras de firewall
- **Saídas seguras** (`safe-outputs:`): Tipos de saída, detecção de ameaças
- **Scripts MCP** (`mcp-scripts:`): Ferramentas MCP personalizadas definidas inline
- **Runtimes** (`runtimes:`): Substituições de versão do Node, Python, Go
- **Importações** (`imports:`): Arquivos de configuração compartilhados
- **Jobs personalizados** (`jobs:`): Jobs de fluxo de trabalho adicionais
- **Motor** (`engine:`): Seleção do motor de IA (copilot, claude, codex)
- **Timeout** (`timeout-minutes:`): Tempo máximo de execução
- **Papéis** (`roles:`): Requisitos de permissão para atores

### Exemplo: Adicionando uma Ferramenta (Exige Recompilação)

**Antes**:
```yaml
---
on:
  issues:
    types: [opened]
---
```

**Depois** (deve recompilar):
```yaml
---
on:
  issues:
    types: [opened]

tools:
  github:
    toolsets: [issues]
---
```

⚠️ Execute `gh aw compile my-workflow` antes de fazer commit desta alteração.

## Expressões e Variáveis de Ambiente

### Expressões Permitidas

Você pode usar essas expressões com segurança no markdown sem recompilação:

```markdown
# Processar Issue

Leia a issue #${{ github.event.issue.number }} no repositório ${{ github.repository }}.

Título da issue: "${{ github.event.issue.title }}"

Use conteúdo higienizado: "${{ steps.sanitized.outputs.text }}"

Ator: ${{ github.actor }}
Repositório: ${{ github.repository }}
```

Essas expressões são avaliadas em tempo de execução e validadas por segurança. Veja [Templating](/gh-aw/reference/templating/) para a lista completa de expressões permitidas.

### Expressões Proibidas

Expressões arbitrárias são bloqueadas por segurança. Isto falhará em tempo de execução:

```markdown
# ❌ INCORRETO - Será rejeitado
Execute este comando: ${{ github.event.comment.body }}
```

Use `steps.sanitized.outputs.text` para entrada do usuário higienizada.

## Documentação relacionada

- [Workflow Structure](/gh-aw/reference/workflow-structure/) - Organização geral de arquivos
- [Frontmatter Reference](/gh-aw/reference/frontmatter/) - Todas as opções de configuração
- [Markdown Reference](/gh-aw/reference/markdown/) - Escrevendo instruções eficazes
- [Compilation Process](/gh-aw/reference/compilation-process/) - Como a compilação funciona
- [Templating](/gh-aw/reference/templating/) - Sintaxe de expressão e substituição
