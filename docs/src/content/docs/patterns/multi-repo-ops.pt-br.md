---
title: MultiRepoOps
description: Coordene fluxos de trabalho agenticos em múltiplos repositórios do GitHub com rastreamento automatizado de issues, sincronização de recursos e aplicação em toda a organização
sidebar:
  badge: { text: 'Avançado', variant: 'caution' }
---

MultiRepoOps estende padrões de automação operacional (IssueOps, ChatOps, etc.) para múltiplos repositórios do GitHub. Usando safe outputs entre repositórios e autenticação segura, o MultiRepoOps permite coordenar o trabalho entre projetos relacionados — criando issues de rastreamento em repos centrais, sincronizando funcionalidades para sub-repositórios e aplicando políticas em toda a organização — tudo através de fluxos de trabalho impulsionados por IA.

## Quando usar o MultiRepoOps

Use o MultiRepoOps para sincronização de funcionalidades (repo principal para sub-repos), rastreamento de issue hub-and-spoke (componentes → rastreador central), aplicação em toda a organização (patches de segurança, rollout de políticas) e sincronização de funcionalidades upstream/downstream.

## Como funciona

Os fluxos de trabalho MultiRepoOps usam o parâmetro `target-repo` em safe outputs para criar issues, pull requests e comentários em repositórios externos. Combinado com conjuntos de ferramentas da API do GitHub para consultar repos remotos e autenticação adequada (tokens PAT ou GitHub App), os fluxos de trabalho podem coordenar operações complexas entre múltiplos repositórios automaticamente.

```aw wrap
---
on:
  issues:
    types: [opened, labeled]
permissions:
  contents: read
  actions: read
safe-outputs:
  github-token: ${{ secrets.GH_AW_CROSS_REPO_PAT }}
  create-issue:
    target-repo: "org/tracking-repo"
    title-prefix: "[component-a] "
    labels: [tracking, multi-repo]
---

# Rastreador de Issue Multi-Repo

Quando issues são criadas em repositórios de componentes, crie automaticamente issues de rastreamento no repositório de coordenação central.

Analise a issue e crie uma issue de rastreamento que:
- Contém link para a issue original do componente
- Resume o problema e o impacto
- Marca as equipes relevantes em toda a organização
- Fornece contexto para coordenação entre componentes
```

## Autenticação para Acesso entre Repositórios

Operações entre repositórios requerem autenticação além do `GITHUB_TOKEN` padrão, que é limitado ao repositório atual.

### Personal Access Token (PAT)

Configure um Personal Access Token com acesso aos repositórios de destino:

```yaml wrap
safe-outputs:
  github-token: ${{ secrets.GH_AW_CROSS_REPO_PAT }}
  create-issue:
    target-repo: "org/tracking-repo"
```

O PAT precisa de permissões apenas nos repositórios de destino — `contents: write`, `issues: write` ou `pull-requests: write` dependendo das operações (não no repositório de origem).

> [!TIP]
> Melhores Práticas de Segurança
> Se você precisar apenas ler de um repo e escrever em outro, configure seu PAT para ter acesso de leitura na origem e acesso de escrita apenas nos repositórios de destino.

### Token de Instalação do GitHub App

Para segurança aprimorada, use GitHub Apps com revogação automática de token. Tokens de GitHub App fornecem criação por job, revogação automática após a conclusão do job, permissões refinadas e melhor atribuição do que PATs de longa duração.

Veja [Usando um GitHub App para Autenticação](/gh-aw/reference/auth/#using-a-github-app-for-authentication) para configuração completa, incluindo escopo específico de repositório e acesso a toda a organização.

## Padrões Comuns de MultiRepoOps

Três topologias cobrem a maioria dos casos de uso:

| Padrão | Descrição |
|---------|-------------|
| **Hub-and-spoke** | Cada fluxo de trabalho de componente cria issues de rastreamento em um repo central via `target-repo` |
| **Upstream-to-downstream** | Repo principal propaga mudanças usando `create-pull-request` com `target-repo` por downstream |
| **Broadcast em toda a org** | Fluxo de trabalho único cria issues em muitos repos até o limite de `max` configurado |

## Safe Outputs Entre Repositórios

A maioria dos tipos de safe output suporta o parâmetro `target-repo` para operações entre repositórios. **Sem `target-repo`, esses safe outputs operam no repositório onde o fluxo de trabalho está sendo executado.**

| Safe Output | Suporte entre Repositórios | Exemplo de Caso de Uso |
|-------------|-------------------|------------------|
| `create-issue` | ✅ | Criar issues de rastreamento no repo central |
| `add-comment` | ✅ | Comentar em issues de outros repos |
| `update-issue` | ✅ | Atualizar status de issue em todos os repos |
| `add-labels` | ✅ | Marcar issues em repos de destino |
| `create-pull-request` | ✅ | Criar PRs em repos de downstream |
| `create-discussion` | ✅ | Criar discussões em qualquer repo |
| `create-agent-session` | ✅ | Criar tarefas em repos de destino |
| `update-release` | ✅ | Atualizar notas de release em todos os repos |

## Ensinando Agentes o Acesso Multi-Repo

Habilite conjuntos de ferramentas do GitHub para permitir que agentes consultem múltiplos repositórios:

```yaml wrap
tools:
  github:
    toolsets: [repos, issues, pull_requests, actions]
    github-token: ${{ secrets.CROSS_REPO_PAT }}  # Necessário para leitura entre repositórios
```

> [!IMPORTANT]
> Ao ler de repositórios diferentes do repositório do fluxo de trabalho, você deve configurar autenticação adicional. O `GITHUB_TOKEN` padrão só tem acesso ao repositório atual. Use um PAT, token de GitHub App ou o segredo mágico `GH_AW_GITHUB_MCP_SERVER_TOKEN`. Veja a [Referência de Ferramentas GitHub](/gh-aw/reference/github-tools/) para detalhes.

As instruções do agente podem referenciar repositórios remotos:

```markdown
Pesquise por issues abertas em org/upstream-repo relacionadas a autenticação.
Verifique as últimas notas de release de org/dependency-repo.
Compare a estrutura de código entre este repo e org/reference-repo.
```

## Fluxos de Trabalho Multi-Repo Determinísticos

Para acesso direto ao repositório sem envolvimento de agente, use um engine de IA com etapas personalizadas:

```aw wrap
---
engine:
  id: claude

steps:
  - name: Checkout repo principal
    uses: actions/checkout@v6
    with:
      path: main-repo

  - name: Checkout repositório secundário
    uses: actions/checkout@v6
    with:
      repository: org/secondary-repo
      token: ${{ secrets.GH_AW_CROSS_REPO_PAT }}
      path: secondary-repo

  - name: Comparar e sincronizar
    run: |
      # Lógica de sincronização determinística
      rsync -av main-repo/shared/ secondary-repo/shared/
      cd secondary-repo
      git add .
      git commit -m "Sincronização do repo principal"
      git push
---

# Sincronização Determinística de Funcionalidade

Fluxo de trabalho que faz checkout direto de múltiplos repos e sincroniza arquivos.
```

## Exemplos de Fluxos de Trabalho

Explore exemplos detalhados de MultiRepoOps:

- **[Sincronização de Funcionalidade](/gh-aw/examples/multi-repo/feature-sync/)** - Sincronize mudanças de código do repo principal para sub-repositórios
- **[Rastreamento de Issue Multi-Repo](/gh-aw/examples/multi-repo/issue-tracking/)** - Arquitetura de rastreamento hub-and-spoke

## Melhores Práticas

Use GitHub Apps em vez de PATs para revogação automática de token; escope os tokens minimamente aos repositórios de destino. Defina limites de `max` apropriados e convenções consistentes de label/prefixo. Teste contra repositórios públicos antes de implementar em alvos privados ou em toda a organização.

## Relacionado

- [IssueOps](/gh-aw/patterns/issue-ops/) — Automação de issue em repo único
- [ChatOps](/gh-aw/patterns/chat-ops/) — Fluxos de trabalho conduzidos por comando
- [Orquestração](/gh-aw/patterns/orchestration/) — Coordenação de iniciativa de múltiplas issues
- [Operações entre Repositórios](/gh-aw/reference/cross-repository/) — Configuração de checkout e `target-repo`
- [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/) — Configuração completa de safe output
- [Ferramentas GitHub](/gh-aw/reference/github-tools/) — Conjuntos de ferramentas da API do GitHub
- [Reutilizando Fluxos de Trabalho](/gh-aw/guides/packaging-imports/) — Compartilhando fluxos de trabalho entre repos
