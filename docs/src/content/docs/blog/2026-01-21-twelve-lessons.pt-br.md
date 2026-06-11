---
title: "12 Lições da Fábrica de Agentes de Peli"
description: "Insights chave sobre o que funciona, o que não funciona e como projetar ecossistemas de agentes eficazes"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-21
draft: true
prev:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows/
  label: Conheça os Workflows
next:
  link: /gh-aw/blog/2026-01-24-design-patterns/
  label: 12 Padrões de Projeto
---

[Anterior: Conheça os Workflows](/gh-aw/blog/2026-01-13-meet-the-workflows/)

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

*Que prazer vê-lo novamente* na Fábrica de Agentes de Peli! Venha, venha - deixe-me mostrar o que descobrimos na *câmara de lições*!

Em nosso [artigo anterior](/gh-aw/blog/2026-01-13-meet-the-workflows/), apresentamos os fluxos de trabalho (workflows) propriamente ditos. Agora, vamos falar sobre o que aprendemos.

Executar nossa coleção de fluxos de trabalho agentic automatizados na prática é... uma experiência e tanto. Vimos agentes terem sucesso espetacular, falharem de formas interessantes e nos surpreenderem constantemente. Ao longo do caminho, aprendemos lições valiosas sobre o que realmente faz ecossistemas de agentes funcionarem.

Aqui está o que descobrimos até agora.

## As 12 Lições Chave

### A Diversidade Supera a Perfeição

Nenhum agente sozinho consegue fazer tudo - e isso é perfeitamente aceitável. Uma coleção de agentes focados, cada um fazendo bem uma coisa, funciona melhor do que tentar construir um assistente universal único. Em vez de passar meses aperfeiçoando um "super agente", começamos a disponibilizar agentes especializados rapidamente.

### As Guardrails (Barreiras) Possibilitam a Inovação

Algo contraintuitivo que descobrimos é que restrições rígidas tornam *mais fácil* experimentar. [Safe outputs](https://github.github.com/gh-aw/reference/safe-outputs/), permissões limitadas, ferramentas permitidas - eles não nos atrasam. Eles nos dão a confiança para avançar rapidamente porque sabemos o raio de explosão de qualquer falha.

Com limites claros estabelecidos, podemos prototipar novos agentes sem medo de quebrar a produção. Safe outputs impedem que agentes deletem código acidentalmente ou fechem issues críticas. Listas de permissão de rede garantem que agentes não possam vazar dados para serviços não autorizados. Essas barreiras nos dão permissão para inovar com ousadia.

### Meta-Agentes São Essenciais

Agentes que observam outros agentes? Parece meta, mas eles se tornaram alguns dos nossos fluxos de trabalho mais valiosos. Eles detectam problemas precocemente e nos ajudam a entender o que está acontecendo em todo o ecossistema.

Depois que passamos de 50 fluxos de trabalho, rastrear tudo manualmente tornou-se impossível. Meta-agentes como [Audit Workflows](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/audit-workflows.md) e [Agent Performance Analyzer](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/agent-performance-analyzer.md) nos dão a camada de observabilidade que precisávamos desesperadamente. Eles detectam padrões entre execuções, identificam agentes com dificuldades e revelam problemas sistêmicos que nunca veríamos olhando para fluxos de trabalho individuais.

### A Personalidade Importa

Descobrimos que agentes com personalidades distintas - como o auditor meticuloso, o zelador prestativo, o poeta criativo - são muito mais fáceis para as equipes entenderem e confiarem.

Notamos que nomes genéricos como "issue-handler" ou "code-checker" geravam confusão. Mas quando demos personalidades aos agentes - como [Grumpy Reviewer](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/grumpy-reviewer.md) ou [Poem Bot](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/poem-bot.md) - seus propósitos tornaram-se imediatamente claros. Os membros da equipe começaram a desenvolver relacionamentos com agentes específicos. É adorável.

### As Trocas entre Custo e Qualidade São Reais

Análises mais longas e completas custam mais - mas nem sempre são melhores. O [Portfolio Analyst](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/portfolio-analyst.md) nos ajuda a descobrir quais agentes realmente entregam valor.

Descobrimos que alguns de nossos agentes "completos" faziam trabalho redundante ou geravam relatórios que ninguém lia. O Portfolio Analyst rastreia o custo por insight entre todos os agentes, revelando que agentes simples e focados geralmente entregam melhor ROI (retorno sobre investimento) do que os complexos. Isso nos levou a consolidar agentes sobrepostos e ajustar o tamanho dos prompts para equilibrar completude com custo. I.A. não é de graça, pessoal!

### Fluxos de Trabalho Multifásicos Possibilitam Metas Ambiciosas

Dividir melhorias complexas em fluxos de trabalho de 3 fases (pesquisa → configuração → implementação) permite que os agentes lidem com projetos que seriam grandes demais para uma única execução. Cada fase se baseia na anterior, com feedback humano entre elas.

Agentes de execução única atingem limites rapidamente - limitados pelo contexto de tokens e tempo de execução. Mas fluxos de trabalho multifásicos como [Daily Test Improver](https://github.com/githubnext/agentics/blob/main/workflows/daily-test-improver.md) e [Daily Perf Improver](https://github.com/githubnext/agentics/blob/main/workflows/daily-perf-improver.md) podem abordar projetos ambiciosos distribuindo o trabalho ao longo de vários dias. A fase de pesquisa explora o problema, a fase de configuração prepara a infraestrutura e a fase de implementação executa as mudanças. Pontos de controle humanos entre as fases mantêm tudo alinhado com as metas da equipe.

### Slash Commands Criam Interfaces de Usuário Naturais

Gatilhos `/comando` ao estilo ChatOps fazem os agentes parecerem membros reais da equipe. Os usuários podem invocar capacidades poderosas com comentários simples, e o controle por função (role-gating) garante que apenas pessoas autorizadas possam disparar operações sensíveis.

Em vez de lembrar URLs de webhook complexas ou sintaxe de GitHub Actions, os membros da equipe apenas comentam `/grumpy` em um PR para uma revisão crítica, ou `/pr-fix` para consertar testes que falharam. O controle por função evita abusos, mantendo a interface extremamente simples. Esse padrão funciona tão bem que a maioria dos nossos agentes interativos o usa agora.

### Heartbeats (Batimentos Cardíacos) Constroem Confiança

Testes de validação frequentes e leves (a cada 12 horas) detectam regressões rapidamente. Esses agentes "heartbeat" mantêm a infraestrutura saudável sem monitoramento manual.

Em vez de esperar por falhas em produção, implantamos múltiplos [fluxos de trabalho de teste de fumaça (smoke tests)](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/smoke-copilot.md) que validam continuamente a funcionalidade principal. Quando um teste de fumaça falha, sabemos imediatamente qual componente quebrou. Esse monitoramento proativo previne falhas em cascata e nos dá confiança de que o ecossistema está realmente estável.

### A Inspeção por MCP É Essencial

À medida que os fluxos de trabalho começam a usar múltiplos servidores MCP, ter agentes que podem validar e relatar a disponibilidade de ferramentas torna-se crítico. O padrão [MCP Inspector](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/mcp-inspector.md) evita aquelas falhas crípticas de "ferramenta não disponível".

No início, víamos agentes falharem com erros vagos como "conexão recusada". O MCP Inspector verifica proativamente todas as configurações de servidor MCP, valida o acesso à rede e gera relatórios de status. Essa visibilidade transformou a depuração de horas de trabalho de detetive em apenas ler um painel.

### Enfileiramento de Tarefas Está em Todo Lugar

O padrão de enfileiramento de tarefas forneceu uma maneira simples de enfileirar e distribuir trabalho entre várias execuções de fluxo de trabalho. Dividir grandes projetos em tarefas discretas permitiu um progresso incremental com rastreamento claro de estado, registrando tarefas como issues, discussões ou cartões de projeto.

Seja gerenciando um backlog de trabalho de refatoração, coordenando correções de segurança ou distribuindo tarefas de criação de testes, o padrão de enfileiramento de tarefas apareceu repetidamente. Representando o trabalho como primitivas do GitHub (issues, cartões de projeto), obtivemos gerenciamento de estado, persistência e trilhas de auditoria integrados, sem construir infraestrutura personalizada.

### Análise de ML Revela Padrões Ocultos

Aplicar agrupamento (clustering) e PLN (processamento de linguagem natural) às interações dos agentes revelou padrões de uso que não eram óbvios em execuções individuais. Essa meta-análise ajudou a identificar oportunidades de consolidação e otimização.

Os fluxos de trabalho [Prompt Clustering Analysis](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/prompt-clustering-analysis.md) e [Copilot PR NLP Analysis](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/copilot-pr-nlp-analysis.md) descobriram que muitos agentes faziam perguntas semelhantes ou realizavam análises redundantes. Esse insight levou a bibliotecas de componentes compartilhados e oportunidades de consolidação que não teríamos notado através de revisão manual.

## Desafios que Encontramos

Nem tudo foram flores. Enfrentamos vários desafios que nos ensinaram lições valiosas:

### Permission Creep (Expansão de Permissões)

À medida que os agentes ganham capacidades, sempre há a tentação de conceder permissões mais amplas. Auditamos e podamos permissões constantemente para manter o privilégio mínimo.

O princípio do privilégio mínimo requer vigilância contínua. Estabelecemos um processo trimestral de auditoria de permissões, onde revisamos as permissões de cada agente em relação ao seu comportamento real. Isso geralmente revela agentes que receberam acesso de escrita, mas só precisam de permissões de leitura, ou agentes solicitando escopos da API do GitHub que nunca usam.

### Complexidade de Depuração

Quando os agentes se comportam mal, rastrear a causa raiz através de múltiplas execuções de fluxo de trabalho e safe outputs pode ser desafiador. Ainda estamos melhorando nosso registro (logging) e observabilidade.

A depuração distribuída através de múltiplos agentes - cada um gerando seus próprios logs e artefatos - é surpreendentemente difícil. Melhoramos isso com registros estruturados, IDs de correlação entre execuções relacionadas e meta-agentes que agregam padrões de falha. Mas definitivamente há espaço para melhores ferramentas aqui.

### Ruído no Repositório

Execuções frequentes de agentes criam muitas issues, PRs e comentários. Tivemos que implementar estratégias de arquivamento para manter o repositório gerenciável.

Com agentes criando dezenas de issues e PRs diariamente, a relação sinal-ruído do repositório pode sofrer. Desenvolvemos agentes de limpeza que arquivam discussões antigas, fecham issues obsoletas e consolidam relatórios redundantes. Encontrar o equilíbrio certo entre transparência e desordem continua sendo um desafio contínuo.

### Gerenciamento de Custos

Executar muitos agentes gera custos significativos. O Portfolio Analyst ajuda, mas o monitoramento contínuo de custos é essencial.

Operações de I.A. agentic em escala não são de graça. Tivemos que incorporar a consciência de custos à cultura da fábrica, com revisões regulares de gastos por agente e métricas de valor por dólar. Alguns agentes caros, mas de baixo valor, são descontinuados, enquanto agentes de alto valor recebem aumentos de orçamento. A visibilidade de custos acaba sendo tão importante quanto a funcionalidade.

### Confiança do Usuário

Alguns membros da equipe hesitam em interagir com agentes automatizados. Uma comunicação clara sobre capacidades e limitações ajuda a construir confiança ao longo do tempo.

A confiança não é automática - ela é conquistada através de comportamento consistente e comunicação transparente. Descobrimos que agentes com descrições "sobre mim" claras, limitações visíveis e padrões de comportamento previsíveis ganham aceitação mais rapidamente. Experimentos fracassados que discutimos abertamente como oportunidades de aprendizado também ajudam a construir confiança.

## Aplicando Estas Lições

Estas lições não são apenas observações acadêmicas - são insights práticos que você pode usar ao construir seu próprio ecossistema de agentes:

1. **Comece diverso, não perfeito** - Lance múltiplos agentes simples em vez de um complexo
2. **Projete com barreiras primeiro** - Restrições permitem experimentação segura
3. **Construa meta-agentes precocemente** - Você precisará deles mais cedo do que imagina
4. **Dê personalidade aos agentes** - Ajuda na compreensão e adoção
5. **Monitore custos desde o primeiro dia** - Consciência de custo evita surpresas desagradáveis
6. **Abrace padrões multifásicos** - Divida projetos ambiciosos em fases gerenciáveis
7. **Use interfaces ChatOps** - Slash commands são intuitivos e podem ter controle por função
8. **Implemente heartbeats** - Monitoramento proativo supera a depuração reativa
9. **Inspecione suas ferramentas** - Valide a disponibilidade da ferramenta antes que os agentes precisem dela
10. **Distribua, não faça monólitos** - Roteie solicitações para agentes especializados
11. **Enfileire seu trabalho** - O enfileiramento de tarefas permite progresso incremental
12. **Analise em meta-nível** - I.A. pode revelar padrões que humanos perdem

## O Que Vem a Seguir?

Estas lições emergiram da observação do comportamento dos agentes, mas entender *como* os agentes realmente funcionam requer mergulhar em seus padrões de projeto fundamentais.

Em nosso próximo artigo, exploraremos os 12 padrões de projeto principais que definem o que os agentes fazem e como eles se comportam. Fique ligado!

*Mais artigos nesta série em breve.*

[Anterior: Conheça os Workflows](/gh-aw/blog/2026-01-13-meet-the-workflows/)
