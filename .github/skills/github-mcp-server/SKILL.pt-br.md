---
name: github-mcp-server
description: Referência para ferramentas, métodos e padrões de uso do servidor MCP do GitHub.
---


# Documentação do Servidor MCP do GitHub

Este arquivo documenta o servidor MCP (Protocolo de Contexto de Modelo) do GitHub, incluindo ferramentas e opções de configuração.

**Nota**: Este arquivo é gerado e atualizado automaticamente pelo fluxo de trabalho `github-mcp-tools-report.md`. Edições manuais podem ser sobrescritas.

**Última Atualização**: [A ser preenchido pelo fluxo de trabalho]

## Visão Geral

O servidor MCP do GitHub fornece aos agentes de IA acesso programático à API do GitHub através do Protocolo de Contexto de Modelo. Ele suporta dois modos de operação:

### Modo Local (Baseado em Docker)

- Executa como um contêiner Docker no runner do GitHub Actions
- Usa a variável de ambiente `GITHUB_PERSONAL_ACCESS_TOKEN` para autenticação
- Toolsets configuráveis via variável de ambiente `GITHUB_TOOLSETS`
- Suporta modo somente leitura via variável de ambiente `GITHUB_READ_ONLY`

### Modo Remoto (Hospedado)

- Conecta-se ao servidor MCP do GitHub hospedado em `https://api.githubcopilot.com/mcp/`
- Usa autenticação por token Bearer nos cabeçalhos HTTP
- Suporta modo somente leitura via cabeçalho `X-MCP-Readonly`
- Nenhum contêiner Docker necessário

## Configuração

### Configuração Básica

**Modo Local (Docker)**:
```yaml
tools:
  github:
    mode: "local"
    toolsets: [default]  # ou [repos, issues, pull_requests]
```

**Modo Remoto (Hospedado)**:
```yaml
tools:
  github:
    mode: "remote"
    toolsets: [default]  # ou [repos, issues, pull_requests]
```

### Modo Somente Leitura

Para restringir o servidor MCP do GitHub a operações somente leitura:

```yaml
tools:
  github:
    mode: "remote"
    read-only: true
    toolsets: [repos, issues]
```

### Autenticação Personalizada

Use um token do GitHub personalizado em vez do padrão:

```yaml
tools:
  github:
    mode: "remote"
    github-token: "${{ secrets.CUSTOM_GITHUB_PAT }}"
    toolsets: [repos, issues]
```

## Toolsets Disponíveis

O servidor MCP do GitHub organiza ferramentas em toolsets lógicos. Você pode habilitar toolsets específicos, usar `[default]` para os padrões recomendados, ou usar `[all]` para habilitar tudo.

:::note[Por que Usar Toolsets?]
O padrão `allowed:` para listar ferramentas individuais do GitHub **não é recomendado para novos fluxos de trabalho**. Nomes de ferramentas individuais podem mudar entre as versões do servidor MCP do GitHub, mas os toolsets fornecem uma API estável. Use sempre `toolsets:` em vez disso. Veja [Migração de Allowed para Toolsets](#migração-de-allowed-para-toolsets) para orientação sobre como atualizar fluxos de trabalho existentes.
:::

:::tip[Melhor Prática]
**Use sempre `toolsets:` para ferramentas do GitHub.** Toolsets fornecem:

- **Estabilidade**: Nomes de ferramentas podem mudar entre versões do servidor MCP, mas toolsets permanecem estáveis
- **Melhor organização**: Agrupamentos claros de funcionalidade relacionada
- **Funcionalidade completa**: Obtenha todas as ferramentas relacionadas automaticamente
- **Menos verbosidade**: Configuração mais limpa
- **À prova de futuro**: Novas ferramentas são incluídas automaticamente à medida que são adicionadas

:::

### Toolsets Padrão Recomendados

Os seguintes toolsets são habilitados por padrão quando `toolsets:` não é especificado:

- `context` - Contexto de usuário e ambiente (altamente recomendado)
- `repos` - Gerenciamento de repositório
- `issues` - Gerenciamento de issue
- `pull_requests` - Operações de pull request

**Nota**: O toolset `users` não está incluído por padrão e deve ser especificado explicitamente se necessário.

### Todos os Toolsets Disponíveis

| Toolset | Descrição | Ferramentas Comuns |
|---------|-------------|--------------|
| `context` | Contexto de usuário e ambiente | `get_teams`, `get_team_members` |
| `repos` | Gerenciamento de repositório | `get_repository`, `get_file_contents`, `search_code`, `list_commits` |
| `issues` | Gerenciamento de issue | `issue_read`, `list_issues`, `create_issue`, `search_issues` |
| `pull_requests` | Operações de pull request | `pull_request_read`, `list_pull_requests`, `create_pull_request` |
| `actions` | GitHub Actions/CI/CD | `list_workflows`, `list_workflow_runs`, `download_workflow_run_artifact` |
| `code_security` | Verificação de código e segurança | `list_code_scanning_alerts`, `get_code_scanning_alert` |
| `dependabot` | Gerenciamento de dependência | Alertas e atualizações do Dependabot |
| `discussions` | GitHub Discussions | `list_discussions`, `create_discussion` |
| `experiments` | Funcionalidades experimentais | APIs instáveis/preview |
| `gists` | Operações de Gist | `create_gist`, `list_gists` |
| `labels` | Gerenciamento de etiqueta (label) | `get_label`, `list_labels`, `create_label` |
| `notifications` | Notificações | `list_notifications`, `mark_notifications_read` |
| `orgs` | Gerenciamento de organização | `get_organization`, `list_organizations` |
| `projects` | Projetos GitHub | Operações de board de projeto |
| `secret_protection` | Verificação de segredo | Detecção e gerenciamento de segredo |
| `security_advisories` | Avisos de segurança | Criação e gerenciamento de avisos |
| `stargazers` | Estrelas de repositório | Operações relacionadas a estrelas |
| `users` | Perfis de usuário | `get_me`, `get_user`, `list_users` |
| `search` | Pesquisa avançada | Pesquisa entre repos, código, usuários |

## Ferramentas Disponíveis por Toolset

Esta seção mapeia ferramentas individuais para seus respectivos toolsets para ajudar na migração de `allowed:` para `toolsets:`.

### Toolset de Contexto

- `get_teams` - Lista times aos quais o usuário pertence
- `get_team_members` - Lista membros de um time específico

### Toolset Repos

- `get_repository` - Obtém informações do repositório
- `get_file_contents` - Lê conteúdo de arquivo do repositório
- `search_code` - Pesquisa código entre repositórios
- `list_commits` - Lista commits em um repositório
- `get_commit` - Obtém detalhes de um commit específico
- `get_latest_release` - Obtém a versão mais recente
- `list_releases` - Lista todas as versões

### Toolset Issues

- `issue_read` - Lê detalhes da issue
- `list_issues` - Lista issues em um repositório
- `create_issue` - Cria uma nova issue
- `update_issue` - Atualiza uma issue existente
- `search_issues` - Pesquisa issues entre repositórios
- `add_reaction` - Adiciona reação a uma issue ou comentário
- `create_issue_comment` - Adiciona um comentário a uma issue

### Toolset Pull Requests

- `pull_request_read` - Lê detalhes do pull request
- `list_pull_requests` - Lista pull requests em um repositório
- `get_pull_request` - Obtém detalhes de um pull request específico
- `create_pull_request` - Cria um novo pull request
- `search_pull_requests` - Pesquisa pull requests entre repositórios

### Toolset Actions

- `list_workflows` - Lista fluxos de trabalho do GitHub Actions
- `list_workflow_runs` - Lista execuções de fluxo de trabalho
- `get_workflow_run` - Obtém detalhes de uma execução de fluxo de trabalho específica
- `download_workflow_run_artifact` - Baixa artefatos de execução de fluxo de trabalho

### Toolset Code Security

- `list_code_scanning_alerts` - Lista alertas de verificação de código
- `get_code_scanning_alert` - Obtém detalhes de um alerta específico
- `create_code_scanning_alert` - Cria um alerta de verificação de código

### Toolset Discussions

- `list_discussions` - Lista discussões em um repositório
- `create_discussion` - Cria uma nova discussão

### Toolset Labels

- `get_label` - Obtém detalhes da etiqueta
- `list_labels` - Lista etiquetas em um repositório
- `create_label` - Cria uma nova etiqueta

### Toolset Users

- `get_me` - Obtém informações do usuário autenticado atual
- `get_user` - Obtém informações de perfil de usuário
- `list_users` - Lista usuários

### Toolset Notifications

- `list_notifications` - Lista notificações do usuário
- `mark_notifications_read` - Marca notificações como lidas

### Toolset Organizations

- `get_organization` - Obtém detalhes da organização
- `list_organizations` - Lista organizações

### Toolset Gists

- `create_gist` - Cria um novo gist
- `list_gists` - Lista os gists do usuário

## Detalhes de Autenticação

### Autenticação em Modo Remoto

O modo remoto usa autenticação por token Bearer:

**Cabeçalhos**:

- `Authorization: Bearer <token>` - Obrigatório para autenticação
- `X-MCP-Readonly: true` - Opcional, habilita modo somente leitura

**Fonte do Token**:

- Padrão: `${{ secrets.GH_AW_GITHUB_TOKEN }}` ou `${{ secrets.GITHUB_TOKEN }}`
- Personalizado: Configure via campo `github-token`

### Autenticação em Modo Local

O modo local usa variáveis de ambiente:

**Variáveis de Ambiente**:

- `GITHUB_PERSONAL_ACCESS_TOKEN` - Obrigatório para autenticação
- `GITHUB_READ_ONLY=1` - Opcional, habilita modo somente leitura
- `GITHUB_TOOLSETS=<lista-separada-por-vírgulas>` - Opcional, especifica toolsets habilitados

## Melhores Práticas

### Seleção de Toolset

1. **Comece com `[default]`**: Para a maioria dos fluxos de trabalho, os toolsets padrão recomendados fornecem funcionalidade suficiente
2. **Habilite toolsets específicos**: Habilite toolsets adicionais apenas quando precisar de sua funcionalidade específica
3. **Consideração de segurança**: Tenha em mente operações de escrita - considere usar modo somente leitura quando possível
4. **Desempenho**: Usar menos toolsets reduz o tempo de inicialização e o uso de memória

### Permissões de Token

Garanta que seu token do GitHub tenha permissões apropriadas para os toolsets que você está habilitando:

- Toolsets `repos`: Requer permissões de leitura/escrita de repositório
- Toolsets `issues`: Requer permissões de leitura/escrita de issues
- Toolsets `pull_requests`: Requer permissões de leitura/escrita de pull requests
- Toolsets `actions`: Requer permissões de leitura/escrita de ações
- Toolsets `discussions`: Requer permissões de leitura/escrita de discussões

### Modo Remoto vs. Local

**Use Modo Remoto quando**:

- Quiser uma inicialização mais rápida (sem contêiner Docker para iniciar)
- Estiver rodando em um ambiente do GitHub Actions com acesso à internet
- Quiser usar a versão mais recente sem especificar tags de imagem Docker

**Use Modo Local quando**:

- Precisar de uma versão específica do servidor MCP
- Quiser usar argumentos personalizados
- Estiver rodando em um ambiente sem acesso à internet
- Quiser testar com um build local do servidor MCP

## Migração de Allowed para Toolsets

Se você tem fluxos de trabalho existentes usando o padrão `allowed:`, recomendamos migrar para `toolsets:` para melhor manutenibilidade e estabilidade. Nomes de ferramentas individuais podem mudar entre versões do servidor MCP do GitHub, mas os toolsets fornecem uma API estável que não quebrará seus fluxos de trabalho.

### Exemplos de Migração

**Usando `allowed:` (não recomendado):**
```yaml
tools:
  github:
    allowed:
      - get_repository
      - get_file_contents
      - list_commits
      - list_issues
      - create_issue
      - update_issue
```

**Usando `toolsets:` (recomendado):**
```yaml
tools:
  github:
    toolsets: [repos, issues]
```

### Mapeamento de Ferramenta para Toolset

Use esta tabela para identificar qual toolset contém as ferramentas que você precisa:

| Ferramentas `allowed:` | Migrar para `toolsets:` |
|------------------|------------------------|
| `get_me` | `users` |
| `get_teams`, `get_team_members` | `context` |
| `get_repository`, `get_file_contents`, `search_code`, `list_commits` | `repos` |
| `issue_read`, `list_issues`, `create_issue`, `update_issue`, `search_issues` | `issues` |
| `pull_request_read`, `list_pull_requests`, `create_pull_request` | `pull_requests` |
| `list_workflows`, `list_workflow_runs`, `get_workflow_run` | `actions` |
| `list_code_scanning_alerts`, `get_code_scanning_alert` | `code_security` |
| `list_discussions`, `create_discussion` | `discussions` |
| `get_label`, `list_labels`, `create_label` | `labels` |
| `get_user`, `list_users` | `users` |
| Ferramentas mistas repos/issues/PRs | `[default]` |
| Todas as ferramentas | `[all]` |

### Passos Rápidos de Migração

1. **Identifique ferramentas em uso**: Revise sua lista `allowed:` atual
2. **Mapeie para toolsets**: Use a tabela acima para encontrar toolsets correspondentes
3. **Substitua configuração**: Altere `allowed:` para `toolsets:`
4. **Teste**: Execute `gh aw mcp inspect <workflow>` para verificar se as ferramentas estão disponíveis
5. **Compile**: Execute `gh aw compile` para atualizar o arquivo de lock

## Usando o Padrão Allowed com Servidores MCP Personalizados

:::note[Quando Usar Allowed]
O padrão `allowed:` é apropriado para:

- Servidores MCP personalizados (não GitHub)
- Migração gradual de fluxos de trabalho existentes
- Restrição de granularidade fina de ferramentas específicas dentro de um toolset

Para ferramentas do GitHub, use sempre `toolsets:` em vez de `allowed:`.
:::

O campo `allowed:` ainda pode ser usado para restringir ferramentas para servidores MCP personalizados:

```yaml
mcp-servers:
  notion:
    container: "mcp/notion"
    allowed: ["search_pages", "get_page"]  # Bom para servidores MCP personalizados
```

Para ferramentas do GitHub, `allowed:` pode ser combinado com `toolsets:` para restringir ainda mais o acesso, mas esse padrão não é recomendado para novos fluxos de trabalho.

## Limitações da API do GitHub

Nem todos os dados do GitHub são acessíveis através do servidor MCP do GitHub ou da API REST do GitHub. Esteja ciente dessas limitações ao projetar fluxos de trabalho para evitar falhas silenciosas ou resultados incompletos em tempo de execução.

### Dados de Faturamento e Custo

**❌ Não disponível via permissões de API padrão:**

- **Dados de custo detalhados por execução** — O GitHub Actions não expõe custos de execução por fluxo de trabalho através da API REST. Não existe endpoint para recuperar o custo exato de uma execução específica de fluxo de trabalho.
- **Resumo de faturamento de Actions** — Endpoints de faturamento (por exemplo, `/orgs/{org}/settings/billing/actions`) requerem escopo `admin:org`, que **não** é concedido por `actions:read` ou pelo `GITHUB_TOKEN` padrão.

**⚠️ Ao sugerir fluxos de trabalho de faturamento/custo, observe sempre:**

> Dados detalhados de faturamento e custo do GitHub Actions não são acessíveis através da API padrão do GitHub com permissões `actions:read`. Fluxos de trabalho que tentam ler dados de custo por execução ou resumos de faturamento falharão silenciosamente ou retornarão resultados vazios, a menos que um token de acesso pessoal com escopo `admin:org` seja configurado explicitamente.

**✅ Alternativas para relatório de custo:**

1. **Relatórios de uso do GitHub Actions** — Baixe relatórios de uso da interface do usuário de faturamento do GitHub (Configurações → Faturamento → Uso) ou via endpoint de exportação CSV de faturamento (requer escopo `admin:org` com um PAT).
2. **Interface do usuário de configurações de faturamento** — Direcione os usuários para `https://github.com/organizations/{org}/settings/billing` ou `https://github.com/settings/billing` para contas pessoais para visualizar dados de custo manualmente.
3. **Metadados de execução de fluxo de trabalho** — Use `list_workflow_runs` e `get_workflow_run` (disponível via toolset `actions`) para obter duração da execução, status e tempo — mas não custos em dólares.
4. **Rastreamento de custo de terceiros** — Integre com ferramentas de custo de CI de terceiros que usam acesso à API pré-autorizado.

### Acesso a Dados entre Organizações

**❌ Não disponível sem autorização explícita:**

- Fluxos de trabalho podem acessar dados apenas de repositórios e organizações aos quais o token do GitHub configurado recebeu acesso.
- Leituras de repositório entre organizações exigem um PAT ou token de GitHub App com acesso à organização de destino — o `GITHUB_TOKEN` padrão é limitado à organização do repositório atual apenas.
- Membros da organização e dados de time de *outras* organizações não são acessíveis sem permissões explícitas `read:org` nessas organizações.

### Associação de Organização e Dados Privados

**❌ Requer escopos adicionais:**

- **Listas de membros da organização** — Ler associação de organização privada requer escopo `read:org`; o `GITHUB_TOKEN` padrão expõe apenas associação pública.
- **Conteúdo de repositório privado** — Acessível apenas se o token tiver acesso explícito ao repositório.
- **Valores de segredo** — Segredos do GitHub são apenas de escrita através da API; seus valores não podem ser lidos após a criação.

### Limites de Taxa (Rate Limits)

**⚠️ Esteja ciente dos limites de taxa da API:**

- A API REST do GitHub impõe limites de taxa (normalmente 5.000 solicitações/hora para solicitações autenticadas com um PAT, menor para `GITHUB_TOKEN`).
- Fluxos de trabalho que realizam coleta de dados em massa (por exemplo, listar todas as execuções de fluxo de trabalho entre muitos repositórios) podem atingir limites de taxa. Projete fluxos de trabalho para paginar cuidadosamente e evitar solicitações desnecessárias.
- A API GraphQL possui limites de taxa separados com base na complexidade da consulta.

## Depuração

### Problemas Comuns

**Problema**: Ferramenta não encontrada ou não disponível

- **Solução**: Verifique se você está usando `allowed:` para restringir ferramentas. Considere usar `toolsets:` em vez disso para obter todas as ferramentas relacionadas.
- **Verifique**: Execute `gh aw mcp inspect <nome-do-fluxo-de-trabalho>` para ver quais ferramentas estão realmente disponíveis.

**Problema**: Funcionalidade faltando após especificar toolset

- **Causa**: Usando um toolset muito restrito que não inclui todas as ferramentas necessárias
- **Solução**: Adicione toolsets adicionais (por exemplo, `toolsets: [default, actions]`) ou use `[all]` para acesso total

**Problema**: Fluxo de trabalho usando lista `allowed:` é verboso e difícil de manter

- **Solução**: Migre para a configuração `toolsets:` usando o guia de migração acima

### Melhores Práticas para Depuração

1. **Comece com o toolset `[default]`**: A maioria dos fluxos de trabalho funciona bem com toolsets padrão
2. **Adicione toolsets específicos conforme necessário**: Adicione incrementalmente toolsets como `actions`, `discussions`, etc.
3. **Use `gh aw mcp inspect`**: Verifique quais ferramentas estão realmente disponíveis
4. **Verifique o mapeamento de ferramenta para toolset**: Consulte as tabelas acima para encontrar o toolset correto

## Referências

- [Repositório do Servidor MCP do GitHub](https://github.com/github/github-mcp-server)
- [Especificação do Protocolo de Contexto de Modelo](https://modelcontextprotocol.io/)
- [Documentação do GitHub Actions](https://docs.github.com/actions)
---
