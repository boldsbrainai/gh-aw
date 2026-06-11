---
title: Guia Introdutório do GitHub Actions
description: Um guia abrangente para entender o GitHub Actions, desde seu histórico e conceitos principais até o teste de fluxos de trabalho e comparação com fluxos de trabalho agênticos.
sidebar:
  order: 1
---

O **GitHub Actions** é a plataforma de automação integrada do GitHub para compilar, testar e implantar código a partir do seu repositório. Ele permite fluxos de trabalho automatizados disparados por eventos do repositório, agendamentos ou gatilhos manuais — tudo definido em arquivos YAML no seu repositório. Os fluxos de trabalho agênticos são compilados a partir de arquivos markdown em YAML do GitHub Actions seguro, herdando esses conceitos principais enquanto adicionam tomada de decisão impulsionada por IA e segurança aprimorada.

## Conceitos Principais

### Fluxos de Trabalho YAML

Um **fluxo de trabalho YAML** é um processo automatizado definido em `.github/workflows/`. Cada fluxo de trabalho consiste em jobs que são executados quando disparados por eventos. Os fluxos de trabalho devem ser armazenados na branch **main** ou padrão para estarem ativos e são versionados junto com seu código.

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

Um **job** é um conjunto de etapas que são executadas no mesmo runner (máquina virtual). Os jobs são executados em paralelo por padrão, mas podem depender uns dos outros com `needs:`. Cada job é executado em uma VM nova e os resultados são compartilhados entre os jobs usando artefatos. O timeout padrão é de 360 minutos para jobs padrão do GitHub Actions; a etapa de execução do agente em fluxos de trabalho agênticos tem como padrão 20 minutos.

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

### Etapas (Steps)

**Etapas** são tarefas individuais dentro de um job, executadas sequencialmente. Elas podem executar comandos de shell ou usar ações pré-construídas do GitHub Marketplace. As etapas compartilham o mesmo sistema de arquivos e ambiente; uma etapa com falha interrompe o job por padrão.

```yaml
steps:
  # Etapa de Ação - usa uma ação pré-construída
  - uses: actions/checkout@v6

  # Etapa de execução - executa um comando de shell
  - name: Instalar dependências
    run: npm install

  # Ação com entradas
  - uses: actions/setup-node@v4
    with:
      node-version: '20'
```

## Modelo de Segurança

### Armazenamento e Execução de Fluxos de Trabalho

Os fluxos de trabalho devem ser armazenados em `.github/workflows/` na **branch padrão** para estarem ativos e confiáveis. Isso garante que as alterações passem por revisão de código, mantenha uma trilha de auditoria, previna a elevação de privilégios de branches de feature e trate a branch padrão como um limite de confiança.

```yaml
# Fluxos de trabalho na branch main podem acessar segredos
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - run: echo "Tem acesso a segredos de produção"
```

### Modelo de Permissão

O GitHub Actions usa o **princípio do privilégio mínimo** com declarações de permissão explícitas. Pull requests de fork são somente leitura por padrão; todas as permissões necessárias devem ser declaradas explicitamente.

```yaml
permissions:
  contents: read       # Ler conteúdo do repositório
  issues: write        # Criar/modificar issues
  pull-requests: write # Criar/modificar PRs

jobs:
  example:
    runs-on: ubuntu-latest
    steps:
      - run: echo "O job tem permissões especificadas apenas"
```

Com o GitHub Agentic Workflows, **permissões de escrita não são usadas explicitamente**. Em vez disso, capacidades muito mais restritas de escrever no GitHub são declaradas através de **saídas seguras (safe-outputs)**, que validam, restringem e higienizam todas as interações com a API do GitHub.

### Gerenciamento de Segredos

**Segredos** são variáveis de ambiente criptografadas armazenadas no nível do repositório, organização ou ambiente. Eles nunca são expostos em logs, são acessíveis apenas a fluxos de trabalho em branches padrão/protegidas e delimitados por ambiente para proteção adicional.

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

O gatilho **`workflow_dispatch`** permite a execução manual do fluxo de trabalho a partir de qualquer branch, inestimável para desenvolvimento e teste:

```yaml
name: Testar Fluxo de Trabalho
on:
  workflow_dispatch:
    inputs:
      environment:
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
      - run: echo "Testando em ${{ inputs.environment }}"
      - run: echo "Modo de depuração: ${{ inputs.debug }}"
```

Para executar: navegue até a aba **Actions** → selecione seu fluxo de trabalho → clique em **Run workflow** → escolha sua branch e forneça as entradas.

> [!TIP]
> Habilite logs de depuração definindo os segredos do repositório `ACTIONS_STEP_DEBUG: true` e `ACTIONS_RUNNER_DEBUG: true`.

**Nota:** A definição do fluxo de trabalho deve ser mesclada à branch principal antes de poder ser executada. Apenas `workflow_dispatch` funciona em branches não padrão — gatilhos de eventos não funcionam.

### Depurando Execuções de Fluxo de Trabalho

Veja os logs na aba **Actions** clicando em uma execução, depois em um job e, em seguida, em etapas individuais. Use comandos de fluxo de trabalho para saída estruturada:

```yaml
steps:
  - name: Depurar contexto
    run: |
      echo "::debug::Depurando contexto de fluxo de trabalho"
      echo "::notice::Este é um aviso"
      echo "::warning::Este é um alerta"
      echo "::error::Este é um erro"

  - name: Depurar ambiente
    run: |
      echo "Evento GitHub: ${{ github.event_name }}"
      echo "Ator: ${{ github.actor }}"
      printenv | sort
```

## Fluxos de Trabalho Agênticos vs GitHub Actions Tradicional

Embora os fluxos de trabalho agênticos sejam compilados em YAML do GitHub Actions e executados na mesma infraestrutura, eles introduzem melhorias significativas em segurança, simplicidade e tomada de decisão impulsionada por IA.

| Funcionalidade | GitHub Actions Tradicional | Fluxos de Trabalho Agênticos |
|---------|----------------------------|-------------------|
| **Linguagem de Definição** | YAML com etapas explícitas | Markdown em linguagem natural |
| **Complexidade** | Exige conhecimento de YAML, conhecimento de API | Descreva a intenção em inglês simples (ou português) |
| **Tomada de Decisão** | Lógica se-então fixa | Decisões contextuais impulsionadas por IA |
| **Modelo de Segurança** | Baseado em token com permissões amplas | Sandbox com saídas seguras (safe-outputs) |
| **Operações de Escrita** | Acesso direto à API com `GITHUB_TOKEN` | Higienizado através da validação de safe-output |
| **Acesso à Rede** | Irrestrito por padrão | Apenas domínios permitidos |
| **Ambiente de Execução** | VM runner padrão | Sandbox aprimorado com isolamento MCP |
| **Integração de Ferramentas** | Seleção manual de ação | Descoberta automática de ferramentas de servidor MCP |
| **Testes** | `workflow_dispatch` em branches | Igual, mais compilação local |
| **Auditoria** | Logs de fluxo de trabalho padrão | Aprimorado com logs de raciocínio do agente |

## Próximos Passos e Recursos

- **[Quick Start](/gh-aw/setup/quick-start/)** - Crie seu primeiro fluxo de trabalho agêntico
- **[Segurança: Melhores Práticas](/gh-aw/introduction/architecture/)** - Mergulho profundo no modelo de segurança agêntico
- **[Saídas Seguras (Safe Outputs)](/gh-aw/reference/safe-outputs/)** - Aprenda sobre operações validadas do GitHub
- **[Estrutura do Fluxo de Trabalho](/gh-aw/reference/workflow-structure/)** - Entenda a sintaxe de fluxo de trabalho em markdown
- **[Padrões de Design](/gh-aw/patterns/daily-ops/)** - Padrões de fluxo de trabalho agêntico do mundo real
- **[Glossário](/gh-aw/reference/glossary/)** - Termos e conceitos chave
- **[Documentação do GitHub Actions](https://docs.github.com/en/actions)** - Referência oficial
- **[Sintaxe de Fluxo de Trabalho](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)** - Referência completa de YAML
- **[Segurança (Security Hardening)](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)** - Melhores práticas de segurança
