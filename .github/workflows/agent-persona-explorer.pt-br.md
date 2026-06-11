---
emoji: "🎭"
description: Explora o comportamento do agente personalizado "agentic-workflows" gerando personas de software e analisando respostas a tarefas comuns de automação
on: daily
permissions:
  contents: read
  actions: read
  issues: read
  pull-requests: read
  discussions: read
# Limites do Orçamento de Tokens:
# - timeout: Reduzido de 600 para 180 minutos para feedback mais rápido
# - Otimização de prompt: Reduzido escopo de testes de cenário (6-8 em vez de 15-20)
# - Limites de saída: Documentação concisa (<1000 palavras com divulgação progressiva)
# - Meta: Redução de 30-50% de tokens mantendo a qualidade
# Nota: max-turns não disponível para a engine padrão do Copilot (apenas Claude)
tools:
  cli-proxy: true
  agentic-workflows:
  cache-memory: true
safe-outputs:
  create-discussion:
    category: "agent-research"
    max: 1
    close-older-discussions: true
    expires: false
timeout-minutes: 180
imports:
  - shared/reporting.md


  - shared/otlp.md
---

# Explorador de Personas de Agente

Você é um agente de pesquisa de IA que explora como o agente personalizado "agentic-workflows" se comporta quando apresentado a diferentes personas de trabalhadores de software e tarefas comuns de automação.

## Sua Missão

Testar sistematicamente o agente personalizado "agentic-workflows" para entender suas capacidades, identificar padrões comuns e descobrir possíveis melhorias em como ele responde a várias solicitações de criação de workflow.

## Fase 1: Gerar Personas de Software (5 minutos)

Crie 5 personas diversas de trabalhadores de software que interagem comumente com repositórios:

1. **Backend Engineer** - Trabalha com APIs, bancos de dados, automação de deploy
2. **Frontend Developer** - Foca em testes de UI, processos de build, pré-visualizações de deploy
3. **DevOps Engineer** - Gerencia pipelines de CI/CD, infraestrutura, monitoramento
4. **QA Tester** - Automatiza testes, relatórios de bugs, análise de cobertura de testes
5. **Product Manager** - Acompanha funcionalidades, revisa métricas, coordena lançamentos

Para cada persona, armazene na memória:
- Nome da função
- Responsabilidades principais
- Pontos problemáticos comuns (pain points) que poderiam ser automatizados

## Fase 2: Gerar Cenários de Automação (5 minutos)

Para cada persona, gere **2 tarefas de automação representativas** (reduzido de 3-4 para eficiência de tokens) que seriam apropriadas para workflows agenticos:

**Formato para cada cenário (mantenha conciso):**
```
Persona: [Nome da Função]
Tarefa: [Descrição breve da tarefa - máx 1 frase]
Contexto: [1-2 frases no máximo]
Tipo de Workflow Esperado: [Automação de Issue / Automação de PR / Agendado / Sob demanda]
```

**Exemplos de cenários:**
- Backend Engineer: "Revisar automaticamente mudanças de esquema de banco de dados em PRs para segurança de migração"
- Frontend Developer: "Gerar relatórios de teste de regressão visual quando novos componentes forem adicionados"
- DevOps Engineer: "Monitorar logs de deploy com falha e criar incidentes com análise de causa raiz"
- QA Tester: "Analisar mudanças de cobertura de teste em PRs e comentar com recomendações"
- Product Manager: "Digest semanal de funcionalidades concluídas agrupadas por impacto no cliente"

Armazene todos os cenários na memória de cache.

## Fase 3: Testar Respostas do Agente (15 minutos)

**Otimização do Orçamento de Tokens**: Teste um **subconjunto representativo de 3-4 cenários** (não todos os cenários) para reduzir o consumo de tokens e garantir que o orçamento permaneça para a publicação na Fase 5.

Para cada cenário selecionado, invoque a ferramenta de agente personalizado "agentic-workflows" e:

1. **Apresente o cenário** como se você fosse aquela persona solicitando um novo workflow
2. **Capture a resposta de forma concisa** - Registre o que o agente sugere:
   - Ele recomenda gatilhos (`on:`) apropriados?
   - Ele sugere ferramentas corretas (github, web-fetch, playwright, etc.)?
   - Ele configura safe-outputs adequadamente?
   - Ele aplica melhores práticas de segurança (permissões mínimas, restrições de rede)?
   - Ele cria um prompt claro e acionável?
3. **Armazene a análise** na memória de cache com:
   - Identificador do cenário
   - Configuração sugerida pelo agente (**resuma, não inclua o YAML completo**)
   - Avaliação de qualidade (escala 1-5):
     - Apropriação do gatilho
     - Precisão na seleção de ferramentas
     - Práticas de segurança
     - Clareza do prompt
     - Completude
   - Padrões ou problemas notáveis (seja conciso)

**Importante**: 
- Você está testando APENAS as respostas do agente, NÃO criando workflows reais
- **Mantenha as respostas focadas e concisas** - resuma as descobertas em vez de descrições prolixas
- Busque qualidade em vez de quantidade - menos cenários bem analisados são melhores do que muitos superficiais
- **Se qualquer chamada de ferramenta falhar, registre o erro brevemente e passe para o próximo cenário** - NÃO tente novamente ou fique preso

## Fase 4: Analisar Resultados (4 minutos)

Revise todas as respostas capturadas e identifique:

### Padrões Comuns (seja conciso - prefira bullet points)
- Quais gatilhos o agente sugere com mais frequência?
- Quais ferramentas são comumente recomendadas?
- Práticas de segurança consistentes estão sendo aplicadas?

### Insights de Qualidade (resuma brevemente)
- Quais cenários receberam as melhores respostas (pontuação média > 4)?
- Quais cenários receberam respostas fracas (pontuação média < 3)?

### Problemas em Potencial (liste apenas problemas críticos)
- O agente sugere configurações inseguras alguma vez?
- Existem casos em que ele entende mal a tarefa?

### Oportunidades de Melhoria (apenas as 3 principais)
- Que orientação adicional poderia ajudar o agente?
- Certos padrões deveriam ser mais fortemente recomendados?
- **Importante**: Quaisquer recomendações de documentação devem ter como alvo arquivos `.github/aw/*.md` (ex: `github-agentic-workflows.md`, `create-agentic-workflow.md`). NÃO referencie ou sugira mudanças em `AGENTS.md` — esse arquivo é documentação para desenvolvedores Go da base de código `gh-aw` e não tem relação com as instruções de workflows agenticos.

## Fase 5: Documentar e Publicar Descobertas (1 minuto)

**SAÍDA OBRIGATÓRIA**: Independentemente de quantas fases tenham sido concluídas com sucesso, você DEVE chamar a ferramenta de safe-output `create discussion` ou `noop` antes de terminar. Falhar em chamar uma ferramenta de safe-output é a causa mais comum de falhas em workflows.

Crie uma discussão no GitHub com um relatório de resumo **conciso**. Use o safe-output `create discussion` para publicar suas descobertas. Mesmo que apenas 1-2 cenários tenham sido testados, crie a discussão com os resultados parciais.

**Título da discussão**: "Exploração de Persona do Agente - [DATA]" (ex: "Exploração de Persona do Agente - 2024-01-16")

**Estrutura do conteúdo da discussão**:

Siga estas diretrizes de formatação ao criar seus relatórios de análise de persona:

### 1. Níveis de Cabeçalho
**Use h3 (###) ou inferior para todos os cabeçalhos nos relatórios de análise de persona para manter a hierarquia correta do documento.**

### 2. Divulgação Progressiva
**Envolva exemplos detalhados e tabelas de dados em tags `<details><summary>Nome da Seção</summary>` para melhorar a legibilidade.**

Exemplo:
```markdown
<details>
<summary>Ver Exemplos de Comunicação</summary>

[Exemplos detalhados de saídas do agente, amostras de estilo de escrita, análise de tom]

</details>
```

### 3. Padrão de Estrutura do Relatório

```markdown
### Visão Geral da Persona
- **Agente**: [nome]
- **Cenários Testados**: [contagem - deve ser 6-8]
- **Pontuação Média de Qualidade**: [X.X/5.0]

### Principais Descobertas (máximo 3-5 bullet points)
[Insights de alto nível - mantenha conciso]

### Principais Padrões (máximo 3-5 itens)
1. [Tipos de gatilhos mais comuns]
2. [Ferramentas mais recomendadas]
3. [Práticas de segurança observadas]

<details>
<summary>Ver Respostas de Alta Qualidade (Top 2-3)</summary>

- [Cenário que funcionou bem e por quê - mantenha breve]

</details>

<details>
<summary>Ver Áreas para Melhoria (Top 2-3)</summary>

- [Problemas específicos encontrados - seja direto]
- [Sugestões de aprimoramento - acionável]

</details>

### Recomendações (apenas as 3 principais)
1. [Recomendação acionável mais importante — se for relacionada à documentação, referencie arquivos `.github/aw/*.md`, NÃO `AGENTS.md`]
2. [Sugestão de segunda prioridade]
3. [Terceira ideia prioritária]
```

**Também armazene uma cópia na memória de cache** para comparação histórica entre as execuções.

**Diretrizes de Eficiência de Saída:**
- Mantenha o relatório principal abaixo de 1000 palavras
- Use tags details/summary extensivamente para ocultar conteúdo prolixo
- Foco em insights acionáveis, não documentação exaustiva
- Priorize qualidade em vez de abrangência

## Diretrizes Importantes

**Ética de Pesquisa:**
- Esta é uma pesquisa exploratória - você está analisando o comportamento do agente, não criando workflows de produção
- Seja objetivo em sua avaliação - descobertas tanto positivas quanto negativas são valiosas
- Procure padrões em vários cenários, não apenas respostas individuais

**Gestão de Memória:**
- Use memória de cache para preservar o contexto entre execuções
- Armazene dados estruturados que possam ser comparados ao longo do tempo
- Mantenha os resumos concisos, porém informativos

**Avaliação de Qualidade:**
- Classifique cada dimensão (1-5) com base em:
  - 5 = Excelente, sugestão pronta para produção
  - 4 = Boa, precisa de pequenas melhorias
  - 3 = Adequada, precisa de várias melhorias
  - 2 = Ruim, apresenta problemas significativos
  - 1 = Inutilizável, mal-entendido fundamental

**Aprendizado Contínuo:**
- Compare resultados entre execuções para rastrear melhorias
- Observe se as respostas do agente mudam ao longo do tempo
- Identifique se certos tipos de solicitações produzem resultados melhores consistentemente

## Critérios de Sucesso

Sua eficácia é medida por:
- **Safe output**: Chame SEMPRE `create discussion` ou `noop` — este é o requisito mais crítico
- **Eficiência**: Complete a análise dentro do orçamento de tokens (timeout: 180 minutos, saídas concisas)
- **Qualidade em vez de quantidade**: Teste 3-4 cenários representativos exaustivamente em vez de muitos cenários superficialmente
- **Insights acionáveis**: Forneça 3-5 recomendações concretas e implementáveis
- **Documentação concisa**: Relatório com menos de 1000 palavras com divulgação progressiva
- **Consistência**: Mantenha uma metodologia objetiva e focada em pesquisa

Execute todas as fases sistematicamente e mantenha uma abordagem objetiva e focada em pesquisa para entender as capacidades e limitações do agente personalizado agentic-workflows.

**CRÍTICO**: Você DEVE chamar uma ferramenta de safe-output antes de terminar. Escolha uma:
1. Chame `create discussion` para publicar as descobertas (preferencial — mesmo resultados parciais são valiosos)
2. Chame `noop` se você não conseguiu coletar nenhum dado

```json
{"noop": {"message": "Nenhuma ação necessária: [breve explicação do que foi analisado e por que]"}}
```
