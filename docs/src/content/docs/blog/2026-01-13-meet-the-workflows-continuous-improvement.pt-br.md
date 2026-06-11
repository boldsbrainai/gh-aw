---
title: "Conheça os Workflows: Melhoria Contínua"
description: "Agentes que adotam uma visão holística da saúde do repositório"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-13T02:45:00
sidebar:
  label: "Melhoria Contínua"
prev:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-continuous-style/
  label: "Conheça os Workflows: Estilo Contínuo"
next:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-documentation/
  label: "Conheça os Workflows: Documentação Contínua"
---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

Bem-vindo de volta à [Fábrica de Agentes do Peli](/gh-aw/blog/2026-01-12-welcome-to-pelis-agent-factory/)!

Em nossas [postagens anteriores](/gh-aw/blog/2026-01-13-meet-the-workflows-continuous-simplicity/), exploramos agentes de limpeza autônomos. Agora, completamos o quadro com agentes que analisam dependências, segurança de tipos e a qualidade geral do repositório.

## Workflows de Melhoria Contínua

- **[Especialista em Uso de Módulos Go (aka Go Fan)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/go-fan.md?plain=1)** - Revisor diário de uso de módulos Go
- **[Tipador (Typist)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/typist.md?plain=1)** - Analisa padrões de uso de tipos para maior segurança
- **[Pragmático Funcional (Functional Pragmatist)](https://github.com/github/gh-aw/blob/main/.github/workflows/functional-programming-enhancer.md?plain=1)** - Aplica técnicas funcionais de forma pragmática
- **[Melhorador de Qualidade de Repositório (Repository Quality Improver)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/repository-quality-improver.md?plain=1)** - Análise holística de qualidade de código

### Especialista em Uso de Módulos Go: O Entusiasta de Dependências 🐹

O **Especialista em Uso de Módulos Go** é talvez o fluxo de trabalho com a caracterização mais singular da fábrica - um "entusiasta especialista em módulos Go" que realiza revisões diárias profundas das dependências Go do projeto. Isso não é apenas escaneamento de dependências - é uma análise cuidadosa de **quão bem estamos usando as ferramentas que escolhemos**.

A maioria das ferramentas de dependência foca em vulnerabilidades ou versões desatualizadas. O Especialista em Uso de Módulos Go faz perguntas mais profundas e positivas: Estamos usando os melhores recursos deste módulo? Atualizações recentes introduziram padrões melhores que deveríamos adotar? Poderíamos usar um módulo mais apropriado para este caso de uso? Estamos seguindo as práticas recomendadas do módulo?

O Especialista em Uso de Módulos Go usa um algoritmo de seleção inteligente. Ele extrai dependências diretas de `go.mod`, busca metadados do GitHub para cada dependência, incluindo a data da última atualização, classifica pela recência para priorizar módulos atualizados recentemente, usa seleção round-robin para garantir cobertura abrangente e mantém memória persistente por meio de cache-memory para rastrear quais módulos foram revisados recentemente.

Isso garante que os módulos atualizados recentemente sejam revisados primeiro (já que novos recursos podem ser relevantes), que todos os módulos sejam eventualmente revisados para que nada seja esquecido, e que as revisões não se repitam desnecessariamente graças ao rastreamento por cache.

Para cada módulo, o Especialista em Uso de Módulos Go pesquisa o repositório (releases, docs, práticas recomendadas), analisa padrões de uso reais usando o Serena e gera recomendações acionáveis. Ele salva resumos em `scratchpad/mods/` e abre Discussões no GitHub.

A saída do Especialista em Uso de Módulos Go é uma discussão, que é então frequentemente "minerada" por tarefas acionáveis usando o padrão de design [ResearchPlanAssignOps](https://github.github.com/gh-aw/patterns/research-plan-assign-ops/).

Vamos dar uma olhada em um exemplo de como isso funciona:

1. O Especialista em Uso de Módulos Go criou a discussão [Go Module Review: actionlint](https://github.com/github/gh-aw/discussions/7472) após notar que o módulo `actionlint` foi atualizado.
2. Peli [solicitou ao agente de Plano](https://github.com/github/gh-aw/discussions/7472#discussioncomment-15342254) que minerasse tarefas acionáveis.
3. Isso criou [uma issue pai](https://github.com/github/gh-aw/issues/7648) e 5 subtarefas.
4. As subtarefas foram então resolvidas por execuções posteriores do fluxo de trabalho. Um exemplo de PR é [Implementar execução paralela multi-arquivo do actionlint](https://github.com/github/gh-aw/issues/7649).

Por meio deste padrão de cadeia causal multi-agente, o Especialista em Uso de Módulos Go gerou **58 PRs mesclados de 74 propostos (taxa de mesclagem de 78%)** em 67 revisões de módulos. Cadeias notáveis incluem: melhorias no spinner (4 PRs da [revisão de briandowns/spinner](https://github.com/github/gh-aw/discussions/5094)), upgrade do MCP SDK v1.2.0 (5 PRs da [revisão do go-sdk](https://github.com/github/gh-aw/discussions/7710)) e revisão do estilo de terminal (3 PRs da [revisão de lipgloss](https://github.com/github/gh-aw/discussions/5158)).

### Tipador: O Defensor da Segurança de Tipos

O **Tipador** analisa os padrões de uso de tipos Go com foco singular: melhorar a segurança de tipos. Ele caça código sem tipagem que deveria ser fortemente tipado e identifica definições de tipo duplicadas que criam confusão.

O Tipador procura por usos sem tipagem: `interface{}` ou `any` onde tipos específicos seriam melhores, constantes sem tipagem que deveriam ter tipos explícitos e asserções de tipo que poderiam ser eliminadas com um design melhor. Ele também caça definições de tipo duplicadas - os mesmos tipos definidos em múltiplos pacotes, tipos similares com nomes diferentes e apelidos de tipo que poderiam ser unificados.

Usando padrões grep e análise semântica do Serena, ele descobre definições de tipo, identifica duplicatas semânticas, analisa padrões de uso sem tipagem e gera recomendações de refatoração.

O Tipador também usa o padrão [ResearchPlanAssignOps](https://github.github.com/gh-aw/patterns/research-plan-assign-ops/). Isso significa que o trabalho do Tipador não é corrigir o código, mas analisar o código e recomendar melhorias possíveis.

Vamos dar uma olhada em um exemplo disso na prática:

- O Tipador criou a discussão [Typist - Go Type Consistency Analysis Report](https://github.com/github/gh-aw/discussions/4082). Isso usou grep e outras ferramentas para realizar uma análise abrangente examinando 208 arquivos Go que não eram de teste.
- O relatório encontrou 477 instâncias de uso de `map[string]any`, 36 constantes sem tipagem e 30+ usos de `any` em assinaturas de função.
- [Peli solicitou `/plan` nessa issue](https://github.com/github/gh-aw/discussions/4082#discussioncomment-14983559), fazendo com que o agente de Plano realizasse pesquisas adicionais e criasse 5 issues para trabalho, como [Criar struct ToolsConfig unificada em tools_types.go](https://github.com/github/gh-aw/issues/4155).
- 4/5 dessas issues foram então resolvidas pelo Copilot. Por exemplo [Adicionar struct ToolsConfig unificada para substituir o padrão map[string]any](https://github.com/github/gh-aw/pull/4158).

Por meio dessa cadeia multi-agente, o Tipador produziu **19 PRs mesclados de 25 propostos (taxa de mesclagem de 76%)** de 57 discussões → 22 issues → 25 PRs. O exemplo do blog (Discussão #4082 → Issue #4155 → PR #4158) é uma cadeia causal verificada.

O debate sobre tipagem estática vs. dinâmica dura décadas. As linguagens híbridas de hoje, como Go, C#, TypeScript e F#, suportam ambas as tipagens. A melhoria contínua de tipos oferece **uma perspectiva nova e refrescante sobre esse antigo debate**: em vez de impor tipagem estrita desde o início, podemos desenvolver rapidamente com flexibilidade e, em seguida, deixar que agentes autônomos como o Tipador nos sigam, fortalecendo a segurança de tipos ao longo do tempo. Isso nos permite obter o melhor dos dois mundos: desenvolvimento rápido sem ficar atolado no design de tipos, enquanto ainda alcançamos forte tipagem e segurança à medida que a base de código amadurece.

### Pragmático Funcional: O Purista Pragmático 🔄

O **Pragmático Funcional** aplica técnicas moderadas de programação funcional para melhorar a clareza e a segurança do código, equilibrando o pragmatismo com princípios funcionais.

O fluxo de trabalho foca em sete padrões: imutabilidade, inicialização funcional, operações transformativas (map/filter/reduce), padrão de opções funcionais, evitar estado mutável compartilhado, funções puras e wrappers de lógica reutilizáveis.

Ele busca por oportunidades (variáveis mutáveis, loops imperativos, anti-padrões de inicialização, estado global), pontua por melhorias de segurança/clareza/testabilidade, usa o Serena para análise profunda e implementa mudanças como conversão para literais compostos, uso de opções funcionais, eliminação de globais, extração de funções puras e criação de wrappers reutilizáveis (Retry, WithTiming, Memoize).

O fluxo de trabalho é pragmático: o estilo simples do Go é respeitado, os loops for permanecem quando mais claros e a abstração é adicionada apenas onde genuinamente melhora o código. Ele é executado nas manhãs de terça e quinta-feira, melhorando sistematicamente os padrões ao longo do tempo.

Um exemplo de PR do nosso próprio uso deste fluxo de trabalho é [Aplicar melhorias de programação funcional e imutabilidade](https://github.com/github/gh-aw/pull/12921).

O Pragmático Funcional (originalmente chamado de "Aprimorador Funcional") é uma adição recente - até agora ele criou **2 PRs (ambos mesclados, taxa de mesclagem de 100%)**, demonstrando que sua abordagem pragmática aos padrões funcionais é bem recebida.

### Melhorador de Qualidade de Repositório: O Analista Holístico

O **Melhorador de Qualidade de Repositório** adota a visão mais ampla, selecionando uma *área de foco* diferente a cada dia para analisar o repositório sob essa perspectiva.

Ele usa cache-memory para garantir cobertura diversificada: 60% áreas customizadas (preocupações específicas do repositório), 30% categorias padrão (qualidade de código, documentação, teste, segurança, desempenho) e 10% revisitas para consistência.

As categorias padrão cobrem os fundamentos. As áreas customizadas são específicas do repositório: consistência de mensagens de erro, convenções de nomenclatura de flags CLI, padrões de geração de YAML de fluxo de trabalho, formatação de saída de console, validação de configuração.

O fluxo de trabalho carrega o histórico recente, seleciona a próxima área, gasta 20 minutos em análise profunda, gera discussões com recomendações e salva o estado. Ele procura preocupações transversais que não se encaixam perfeitamente em outras categorias, mas que impactam a qualidade geral.

Exemplos de relatórios do nosso próprio uso deste fluxo de trabalho são:

- [Melhoria da Qualidade do Repositório - Otimização de CI/CD](https://github.com/github/gh-aw/discussions/6863)
- [Relatório de Melhoria da Qualidade do Repositório - Desempenho](https://github.com/github/gh-aw/discussions/13280).

Por meio de sua cadeia causal multi-agente (59 discussões → 30 issues → 40 PRs), o Melhorador de Qualidade de Repositório produziu **25 PRs mesclados de 40 propostos (taxa de mesclagem de 62%)**, adotando uma visão holística da qualidade sob múltiplos ângulos.

## O Poder da Melhoria Contínua

Esses fluxos de trabalho completam o quadro de melhoria autônoma: Especialista em Uso de Módulos Go mantém as dependências novas, Tipador fortalece a segurança de tipos, Pragmático Funcional aplica técnicas funcionais e Melhorador de Qualidade de Repositório mantém a coerência.

Combinado com fluxos de trabalho anteriores, temos agentes melhorando o código em todos os níveis: saída em nível de linha (Estilista de Terminal), complexidade em nível de função (Simplificador de Código), organização em nível de arquivo (Refatorador Semântico de Função), consistência em nível de padrão (Detector de Padrões Go), clareza funcional (Pragmático Funcional), segurança de tipos (Tipador), dependências de módulo (Especialista em Uso de Módulos Go) e coerência do repositório (Melhorador de Qualidade de Repositório).

Este é o futuro da qualidade do código: não sprints periódicos de limpeza, mas melhoria autônoma contínua em todas as dimensões simultaneamente.

## Usando estes Workflows

Você pode adicionar esses fluxos de trabalho ao seu próprio repositório e remixá-los. Comece com nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/), depois execute um dos seguintes:

**Especialista em Uso de Módulos Go:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/go-fan.md
```

**Tipador:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/typist.md
```

**Pragmático Funcional:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/main/.github/workflows/functional-programming-enhancer.md
```

**Melhorador de Qualidade de Repositório:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/repository-quality-improver.md
```

Em seguida, edite e remixe as especificações do fluxo de trabalho para atender às suas necessidades, regenere o arquivo de bloqueio usando `gh aw compile` e envie para o seu repositório. Veja nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/) para obter mais instruções de instalação e configuração.

Você também pode [criar seus próprios fluxos de trabalho](/gh-aw/setup/creating-workflows/).

## Saiba mais

- **[GitHub Agentic Workflows](https://github.github.com/gh-aw/)** - A tecnologia por trás dos fluxos de trabalho
- **[Início Rápido](https://github.github.com/gh-aw/setup/quick-start/)** - Como escrever e compilar fluxos de trabalho

---

*Esta é a parte 5 de uma série de 19 partes explorando os fluxos de trabalho na Fábrica de Agentes do Peli.*
