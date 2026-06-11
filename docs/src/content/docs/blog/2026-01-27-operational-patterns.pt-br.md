---
title: "9 Padrões para Operações de Agentes Automatizados no GitHub"
description: "Padrões estratégicos para operar agentes no ecossistema GitHub"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-27
draft: true
prev:
  link: /gh-aw/blog/2026-01-24-design-patterns/
  label: 12 Padrões de Projeto
next:
  link: /gh-aw/blog/2026-01-30-imports-and-sharing/
  label: Imports & Compartilhamento
---

[Artigo Anterior](/gh-aw/blog/2026-01-24-design-patterns/)

---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

*Temporização maravilhosa!* Você retornou à nossa série em andamento sobre a Fábrica de Agentes de Peli! Tendo explorado as [receitas secretas](/gh-aw/blog/2026-01-24-design-patterns/) que definem o que os agentes fazem, agora nos aventuramos no *teatro de operações* - onde a teoria encontra a prática!

Então você aprendeu o que os agentes *fazem* (padrões de projeto), mas como eles realmente *operam* no ecossistema do GitHub? É aí que entram os padrões operacionais.

Esses padrões surgiram da construção e execução de fluxos de trabalho em escala - eles são abordagens testadas em batalha para desafios comuns. Enquanto os padrões de projeto descrevem a arquitetura do agente, os padrões operacionais descrevem como os agentes se integram aos sistemas de fluxo de trabalho, issue, projeto e eventos do GitHub para criar uma automação eficaz.

Vamos explorar 9 padrões operacionais que fazem os agentes funcionarem na prática!

## Padrão 1: ChatOps - Interações Orientadas por Comandos

Esses fluxos de trabalho são disparados por slash commands (`/review`, `/deploy`, `/fix`) em comentários de issue ou PR. Isso cria uma interface de conversa interativa onde os membros da equipe podem invocar capacidades poderosas de I.A. com comandos simples.

Use-os quando:

- Revisões de código sob demanda
- Investigações de desempenho
- Correções de bugs e otimizações
- Solicitações de pesquisa e documentação
- Qualquer operação que exija autorização do usuário

Esses fluxos de trabalho fazem o seguinte:

1. Usuário comenta `/comando` em uma issue ou PR
2. O fluxo de trabalho é disparado pelo evento `issue_comment` ou `pull_request_comment`
3. O comentário é analisado para identificar comando e parâmetros
4. O controle por função (role-gating) valida as permissões do usuário
5. O agente executa e responde na thread
6. A memória de cache (cache-memory) evita trabalho duplicado

### Exemplo: Grumpy Reviewer

O fluxo de trabalho [`grumpy-reviewer`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/grumpy-reviewer.md) é um exemplo perfeito deste padrão:

- Disparado por `/grumpy` em comentários de PR
- Realiza revisão crítica de código com personalidade distinta
- Usa cache memory para evitar feedback duplicado
- Controle por função para evitar abuso
- Responde diretamente na thread do PR

Os principais benefícios são:

- Interface natural e conversacional
- Controle de acesso baseado em função integrado
- Consciente do contexto (sabe qual issue/PR)
- Feedback imediato
- Trilha de auditoria nos comentários

Aqui estão nossas dicas!

- Use nomes de comando claros e memoráveis
- Documente comandos no README
- Implemente controle por função para operações sensíveis
- Adicione texto de ajuda para `/comando help`
- Use cache-memory para rastrear o histórico de comandos

**Saiba mais**: [Exemplos de ChatOps](/gh-aw/patterns/chat-ops/)

---

## Padrão 2: DailyOps - Progresso Incremental Agendado

Fluxos de trabalho que rodam em agendas de dias úteis para fazer progresso pequeno e diário em direção a grandes metas. Em vez de sobrecarregar as equipes com grandes mudanças, o trabalho acontece automaticamente em pedaços gerenciáveis que são fáceis de revisar e integrar.

Use-os quando:

- Melhorias na cobertura de testes
- Otimização de desempenho
- Atualizações de documentação
- Redução de dívida técnica
- Gerenciamento de dependências

Esses fluxos de trabalho fazem o seguinte:

1. O fluxo de trabalho roda em agenda (ex: `0 9 * * 1-5` para dias úteis às 9h)
2. O agente verifica o estado de execuções anteriores
3. Faz progresso incremental (1-3 pequenas mudanças)
4. Cria PR ou issue com os resultados
5. No dia seguinte, continua de onde parou

### Exemplo: Daily Test Improver

O fluxo de trabalho [`daily-test-improver`](https://github.com/githubnext/agentics/blob/main/workflows/daily-test-improver.md) identifica sistematicamente lacunas de cobertura e implementa novos testes ao longo de vários dias:

**Fase 1 (Dia 1-2)**: Pesquise lacunas de cobertura e crie discussão de plano
**Fase 2 (Dia 3-4)**: Configure infraestrutura de teste
**Fase 3 (Dia 5+)**: Implemente testes incrementalmente com aprovação faseada

Os principais benefícios são:

- Melhorias sustentáveis e não disruptivas
- Fácil de revisar pequenas mudanças
- Constrói impulso ao longo do tempo
- Pontos de verificação humanos entre fases
- Quebra de tarefas natural

Aqui estão nossas dicas!

- Use repo-memory para persistência de estado
- Limite as mudanças por execução (1-3 itens)
- Crie PRs diários com títulos descritivos
- Inclua relatórios de progresso nas descrições do PR
- Permita intervenção humana em qualquer fase

**Saiba mais**: [Exemplos de DailyOps](/gh-aw/patterns/daily-ops/)

---

## Padrão 3: IssueOps - Automação de Issue Orientada por Eventos

Fluxos de trabalho que transformam issues do GitHub em gatilhos de automação, analisando, categorizando e respondendo automaticamente às issues conforme elas são criadas ou atualizadas. Usa safe outputs para garantir respostas automatizadas seguras.

Use-os quando:

- Triagem automática de issue
- Classificação e rotulagem de issue
- Validação de template
- Automação de resposta inicial
- Vinculação de issue relacionada

Esses fluxos de trabalho fazem o seguinte:

1. O fluxo de trabalho é disparado pelo evento `issues: opened` ou `issues: edited`
2. O agente analisa o conteúdo da issue
3. Determina labels, responsáveis e projetos apropriados
4. Usa safe outputs para aplicar mudanças
5. Opcional: Posta comentário de boas-vindas ou solicita esclarecimentos

### Exemplo: Issue Triage Agent

O [`issue-triage-agent`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/issue-triage-agent.md) rotula e categoriza automaticamente novas issues:

- Analisa o título e o corpo da issue
- Aplica labels relevantes (bug, feature, documentation, etc.)
- Estima prioridade com base no conteúdo
- Roteia para a equipe apropriada
- Posta recursos úteis

Os principais benefícios são:

- Processamento imediato de issue
- Categorização consistente
- Reduz a carga de triagem manual
- Melhora a qualidade da issue ao longo do tempo
- Cria trilha de auditoria

Aqui estão nossas dicas!

- Use safe outputs para todas as modificações
- Inclua pontuações de confiança nos labels
- Permita a substituição manual
- Rastreie a precisão da triagem
- Atualize as regras de classificação com base no feedback
- **Para repos públicos**: Por padrão, `min-integrity: approved` restringe a visibilidade do agente a proprietários, membros e colaboradores. Para fluxos de trabalho de triagem que precisam processar issues de todos os usuários, defina `min-integrity: none` explicitamente — veja [Filtro de Integridade](/gh-aw/reference/integrity/) para orientação.

**Saiba mais**: [Exemplos de IssueOps](/gh-aw/patterns/issue-ops/)

---

## Padrão 4: LabelOps - Automação de Fluxo de Trabalho Orientada por Label 🏷️

Fluxos de trabalho que usam labels do GitHub como gatilhos, metadados e marcadores de estado. Respondem a mudanças de label específicas com filtragem para ativar apenas para labels relevantes, mantendo respostas automatizadas seguras.

Use-os quando:

- Escalonamento de prioridade
- Roteamento de fluxo de trabalho
- Implementação de máquina de estado
- Sinalização de recursos (feature flagging)
- Atribuição de equipe

Esses fluxos de trabalho fazem o seguinte:

1. O fluxo de trabalho é disparado pelo evento `issues: labeled` ou `pull_request: labeled`
2. O filtro verifica label(s) específica(s)
3. O agente realiza ação específica do label
4. Atualiza o estado através de labels adicionais ou campos de projeto
5. Pode criar issues de acompanhamento ou notificações

### Exemplo: Escalonamento de Prioridade

Quando o label `priority: critical` é adicionado:

- Notifica líderes de equipe
- Adiciona ao quadro de projeto urgente
- Cria lembrete diário
- Atualiza o rastreamento de SLA

Os principais benefícios são:

- Representação visual de estado
- Mecanismo de gatilho amigável ao usuário
- Fluxos de trabalho fáceis de entender
- Padrão nativo do GitHub
- Consultável via filtros de label

Aqui estão nossas dicas!

- Use convenções de nomenclatura de label consistentes
- Documente significados de label
- Implemente hierarquias de label
- Evite a proliferação de labels
- Use descrições de label

**Saiba mais**: [Exemplos de LabelOps](/gh-aw/patterns/label-ops/)

---

## Padrão 5: ProjectOps - Gerenciamento de Quadro de Projeto Potencializado por I.A. 📊

Fluxos de trabalho que mantêm os quadros do GitHub Projects v2 atualizados usando I.A. para analisar issues/PRs e decidir de forma inteligente o roteamento, status, prioridade e valores de campo. Arquitetura de safe output garante segurança enquanto automatiza o gerenciamento de projeto.

Use-os quando:

- Atualizações automáticas de quadro de projeto
- Assistência no planejamento de sprint
- Gerenciamento de prioridade
- Rastreamento de status
- Alocação de recursos

Esses fluxos de trabalho fazem o seguinte:

1. O fluxo de trabalho é disparado por eventos de issue/PR
2. O agente analisa conteúdo e contexto
3. Determina projeto, status e campos apropriados
4. Usa safe outputs para atualizar o projeto
5. Notifica as partes interessadas relevantes

### Exemplo: População Automática de Quadro

Quando uma issue é criada:

- I.A. determina a qual/quais projeto(s) ela pertence
- Define status inicial (Backlog, To Do, etc.)
- Estima tamanho/esforço
- Atribui prioridade
- Define sprint/milestone, se aplicável

Os principais benefícios são:

- Quadros de projeto sempre atualizados
- Reduz o gerenciamento manual de projeto
- Preenchimento consistente de campos
- Classificação potencializada por I.A.
- Integra-se com fluxos de trabalho existentes

Aqui estão nossas dicas!

- Use tipos de campo de projeto efetivamente
- Defina transições de status claras
- Implemente limites de confiança
- Permita substituições manuais
- Rastreie a precisão da automação

**Saiba mais**: [Exemplos de ProjectOps](/gh-aw/patterns/project-ops/)

---

## Padrão 6: ResearchPlanAssignOps - Estratégia de Melhoria Estruturada 🔬

Uma estratégia de três fases que mantém os desenvolvedores no controle enquanto aproveita agentes de I.A. para melhorias sistemáticas de código. Fornece pontos de decisão claros em cada fase: Pesquisa (investigar), Planejamento (quebrar o trabalho), Atribuição (executar).

Use-os quando:

- Iniciativas de refatoração grandes
- Campanhas de qualidade de código
- Melhorias de arquitetura
- Projetos sistemáticos de limpeza
- Projetos de transferência de conhecimento

Esses fluxos de trabalho fazem o seguinte:

**Fase 1: Pesquisa**

- Agente analisa a base de código
- Identifica oportunidades de melhoria
- Cria discussão de pesquisa com descobertas
- Humano revisa e aprova a direção

**Fase 2: Planejamento**

- Agente cria plano de implementação detalhado
- Quebra o trabalho em issues gerenciáveis
- Estima esforço e dependências
- Humano revisa e prioriza

**Fase 3: Atribuição**

- Issues atribuídas a agentes ou desenvolvedores
- O trabalho prossegue incrementalmente
- Progresso rastreado via issues/PRs
- Humano revisa cada conclusão

### Exemplo: Detecção de Código Duplicado

O [`duplicate-code-detector`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/duplicate-code-detector.md) usa ResearchPlanAssignOps:

**Pesquisa**: Usa Serena MCP para análise semântica, cria relatório
**Planejamento**: Cria issues bem escopadas (máximo de 3 por execução) com estratégias de refatoração
**Atribuição**: Cria issues e [atribui ao Copilot](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-a-pr#assigning-an-issue-to-copilot) (via `assignees: copilot`), já que as correções são diretas

Os principais benefícios são:

- Controle humano em pontos de decisão
- Evita automação desenfreada
- Quebra de trabalho clara
- Progresso incremental
- Conhecimento capturado em issues

Aqui estão nossas dicas!

- Use discussões para a fase de pesquisa
- Crie issues para a fase de planejamento
- Rastreie atribuições explicitamente
- Inclua critérios de aceitação
- Revise e repita

**Saiba mais**: [ResearchPlanAssignOps](/gh-aw/patterns/research-plan-assign-ops/)

---

## Padrão 7: MultiRepoOps - Coordenação Cross-Repository 🔗

Fluxos de trabalho que coordenam operações em múltiplos repositórios do GitHub usando safe outputs cross-repository e autenticação segura. Permite sincronização de recursos, rastreamento hub-and-spoke, aplicação em toda a organização e fluxos de trabalho upstream/downstream.

Use-os quando:

- Políticas em toda a organização
- Atualizações de dependência entre repos
- Lançamentos de recursos sincronizados
- Aplicação de conformidade de segurança
- Monitoramento da saúde cross-repo

Esses fluxos de trabalho fazem o seguinte:

1. Fluxo de trabalho roda no repositório "hub"
2. Usa GitHub App ou PAT para autenticação
3. Consulta múltiplos repositórios
4. Analisa padrões entre repos
5. Usa safe outputs para criar issues/PRs nos repos de destino
6. Agrega resultados de volta ao hub

### Exemplo: Org Health Report

O [`org-health-report`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/org-health-report.md) analisa métricas de saúde em todos os repositórios da organização:

- Verifica dependências obsoletas
- Valida políticas de segurança
- Monitora a saúde do CI
- Cria issues em repos problemáticos
- Gera relatório em toda a organização

Os principais benefícios são:

- Visibilidade em toda a organização
- Aplicação consistente de políticas
- Coordenação centralizada
- Reduz a duplicação
- Escala para muitos repos

Aqui estão nossas dicas!

- Use GitHub Apps para autenticação
- Implemente limitação de taxa (rate limiting)
- Respeite as permissões do repositório
- Realize operações em lote eficientemente
- Monitore dependências cross-repo

**Saiba mais**: [MultiRepoOps](/gh-aw/patterns/multi-repo-ops/)

---

## Padrão 8: SideRepoOps - Infraestrutura de Automação Isolada 🏗️

Rode fluxos de trabalho a partir de um repositório "side" separado que visa sua base de código principal, mantendo issues, comentários e execuções de fluxo de trabalho gerados por I.A. isolados do código de produção. Fornece uma maneira fácil de começar com fluxos de trabalho agentic sem desorganizar seu repositório principal.

Use-os quando:

- Experimentar com agentes
- Execuções de fluxo de trabalho de alto volume
- Operações sensíveis ou ruidosas
- Testar antes da produção
- Separação organizacional

### Exemplo: Repositório de Análise Separado

Repositório principal: `company/product` (código de produção)
Repositório side: `company/product-automation` (fluxos de trabalho)

Fluxos de trabalho em `product-automation` analisam a base de código `product` e criam issues/PRs em `product` quando apropriado, mas mantêm discussões ruidosas em `product-automation`.

Os principais benefícios são:

- Mantém o repositório principal limpo
- Fácil de experimentar
- Separação clara de preocupações
- Pode ser mais permissivo no repositório side
- Fácil de desabilitar toda a automação

Aqui estão nossas dicas!

- Use GitHub Apps para acesso cross-repo
- Documente o relacionamento claramente
- Considere a visibilidade (público vs privado)
- Configure notificações apropriadas
- Planeje uma eventual migração, se bem-sucedido

**Saiba mais**: [SideRepoOps](/gh-aw/patterns/side-repo-ops/)

---

## Padrão 9: TrialOps - Validação Segura de Fluxo de Trabalho 🧪

Um padrão de teste especializado que estende SideRepoOps para validar fluxos de trabalho em repositórios de teste temporários antes da implantação em produção. Cria repositórios privados isolados onde os fluxos de trabalho executam e capturam safe outputs sem afetar bases de código reais.

Use-os quando:

- Testar novos fluxos de trabalho
- Validar mudanças de fluxo de trabalho
- Treinamento e demonstrações
- Verificação de conformidade
- Testes de regressão

Esses fluxos de trabalho fazem o seguinte:

1. Criam repositório privado temporário
2. Instalam fluxo de trabalho sob teste
3. Populam com dados de teste
4. Executam fluxo de trabalho
5. Capturam e validam saídas
6. Deletam repositório de teste ou mantêm para referência

**Saiba mais**: [TrialOps](/gh-aw/experimental/trial-ops/)

---

## Combinando Padrões Operacionais

Muitos sistemas de agentes bem-sucedidos combinam múltiplos padrões operacionais:

- **ChatOps + IssueOps**: O usuário dispara a análise via `/analyze`, o que cria uma issue com os resultados
- **DailyOps + MultiRepoOps**: Atualizações diárias de dependência em toda a organização
- **ResearchPlanAssignOps + ProjectOps**: A pesquisa cria um quadro de projeto populado com trabalho planejado
- **SideRepoOps + TrialOps**: Teste no repositório de teste, depois implante no repositório side, depois no principal

## Escolhendo o Padrão Operacional Certo

Ao projetar operações de agente, considere:

1. **Mecanismo de gatilho**: Manual (ChatOps), agendado (DailyOps) ou orientado a eventos (IssueOps, LabelOps)?
2. **Escopo**: Repositório único ou multi-repositório (MultiRepoOps)?
3. **Necessidades de isolamento**: Produção ou separado (SideRepoOps, TrialOps)?
4. **Coordenação**: Simples ou complexa (ProjectOps, ResearchPlanAssignOps)?
5. **Gerenciamento de estado**: Sem estado ou com estado (LabelOps, ProjectOps)?

## O Que Vem a Seguir?

Estes padrões operacionais funcionam efetivamente porque se baseiam em uma fundação de componentes reutilizáveis e compostáveis. A arma secreta que permitiu que a Fábrica de Agentes de Peli escalasse não foi apenas bons padrões - foi a capacidade de compartilhar e reutilizar componentes entre fluxos de trabalho.

Em nosso próximo artigo, exploraremos o sistema de imports e compartilhamento que tornou essa escalabilidade possível.

*Mais artigos nesta série em breve.*

[Artigo Anterior](/gh-aw/blog/2026-01-24-design-patterns/)
