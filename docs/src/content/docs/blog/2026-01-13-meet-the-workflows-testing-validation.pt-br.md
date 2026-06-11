---
title: "Conheça os Workflows: Teste e Validação"
description: "Um tour curado de fluxos de trabalho de teste que mantêm tudo funcionando perfeitamente"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-13T11:00:00
sidebar:
  label: "Teste e Validação"
prev:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-interactive-chatops/
  label: "Workflows Interativos e ChatOps"
next:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-tool-infrastructure/
  label: "Workflows de Ferramentas e Infraestrutura"
---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

*Por aqui!* Vamos continuar nosso grand tour da [Fábrica de Agentes do Peli](/gh-aw/blog/2026-01-12-welcome-to-pelis-agent-factory/)! Dentro da *câmara de verificação* onde nada escapa ao escrutínio!

Em nossa [postagem anterior](/gh-aw/blog/2026-01-13-meet-the-workflows-interactive-chatops/), exploramos fluxos de trabalho de ChatOps - agentes que respondem a comandos de barra e reações do GitHub, fornecendo assistência sob demanda com contexto total.

Mas tornar o código *melhor* é apenas metade da batalha. Também precisamos garantir que ele continue *funcionando*. À medida que refatoramos, otimizamos e evoluímos nossa base de código, como saber que não quebramos nada? Como detectar regressões antes que os usuários o façam? É aí que entram os fluxos de trabalho de teste e validação - os guardiões céticos que verificam continuamente se nossos sistemas funcionam conforme o esperado. Aprendemos que a infraestrutura de IA precisa de verificações de saúde constantes, porque o que funcionou ontem pode falhar silenciosamente hoje. Esses fluxos de trabalho incorporam **confiar, mas verificar**.

## Workflows de Teste e Validação

Estes agentes mantêm tudo funcionando perfeitamente por meio de testes contínuos:

### Validação de Qualidade de Código e Testes

- **[Especialista Super Testify (Daily Testify Uber Super Expert)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-testify-uber-super-expert.md?plain=1)** - Analisa arquivos de teste diariamente e sugere melhorias baseadas em testify - **19 issues criadas**, **13 levaram a PRs mesclados (taxa de mesclagem de cadeia causal de 100%)**
- **[Aprimorador Diário de Testes (Daily Test Improver)](https://github.com/githubnext/agentics/blob/main/workflows/daily-test-improver.md?plain=1)** - Identifica lacunas de cobertura e implementa novos testes incrementalmente
- **[Verificação Diária de Qualidade do Compilador (Daily Compiler Quality Check)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-compiler-quality.md?plain=1)** - Analisa o código do compilador para garantir que atenda aos padrões de qualidade

### Validação de Experiência do Usuário e Integração

- **[Testador de Docs Multi-dispositivo (Daily Multi-device Docs Tester)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-multi-device-docs-tester.md?plain=1)** - Testa documentação em todos os dispositivos com Playwright - **2 PRs mesclados de 2 propostos (taxa de mesclagem de 100%)**
- **[Verificador de Consistência da CLI (CLI Consistency Checker)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/cli-consistency-checker.md?plain=1)** - Inspeciona a CLI em busca de inconsistências, erros de digitação e lacunas na documentação - **80 PRs mesclados de 102 propostos (taxa de mesclagem de 78%)**

### Otimização de CI/CD

- **[Coach de CI (CI Coach)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/ci-coach.md?plain=1)** - Analisa pipelines de CI e sugere otimizações - **9 PRs mesclados de 9 propostos (taxa de mesclagem de 100%)**
- **[Gerenciador de Saúde do Fluxo de Trabalho (Workflow Health Manager)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/workflow-health-manager.md?plain=1)** - Meta-orquestrador monitorando a saúde de todos os fluxos de trabalho agentic - **40 issues criadas**, **5 PRs diretos + 14 PRs de cadeia causal mesclados**

O Especialista em Testify Diário criou **19 issues** analisando a qualidade dos testes, e **13 dessas issues levaram a PRs mesclados** por agentes downstream - uma taxa de mesclagem de cadeia causal perfeita de 100%. Por exemplo, a [issue #13701](https://github.com/github/gh-aw/issues/13701) levou ao [#13722](https://github.com/github/gh-aw/pull/13722) modernizando testes de renderização de console com asserções testify. O Aprimorador Diário de Testes trabalha ao lado dele para identificar lacunas de cobertura e implementar novos testes.

O Testador de Docs Multi-dispositivo usa Playwright para testar nossa documentação em diferentes tamanhos de tela - criou **2 PRs (ambos mesclados)**, incluindo [adicionar --network host aos containers Docker do Playwright](https://github.com/github/gh-aw/pull/7158). Ele encontrou problemas de renderização móvel que nunca teríamos detectado manualmente. O Verificador de Consistência da CLI contribuiu com **80 PRs mesclados de 102 propostos (taxa de mesclagem de 78%)**, mantendo a consistência na interface e documentação da CLI. Exemplos recentes incluem [remover comandos da CLI não documentados](https://github.com/github/gh-aw/pull/12762) e [corrigir a documentação do comando upgrade](https://github.com/github/gh-aw/pull/11559).

O Coach de Otimização de CI contribuiu com **9 PRs mesclados de 9 propostos (taxa de mesclagem de 100%)**, otimizando pipelines de CI para velocidade e eficiência com execução perfeita. Exemplos incluem [remover dependências de teste desnecessárias](https://github.com/github/gh-aw/pull/13925) e [corrigir execução de teste duplicada](https://github.com/github/gh-aw/pull/8176).

O Gerenciador de Saúde do Fluxo de Trabalho criou **40 issues** monitorando a saúde de todos os outros fluxos de trabalho, com **25 dessas issues levando a 34 PRs** (14 mesclados) por agentes downstream - mais **5 PRs diretos mesclados**. Por exemplo, a [issue #14105](https://github.com/github/gh-aw/issues/14105) sobre um arquivo de runtime ausente levou ao [#14127](https://github.com/github/gh-aw/pull/14127) corrigindo a configuração do fluxo de trabalho.

Esses fluxos de trabalho incorporam o princípio: **confiar, mas verificar**. Só porque funcionou ontem não significa que funciona hoje.

## Usando estes Workflows

Você pode adicionar esses fluxos de trabalho ao seu próprio repositório e remixá-los. Comece com nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/), depois execute um dos seguintes:

**Especialista Super Testify:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-testify-uber-super-expert.md
```

**Aprimorador Diário de Testes:**

```bash
gh aw add-wizard githubnext/agentics/daily-test-improver
```

**Verificação Diária de Qualidade do Compilador:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-compiler-quality.md
```

**Testador de Docs Multi-dispositivo:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-multi-device-docs-tester.md
```

**Verificador de Consistência da CLI:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/cli-consistency-checker.md
```

**Coach de CI:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/ci-coach.md
```

**Gerenciador de Saúde do Fluxo de Trabalho:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/workflow-health-manager.md
```

Em seguida, edite e remixe as especificações do fluxo de trabalho para atender às suas necessidades, regenere o arquivo de bloqueio usando `gh aw compile` e envie para o seu repositório. Veja nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/) para obter mais instruções de instalação e configuração.

Você também pode [criar seus próprios fluxos de trabalho](/gh-aw/setup/creating-workflows/).

## Saiba mais

- **[GitHub Agentic Workflows](https://github.github.com/gh-aw/)** - A tecnologia por trás dos fluxos de trabalho
- **[Início Rápido](https://github.github.com/gh-aw/setup/quick-start/)** - Como escrever e compilar fluxos de trabalho

## Próximo: Monitoramento dos Monitores

Mas e quanto à infraestrutura em si? Quem observa os observadores? Hora de ser meta.

Continue lendo: [Workflows de Ferramentas e Infraestrutura →](/gh-aw/blog/2026-01-13-meet-the-workflows-tool-infrastructure/)

---

*Esta é a parte 14 de uma série de 19 partes explorando os fluxos de trabalho na Fábrica de Agentes do Peli.*
