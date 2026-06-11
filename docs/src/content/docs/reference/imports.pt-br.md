---
title: Importações
description: Aprenda como modularizar e reutilizar componentes de fluxo de trabalho em múltiplos fluxos de trabalho usando o campo imports no frontmatter para melhor organização e manutenibilidade.
sidebar:
  order: 325
---

## Sintaxe

Use `imports:` no frontmatter ou `{{#import ...}}` no markdown para compartilhar componentes de fluxo de trabalho entre múltiplos fluxos de trabalho.

```aw wrap
---
on: issues
engine: copilot
imports:
  - shared/common-tools.md
  - shared/mcp/tavily.md
---

# Seu Fluxo de Trabalho

Instruções do fluxo de trabalho aqui...
```

### Importações parametrizadas (`uses`/`with`)

Fluxos de trabalho compartilhados que declaram um `import-schema` aceitam parâmetros de runtime. Use a forma `uses`/`with` para passar valores:

```aw wrap
---
on: issues
engine: copilot
imports:
  - uses: shared/mcp/serena.md
    with:
      languages: ["go", "typescript"]
---
```

`uses` é um alias para `path`; `with` é um alias para `inputs`.

### Restrição de importação única

Um arquivo de fluxo de trabalho pode aparecer no máximo uma vez em um grafo de importação. Se o mesmo arquivo for importado mais de uma vez com valores `with` idênticos, ele é silenciosamente deduplicado. Importar o mesmo arquivo com valores `with` **diferentes** é um erro em tempo de compilação:

```
conflito de importação: 'shared/mcp/serena.md' é importado mais de uma vez com valores 'with' diferentes.
Um fluxo de trabalho importado só pode ser importado uma vez por fluxo de trabalho.
  'with' anterior: {"languages":["go"]}
  Novo 'with':      {"languages":["typescript"]}
```

No markdown, use `{{#runtime-import filepath}}` para injetar o conteúdo de outro arquivo diretamente no corpo nessa posição. Isso é útil para compartilhar trechos de prompt reutilizáveis, instruções de tom ou material de referência entre fluxos de trabalho.

```aw wrap
---
on: schedule
engine: copilot
---

{{#runtime-import .github/shared/editorial.md}}

# Relatório Diário

Gere o relatório diário.
```

Use `{{#runtime-import? filepath}}` para pular silenciosamente um arquivo ausente em vez de falhar:

```aw wrap
{{#runtime-import .github/shared/editorial.md}}    # obrigatório — falha se ausente
{{#runtime-import? .github/shared/optional.md}}    # opcional — pulado se ausente
```

Os caminhos são resolvidos dentro da pasta `.github`. Você pode especificar caminhos com ou sem o prefixo `.github/` — ambos `.github/shared/editorial.md` e `shared/editorial.md` referem-se ao mesmo arquivo. Veja [Runtime Imports](/gh-aw/reference/templating/#runtime-imports) para URLs, intervalos de linha e detalhes de segurança.

## Componentes de Fluxo de Trabalho Compartilhados

Arquivos sem um campo `on` são componentes de fluxo de trabalho compartilhados — validados, mas não compilados no GitHub Actions, apenas importados por outros fluxos de trabalho. Componentes compartilhados também podem definir chaves `on` seguras para importação (`skip-if-match`, `skip-if-no-match`, `skip-roles`, `skip-bots`, `github-token`, `github-app`) para reutilização por meio de importações.

### Bundles comuns

Use componentes compartilhados agrupados (bundles) quando você importar regularmente o mesmo par em conjunto:

```aw wrap
---
on:
  schedule: daily
engine: copilot
imports:
  - shared/reporting-otlp.md
---
```

`shared/reporting-otlp.md` combina `shared/reporting.md` e `shared/otlp.md` para fluxos de trabalho de relatório habilitados para telemetria.

## Esquema de Importação (`import-schema`)

Use `import-schema` para declarar um contrato de parâmetro tipado. Chamadores passam valores via `with`; o compilador valida-os e os substitui no frontmatter e corpo do arquivo compartilhado antes do processamento.

```aw wrap
---
# shared/deploy.md — sem campo 'on:', apenas componente compartilhado
import-schema:
  region:
    type: string
    required: true
  environment:
    type: choice
    options: [staging, production]
    required: true
  count:
    type: number
    default: 10
  languages:
    type: array
    items:
      type: string
    required: true
  config:
    type: object
    description: Objeto de configuração
    properties:
      apiKey:
        type: string
        required: true
      timeout:
        type: number
        default: 30

mcp-servers:
  my-server:
    url: "https://example.com/mcp"
    allowed: ["*"]
---

Implantar ${{ github.aw.import-inputs.count }} itens para ${{ github.aw.import-inputs.region }}.
Chave de API: ${{ github.aw.import-inputs.config.apiKey }}.
Linguagens: ${{ github.aw.import-inputs.languages }}.
```

### Tipos suportados

| Tipo | Descrição | Campos extras |
|------|-------------|--------------|
| `string` | Valor de texto simples | — |
| `number` | Valor numérico | — |
| `boolean` | `true`/`false` | — |
| `choice` | Um de um conjunto fixo de strings | `options: [...]` |
| `array` | Lista ordenada de valores | `items.type` (tipo de elemento) |
| `object` | Mapa chave/valor | `properties` (um nível de profundidade) |

Cada campo suporta `required: true` e um valor `default` opcional.

### Acessando entradas em fluxos de trabalho compartilhados

Use `${{ github.aw.import-inputs.<key> }}` para substituir um valor de nível superior; use notação de ponto para sub-campos de objeto (ex: `${{ github.aw.import-inputs.config.apiKey }}`). A substituição aplica-se tanto ao frontmatter quanto ao corpo, portanto, as entradas podem orientar qualquer campo, como `mcp-servers` ou `runtimes`.

### Chamando um fluxo de trabalho compartilhado parametrizado

```aw wrap
---
on: issues
engine: copilot
imports:
  - uses: shared/deploy.md
    with:
      region: us-east-1
      environment: staging
      count: 5
      languages: ["go", "typescript"]
      config:
        apiKey: my-secret-key
        timeout: 60
---
```

O compilador valida campos `required`, opções `choice`, tipos de elemento de array e `properties` de objeto. Chaves desconhecidas são erros de tempo de compilação.

## Resolução de Caminho

Os caminhos de importação são resolvidos usando um de três modos, dependendo do formato.

### Caminhos relativos (padrão)

Caminhos que não começam com `.github/`, `/` ou um prefixo `owner/repo/` são resolvidos em relação ao diretório do fluxo de trabalho importador. Ao compilar com o valor padrão `--dir`, esse diretório é `.github/workflows/`.

```aw wrap
---
on: issues
engine: copilot
imports:
  - shared/common-tools.md        # → .github/workflows/shared/common-tools.md
  - ../agents/helper.md           # → .github/agents/helper.md (.. sobe a partir de .github/workflows/)
---
```

### Caminhos relativos à raiz do repositório

Caminhos começando com `.github/` ou `/` são resolvidos a partir da raiz do repositório. Caminhos absolutos (`/`) devem apontar para dentro de `.github/` ou `.agents/`; qualquer outro prefixo é rejeitado no momento da compilação por segurança.

```aw wrap
---
on: pull_request
engine: copilot
imports:
  - .github/agents/code-reviewer.md   # resolvido a partir da raiz do repo
  - .github/workflows/shared/app.md   # resolvido a partir da raiz do repo
---
```

Este formato é necessário quando fluxos de trabalho em diferentes diretórios precisam importar o mesmo arquivo compartilhado usando um caminho estável, e é a maneira suportada de importar arquivos do diretório `.github/agents/`.

### Importações entre repositórios

Caminhos correspondentes a `owner/repo/path@ref` são buscados do GitHub no momento da compilação. O sufixo `@ref` fixa uma tag semântica (`@v1.0.0`), branch (`@main`) ou SHA de commit. Importações remotas são armazenadas em cache em `.github/aw/imports/` pelo SHA de commit, permitindo compilação offline; importações locais nunca são armazenadas em cache. Veja [Reutilizando Fluxos de Trabalho](/gh-aw/guides/packaging-imports/) para fluxos de instalação e atualização.

```aw wrap
---
on: issues
engine: copilot
imports:
  - acme-org/shared-workflows/shared/reporting.md@v2.1.0   # fixado em uma tag
  - acme-org/shared-workflows/shared/tools.md@main         # rastrear um branch
  - acme-org/shared-workflows/shared/helpers.md@abc1234    # fixado em um SHA
---
```

### Referências de seção e importações opcionais

Anexe `#SectionName` a qualquer caminho para importar uma única seção de um arquivo markdown:

```
imports:
  - shared/tools.md#WebSearch
```

Use `?` após `import` para marcar uma importação como opcional — arquivos ausentes são pulados silenciosamente em vez de falhar a compilação. Isso se aplica tanto a importações de frontmatter quanto a diretivas de nível de corpo:

```yaml
# Frontmatter — opcional
imports:
  - shared/optional-tools.md?
```

```aw wrap
# Corpo — injeção de conteúdo opcional
{{#runtime-import? .github/shared/optional.md}}
```

## Arquivos de Agente

Arquivos de agente são documentos markdown em `.github/agents/` que adicionam instruções especializadas ao motor de IA. Importe-os como caminhos locais ou remotos — arquivos em `.github/agents/` são reconhecidos automaticamente como arquivos de agente, e apenas **um arquivo de agente** pode ser importado por fluxo de trabalho.

```yaml wrap
---
on: pull_request
engine: copilot
imports:
  - .github/agents/code-reviewer.md                                       # local
  - githubnext/shared-agents/.github/agents/security-reviewer.md@v1.0.0   # remoto, fixado
---
```

Importações de agente remotas suportam o mesmo versionamento `@ref` e armazenamento em cache por chave SHA que outras importações remotas.

## Mesclagem de Frontmatter

### Campos de Importação Permitidos

Arquivos de fluxo de trabalho compartilhados (sem campo `on:`) podem definir os campos abaixo. Outros campos geram avisos e são ignorados. Arquivos de agente (`.github/agents/*.md`) podem adicionalmente definir `name` e `description`.

| Campo | Objetivo |
|-------|---------|
| `import-schema` | Esquema de parâmetro para validação `with` e substituição de entrada |
| `tools` | Configurações de ferramenta (`bash`, `web-fetch`, `github`, `mcp-*` etc.) |
| `mcp-servers` | Configurações de servidor Model Context Protocol |
| `mcp-scripts` | Configurações de Scripts MCP |
| `services` | Serviços Docker para execução de fluxo de trabalho |
| `safe-outputs` | Manipuladores de safe output e configuração |
| `network` | Especificações de permissão de rede |
| `permissions` | Permissões do GitHub Actions (validadas, não mescladas) |
| `runtimes` | Substituições de versão de runtime (node, python, go etc.) |
| `secret-masking` | Passos de mascaramento de segredo |
| `env` | Variáveis de ambiente em nível de fluxo de trabalho |
| `pre-agent-steps` | Passos executados após o download de artefatos, antes da execução do motor |
| `post-steps` | Passos executados após a execução do motor |
| `github-app` | Credenciais do GitHub App para emissão de token |
| `checkout` | Configuração de checkout para o job do agente |
| `engine.mcp` | Configurações de gateway MCP (`tool-timeout`, `session-timeout`); o identificador do próprio motor é sempre herdado do fluxo de trabalho importador |

### Semântica de Mesclagem Específica de Campo

As importações são processadas usando travessia em largura (breadth-first): importações diretas primeiro, depois aninhadas. Importações anteriores na lista têm precedência; importações circulares falham no momento da compilação.

| Campo | Estratégia de mesclagem |
|-------|---------------|
| `tools:` | Mesclagem profunda; arrays `allowed` concatenam e deduplicam. Conflitos de ferramenta MCP falham, exceto em arrays `allowed`. |
| `mcp-servers:` | Servidores importados sobrescrevem servidores principais com o mesmo nome; primeiro-a-vencer entre as importações. |
| `network:` | União de domínios `allowed` (deduplicados, ordenados). `mode` e `firewall` principais têm precedência. |
| `permissions:` | Apenas validação — não mesclado. Principal deve declarar todas as permissões importadas em níveis suficientes (`write` ≥ `read` ≥ `none`). |
| `safe-outputs:` | Cada tipo definido uma vez; principal sobrescreve importações. Tipos duplicados entre importações falham. |
| `runtimes:` | Principal sobrescreve importações; valores importados preenchem campos não especificados. |
| `services:` | Todos os serviços mesclados; nomes duplicados falham na compilação. |
| `github-app:` | `github-app` do fluxo de trabalho principal tem precedência; primeiro valor importado preenche se o fluxo de trabalho principal não definir um. |
| `checkout:` | Entradas de checkout importadas são anexadas após as entradas do fluxo de trabalho principal. Para pares (repositório, path) duplicados, a entrada do fluxo de trabalho principal tem precedência: primeiro-visto vence para `ref`, e a auth é mutuamente exclusiva — uma vez que `github-token` ou `github-app` é definido pelo fluxo de trabalho principal, uma duplicata importada não pode adicionar o outro método de auth. `checkout: false` no fluxo de trabalho principal desativa todo o checkout, incluindo entradas importadas. |
| `engine.mcp` | Primeiro-a-vencer entre importações. Arquivos compartilhados podem definir `engine:` apenas com `mcp.tool-timeout` e/ou `mcp.session-timeout` (sem identificador de motor). A configuração `engine.mcp` do próprio fluxo de trabalho importador tem precedência; o primeiro valor importado preenche se o fluxo de trabalho principal não definir um valor. |
| `steps:` | Passos importados prependidos ao principal; concatenados na ordem de importação. |
| `pre-agent-steps:` | Passos pré-agente importados prependidos ao principal; concatenados na ordem de importação. |
| `post-steps:` | Passos pós-execução importados anexados após o principal; concatenados na ordem de importação. |
| `jobs:` | Não mesclado — defina apenas no fluxo de trabalho principal. Use `safe-outputs.jobs` para jobs importáveis. |
| `safe-outputs.jobs` | Nomes devem ser únicos; duplicatas falham. Ordem determinada por declarações `needs:`. |
| `env:` | Variáveis de env do fluxo de trabalho principal têm precedência sobre importações. Chaves duplicadas entre diferentes importações falham na compilação — mova para o fluxo de trabalho principal para substituir valores importados. |

Exemplo — mesclagem de `tools.bash.allowed`:

```aw wrap
# main.md: [write]
# import:  [read, list]
# result:  [read, list, write]
```

### Passos de Importação

Compartilhe passos reutilizáveis de pré-execução — como rotação de token, configuração de ambiente ou verificações de gate — entre múltiplos fluxos de trabalho definindo-os em um arquivo compartilhado:

```aw title="shared/rotate-token.md" wrap
---
description: Configuração compartilhada de rotação de token
steps:
  - name: Rotacionar token do GitHub App
    id: get-token
    uses: actions/create-github-app-token@v1
    with:
      client-id: ${{ vars.APP_ID }}
      private-key: ${{ secrets.APP_PRIVATE_KEY }}
---
```

Qualquer fluxo de trabalho que importa este arquivo terá o passo de rotação prependido antes de seus próprios passos:

```aw title="my-workflow.md" wrap
---
on: issues
engine: copilot
imports:
  - shared/rotate-token.md
permissions:
  contents: read
  issues: write
steps:
  - name: Preparar contexto
    run: echo "context ready"
---

# Meu Fluxo de Trabalho

Processe a issue usando o token rotacionado do passo importado.
```

Os passos das importações são executados **antes** dos passos definidos no fluxo de trabalho principal, na ordem de declaração da importação.

### Importando Servidores MCP

Defina uma configuração de servidor MCP uma vez e importe-a onde for necessário:

```aw title="shared/mcp/tavily.md" wrap
---
description: Servidor MCP de busca na web Tavily
mcp-servers:
  tavily:
    url: "https://mcp.tavily.com/mcp/?tavilyApiKey=${{ secrets.TAVILY_API_KEY }}"
    allowed: ["*"]
network:
  allowed:
    - mcp.tavily.com
---
```

Os consumidores importam com `imports: [shared/mcp/tavily.md]`.

### Importando Configurações de Gateway MCP

Arquivos de fluxo de trabalho compartilhados podem exportar `engine.mcp.tool-timeout` e `engine.mcp.session-timeout` sem especificar um identificador de motor — o próprio motor é sempre herdado do fluxo de trabalho importador.

```aw title="shared/mcp/slow-backend.md" wrap
---
description: Configurações de gateway MCP para servidores MCP slow-backend
engine:
  mcp:
    tool-timeout: 5m     # Permitir até 5 minutos por chamada de ferramenta
    session-timeout: 2h  # Manter sessões MCP vivas para fluxos de trabalho de longa duração
---
```

As configurações `engine.mcp` do próprio fluxo de trabalho importador têm precedência. Entre as importações, o primeiro arquivo que declara um timeout vence para aquela configuração.

### Importando `jobs:` de Nível Superior

Os `jobs:` de nível superior definidos em um fluxo de trabalho compartilhado são mesclados no arquivo de bloqueio compilado do fluxo de trabalho importador. A ordem de execução do job é determinada pelas entradas `needs` — um job compartilhado pode ser executado antes ou depois de outros jobs no fluxo de trabalho final:

```aw title="shared/build.md" wrap
---
description: Job de build compartilhado que compila artefatos para o agente inspecionar

jobs:
  build:
    runs-on: ubuntu-latest
    needs: [activation]
    outputs:
      artifact_name: ${{ steps.build.outputs.artifact_name }}
    steps:
      - uses: actions/checkout@v6
      - name: Build
        id: build
        run: |
          npm ci && npm run build
          echo "artifact_name=build-output" >> "$GITHUB_OUTPUT"
      - uses: actions/upload-artifact@v4
        with:
          name: build-output
          path: dist/

steps:
  - uses: actions/download-artifact@v4
    with:
      name: ${{ needs.build.outputs.artifact_name }}
      path: /tmp/build-output
---
```

Importe-o para que o job `build` seja executado antes do agente e seus artefatos estejam disponíveis como pré-passos:

```aw title="my-workflow.md" wrap
---
on: pull_request
engine: copilot
imports:
  - shared/build.md
permissions:
  contents: read
  pull-requests: write
---

# Fluxo de Trabalho de Revisão de Código

Revise a saída de build em /tmp/build-output e sugira melhorias.
```

No arquivo de bloqueio compilado, o job `build` aparece juntamente com os jobs `activation` e `agent`, ordenados de acordo com as declarações `needs` de cada job.

### Importando Jobs via `safe-outputs.jobs`

Jobs definidos sob `safe-outputs:` podem ser compartilhados entre fluxos de trabalho. Esses jobs tornam-se ferramentas MCP chamáveis que o agente de IA pode invocar durante a execução:

```aw title="shared/notify.md" wrap
---
description: Job de notificação compartilhado
safe-outputs:
  notify-slack:
    description: "Postar uma mensagem no Slack"
    runs-on: ubuntu-latest
    output: "Notificação enviada"
    inputs:
      message:
        description: "Mensagem para postar"
        required: true
        type: string
    steps:
      - name: Postar no Slack
        env:
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: |
          curl -s -X POST "$SLACK_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"text\":\"${{ inputs.message }}\"}"
---
```

Os consumidores importam com `imports: [shared/notify.md]` e instruem o agente a chamar `notify-slack` quando apropriado.

## Arquivos de Bloqueio Autocontidos (`inlined-imports: true`)

Definir `inlined-imports: true` incorpora todo o conteúdo importado diretamente no `.lock.yml` compilado no momento da compilação. O arquivo de bloqueio resultante é **autocontido** — não requer acesso ao sistema de arquivos ou checkout entre repositórios em tempo de execução.

Habilite-o sempre que a resolução de importação em runtime falhar:

- **`workflow_call` entre organizações** — um trigger na Org A chamando um fluxo de trabalho na Org B não pode fazer checkout da pasta `.github` da Org B com o `GITHUB_TOKEN` do chamador, produzindo `fatal: repository '...' not found`.
- **Regras de repositório** — fluxos de trabalho usados como um [status check obrigatório](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) são executados em um contexto restrito que não pode acessar outros arquivos no repo, produzindo `ERR_SYSTEM: Runtime import file not found`.

Ambos os casos são resolvidos agrupando importações no arquivo de bloqueio no momento da compilação:

```aw wrap
---
on:
  workflow_call:
engine: copilot
inlined-imports: true
imports:
  - shared/common-tools.md
  - shared/security-setup.md
---

# Fluxo de Trabalho de Gateway de Plataforma

Instruções do fluxo de trabalho aqui.
```

Após adicionar a flag, recompile:

```bash
gh aw compile my-workflow
```

**Trade-off**: o `.lock.yml` compilado é maior porque o conteúdo importado é incorporado inline.

> [!NOTE]
> Com `inlined-imports: true`, qualquer alteração em um arquivo importado requer a recompilação do fluxo de trabalho para entrar em vigor. O `.lock.yml` compilado deve ser comitado e enviado para que o conteúdo atualizado seja executado.
>
> `inlined-imports: true` não pode ser combinado com importações de arquivo de agente (arquivos `.github/agents/`). Se o seu fluxo de trabalho importar um arquivo de agente personalizado, remova-o antes de habilitar inlined imports.

## Documentação Relacionada

- [Empacotamento e Atualização](/gh-aw/guides/packaging-imports/) - Guia completo para gerenciar importações de fluxo de trabalho
- [Frontmatter](/gh-aw/reference/frontmatter/) - Referência de opções de configuração
- [MCPs](/gh-aw/guides/mcps/) - Configuração do Model Context Protocol
- [Safe Outputs](/gh-aw/reference/safe-outputs/) - Detalhes de configuração de safe output
- [Configuração de Rede](/gh-aw/reference/network/) - Gerenciamento de permissão de rede
