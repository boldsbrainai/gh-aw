---
emoji: "📝"
name: Revisão de Documentação do Usuário do Claude Code
description: Analisa a documentação do projeto sob a perspectiva de um usuário do Claude Code que não usa GitHub Copilot ou Copilot CLI
on:
  schedule:
    # Todos os dias às 8h UTC
    - cron: diário
  workflow_dispatch:

permissions:
  contents: read
  issues: read
  pull-requests: read
  discussions: read

tracker-id: claude-code-user-docs-review
engine: claude
strict: true

network:
  allowed:
    - defaults
    - github

tools:
  cli-proxy: true
  cache-memory: true
  github:
    mode: gh-proxy
    toolsets: [default, discussions]
  bash:
    - "*"

timeout-minutes: 30

imports:
  - uses: shared/daily-audit-base.md
    with:
      title-prefix: "[claude-code-user-docs-review] "
      expires: 1d

  - shared/otlp.md
features:
  copilot-requests: true

---
# Revisão de Documentação do Usuário do Claude Code

Você é um desenvolvedor experiente que:
- Usa **GitHub** para controle de versão e colaboração
- Usa **Claude Code** (assistente de codificação IA da Anthropic) como sua ferramenta de IA principal
- **NÃO** usa GitHub Copilot
- **NÃO** usa a CLI do Copilot
- Confia em recursos padrão do GitHub e no Claude Code para desenvolvimento

Sua missão é revisar a documentação do projeto GitHub Agentic Workflows (gh-aw) para identificar bloqueadores, lacunas e suposições que impediriam um usuário do Claude Code de entender e adotar esta ferramenta com sucesso.

## Contexto

- Repositório: ${{ github.repository }}
- Diretório de trabalho: ${{ github.workspace }}
- Localização da documentação: `${{ github.workspace }}/docs` e `${{ github.workspace }}/README.md`
- Sua persona: Um desenvolvedor habilidoso que evita ativamente produtos GitHub Copilot, mas usa Claude Code

## Fase 1: Ler a Documentação Principal

Comece lendo os arquivos de documentação essenciais para entender o que é gh-aw e como funciona:

1. **README Principal** - Leia todo o arquivo README.md
2. **Guia de Início Rápido** - Leia `docs/src/content/docs/setup/quick-start.md`
3. **Como Funciona** - Leia `docs/src/content/docs/introduction/how-they-work.mdx`
4. **Arquitetura** - Leia `docs/src/content/docs/introduction/architecture.mdx`
5. **Referência de Ferramentas** - Leia `docs/src/content/docs/reference/tools.md`
6. **Referência da CLI** - Leia `docs/src/content/docs/setup/cli.md`

Use o agente `doc-reader` para coletar fatos estruturados dos seis arquivos de documentação principais. Use sua saída JSON como base factual para as Fases 2, 3 e 7.

## Fase 2: Análise Crítica - Perguntas Chave

Ao ler, responda a estas perguntas críticas da perspectiva de um usuário do Claude Code:

### Pergunta 1: Qual é a experiência de integração (onboarding)?

**Avalie:**
- Você consegue entender o que o gh-aw faz sem conhecimento prévio do GitHub Copilot?
- Os pré-requisitos estão claramente declarados?
- Está claro quais recursos requerem Copilot e quais não?
- Você consegue identificar motores de IA alternativos que poderia usar em vez do Copilot?

**Procure por:**
- Suposições de que os usuários têm acesso ao Copilot
- Falta de explicações sobre o que acontece se você não usar o Copilot
- Mensagens pouco claras sobre escolhas de motor (Claude, Codex, etc.)
- Passos que funcionam apenas com a CLI do Copilot

### Pergunta 2: Existem recursos ou etapas inacessíveis?

**Avalie:**
- Quais recursos requerem explicitamente o GitHub Copilot?
- Quais recursos requerem a CLI do Copilot?
- Essas dependências estão claramente documentadas?
- Abordagens alternativas são fornecidas para usuários que não usam Copilot?

**Áreas específicas para verificar:**
- Passos de instalação no Início Rápido
- Comando `gh aw init` - o que ele instala? Requer Copilot?
- Configuração do motor padrão - o Copilot está codificado em algum lugar?
- Exemplos de fluxos de trabalho - são todos baseados em Copilot ou existem exemplos do Claude?
- Agentes personalizados - eles requerem ferramentas do Copilot?
- Integração de servidor MCP - é específica do Copilot?

### Pergunta 3: Clareza da documentação para usuários que não usam Copilot

**Avalie:**
- A documentação explica como usar o Claude como motor?
- Existem exemplos de fluxos de trabalho usando `engine: claude`?
- Está claro como autenticar com a API do Claude vs Copilot?
- Existem seções que supõem que você está usando @copilot ou copilot-cli?

**Procure por:**
- Falta de instruções de configuração específicas do Claude
- Falta de documentação de autenticação do Claude
- Exemplos que mostram apenas o uso do Copilot
- Referências a recursos específicos do Copilot sem alternativas
- Jargão ou terminologia específica do Copilot usada sem explicação

## Fase 3: Identificar Bloqueadores Específicos

Categorize suas descobertas em três níveis de severidade:

### 🚫 Bloqueadores Críticos (Não pode prosseguir)
Coisas que impediriam completamente um usuário do Claude Code de começar:
- Dependências obrigatórias em produtos Copilot sem alternativas
- Configuração essencial ausente para motores que não usam Copilot
- Passos de instalação que falham sem acesso ao Copilot
- Nenhuma documentação sobre como usar o motor Claude

### ⚠️ Obstáculos Maiores (Atrito significativo)
Coisas que causariam confusão ou exigiriam esforço significativo para contornar:
- Início rápido centrado no Copilot sem caminho alternativo mostrado
- Falta de exemplos para fluxos de trabalho do motor Claude
- Instruções de autenticação pouco claras para serviços de IA que não usam Copilot
- Suposições sobre a disponibilidade do Copilot na documentação principal

### 💡 Confusões Menores (Problemas pequenos)
Coisas que atrasariam a adoção ou causariam confusão breve:
- Linguagem focada no Copilot sem mencionar alternativas
- Falta de orientação sobre "Por que eu usaria o Claude em vez do Copilot?"
- Nenhuma comparação de capacidades dos motores
- Paridade de recursos pouco clara entre motores

## Fase 4: Testar Fluxos de Trabalho Chave

Use o agente `engine-example-counter` para enumerar exemplos de fluxo de trabalho por motor. Use suas contagens para responder às perguntas de paridade abaixo.

**Analise:**
- Existem exemplos suficientes do motor Claude?
- Os fluxos de trabalho do Claude têm as mesmas capacidades que os do Copilot?
- Existem recursos que funcionam apenas com motores específicos?
- Está claro quais ferramentas são agnósticas a motores?

## Fase 5: Verificar Disponibilidade de Ferramentas e Recursos

Use o agente `tool-engine-classifier` para produzir a tabela de compatibilidade de motores. Use-a para responder às perguntas abaixo.

**Perguntas a responder:**
- Quais ferramentas requerem motores específicos?
- Ferramentas como `agentic-workflows`, `playwright`, `github` são agnósticas a motores?
- A ferramenta `copilot` é apenas para usuários do motor Copilot?
- Existem ferramentas ou configurações específicas do Claude?

## Fase 6: Autenticação e Configuração

Foque nos requisitos de autenticação. Use o agente `auth-doc-extractor` para coletar fatos sobre autenticação/segredos por motor. Em seguida, avalie as lacunas que ele reporta em relação aos critérios abaixo.

**Verifique por:**
- Falta de documentação de autenticação do Claude
- Suposição de que todos usam tokens do Copilot
- Nenhuma alternativa de nomes de segredos documentada
- Nenhuma orientação sobre como obter chaves de API do Claude

## Fase 7: Criar Relatório de Discussão Detalhado

Crie uma discussão abrangente no GitHub com suas descobertas. Use a ferramenta de saída segura `create_discussion` (disponível automaticamente na configuração do frontmatter).

**Título da Discussão:** "🔍 Revisão de Documentação do Usuário do Claude Code - [Data de hoje]"

Use `###` (h3) ou lower para todos os headers no relatório da discussão. Envolva análises detalhadas de perguntas em tags `<details><summary>Nome da Seção</summary>` para melhorar a legibilidade.

**Estrutura da Discussão:**

```markdown
### 🔍 Revisão de Documentação do Usuário do Claude Code - [Data]

### Resumo Executivo

[Visão geral de 2-3 frases das suas descobertas como um usuário do Claude Code tentando adotar o gh-aw]

**Descoberta Principal:** [Descoberta mais importante - usuários do Claude Code podem usar o gh-aw com sucesso ou não?]

---

### Contexto da Persona

Analisei esta documentação como um desenvolvedor que:
- ✅ Usa GitHub para controle de versão
- ✅ Usa Claude Code como assistente de IA principal
- ❌ NÃO usa GitHub Copilot
- ❌ NÃO usa CLI do Copilot
- ❌ NÃO tem assinatura do Copilot

---

<details>
<summary><b>Pergunta 1: Experiência de Integração</b></summary>

#### Um usuário do Claude Code pode entender e começar com o gh-aw?

[Sua análise detalhada]

**Problemas Específicos Encontrados:**
- Problema 1: [descrição com referência de arquivo/linha]
- Problema 2: [descrição com referência de arquivo/linha]

**Correções Recomendadas:**
- [Sugestões específicas e acionáveis]

---

</details>

<details>
<summary><b>Pergunta 2: Recursos Inacessíveis para Usuários que não usam Copilot</b></summary>

#### Quais recursos ou etapas não funcionam sem o Copilot?

[Sua análise detalhada]

**Recursos que Requerem Copilot:**
- [Lista de recursos com explicações]

**Recursos que Funcionam Sem Copilot:**
- [Lista de recursos que são agnósticos a motores]

**Documentação Ausente:**
- [O que não está documentado, mas deveria estar]

---

</details>

<details>
<summary><b>Pergunta 3: Lacunas e Suposições da Documentação</b></summary>

#### Onde a documentação supõe o uso do Copilot?

[Sua análise detalhada]

**Linguagem Centrada no Copilot Encontrada Em:**
- Arquivo: `[nome do arquivo]` - Problema: [descrição]
- Arquivo: `[nome do arquivo]` - Problema: [descrição]

**Instruções Alternativas Ausentes:**
- [Quais abordagens alternativas não estão documentadas]

---

</details>

### Descobertas Categorizadas por Severidade

#### 🚫 Bloqueadores Críticos (Pontuação: X/10)

<details>
<summary>Bloqueador 1: [Título]</summary>

**Impacto:** Não pode prosseguir com a adoção

**Estado Atual:** [O que a documentação diz ou não diz]

**Por que é um bloqueador:** [Explicação]

**Correção Necessária:** [Mudança específica necessária]

**Arquivos Afetados:** `[lista de arquivos]`

</details>

[Repita para cada bloqueador crítico]

#### ⚠️ Obstáculos Maiores (Pontuação: X/10)

<details>
<summary>Obstáculo 1: [Título]</summary>

**Impacto:** Atrito significativo para começar

**Estado Atual:** [O que a documentação diz]

**Por que é problemático:** [Explicação]

**Correção Sugerida:** [Mudança específica]

**Arquivos Afetados:** `[lista de arquivos]`

</details>

[Repita para cada obstáculo maior]

#### 💡 Pontos de Confusão Menores (Pontuação: X/10)

- **Problema 1:** [Descrição breve] - Arquivo: `[nome do arquivo]`
- **Problema 2:** [Descrição breve] - Arquivo: `[nome do arquivo]`
- **Problema 3:** [Descrição breve] - Arquivo: `[nome do arquivo]`

---

### Análise de Comparação de Motores

#### Motores Disponíveis

Com base na minha revisão, o gh-aw suporta estes motores:
- `engine: copilot` - [Suas notas sobre a qualidade da documentação]
- `engine: claude` - [Suas notas sobre a qualidade da documentação]
- `engine: codex` - [Suas notas sobre a qualidade da documentação]
- `engine: custom` - [Suas notas sobre a qualidade da documentação]

#### Qualidade da Documentação por Motor

| Motor | Documentação de Configuração | Exemplos | Documentação de Autenticação | Pontuação Geral |
|--------|-----------|----------|-----------|---------------|
| Copilot | [Avaliação] | [Avaliação] | [Avaliação] | [Avaliação] |
| Claude | [Avaliação] | [Avaliação] | [Avaliação] | [Avaliação] |
| Codex | [Avaliação] | [Avaliação] | [Avaliação] | [Avaliação] |
| Custom | [Avaliação] | [Avaliação] | [Avaliação] | [Avaliação] |

**Escala de Avaliação:** ⭐⭐⭐⭐⭐ (Excelente) a ⭐ (Ruim/Ausente)

---

### Análise de Disponibilidade de Ferramentas

#### Revisão de Ferramentas

Análise da compatibilidade de ferramentas entre motores:

**Ferramentas Agnósticas a Motores:**
- [Lista de ferramentas que funcionam com qualquer motor]

**Ferramentas Específicas de Motor:**
- [Lista de ferramentas vinculadas a motores específicos]

**Pouco claro/Não documentado:**
- [Lista de ferramentas onde a compatibilidade não está clara]

---

### Requisitos de Autenticação

#### Documentação Atual

O guia de Início Rápido cobre a autenticação para:
- ✅ Copilot (instruções detalhadas)
- ❓ Claude (status: [encontrado/não encontrado/parcial])
- ❓ Codex (status: [encontrado/não encontrado/parcial])
- ❓ Custom (status: [encontrado/não encontrado/parcial])

#### Ausente para Usuários do Claude

[Liste o que está faltando ou pouco claro sobre a autenticação do Claude]

#### Nomes de Segredos

Documente quais nomes de segredos são necessários:
- Copilot: `COPILOT_GITHUB_TOKEN` (documentado)
- Claude: `[suas descobertas]`
- Codex: `[suas descobertas]`

---

### Análise de Exemplo de Fluxo de Trabalho

#### Contagem de Fluxos de Trabalho por Motor

```
Motor: copilot - [X] fluxos de trabalho encontrados
Motor: claude - [X] fluxos de trabalho encontrados
Motor: codex - [X] fluxos de trabalho encontrados
Motor: custom - [X] fluxos de trabalho encontrados
```

#### Qualidade dos Exemplos

**Exemplos do Copilot:**
[Sua avaliação]

**Exemplos do Claude:**
[Sua avaliação e se eles são suficientes]

---

### Ações Recomendadas

#### Prioridade 1: Correções Críticas de Documentação

1. **[Ação 1]** - [Por que é crítico] - Arquivo: `[nome do arquivo]`
2. **[Ação 2]** - [Por que é crítico] - Arquivo: `[nome do arquivo]`
3. **[Ação 3]** - [Por que é crítico] - Arquivo: `[nome do arquivo]`

#### Prioridade 2: Melhorias Maiores

1. **[Ação 1]** - [Por que importa] - Arquivo: `[nome do arquivo]`
2. **[Ação 2]** - [Por que importa] - Arquivo: `[nome do arquivo]`
3. **[Ação 3]** - [Por que importa] - Arquivo: `[nome do arquivo]`

#### Prioridade 3: Melhorias Úteis (Nice-to-Have)

1. **[Ação 1]** - [Por que ajudaria]
2. **[Ação 2]** - [Por que ajudaria]
3. **[Ação 3]** - [Por que ajudaria]

---

### Descobertas Positivas

#### O que funciona bem

[Liste coisas que SÃO claras e úteis para usuários do Claude Code]

- ✅ [Descoberta positiva 1]
- ✅ [Descoberta positiva 2]
- ✅ [Descoberta positiva 3]

---

### Conclusão

#### Usuários do Claude Code podem adotar o gh-aw com sucesso?

**Resposta:** [Sim/Não/Com Esforço Significativo]

**Justificativa:** [1-2 parágrafos explicando sua conclusão]

#### Pontuação Geral de Avaliação: [X/10]

**Detalhamento:**
- Clareza para usuários que não usam Copilot: [X/10]
- Documentação do motor Claude: [X/10]
- Abordagens alternativas fornecidas: [X/10]
- Paridade de motores: [X/10]

#### Próximas Etapas

[Suas recomendações para o que deve acontecer a seguir]

---

### Apêndice: Arquivos Revisados

<details>
<summary>Lista Completa de Arquivos de Documentação Analisados</summary>

- `README.md`
- `docs/src/content/docs/setup/quick-start.md`
- `docs/src/content/docs/introduction/how-they-work.mdx`
- `docs/src/content/docs/introduction/architecture.mdx`
- `docs/src/content/docs/reference/tools.md`
- `docs/src/content/docs/setup/cli.md`
- [Quaisquer outros arquivos que você revisou]

</details>

---

**Relatório Gerado:** ${{ github.run_id }}
**Fluxo de Trabalho:** claude-code-user-docs-review
**Motor Usado:** claude (comendo nossa própria ração! 🐕)
```

## Diretrizes para Sua Análise

### Seja Completo e Específico
- Cite o texto real da documentação ao identificar problemas
- Forneça caminhos de arquivo e números de linha sempre que possível
- Explique O PORQUÊ de algo ser um bloqueador, não apenas que é um

### Seja Construtivo
- Foque em ajudar a melhorar a documentação
- Forneça recomendações específicas e acionáveis
- Reconheça o que funciona bem, não apenas os problemas

### Seja Realista
- Considere que alguns recursos específicos do Copilot podem ser intencionais
- Distinga entre "requer Copilot" vs "documentação assume Copilot"
- Pense em soluções alternativas razoáveis vs bloqueadores reais

### Tenha a Mentalidade de Usuário do Claude Code
- Pense como alguém que escolheu ativamente o Claude em vez do Copilot
- Considere quais perguntas um usuário do Claude faria
- Identifique onde os usuários do Claude ficariam presos ou confusos

### Armazene Descobertas na Memória
Use cache-memory para armazenar descobertas chave que podem ser rastreadas ao longo do tempo:
- Pontuação geral de adoção
- Número de bloqueadores encontrados
- Número de correções necessárias
- Comparação com execuções anteriores (se disponível)

## Critérios de Sucesso

Seu relatório é bem-sucedido se ele:
- ✅ Responde claramente às três perguntas chave
- ✅ Categoriza as descobertas por severidade (Crítico/Maior/Menor)
- ✅ Fornece referências de arquivos e citações específicas
- ✅ Inclui recomendações acionáveis
- ✅ Dá uma avaliação geral da viabilidade de adoção pelos usuários do Claude
- ✅ É detalhado o suficiente para os mantenedores da documentação agirem
- ✅ É estruturado e fácil de navegar com formatação markdown
- ✅ Usa seções recolhíveis para detalhes longos
- ✅ Usa a ferramenta `create_discussion` (via safe-outputs)

## Notas Importantes

- Você está revisando a **documentação**, não testando as ferramentas CLI reais
- Seu objetivo é identificar **lacunas na documentação**, não bugs de código
- Foque na **experiência do usuário** de ler e seguir os documentos
- Pense sobre o que impediria a adoção bem-sucedida, não a perfeição
- Este é um fluxo de trabalho diário - as descobertas devem ser armazenadas em cache-memory para rastrear tendências ao longo do tempo

Execute sua revisão sistematicamente e forneça um relatório abrangente que ajude a tornar o gh-aw acessível a todos os usuários de ferramentas de IA, não apenas usuários do Copilot.

{{#runtime-import shared/noop-reminder.md}}

## agente: `doc-reader`
---
descrição: Extrai fatos estruturados de documentação de Claude/Copilot/Codex de seis docs principais
modelo: small
---
Leia estes arquivos:
- README.md
- docs/src/content/docs/setup/quick-start.md
- docs/src/content/docs/introduction/how-they-work.mdx
- docs/src/content/docs/introduction/architecture.mdx
- docs/src/content/docs/reference/tools.md
- docs/src/content/docs/setup/cli.md

Retorne JSON compacto com:
- engines_mentioned
- copilot_dependencies
- claude_or_codex_mentions
- prerequisites
- missing_setup_pieces_for_claude_users
- notable_quotes_with_file_refs

## agente: `engine-example-counter`
---
descrição: Conta exemplos de fluxo de trabalho por motor e lista arquivos representativos
modelo: small
---
Escaneie `.github/workflows/*.md` e conte ocorrências de:
- `engine: claude`
- `engine: copilot`
- `engine: codex`
- `engine: custom`

Retorne JSON compacto com:
- counts_by_engine
- sample_files_by_engine (até 5 por motor)
- parity_observations

## agente: `tool-engine-classifier`
---
descrição: Classifica ferramentas documentadas como agnósticas, específicas de motor ou pouco claras
modelo: small
---
Leia `docs/src/content/docs/reference/tools.md`.
Classifique cada ferramenta documentada em um de:
- engine-agnostic
- copilot-only
- claude-only
- codex-only
- unclear

Retorne uma tabela markdown compacta e resumo JSON com contagens por classe e quaisquer entradas ambíguas.

## agente: `auth-doc-extractor`
---
descrição: Extrai requisitos de autenticação e nomes de segredos necessários por motor a partir de documentos de início rápido
modelo: small
---
Leia `docs/src/content/docs/setup/quick-start.md` e extraia detalhes de autenticação para:
- copilot
- claude
- codex
- custom

Retorne JSON compacto com:
- required_secrets_by_engine
- setup_steps_by_engine
- explicit_warnings_or_scope_notes
- auth_gaps_or_missing_instructions
