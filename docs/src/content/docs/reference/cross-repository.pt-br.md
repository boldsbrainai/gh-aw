---
title: Operações entre repositórios
description: Configure fluxos de trabalho para acessar, modificar e operar entre múltiplos repositórios do GitHub usando checkout, target-repo e configurações de allowed-repos
sidebar:
  order: 850
---

Operações entre repositórios permitem que fluxos de trabalho acessem código de múltiplos repositórios e criem recursos (issues, PRs, comentários) em repositórios externos. Esta página documenta todos os recursos de frontmatter declarativos para fluxos de trabalho entre repositórios.

Recursos entre repositórios se enquadram em três categorias:

1. **Checkout entre repositórios** - Faça checkout de código de outros repositórios
2. **Leitura entre repositórios** - Leia issues, pull requests e outras informações de outros repositórios
3. **Safe Outputs entre repositórios** - Crie issues, PRs, comentários e outros recursos em repositórios externos usando `target-repo` e `allowed-repos` em safe outputs

Todos exigem autenticação adicional.

## Checkout entre repositórios (`checkout:`)

O campo de frontmatter `checkout:` controla como `actions/checkout` é invocado no job do agente. Use-o para fazer checkout de um ou mais repositórios, sobrescrever configurações de profundidade de busca (fetch depth) ou sparse-checkout, buscar refs adicionais (ex: todas as branches de PR abertas), ou desabilitar o checkout completamente com `checkout: false`.

Para fluxos de trabalho multirrepositório, liste múltiplas entradas para clonar vários repositórios no workspace. Marque o alvo primário do agente com `current: true` ao trabalhar a partir de um repositório central que tem como alvo um repositório diferente.

```yaml wrap
checkout:
  - fetch-depth: 0                 # checkout deste repositório com histórico completo
    fetch: ["refs/pulls/open/*"]   # busca todas as branches de PR abertas após checkout
  - repository: owner/other-repo   # outro repositório para fazer checkout
    path: ./libs/other             # caminho dentro do workspace para o qual fazer checkout
    github-token: ${{ secrets.CROSS_REPO_PAT }} # autenticação adicional para acesso entre repositórios
```

Veja [Checkout de repositório do GitHub](/gh-aw/reference/checkout/) para a referência completa de configuração, incluindo opções de busca, sparse checkout, regras de mesclagem e exemplos.

## Leitura entre repositórios

As [Ferramentas do GitHub](/gh-aw/reference/github-tools/) são usadas para ler informações como issues e pull requests de repositórios. Por padrão, essas ferramentas podem acessar o repositório atual e todos os repositórios públicos (se permitido pelo firewall de rede). Este conjunto pode ser restrito ainda mais usando [Restrições de Acesso a Repositório do GitHub](/gh-aw/reference/github-tools/#github-repository-access-restrictions-toolsgithuballowed-repos).

Para ler de outros repositórios privados, você deve configurar autorização adicional. Configure um PAT ou GitHub App na sua configuração de Ferramentas do GitHub:

```yaml wrap
tools:
  github:
    toolsets: [repos, issues, pull_requests]
    github-token: ${{ secrets.CROSS_REPO_PAT }}
```

Isso habilita operações como:

- Ler arquivos e pesquisar código em repositórios externos dinamicamente, mesmo que o repositório não tenha recebido checkout
- Consultar issues e pull requests de outros repos
- Acessar commits, releases e execuções de fluxo de trabalho entre repositórios
- Ler informações em nível de organização

Veja [Autenticação Adicional para Ferramentas do GitHub](/gh-aw/reference/github-tools/#additional-authentication-for-github-tools) para detalhes completos sobre como criar um PAT, usar um GitHub App ou usar o secret mágico `GH_AW_GITHUB_MCP_SERVER_TOKEN`.

## Safe Outputs entre repositórios

A maioria dos tipos de safe output suporta a criação de recursos em repositórios externos usando os parâmetros `target-repo` e `allowed-repos`.

### Repositório de destino (`target-repo`)

Especifique um único repositório de destino para criação de recursos:

```yaml wrap
safe-outputs:
  github-token: ${{ secrets.CROSS_REPO_PAT }}
  create-issue:
    target-repo: "org/tracking-repo"
    title-prefix: "[component] "
```

Sem `target-repo`, safe outputs operam no repositório onde o fluxo de trabalho está sendo executado.

### Repositório de destino curinga (`target-repo: "*"`)

Defina `target-repo: "*"` para permitir que o agente tenha como alvo dinâmico qualquer repositório em tempo de execução. Quando configurado, o agente recebe um parâmetro `repo` em sua chamada de ferramenta onde ele fornece o repositório de destino no formato `proprietário/repo`:

```yaml wrap
safe-outputs:
  github-token: ${{ secrets.CROSS_REPO_PAT }}
  create-issue:
    target-repo: "*"
    title-prefix: "[component] "
```

Use isso quando o repositório de destino não for conhecido no momento da autoria do fluxo de trabalho — por exemplo, ao construir um fluxo de trabalho que roteia issues para diferentes repositórios com base em labels ou conteúdo.

:::caution
Os seguintes tipos de safe-output **não** suportam `target-repo: "*"`: `create-pull-request-review-comment`, `reply-to-pull-request-review-comment`, `submit-pull-request-review`, `create-agent-session` e `manage-project-items`. Use um valor explícito `proprietário/repo` ou `allowed-repos` para esses tipos.
:::

### Repositórios permitidos (`allowed-repos`)

Permita que o agente selecione dinamicamente a partir de múltiplos repositórios:

```yaml wrap
safe-outputs:
  github-token: ${{ secrets.CROSS_REPO_PAT }}
  create-issue:
    target-repo: "org/default-repo"
    allowed-repos: ["org/repo-a", "org/repo-b", "org/repo-c"]
    title-prefix: "[cross-repo] "
```

Quando `allowed-repos` é especificado:

- O agente pode incluir um campo `repo` na saída para selecionar qual repositório
- O repositório de destino (de `target-repo` ou repositório atual) é sempre implicitamente permitido
- Cria uma união de destinos permitidos

### Requisito de Checkout para `push-to-pull-request-branch`

Diferente de outros tipos de safe output, `push-to-pull-request-branch` com `target-repo` exige que o repositório de destino tenha recebido **checkout no workspace do fluxo de trabalho** usando o campo de frontmatter `checkout:` com um `path:` especificado. Sem um checkout, o agente não tem histórico git local para criar e enviar um patch.

Veja o exemplo [Push agendado para branch de pull-request](#example-scheduled-push-to-pull-request-branch) e a documentação [Uso entre repositórios de Push para branch de PR](/gh-aw/reference/safe-outputs-pull-requests/#cross-repo-usage) para uma configuração completa.

## Exemplos

### Exemplo: Desenvolvimento em Monorepo

Isso usa múltiplas entradas `checkout:` para fazer checkout de diferentes partes do mesmo repositório com configurações diferentes:

```aw wrap
---
on:
  pull_request:
    types: [opened, synchronize]

checkout:
  - fetch-depth: 0
  - repository: org/shared-libs
    path: ./libs/shared
    ref: main
    github-token: ${{ secrets.LIBS_PAT }}
  - repository: org/config-repo
    path: ./config
    sparse-checkout: |
      defaults/
      overrides/

permissions:
  contents: read
  pull-requests: read
---

# Análise de PR entre repositórios

Analise este PR considerando a compatibilidade da biblioteca compartilhada e os padrões de configuração.

Verifique a compatibilidade com bibliotecas compartilhadas em `./libs/shared` e verifique a configuração em relação aos padrões em `./config`.
```

### Exemplo: Rastreamento Hub-and-Spoke

Isso cria issues em um repositório de rastreamento central quando issues são abertas em repositórios de componentes:

```aw wrap
---
on:
  issues:
    types: [opened, labeled]

permissions:
  contents: read
  issues: read

safe-outputs:
  github-token: ${{ secrets.CROSS_REPO_PAT }}
  create-issue:
    target-repo: "org/central-tracker"
    title-prefix: "[component-a] "
    labels: [tracking, multi-repo]
    max: 1
---

# Rastreador de Issue entre repositórios

Quando issues são criadas neste repositório de componente, crie issues de rastreamento no repositório de coordenação central.

Analise a issue e crie uma issue de rastreamento que:
- Faz link de volta para a issue de componente original
- Resume o problema e o impacto
- Marca equipes relevantes para coordenação
```

### Exemplo: Análise entre repositórios

Isso faz checkout de múltiplos repositórios e compara padrões de código entre eles:

```aw wrap
---
on:
  issue_comment:
    types: [created]

tools:
  github:
    toolsets: [repos, issues, pull_requests]
    github-token: ${{ secrets.CROSS_REPO_PAT }}

permissions:
  contents: read
  issues: read

safe-outputs:
  github-token: ${{ secrets.CROSS_REPO_WRITE_PAT }}
  add-comment:
    max: 1
---

# Pesquisa de Código em Múltiplos Repositórios

Pesquise padrões semelhantes em org/repo-a, org/repo-b e org/repo-c.

Analise como cada repositório implementa autenticação e forneça uma comparação.
```

### Exemplo: Fluxos de trabalho multirrepositório determinísticos

Para acesso direto ao repositório sem envolvimento do agente, use etapas personalizadas com `actions/checkout`:

```aw wrap
---
engine:
  id: claude

steps:
  - name: Checkout repo principal
    uses: actions/checkout@v6
    with:
      path: main-repo

  - name: Checkout repo secundário
    uses: actions/checkout@v6
    with:
      repository: org/secondary-repo
      token: ${{ secrets.CROSS_REPO_PAT }}
      path: secondary-repo

permissions:
  contents: read
---

# Comparar Repositórios

Compare a estrutura de código entre main-repo e secondary-repo.
```

Esta abordagem oferece controle total sobre o tempo e a configuração do checkout.

### Exemplo: Push Agendado para branch de Pull-Request

Um fluxo de trabalho agendado que automaticamente envia alterações para branches de pull-request abertos em outro repositório precisa buscar essas branches após o checkout. Sem `fetch:`, apenas a branch padrão (geralmente `main`) está disponível.

```aw wrap
---
on:
  schedule: hourly

checkout:
  - repository: org/target-repo
    github-token: ${{ secrets.GH_AW_SIDE_REPO_PAT }}
    fetch: ["refs/pulls/open/*"]   # busca todas as branches de PR abertas após checkout
    current: true

permissions:
  contents: read

safe-outputs:
  github-token: ${{ secrets.GH_AW_SIDE_REPO_PAT }}
  push-to-pull-request-branch:
    target-repo: "org/target-repo"
---

# Atualização Automática de Branches de PR

Verifique pull requests abertos em org/target-repo e aplique quaisquer atualizações
automatizadas pendentes a cada branch de PR.
```

`fetch: ["refs/pulls/open/*"]` faz com que uma etapa `git fetch` seja executada após `actions/checkout`, baixando todos os refs head de PR abertos para o workspace. O agente pode então inspecionar e modificar essas branches diretamente.

## Documentação relacionada

- [Checkout de repositório do GitHub](/gh-aw/reference/checkout/) - Referência completa de configuração de checkout
- [Padrão MultiRepoOps](/gh-aw/patterns/multi-repo-ops/) - Padrão de fluxo de trabalho entre repositórios
- [Padrão CentralRepoOps](/gh-aw/patterns/central-repo-ops/) - Padrão de plano de controle central
- [Referência de Ferramentas do GitHub](/gh-aw/reference/github-tools/) - Configuração completa de Ferramentas do GitHub
- [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/) - Configuração completa de safe output
- [Referência de Autenticação](/gh-aw/reference/auth/) - Configuração de PAT e GitHub App
- [Exemplos de multirrepositório](/gh-aw/examples/multi-repo/) - Exemplos funcionais completos
