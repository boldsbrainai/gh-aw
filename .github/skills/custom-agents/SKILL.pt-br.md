---
name: custom-agents
description: Defina e valide arquivos de agentes personalizados do GitHub, prompts e exemplos.
---


# Formato de Arquivo de Agente Personalizado do GitHub

Use esta referência para o formato de arquivo de agente personalizado do GitHub.

## Visão Geral

O GitHub Copilot lê instruções de agente personalizado a partir de arquivos Markdown com frontmatter YAML. Use-os para definir comportamento especializado, acesso a ferramentas e fluxos de trabalho para seu repositório.

## Locais de Arquivo

Coloque arquivos de agente personalizado nestes locais com base no escopo:

### 1. Instruções em todo o repositório
- **Arquivo**: `.github/copilot-instructions.md`
- **Escopo**: Aplica-se a toda geração de código no repositório
- **Caso de uso**: Padrões gerais de codificação, requisitos de segurança, práticas de teste

### 2. Instruções específicas de caminho
- **Diretório**: `.github/instructions/`
- **Padrão**: `*.instructions.md` (ex: `frontend.instructions.md`, `backend.instructions.md`)
- **Escopo**: Pode direcionar diretórios ou padrões de arquivo específicos usando `applyTo` no frontmatter
- **Caso de uso**: Diretrizes específicas de framework, regras específicas de componente

### 3. Perfis de Agente Personalizado
- **Diretório**: `.github/agents/` ou `.github/copilot/instructions/`
- **Padrão**: `AGENTS.md`, `*.md` (ex: `readme-creator.md`, `test-writer.md`)
- **Escopo**: Define agentes especializados com capacidades e instruções específicas
- **Caso de uso**: Agentes específicos de tarefa (documentação, testes, refatoração)

### 4. Integração de fluxo de trabalho agentic
- **Localização**: Importado via campo `imports` no frontmatter do fluxo de trabalho
- **Padrão**: Quaisquer arquivos markdown sob o diretório `.github/agents/`
- **Escopo**: Agente personalizado para execução específica de fluxo de trabalho agentic
- **Caso de uso**: Configuração de agente específica de fluxo de trabalho
- **Importante**: Apenas um arquivo de agente é permitido por fluxo de trabalho

## Formato de Arquivo

### Estrutura Básica

```markdown
# YAML frontmatter (configuração)
name: nome-do-agente
description: Breve descrição do propósito do agente

# Corpo do Markdown (instruções)

Suas instruções em linguagem natural para o agente vão aqui.
```

### Esquema Completo de Frontmatter YAML

```yaml
# Campos obrigatórios
name: identificador-do-agente              # Identificador único para o agente

# Campos descritivos opcionais
description: >                      # Descrição de várias linhas do propósito do agente
  Agente especializado em tarefas específicas

# Campos de instrução opcionais
prompt: |                          # Instruções de forma livre (alternativa ao corpo markdown)
  Suas instruções aqui

# Configuração opcional de ferramenta
tools:                             # Lista de ferramentas permitidas para este agente
  - createFile
  - editFiles
  - codeSearch
  - search

# Direcionamento de caminho opcional (para arquivos .instructions.md)
applyTo:                          # Padrões glob para arquivos/diretórios direcionados
  - "src/frontend/**"
  - "**/*.tsx"

# Configuração opcional de servidor MCP (somente enterprise/org)
mcp-server:                       # Configuração de servidor MCP externo
  url: https://my-mcp-server.com
  api-key: ${{ secrets.MCPSERVER_API_KEY }}

# Configurações opcionais
settings:                         # Configurações personalizadas de runtime ou conexão
  key: value
```

## Descrições de Campo

### Campos Principais

#### name (string, obrigatório para perfis de agente)
- Identificador único para o agente
- Usado para referenciar o agente em fluxos de trabalho ou atribuições
- Convenção: minúsculo com hifens (ex: `readme-creator`, `test-writer`)

#### description (string, opcional)
- Descrição amigável do foco e comportamento do agente
- Ajuda os usuários a entender no que o agente se especializa
- Pode ser de várias linhas usando a sintaxe `>` ou `|` do YAML

#### prompt (string, opcional)
- Alternativa ao uso do corpo markdown para instruções
- Contém instruções em linguagem natural de forma livre
- Use `|` (literal) ou `>` (dobrado) do YAML para conteúdo de várias linhas
- Se tanto o `prompt` quanto o corpo markdown existirem, eles são normalmente combinados

### Configuração de Ferramenta

#### tools (array de strings, opcional)
- Lista de ferramentas que o agente tem permissão para usar
- Se omitido ou definido como `["*"]`, o agente tem acesso a todas as ferramentas disponíveis
- Nomes de ferramentas são **case-insensitive** (insensíveis a maiúsculas/minúsculas)
- Suporta tanto aliases de ferramenta padrão do GitHub quanto convenções de nomenclatura legadas

**Aliases de Ferramenta Padrão do GitHub:**

O GitHub Copilot define um conjunto padronizado de aliases de ferramenta para agentes personalizados:

- **`read`** - Acessar e ler conteúdos de arquivos ou código
- **`edit`** - Fazer alterações em arquivos de código, aplicar edições ou refatoração
- **`search`** - Pesquisar na base de código por palavras-chave, referências ou padrões
- **`pr`** - Criar, gerenciar ou atualizar pull requests
- **`issue`** - Criar, gerenciar ou atualizar issues

**Nomes de Ferramentas Legados:**

Para compatibilidade retroativa, esses nomes de ferramentas legados ainda são suportados:

- `createFile` - Criar novos arquivos (use `edit` em vez disso)
- `editFiles` - Modificar arquivos existentes (use `edit` em vez disso)
- `deleteFiles` - Remover arquivos (use `edit` em vez disso)
- `codeSearch` - Pesquisa de código semântica (use `search` em vez disso)
- `runCommand` - Executar comandos shell
- `getFile` - Ler conteúdo de arquivo (use `read` em vez disso)
- `listFiles` - Listar conteúdo de diretório (use `read` em vez disso)

**Prefixos de Ferramenta de Servidor MCP:**

Ao usar servidores MCP (Model Context Protocol), você pode especificar ferramentas com prefixos de servidor:
- Ferramenta única: `my-mcp-server/nome-da-ferramenta`
- Todas as ferramentas de um servidor: `my-mcp-server/*`

**Exemplos:**

```yaml
# Usando aliases de ferramenta padrão
tools:
  - read
  - edit
  - search

# Habilitar todas as ferramentas com wildcard
tools: ["*"]

# Usando nomes legados (ainda suportados)
tools:
  - editFiles
  - createFile
  - search

# Ferramentas mistas padrão e de servidor MCP
tools:
  - read
  - edit
  - github-mcp/create_issue
  - custom-mcp/*

# Lista vazia desabilita todas as ferramentas
tools: []
```

### Direcionamento de Caminho

#### applyTo (array de strings, opcional)
- Usado apenas em arquivos `.instructions.md`
- Especifica padrões glob para arquivos/diretórios que estas instruções se aplicam
- Suporta wildcards: `*` (quaisquer caracteres), `**` (quaisquer diretórios)
- Múltiplos padrões podem ser especificados

**Exemplo:**
```yaml
applyTo:
  - "src/frontend/**/*.tsx"
  - "src/frontend/**/*.ts"
  - "components/**"
```

### Recursos Enterprise

#### mcp-server (objeto, opcional)
- Configuração para servidores MCP (Model Context Protocol) externos
- Normalmente usado em ambientes corporativos ou de organização
- Permite integração com ferramentas e serviços personalizados

**Campos:**
- `url` (string): Endpoint do servidor MCP
- `api-key` (string): Chave de autenticação (use segredos do GitHub)

**Exemplo:**
```yaml
mcp-server:
  url: https://internal-tools.company.com/mcp
  api-key: ${{ secrets.INTERNAL_MCP_KEY }}
```

#### settings (objeto, opcional)
- Configurações personalizadas de runtime ou conexão
- Pares chave-valor para configuração específica do agente
- O formato e as chaves disponíveis dependem da implementação do agente

## Padrões de Uso

### Padrão 1: Padrões em todo o repositório

**Arquivo:** `.github/copilot-instructions.md`

```markdown
description: Padrões de codificação em todo o repositório

# Padrões de Codificação

## Guia de Estilo
- Use aspas simples em JavaScript/TypeScript
- Siga a configuração do ESLint em `.eslintrc.json`
- Comprimento máximo de linha: 100 caracteres

## Segurança
- Sempre defina sinalizadores `httpOnly` e `secure` para cookies
- Valide toda a entrada do usuário
- Use consultas parametrizadas para acesso ao banco de dados

## Testes
- Todo código novo deve incluir testes Jest
- Tente >80% de cobertura de código
- Teste casos extremos e condições de erro
```

### Padrão 2: Instruções específicas de caminho

**Arquivo:** `.github/instructions/frontend.instructions.md`

```markdown
description: Diretrizes de desenvolvimento frontend
applyTo:
  - "src/frontend/**"
  - "components/**"

# Diretrizes de Desenvolvimento Frontend

## Estrutura do Componente
- Use componentes funcionais React com hooks
- Prefira composição a herança
- Mantenha componentes pequenos e focados (< 150 linhas)

## Estilização
- Use Módulos CSS para estilos de componente
- Siga a convenção de nomenclatura BEM
- Use classes utilitárias Tailwind quando apropriado

## Gerenciamento de Estado
- Use Context do React para estado global
- Mantenha estado local nos componentes quando possível
- Use reducers para lógica de estado complexa
```

### Padrão 3: Perfil de Agente Personalizado

**Arquivo:** `.github/agents/readme-creator.md`

```markdown
name: readme-creator
description: Agente especializado em criar e melhorar arquivos README
tools:
  - read
  - edit
  - search

# Agente Criador de README

Você é um especialista em documentação focado em criar arquivos README claros e abrangentes.

## Responsabilidades
- Criar arquivos README.md bem estruturados para projetos
- Incluir todas as seções padrão: Visão Geral, Instalação, Uso, Contribuição
- Gerar exemplos de código precisos
- Garantir que a documentação esteja atualizada com a base de código

## Diretrizes de Estilo
- Use linguagem clara e concisa
- Inclua exemplos de código com realce de sintaxe
- Adicione selos (badges) para status de build, cobertura, versão
- Organize com hierarquia lógica de cabeçalhos
- Inclua sumário para READMEs longos

## Padrões de Qualidade
- Verifique se todos os exemplos de código estão precisos
- Teste as instruções de instalação
- Garanta que os links estejam válidos e funcionando
- Verifique a formatação Markdown adequada
```

### Padrão 4: Agente Escrevedor de Testes

**Arquivo:** `.github/agents/test-writer.md`

```markdown
name: test-writer
description: Agente especializado para escrever suítes de teste abrangentes
tools:
  - read
  - edit
  - search

# Agente Escritor de Testes

Você se especializa na criação de suítes de teste abrangentes e bem estruturadas.

## Framework de Testes
- Use Jest para JavaScript/TypeScript
- Siga o padrão AAA: Arrange (Organizar), Act (Agir), Assert (Assertir)
- Use nomes de teste descritivos: "should [comportamento esperado] when [condição]"

## Cobertura de Testes
- Escreva testes unitários para todas as funções públicas
- Crie testes de integração para endpoints de API
- Adicione testes de casos extremos (nulo, indefinido, vazio, valores de limite)
- Teste condições de erro e tratamento de exceções

## Organização de Testes
- Agrupe testes relacionados com blocos `describe`
- Use `beforeEach` e `afterEach` para configuração/limpeza
- Mantenha os testes independentes e isolados

## Melhores Práticas
- Uma asserção por teste quando possível
- Use construtores de dados de teste para objetos complexos
- Evite interdependência de testes
- Mantenha testes rápidos (< 1 segundo cada)
```

### Padrão 5: Integração de Fluxo de Trabalho Agentic

**Arquivo:** `.github/workflows/code-review.md`

```markdown
on:
  pull_request:
    types: [opened, synchronize]
permissions:
  contents: read
  pull-requests: write
engine:
  id: copilot
  custom-agent: .github/agents/code-reviewer.md

# Revisão de Código Automatizada

Revise as alterações do pull request e forneça feedback construtivo.
```

**Arquivo:** `.github/agents/code-reviewer.md`

```markdown
name: code-reviewer
description: Agente especializado em realizar revisões de código
tools:
  - read
  - search

# Agente de Revisão de Código

Você é um revisor de código experiente focado em qualidade de código, segurança e melhores práticas.

## Lista de Verificação de Revisão
- O código segue as diretrizes de estilo do repositório
- Tratamento de erro adequado está implementado
- Melhores práticas de segurança são seguidas
- Testes estão incluídos para nova funcionalidade
- A documentação é atualizada onde necessário
- Sem complexidade desnecessária

## Estilo de Feedback
- Seja construtivo e específico
- Explique o raciocínio por trás das sugestões
- Priorize problemas (crítico, importante, menor)
- Reconheça bons padrões e melhorias
- Forneça exemplos de código para sugestões
```

## Integração com gh-aw

A ferramenta gh-aw (GitHub Agentic Workflows) suporta arquivos de agente personalizados através do campo `imports` no frontmatter do fluxo de trabalho. Quaisquer arquivos markdown sob o diretório `.github/agents/` são tratados como arquivos de agente personalizados quando importados.

### Configuração

```markdown
on: issues
engine:
  id: copilot
imports:
  - .github/agents/my-agent.md

# Meu Fluxo de Trabalho

Instruções para o fluxo de trabalho...
```

### Engines Suportadas

Arquivos de agente personalizados são suportados pelas seguintes engines:

1. **Copilot** - Usa a flag `--agent <caminho>` para carregar arquivo de agente personalizado
2. **Claude** - Prepõe o conteúdo do arquivo de agente ao prompt do fluxo de trabalho
3. **Codex** - Prepõe o conteúdo do arquivo de agente ao prompt do fluxo de trabalho

### Resolução de Caminho de Arquivo

- Arquivos de agente são importados via campo `imports`
- Devem ser arquivos markdown localizados sob o diretório `.github/agents/`
- Apenas um arquivo de agente é permitido por fluxo de trabalho
- O arquivo é validado durante a compilação do fluxo de trabalho
- A etapa de checkout é adicionada automaticamente se o arquivo de agente for importado

### Exemplo de Fluxo de Trabalho com Agente Personalizado

```markdown
on:
  issues:
    types: [opened]
permissions:
  contents: read
  issues: write
engine:
  id: copilot
imports:
  - .github/agents/issue-triager.md
tools:
  github:
    allowed:
      - add_labels_to_issue
      - create_issue_comment

# Fluxo de Trabalho de Triagem de Issue

Analise a issue e categorize-a apropriadamente.
```

## Melhores Práticas

### 1. Mantenha as Instruções Focadas
- Cada agente deve ter um propósito claro e específico
- Evite misturar preocupações não relacionadas em um único agente
- Crie múltiplos agentes especializados em vez de um agente de propósito geral

### 2. Seja Explícito e Específico
- Forneça exemplos concretos do comportamento esperado
- Defina critérios de sucesso claros
- Especifique casos extremos e tratamento de erros

### 3. Use Escopo Apropriado
- Instruções para todo o repositório para padrões universais
- Instruções específicas de caminho para regras de framework ou diretório
- Agentes personalizados para fluxos de trabalho específicos de tarefa

### 4. Teste o Comportamento do Agente
- Verifique se o agente segue as instruções corretamente
- Teste com vários cenários de entrada
- Itere com base no desempenho real do agente

### 5. Mantenha e Atualize
- Mantenha as instruções atualizadas com mudanças na base de código
- Revise e refine com base no desempenho do agente
- Remova instruções obsoletas ou conflitantes

### 6. Considerações de Segurança
- Limite o acesso a ferramentas ao que for necessário
- Seja cauteloso com permissões de exclusão de arquivos
- Use segredos para configuração sensível
- Revise as ações do agente regularmente

## Padrões Comuns

### Agente de Documentação
```yaml
name: documentation-specialist
description: Cria e mantém documentação técnica
tools: [read, edit, search]
```

### Agente de Refatoração
```yaml
name: code-refactorer
description: Melhora a qualidade e estrutura do código
tools: [read, edit, search]
```

### Auditor de Segurança
```yaml
name: security-auditor
description: Analisa código em busca de vulnerabilidades de segurança
tools: [read, search]
```

### Assistente de Migração
```yaml
name: migration-helper
description: Auxilia com migrações de framework ou biblioteca
tools: [read, edit, search]
```

### Agente de Gerenciamento de Issue
```yaml
name: issue-manager
description: Gerencia issues do GitHub e rastreamento de projetos
tools: [read, issue]
```

### Assistente de Pull Request
```yaml
name: pr-assistant
description: Auxilia na criação e gerenciamento de pull requests
tools: [read, edit, pr]
```

## Solução de Problemas

### Agente Não Seguindo Instruções
- Torne as instruções mais explícitas e específicas
- Forneça exemplos concretos
- Quebre instruções complexas em passos
- Garanta que as instruções não entrem em conflito

### Problemas de Acesso a Ferramentas
- Verifique se as ferramentas estão listadas no array `tools`
- Verifique se o agente tem as permissões necessárias
- Garanta que as ferramentas estejam disponíveis no ambiente

### Direcionamento de Caminho Não Funcionando
- Verifique se os padrões glob estão corretos
- Verifique se os caminhos dos arquivos correspondem aos padrões
- Certifique-se de que `applyTo` seja usado apenas em arquivos `.instructions.md`

### Arquivo de Agente Personalizado Não Encontrado
- Verifique se o arquivo do agente está importado no campo `imports`
- Certifique-se de que o arquivo existe e está commitado sob o diretório `.github/agents/`
- Confirme se o caminho do arquivo do agente está correto na lista de imports
- Lembre-se: apenas um arquivo de agente é permitido por fluxo de trabalho

## Referências

- [Configuração de Arquivos de Agente do GitHub Copilot](https://docs.github.com/en/copilot/reference/copilot-custom-agents-configuration) - Referência oficial para configuração de agente personalizado, incluindo aliases de ferramenta
- [Documentação de Instruções Personalizadas do GitHub Copilot](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- [Sobre Agentes Personalizados](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-custom-agents)
- [Blog do GitHub: Suporte a Instruções Personalizadas](https://github.blog/changelog/2025-07-23-github-copilot-coding-agent-now-supports-instructions-md-custom-instructions/)
- [Blog do GitHub: Suporte a AGENTS.md](https://github.blog/changelog/2025-08-28-copilot-coding-agent-now-supports-agents-md-custom-instructions/)

## Exemplos Neste Repositório

O repositório gh-aw usa arquivos de agente personalizados para guias de engenharia de desempenho:

- `.github/copilot/instructions/ci-performance.md` - Otimização de CI/CD
- `.github/copilot/instructions/workflow-performance.md` - Eficiência de fluxo de trabalho
- `.github/copilot/instructions/build-performance.md` - Otimização de build
- `.github/copilot/instructions/cli-performance.md` - Desempenho da CLI

Esses arquivos fornecem orientação especializada para tarefas de engenharia de desempenho e demonstram o formato de arquivo de agente personalizado na prática.
