---
title: Filtragem de Integridade do GitHub
description: Como a filtragem de integridade restringe o acesso do agente ao conteúdo do GitHub com base na confiança do autor e no status de merge, e como eventos filtrados aparecem nos logs.
sidebar:
  order: 680
---

A filtragem de integridade (`tools.github.min-integrity`) controla qual conteúdo do GitHub um agente pode acessar durante uma execução de fluxo de trabalho. Em vez de filtrar por permissões, ela filtra por **confiança**: a associação do autor de uma issue, pull request ou comentário, e se esse conteúdo foi mesclado no branch principal.

## Como Funciona

O gateway MCP intercepta chamadas de ferramenta para o GitHub e aplica verificações de integridade a cada item de conteúdo retornado. Se o nível de integridade de um item estiver abaixo do mínimo configurado, o gateway o remove antes que o motor de IA o veja. Isso acontece de forma transparente — o agente recebe um conjunto de resultados reduzido, e itens filtrados são registrados como eventos `DIFC_FILTERED` para inspeção posterior.

## Configuração

Defina `min-integrity` sob `tools.github` no seu frontmatter de fluxo de trabalho:

```aw wrap
tools:
  github:
    min-integrity: approved
```

`min-integrity` pode ser especificado sozinho. Quando `allowed-repos` é omitido, ele assume como padrão `"all"`. Se `allowed-repos` também for especificado, ambos os campos devem estar presentes.

```aw wrap
tools:
  github:
    allowed-repos: "myorg/*"
    min-integrity: approved
```

## Referência de Configuração

Todas as entradas de filtragem de integridade são especificadas sob `tools.github` no frontmatter do seu fluxo de trabalho. A tabela abaixo resume cada campo disponível:

| Campo | Tipo | Obrigatório | Padrão | Descrição |
|-------|------|----------|---------|-------------|
| `min-integrity` | string | Sim (quando qualquer campo de política de proteção é usado) | `approved` para repos públicos; none para privados | Nível de integridade mínimo: `merged`, `approved`, `unapproved` ou `none` |
| `allowed-repos` | string ou array | Não | `"all"` | Escopo do repositório: `"all"`, `"public"` ou um array de padrões (ex: `["myorg/*", "partner/repo"]`) |
| `blocked-users` | array ou expressão | Não | `[]` | Nomes de usuário do GitHub cujo conteúdo é negado incondicionalmente |
| `trusted-users` | array ou expressão | Não | `[]` | Nomes de usuário do GitHub elevados à integridade `approved` independentemente da associação do autor |
| `approval-labels` | array ou expressão | Não | `[]` | Nomes de label do GitHub que promovem itens para integridade `approved` |
| `refusal-labels` | array ou expressão | Não | `[]` | Nomes de label do GitHub que rebaixam itens para integridade `none`, substituindo qualquer promoção de `trusted-users` ou `approval-labels` |
| `integrity-proxy` | booleano | Não | `true` | Se deve executar o proxy DIFC para chamadas CLI `gh` de pré-agente. Defina como `false` para desabilitar |
| `endorsement-reactions` | array | Não | `["THUMBS_UP", "HEART"]` (quando `integrity-reactions` habilitado) | Tipos de reação que promovem a integridade do item para `approved`. Requer `features.integrity-reactions: true` |
| `disapproval-reactions` | array | Não | `["THUMBS_DOWN", "CONFUSED"]` (quando `integrity-reactions` habilitado) | Tipos de reação que rebaixam a integridade do item. Requer `features.integrity-reactions: true` |
| `endorser-min-integrity` | string | Não | `approved` (quando `integrity-reactions` habilitado) | Integridade mínima do reator para que um endosso ou reprovação tenha efeito. Requer `features.integrity-reactions: true` |
| `disapproval-integrity` | string | Não | `none` (quando `integrity-reactions` habilitado) | Nível de integridade atribuído quando uma reação de reprovação qualificada é adicionada. Requer `features.integrity-reactions: true` |

## Níveis de Integridade

A hierarquia completa de integridade, do nível mais alto para o mais baixo:

```text
merged > approved > unapproved > none > blocked
```

| Nível | O que se qualifica neste nível |
|-------|------------------------------|
| `merged` | Pull requests que foram mesclados e commits alcançáveis a partir do branch padrão (qualquer autor) |
| `approved` | Objetos autorados por `OWNER`, `MEMBER` ou `COLLABORATOR`; PRs não-fork em repos públicos; todos os itens em repos privados; bots de plataforma reconhecidos (ex: dependabot); usuários listados em `trusted-users` |
| `unapproved` | Objetos autorados por `CONTRIBUTOR` ou `FIRST_TIME_CONTRIBUTOR` |
| `none` | Todos os objetos, incluindo `FIRST_TIMER` e usuários sem associação (`NONE`) |
| `blocked` | Itens autorados por usuários em `blocked-users` — sempre negados, não podem ser promovidos |

Os quatro níveis configuráveis (`merged`, `approved`, `unapproved`, `none`) são cumulativos e ordenados do mais restritivo para o menos restritivo. Definir `min-integrity: approved` significa que apenas itens no nível `approved` **ou superior** (`merged`) chegam ao agente. Itens em `unapproved` ou `none` são filtrados.

`blocked` não é um valor de `min-integrity` configurável — é atribuído automaticamente a itens de usuários na lista `blocked-users` e é sempre negado independentemente do limite configurado.

**`merged`** é o nível configurável mais restritivo. Um pull request qualifica-se como `merged` quando foi mesclado no branch de destino. Commits qualificam-se quando são alcançáveis a partir do branch padrão. Isso é útil para fluxos de trabalho que devem agir apenas em conteúdo de produção.

**`approved`** corresponde a usuários que têm um relacionamento de confiança formal com o repositório: proprietários, membros e colaboradores. Itens em repositórios privados são automaticamente elevados para `approved` (já que apenas colaboradores podem acessá-los). Bots de plataforma reconhecidos, como dependabot e github-actions, também recebem integridade `approved`. Usuários listados em `trusted-users` também são elevados para este nível. Esta é a escolha mais comum para fluxos de trabalho em repositórios públicos.

**`unapproved`** inclui contribuidores que já tiveram código mesclado anteriormente, bem como contribuidores de primeira viagem. Apropriado quando a participação da comunidade é bem-vinda e as saídas do fluxo de trabalho são revisadas antes de serem aplicadas.

**`none`** permite que todo o conteúdo passe. Use isso deliberadamente, com salvaguardas apropriadas, para fluxos de trabalho projetados para processar entrada não confiável — como bots de triagem ou detecção de spam.

**`blocked`** situa-se abaixo de `none` e representa uma decisão de confiança negativa explícita. Itens neste nível são incondicionalmente negados — mesmo `min-integrity: none` não os permite passar. Veja [Bloqueando usuários específicos](#blocking-specific-users) abaixo.

## Escopo para Repositórios

`allowed-repos` define quais repositórios a política de proteção se aplica. Aceita três formas:

- **`"all"`** — Todos os repositórios que o token pode acessar (padrão quando omitido).
- **`"public"`** — Apenas repositórios públicos.
- **Um array de padrões** — Repositórios específicos ou curingas de proprietário.

```aw wrap
tools:
  github:
    allowed-repos:
      - "myorg/*"
      - "partner/shared-repo"
    min-integrity: approved
```

Padrões de repositório devem estar em minúsculas e seguir um destes formatos:

| Padrão | Significado |
|---------|---------|
| `owner/*` | Todos os repositórios sob `owner` |
| `owner/prefix*` | Repositórios sob `owner` cujo nome começa com `prefix` |
| `owner/repo` | Um repositório específico único |

## Ajustando a Integridade por Item

Além de definir um nível mínimo, você pode substituir a integridade para autores ou labels específicos.

### Bloqueando usuários específicos

`blocked-users` bloqueia incondicionalmente o conteúdo dos nomes de usuário do GitHub listados, independentemente de `min-integrity`, `trusted-users` ou qualquer label. Itens bloqueados recebem uma integridade efetiva de `blocked` (abaixo de `none`) e são sempre negados.

```aw wrap
tools:
  github:
    min-integrity: none
    blocked-users:
      - "spam-bot"
      - "compromised-account"
```

Use isso para suprimir conteúdo de contas sabidamente ruins — bots automatizados, usuários comprometidos ou contribuidores externos aguardando revisão de segurança.

### Confiando em usuários específicos

`trusted-users` eleva o conteúdo dos nomes de usuário do GitHub listados para a integridade `approved`, independentemente da associação do autor. Isso é útil para contratados, desenvolvedores parceiros ou contribuidores externos que devem ser tratados como confiáveis, embora o GitHub os classifique como `CONTRIBUTOR` ou `FIRST_TIME_CONTRIBUTOR`.

```aw wrap
tools:
  github:
    min-integrity: approved
    trusted-users:
      - "contractor-1"
      - "partner-dev"
```

A elevação de confiança apenas aumenta a integridade — ela nunca a diminui. Um usuário já em `merged` permanece em `merged`. `blocked-users` sempre tem precedência: se um usuário aparecer tanto em `blocked-users` quanto em `trusted-users`, ele é bloqueado.

`trusted-users` requer que `min-integrity` seja definido.

### Promovendo itens via labels

`approval-labels` promove itens que carregam qualquer label do GitHub listada para a integridade `approved`, permitindo fluxos de trabalho de revisão humana onde um revisor confiável etiqueta o conteúdo para sinalizar que ele é seguro para o agente.

```aw wrap
tools:
  github:
    min-integrity: approved
    approval-labels:
      - "human-reviewed"
      - "safe-for-agent"
```

Isso é útil quando a `min-integrity` de um fluxo de trabalho normalmente filtraria contribuições externas, mas um mantenedor pode etiquetar itens específicos para permitir que eles passem.

A promoção apenas aumenta a integridade — ela nunca a diminui. Um item já em `merged` permanece em `merged`. A exclusão de usuário bloqueado sempre tem precedência: os itens de um usuário bloqueado permanecem bloqueados mesmo se carregarem uma label de aprovação.

### Recusando itens via labels

`refusal-labels` é o inverso de `approval-labels`. Itens que carregam qualquer label do GitHub listada têm sua integridade efetiva rebaixada para `none`, independentemente da associação do autor ou de qualquer promoção de `trusted-users` ou `approval-labels`.

```aw wrap
tools:
  github:
    min-integrity: approved
    refusal-labels:
      - "needs-security-review"
      - "do-not-automate"
```

Isso é útil quando a `min-integrity` de um fluxo de trabalho normalmente permitiria certo conteúdo, mas um mantenedor pode etiquetar itens específicos para suprimi-los do agente — por exemplo, issues marcadas como sensíveis à segurança ou pull requests pendentes de uma verificação de conformidade manual.

A recusa sempre substitui a promoção: se um item carrega tanto uma label de `approval-labels` quanto uma label de `refusal-labels`, a integridade efetiva do item deve ser `none`. A exclusão de usuário bloqueado ainda tem precedência: os itens de um usuário bloqueado permanecem `blocked` independentemente de quaisquer labels.

### Promovendo e rebaixando itens via reações

`features.integrity-reactions: true` permite que mantenedores ajustem a integridade do item usando reações do GitHub, sem adicionar labels ou modificar o estado da issue. Disponível a partir do gh-aw v0.68.2.

```aw wrap
features:
  integrity-reactions: true
tools:
  github:
    min-integrity: approved
```

Quando habilitado, o compilador habilita automaticamente o proxy da CLI (necessário para identificar autores de reação) e injeta a configuração de reação padrão. Quando uma conta em ou acima de `endorser-min-integrity` adiciona uma reação de endosso a uma issue ou comentário, a integridade do item é promovida para `approved`. Uma reação de reprovação de tal conta define a integridade do item para `disapproval-integrity`.

Os padrões são `endorsement-reactions: [THUMBS_UP, HEART]`, `disapproval-reactions: [THUMBS_DOWN, CONFUSED]`, `endorser-min-integrity: approved` e `disapproval-integrity: none`. Para sobrescrevê-los, defina os campos de reação explicitamente sob `tools.github`:

```aw wrap
tools:
  github:
    endorsement-reactions:
      - "THUMBS_UP"
      - "HEART"
    disapproval-reactions:
      - "THUMBS_DOWN"
    endorser-min-integrity: merged
    disapproval-integrity: unapproved
```

Valores de reação válidos: `THUMBS_UP`, `THUMBS_DOWN`, `HEART`, `HOORAY`, `CONFUSED`, `ROCKET`, `EYES`, `LAUGH`. Os campos de reação só entram em vigor quando `features.integrity-reactions: true` também está definido.

### Usando expressões do GitHub Actions

`blocked-users`, `trusted-users`, `approval-labels` e `refusal-labels` podem cada um aceitar uma expressão do GitHub Actions em vez de um array literal. A expressão é avaliada em tempo de execução e deve ser resolvida para uma lista de valores separados por vírgula ou nova linha.

```aw wrap
tools:
  github:
    min-integrity: approved
    blocked-users: ${{ vars.BLOCKED_USERS }}
    trusted-users: ${{ vars.TRUSTED_USERS }}
    approval-labels: ${{ vars.APPROVAL_LABELS }}
    refusal-labels: ${{ vars.REFUSAL_LABELS }}
```

Isso é útil para gerenciar listas centralmente via variáveis de repositório ou organização do GitHub em vez de duplicá-las em fluxos de trabalho.

### Computação de integridade efetiva

O gateway computa a integridade efetiva de cada item nesta ordem:

1. **Início** com o nível de integridade base a partir de metadados do GitHub (associação do autor, status de mesclagem, visibilidade do repo).
2. **Se o autor estiver em `blocked-users`**: integridade efetiva → `blocked` (sempre negado).
3. **Senão, se o item tiver uma label em `refusal-labels`**: integridade efetiva → `none` (rebaixado, substitui qualquer promoção das etapas 4–5).
4. **Senão, se o autor estiver em `trusted-users`**: integridade efetiva → max(base, `approved`).
5. **Senão, se o item tiver uma label em `approval-labels`**: integridade efetiva → max(base, `approved`).
6. **Senão**: integridade efetiva → base.

A verificação de limite `min-integrity` é aplicada após esta computação.

## Gerenciamento Centralizado via Variáveis do GitHub

Cada campo de lista por item (`blocked-users`, `trusted-users`, `approval-labels`, `refusal-labels`) PODE ser estendido centralmente usando variáveis de repositório ou organização do GitHub. O runtime DEVE unir os valores por fluxo de trabalho com a variável correspondente no momento da execução:

| Campo do Fluxo de Trabalho | Variável do GitHub |
|---------------|----------------|
| `blocked-users` | `GH_AW_GITHUB_BLOCKED_USERS` |
| `trusted-users` | `GH_AW_GITHUB_TRUSTED_USERS` |
| `approval-labels` | `GH_AW_GITHUB_APPROVAL_LABELS` |
| `refusal-labels` | `GH_AW_GITHUB_REFUSAL_LABELS` |

Por exemplo, se um fluxo de trabalho declara `blocked-users: ["spam-bot"]` e a variável de organização `GH_AW_GITHUB_BLOCKED_USERS` está definida como `compromised-acct,old-bot`, a lista efetiva de blocked-users no tempo de execução é `["spam-bot", "compromised-acct", "old-bot"]`.

Variáveis são divididas por vírgulas e novas linhas, aparadas de espaços em branco e deduplicadas. Defina-as como variáveis de repositório (em **Configurações → Segredos e variáveis → Ações → Variáveis**) ou como variáveis em nível de organização para aplicá-las a todos os fluxos de trabalho.

Este mecanismo permite que uma equipe de segurança mantenha uma lista compartilhada de blocked-users, política de approval-labels ou política de refusal-labels sem modificar arquivos de fluxo de trabalho individuais.

## Comportamento Padrão

Para **repositórios públicos**, se nenhuma `min-integrity` for configurada, o runtime aplica automaticamente `min-integrity: approved`. Isso protege fluxos de trabalho públicos mesmo quando a autenticação adicional não foi configurada.

Para **repositórios privados e internos**, nenhuma política de proteção é aplicada automaticamente. O conteúdo de todos os usuários é acessível por padrão.

## Proxy de Integridade de Pré-Agente

Quando uma política de guarda é configurada (`min-integrity` está definido), o compilador injeta passos de proxy que filtram chamadas CLI `gh` em passos de configuração de pré-agente. Isso garante que passos personalizados executados antes do agente vejam as mesmas respostas de API filtradas por integridade sob as quais o próprio agente opera.

O proxy:

- Roteia chamadas CLI `gh` por meio da filtragem de integridade usando o mesmo container de gateway MCP.
- Aplica os campos de política de proteção estática (`min-integrity` e `allowed-repos`) que estão disponíveis no momento da compilação.
- NÃO aplica `blocked-users`, `trusted-users`, `approval-labels` ou `refusal-labels` (eles são resolvidos no momento da execução após o proxy iniciar).
- É iniciado automaticamente antes de passos personalizados e parado antes que o gateway MCP inicie para evitar dupla filtragem.

### Desabilitando o proxy

O proxy é habilitado por padrão sempre que uma política de guarda é configurada. Para desativá-lo, defina `integrity-proxy: false`:

```aw wrap
tools:
  github:
    min-integrity: approved
    integrity-proxy: false
```

Esta é uma válvula de escape de opt-out para fluxos de trabalho onde os passos de pré-agente não devem ser filtrados — por exemplo, quando passos personalizados precisam de acesso à API não filtrado para fins de configuração.

Desabilitar o proxy afeta apenas chamadas CLI `gh` de pré-agente. O próprio agente sempre opera sob a política de guarda configurada via gateway MCP.

## Escolhendo um Nível

O nível correto depende de quem você quer que o agente veja o conteúdo:

- **Fluxos de trabalho que automatizam revisão de código ou aplicam alterações**: `merged` ou `approved` — aja apenas em conteúdo confiável.
- **Fluxos de trabalho que respondem a mantenedores e contribuidores confiáveis**: `approved` — um padrão comum e seguro para a maioria dos fluxos de trabalho.
- **Fluxos de trabalho de triagem ou planejamento da comunidade**: `unapproved` — permita a entrada de contribuidores enquanto exclui interações anônimas ou de primeira vez.
- **Fluxos de trabalho de dados públicos ou detecção de spam**: `none` — veja todas as atividades, mas garanta que as saídas do fluxo de trabalho não sejam aplicadas diretamente sem revisão.

> [!NOTE]
> Definir `min-integrity: none` em um repositório público desativa a proteção automática. Use apenas quando o fluxo de trabalho for projetado para lidar com entrada não confiável.

## Exemplos

**Permitir apenas conteúdo mesclado:**

```aw wrap
tools:
  github:
    allowed-repos: "all"
    min-integrity: merged
```

**Apenas contribuidores confiáveis (típico para um fluxo de trabalho de repositório público):**

```aw wrap
tools:
  github:
    min-integrity: approved
```

**Permitir todas as contribuições da comunidade (para um fluxo de trabalho de triagem):**

```aw wrap
tools:
  github:
    min-integrity: unapproved
```

**Desabilitar explicitamente a filtragem em um repositório público, além de usuários bloqueados:**

```aw wrap
tools:
  github:
    min-integrity: none
```

**Escopo para organizações específicas com filtragem de integridade:**

```aw wrap
tools:
  github:
    allowed-repos:
      - "myorg/*"
      - "partner/shared-repo"
    min-integrity: approved
```

**Bloquear usuários específicos enquanto permite todo o outro conteúdo:**

```aw wrap
tools:
  github:
    min-integrity: none
    blocked-users:
      - "known-spam-bot"
```

**Confiar em contribuidores externos específicos:**

```aw wrap
tools:
  github:
    min-integrity: approved
    trusted-users:
      - "contractor-1"
      - "partner-dev"
```

**Gate de revisão humana para contribuições externas:**

```aw wrap
tools:
  github:
    min-integrity: approved
    approval-labels:
      - "agent-approved"
      - "human-reviewed"
```

**Suprimir itens específicos do agente usando labels:**

```aw wrap
tools:
  github:
    min-integrity: approved
    refusal-labels:
      - "needs-security-review"
      - "do-not-automate"
```

**Endosso baseado em reação para acelerar contribuições (disponível a partir da v0.68.2):**

```aw wrap
features:
  integrity-reactions: true
tools:
  github:
    min-integrity: approved
```

**Listas gerenciadas centralmente via variáveis do GitHub:**

```aw wrap
tools:
  github:
    min-integrity: approved
    blocked-users: ${{ vars.BLOCKED_USERS }}
    trusted-users: ${{ vars.TRUSTED_USERS }}
    approval-labels: ${{ vars.APPROVAL_LABELS }}
    refusal-labels: ${{ vars.REFUSAL_LABELS }}
```

**Combinado: bloqueando, confiando, rotulando e recusando:**

```aw wrap
tools:
  github:
    allowed-repos: "all"
    min-integrity: approved
    blocked-users:
      - "known-spam-bot"
    trusted-users:
      - "contractor-1"
    approval-labels:
      - "agent-approved"
    refusal-labels:
      - "needs-security-review"
```

**Desabilitar o proxy de integridade de pré-agente:**

```aw wrap
tools:
  github:
    min-integrity: approved
    integrity-proxy: false
```

## Em Logs e Relatórios

Quando um item é filtrado pela verificação de integridade, o gateway MCP registra um evento `DIFC_FILTERED` no log `gateway.jsonl` da execução. Cada evento inclui:

- **Server**: o servidor MCP que retornou o conteúdo filtrado
- **Tool**: a chamada de ferramenta que a produziu (ex: `list_issues`, `get_pull_request`)
- **User**: o login do autor do conteúdo
- **Reason**: uma descrição como `"Resource has lower integrity than agent requires."`
- **Integrity tags**: as tags atribuídas ao item que causaram sua filtragem
- **Author association**: a associação do autor no GitHub (`CONTRIBUTOR`, `FIRST_TIMER` etc.)

Quando métricas de gateway são exibidas, os eventos filtrados aparecem em uma tabela de **Eventos Filtrados DIFC** ao lado da tabela de uso de servidor padrão:

```text
┌────────────────────────────────────────────────────────────────────────────────────┐
│ Eventos Filtrados DIFC                                                               │
├────────────────┬───────────────┬───────────────┬──────────────────────────────────-┤
│ Servidor         │ Ferramenta          │ Usuário          │ Razão                            │
├────────────────┼───────────────┼───────────────┼───────────────────────────────────┤
│ github         │ list_issues   │ new-user      │ Recurso tem integridade inferior  │
│                │               │               │ ao que o agente requer.           │
└────────────────┴───────────────┴───────────────┴───────────────────────────────────┘
```

A contagem `Total DIFC Filtered` na linha de resumo mostra quantos itens foram suprimidos durante a execução.

### Filtrando logs por eventos de integridade

Para baixar apenas execuções que tiveram conteúdo filtrado por integridade, use a flag `--filtered-integrity` com o comando `logs`:

```bash
gh aw logs --filtered-integrity
```

Isso é útil ao investigar se sua configuração de `min-integrity` está filtrando conteúdo esperado ou ao ajustar o nível após observar padrões de tráfego reais.

## Documentação Relacionada

- [Referência de Ferramentas GitHub](/gh-aw/reference/github-tools/) — Configuração completa de `tools.github`
- [Gateway MCP](/gh-aw/reference/mcp-gateway/) — Arquitetura de gateway e formato de log
- [Referência da CLI: logs](/gh-aw/setup/cli/#logs) — Baixando e analisando logs de execução de fluxo de trabalho
