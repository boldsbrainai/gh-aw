---
title: "Conheça os Workflows: Interativos e ChatOps"
description: "Um tour curado de fluxos de trabalho interativos que respondem a comandos"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-13T10:00:00
sidebar:
  label: "Interativos e ChatOps"
prev:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-creative-culture/
  label: "Workflows de Trabalho em Equipe e Cultura"
next:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-testing-validation/
  label: "Workflows de Teste e Validação"
---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

*Em frente, em frente!* Vamos continuar explorando as maravilhas da [Fábrica de Agentes do Peli](/gh-aw/blog/2026-01-12-welcome-to-pelis-agent-factory/)! Para o *centro de comando* onde a magia acontece instantaneamente!

Em nossa [postagem anterior](/gh-aw/blog/2026-01-13-meet-the-workflows-creative-culture/), exploramos fluxos de trabalho criativos e de cultura - agentes que trazem alegria, constroem a cultura da equipe e criam momentos de deleite. Descobrimos que os agentes de IA não precisam ser puramente profissionais; eles podem ter personalidade enquanto tornam o trabalho mais agradável.

Mas às vezes você precisa de ajuda *agora mesmo*, no momento exato em que está preso em um problema. Você não quer esperar por uma execução agendada - você quer convocar um agente especialista com um comando. É aí que entram os fluxos de trabalho interativos e o ChatOps. Esses agentes respondem a comandos de barra (slash commands) e reações do GitHub, fornecendo assistência sob demanda com contexto total da situação atual.

Aprendemos que o agente certo no momento certo com a informação certa é uma adição valiosa a um portfólio de agentes.

## Workflows Interativos e ChatOps

Estes agentes respondem a comandos, fornecendo assistência sob demanda sempre que você precisar:

- **[Q](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/q.md?plain=1)** - Otimizador de fluxo de trabalho que investiga o desempenho e cria PRs - **69 PRs mesclados de 88 propostos (taxa de mesclagem de 78%)**
- **[Revisor Rabugento (Grumpy Reviewer)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/grumpy-reviewer.md?plain=1)** - Realiza revisões de código críticas com personalidade - cria issues para agentes downstream
- **[Gerador de Workflow (Workflow Generator)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/workflow-generator.md?plain=1)** - Cria novos fluxos de trabalho a partir de solicitações de issue - cria estrutura de arquivos de fluxo de trabalho

Os fluxos de trabalho interativos mudaram a forma como pensamos sobre a invocação de agentes. Em vez de tudo rodar em um cronograma, eles respondem a comandos de barra e reações - `/q` convoca o otimizador de fluxo de trabalho, uma reação 🚀 aciona a análise. O Q (sim, nomeado em homenagem ao oficial de suprimentos de James Bond) tornou-se nosso solucionador de problemas - contribuiu com **69 PRs mesclados de 88 propostos (taxa de mesclagem de 78%)**, respondendo a comandos e investigando problemas de fluxo de trabalho sob demanda. Exemplos recentes incluem [correção do action-tag do fluxo de trabalho daily-fact](https://github.com/github/gh-aw/pull/14127) e [configuração de relatórios de triagem de PR com expiração de 1 dia](https://github.com/github/gh-aw/pull/13903).

O Revisor Rabugento realiza revisões de código opinativas, criando issues que sinalizam riscos de segurança e preocupações com a qualidade do código (por exemplo, [#13990](https://github.com/github/gh-aw/issues/13990) sobre gatilhos de eventos arriscados) para que agentes downstream corrijam. Ele nos deu feedback surpreendentemente valioso com um toque de audácia ("Esta função está tão aninhada que tem seu próprio CEP").

O Gerador de Workflow cria novos fluxos de trabalho agentic a partir de solicitações de issue, criando a estrutura dos arquivos de fluxo de trabalho markdown que outros agentes então refinam (por exemplo, [#13379](https://github.com/github/gh-aw/issues/13379) solicitando mudanças no modo AWF).

Aprendemos que **contexto é tudo** - esses agentes funcionam porque são invocados no momento certo com o contexto certo, não porque rodam em um cronograma.

## Usando estes Workflows

Você pode adicionar esses fluxos de trabalho ao seu próprio repositório e remixá-los. Comece com nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/), depois execute um dos seguintes:

**Q:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/q.md
```

**Revisor Rabugento:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/grumpy-reviewer.md
```

**Gerador de Workflow:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/workflow-generator.md
```

Em seguida, edite e remixe as especificações do fluxo de trabalho para atender às suas necessidades, regenere o arquivo de bloqueio usando `gh aw compile` e envie para o seu repositório. Veja nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/) para obter mais instruções de instalação e configuração.

Você também pode [criar seus próprios fluxos de trabalho](/gh-aw/setup/creating-workflows/).

## Saiba mais

- **[GitHub Agentic Workflows](https://github.github.com/gh-aw/)** - A tecnologia por trás dos fluxos de trabalho
- **[Início Rápido](https://github.github.com/gh-aw/setup/quick-start/)** - Como escrever e compilar fluxos de trabalho

## Próximo: Workflows de Teste e Validação

Embora os agentes de ChatOps respondam a comandos, também precisamos de fluxos de trabalho que verifiquem continuamente se nossos sistemas funcionam conforme o esperado.

Continue lendo: [Workflows de Teste e Validação →](/gh-aw/blog/2026-01-13-meet-the-workflows-testing-validation/)

---

*Esta é a parte 13 de uma série de 19 partes explorando os fluxos de trabalho na Fábrica de Agentes do Peli.*
