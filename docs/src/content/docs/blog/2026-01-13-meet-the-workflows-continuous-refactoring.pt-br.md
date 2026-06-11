---
title: "Conheça os Workflows: Refatoração Contínua"
description: "Agentes que identificam melhorias estruturais e refatoram o código sistematicamente"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-13T02:15:00
sidebar:
  label: "Conheça os Workflows: Refatoração Contínua"
prev:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-continuous-simplicity/
  label: "Conheça os Workflows: Simplicidade Contínua"
next:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-continuous-style/
  label: "Conheça os Workflows: Estilo Contínuo"
---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

Bem-vindo de volta à [Fábrica de Agentes do Peli](/gh-aw/blog/2026-01-12-welcome-to-pelis-agent-factory/)!

Em nossa [postagem anterior](/gh-aw/blog/2026-01-13-meet-the-workflows-continuous-simplicity/), conhecemos agentes automatizados que detectam complexidade e propõem soluções mais simples. Eles trabalham incansavelmente em segundo plano, limpando as coisas. Agora vamos explorar agentes similares que adotam uma visão estrutural mais profunda, estendendo a automação para a *refatoração estrutural*.

## Refatoração Contínua

Nossos dois próximos agentes analisam continuamente a estrutura do código, sugerindo melhorias sistemáticas:

- **[Refatorador Semântico de Função (Semantic Function Refactor)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/semantic-function-refactor.md?plain=1)** - Identifica oportunidades de refatoração que podemos ter perdido
- **[Simplificador de Arquivos Grandes (Large File Simplifier)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-file-diet.md?plain=1)** - Monitora tamanhos de arquivo e propõe a divisão de arquivos grandes

O fluxo de trabalho **Refatorador Semântico de Função** combina IA agentic com ferramentas de análise de código para analisar e abordar a estrutura de toda a base de código. Ele analisa todos os arquivos de código-fonte Go no diretório `pkg/` para identificar funções que podem estar no lugar errado.

À medida que as bases de código evoluem, as funções às vezes acabam em arquivos onde não deveriam estar. Os humanos lutam para notar esses problemas organizacionais porque trabalhamos em um arquivo de cada vez e focamos em fazer o código funcionar, em vez de onde ele vive.

O fluxo de trabalho realiza uma descoberta abrangente:

1. coletando algoritmicamente todos os nomes de funções de arquivos Go que não sejam de teste, e então
2. agrupando agêntica e semanticamente as funções por nome e propósito.

Ele então identifica funções que não se encaixam no tema atual de seus arquivos como outliers, usa análise de código semântico baseada no Serena para detectar possíveis duplicatas e cria issues recomendando refatoração consolidada. Essas issues podem então ser revisadas e abordadas por agentes de codificação.

O fluxo de trabalho segue o princípio de "um arquivo por funcionalidade": os arquivos devem ser nomeados de acordo com seu propósito principal, e as funções dentro de cada arquivo devem estar alinhadas com esse propósito. Ele fecha issues existentes com o prefixo `[refactor]` antes de criar novas. Isso evita o acúmulo de issues e garante que as recomendações permaneçam atuais.

Em nosso uso estendido de Refatoração Semântica de Função, o fluxo de trabalho impulsionou **112 PRs mesclados de 142 propostos (taxa de mesclagem de 79%)** por meio de cadeias causais - criando 99 issues de refatoração que agentes downstream transformam em mudanças de código. Por exemplo, a [issue #12291](https://github.com/github/gh-aw/issues/12291) analisando oportunidades de organização de código levou ao [PR #12363 dividindo permissions.go em módulos focados](https://github.com/github/gh-aw/pull/12363) (de 928 para 133 linhas).

Um exemplo de PR do nosso próprio uso deste fluxo de trabalho é [Mover funções de extração deslocadas para frontmatter_extraction.go](https://github.com/github/gh-aw/pull/7043).

### Simplificador de Arquivos Grandes: O Monitor de Tamanho

Arquivos grandes são um mau cheiro de código comum - eles frequentemente indicam limites pouco claros, responsabilidades mistas ou complexidade acumulada. O fluxo de trabalho **Simplificador de Arquivos Grandes** monitora diariamente os tamanhos dos arquivos e cria issues acionáveis quando os arquivos crescem demais.

O fluxo de trabalho é executado durante os dias úteis, analisando todos os arquivos de código-fonte Go no diretório `pkg/`. Ele identifica o maior arquivo, verifica se excede os limites de tamanho saudáveis e cria uma issue detalhada propondo como dividi-lo em arquivos menores e mais focados.

O que torna este fluxo de trabalho eficaz é seu foco e priorização. Em vez de sobrecarregar os desenvolvedores com issues sobre cada arquivo grande, ele cria no máximo uma issue, visando o maior infrator. O fluxo de trabalho também pula se uma issue `[file-diet]` aberta já existir, evitando trabalho duplicado.

Em nosso uso estendido, o Simplificador de Arquivos Grandes (também conhecido como "Dieta Diária de Arquivos") impulsionou **26 PRs mesclados de 33 propostos (taxa de mesclagem de 79%)** por meio de cadeias causais - criando 37 issues de dieta de arquivos visando os maiores, que os agentes downstream transformam em mudanças de código modulares. Por exemplo, a [issue #12535](https://github.com/github/gh-aw/issues/12535) visando add_interactive.go levou ao [PR #12545 refatorando-o em 6 módulos focados em domínio](https://github.com/github/gh-aw/pull/12545).

O fluxo de trabalho usa o Serena para análise de código semântico para entender os relacionamentos das funções e propor limites lógicos para a divisão. Ele conta linhas e analisa a estrutura do código para sugerir limites de módulo significativos que façam sentido.

## O Poder da Refatoração Contínua

Esses fluxos de trabalho demonstram como os agentes de IA podem manter continuamente o conhecimento institucional sobre a organização do código. Os benefícios se acumulam com o tempo: uma organização melhor torna o código mais fácil de encontrar, padrões consistentes reduzem a carga cognitiva, a duplicação reduzida melhora a manutenibilidade e uma estrutura limpa atrai mais limpeza. Eles são particularmente valiosos no desenvolvimento assistido por IA, onde o código é escrito rapidamente e as preocupações organizacionais podem ficar em segundo plano em relação à funcionalidade.

## Usando estes Workflows

Você pode adicionar esses fluxos de trabalho ao seu próprio repositório e remixá-los. Comece com nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/), depois execute um dos seguintes:

**Refatorador Semântico de Função:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/semantic-function-refactor.md
```

**Simplificador de Arquivos Grandes:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-file-diet.md
```

Em seguida, edite e remixe as especificações do fluxo de trabalho para atender às suas necessidades, regenere o arquivo de bloqueio usando `gh aw compile` e envie para o seu repositório. Veja nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/) para obter mais instruções de instalação e configuração.

Você também pode [criar seus próprios fluxos de trabalho](/gh-aw/setup/creating-workflows/).

## Saiba mais

- **[GitHub Agentic Workflows](https://github.github.com/gh-aw/)** - A tecnologia por trás dos fluxos de trabalho
- **[Início Rápido](https://github.github.com/gh-aw/setup/quick-start/)** - Como escrever e compilar fluxos de trabalho

---

## Próximo: Estilo Contínuo

Além da estrutura e organização, há outra dimensão da qualidade do código: apresentação e estilo. Como mantemos uma saída de console bonita e consistente e a formatação?

Continue lendo: [Conheça os Workflows: Estilo Contínuo →](/gh-aw/blog/2026-01-13-meet-the-workflows-continuous-style/)

## Saiba mais

- **[GitHub Agentic Workflows](https://github.github.com/gh-aw/)** - A tecnologia por trás dos fluxos de trabalho
- **[Início Rápido](https://github.github.com/gh-aw/setup/quick-start/)** - Como escrever e compilar fluxos de trabalho

---

*Esta é a parte 3 de uma série de 19 partes explorando os fluxos de trabalho na Fábrica de Agentes do Peli.*
