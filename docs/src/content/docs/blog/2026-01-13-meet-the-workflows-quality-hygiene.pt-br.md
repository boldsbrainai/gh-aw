---
title: "Conheça os Workflows: Investigação de Falhas"
description: "Um tour curado de fluxos de trabalho proativos de investigação de falhas que mantêm a saúde da base de código"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-13T05:00:00
sidebar:
  label: "Investigação de Falhas"
prev:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-issue-management/
  label: "Workflows de Gerenciamento de Issues e PR"
next:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-metrics-analytics/
  label: "Workflows de Métricas e Analytics"
---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

*Ah, esplêndido!* Bem-vindo de volta à [Fábrica de Agentes do Peli](/gh-aw/blog/2026-01-12-welcome-to-pelis-agent-factory/)! Venha, deixe-me mostrar a câmara onde zeladores vigilantes investigam falhas antes que elas escalem!

Em nossa [postagem anterior](/gh-aw/blog/2026-01-13-meet-the-workflows-issue-management/), exploramos fluxos de trabalho de gerenciamento de issues e PR.

Agora vamos mudar da cerimônia de colaboração para a investigação de falhas.

Embora os fluxos de trabalho de issue nos ajudem a lidar com o que chega, os fluxos de trabalho de investigação de falhas atuam como zeladores vigilantes - detectando problemas antes que eles escalem e mantendo nossa base de código saudável. Esses são os agentes que investigam falhas de CI, detectam deriva de esquema e capturam mudanças de quebra antes dos usuários.

## Workflows de Investigação de Falhas

Estes são nossos zeladores diligentes - os agentes que detectam problemas antes que eles se tornem problemas maiores:

- **[CI Doctor](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/ci-doctor.md?plain=1)** - Investiga fluxos de trabalho com falha e abre issues de diagnóstico - **9 PRs mesclados de 13 propostos (taxa de mesclagem de 69%)**
- **[Verificador de Consistência de Esquema (Schema Consistency Checker)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/schema-consistency-checker.md?plain=1)** - Detecta quando esquemas, código e documentos se desviam - **55 discussões de análise** criadas
- **[Verificador de Mudanças de Quebra (Breaking Change Checker)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/breaking-change-checker.md?plain=1)** - Monitora mudanças que podem quebrar coisas para os usuários - cria issues de alerta

O CI Doctor (também conhecido como "CI Failure Doctor") foi um dos nossos fluxos de trabalho mais importantes. Em vez de nos afogarmos em notificações de falha de CI, agora recebemos falhas *oportunas* e *investigadas* com insights de diagnóstico reais. O agente não apenas nos diz que algo quebrou - ele analisa logs, identifica padrões, pesquisa problemas semelhantes do passado e até sugere correções - mesmo antes de o humano ter lido a notificação de falha. O CI Failure Doctor contribuiu com **9 PRs mesclados de 13 propostos (taxa de mesclagem de 69%)**, incluindo correções como [adição de verificações de pré-voo de download do módulo Go](https://github.com/github/gh-aw/pull/13740) e [adição de lógica de retry para evitar falhas 403 de proxy](https://github.com/github/gh-aw/pull/13155). Aprendemos que os agentes se destacam no trabalho tedioso de investigação que os humanos consideram exaustivo.

O Verificador de Consistência de Esquema criou **55 discussões de análise** examinando a deriva de esquema entre esquemas JSON, structs Go e documentação - por exemplo, [#7020](https://github.com/github/gh-aw/discussions/7020) analisando a consistência da lógica condicional em toda a base de código. Ele detectou desvios que teriam nos levado dias para notar manualmente.

O Verificador de Mudanças de Quebra é um fluxo de trabalho mais novo que monitora mudanças incompatíveis com versões anteriores e cria issues de alerta (por exemplo, [#14113](https://github.com/github/gh-aw/issues/14113) sinalizando atualizações de versão da CLI) antes que cheguem à produção.

Esses fluxos de trabalho de "higiene" tornaram-se nossa primeira linha de defesa, capturando problemas antes que chegassem aos usuários.

O CI Doctor inspirou uma gama crescente de fluxos de trabalho semelhantes dentro do GitHub, onde os agentes realizam investigações profundas de incidentes e falhas do site de forma proativa. Este é o futuro da excelência operacional: agentes de IA entrando imediatamente em ação para realizar uma investigação profunda, para uma resposta organizacional mais rápida.

## Usando estes Workflows

Você pode adicionar esses fluxos de trabalho ao seu próprio repositório e remixá-los. Comece com nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/), depois execute um dos seguintes:

**CI Doctor:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/ci-doctor.md
```

**Verificador de Consistência de Esquema:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/schema-consistency-checker.md
```

**Verificador de Mudanças de Quebra:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/breaking-change-checker.md
```

Em seguida, edite e remixe as especificações do fluxo de trabalho para atender às suas necessidades, regenere o arquivo de bloqueio usando `gh aw compile` e envie para o seu repositório. Veja nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/) para obter mais instruções de instalação e configuração.

Você também pode [criar seus próprios fluxos de trabalho](/gh-aw/setup/creating-workflows/).

## Saiba mais

- **[GitHub Agentic Workflows](https://github.github.com/gh-aw/)** - A tecnologia por trás dos fluxos de trabalho
- **[Início Rápido](https://github.github.com/gh-aw/setup/quick-start/)** - Como escrever e compilar fluxos de trabalho

## Próximo: Workflows de Métricas e Analytics

A seguir, veremos agentes que nos ajudam a entender se a coleção de agentes como um todo está funcionando bem. É aí que entram os fluxos de trabalho de métricas e analytics.

Continue lendo: [Workflows de Métricas e Analytics →](/gh-aw/blog/2026-01-13-meet-the-workflows-metrics-analytics/)

---

*Esta é a parte 8 de uma série de 19 partes explorando os fluxos de trabalho na Fábrica de Agentes do Peli.*
