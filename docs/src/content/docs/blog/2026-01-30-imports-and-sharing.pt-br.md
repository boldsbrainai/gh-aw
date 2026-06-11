---
title: "Imports & Compartilhamento: A Arma Secreta de Peli"
description: "Como componentes modulares e reutilizáveis permitiram escalar nossa coleção de agentes"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-30
draft: true
prev:
  link: /gh-aw/blog/2026-01-27-operational-patterns/
  label: 9 Padrões Operacionais
next:
  link: /gh-aw/blog/2026-02-02-security-lessons/
  label: Lições de Segurança
---

[Artigo Anterior](/gh-aw/blog/2026-01-27-operational-patterns/)

---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

*Venha comigo, e você verá* outra parte da nossa série Fábrica de Agentes de Peli! Já percorremos os [fluxos de trabalho](/gh-aw/blog/2026-01-13-meet-the-workflows/), aprendemos nossas [lições](/gh-aw/blog/2026-01-21-twelve-lessons/), descobrimos as [receitas secretas](/gh-aw/blog/2026-01-24-design-patterns/) e exploramos os [padrões operacionais](/gh-aw/blog/2026-01-27-operational-patterns/). Hoje, revelarei o *eterno gobstopper* - a arma secreta que tornou o escalonamento possível: imports!

Aqui está a verdade: cuidar de dezenas de agentes seria completamente insustentável sem reutilização. Uma das características mais poderosas que nos permitiu escalar a Fábrica de Agentes de Peli é o **sistema de imports** - um mecanismo para compartilhar e reutilizar componentes de fluxo de trabalho em toda a fábrica.

Em vez de duplicar configurações, configurações de ferramentas e instruções em cada fluxo de trabalho, criamos uma biblioteca de componentes compartilhados que os agentes podem importar sob demanda. Isso não é apenas sobre ser DRY (embora isso seja bom) - é cuidadosamente projetado para suportar modularização, compartilhamento, instalação, fixação (pinning) e versionamento de porções de arquivo único de fluxos de trabalho agentic.

Vamos mergulhar!

## O Poder dos Imports

Os imports oferecem vários benefícios revolucionários que transformaram a forma como desenvolvemos e mantemos a fábrica:

### 🔄 Princípio DRY para Fluxos de Trabalho Agentic

Quando melhoramos a formatação de relatórios ou atualizamos uma configuração de servidor MCP, a mudança se propaga automaticamente para todos os fluxos de trabalho que a importam. Não há necessidade de atualizar 46 fluxos de trabalho individualmente. Isso é enorme!

Por exemplo, quando melhoramos o componente [`reporting.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/reporting.md) com melhores diretrizes de formatação, todos os 46 fluxos de trabalho que o importavam se beneficiaram imediatamente. Uma mudança, 46 fluxos de trabalho melhorados. Mágica.

### 🧩 Capacidades de Fluxo de Trabalho Componíveis

Fluxos de trabalho podem misturar e combinar capacidades importando diferentes componentes compartilhados - como combinar visualização de dados, análise de tendências e pesquisa na web em uma única lista de imports.

Um fluxo de trabalho analítico típico pode importar:

- `reporting.md` para diretrizes de formatação
- `python-dataviz.md` para capacidades de visualização
- `jqschema.md` para processamento de JSON
- `mcp/tavily.md` para pesquisa na web

Cada import adiciona uma capacidade específica, e os fluxos de trabalho compõem exatamente o que precisam. É como blocos de montar LEGO para agentes!

### 🎯 Separação de Preocupações

A configuração de ferramentas, permissões de rede, lógica de busca de dados e instruções de agente podem ser mantidas independentemente por diferentes especialistas, e então compostas juntas.

Isso permite a especialização:

- Equipe de infraestrutura gerencia configurações de servidor MCP
- Equipe de segurança mantém políticas de rede
- Equipe de dados constrói componentes de visualização
- Autores de agentes focam em prompts e lógica

Todos trabalham no que conhecem melhor, e tudo se une perfeitamente.

### ⚡ Experimentação Rápida

Criar um novo fluxo de trabalho geralmente significa escrever apenas o prompt específico do agente e importar 3-5 componentes compartilhados. Podemos prototipar novos agentes em minutos em vez de horas.

Exemplo de fluxo de trabalho mínimo:

```markdown
---
description: Analisar padrões de código
imports:
  - shared/reporting.md
  - shared/mcp/serena.md
  - shared/jqschema.md
---

Analise a base de código para padrões comuns...
```

É isso! Três imports fornecem relatórios, análise de código e processamento de JSON. Você apenas foca em escrever o prompt.

## A Biblioteca de Importação

A fábrica organizou componentes compartilhados em dois diretórios principais:

### Capacidades Principais: `.github/workflows/shared/`

35+ componentes fornecendo capacidades fundamentais:

#### Componentes Compartilhados Mais Populares

**[`reporting.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/reporting.md?plain=1)** (46 imports)

- Diretrizes de formatação de relatório
- Referências de execução de fluxo de trabalho
- Padrões de rodapé
- Estrutura consistente

**[`jqschema.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/jqschema.md?plain=1)** (17 imports)

- Utilitários de consulta JSON
- Validação de esquema
- Padrões de transformação de dados

**[`python-dataviz.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/python-dataviz.md?plain=1)** (7 imports)

- Ambiente Python com NumPy, Pandas, Matplotlib, Seaborn
- Templates de visualização de dados
- Utilitários de geração de gráficos

**[`trending-charts-simple.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/trending-charts-simple.md?plain=1)** (6 imports)

- Configuração rápida para visualizações de tendência
- Análise de série temporal
- Gráficos de comparação

**[`gh.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/gh.md?plain=1)** (4 imports)

- Wrapper safe-input para GitHub CLI
- Gerenciamento de autenticação
- Comandos gh comuns

**[`copilot-pr-data-fetch.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/copilot-pr-data-fetch.md?plain=1)** (4 imports)

- Buscar dados de PR do GitHub Copilot
- Gerenciamento de cache
- Pré-processamento de dados

#### Componentes Especializados

**Análise de Dados**

- [`charts-with-trending.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/charts-with-trending.md) - Tendências abrangentes com cache-memory
- [`ci-data-analysis.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/ci-data-analysis.md) - Análise de fluxo de trabalho de CI
- [`session-analysis-charts.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/session-analysis-charts.md) - Visualização de sessão do Copilot

**Prompts & Saída**

- [`keep-it-short.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/keep-it-short.md) - Orientação para respostas concisas
- [`safe-output-app.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/safe-output-app.md) - Padrões de saída segura

### Configurações de Servidor MCP: `.github/workflows/shared/mcp/`

20+ configurações de servidor MCP para capacidades especializadas:

#### Servidores MCP Mais Usados

**[`gh-aw.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/mcp/gh-aw.md?plain=1)** (12 imports)

- GH-AW como um servidor MCP
- Comando `logs` para depuração de fluxo de trabalho
- Acesso a metadados de fluxo de trabalho

**[`tavily.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/mcp/tavily.md?plain=1)** (5 imports)

- Pesquisa na web via API Tavily
- Capacidades de pesquisa
- Acesso a informações atuais

**[`markitdown.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/mcp/markitdown.md?plain=1)** (3 imports)

- Conversão de documento (PDF, Office, imagens para Markdown)
- Extração de conteúdo
- Análise multimídia

**[`ast-grep.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/mcp/ast-grep.md?plain=1)** (2 imports)

- Pesquisa estrutural de código e análise
- Correspondência de padrões
- Suporte a refatoração

**[`brave.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/mcp/brave.md?plain=1)** (2 imports)

- Pesquisa web alternativa via API Brave
- Pesquisa focada em privacidade
- Resultados de pesquisa diversos

#### Infraestrutura & Análise

**Ferramentas de Desenvolvimento**

- [`jupyter.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/mcp/jupyter.md) - Ambiente Jupyter notebook com serviços Docker
- [`skillz.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/mcp/skillz.md) - Carregamento dinâmico de skill de `.github/skills/`
- [`serena.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/mcp/serena.md) - Análise semântica de código

**Conhecimento & Pesquisa**

- [`context7.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/mcp/context7.md) - Pesquisa consciente do contexto
- [`deepwiki.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/mcp/deepwiki.md) - Pesquisa profunda na Wikipedia
- [`microsoft-docs.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/mcp/microsoft-docs.md) - Documentação Microsoft
- [`arxiv.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/mcp/arxiv.md) - Pesquisa de artigos acadêmicos

**Integrações Externas**

- [`slack.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/mcp/slack.md) - Integração com workspace Slack
- [`notion.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/mcp/notion.md) - Integração com workspace Notion
- [`sentry.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/mcp/sentry.md) - Rastreamento de erros
- [`datadog.md`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/shared/mcp/datadog.md) - Plataforma de observabilidade

## Estatísticas de Importação

O uso extensivo de imports pela fábrica demonstra seu valor:

- **84 fluxos de trabalho** (65% da fábrica) usam o recurso de imports
- **46 fluxos de trabalho** importam `reporting.md` (componente mais popular)
- **17 fluxos de trabalho** importam `jqschema.md` (utilitários JSON)
- **12 fluxos de trabalho** importam `mcp/gh-aw.md` (servidor de meta-análise)
- **35+ componentes compartilhados** em `.github/workflows/shared/`
- **20+ configurações de servidor MCP** em `.github/workflows/shared/mcp/`
- **Média de 2-3 imports** por fluxo de trabalho (alguns têm 8+!)

## Como Funcionam os Imports

### Sintaxe Básica de Importação

```markdown
---
description: Meu fluxo de trabalho
imports:
  - shared/reporting.md
  - shared/mcp/tavily.md
---

O prompt do seu fluxo de trabalho aqui...
```

### O que é Importado

Quando um fluxo de trabalho importa um componente compartilhado, várias coisas são mescladas:

1. **Frontmatter** - Ferramentas, permissões, configurações de rede
2. **Instruções** - Orientação de prompt e contexto
3. **Servidores MCP** - Configurações de ferramenta
4. **Safe Outputs** - Templates de saída

### Resolução de Importação

Imports são resolvidos no momento da compilação:

1. Analisar frontmatter do fluxo de trabalho
2. Carregar cada arquivo importado
3. Mesclar configurações (o fluxo de trabalho sobrescreve os imports)
4. Compilar para YAML final

### Versionamento & Fixação (Pinning)

Imports podem ser fixados a commits específicos:

```markdown
imports:
  - shared/reporting.md@abc123
  - shared/mcp/tavily.md@v1.2.0
```

Isso garante estabilidade para fluxos de trabalho de produção enquanto permite a experimentação com versões mais recentes.

## Melhores Práticas para Imports

### Criando Componentes Compartilhados

**Faça:**

- ✅ Torne os componentes focados e de propósito único
- ✅ Documente as opções de configuração
- ✅ Versionar mudanças significativas
- ✅ Teste com múltiplos importadores
- ✅ Forneça exemplos

**Não faça:**

- ❌ Criar componentes monolíticos "tudo em um"
- ❌ Quebrar importadores existentes sem versionamento
- ❌ Duplicar funcionalidade entre componentes
- ❌ Codificar valores específicos do repositório
- ❌ Esquecer de atualizar a documentação

### Usando Imports Efetivamente

**Faça:**

- ✅ Importe apenas o que você precisa
- ✅ Sobrescreva configurações importadas quando necessário
- ✅ Fixe fluxos de trabalho críticos de produção
- ✅ Documente por que cada import é necessário
- ✅ Teste após atualizar os imports

**Não faça:**

- ❌ Importar componentes conflitantes
- ❌ Sobrescrever sem entender o impacto
- ❌ Usar imports não fixados em produção
- ❌ Seguir listas de importação sem entender
- ❌ Esquecer de recompilar após alterações

## Evolução dos Componentes Compartilhados

A biblioteca de componentes compartilhados evoluiu organicamente:

### Fase 1: Duplicação (Fluxos de Trabalho 1-10)

Os primeiros fluxos de trabalho duplicavam a configuração. O copiar-colar foi o mais rápido para protótipos iniciais.

### Fase 2: Extração (Fluxos de Trabalho 11-30)

À medida que os padrões emergiram, extraímos configurações comuns para arquivos compartilhados. Primeiros componentes: `reporting.md` e `python-dataviz.md`.

### Fase 3: Ecossistema (Fluxos de Trabalho 31-80)

A biblioteca de componentes cresceu para atender à maioria das necessidades comuns. Novos fluxos de trabalho compunham principalmente componentes existentes.

### Fase 4: Especialização (Fluxos de Trabalho Posteriores)

Componentes altamente especializados surgiram para domínios específicos (análise do Copilot, escaneamento de segurança, etc.).

## Impacto na Velocidade

O sistema de imports acelerou drasticamente o desenvolvimento:

| Métrica | Sem Imports | Com Imports |
| ------ | --------------- | ------------ |
| Tempo para criar fluxo de trabalho | 2-4 horas | 15-30 minutos |
| Linhas de configuração | 100-200 | 20-40 |
| Carga de manutenção | Alta | Baixa |
| Consistência | Manual | Automática |
| Taxa de reutilização | ~0% | ~65% |

## Padrões de Importação Comuns

### A Pilha do Analista

```markdown
imports:
  - shared/reporting.md
  - shared/jqschema.md
  - shared/python-dataviz.md
```

Para fluxos de trabalho de análise somente leitura com visualização.

### A Pilha do Pesquisador

```markdown
imports:
  - shared/reporting.md
  - shared/mcp/tavily.md
  - shared/mcp/arxiv.md
```

Para fluxos de trabalho de pesquisa que precisam de pesquisa na web e artigos acadêmicos.

### A Pilha de Inteligência de Código

```markdown
imports:
  - shared/reporting.md
  - shared/mcp/serena.md
  - shared/mcp/ast-grep.md
```

Para análise semântica de código e refatoração.

### A Pilha de Meta-Agente

```markdown
imports:
  - shared/reporting.md
  - shared/mcp/gh-aw.md
  - shared/charts-with-trending.md
```

Para fluxos de trabalho que analisam outros fluxos de trabalho.

## O Que Vem a Seguir?

O sistema de imports permitiu o escalonamento rápido, mas até os melhores componentes precisam de bases de segurança adequadas. Toda a reutilização do mundo não ajuda se os agentes puderem causar danos acidentalmente.

Em nosso próximo artigo, exploraremos as lições de segurança aprendidas operando nossa coleção de fluxos de trabalho agentic automatizados com acesso a repositórios reais.

_Mais artigos nesta série em breve._

[Artigo Anterior](/gh-aw/blog/2026-01-27-operational-patterns/)
