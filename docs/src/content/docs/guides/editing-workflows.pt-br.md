---
title: Editando Fluxos de Trabalho
description: Saiba quando você pode editar fluxos de trabalho diretamente no GitHub.com versus quando a recompilação é necessária, e melhores práticas para iterar em fluxos de trabalho agenticos.
sidebar:
  order: 5
---

Fluxos de trabalho agenticos consistem em duas partes: o **YAML frontmatter** (compilado no arquivo de lock; alterações exigem recompilação) e o **corpo em markdown** (carregado em tempo de execução; alterações entram em vigor imediatamente). Isso permite iterar nas instruções da IA sem recompilação, mantendo um controle rigoroso sobre a configuração sensível à segurança.

Veja [Criando Fluxos de Trabalho Agenticos](/gh-aw/setup/creating-workflows/) para orientação sobre a criação de fluxos de trabalho com assistência de IA.

## Editando Sem Recompilação

Você pode editar o **corpo em markdown** diretamente no GitHub.com ou em qualquer editor sem recompilar. As alterações entram em vigor na próxima execução do fluxo de trabalho.

### O que você pode editar

O corpo em markdown é carregado em tempo de execução a partir do arquivo `.md` original. Você pode editar livremente instruções de tarefas, modelos de saída, lógica condicional ("Se X, então faça Y"), explicações de contexto e exemplos.

### Exemplo: Adicionando Instruções

**Antes** (em `.github/workflows/issue-triage.md`):
```markdown
---
on:
  issues:
    types: [opened]
---

# Triagem de Issue

Leia a issue #${{ github.event.issue.number }} e adicione os labels apropriados.
```

**Depois** (editado no GitHub.com):
```markdown
---
on:
  issues:
    types: [opened]
---

# Triagem de Issue

Leia a issue #${{ github.event.issue.number }} e adicione os labels apropriados.

## Critérios de Label

Aplique estes labels com base no conteúdo:
- `bug`: Issues descrevendo comportamento incorreto com passos de reprodução
- `enhancement`: Solicitações de funcionalidades ou melhorias
- `question`: Solicitações de ajuda ou esclarecimentos necessários
- `documentation`: Atualizações ou correções de documentação

Para prioridade, considere:
- `high-priority`: Problemas de segurança, bugs críticos, problemas bloqueantes
- `medium-priority`: Funcionalidades importantes, bugs não críticos
- `low-priority`: Melhorias desejáveis, pequenas melhorias
```

✅ Esta alteração entra em vigor imediatamente sem recompilação.

## Editando Com Recompilação Necessária

> [!WARNING]
> Alterações no **YAML frontmatter** sempre exigem recompilação. Estas são opções de configuração sensíveis à segurança.

### O que requer recompilação

Quaisquer alterações na configuração do frontmatter entre os delimitadores `---`:

- **Gatilhos** (`on:`): Tipos de evento, filtros, agendamentos
- **Permissões** (`permissions:`): Níveis de acesso ao repositório
- **Ferramentas** (`tools:`): Configurações de ferramentas, servidores MCP, ferramentas permitidas
- **Rede** (`network:`): Domínios permitidos, regras de firewall
- **Saídas seguras** (`safe-outputs:`): Tipos de saída, detecção de ameaças
- **Scripts MCP** (`mcp-scripts:`): Ferramentas MCP personalizadas definidas inline
- **Runtimes** (`runtimes:`): Substituições de versão de Node, Python, Go
- **Importações** (`imports:`): Arquivos de configuração compartilhados
- **Jobs personalizados** (`jobs:`): Jobs de fluxo de trabalho adicionais
- **Engine** (`engine:`): Seleção da engine de IA (copilot, claude, codex)
- **Tempo limite** (`timeout-minutes:`): Tempo máximo de execução
- **Papéis** (`roles:`): Requisitos de permissão para atores

### Exemplo: Adicionando uma Ferramenta (Requer Recompilação)

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

⚠️ Execute `gh aw compile meu-fluxo-de-trabalho` antes de commitar esta alteração.

## Expressões e Variáveis de Ambiente

### Expressões Permitidas

Você pode usar estas expressões com segurança no markdown sem recompilação:

```markdown
# Processar Issue

Leia a issue #${{ github.event.issue.number }} no repositório ${{ github.repository }}.

Título da issue: "${{ github.event.issue.title }}"

Use conteúdo higienizado: "${{ steps.sanitized.outputs.text }}"

Ator: ${{ github.actor }}
Repositório: ${{ github.repository }}
```

Essas expressões são avaliadas em tempo de execução e validadas por segurança. Veja [Modelagem (Templating)](/gh-aw/reference/templating/) para a lista completa de expressões permitidas.

### Expressões Proibidas

Expressões arbitrárias são bloqueadas por segurança. Isto falhará em tempo de execução:

```markdown
# ❌ ERRADO - Será rejeitado
Execute este comando: ${{ github.event.comment.body }}
```

Use `steps.sanitized.outputs.text` para entrada de usuário higienizada.

## Documentação Relacionada

- [Estrutura do Fluxo de Trabalho](/gh-aw/reference/workflow-structure/) - Organização geral do arquivo
- [Referência de Frontmatter](/gh-aw/reference/frontmatter/) - Todas as opções de configuração
- [Referência de Markdown](/gh-aw/reference/markdown/) - Escrevendo instruções eficazes
- [Processo de Compilação](/gh-aw/reference/compilation-process/) - Como funciona a compilação
- [Modelagem (Templating)](/gh-aw/reference/templating/) - Sintaxe de expressão e substituição
