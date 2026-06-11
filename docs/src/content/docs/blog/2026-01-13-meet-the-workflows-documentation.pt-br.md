---
title: "Conheça os Workflows: Documentação Contínua"
description: "Um tour curado de fluxos de trabalho que mantêm documentação de alta qualidade"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-13T03:00:00
sidebar:
  label: "Documentação Contínua"
prev:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-continuous-improvement/
  label: "Workflows de Melhoria Contínua"
next:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-issue-management/
  label: "Workflows de Gerenciamento de Issues e PR"
---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

Aproxime-se, aproxime-se, e entre na *câmara de documentação* da [Fábrica de Agentes do Peli](/gh-aw/blog/2026-01-12-welcome-to-pelis-agent-factory/)! A pura imaginação encontra a precisão técnica neste canto mais encantador do nosso estabelecimento!

Em nossas [postagens anteriores](/gh-aw/blog/2026-01-13-meet-the-workflows-continuous-simplicity/), exploramos agentes de limpeza autônomos - fluxos de trabalho que melhoram continuamente a qualidade do código simplificando a complexidade, refatorando a estrutura, polindo o estilo e mantendo a saúde geral do repositório. Esses agentes nunca tiram um dia de folga, trabalhando silenciosamente para tornar nossa base de código melhor.

Agora, vamos abordar um dos desafios eternos do desenvolvimento de software: manter a documentação precisa e atualizada. O código evolui rapidamente; a documentação... nem tanto. A terminologia deriva, os exemplos de API ficam obsoletos, os decks de slides envelhecem e as postagens de blog fazem referência a recursos obsoletos. A questão não é "podem os agentes de IA escrever uma boa documentação?", mas sim "podem eles mantê-la à medida que o código muda?". Os fluxos de trabalho de documentação e conteúdo desafiam a sabedoria convencional sobre conteúdo técnico gerado por IA. Spoiler: a resposta envolve revisão humana, mas é muito melhor do que a alternativa (nenhuma documentação).

## Workflows de Documentação Contínua

Estes agentes mantêm documentação e conteúdo de alta qualidade:

- **[Atualizador Diário de Documentação (Daily Documentation Updater)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-doc-updater.md?plain=1)** - Revisa e atualiza a documentação para garantir precisão e integridade - **57 PRs mesclados de 59 propostos (taxa de mesclagem de 96%)**
- **[Mantenedor de Glossário (Glossary Maintainer)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/glossary-maintainer.md?plain=1)** - Mantém o glossário sincronizado com a base de código - **10 PRs mesclados de 10 propostos (taxa de mesclagem de 100%)**
- **[Desbloqueador de Documentação (Documentation Unbloat)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/unbloat-docs.md?plain=1)** - Revisa e simplifica a documentação reduzindo a verbosidade - **88 PRs mesclados de 103 propostos (taxa de mesclagem de 85%)**
- **[Testador de Documentação para Iniciantes (Documentation Noob Tester)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/docs-noob-tester.md?plain=1)** - Testa a documentação como um novo usuário faria, identificando passos confusos - **9 PRs mesclados (taxa de mesclagem de 43%)** via cadeia causal
- **[Mantenedor de Deck de Slides (Slide Deck Maintainer)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/slide-deck-maintainer.md?plain=1)** - Mantém decks de slides de apresentação - **2 PRs mesclados de 5 propostos (taxa de mesclagem de 40%)**
- **[Testador de Docs Multi-dispositivo (Multi-device Docs Tester)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-multi-device-docs-tester.md?plain=1)** - Testa o site de documentação em dispositivos móveis, tablets e desktops - **2 PRs mesclados de 2 propostos (taxa de mesclagem de 100%)**
- **[Auditor de Blog (Blog Auditor)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/blog-auditor.md?plain=1)** - Verifica se as postagens do blog estão acessíveis e contêm o conteúdo esperado - **6 auditorias concluídas** (5 aprovadas, 1 issue sinalizada)

A documentação é onde desafiamos a sabedoria convencional. Podem os agentes de IA escrever *boa* documentação?

O **Escritor de Docs Técnicos** gera docs de API a partir do código, mas, mais importante, ele os *mantém* - atualizando a documentação quando o código muda. O Mantenedor de Glossário detectou a deriva de terminologia ("estamos usando três termos diferentes para o mesmo conceito").

O **Mantenedor de Deck de Slides** mantém nossos materiais de apresentação atualizados sem atualizações manuais.

O **Testador de Docs Multi-dispositivo** usa Playwright para verificar se nosso site de documentação funciona em celulares, tablets e desktops - testando layouts responsivos, acessibilidade e elementos interativos. Ele detecta regressões visuais e problemas de layout que só aparecem em tamanhos de tela específicos.

O **Auditor de Blog** garante que as postagens do blog permaneçam precisas à medida que a base de código evolui - ele sinaliza exemplos de código desatualizados e links quebrados. O Auditor de Blog é um **fluxo de trabalho apenas de validação** que cria relatórios de auditoria em vez de mudanças de código. Ele executou **6 auditorias** (5 aprovadas, [1 sinalizou conteúdo desatualizado](https://github.com/github/gh-aw/issues/2162)), confirmando a precisão do blog.

O Testador de Documentação para Iniciantes merece menção especial pela sua natureza exploratória. Ele produziu **9 PRs mesclados de 21 propostos (taxa de mesclagem de 43%)** por meio de uma cadeia causal: 62 discussões analisadas → 21 issues criadas → 21 PRs. A menor taxa de mesclagem reflete a natureza exploratória deste fluxo de trabalho - ele identifica muitas melhorias potenciais, algumas das quais são ambiciosas demais para implementação imediata. Por exemplo, a [Discussão #8477](https://github.com/github/gh-aw/discussions/8477) levou à [Issue #8486](https://github.com/github/gh-aw/issues/8486) que gerou os PRs [#8716](https://github.com/github/gh-aw/pull/8716) e [#8717](https://github.com/github/gh-aw/pull/8717), ambos mesclados.

Docs geradas por IA precisam de revisão humana/agente, mas são dramaticamente melhores do que *nenhuma* documentação (que é frequentemente a alternativa). A validação pode ser automatizada em grande parte, liberando os escritores para focar na estruturação do conteúdo, tópico, clareza, tom e precisão.

Nesta coleção de agentes, adotamos uma abordagem heterogênea - alguns fluxos de trabalho geram conteúdo, outros o mantêm e outros validam. Outras abordagens são possíveis - todas as tarefas podem ser agrupadas em um único agente. Descobrimos que é mais fácil explorar o espaço usando múltiplos agentes, para separar preocupações, e isso nos encorajou a usar agentes para outras saídas de comunicação, como blogs e slides.

## Usando estes Workflows

Você pode adicionar esses fluxos de trabalho ao seu próprio repositório e remixá-los. Comece com nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/), depois execute um dos seguintes:

**Atualizador Diário de Documentação:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-doc-updater.md
```

**Mantenedor de Glossário:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/glossary-maintainer.md
```

**Desbloqueador de Documentação:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/unbloat-docs.md
```

**Testador de Documentação para Iniciantes:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/docs-noob-tester.md
```

**Mantenedor de Deck de Slides:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/slide-deck-maintainer.md
```

**Testador de Docs Multi-dispositivo:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-multi-device-docs-tester.md
```

**Auditor de Blog:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/blog-auditor.md
```

Em seguida, edite e remixe as especificações do fluxo de trabalho para atender às suas necessidades, regenere o arquivo de bloqueio usando `gh aw compile` e envie para o seu repositório. Veja nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/) para obter mais instruções de instalação e configuração.

Você também pode [criar seus próprios fluxos de trabalho](/gh-aw/setup/creating-workflows/).

## Saiba mais

- **[GitHub Agentic Workflows](https://github.github.com/gh-aw/)** - A tecnologia por trás dos fluxos de trabalho
- **[Início Rápido](https://github.github.com/gh-aw/setup/quick-start/)** - Como escrever e compilar fluxos de trabalho

## Próximo: Workflows de Gerenciamento de Issues e PR

Além de escrever código e documentos, precisamos gerenciar o fluxo de issues e pull requests. Como mantemos a colaboração suave e eficiente?

Continue lendo: [Workflows de Gerenciamento de Issues e PR →](/gh-aw/blog/2026-01-13-meet-the-workflows-issue-management/)

---

*Esta é a parte 6 de uma série de 19 partes explorando os fluxos de trabalho na Fábrica de Agentes do Peli.*
