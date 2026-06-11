---
title: "Conheça os Workflows: Simplicidade Contínua"
description: "Agentes que detectam complexidade e propõem soluções mais simples"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-13T02:00:00
sidebar:
  label: "Simplicidade Contínua"
prev:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows/
  label: "Conheça um Workflow de Triagem Simples"
next:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-continuous-refactoring/
  label: "Conheça os Workflows: Refatoração Contínua"
---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

Ah, que timing maravilhoso! Venha, venha, deixe-me mostrar as *próximas maravilhas* na [Fábrica de Agentes do Peli](/gh-aw/blog/2026-01-12-welcome-to-pelis-agent-factory/)!

Em nossa [postagem anterior](/gh-aw/blog/2026-01-13-meet-the-workflows/), exploramos como um fluxo de trabalho de triagem simples nos ajuda a manter o controle da atividade recebida - rotulando automaticamente as issues e reduzindo a carga cognitiva.

Agora vamos conhecer os agentes que trabalham silenciosamente em segundo plano para manter o código simples e limpo. Esses fluxos de trabalho incorporam um princípio poderoso: **qualidade de código não é um destino, é uma prática contínua**. Enquanto os desenvolvedores correm para implementar recursos e corrigir bugs, agentes de limpeza autônomos seguem atrás, constantemente varrendo, polindo e simplificando. Vamos conhecer os agentes que caçam a complexidade.

## Simplicidade Contínua

Os próximos dois agentes representam diferentes aspectos da simplicidade do código: detectar *código supercomplicado* e *lógica duplicada*:

- **[Simplificador Automático de Código (Automatic Code Simplifier)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/code-simplifier.md?plain=1)** - Analisa código modificado recentemente e cria PRs com simplificações
- **[Detector de Código Duplicado (Duplicate Code Detector)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/duplicate-code-detector.md?plain=1)** - Usa a análise semântica do Serena para identificar padrões de código duplicados

O **Simplificador Automático de Código** é executado diariamente, analisando o código modificado recentemente em busca de oportunidades de simplificação sem alterar a funcionalidade. Ele analisa o que mudou nos últimos commits e pergunta: "Isso poderia ser mais claro? Poderia ser mais curto? Poderia ser mais idiomático?"

Este fluxo de trabalho é particularmente valioso após sessões rápidas de desenvolvimento. Quando você está correndo para implementar um recurso ou corrigir um bug, o código frequentemente se torna mais complexo do que o necessário. Variáveis recebem nomes temporários, a lógica se torna aninhada, o tratamento de erros fica verboso. O fluxo de trabalho limpa incansavelmente após essas sessões de desenvolvimento, criando PRs que preservam a funcionalidade enquanto melhoram a clareza, a consistência e a manutenibilidade.

Os tipos de simplificações que ele propõe variam desde a extração de lógica repetida para funções auxiliares até a conversão de if-statements aninhados em retornos antecipados (early returns). Ele detecta oportunidades para simplificar expressões booleanas, usar funções da biblioteca padrão em vez de implementações customizadas e consolidar padrões similares de tratamento de erros.

O Simplificador de Código é uma adição recente - até agora ele criou **6 PRs (5 mesclados, taxa de mesclagem de 83%)**, como [extração de um helper de modo de ação para reduzir a duplicação de código](https://github.com/github/gh-aw/pull/13982) e [simplificação de código de configuração de validação para clareza](https://github.com/github/gh-aw/pull/13118).

O **Detector de Código Duplicado** usa análise de código semântico tradicional e testada em estrada em conjunto com raciocínio agentic para encontrar padrões duplicados. Ele entende o *significado* do código em vez de apenas a similaridade textual, capturando padrões onde:

- A mesma lógica aparece com nomes de variáveis diferentes
- Funções similares existem em arquivos diferentes
- Padrões repetidos poderiam ser extraídos para utilitários
- A estrutura é duplicada mesmo se a implementação diferir

O que torna este fluxo de trabalho especial é seu uso de análise semântica por meio do [Serena](https://oraios.github.io/serena/) - um poderoso kit de ferramentas de agente de codificação capaz de transformar um LLM em um agente com recursos completos que trabalha diretamente na sua base de código. Quando usamos o Serena, entendemos o código no nível resolvido pelo compilador, não apenas a sintaxe.

O fluxo de trabalho foca nas mudanças recentes nos últimos commits, filtrando de forma inteligente arquivos de teste, fluxos de trabalho e arquivos que não são de código. Ele cria issues apenas para duplicatas significativas: padrões que abrangem mais de 10 linhas ou que aparecem em 3 ou mais locais. Ele realiza uma análise de várias fases. Começa configurando o ambiente semântico do Serena para o repositório, então encontra arquivos `.go` e `.cjs` modificados, excluindo testes e fluxos de trabalho. Usando `get_symbols_overview` e `find_symbol`, ele entende a estrutura, identifica assinaturas de função e blocos de lógica similares e compara visões gerais de símbolos entre arquivos para similaridades mais profundas. Ele cria issues com o prefixo `[duplicate-code]` e limita-se a 3 issues por execução, evitando sobrecarga. As issues incluem referências específicas de arquivos, trechos de código e sugestões de refatoração.

Em nosso uso estendido do Detector de Código Duplicado, o agente levantou **76 PRs mesclados de 96 propostos (taxa de mesclagem de 79%)**, demonstrando o valor prático sustentado da análise de código semântico. Exemplos recentes incluem [refatoração de scripts de limpeza de entidade expirada para compartilhar o processamento de expiração](https://github.com/github/gh-aw/pull/13420) e [refatoração de handlers de atualização de saída segura para eliminar fluxo de controle duplicado](https://github.com/github/gh-aw/pull/8791).

## IA Contínua para Simplicidade - Um Novo Paradigma

Juntos, esses fluxos de trabalho apontam para **uma mudança emergente em como mantemos a qualidade do código**. Em vez de "sprints de limpeza" periódicos ou esperar que as revisões de código capturem a complexidade, temos agentes que limpam depois de nós e monitoram e propõem melhorias continuamente. Isso é especialmente valioso no desenvolvimento assistido por IA. Quando os desenvolvedores usam IA para escrever código mais rápido, esses agentes de limpeza garantem que a velocidade não sacrifique a simplicidade. Eles entendem os mesmos padrões que os humanos reconhecem, mas os aplicam de forma consistente em toda a base de código, todos os dias.

Os fluxos de trabalho nunca tiram um dia de folga, nunca se cansam e nunca deixam a dívida técnica se acumular. Eles incorporam o princípio de que o *bom o suficiente* sempre pode se tornar *melhor* e que melhorias incrementais se acumulam com o tempo.

## Usando estes Workflows

Você pode adicionar esses fluxos de trabalho ao seu próprio repositório e remixá-los. Comece com nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/), depois execute um dos seguintes:

**Simplificador Automático de Código:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/code-simplifier.md
```

**Detector de Código Duplicado:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/duplicate-code-detector.md
```

Em seguida, edite e remixe as especificações do fluxo de trabalho para atender às suas necessidades, regenere o arquivo de bloqueio usando `gh aw compile` e envie para o seu repositório. Veja nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/) para obter mais instruções de instalação e configuração.

Você também pode [criar seus próprios fluxos de trabalho](/gh-aw/setup/creating-workflows/).

## Saiba mais

- **[GitHub Agentic Workflows](https://github.github.com/gh-aw/)** - A tecnologia por trás dos fluxos de trabalho
- **[Início Rápido](https://github.github.com/gh-aw/setup/quick-start/)** - Como escrever e compilar fluxos de trabalho

---

## Próximo: Refatoração Contínua

A simplificação é apenas o começo. Além de remover a complexidade, podemos usar agentes para melhorar continuamente o código de muitas outras maneiras. Nossas próximas postagens exploram esse tópico.

Continue lendo: [Refatoração Contínua →](/gh-aw/blog/2026-01-13-meet-the-workflows-continuous-refactoring/)

## Saiba mais

- **[GitHub Agentic Workflows](https://github.github.com/gh-aw/)** - A tecnologia por trás dos fluxos de trabalho
- **[Início Rápido](https://github.github.com/gh-aw/setup/quick-start/)** - Como escrever e compilar fluxos de trabalho

---

*Esta é a parte 2 de uma série de 19 partes explorando os fluxos de trabalho na Fábrica de Agentes do Peli.*
