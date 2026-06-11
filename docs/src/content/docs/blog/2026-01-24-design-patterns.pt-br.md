---
title: "12 Padrões de Projeto da Fábrica de Agentes de Peli"
description: "Padrões comportamentais fundamentais para fluxos de trabalho agentic bem-sucedidos"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-24
draft: true
prev:
  link: /gh-aw/blog/2026-01-21-twelve-lessons/
  label: 12 Lições
next:
  link: /gh-aw/blog/2026-01-27-operational-patterns/
  label: 9 Padrões Operacionais
---

[Artigo Anterior](/gh-aw/blog/2026-01-21-twelve-lessons/)

---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

*Meus queridos amigos!* Que terceira porção deliciosa na série Fábrica de Agentes de Peli! Vocês experimentaram os [fluxos de trabalho](/gh-aw/blog/2026-01-13-meet-the-workflows/) e saborearam as [lições que aprendemos](/gh-aw/blog/2026-01-21-twelve-lessons/) - agora preparem-se para as *receitas secretas* - os padrões de projeto fundamentais que surgiram da execução da nossa coleção!

Depois de construir nossa coleção de agentes na Fábrica de Agentes de Peli, começamos a notar padrões. Não o tipo que planejamos de antemão - estes surgiram organicamente resolvendo problemas reais. Agora identificamos 12 padrões de projeto fundamentais que capturam o que fluxos de trabalho agentic bem-sucedidos realmente fazem.

Pense nesses padrões como plantas arquitetônicas para agentes. Cada fluxo de trabalho na fábrica se encaixa em pelo menos um padrão, e muitos combinam vários. Entender esses padrões o ajudará a projetar agentes eficazes mais rapidamente, sem reinventar a roda.

Vamos mergulhar!

## Padrão 1: O Analista Somente Leitura (Read-Only Analyst)

**Observe, analise e reporte - sem alterar nada**

Esses agentes coletam dados, realizam análises e publicam insights através de discussões ou ativos. Eles possuem permissões zero de escrita para código. Isso os torna incrivelmente seguros para execução contínua em qualquer frequência.

Use-os quando:

- Construir confiança no comportamento do agente (ótimo para começar!)
- Estabelecer linhas de base (baselines) antes da automação
- Gerar relatórios e métricas
- Pesquisa profunda e investigação

Aqui estão alguns exemplos:

- [`audit-workflows`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/audit-workflows.md) - Meta-agente que audita todas as execuções de outros agentes
- [`portfolio-analyst`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/portfolio-analyst.md) - Identifica oportunidades de otimização de custos
- [`session-insights`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/copilot-session-insights.md) - Analisa padrões de uso do Copilot
- [`org-health-report`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/org-health-report.md) - Métricas de saúde de toda a organização
- [`scout`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/scout.md), [`archie`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/archie.md) - Agentes de pesquisa profunda

Algumas características chave são:

- `permissions: contents: read` apenas (é isso!)
- Saída via discussões, issues ou uploads de artefatos
- Pode rodar em qualquer agenda sem risco
- Constrói confiança através da transparência
- Frequentemente cria visualizações e gráficos

---

## Padrão 2: O Respondente ChatOps (ChatOps Responder)

**Assistência sob demanda via slash commands**

Esses fluxos de trabalho agentic são ativados por menções `/comando` em issues ou PRs. Controle por função para segurança. Eles respondem com análises, visualizações ou ações.

Use-os quando:

- Revisões de código sob demanda
- Otimizações sob demanda
- Pesquisa iniciada pelo usuário
- Assistência especializada que requer autorização

Aqui estão alguns exemplos:

- [`q`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/q.md) - Otimizador de fluxo de trabalho (digite `/q` e ele investiga!)
- [`grumpy-reviewer`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/grumpy-reviewer.md) - Revisão de código crítica com personalidade
- [`poem-bot`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/poem-bot.md) - Geração criativa de versos (porque não?)
- [`mergefest`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/mergefest.md) - Automação de merge de branch
- [`pr-fix`](https://github.com/githubnext/agentics/blob/main/workflows/pr-fix.md) - Corrige testes falhos sob demanda

Algumas características chave são:

- Acionado por `/comando` em comentários de issue/PR
- Frequentemente inclui controle por função (role-gating) para segurança
- Fornece feedback imediato
- Usa cache-memory para evitar trabalho duplicado
- Personalidade e propósito claros

---

## Padrão 3: O Zelador Contínuo (Continuous Janitor)

**Limpeza e manutenção automatizada**

Esses fluxos de trabalho agentic propõem melhorias incrementais através de PRs. Rodam em agendas (diariamente/semanalmente). Criam mudanças escopadas com labels e mensagens de commit descritivas. Sempre requerem revisão humana antes de realizar o merge.

Use-os quando:

- Manter dependências atualizadas
- Manter a sincronia da documentação
- Consistência de formatação e estilo
- Pequenas refatorações e limpezas
- Melhorias na organização de arquivos

Aqui estão alguns exemplos:

- [`daily-workflow-updater`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/daily-workflow-updater.md) - Mantém ações e dependências atuais
- [`glossary-maintainer`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/glossary-maintainer.md) - Sincroniza glossário com o código
- [`daily-file-diet`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/daily-file-diet.md) - Refatora arquivos superdimensionados
- [`hourly-ci-cleaner`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/hourly-ci-cleaner.md) - Repara problemas de CI

Algumas características chave são:

- Rodam em agendas fixas
- Criam PRs para revisão humana (sem auto-merge!)
- Fazem mudanças pequenas e focadas
- Usam labels e commits descritivos
- Frequentemente incluem guardas "se não houver mudanças"

---

## Padrão 4: O Guardião da Qualidade (Quality Guardian)

**Validação contínua e aplicação de conformidade**

Esses fluxos de trabalho agentic validam a integridade do sistema através de testes, escaneamentos e verificações de conformidade. Rodam frequentemente (a cada hora/diariamente) para detectar regressões precocemente.

Use-os quando:

- Testes de fumaça (smoke testing) de infraestrutura
- Escaneamento de segurança
- Validação de acessibilidade
- Verificações de consistência de esquema
- Monitoramento da saúde da infraestrutura

Aqui estão alguns exemplos:

- Testes de fumaça para [`copilot`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/smoke-copilot.md), [`claude`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/smoke-claude.md), [`codex`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/smoke-codex.md)
- [`schema-consistency-checker`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/schema-consistency-checker.md)
- [`breaking-change-checker`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/breaking-change-checker.md)
- [`firewall`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/firewall.md), [`mcp-inspector`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/mcp-inspector.md)
- [`daily-accessibility-review`](https://github.com/githubnext/agentics/blob/main/workflows/daily-accessibility-review.md)

Algumas características chave são:

- Execução frequente (de hora em hora até diariamente)
- Critérios de aprovação/falha claros
- Cria issues quando a validação falha
- Mínimo de falsos positivos
- Execução rápida (padrão de batimento cardíaco)

---

## Padrão 5: O Gerenciador de Issues & PRs

**Automação inteligente de fluxo de trabalho para issues e pull requests**

Esses fluxos de trabalho agentic fazem triagem, vinculam, rotulam, fecham e coordenam issues e PRs. Reagem a eventos ou rodam em agendas.

Use-os quando:

- Automação de triagem de issue
- Vinculação de issues relacionadas
- Gerenciamento de sub-issues
- Coordenação de merges
- Otimização de templates de issue

Aqui estão alguns exemplos:

- [`issue-triage-agent`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/issue-triage-agent.md) - Auto-rotulagem e categorização
- [`issue-arborist`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/issue-arborist.md) - Vincula issues relacionadas
- [`mergefest`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/mergefest.md) - Coordenação de merge
- [`sub-issue-closer`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/sub-issue-closer.md) - Fecha sub-issues concluídas

Algumas características chave são:

- Baseado em eventos (gatilhos de issue/PR)
- Usa safe outputs para modificações
- Frequentemente inclui classificação inteligente
- Mantém relacionamentos de issue
- Respeita a intenção e o contexto do usuário
- **Para triagem em repos público**: Defina `min-integrity: none` para processar issues de todos os usuários (o padrão é `approved`, que restringe a colaboradores de confiança) — veja [Filtro de Integridade](/gh-aw/reference/integrity/)

---

## Padrão 6: O Improvisador Multifásico (Multi-Phase Improver)

**Progresso progressivo ao longo de vários dias com pontos de verificação humanos**

Esses fluxos de trabalho agentic abordam melhorias complexas grandes demais para execuções únicas. Três fases: (1) Pesquisa e criação de discussão de plano, (2) Inferência/configuração de infraestrutura de build, (3) Implementação de mudanças via PR. Verificam o estado a cada execução para determinar a fase atual.

Use-os quando:

- Projetos de refatoração grandes
- Melhorias na cobertura de testes
- Otimização de desempenho
- Iniciativas de redução de backlog
- Projetos de melhoria de qualidade

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

O [`duplicate-code-detector`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/duplicate-code-detector.md) usa o Improvisador Multifásico:

**Pesquisa**: Usa Serena MCP para análise semântica, cria relatório
**Planejamento**: Cria issues bem escopadas (máximo de 3 por execução) com estratégias de refatoração
**Atribuição**: Cria issues e [atribui ao Copilot](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-a-pr#assigning-an-issue-to-copilot) (via `assignees: copilot`), já que as correções são diretas

Algumas características chave são:

- Operação de vários dias
- Três fases distintas com pontos de verificação
- Usa repo-memory para persistência de estado
- Aprovação humana entre fases
- Cria documentação abrangente

---

## Padrão 7: O Agente de Inteligência de Código

**Análise semântica e detecção de padrões**

Agentes usando ferramentas de análise de código especializadas (Serena, ast-grep) para detectar padrões, duplicatas, antipadrões e oportunidades de refatoração.

Use-os quando:

- Encontrar código duplicado
- Detectar antipadrões
- Identificar oportunidades de refatoração
- Analisar consistência de estilo de código
- Melhorias no sistema de tipos

Aqui estão alguns exemplos:

- [`duplicate-code-detector`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/duplicate-code-detector.md) - Encontra duplicatas de código
- [`semantic-function-refactor`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/semantic-function-refactor.md) - Oportunidades de refatoração
- [`terminal-stylist`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/terminal-stylist.md) - Análise de saída do console
- [`go-pattern-detector`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/go-pattern-detector.md) - Padrões específicos de Go
- [`typist`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/typist.md) - Análise de tipos

Algumas características chave são:

- Usa ferramentas de análise especializadas (servidores MCP)
- Sensível à linguagem ou cross-language
- Cria issues detalhadas com locais de código
- Frequentemente propõe correções concretas
- Integra-se com fluxos de trabalho de IDE

---

## Padrão 8: O Agente de Conteúdo & Documentação

**Manter artefatos de conhecimento sincronizados com o código**

Esses fluxos de trabalho agentic mantêm documentação, glossários, apresentações, posts de blog e outros conteúdos atualizados monitorando mudanças na base de código e atualizando os docs correspondentes.

Use-os quando:

- Manter docs sincronizados
- Manter glossários
- Atualizar apresentações
- Analisar conteúdo multimídia
- Gerar documentação

Aqui estão alguns exemplos:

- [`glossary-maintainer`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/glossary-maintainer.md) - Sincronização de glossário
- [`technical-doc-writer`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/technical-doc-writer.md) - Documentação técnica
- [`slide-deck-maintainer`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/slide-deck-maintainer.md) - Manutenção de apresentações
- [`ubuntu-image-analyzer`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/ubuntu-image-analyzer.md) - Documentação de ambiente

Algumas características chave são:

- Monitora mudanças de código
- Cria PRs de documentação
- Usa ferramentas de análise de documentos (markitdown)
- Mantém a consistência
- Frequentemente inclui visualização

---

## Padrão 9: O Meta-Agente Otimizador (Meta-Agent Optimizer)

**Monitorar e otimizar outros agentes**

Esses fluxos de trabalho agentic analisam o ecossistema de agentes em si. Baixam logs de fluxo de trabalho, classificam falhas, detectam ferramentas ausentes, rastreiam métricas de desempenho, identificam oportunidades de otimização de custos.

Use-os quando:

- Gerenciamento de ecossistemas agentic em escala
- Otimização de custos
- Monitoramento de desempenho
- Detecção de padrões de falha
- Validação da disponibilidade de ferramentas

Aqui estão alguns exemplos:

- [`audit-workflows`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/audit-workflows.md) - Auditoria abrangente de fluxo de trabalho
- [`agent-performance-analyzer`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/agent-performance-analyzer.md) - Métricas de qualidade do agente
- [`portfolio-analyst`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/portfolio-analyst.md) - Otimização de custos
- [`workflow-health-manager`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/workflow-health-manager.md) - Monitoramento de saúde

Algumas características chave são:

- Acessa dados de execução de fluxo de trabalho
- Analisa logs e métricas
- Identifica problemas sistêmicos
- Fornece recomendações acionáveis
- Essencial para escala

---

## Padrão 10: O Meta-Agente Orquestrador

**Orquestrar fluxos de trabalho multifásicos via máquinas de estado**

Esses fluxos de trabalho agentic coordenam fluxos de trabalho complexos através de padrões de enfileiramento de tarefas. Rastreiam estado entre execuções (aberto/em andamento/concluído).

Use-os quando:

- Gerenciamento de tarefas
- Coordenação de várias etapas
- Geração de fluxo de trabalho
- Monitoramento de desenvolvimento
- Distribuição de tarefas

Aqui estão alguns exemplos:

- [`workflow-generator`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/workflow-generator.md) - Gera novos fluxos de trabalho
- [`dev-hawk`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/dev-hawk.md) - Monitoramento de desenvolvimento

Algumas características chave são:

- Gerencia o estado entre execuções
- Usa primitivas do GitHub (issues, projetos)
- Coordena múltiplos agentes
- Implementa padrões de fluxo de trabalho
- Frequentemente baseado em despachante (dispatcher)

---

## Padrão 11: O Agente de ML & Análise

**Insights avançados através de aprendizado de máquina e PLN**

Esses fluxos de trabalho agentic aplicam agrupamento, PLN, análise estatística ou técnicas de ML para extrair padrões de dados históricos. Geram visualizações e relatórios de tendências.

Use-os quando:

- Descoberta de padrões em grandes conjuntos de dados
- PLN em conversas
- Agrupamento de itens semelhantes
- Análise de tendências
- Estudos longitudinais

Aqui estão alguns exemplos:

- [`copilot-session-insights`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/copilot-session-insights.md) - Análise de uso de sessão
- [`copilot-pr-nlp-analysis`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/copilot-pr-nlp-analysis.md) - PLN em conversas de PR
- [`prompt-clustering`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/prompt-clustering-analysis.md) - Agrupa e categoriza prompts

Algumas características chave são:

- Usa técnicas de ML/estatísticas
- Requer dados históricos
- Frequentemente usa repo-memory
- Gera visualizações
- Descobre padrões não óbvios

---

## Padrão 12: O Agente de Segurança & Moderação

**Proteger repositórios contra ameaças e aplicar políticas**

Esses fluxos de trabalho agentic protegem repositórios através de escaneamento de vulnerabilidades, detecção de segredos, filtragem de spam, análise de código malicioso e aplicação de conformidade.

Use-os quando:

- Escaneamento de vulnerabilidades de segurança
- Detecção de segredos
- Prevenção de spam e abuso
- Aplicação de conformidade
- Geração de correção de segurança

Aqui estão alguns exemplos:

- [`security-compliance`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/security-compliance.md) - Campanhas de vulnerabilidade
- [`firewall`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/firewall.md) - Testes de segurança de rede
- [`daily-secrets-analysis`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/daily-secrets-analysis.md) - Escaneamento de segredos
- [`ai-moderator`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/ai-moderator.md) - Filtragem de spam de comentários
- [`security-fix-pr`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/security-fix-pr.md) - Correções de segurança automatizadas

Algumas características chave são:

- Permissões focadas em segurança
- Requisitos de alta precisão
- Frequentemente impulsionado por regulamentações
- Cria alertas acionáveis
- Pode incluir auto-remediação

---

## Combinando Padrões

Aqui é onde fica divertido: muitos fluxos de trabalho bem-sucedidos combinam múltiplos padrões. Por exemplo:

- **Analista Somente Leitura + Análise de ML** - Analise dados históricos e gere insights
- **Respondente ChatOps + Improvisador Multifásico** - O usuário dispara um projeto de melhoria de vários dias
- **Guardião da Qualidade + Agente de Segurança** - Valide qualidade e segurança continuamente
- **Meta-Agente Otimizador + Meta-Agente Orquestrador** - Monitore e coordene o ecossistema

## Escolhendo o Padrão Certo

Ao projetar um novo agente, considere:

1. **Ele modifica algo?** → Se não, comece com Analista Somente Leitura (mais seguro!)
2. **É disparado pelo usuário?** → Considere Respondente ChatOps
3. **Deve rodar automaticamente?** → Escolha entre Zelador (PRs) ou Guardião (validação)
4. **Ele está gerenciando outros agentes?** → Use Meta-Agente Otimizador ou Orquestrador
5. **Ele precisa de múltiplas fases?** → Use Improvisador Multifásico
6. **É relacionado à segurança?** → Aplique o padrão Segurança & Moderação

## O Que Vem a Seguir?

Estes padrões de projeto descrevem *o que* os agentes fazem comportamentalmente. Mas *como* eles operam dentro do ecossistema do GitHub - isso requer entender padrões operacionais.

Em nosso próximo artigo, exploraremos 9 padrões operacionais para executar agentes eficazmente no GitHub. Estas são as estratégias que fazem os agentes funcionarem na prática!

*Mais artigos nesta série em breve.*

[Artigo Anterior](/gh-aw/blog/2026-01-21-twelve-lessons/)
