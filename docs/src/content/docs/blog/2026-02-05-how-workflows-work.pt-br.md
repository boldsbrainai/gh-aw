---
title: "Como os Fluxos de Trabalho Agentic Funcionam"
description: "A fundação técnica: da linguagem natural à execução segura"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-02-05
draft: true
prev:
  link: /gh-aw/blog/2026-02-02-security-lessons/
  label: Lições de Segurança
---

[Artigo Anterior](/gh-aw/blog/2026-02-02-security-lessons/)

---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

*Aha!* Hora de um mergulho profundo nas *profundezas borbulhantes* da Fábrica de Agentes de Peli! Tendo explorado o [cofre de segurança](/gh-aw/blog/2026-02-02-security-lessons/), agora vamos espiar por trás da cortina e descobrir a *maquinaria magnífica* - a fundação técnica que faz tudo funcionar!

Já se perguntou o que realmente acontece quando você escreve um fluxo de trabalho agentic? Vamos fazer uma jornada desde um simples arquivo Markdown até a execução segura e auditável no GitHub Actions.

Cada agente na Fábrica de Agentes de Peli segue o mesmo ciclo de vida básico, transformando descrições em linguagem natural em fluxos de trabalho prontos para produção. Entender essa arquitetura o ajuda a projetar agentes eficazes e depurar problemas quando eles surgem.

Vamos percorrer a jornada completa juntos!

## O Ciclo de Vida de Três Estágios

```text
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Escrita   │      │ Compilação  │      │  Execução   │
│  (Markdown) │ ───> │   (YAML)    │ ───> │  (Actions)  │
└─────────────┘      └─────────────┘      └─────────────┘
  Ling. Natural       Trava Segura         Visível à Equipe
  Declarativo         Validado             Auditável
  Amigável ao Humano  Pronto p/ Máquina    Observável
```

Três estágios, cada um com um propósito claro. Vamos explorar o que acontece em cada passo!

## Estágio 1: Escrita em Linguagem Natural

Os fluxos de trabalho agentic começam como **arquivos Markdown** que combinam prompts em linguagem natural com configuração declarativa. Pense nisso como escrever instruções para um robô prestativo.

### Anatomia de um Arquivo de Fluxo de Trabalho

```markdown
---
description: Investiga fluxos de trabalho de CI falhos para identificar causas raiz
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
permissions:
  contents: read

tools:
  github:
    toolsets: [issues, pull-requests]
  bash:
    commands: [git, jq]

network:
  allowed:
    - "api.github.com"

safe_outputs:
  create_issue:
    title_prefix: "[CI Doctor]"
    labels: ["ci", "automated"]
    max_items: 3
    expire: "+7d"
---

# CI Doctor

Quando um fluxo de trabalho de CI falha, investigue a causa raiz:

1. Baixe os logs do fluxo de trabalho
2. Analise os padrões de falha
3. Identifique a causa raiz
4. Crie uma issue com informações diagnósticas

Inclua:
- Resumo da falha
- Trechos relevantes de log
- Correções sugeridas
- Issues ou PRs relacionados
```

### Frontmatter: Configuração Declarativa

O frontmatter YAML define **como** o fluxo de trabalho roda. Configure gatilhos (agenda, eventos, manual ou comentários), permissões (comece com `contents: read`, adicione acesso de escrita com parcimônia), ferramentas (GitHub API, comandos bash, servidores MCP - todos enumerados explicitamente), acesso de rede (apenas domínios permitidos) e safe outputs (templates com barreiras integradas para criar issues/PRs).

### Prompt: Instruções em Linguagem Natural

O conteúdo Markdown após o frontmatter é o **prompt do agente** - instruções em linguagem natural descrevendo o que o agente deve fazer, como deve se comportar e quais saídas criar. Prompts eficazes começam com um objetivo claro, fornecem orientação passo a passo, incluem exemplos de saída e fazem referência a ferramentas disponíveis. É aqui que você dá personalidade e direção clara ao agente.

## Estágio 2: Compilação para Fluxos de Trabalho Seguros

O comando `gh aw compile` transforma fluxos de trabalho em linguagem natural em arquivos YAML de GitHub Actions com controles de segurança incorporados.

### Processo de Compilação

```text
┌──────────────┐
│ workflow.md  │
└──────┬───────┘
       │
       ├─► Analisar frontmatter
       │   └─► Validar esquema
       │
       ├─► Carregar imports
       │   └─► Mesclar configurações
       │
       ├─► Validar segurança
       │   ├─► Verificar permissões
       │   ├─► Verificar listas de permissão de ferramentas
       │   ├─► Validar regras de rede
       │   └─► Auditar safe outputs
       │
       ├─► Gerar jobs de GitHub Actions
       │   ├─► Setup job (preparação de ambiente)
       │   ├─► Agent job (execução de I.A.)
       │   └─► Safe output jobs (escritas)
       │
       └─► Escrever workflow.lock.yml
           └─► Travado, validado, pronto para rodar
```

### O que a Compilação Faz

A compilação realiza cinco operações chave:

1. **Validação de Esquema** - Garante que o frontmatter esteja em conformidade com a sintaxe de gatilho válida, permissões, configurações de ferramenta e templates de safe output
2. **Validação de Segurança** - Aplica que as permissões não excedam os requisitos, que as ferramentas sejam explicitamente listadas, que o acesso à rede seja limitado e que os safe outputs tenham limites apropriados
3. **Resolução de Importação** - Carrega e mescla arquivos de componentes compartilhados, configurações de ferramentas, instruções de prompt e versões fixadas
4. **Geração de Job** - Cria jobs de Setup (preparação de ambiente), Agente (execução de I.A.) e Safe Output (escritas)
5. **Geração de Arquivo de Trava (Lock File)** - Produz um arquivo `.lock.yml` completo e validado pronto para implantação

### Exemplo de Compilação

**Entrada: `ci-doctor.md`** (50 linhas de linguagem natural)

**Saída: `ci-doctor.lock.yml`** (300 linhas de YAML validado)

O arquivo de trava inclui preparação de ambiente, instalações de ferramentas, controles de segurança, lógica de execução de agente, processamento de safe output, tratamento de erros e passos de limpeza.

## Estágio 3: Execução e Produção de Artefatos

Fluxos de trabalho compilados executam em runners do GitHub Actions, produzindo artefatos visíveis para a equipe.

### Fluxo de Execução

```text
Fluxo de Trabalho Disparado
    │
    ├─► Setup Job
    │   ├─► Instalar CLI gh-aw
    │   ├─► Configurar servidores MCP
    │   ├─► Configurar restrições de rede
    │   └─► Preparar manipuladores de safe output
    │
    ├─► Agent Job
    │   ├─► Carregar prompt
    │   ├─► Reunir contexto (issues, PRs, arquivos)
    │   ├─► Executar contra mecanismo de I.A.
    │   │   └─► Agente usa ferramentas conforme necessário
    │   ├─► Gerar solicitações de safe output
    │   └─► Fazer upload de artefatos
    │
    └─► Safe Output Jobs (paralelo)
        ├─► Criar Issue (se solicitado)
        ├─► Criar PR (se solicitado)
        ├─► Adicionar Comentário (se solicitado)
        └─► Fazer upload de Ativos (se solicitado)
```

### Ambiente de Execução do Agente

O agente roda em um ambiente sandboxed com acesso à API do GitHub (via MCP), comandos bash permitidos, sistema de arquivos do repositório e servidores MCP configurados. O contexto inclui detalhes do evento de gatilho, estado do repositório, issues/PRs recentes, arquivos relevantes e execuções anteriores de fluxo de trabalho. Restrições aplicam listas de permissão de rede, restrições de ferramentas, limites de permissão e templates de safe output.

### Tipos de Saída

Agentes produzem issues, pull requests, comentários, discussões e artefatos (gráficos, arquivos de dados, relatórios) através de templates de safe output:

```yaml
safe_outputs:
  create_issue:
    title: "Falha de CI na suíte de testes"
    body: "Análise detalhada..."
    labels: ["ci", "automated"]
  create_pull_request:
    title: "Corrigir vulnerabilidade de dependência"
    body: "Atualiza pacote X..."
    branch: "agent/fix-vuln-123"
```

### Artefatos Auditáveis

Cada ação do agente cria um registro permanente. As execuções de fluxo de trabalho incluem logs completos de execução com tempos de início/fim, invocações de ferramentas, chamadas de API e erros. Issues, PRs e comentários são carimbados com data/hora e atribuídos, mostrando quem disparou o fluxo de trabalho, quando executou e o que criou. Discussões fornecem relatórios históricos pesquisáveis, e artefatos oferecem gráficos versionados e baixáveis, arquivos de dados e logs de depuração.

## A Interface do Mecanismo de I.A.

Fluxos de trabalho suportam múltiplos mecanismos de I.A. **Copilot** (padrão) fornece contexto consciente de código e integração com API do GitHub, com uso rastreado em sua assinatura. **Claude** oferece longas janelas de contexto e forte raciocínio via ANTHROPIC_API_KEY. **Codex** fornece integração empresarial com Azure OpenAI. Mecanismos **Custom** permitem que você traga seu próprio provedor de I.A. com controle total sobre a pilha.

```yaml
engine: copilot  # ou claude, codex, custom
model: claude-sonnet-4
```

## Arquitetura de Ferramenta: Servidores MCP

Servidores do Protocolo de Contexto de Modelo (MCP) fornecem capacidades especializadas através de um gateway. Servidores nativos incluem `github` (operações de API), `bash` (comandos shell) e `filesystem` (operações de arquivo). Servidores externos como `serena` (análise de código), `tavily` (pesquisa na web) e `ast-grep` (pesquisa estrutural) estendem a funcionalidade.

```yaml
tools:
  github:
    toolsets: [repos, issues, pull-requests]
  bash:
    commands: [git, jq, python]
  playwright:
    mode: cli
```

## Tratamento de Erros e Depuração

Quando os fluxos de trabalho falham, logs detalhados capturam informações de job, passo, invocação de ferramenta e erro. A validação de safe output fornece mensagens de erro claras e exemplos de correções, permitindo que os fluxos de trabalho falhem graciosamente. O fluxo de trabalho [`mcp-inspector`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/mcp-inspector.md) valida a disponibilidade e configuração do servidor. O agente [`audit-workflows`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/audit-workflows.md) rastreia execuções, classifica falhas e cria issues para problemas persistentes.

## Considerações de Desempenho

Fluxos de trabalho típicos rodam em 2-6 minutos (30-60s de setup, 1-5m de execução do agente, 10-30s de safe outputs). Os custos incluem computação do GitHub Actions, chamadas de API do mecanismo de I.A., uso de servidor MCP e armazenamento de artefatos. Otimize fazendo cache de consultas, realizando operações em lote, usando prompts concisos e solicitando apenas as permissões necessárias.

## O Que Vem a Seguir?

_Mais artigos nesta série em breve._

[Artigo Anterior](/gh-aw/blog/2026-02-02-security-lessons/)
