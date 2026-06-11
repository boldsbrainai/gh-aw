---
title: Exemplos Multi-Repositório
description: Exemplos completos para gerenciar fluxos de trabalho em múltiplos repositórios do GitHub, incluindo sincronização de recursos, rastreamento cross-repo e atualizações em toda a organização.
---

Operações em múltiplos repositórios permitem coordenar o trabalho em múltiplos repositórios do GitHub enquanto mantém segurança e controles de acesso adequados. Esses exemplos demonstram padrões comuns para fluxos de trabalho cross-repo.

## Exemplos em Destaque

### [Sincronização de Recursos](/gh-aw/examples/multi-repo/feature-sync/)

Automatiza a sincronização de código de repositórios principais para sub-repositórios ou serviços downstream através de pull requests com detecção de mudança, filtros de caminho e suporte a sincronização bidirecional. Use para alternativas de monorepo, bibliotecas de componentes compartilhados, implantações multiplataforma ou manutenção de fork.

### [Rastreamento de Issue Cross-Repository](/gh-aw/examples/multi-repo/issue-tracking/)

Centraliza o rastreamento de issue criando automaticamente issues de rastreamento em um repositório central com sincronização de status e coordenação de múltiplos componentes. Use para visibilidade de arquitetura baseada em componentes, coordenação entre múltiplas equipes, iniciativas cross-project ou rastreamento de dependência upstream.

## Primeiros Passos

Todos os fluxos de trabalho multi-repo exigem autenticação adequada:

### Configuração de Personal Access Token (PAT)

```bash
# Crie PAT com permissões necessárias
gh auth token

# Armazene como segredo de repositório ou organização
gh aw secrets set GH_AW_CROSS_REPO_PAT --value "ghp_seu_token_aqui"
```

O PAT precisa de permissões **apenas nos repositórios de destino** (não no repositório de origem onde o fluxo de trabalho roda): `repo` para repos privados, `contents: write` para commits, `issues: write` para issues e `pull-requests: write` para PRs.

> [!TIP]
> **Melhor Prática de Segurança**: Se você só precisa ler de um repositório e escrever em outro, escope seu PAT para ter acesso de leitura na origem e acesso de escrita apenas nos repositórios de destino. Use tokens separados para diferentes operações quando possível.

### Configuração de GitHub App

Para maior segurança, use GitHub Apps para criação automática e revogação de tokens. Tokens de GitHub App são criados sob demanda, revogados automaticamente após a conclusão do job e fornecem melhor segurança do que PATs de longa duração.

Veja [Usando um GitHub App para Autenticação](/gh-aw/reference/auth/#using-a-github-app-for-authentication) para exemplos completos de configuração, incluindo escopo de repositório específico e acesso em toda a organização.

## Padrões Comuns

### Arquitetura Hub-and-Spoke

Repositório central agrega informações de múltiplos repositórios de componentes:

```text
Component Repo A ──┐
Component Repo B ──┼──> Central Tracker
Component Repo C ──┘
```

### Sincronização Upstream-to-Downstream

Repositório principal propaga mudanças para repositórios downstream:

```text
Main Repo ──> Sub-Repo Alpha
          ──> Sub-Repo Beta
          ──> Sub-Repo Gamma
```

### Coordenação em Nível de Organização

Fluxo de trabalho de controle cria issues em múltiplos repositórios:

```text
Control Workflow ──> Repo 1 (issue de rastreamento)
                 ──> Repo 2 (issue de rastreamento)
                 ──> Repo 3 (issue de rastreamento)
                 ──> ... (até o limite máximo)
```

## Safe Outputs Cross-Repository

A maioria dos tipos de safe output suporta o parâmetro `target-repo` para operações cross-repository. **Sem `target-repo`, esses safe outputs operam no repositório onde o fluxo de trabalho está rodando.**

| Safe Output | Suporte Cross-Repo | Caso de Uso de Exemplo |
|-------------|-------------------|------------------|
| `create-issue` | ✅ | Criar issues de rastreamento no repositório central |
| `add-comment` | ✅ | Comentar em issues em outros repos |
| `update-issue` | ✅ | Atualizar status de issue entre repos |
| `add-labels` | ✅ | Rotular issues em repos de destino |
| `create-pull-request` | ✅ | Criar PRs em repositórios downstream |
| `create-discussion` | ✅ | Criar discussões em qualquer repo |
| `create-agent-session` | ✅ | Criar tarefas em repos de destino |
| `update-release` | ✅ | Atualizar notas de versão entre repos |
| `update-project` | ✅ (`target_repo`) | Atualizar itens de projeto de outros repos |

**Exemplo de Configuração:**

```yaml wrap
safe-outputs:
  github-token: ${{ secrets.GH_AW_CROSS_REPO_PAT }}
  create-issue:
    target-repo: "org/tracking-repo"  # Cross-repo: cria no tracking-repo
    title-prefix: "[component] "
  add-comment:
    # Sem target-repo: opera no repositório atual
```

Veja [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/) para opções de configuração completas.

## Ferramentas da API GitHub para Acesso Multi-Repo

Habilite conjuntos de ferramentas GitHub para permitir que os agentes consultem múltiplos repositórios:

```yaml wrap
tools:
  github:
    toolsets: [repos, issues, pull_requests, actions]
```

Os agentes podem acessar **repos** (ler arquivos, pesquisar código, listar commits, obter releases), **issues** (listar e pesquisar em repositórios), **pull_requests** (listar e pesquisar PRs) e **actions** (execuções de fluxo de trabalho e artefatos).

## Melhores Práticas

Use GitHub Apps para revogação automática de token, escope PATs minimamente, rode tokens regularmente e armazene-os como segredos do GitHub. Defina limites `max` apropriados em safe outputs, use prefixos de título significativos e labels consistentes e inclua documentação clara nos itens criados. Valide o acesso ao repositório antes das operações, trate os limites de taxa adequadamente e monitore a execução do fluxo de trabalho. Teste com repositórios públicos primeiro, pilote com subconjuntos pequenos, verifique configurações e monitore custos.

## Tópicos Avançados

### Acesso a Repositório Privado

Ao trabalhar com repositórios privados, garanta que o proprietário do PAT tenha acesso ao repositório, instale GitHub Apps em organizações de destino, configure listas de repositório explicitamente e teste permissões antes da implantação total.

### Fluxos de Trabalho Determinísticos

Para acesso direto ao repositório, use um mecanismo de I.A. com passos personalizados via `actions/checkout`:

```yaml wrap
engine:
  id: claude
  steps:
    - name: Checkout main repo
      uses: actions/checkout@v6
      with:
        path: main-repo
    
    - name: Checkout secondary repo
      uses: actions/checkout@v6
      with:
        repository: org/secondary-repo
        token: ${{ secrets.GH_AW_CROSS_REPO_PAT }}
        path: secondary-repo
```

### Operações em Nível de Organização

Para fluxos de trabalho em toda a organização, use segredos em nível de organização, configure GitHub Apps em nível de organização, planeje lançamentos faseados e forneça comunicação clara.

## Guia Completo

Para documentação abrangente sobre o padrão de projeto MultiRepoOps, veja:

[Padrão de Projeto MultiRepoOps](/gh-aw/patterns/multi-repo-ops/)

## Documentação Relacionada

- [Operações Cross-Repository](/gh-aw/reference/cross-repository/) - Configuração de checkout e target-repo
- [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/) - Opções de configuração
- [Ferramentas GitHub](/gh-aw/reference/github-tools/) - Configuração de acesso à API
- [Melhores Práticas de Segurança](/gh-aw/introduction/architecture/) - Autenticação e segurança
- [Reutilizando Fluxos de Trabalho](/gh-aw/guides/packaging-imports/) - Compartilhando fluxos de trabalho
