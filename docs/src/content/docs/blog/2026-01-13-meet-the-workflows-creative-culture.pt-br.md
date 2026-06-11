---
title: "Conheça os Workflows: Trabalho em Equipe e Cultura"
description: "Um tour curado de fluxos de trabalho criativos e de cultura que trazem alegria ao trabalho"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-13T09:00:00
sidebar:
  label: "Trabalho em Equipe e Cultura"
prev:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-security-compliance/
  label: "Workflows relacionados à Segurança"
next:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-interactive-chatops/
  label: "Workflows Interativos e ChatOps"
---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

*Ah, meus caros amigos!* Vamos explorar o *workshop lúdico* - o canto mais divertido da [Fábrica de Agentes do Peli](/gh-aw/blog/2026-01-12-welcome-to-pelis-agent-factory/)!

Em nossa [postagem anterior](/gh-aw/blog/2026-01-13-meet-the-workflows-security-compliance/), exploramos fluxos de trabalho de segurança e conformidade - os mecanismos de proteção essenciais que gerenciam campanhas de vulnerabilidade, validam a segurança da rede e evitam a exposição de credenciais. Esses fluxos de trabalho nos permitem dormir tranquilos sabendo que nossos agentes operam dentro de limites seguros.

Mas aqui está o ponto: o trabalho não precisa ser apenas negócios. Embora tenhamos construído fluxos de trabalho sérios e críticos para a produção para qualidade, releases e segurança, também descobrimos algo inesperado - os agentes de IA podem trazer alegria, construir cultura de equipe e criar momentos de deleite. Nem todo fluxo de trabalho precisa resolver um problema crítico; alguns podem simplesmente tornar o seu dia melhor. Vamos explorar o lado lúdico da nossa fábrica de agentes, onde aprendemos que a personalidade e a diversão impulsionam o engajamento tão poderosamente quanto a utilidade.

## Workflows de Trabalho em Equipe e Cultura

Estes agentes facilitam a comunicação da equipe e nos lembram que o trabalho pode ser divertido:

- **[Status Diário da Equipe (Daily Team Status)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-team-status.md?plain=1)** - Compartilha o humor da equipe e atualizações de status - **22 issues**, **17 discussões** (mais 2 PRs de cadeia causal!)
- **[Notícias Diárias (Daily News)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-news.md?plain=1)** - Faz a curadoria de notícias relevantes para a equipe - **45 discussões de digest de notícias**
- **[Bot de Poesia (Poem Bot)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/poem-bot.md?plain=1)** - Responde a comandos `/poem-bot` com versos criativos (sim, sério)
- **[Resumo Semanal de Issues (Weekly Issue Summary)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/weekly-issue-summary.md?plain=1)** - Cria resumos digeríveis completos com gráficos e tendências - **5 discussões de análise semanal**
- **[Crônica Diária do Repositório (Daily Repo Chronicle)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-repo-chronicle.md?plain=1)** - Narra a atividade do dia como um contador de histórias - **6 discussões de crônicas**

O Bot de Poesia começou como um capricho em nosso projeto Copilot para PRs em 2022. Alguém disse "não seria engraçado se tivéssemos um agente que escreve poemas sobre nosso código?" e então nós o construímos. O Bot de Poesia responde a comandos `/poem-bot` com versos criativos sobre código, adicionando um toque de capricho ao fluxo de trabalho de desenvolvimento. Aprendemos que os agentes de IA não precisam ser puramente profissionais - eles podem construir cultura e criar momentos de alegria.

As Notícias Diárias criaram **45 discussões de digest de notícias** curando desenvolvimentos relevantes para a equipe - por exemplo, [#6932](https://github.com/github/gh-aw/discussions/6932) com o resumo diário de status. Ele compartilha links, adiciona comentários e os conecta ao nosso trabalho.

O Status Diário da Equipe criou **22 issues** e **17 discussões** compartilhando atualizações diárias de status da equipe - por exemplo, [#6930](https://github.com/github/gh-aw/discussions/6930) com o relatório diário de status da equipe. Duas de suas issues levaram a PRs mesclados por agentes downstream, mostrando que mesmo fluxos de trabalho "leves" podem impulsionar melhorias concretas.

O Resumo Semanal de Issues criou **5 discussões de análise semanal** com resumos digeríveis, gráficos e tendências - por exemplo, [#5844](https://github.com/github/gh-aw/discussions/5844) analisando a semana de 1 a 8 de dezembro de 2025.

A Crônica Diária do Repositório criou **6 discussões de crônicas** narrando a atividade do repositório como um contador de histórias - por exemplo, [#6750](https://github.com/github/gh-aw/discussions/6750) narrando um surto de desenvolvimento com 42 PRs ativos.

Um tema aqui é a **redução da carga cognitiva**. Ter agentes que resumem e narram a atividade diária significa que não precisamos analisar mentalmente longas listas de issues ou PRs. Em vez disso, recebemos histórias digeríveis que destacam o que é importante. Isso libera largura de banda mental para o trabalho real.

Outro tema é que o **tom** pode ajudar a tornar as coisas mais agradáveis. A Crônica Diária do Repositório começou a escrever resumos em um estilo narrativo, quase jornalístico. As saídas dos agentes de IA não precisam ser robóticas - elas podem ter personalidade e ainda serem informativas.

Esses fluxos de trabalho de comunicação ajudam a construir a coesão da equipe e nos lembram que o trabalho pode ser encantador.

## Usando estes Workflows

Você pode adicionar esses fluxos de trabalho ao seu próprio repositório e remixá-los. Comece com nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/), depois execute um dos seguintes:

**Status Diário da Equipe:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-team-status.md
```

**Notícias Diárias:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-news.md
```

**Bot de Poesia:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/poem-bot.md
```

**Resumo Semanal de Issues:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/weekly-issue-summary.md
```

**Crônica Diária do Repositório:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-repo-chronicle.md
```

Em seguida, edite e remixe as especificações do fluxo de trabalho para atender às suas necessidades, regenere o arquivo de bloqueio usando `gh aw compile` e envie para o seu repositório. Veja nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/) para obter mais instruções de instalação e configuração.

Você também pode [criar seus próprios fluxos de trabalho](/gh-aw/setup/creating-workflows/).

## Saiba mais

- **[GitHub Agentic Workflows](https://github.github.com/gh-aw/)** - A tecnologia por trás dos fluxos de trabalho
- **[Início Rápido](https://github.github.com/gh-aw/setup/quick-start/)** - Como escrever e compilar fluxos de trabalho

## Próximo: Summon an Agent on Demand

Fluxos de trabalho agendados são ótimos, mas às vezes você precisa de ajuda *agora mesmo*. Entre os fluxos de trabalho interativos e ChatOps.

Continue lendo: [Workflows Interativos e ChatOps →](/gh-aw/blog/2026-01-13-meet-the-workflows-interactive-chatops/)

---

*Esta é a parte 12 de uma série de 19 partes explorando os fluxos de trabalho na Fábrica de Agentes do Peli.*
