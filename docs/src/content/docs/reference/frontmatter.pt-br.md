---
title: Frontmatter
description: Guia completo para todas as opções de configuração de frontmatter disponíveis para GitHub Agentic Workflows, incluindo triggers, permissões, motores de IA e configurações de fluxo de trabalho.
sidebar:
  order: 200
---

O [frontmatter](/gh-aw/reference/glossary/#frontmatter) (seção de configuração YAML entre marcadores `---`) do GitHub Agentic Workflows inclui os triggers, permissões, [motores](/gh-aw/reference/glossary/#engine) de IA (qual modelo/provedor de IA usar) e configurações de fluxo de trabalho. Por exemplo:

```yaml wrap
---
on:
  issues:
    types: [opened]

tools:
  edit:
  bash: ["gh issue comment"]
---
...markdown instructions...
```

## Elementos de Frontmatter

Abaixo está uma referência abrangente para todos os campos de frontmatter disponíveis para o GitHub Agentic Workflows.

### Eventos de Trigger (`on:`)

A seção `on:` usa a sintaxe padrão do GitHub Actions para definir triggers de fluxo de trabalho, com campos adicionais para controles de segurança e aprovação:

- Triggers padrão do GitHub Actions (push, pull_request, issues, schedule etc.)
- `reaction:` - Adiciona reações de emoji a itens de disparo
- `status-comment:` - Posta um comentário de iniciado/concluído com um link da execução do fluxo de trabalho (automaticamente habilitado para triggers `slash_command` e `label_command`; deve ser explicitamente definido como `true` para outros tipos de trigger). Aceita um booleano ou um objeto com campos opcionais `issues`, `pull-requests` e `discussions` para desativar seletivamente comentários de status para tipos de destino específicos.
- `stop-after:` - Desativa triggers automaticamente após um prazo
- `manual-approval:` - Exige aprovação manual usando regras de proteção de ambiente
- `forks:` - Configura filtragem de fork para triggers `pull_request`
- `skip-roles:` - Pula a execução do fluxo de trabalho para funções de repositório específicas
- `skip-bots:` - Pula a execução do fluxo de trabalho para atores específicos do GitHub
- `skip-author-associations:` - Pula a execução para combinações de evento + `author_association` configuradas
- `skip-if-match:` - Pula a execução quando uma consulta de busca tiver correspondências (suporta `scope: none`; use `on.github-token` / `on.github-app` de nível superior para auth personalizada)
- `skip-if-no-match:` - Pula a execução quando uma consulta de busca não tiver correspondências (suporta `scope: none`; use `on.github-token` / `on.github-app` de nível superior para auth personalizada)
- `steps:` - Injeta passos determinísticos personalizados no job de pré-ativação (economiza um job de fluxo de trabalho vs. padrão multi-job)
- `permissions:` - Concede escopos adicionais de token do GitHub ao job de pré-ativação (para uso com chamadas de API `on.steps:`)
- `needs:` - Adiciona dependências de job personalizadas que tanto `pre_activation` quanto `activation` devem aguardar
- `github-token:` - Token personalizado para reações do job de ativação, comentários de status de ativação e consultas de busca skip-if
- `github-app:` - GitHub App para emitir um token de curta duração usado pelo job de ativação e todos os passos de busca skip-if

Veja [Eventos de Trigger](/gh-aw/reference/triggers/) para documentação completa.

### Descrição (`description:`)

Fornece uma descrição legível por humanos do fluxo de trabalho renderizada como um comentário no arquivo de bloqueio gerado.

```yaml wrap
description: "Fluxo de trabalho que analisa pull requests e fornece feedback"
```

### Emoji (`emoji:`)

Um emoji opcional para representar o fluxo de trabalho visualmente, por exemplo, em listagens e superfícies de interface.

```yaml wrap
emoji: "🤖"
```

### Rastreamento de Origem (`source:`)

Rastreia a origem do fluxo de trabalho no formato `owner/repo/path@ref`. Preenchido automaticamente ao usar `gh aw add` para instalar fluxos de trabalho de repositórios externos. Opcional para fluxos de trabalho criados manualmente.

```yaml wrap
source: "githubnext/agentics/workflows/ci-doctor.md@v1.0.0"
```

### Redirecionamento (`redirect:`)

Especifica uma nova localização canônica quando um fluxo de trabalho foi movido ou renomeado. `gh aw add`, `gh aw add-wizard` e `gh aw update` seguem cadeias de redirecionamento até a localização resolvida para fluxos de trabalho remotos. Durante fluxos de add/update, o campo `source` local é escrito (ou reescrito) para a localização resolvida, e loops de redirecionamento são detectados e relatados como erros.

```yaml wrap
redirect: "githubnext/agentics/workflows/new-workflow-name.md@main"
```

Use `gh aw update --no-redirect` para recusar atualizações quando o fluxo de trabalho de origem tiver um campo `redirect` — a atualização falha em vez de seguir o redirecionamento. Isso é útil para auditoria ou quando você deseja controlar explicitamente quando os redirecionamentos são seguidos.

`gh aw compile` emite uma mensagem informativa quando um fluxo de trabalho tem um campo `redirect` configurado, portanto, o redirecionamento é visível durante o desenvolvimento local.

O campo `redirect` usa o mesmo formato `owner/repo/path@ref` que `source:`. Cadeias de redirecionamento são seguidas transitivamente (até um limite de profundidade).

> [!NOTE]
> O campo `redirect` é definido pelos *autores* do fluxo de trabalho para sinalizar que um fluxo de trabalho foi movido. Normalmente não é definido por usuários finais. Se você vir um redirecionamento ao executar `gh aw update`, significa que o fluxo de trabalho upstream foi realocado.

### Fluxos de Trabalho Privados (`private:`)

Marque um fluxo de trabalho como privado para impedir que ele seja instalado em outros repositórios via `gh aw add`.

```yaml wrap
private: true
```

Quando `private: true` está definido, a tentativa de adicionar o fluxo de trabalho de outro repositório falhará com um erro:

```
workflow 'owner/repo/internal-tooling' é privado e não pode ser adicionado a outros repositórios
```

Use este campo para ferramentas internas, automação sensível ou fluxos de trabalho que dependem de contexto específico do repositório e não se destinam à reutilização externa.

> [!NOTE]
> O campo `private:` apenas bloqueia a instalação via `gh aw add`. Ele não afeta a visibilidade do próprio arquivo de fluxo de trabalho — isso é controlado pelas configurações de acesso do seu repositório.

### Recursos (`resources:`)

Declara arquivos adicionais de fluxo de trabalho ou ação para buscar juntamente com este fluxo de trabalho ao executar `gh aw add`. Use este campo quando o fluxo de trabalho depender de fluxos de trabalho complementares ou ações personalizadas armazenadas no mesmo diretório.

```yaml wrap
resources:
  - triage-issue.md          # fluxo de trabalho complementar
  - label-issue.md           # fluxo de trabalho complementar
  - shared/helper-action.yml # GitHub Action de suporte
```

As entradas são caminhos relativos da localização do fluxo de trabalho no repositório de origem. A sintaxe de expressão do GitHub Actions (`${{`) não é permitida em caminhos de recurso.

Quando um usuário executa `gh aw add` para instalar este fluxo de trabalho, cada arquivo listado também é baixado e colocado ao lado do fluxo de trabalho principal no repositório de destino. Isso garante que fluxos de trabalho complementares e ações personalizadas das quais o fluxo de trabalho principal depende estejam disponíveis após a instalação.

Além dos arquivos listados explicitamente em `resources:`, `gh aw add` busca automaticamente fluxos de trabalho referenciados no safe output [`dispatch-workflow`](/gh-aw/reference/safe-outputs/#workflow-dispatch-dispatch-workflow).

### Labels (`labels:`)

Array opcional de strings para categorizar e organizar fluxos de trabalho. Labels são exibidas na saída do comando `gh aw status` e podem ser filtradas usando a flag `--label`.

```yaml wrap
labels: ["automation", "ci", "diagnostics"]
```

Labels ajudam a organizar fluxos de trabalho por objetivo, equipe ou funcionalidade. Elas aparecem na saída da tabela do comando status como `[automation ci diagnostics]` e como um array JSON no modo `--json`. Filtre fluxos de trabalho por label usando `gh aw status --label automation`.

### Metadados (`metadata:`)

Pares chave-valor opcionais para armazenar metadados personalizados compatíveis com a [especificação de agente personalizado do GitHub Copilot](https://docs.github.com/en/copilot/reference/custom-agents-configuration).

```yaml wrap
metadata:
  author: John Doe
  version: 1.0.0
  category: automation
```

**Restrições:**

- Chaves: 1-64 caracteres
- Valores: Máximo 1024 caracteres
- Apenas valores de string são suportados

Metadados fornecem uma maneira flexível de adicionar informações descritivas a fluxos de trabalho sem afetar a execução.

### Dependências APM (importação `shared/apm.md`)

Importe `shared/apm.md` para instalar pacotes do [APM (Agent Package Manager)](https://microsoft.github.io/apm/) antes da execução do fluxo de trabalho. O APM gerencia primitivas de agente de IA, como habilidades, prompts, instruções, agentes, hooks e plugins (incluindo o formato `plugin.json` do Claude).

```aw wrap
imports:
  - uses: shared/apm.md
    with:
      packages:
        - microsoft/apm-sample-package
        - github/awesome-copilot/skills/review-and-refactor
        - microsoft/apm-sample-package#v2.0   # fixado por versão
```

Veja **[Referência de Dependências APM](/gh-aw/reference/dependencies/)** para a especificação completa do formato, sintaxe de fixação de versão, formatos de referência de pacote, detalhes de reprodutibilidade e governança e instruções de depuração local.

### Runtimes (`runtimes:`)

Substitua versões de runtime padrão para linguagens e ferramentas usadas em fluxos de trabalho. O compilador detecta automaticamente os requisitos de runtime a partir de configurações de ferramenta e passos de fluxo de trabalho, então instala as versões especificadas.

**Formato**: Objeto com nome do runtime como chave e configuração como valor

**Campos por runtime**:

- `version`: String de versão do runtime (obrigatório)
- `action-repo`: Action de setup personalizada do GitHub Actions (opcional, substitui o padrão)
- `action-version`: Versão da action de setup (opcional, substitui o padrão)

**Runtimes suportados**:

| Runtime | Versão Padrão | Action de Setup Padrão |
|---------|----------------|---------------------|
| `node` | 24 | `actions/setup-node@v6` |
| `python` | 3.12 | `actions/setup-python@v5` |
| `go` | 1.25 | `actions/setup-go@v5` |
| `uv` | latest | `astral-sh/setup-uv@v5` |
| `bun` | 1.1 | `oven-sh/setup-bun@v2` |
| `deno` | 2.x | `denoland/setup-deno@v2` |
| `ruby` | 3.3 | `ruby/setup-ruby@v1` |
| `java` | 21 | `actions/setup-java@v4` |
| `dotnet` | 8.0 | `actions/setup-dotnet@v4` |
| `elixir` | 1.17 | `erlef/setup-beam@v1` |
| `haskell` | 9.10 | `haskell-actions/setup@v2` |

**Exemplos**:

Substituir versão do Node.js:

```yaml wrap
runtimes:
  node:
    version: "22"
```

Usar versão específica do Python com action de setup personalizada:

```yaml wrap
runtimes:
  python:
    version: "3.12"
    action-repo: "actions/setup-python"
    action-version: "v5"
```

Substituições de múltiplos runtimes:

```yaml wrap
runtimes:
  node:
    version: "20"
  python:
    version: "3.11"
  go:
    version: "1.22"
```

**Comportamento Padrão**: Se não especificado, os fluxos de trabalho usam as versões de runtime padrão definidas no sistema. O compilador detecta automaticamente quais runtimes são necessários com base nas configurações de ferramenta (ex: `bash: ["node"]`, `bash: ["python"]`) e passos do fluxo de trabalho.

**Casos de Uso**:

- Fixar versões de runtime específicas para reprodutibilidade
- Usar versões de runtime preview/beta para testes
- Usar actions de setup personalizadas (forks, espelhos corporativos)
- Substituir padrões do sistema para requisitos de compatibilidade

**Nota**: Runtimes de fluxos de trabalho compartilhados importados são automaticamente mesclados com a configuração de runtime do seu fluxo de trabalho.

### Permissões (`permissions:`)

A seção `permissions:` usa uma sintaxe semelhante à sintaxe de permissões padrão do GitHub Actions para especificar as permissões de leitura do GitHub relevantes para a parte agentic (linguagem natural) da execução do fluxo de trabalho. Veja [Permissões de Leitura de Ferramentas GitHub](/gh-aw/reference/permissions/).

### Funções de Acesso ao Repositório (`on.roles:`)

Controla quem pode acionar fluxos de trabalho agentic com base no nível de permissão do repositório. Padrão para `[admin, maintainer, write]`.

```yaml wrap
on:
  issues:
    types: [opened]
  roles: [admin, maintainer, write]  # Padrão
```

```yaml wrap
on:
  workflow_dispatch:
  roles: all                         # Permitir qualquer usuário (⚠️ use com cautela)
```

Você também pode usar uma string de função única, por exemplo `roles: write`.

Funções disponíveis: `admin`, `maintainer`/`maintain`, `write`, `triage`, `read`, `all`. Fluxos de trabalho com triggers inseguros (`push`, `issues`, `pull_request`) aplicam automaticamente verificações de permissão. Verificações com falha cancelam o fluxo de trabalho com um aviso.

> [!TIP]
> Execute `gh aw fix workflow.md --write` para migrar automaticamente `roles:` de nível superior para `on.roles:` usando o codemod embutido.

### Filtragem de Bot (`on.bots:`)

Configure quais contas de bot do GitHub podem acionar fluxos de trabalho. Útil para permitir automações específicas enquanto mantém controles de segurança.

```yaml wrap
on:
  issues:
    types: [opened]
  bots:
    - "dependabot[bot]"
    - "renovate[bot]"
    - "agentic-workflows-dev[bot]"
```

**Comportamento**:

- Quando especificado, apenas as contas de bot listadas podem acionar o fluxo de trabalho
- O bot deve estar ativo (instalado) no repositório para acionar o fluxo de trabalho
- Combine com `on.roles:` para controle de acesso abrangente
- Aplica-se a todos os triggers de fluxo de trabalho (`pull_request`, `issues` etc.)
- Quando `on.roles: all` é definido, a filtragem de bot não é aplicada

**Nomes de bot comuns**:

- `dependabot[bot]` - Dependabot do GitHub para atualizações de dependência
- `renovate[bot]` - Bot Renovate para gerenciamento automatizado de dependência
- `github-actions[bot]` - Bot do GitHub Actions
- `agentic-workflows-dev[bot]` - Bot de desenvolvimento para testar fluxos de trabalho

> [!TIP]
> Execute `gh aw fix workflow.md --write` para migrar automaticamente `bots:` de nível superior para `on.bots:` usando o codemod embutido.

### Pular Funções (`on.skip-roles`)

Pula a execução do fluxo de trabalho para usuários com níveis de permissão de repositório específicos. Útil para isentar membros da equipe de verificações automatizadas que devem se aplicar apenas a colaboradores externos.

```yaml wrap
on:
  issues:
    types: [opened]
  skip-roles: [admin, maintainer, write]
```

**Funções disponíveis**: `admin`, `maintainer`/`maintain`, `write`, `triage`, `read`

**Comportamento**:

- O fluxo de trabalho é cancelado durante a pré-ativação quando acionado por usuários com funções listadas
- A verificação ocorre antes da execução do agente para evitar custos computacionais desnecessários
- Mesclado como união ao importar fluxos de trabalho (todas as skip-roles de fluxos de trabalho importados são combinadas)
- Útil para fluxos de trabalho de moderação de IA que devem verificar apenas o conteúdo de usuários externos

**Exemplo de caso de uso**: Um fluxo de trabalho de moderação de conteúdo de IA que verifica issues por violações de política, mas isenta membros da equipe de confiança com acesso de escrita ou superior.

### Pular Bots (`on.skip-bots`)

Pula a execução do fluxo de trabalho quando acionado por atores específicos do GitHub (usuários ou bots). Complementa `skip-roles` filtrando com base na identidade do ator em vez do nível de permissão.

```yaml wrap
on:
  issues:
    types: [opened]
  skip-bots: [github-actions, copilot, dependabot]
```

**Correspondência de nome de bot**: A correspondência flexível automática lida com nomes de bot com ou sem o sufixo `[bot]`. Por exemplo, especificar `github-actions` corresponde automaticamente a ambos os atores `github-actions` e `github-actions[bot]`.

**Comportamento**:

- O fluxo de trabalho é cancelado durante a pré-ativação quando `github.actor` corresponde a qualquer ator listado
- A verificação ocorre antes da execução do agente para evitar custos computacionais desnecessários
- Mesclado como união ao importar fluxos de trabalho (todas as skip-bots de fluxos de trabalho importados são combinadas)
- Aceita tanto contas de usuário quanto contas de bot

**Formato de string ou array**:

```yaml wrap
# Bot único
skip-bots: github-actions

# Múltiplos bots
skip-bots: [github-actions, copilot, renovate]
```

**Exemplos de casos de uso**:

- Pular fluxos de trabalho de IA quando acionados por bots de automação para evitar interações bot-a-bot
- Prevenir loops de fluxo de trabalho onde a saída de um fluxo de trabalho aciona outro
- Isentar bots específicos conhecidos de verificações de conteúdo ou aplicação de políticas

### Pular Associações de Autor (`on.skip-author-associations`)

Pula a execução do fluxo de trabalho no nível do job de pré-ativação quando um evento específico é acionado por um autor com um campo de payload de evento `author_association` correspondente (por exemplo `github.event.comment.author_association`, `github.event.issue.author_association` ou `github.event.pull_request.author_association`).

```yaml wrap
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  skip-author-associations:
    issue_comment: contributor
    pull_request_review_comment: [first_time_contributor, none]
```

**Comportamento**:

- Compila para uma expressão `if` de nível de job (sem custo de passo de script de pré-ativação para skips correspondentes)
- Usa o campo de payload específico do evento (`github.event.comment.author_association`, `github.event.issue.author_association` ou `github.event.pull_request.author_association`)
- Valores não diferenciam maiúsculas de minúsculas no frontmatter (`contributor` e `CONTRIBUTOR` são tratados da mesma forma)
- Suporta uma string única ou um array de strings por chave de evento

### Modo Estrito (`strict:`)

Habilita validação de segurança aprimorada para fluxos de trabalho de produção. **Habilitado por padrão**.

```yaml wrap
strict: true   # Habilitar (padrão)
strict: false  # Desabilitar para desenvolvimento/testes
```

**Áreas de aplicação:**

1. Recusa permissões de escrita (`contents:write`, `issues:write`, `pull-requests:write`) - use [safe-outputs](/gh-aw/reference/safe-outputs/) em vez disso
2. Exige [configuração de rede](/gh-aw/reference/network/) explícita
3. Recusa curinga `*` em domínios `network.allowed`
4. Exige identificadores de ecossistema (ex: `python`, `node`) em vez de domínios de ecossistema individuais (ex: `pypi.org`, `npmjs.org`) para todos os motores
5. Exige configuração de rede para servidores MCP personalizados com containers
6. Exige GitHub Actions fixadas em SHAs de commit
7. Recusa campos de frontmatter obsoletos

Quando o modo estrito rejeita domínios de ecossistema individuais, mensagens de erro úteis sugerem o identificador de ecossistema apropriado (ex: "Você quis dizer: 'pypi.org' pertence ao ecossistema 'python'?").

**Configuração:**

- **Frontmatter**: `strict: true/false` (por fluxo de trabalho)
- **Flag da CLI**: `gh aw compile --strict` (todos os fluxos de trabalho, substitui o frontmatter)

> [!IMPORTANT]
> Fluxos de trabalho compilados com `strict: false` não podem ser executados em repositórios públicos. O fluxo de trabalho falha em runtime com uma mensagem de erro solicitando a recompilação com modo estrito.

Veja [Permissões de Rede - Validação de Modo Estrito](/gh-aw/reference/network/#strict-mode-validation) para detalhes sobre validação de rede e [Comandos da CLI](/gh-aw/setup/cli/#compile) para opções de compilação.

### Feature Flags (`features:`)

Habilita funcionalidades experimentais ou opcionais como pares chave-valor.

```yaml wrap
features:
  my-experimental-feature: true
  action-mode: "script"
```

#### Action Mode (`features.action-mode`)

Controla como o compilador de fluxo de trabalho gera referências de ação personalizadas em fluxos de trabalho compilados. Pode ser definido como `"dev"`, `"release"`, `"action"` ou `"script"`.

```yaml wrap
features:
  action-mode: "script"
```

**Modos disponíveis:**

- **`dev`** (padrão): Faz referência a ações personalizadas usando caminhos locais (ex: `uses: ./actions/setup`). Melhor para fluxos de trabalho de desenvolvimento e teste no repositório gh-aw.

- **`release`**: Faz referência a ações personalizadas usando caminhos remotos fixados por SHA dentro de `github/gh-aw` (ex: `uses: github/gh-aw/actions/setup@sha`). Usado para fluxos de trabalho de produção com fixação de versão.

- **`action`**: Faz referência a ações personalizadas do repositório externo `github/gh-aw-actions` na mesma versão de release (ex: `uses: github/gh-aw-actions/setup@sha`). Usa fixação SHA quando disponível, com fallback para tag de versão. Use isso ao implantar fluxos de trabalho a partir do repositório de distribuição `github/gh-aw-actions`.

- **`script`**: Gera chamadas de script shell diretas em vez de usar a sintaxe `uses:` do GitHub Actions. O compilador:
  1. Faz o checkout do repositório `github/gh-aw` pasta `actions` para `/tmp/gh-aw/actions-source`
  2. Executa o script de setup diretamente: `bash /tmp/gh-aw/actions-source/actions/setup/setup.sh`
  3. Usa clone raso (`depth: 1`) para eficiência

**Quando usar o modo script:**

- Testar scripts de action personalizados durante o desenvolvimento
- Depurar problemas de instalação de action
- Ambientes onde referências de action local não estão disponíveis
- Cenários de depuração avançados que exigem execução de script direta

**Exemplo:**

```yaml wrap
---
name: Debug Workflow
on: workflow_dispatch
features:
  action-mode: "script"
permissions:
  contents: read
---

Fluxo de trabalho de depuração usando o modo script para ações personalizadas.
```

**Nota:** O `action-mode` também pode ser substituído pela flag da CLI `--action-mode` ou pela variável de ambiente `GH_AW_ACTION_MODE`. A precedência é: Flag da CLI > flag de feature > variável de ambiente > detecção automática.

#### Copilot BYOK Mode (Padrão para `engine: copilot`)

O comportamento BYOK (Bring Your Own Key) offline do Copilot agora é o padrão para `engine: copilot`, agrupando quatro comportamentos:

1. Injeção de um `COPILOT_API_KEY` fictício para acionar o caminho de runtime AWF BYOK.
2. Habilitação implícita de `cli-proxy`.
3. Forçar a CLI do Copilot a instalar na versão `latest` (ignorando qualquer `engine.version` fixada).
4. Configuração de `COPILOT_MODEL` para `${{ vars.GH_AW_MODEL_AGENT_COPILOT || 'claude-sonnet-4.6' }}` — provedores BYOK do Copilot exigem um modelo não vazio, então o compilador fornece `claude-sonnet-4.6` como fallback quando `GH_AW_MODEL_AGENT_COPILOT` não está definido.

Nenhuma feature flag é necessária.

Para usar um modelo diferente, defina a variável de repositório `GH_AW_MODEL_AGENT_COPILOT`. O fluxo de trabalho compilado usa `${{ vars.GH_AW_MODEL_AGENT_COPILOT || 'claude-sonnet-4.6' }}` para `COPILOT_MODEL`.

> [!IMPORTANT]
> `features.byok-copilot` está obsoleto e não é mais necessário. Fluxos de trabalho existentes ainda podem incluí-lo, mas não tem efeito.
>
> Para detalhes sobre configuração e política do Copilot BYOK, veja [Using your LLM provider API keys with Copilot](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-enterprise/use-your-own-api-keys).
 
> [!NOTE]
> Os padrões Copilot BYOK aplicam-se apenas a fluxos de trabalho `engine: copilot`. Outros motores permanecem inalterados.

#### Diagnósticos de Falha AWF (`features.awf-diagnostic-logs`)

Habilita a coleta de diagnósticos operacionais do Docker AWF em caso de falha adicionando `--diagnostic-logs` aos argumentos de runtime do AWF.

Quando habilitado, o AWF inclui diagnósticos de falha sob o subdiretório `diagnostics/` no artefato `firewall-audit-logs` (por exemplo, logs de container, códigos de saída, metadados de montagem e configuração compose sanitizada).

```yaml wrap
features:
  awf-diagnostic-logs: true
```

#### Sinais de Confiança baseados em Reação (`features.integrity-reactions`)

Permite que mantenedores promovam ou rebaixem conteúdo passando pelo filtro de integridade usando reações do GitHub (👍, ❤️, 👎, 😕), sem adicionar labels ou modificar o estado da issue. Disponível a partir do gh-aw v0.68.2.

```yaml wrap
features:
  integrity-reactions: true
```

Quando definido, o compilador habilita automaticamente o proxy da CLI (necessário para identificar autores de reação) e injeta a configuração padrão de reação de endosso e reprovação. Apenas a flag `features.integrity-reactions` é necessária — os campos de reação sob `tools.github` (`endorsement-reactions`, `disapproval-reactions`, `endorser-min-integrity`, `disapproval-integrity`) são substituições opcionais.

Veja [Promovendo e rebaixando itens via reações](/gh-aw/reference/integrity/#promoting-and-demoting-items-via-reactions) na Referência de Filtragem de Integridade para detalhes completos de configuração.

#### Proxy DIFC (`tools.github.integrity-proxy`)

Controla a injeção de proxy DIFC (Data Integrity and Flow Control). Quando `tools.github.min-integrity` é configurado, o compilador insere passos de proxy ao redor do agente que aplicam isolamento de nível de integridade no limite da rede. O proxy é **habilitado por padrão** — defina `integrity-proxy: false` para optar por não participar.

```yaml wrap
tools:
  github:
    min-integrity: approved
    # integrity-proxy: false  # descomente para desativar a injeção de proxy
```

Sem `min-integrity`, `integrity-proxy` não tem efeito. Quando ambos estão configurados, o proxy aplica a filtragem de integridade de limite de rede além da filtragem de nível de gateway MCP. Defina `integrity-proxy: false` quando você precisar apenas de filtragem de nível de gateway.

:::note[Migração]
A flag obsoleta `features.difc-proxy: true` é substituída por este campo. Execute `gh aw fix` para migrar automaticamente fluxos de trabalho existentes.
:::

### Motor de IA (`engine:`)

Especifica qual motor de IA interpreta a seção markdown. Veja [Motores de IA](/gh-aw/reference/engines/) para detalhes.

```yaml wrap
engine: copilot
```

### Orçamento de Effective Token (`max-effective-tokens:`)

Define o orçamento de effective-token do AWF usado para aplicação de custos. O padrão é `25000000` quando omitido. O direcionamento de token (mensagens de aviso de orçamento a 80%, 90%, 95% e 99% do orçamento) é habilitado por padrão. Defina como um valor negativo para desativar tanto a aplicação de orçamento quanto o direcionamento de token.

```yaml wrap
max-effective-tokens: 5000000
```

```yaml wrap
# Desativar aplicação de orçamento e direcionamento de token
max-effective-tokens: -1
```

### Inline Sub-Agents (`inline-sub-agents:`)

Opção de compatibilidade obsoleta para suporte a sub-agentes inline. Sub-agentes inline são habilitados por padrão, e `inline-sub-agents: false` é recusado no momento da compilação. Veja [Sub-Agentes Inline](/gh-aw/reference/inline-sub-agents/) para sintaxe e uso.

```yaml wrap
inline-sub-agents: true
```

### Permissões de Rede (`network:`)

Controla o acesso à rede usando identificadores de ecossistema e listas de permissão de domínio. Veja [Permissões de Rede](/gh-aw/reference/network/) para documentação completa.

```yaml wrap
network:
  allowed:
    - defaults              # Infraestrutura básica
    - python               # Ecossistema Python/PyPI
    - "api.example.com"    # Domínio personalizado
```

### Scripts MCP (`mcp-scripts:`)

Permite definir ferramentas MCP personalizadas inline usando JavaScript ou scripts shell. Veja [Scripts MCP](/gh-aw/reference/mcp-scripts/) para documentação completa sobre a criação de ferramentas personalizadas com acesso controlado a segredos.

### Safe Outputs (`safe-outputs:`)

Habilita a criação automática de issue, postagem de comentário e outros safe outputs. Veja [Processamento de Safe Outputs](/gh-aw/reference/safe-outputs/).

### Configuração de Execução (`run-name:`, `runs-on:`, `runs-on-slim:`, `timeout-minutes:`)

Propriedades padrão do GitHub Actions:

```yaml wrap
run-name: "Nome de execução de fluxo de trabalho personalizado"  # Padrão para nome do fluxo de trabalho
runs-on: ubuntu-latest               # Padrão para ubuntu-latest (job principal)
runs-on-slim: ubuntu-slim            # Padrão para ubuntu-slim (jobs de framework)
timeout-minutes: 30                  # Padrão para 20 minutos
```

`runs-on` aplica-se apenas ao job do agente principal. `runs-on-slim` aplica-se a todos os jobs de framework/gerados (ativação, safe-outputs, desbloqueio etc.) e o padrão é `ubuntu-slim`. `safe-outputs.runs-on` tem precedência sobre `runs-on-slim` para jobs de safe-output especificamente.

`timeout-minutes` aceita um inteiro ou uma string de expressão do GitHub Actions. Isso permite que fluxos de trabalho reutilizáveis `workflow_call` parametrizem o timeout via entradas do chamador:

```yaml wrap
# Inteiro literal
timeout-minutes: 30

# Expressão — útil em fluxos de trabalho reutilizáveis (workflow_call)
timeout-minutes: ${{ inputs.timeout }}
```

**Runners suportados para `runs-on:`**

| Runner | Status |
|--------|--------|
| `ubuntu-latest` | ✅ Padrão. Recomendado para a maioria dos fluxos de trabalho. |
| `ubuntu-24.04` / `ubuntu-22.04` | ✅ Suportado. |
| `ubuntu-24.04-arm` | ✅ Suportado. Runner Linux ARM64. |
| `macos-*` | ❌ Não suportado. Docker não está disponível em runners macOS (sem virtualização aninhada). Veja [FAQ](/gh-aw/reference/faq/). |
| `windows-*` | ❌ Não suportado. AWF requer Linux. |

### Controle de Simultaneidade do Fluxo de Trabalho (`concurrency:`)

Gera automaticamente políticas de simultaneidade para o job do agente. Veja [Controle de Simultaneidade](/gh-aw/reference/concurrency/).

## Variáveis de Ambiente (`env:`)

Sintaxe padrão do GitHub Actions `env:` para variáveis de ambiente em nível de fluxo de trabalho:

```yaml wrap
env:
  CUSTOM_VAR: "value"
```

Variáveis de ambiente podem ser definidas em múltiplos escopos (fluxo de trabalho, job, passo, motor, safe-outputs etc.) com regras de precedência claras. Veja [Variáveis de Ambiente](/gh-aw/reference/environment-variables/) para documentação completa sobre todos os 13 escopos de env e ordem de precedência.

> [!WARNING]
> Não use expressões `${{ secrets.* }}` na seção `env:` em nível de fluxo de trabalho. Variáveis de ambiente definidas aqui são passadas diretamente para o container do agente, o que significa que valores de segredo estariam visíveis para o modelo de IA. No modo estrito, este é um erro de compilação. No modo não estrito, ele emite um aviso.
>
> Use configuração de segredo específica do motor em vez da seção `env:` para passar segredos com segurança.

## Segredos (`secrets:`)

Define valores de segredo passados para a execução do fluxo de trabalho. Segredos são normalmente usados para fornecer configuração sensível a servidores MCP ou componentes de fluxo de trabalho. Os valores devem ser expressões do GitHub Actions que fazem referência a segredos (ex: `${{ secrets.API_KEY }}`).

```yaml wrap
secrets:
  API_TOKEN: ${{ secrets.API_TOKEN }}
  DATABASE_URL: ${{ secrets.DB_URL }}
```

Segredos também podem incluir descrições para documentação:

```yaml wrap
secrets:
  API_TOKEN:
    value: ${{ secrets.API_TOKEN }}
    description: "API token for external service"
  DATABASE_URL:
    value: ${{ secrets.DB_URL }}
    description: "Production database connection string"
```

**Melhores práticas de segurança:**

- Use sempre expressões de segredo do GitHub Actions (`${{ secrets.NAME }}`)
- Nunca comite segredos em texto simples em arquivos de fluxo de trabalho
- Use segredos específicos do ambiente quando possível (via campo `environment:`)
- Limite o acesso ao segredo apenas aos componentes que precisam dele

**Nota:** Para passar segredos para fluxos de trabalho reutilizáveis, use o campo `jobs.<job_id>.secrets` em vez disso. O campo `secrets:` de nível superior é para configuração de segredo em nível de fluxo de trabalho.

## Proteção de Ambiente (`environment:`)

Especifica o ambiente para regras de proteção de implantação e segredos específicos do ambiente. Sintaxe padrão do GitHub Actions.

```yaml wrap
environment: production
```

Veja [documentação de ambiente do GitHub Actions](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment).

## Configuração de Container (`container:`)

Especifica um container para executar os passos do job.

```yaml wrap
container: node:18
```

Veja [documentação de container do GitHub Actions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/run-jobs-in-a-container).

## Containers de Serviço (`services:`)

Define containers de serviço que são executados juntamente com seu job (bancos de dados, caches etc.).

```yaml wrap
services:
  postgres:
    image: postgres:13
    env:
      POSTGRES_PASSWORD: postgres
    ports:
      - 5432:5432
```

> [!NOTE]
> O agente AWF é executado dentro de um container Docker isolado. Containers de serviço expõem portas no runner host, não dentro do namespace de rede do agente. Para conectar a um serviço a partir do agente, use `host.docker.internal` como o nome do host em vez de `localhost`. Por exemplo, um serviço Postgres configurado com a porta `5432:5432` é acessível em `host.docker.internal:5432`.

Veja [documentação de serviço do GitHub Actions](https://docs.github.com/en/actions/using-containerized-services).

## Execução Condicional (`if:`)

Sintaxe padrão do GitHub Actions `if:`:

```yaml wrap
if: github.event_name == 'push'
```

## Checkout de Repositório (`checkout:`)

Configura como `actions/checkout` é invocado no job do agente. Substitua as configurações de checkout padrão ou faça checkout de múltiplos repositórios para fluxos de trabalho entre repositórios.

Defina `checkout: false` para desativar o checkout de repositório padrão completamente — útil para fluxos de trabalho que acessam repositórios por meio de servidores MCP ou outros mecanismos que não requerem um clone local:

```yaml wrap
checkout: false
```

Veja [Operações Entre Repositórios](/gh-aw/reference/cross-repository/) para documentação completa sobre opções de configuração de checkout (incluindo `fetch:`, `checkout: false`), comportamento de mesclagem e exemplos entre repositórios.

## Passos Personalizados (`steps:`)

Adiciona passos personalizados antes da execução agentic. Se não especificado, um passo de checkout padrão é adicionado automaticamente.

```yaml wrap
steps:
  - name: Instalar dependências
    run: npm ci
```

Use passos personalizados para pré-computar dados, filtrar triggers ou preparar contexto para agentes de IA. Veja [DeterministicOps](/gh-aw/patterns/deterministic-ops/) para combinar computação com raciocínio de IA.

Passos personalizados são executados fora do sandbox de firewall. Esses passos são executados com a segurança padrão do GitHub Actions.

## Passos Pré-Agente (`pre-agent-steps:`)

Adiciona passos personalizados antes da inicialização do gateway MCP no job do agente para que a instalação/configuração do MCP de pré-requisito possa acontecer primeiro.

```yaml wrap
pre-agent-steps:
  - name: Finalizar Contexto
    run: ./scripts/prepare-agent-context.sh
```

Use passos pré-agente quando o trabalho precisar acontecer logo antes da execução do motor (por exemplo, preparação final de contexto ou validações de último momento).

Passos pré-agente são executados fora do sandbox de firewall. Esses passos são executados com a segurança padrão do GitHub Actions.

## Passos Pós-Execução (`post-steps:`)

Adiciona passos personalizados após a execução agentic. Executado após a conclusão do motor de IA, independentemente de sucesso/falha (a menos que expressões condicionais sejam usadas).

```yaml wrap
post-steps:
  - name: Fazer Upload dos Resultados
    if: always()
    uses: actions/upload-artifact@v4
    with:
      name: workflow-results
      path: /tmp/gh-aw/
      retention-days: 7
```

Útil para uploads de artefato, resumos, limpeza ou disparo de fluxos de trabalho a jusante.

Passos pós-execução são executados FORA do sandbox de firewall. Esses passos são executados com a segurança padrão do GitHub Actions.

## Jobs Personalizados (`jobs:`)

Define jobs personalizados que são executados antes da execução agentic.

```yaml wrap
jobs:
  super_linter:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - name: Run Super-Linter
        uses: super-linter/super-linter@v7
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

A execução agentic aguarda a conclusão de todos os jobs personalizados. Jobs personalizados podem compartilhar dados por meio de artefatos ou saídas de job. Veja [DeterministicOps](/gh-aw/patterns/deterministic-ops/) para fluxos de trabalho de múltiplos jobs.

Jobs personalizados são executados fora do sandbox de firewall. Esses jobs são executados com a segurança padrão do GitHub Actions.

### Campos Suportados em Nível de Job

Os seguintes campos de nível de job são suportados em jobs personalizados:

| Campo | Descrição |
|---|---|
| `name` | Nome de exibição para o job |
| `needs` | Jobs que devem ser concluídos antes que este job seja executado |
| `runs-on` | Label do runner — formato string, array ou objeto |
| `if` | Expressão condicional para controlar a execução do job |
| `permissions` | Permissões de token do GitHub para este job |
| `outputs` | Valores expostos a jobs a jusante |
| `env` | Variáveis de ambiente disponíveis para todos os passos |
| `timeout-minutes` | Duração máxima do job (padrão do GitHub Actions: 360) |
| `concurrency` | Grupo de simultaneidade para evitar execuções paralelas |
| `continue-on-error` | Permitir que o fluxo de trabalho continue se este job falhar |
| `container` | Container Docker para executar passos |
| `services` | Containers de serviço (ex: bancos de dados) |
| `pre-steps` | Passos injetados após passos de setup do compilador e antes do checkout/`steps` naquele job |
| `steps` | Lista de passos — suporta especificação completa de passo do GitHub Actions |
| `uses` | Fluxo de trabalho reutilizável para chamar |
| `with` | Parâmetros de entrada para um fluxo de trabalho reutilizável |
| `secrets` | Segredos passados para um fluxo de trabalho reutilizável |

O campo `strategy` (builds de matriz) não é suportado.

`runs-on` aceita uma string, um array de labels de runner ou o formato de objeto:

```yaml wrap
jobs:
  build:
    runs-on:
      group: my-runner-group
      labels: [self-hosted, linux]
    steps:
      - uses: actions/checkout@v6
```

Quando `jobs.<job-id>.pre-steps` é definido, a ordem de execução dos passos é determinística:

1. Passos de setup injetados pelo compilador
2. `jobs.<job-id>.pre-steps`
3. Passos de checkout
4. Passos `jobs.<job-id>.steps` restantes

O exemplo a seguir usa `timeout-minutes` e `env`:

```yaml wrap
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    env:
      NODE_ENV: production
    steps:
      - uses: actions/checkout@v6
      - run: npm ci && npm run build
```

### Saídas de Job

Jobs personalizados podem expor saídas acessíveis no prompt de execução agentic via `${{ needs.job-name.outputs.output-name }}`:

```yaml wrap
jobs:
  release:
    outputs:
      release_id: ${{ steps.get_release.outputs.release_id }}
      version: ${{ steps.get_release.outputs.version }}
    steps:
      - id: get_release
        run: echo "version=${{ github.event.release.tag_name }}" >> $GITHUB_OUTPUT
---

Gerar destaques para o release ${{ needs.release.outputs.version }}.
```

Saídas de job devem ser valores de string.

## Configuração de Cache (`cache:`)

Configuração de cache usando a sintaxe padrão `actions/cache` do GitHub Actions:

Cache único:

```yaml wrap
cache:
  key: node-modules-${{ hashFiles('package-lock.json') }}
  path: node_modules
  restore-keys: |
    node-modules-
```

## Observabilidade (`observability:`)

Use `observability.otlp` para exportar rastreamentos distribuídos de execuções de fluxo de trabalho para um backend compatível com OpenTelemetry Protocol (OTLP).

```yaml wrap
observability:
  otlp:
    endpoint: ${{ secrets.OTLP_ENDPOINT }}
    headers:
      Authorization: ${{ secrets.OTLP_TOKEN }}
      X-Tenant: my-org
```

`endpoint` aceita uma string, um objeto `{url, headers}` ou um array de objetos de endpoint para fan-out.
`headers` aceita um mapa ou uma string separada por vírgula `chave=valor`.
`if-missing` suporta `error` (padrão), `warn` e `ignore`.

Para detalhes completos de referência do OpenTelemetry, incluindo variáveis de runtime, formatos de endpoint, atributos de span e arquivos de artefato, veja [OpenTelemetry](/gh-aw/reference/open-telemetry/).

## Documentação Relacionada

Veja também: [Eventos de Trigger](/gh-aw/reference/triggers/), [Motores de IA](/gh-aw/reference/engines/), [Comandos da CLI](/gh-aw/setup/cli/), [Estrutura do Fluxo de Trabalho](/gh-aw/reference/workflow-structure/), [Permissões de Rede](/gh-aw/reference/network/), [OpenTelemetry](/gh-aw/reference/open-telemetry/), [Triggers de Comando](/gh-aw/reference/command-triggers/), [MCPs](/gh-aw/guides/mcps/), [Ferramentas](/gh-aw/reference/tools/), [Importações](/gh-aw/reference/imports/)
