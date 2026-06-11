---
title: Introdução ao GitHub Actions
description: Um guia abrangente para entender o GitHub Actions, desde sua história e conceitos principais até o teste de fluxos de trabalho e comparação com fluxos de trabalho agenticos
sidebar:
  order: 1
---

**GitHub Actions** é a plataforma de automação integrada do GitHub para construir, testar e implantar código a partir do seu repositório. Ele permite fluxos de trabalho automatizados disparados por eventos de repositório, agendamentos ou gatilhos manuais — tudo definido em arquivos YAML no seu repositório. Fluxos de trabalho agenticos compilam de arquivos markdown para YAML de GitHub Actions seguro, herdando esses conceitos principais enquanto adicionam tomada de decisão impulsionada por IA e segurança aprimorada.

## Conceitos Principais

### Fluxos de Trabalho YAML

Um **fluxo de trabalho YAML** é um processo automatizado definido em `.github/workflows/`. Cada fluxo de trabalho consiste em jobs que executam quando disparados por eventos. Os fluxos de trabalho devem ser armazenados no branch **main** ou branch padrão para estarem ativos e são versionados junto com seu código.

**Exemplo** (`.github/workflows/ci.yml`):

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - name: Executar testes
        run: npm test
```

### Jobs

Um **job** é um conjunto de passos que executam no mesmo runner (máquina virtual). Jobs executam em paralelo por padrão, mas podem depender uns dos outros com `needs:`. Cada job executa em uma VM nova, e os resultados são compartilhados entre jobs usando artefatos. O tempo limite padrão é de 360 minutos para jobs padrão do GitHub Actions; o passo de execução do agente em fluxos de trabalho agenticos tem o padrão de 20 minutos.

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: npm run build

  test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: npm test
```

### Passos (Steps)

**Passos (Steps)** são tarefas individuais dentro de um job, executando sequencialmente. Eles podem executar comandos de shell ou usar ações pré-construídas do GitHub Marketplace. Os passos compartilham o mesmo sistema de arquivos e ambiente; um passo com falha interrompe o job por padrão.

```yaml
steps:
  # Passo de ação - usa uma ação pré-construída
  - uses: actions/checkout@v6

  # Passo de execução - executa um comando de shell
  - name: Instalar dependências
    run: npm install

  # Ação com entradas (inputs)
  - uses: actions/setup-node@v4
    with:
      node-version: '20'
```

## Modelo de Segurança

### Armazenamento e Execução de Fluxo de Trabalho

Os fluxos de trabalho devem ser armazenados em `.github/workflows/` no **branch padrão** para estarem ativos e confiáveis. Isso garante que as alterações passem por revisão de código, mantenha uma trilha de auditoria, evite escalonamento de privilégios de branches de funcionalidade e trate o branch padrão como um limite de confiança.

```yaml
# Fluxos de trabalho no branch main podem acessar segredos
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - run: echo "Tem acesso aos segredos de produção"
```

### Modelo de Permissões

O GitHub Actions usa o **princípio do menor privilégio** com declarações explícitas de permissão. Pull requests de fork são somente leitura por padrão; todas as permissões necessárias devem ser declaradas explicitamente.

```yaml
permissions:
  contents: read       # Ler conteúdo do repositório
  issues: write        # Criar/modificar issues
  pull-requests: write # Criar/modificar PRs

jobs:
  exemplo:
    runs-on: ubuntu-latest
    steps:
      - run: echo "O job tem apenas as permissões especificadas"
```

Com os GitHub Agentic Workflows, **permissões de escrita não são usadas explicitamente**. Em vez disso, capacidades muito mais restritas para escrever no GitHub são declaradas através de **saídas seguras (safe outputs)**, que validam, restringem e higienizam todas as interações com a API do GitHub.

### Gerenciamento de Segredos

**Segredos (Secrets)** são variáveis de ambiente criptografadas armazenadas no nível de repositório, organização ou ambiente. Eles nunca são expostos em logs, são acessíveis apenas a fluxos de trabalho em branches padrão/protegidos e limitados por ambiente para proteção adicional.

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Implantar em produção
        env:
          API_KEY: ${{ secrets.API_KEY }}
        run: ./deploy.sh
```

## Testando e Depurando Fluxos de Trabalho

### Testando de Branches com workflow_dispatch

O gatilho **`workflow_dispatch`** permite a execução manual de fluxo de trabalho de qualquer branch, inestimável para desenvolvimento e teste:

```yaml
name: Testar Fluxo de Trabalho
on:
  workflow_dispatch:
    inputs:
      ambiente:
        description: 'Ambiente de destino'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production
      debug:
        description: 'Habilitar log de depuração'
        required: false
        type: boolean

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Testando em ${{ inputs.ambiente }}"
      - run: echo "Modo debug: ${{ inputs.debug }}"
```

Para executar: navegue até a aba **Actions** → selecione seu fluxo de trabalho → clique em **Run workflow** → escolha seu branch e forneça os inputs.

> [!TIP]
> Habilite logs de depuração definindo os segredos de repositório `ACTIONS_STEP_DEBUG: true` e `ACTIONS_RUNNER_DEBUG: true`.

**Nota:** A definição do fluxo de trabalho deve ser mergeada ao branch principal antes que possa ser executada. Apenas `workflow_dispatch` funciona em branches não padrão — gatilhos de evento não funcionam.

### Depurando Execuções de Fluxo de Trabalho

Veja os logs na aba **Actions** clicando em uma execução, depois em um job, e depois em passos individuais. Use comandos de fluxo de trabalho para saída estruturada:

```yaml
steps:
  - name: Depurar contexto
    run: |
      echo "::debug::Depurando contexto de fluxo de trabalho"
      echo "::notice::Este é um aviso (notice)"
      echo "::warning::Este é um alerta (warning)"
      echo "::error::Este é um erro (error)"

  - name: Depurar ambiente
    run: |
      echo "GitHub event: ${{ github.event_name }}"
      echo "Ator: ${{ github.actor }}"
      printenv | sort
```

## Fluxos de Trabalho Agenticos vs. GitHub Actions Tradicional

Embora os fluxos de trabalho agenticos sejam compilados para YAML de GitHub Actions e executados na mesma infraestrutura, eles introduzem melhorias significativas em segurança, simplicidade e tomada de decisão impulsionada por IA.

| Funcionalidade | GitHub Actions Tradicional | Fluxos de Trabalho Agenticos |
|---------|----------------------------|-------------------|
| **Linguagem de Definição** | YAML com passos explícitos | Markdown de linguagem natural |
| **Complexidade** | Exige conhecimento em YAML, API | Descreva a intenção em inglês simples |
| **Tomada de Decisão** | Lógica fixa de se-então | Decisões contextuais impulsionadas por IA |
| **Modelo de Segurança** | Baseado em token com permissões amplas | Sandbox com saídas seguras (safe-outputs) |
| **Operações de Escrita** | Acesso direto à API com `GITHUB_TOKEN` | Higienizadas através da validação de safe-output |
| **Acesso à Rede** | Irrestrito por padrão | Apenas domínios permitidos (allowlist) |
| **Ambiente de Execução** | VM runner padrão | Sandbox aprimorado com isolamento MCP |
| **Integração de Ferramentas** | Seleção manual de ações | Descoberta automática de ferramentas MCP |
| **Teste** | `workflow_dispatch` em branches | Igual, mais compilação local |
| **Auditabilidade** | Logs de fluxo de trabalho padrão | Aprimorado com logs de raciocínio do agente |

## Próximos Passos e Recursos

- **[Início Rápido](/gh-aw/setup/quick-start/)** - Crie seu primeiro fluxo de trabalho agentico
- **[Melhores Práticas de Segurança](/gh-aw/introduction/architecture/)** - Mergulho profundo no modelo de segurança agentica
- **[Saídas Seguras (Safe Outputs)](/gh-aw/reference/safe-outputs/)** - Saiba mais sobre operações validadas do GitHub
- **[Estrutura do Fluxo de Trabalho](/gh-aw/reference/workflow-structure/)** - Entenda a sintaxe de fluxo de trabalho em markdown
- **[Padrões de Design](/gh-aw/patterns/daily-ops/)** - Padrões de fluxo de trabalho agentico do mundo real
- **[Glossário](/gh-aw/reference/glossary/)** - Termos e conceitos principais
- **[Documentação do GitHub Actions](https://docs.github.com/en/actions)** - Referência oficial
- **[Sintaxe de Fluxo de Trabalho](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)** - Referência completa em YAML
- **[Endurecimento de Segurança](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)** - Melhores práticas de segurança
