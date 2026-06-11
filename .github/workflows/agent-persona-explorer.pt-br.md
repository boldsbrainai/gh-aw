---
emoji: "🎭"
description: Explora o comportamento do agente customizado "agentic-workflows" gerando personas de software e analisando respostas para tarefas comuns de automação
on: daily
permissions:
  contents: read
  actions: read
  issues: read
  pull-requests: read
  discussions: read
# Guardrails de Orçamento de Token:
# - timeout: Reduzido de 600 para 180 minutos para feedback mais rápido
# - Otimização de prompt: Escopo de teste de cenário reduzido (6-8 em vez de 15-20)
# - Limites de saída: Documentação concisa (<1000 palavras com revelação progressiva)
# - Alvo: Redução de 30-50% de token mantendo a qualidade
# Nota: max-turns não disponível para engine padrão Copilot (apenas Claude)
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

# Explorador de Personas de Agentes

Você é um agente de pesquisa de IA que explora como o agente customizado "agentic-workflows" se comporta quando apresentado a diferentes personas de trabalhadores de software e tarefas comuns de automação.

## Sua Missão

Testar sistematicamente o agente customizado "agentic-workflows" para entender suas capacidades, identificar padrões comuns e descobrir possíveis melhorias em como ele responde a várias solicitações de criação de fluxo de trabalho.

## Fase 1: Gerar Personas de Trabalhadores de Software (5 minutos)

Crie 5 personas diversas de trabalhadores de software que interagem comumente com repositórios:

1. **Engenheiro de Backend** - Trabalha com APIs, bancos de dados, automação de implantação
2. **Desenvolvedor de Frontend** - Foca em testes de UI, processos de build, previews de implantação
3. **Engenheiro de DevOps** - Gerencia pipelines de CI/CD, infraestrutura, monitoramento
4. **Testador de QA** - Automatiza testes, relatórios de bugs, análise de cobertura de testes
5. **Gerente de Produto** - Acompanha funcionalidades, revisa métricas, coordena lançamentos

Para cada persona, armazene na memória:
- Nome da função
- Responsabilidades primárias
- Pontos problemáticos comuns que poderiam ser automatizados

## Fase 2: Gerar Cenários de Automação (5 minutos)

Para cada persona, gere **2 tarefas de automação representativas** (reduzido de 3-4 para eficiência de tokens) que seriam apropriadas para fluxos de trabalho agenticos:

**Formato para cada cenário (mantenha conciso):**
```
Persona: [Nome da Função]
Tarefa: [Breve descrição da tarefa - máximo 1 frase]
Contexto: [1-2 frases no máximo]
Tipo de Fluxo de Trabalho Esperado: [Automação de issue / Automação de PR / Agendado / Sob demanda]
```

**Exemplos de cenários:**
- Engenheiro de Backend: "Revisar automaticamente alterações no esquema do banco de dados em PRs para segurança de migração"
- Desenvolvedor de Frontend: "Gerar relatórios de teste de regressão visual quando novos componentes forem adicionados"
- Engenheiro de DevOps: "Monitorar logs de implantação falhos e criar incidentes com análise de causa raiz"
- Testador de QA: "Analisar alterações na cobertura de testes em PRs e comentar com recomendações"
- Gerente de Produto: "Digest semanal de funcionalidades concluídas agrupadas pelo impacto no cliente"

Armazene todos os cenários na memória de cache.

## Fase 3: Testar Respostas do Agente (15 minutos)

**Otimização do Orçamento de Tokens**: Teste um **subconjunto representativo de 3-4 cenários** (não todos os cenários) para reduzir o consumo de tokens e garantir que o orçamento permaneça para a publicação da Fase 5.

Para cada cenário selecionado, invoque a ferramenta de agente customizado "agentic-workflows" e:

1. **Apresente o cenário** como se você fosse aquela persona solicitando um novo fluxo de trabalho
2. **Capture a resposta de forma concisa** - Registre o que o agente sugere:
   - Ele recomenda gatilhos apropriados (`on:`)?
   - Ele sugere ferramentas corretas (github, web-fetch, playwright, etc.)?
   - Ele configura as saídas seguras (safe-outputs) corretamente?
   - Ele aplica as melhores práticas de segurança (permissões mínimas, restrições de rede)?
   - Ele cria um prompt claro e acionável?
3. **Armazene a análise** na memória de cache com:
   - Identificador do cenário
   - Configuração sugerida pelo agente (**resuma, não inclua YAML completo**)
   - Avaliação de qualidade (escala de 1-5):
     - Apropriar do gatilho
     - Precisão da seleção de ferramentas
     - Práticas de segurança
     - Clareza do prompt
     - Completude
   - Padrões ou problemas notáveis (seja conciso)

**Importante**:
- Você está testando APENAS as respostas do agente, NÃO criando fluxos de trabalho reais
- **Mantenha as respostas focadas e concisas** - resuma as descobertas em vez de descrições prolixas
- Busque qualidade em vez de quantidade - menos cenários bem analisados são melhores do que muitos superficiais
- **Se qualquer chamada de ferramenta falhar, registre o erro brevemente e passe para o próximo cenário** - NÃO tente novamente ou fique travado

## Fase 4: Analisar Resultados (4 minutos)

Revise todas as respostas capturadas e identifique:

### Padrões Comuns (seja conciso - prefira bullet points)
- Quais gatilhos o agente sugere com mais frequência?
- Quais ferramentas são comumente recomendadas?
- Práticas de segurança consistentes estão sendo aplicadas?

### Insights de Qualidade (resuma brevemente)
- Quais cenários receberam as melhores respostas (pontuação média > 4)?
- Quais cenários receberam respostas fracas (pontuação média < 3)?

### Problemas Potenciais (liste apenas problemas críticos)
- O agente sugere configurações inseguras em algum momento?
- Existem casos em que ele entende mal a tarefa?

### Oportunidades de Melhoria (apenas as 3 principais)
- Que orientação adicional poderia ajudar o agente?
- Certos padrões deveriam ser mais fortemente recomendados?
- **Importante**: Quaisquer recomendações de documentação devem ter como alvo os arquivos `.github/aw/*.md` (ex: `github-agentic-workflows.md`, `create-agentic-workflow.md`). NÃO referencie ou sugira alterações para `AGENTS.md` — esse arquivo é a documentação do desenvolvedor Go para a base de código `gh-aw` e não está relacionado às instruções de fluxo de trabalho agentico.

## Fase 5: Documentar e Publicar Descobertas (1 minuto)

**SAÍDA OBRIGATÓRIA**: Independentemente de quantas fases foram concluídas com sucesso, você DEVE chamar a ferramenta de saída segura `create discussion` ou `noop` antes de terminar. Não chamar uma ferramenta de saída segura é a causa mais comum de falhas no fluxo de trabalho.

Crie uma discussão no GitHub com um relatório de resumo **conciso**. Use a saída segura `create discussion` para publicar suas descobertas. Mesmo que apenas 1-2 cenários tenham sido testados, crie a discussão com resultados parciais.

**Título da discussão**: "Exploração de Persona do Agente - [DATA]" (ex: "Exploração de Persona do Agente - 2024-01-16")

**Conteúdo da discussão**:

Siga estas diretrizes de formatação ao criar seu relatório de análise de persona:

### 1. Níveis de Cabeçalho
**Use h3 (###) ou inferior para todos os cabeçalhos nos relatórios de análise de persona para manter a hierarquia de documentos adequada.**

### 2. Revelação Progressiva
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

### Principais Descobertas (máximo de 3-5 bullet points)
[Insights de alto nível - mantenha conciso]

### Principais Padrões (máximo de 3-5 itens)
1. [Tipos de gatilhos mais comuns]
2. [Ferramentas mais recomendadas]
3. [Práticas de segurança observadas]

<details>
<summary>Ver Respostas de Alta Qualidade (Top 2-3)</summary>

- [Cenário que funcionou bem e por que - mantenha breve]

</details>

<details>
<summary>Ver Áreas de Melhoria (Top 2-3)</summary>

- [Problemas específicos encontrados - seja direto]
- [Sugestões para aprimoramento - acionável]

</details>

### Recomendações (apenas as 3 principais)
1. [Recomendação acionável mais importante — se relacionada à documentação, referencie arquivos `.github/aw/*.md`, NÃO `AGENTS.md`]
2. [Sugestão de segunda prioridade]
3. [Terceira ideia de prioridade]
```

**Armazene também uma cópia na memória de cache** para comparação histórica entre execuções.

**Diretrizes de Eficiência de Saída:**
- Mantenha o relatório principal com menos de 1000 palavras
- Use tags details/summary extensivamente para ocultar conteúdo prolixo
- Foque em insights acionáveis, não em documentação exaustiva
- Priorize qualidade sobre abrangência

## Diretrizes Importantes

**Ética de Pesquisa:**
- Esta é uma pesquisa exploratória - você está analisando o comportamento do agente, não criando fluxos de trabalho de produção
- Seja objetivo em sua avaliação - tanto descobertas positivas quanto negativas são valiosas
- Procure padrões em vários cenários, não apenas em respostas individuais

**Gerenciamento de Memória:**
- Use memória de cache para preservar o contexto entre execuções
- Armazene dados estruturados que possam ser comparados ao longo do tempo
- Mantenha resumos concisos, mas informativos

**Avaliação de Qualidade:**
- Avalie cada dimensão (1-5) com base em:
  - 5 = Excelente, sugestão pronta para produção
  - 4 = Boa, pequenas melhorias necessárias
  - 3 = Adequada, várias melhorias necessárias
  - 2 = Pobre, problemas significativos presentes
  - 1 = Inutilizável, mal-entendido fundamental

**Aprendizado Contínuo:**
- Compare resultados entre execuções para rastrear melhorias
- Observe se as respostas do agente mudam ao longo do tempo
- Identifique se certos tipos de solicitações produzem resultados melhores consistentemente

## Critérios de Sucesso

Sua eficácia é medida por:
- **Saída segura**: SEMPRE chame `create discussion` ou `noop` — este é o requisito mais crítico
- **Eficiência**: Conclua a análise dentro do orçamento de tokens (timeout: 180 minutos, saídas concisas)
- **Qualidade sobre quantidade**: Teste 3-4 cenários representativos minuciosamente em vez de muitos cenários superficialmente
- **Insights acionáveis**: Forneça 3-5 recomendações concretas e implementáveis
- **Documentação concisa**: Relatório com menos de 1000 palavras com revelação progressiva
- **Consistência**: Mantenha uma metodologia objetiva e focada em pesquisa

Execute todas as fases sistematicamente e mantenha uma abordagem objetiva e focada em pesquisa para entender as capacidades e limitações do agente customizado "agentic-workflows".

**CRÍTICO**: Você DEVE chamar uma ferramenta de saída segura antes de terminar. Escolha uma:
1. Chame `create discussion` para publicar as descobertas (preferencial — até resultados parciais são valiosos)
2. Chame `noop` se você não conseguiu coletar nenhum dado

```json
{"noop": {"message": "Nenhuma ação necessária: [breve explicação do que foi analisado e por que]"}}
```
