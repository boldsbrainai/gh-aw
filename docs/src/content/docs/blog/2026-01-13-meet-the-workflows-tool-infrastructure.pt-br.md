---
title: "Conheça os Workflows: Ferramentas e Infraestrutura"
description: "Um tour curado de fluxos de trabalho de infraestrutura que monitoram os sistemas agentic"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-13T12:00:00
sidebar:
  label: "Ferramentas e Infraestrutura"
prev:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-testing-validation/
  label: "Workflows de Teste e Validação"
next:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-multi-phase/
  label: "Workflows de Melhoria de Múltiplas Fases"
---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

*Encantado em ter você de volta* em nossa jornada pela [Fábrica de Agentes do Peli](/gh-aw/blog/2026-01-12-welcome-to-pelis-agent-factory/)! Agora, prepare-se para algo *bastante peculiar* - a sala onde assistimos aos observadores!

Em nossa [postagem anterior](/gh-aw/blog/2026-01-13-meet-the-workflows-testing-validation/), exploramos fluxos de trabalho de teste e validação que verificam continuamente se nossos sistemas funcionam corretamente - executando testes de fumaça, verificando a documentação em dispositivos e capturando regressões antes que os usuários as percebam. Aprendemos que a confiança deve ser verificada.

Mas aqui está uma pergunta que nos tirou o sono: e se a *própria infraestrutura* falhar? E se os servidores MCP estiverem mal configurados, as ferramentas ficarem indisponíveis ou os agentes não puderem acessar os recursos de que precisam? Testar o *aplicativo* é uma coisa; monitorar a *plataforma* que executa os agentes de IA é outra fera inteiramente diferente. Os fluxos de trabalho de ferramentas e infraestrutura fornecem meta-monitoramento - eles observam os observadores, validam configurações e garantem que o encanamento invisível permaneça funcional. Bem-vindo à camada onde monitoramos agentes monitorando agentes monitorando código. Sim, fica muito meta.

## Workflows de Ferramentas e Infraestrutura

Estes agentes monitoram e analisam a própria infraestrutura agentic:

- **[Inspetor MCP (MCP Inspector)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/mcp-inspector.md?plain=1)** - Valida configurações do Protocolo de Contexto de Modelo - garante que os agentes possam acessar ferramentas
- **[Relatório de Ferramentas GitHub MCP (GitHub MCP Tools Report)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/github-mcp-tools-report.md?plain=1)** - Analisa ferramentas MCP disponíveis - **5 PRs mesclados de 6 propostos (taxa de mesclagem de 83%)**
- **[Analisador de Desempenho do Agente (Agent Performance Analyzer)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/agent-performance-analyzer.md?plain=1)** - Meta-orquestrador para a qualidade do agente - **29 issues criadas, 14 levando a PRs (8 mesclados)**

A infraestrutura para agentes de IA é diferente da infraestrutura tradicional - você precisa validar que as ferramentas estão disponíveis, configuradas corretamente e realmente funcionando. O Inspetor MCP valida continuamente as configurações do servidor do Protocolo de Contexto de Modelo (Model Context Protocol), porque um servidor MCP mal configurado significa que um agente não pode acessar as ferramentas de que precisa.

O Gerador de Relatório de Ferramentas GitHub MCP contribuiu com **5 PRs mesclados de 6 propostos (taxa de mesclagem de 83%)**, analisando a disponibilidade de ferramentas MCP e mantendo as configurações de ferramentas atualizadas. Por exemplo, o [PR #13169](https://github.github.com/gh-aw/pull/13169) atualiza as configurações de ferramenta do servidor MCP.

O Analisador de Desempenho do Agente criou **29 issues** identificando problemas de desempenho em todo o ecossistema de agentes, e **14 dessas issues levaram a PRs** (8 mesclados) por agentes downstream - por exemplo, detectou que PRs de rascunho representavam 9,6% das PRs abertas, criou a issue #12168, que levou ao [#12174](https://github.com/github/gh-aw/pull/12174) implementando limpeza automática de rascunhos.

Aprendemos que a **observabilidade em camadas** é crucial: você precisa de monitoramento no nível da infraestrutura (os servidores estão ativos?), no nível da ferramenta (os agentes podem acessar o que precisam?) e no nível do agente (eles estão apresentando um bom desempenho?).

Esses fluxos de trabalho fornecem visibilidade para o invisível.

## Usando estes Workflows

Você pode adicionar esses fluxos de trabalho ao seu próprio repositório e remixá-los. Comece com nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/), depois execute um dos seguintes:

**Inspetor MCP:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/mcp-inspector.md
```

**Relatório de Ferramentas GitHub MCP:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/github-mcp-tools-report.md
```

**Analisador de Desempenho do Agente:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/agent-performance-analyzer.md
```

Em seguida, edite e remixe as especificações do fluxo de trabalho para atender às suas necessidades, regenere o arquivo de bloqueio usando `gh aw compile` e envie para o seu repositório. Veja nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/) para obter mais instruções de instalação e configuração.

Você também pode [criar seus próprios fluxos de trabalho](/gh-aw/setup/creating-workflows/).

## Saiba mais

- **[GitHub Agentic Workflows](https://github.github.com/gh-aw/)** - A tecnologia por trás dos fluxos de trabalho
- **[Início Rápido](https://github.github.com/gh-aw/setup/quick-start/)** - Como escrever e compilar fluxos de trabalho

## Próximo: Workflows de Melhoria de Múltiplas Fases

A maioria dos fluxos de trabalho que vimos são sem estado - eles rodam, completam e desaparecem. Mas e se os agentes pudessem manter a memória ao longo dos dias?

Continue lendo: [Workflows de Melhoria de Múltiplas Fases →](/gh-aw/blog/2026-01-13-meet-the-workflows-multi-phase/)

---

*Esta é a parte 15 de uma série de 19 partes explorando os fluxos de trabalho na Fábrica de Agentes do Peli.*
