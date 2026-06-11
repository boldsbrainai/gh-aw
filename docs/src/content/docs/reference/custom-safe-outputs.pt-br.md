---
title: Custom Safe Outputs
description: Como criar custom safe outputs para integrações de terceiros usando jobs personalizados e servidores MCP.
sidebar:
  order: 5
---

Custom safe outputs estendem operações integradas do GitHub para integrar com serviços de terceiros — Slack, Discord, Notion, Jira, bancos de dados ou qualquer API externa que exija autenticação. Use-os para qualquer operação de escrita que os safe outputs integrados não cobrem.

## Início rápido

Aqui está um custom safe output mínimo que envia uma mensagem para o Slack:

```yaml wrap title=".github/workflows/shared/slack-notify.md"
---
safe-outputs:
  jobs:
    slack-notify:
      description: "Envia uma mensagem para o Slack"
      runs-on: ubuntu-latest
      output: "Mensagem enviada para o Slack!"
      inputs:
        message:
          description: "A mensagem a ser enviada"
          required: true
          type: string
      steps:
        - name: Enviar mensagem para o Slack
          env:
            SLACK_WEBHOOK: "${{ secrets.SLACK_WEBHOOK }}"
          run: |
            if [ -f "$GH_AW_AGENT_OUTPUT" ]; then
              MESSAGE=$(cat "$GH_AW_AGENT_OUTPUT" | jq -r '.items[] | select(.type == "slack_notify") | .message')
              # Use jq para escapar com segurança o conteúdo JSON
              PAYLOAD=$(jq -n --arg text "$MESSAGE" '{text: $text}')
              curl -X POST "$SLACK_WEBHOOK" \
                -H 'Content-Type: application/json' \
                -d "$PAYLOAD"
            else
              echo "Nenhuma saída do agente encontrada"
              exit 1
            fi
---
```

Use-o em um fluxo de trabalho:

```aw wrap title=".github/workflows/issue-notifier.md"
---
on:
  issues:
    types: [opened]
permissions:
  contents: read
imports:
  - shared/slack-notify.md
---

# Notificador de Issue

Uma nova issue foi aberta: "${{ steps.sanitized.outputs.text }}"

Resuma a issue e use a ferramenta slack-notify para enviar uma notificação.
```

O agente agora pode chamar `slack-notify` com uma mensagem, e o job personalizado é executado com acesso ao secret `SLACK_WEBHOOK`.

## Arquitetura

Custom safe outputs separam operações de leitura e escrita: agentes usam servidores Model Context Protocol (MCP) somente leitura com listas de ferramentas `allowed:`, enquanto jobs personalizados lidam com operações de escrita com acesso a secrets após a conclusão do agente.

```text
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Agente (IA)   │────▶│  Servidor MCP   │────▶│  API Externa    │
│                 │     │  (somente leitura)│     │  (Solicitações GET)│
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │
        │ chama a ferramenta safe-job
        ▼
┌─────────────────┐     ┌─────────────────┐
│  Job Personalizado │────▶│  API Externa    │
│  (com secrets)  │     │  (Solicitações POST/PUT)│
└─────────────────┘     └─────────────────┘
```

## Criando um Custom Safe Output

### Passo 1: Defina a configuração compartilhada

Em um arquivo compartilhado, defina o servidor MCP somente leitura e o job personalizado juntos:

```yaml wrap
---
mcp-servers:
  notion:
    container: "mcp/notion"
    env:
      NOTION_TOKEN: "${{ secrets.NOTION_TOKEN }}"
    allowed:
      - "search_pages"
      - "get_page"
      - "get_database"
      - "query_database"

safe-outputs:
  jobs:
    notion-add-comment:
      description: "Adiciona um comentário a uma página do Notion"
      runs-on: ubuntu-latest
      output: "Comentário adicionado ao Notion com sucesso!"
      permissions:
        contents: read
      inputs:
        page_id:
          description: "O ID da página do Notion para adicionar um comentário"
          required: true
          type: string
        comment:
          description: "O texto do comentário a ser adicionado"
          required: true
          type: string
      steps:
        - name: Adicionar comentário à página do Notion
          uses: actions/github-script@v8
          env:
            NOTION_TOKEN: "${{ secrets.NOTION_TOKEN }}"
          with:
            script: |
              const fs = require('fs');
              const notionToken = process.env.NOTION_TOKEN;
              const outputFile = process.env.GH_AW_AGENT_OUTPUT;
              
              if (!notionToken) {
                core.setFailed('O secret NOTION_TOKEN não está configurado');
                return;
              }
              
              if (!outputFile) {
                core.info('Nenhuma variável de ambiente GH_AW_AGENT_OUTPUT encontrada');
                return;
              }
              
              // Ler e analisar a saída do agente
              const fileContent = fs.readFileSync(outputFile, 'utf8');
              const agentOutput = JSON.parse(fileContent);
              
              // Filtrar para itens notion-add-comment (nome do job com traços → sublinhados)
              const items = agentOutput.items.filter(item => item.type === 'notion_add_comment');
              
              for (const item of items) {
                const pageId = item.page_id;
                const comment = item.comment;
                
                core.info(`Adicionando comentário à página do Notion: ${pageId}`);
                
                try {
                  const response = await fetch('https://api.notion.com/v1/comments', {
                    method: 'POST',
                    headers: {
                      'Authorization': `Bearer ${notionToken}`,
                      'Notion-Version': '2022-06-28',
                      'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                      parent: { page_id: pageId },
                      rich_text: [{
                        type: 'text',
                        text: { content: comment }
                      }]
                    })
                  });
                  
                  if (!response.ok) {
                    const errorData = await response.text();
                    core.setFailed(`Erro da API do Notion (${response.status}): ${errorData}`);
                    return;
                  }
                  
                  const data = await response.json();
                  core.info('Comentário adicionado com sucesso');
                  core.info(`ID do comentário: ${data.id}`);
                } catch (error) {
                  core.setFailed(`Falha ao adicionar comentário: ${error.message}`);
                  return;
                }
              }
---
```

Use `container:` para servidores Docker ou `command:`/`args:` para npx. Liste apenas ferramentas somente leitura em `allowed`. Todos os jobs exigem `description` e `inputs`. Use `output` para mensagens de sucesso e `actions/github-script@v8` para chamadas de API com tratamento de erro `core.setFailed()`.

### Passo 2: Use no fluxo de trabalho

Importe a configuração:

```aw wrap
---
on:
  issues:
    types: [opened]
permissions:
  contents: read
  actions: read

imports:
  - shared/mcp/notion.md
---

# Resumo de Issue para Notion

Analise a issue: "${{ steps.sanitized.outputs.text }}"

Pesquise a página do GitHub Issues no Notion usando as ferramentas somente leitura do Notion, depois adicione um comentário de resumo usando o safe-job notion-add-comment.
```

O agente usa ferramentas somente leitura para consultar, depois chama o safe-job que executa com permissões de escrita após a conclusão.

## Referência de Safe Job

### Propriedades do Job

| Propriedade | Tipo | Obrigatório | Descrição |
|----------|------|----------|-------------|
| `description` | string | Sim | Descrição da ferramenta mostrada ao agente |
| `runs-on` | string | Sim | Executor do GitHub Actions (ex: `ubuntu-latest`) |
| `inputs` | object | Sim | Parâmetros da ferramenta (veja [Tipos de entrada](#input-types)) |
| `steps` | array | Sim | Etapas do GitHub Actions a executar |
| `output` | string | Não | Mensagem de sucesso retornada ao agente |
| `needs` | string ou array | Não | Jobs que devem ser concluídos antes da execução deste job (veja [Ordenação de Jobs](#job-ordering-needs)) |
| `permissions` | object | Não | Permissões de token do GitHub para o job |
| `env` | object | Não | Variáveis de ambiente para todas as etapas |
| `if` | string | Não | Expressão de execução condicional |
| `timeout-minutes` | number | Não | Duração máxima do job (padrão do GitHub Actions: 360) |

### Ordenação de Jobs (`needs:`)

Use `needs:` para sequenciar um job de safe-output personalizado em relação a outros jobs no fluxo de trabalho compilado. Ao contrário de modificar manualmente `needs:` no arquivo de lock (que é sobrescrito a cada recompilação), `needs:` declarado no frontmatter persiste entre recompilações.

```yaml wrap
safe-outputs:
  create-issue: {}
  jobs:
    post-process:
      needs: safe_outputs        # executa após o job consolidated safe-outputs
      steps:
        - run: echo "post-processing"
```

O compilador valida cada entrada `needs:` no momento da compilação e falha com um erro claro se o alvo não existir. Nomes de alvo com traços são automaticamente normalizados para sublinhados (ex: `safe-outputs` → `safe_outputs`).

Alvos `needs:` válidos para safe-jobs personalizados:

| Alvo | Disponível quando |
|--------|---------------|
| `agent` | Sempre |
| `safe_outputs` | Pelo menos um manipulador integrado, script, ação ou etapa de usuário está configurado |
| `detection` | A detecção de ameaças está habilitada |
| `upload_assets` | `upload-asset` está configurado |
| `unlock` | `lock-for-agent` está habilitado |
| `<job-name>` | Esse job existe em `safe-outputs.jobs` |

Autodependências e ciclos entre jobs personalizados também são capturados no momento da compilação.

### Tipos de entrada

Todos os jobs devem definir `inputs`:

| Tipo | Descrição |
|------|-------------|
| `string` | Entrada de texto |
| `boolean` | Verdadeiro/falso (como strings: `"true"` ou `"false"`) |
| `choice` | Seleção a partir de opções predefinidas |

```yaml wrap
inputs:
  message:
    description: "Conteúdo da mensagem"
    required: true
    type: string
  notify:
    description: "Enviar notificação"
    required: false
    type: boolean
    default: "true"
  environment:
    description: "Ambiente de destino"
    required: true
    type: choice
    options: ["staging", "production"]
```

### Variáveis de ambiente

Jobs de safe-output personalizados têm acesso a estas variáveis de ambiente:

| Variável | Descrição |
|----------|-------------|
| `GH_AW_AGENT_OUTPUT` | Caminho para o arquivo JSON contendo os dados de saída do agente |
| `GH_AW_SAFE_OUTPUTS_STAGED` | Definido como `"true"` ao executar no modo encenado/visualização |

### Acessando a saída do agente

Jobs de safe-output personalizados recebem os dados do agente através da variável de ambiente `GH_AW_AGENT_OUTPUT`, que contém um caminho para um arquivo JSON. Este arquivo tem a estrutura:

```json
{
  "items": [
    {
      "type": "nome_do_job_com_sublinhados",
      "field1": "valor1",
      "field2": "valor2"
    }
  ]
}
```

O campo `type` corresponde ao nome do seu job com traços convertidos para sublinhados (ex: job `webhook-notify` → tipo `webhook_notify`).

#### Exemplo

```yaml
steps:
  - name: Processar saída
    run: |
      if [ -f "$GH_AW_AGENT_OUTPUT" ]; then
        MESSAGE=$(cat "$GH_AW_AGENT_OUTPUT" | jq -r '.items[] | select(.type == "my_job") | .message')
        echo "Mensagem: $MESSAGE"
      else
        echo "Nenhuma saída do agente encontrada"
        exit 1
      fi
```

O esquema `inputs:` serve tanto como definição da ferramenta MCP visível ao agente quanto como validação para os campos de saída gravados em `GH_AW_AGENT_OUTPUT`.

## Manipuladores de Script Inline (`safe-outputs.scripts`)

Use `safe-outputs.scripts` para definir manipuladores JavaScript inline leves que são executados dentro do loop do manipulador de job consolidated safe-outputs. Ao contrário de `jobs` (que criam um job separado do GitHub Actions para cada chamada de ferramenta), scripts são executados em processo junto aos manipuladores integrados de safe-output — não há alocação de job extra ou sobrecarga de inicialização.

**Quando usar scripts vs jobs:**

| | Scripts | Jobs |
|---|---|---|
| Execução | Em processo, no job consolidated safe-outputs | Job separado do GitHub Actions |
| Inicialização | Rápida (sem agendamento de job) | Mais lenta (novo job por chamada) |
| Secrets | Não diretamente disponíveis — use para lógica leve | Acesso total aos secrets do repositório |
| Caso de uso | Processamento leve, logs, notificações sem secrets | Chamadas de API externa que exigem secrets |

### Definindo um Script

Sob `safe-outputs.scripts`, defina cada manipulador com `description`, `inputs` e corpo `script`:

```yaml wrap title=".github/workflows/my-workflow.md"
---
safe-outputs:
  scripts:
    post-slack-message:
      description: Postar uma mensagem em um canal do Slack
      inputs:
        channel:
          description: Nome do canal do Slack
          required: true
          type: string
        message:
          description: Texto da mensagem
          required: true
          type: string
      script: |
        const targetChannel = item.channel || "#general";
        const text = item.message || "(sem mensagem)";
        core.info(`Postando em ${targetChannel}: ${text}`);
        return { success: true, channel: targetChannel };
---
```

O agente chama `post_slack_message` (traços normalizados para sublinhados) e o script é executado de forma síncrona no loop do manipulador.

### Contexto do corpo do Script

Escreva apenas o corpo do manipulador — o compilador o encapsula automaticamente. Dentro do corpo você tem acesso a:

| Variável | Descrição |
|----------|-------------|
| `item` | Objeto de mensagem de runtime com valores de campo correspondentes ao seu esquema de `inputs` |
| `core` | `@actions/core` para logs (`core.info()`, `core.warning()`, `core.error()`) |
| `resolvedTemporaryIds` | Mapa de IDs de objetos temporários resolvidos em tempo de execução |

Cada entrada declarada em `inputs` também é desestruturada em uma variável local. Por exemplo, uma entrada `inputs.channel` está disponível como `item.channel`.

```javascript
// Exemplo: acesse entradas via item
const channel = item.channel;
const message = item.message;
core.info(`Enviando para ${channel}: ${message}`);
return { sent: true };
```

> [!NOTE]
> Nomes de script com traços são normalizados para sublinhados quando registrados como ferramentas MCP (ex: `post-slack-message` torna-se `post_slack_message`). O nome normalizado é o que o agente usa para chamar a ferramenta.

### Referência de Script

| Propriedade | Tipo | Obrigatório | Descrição |
|----------|------|----------|-------------|
| `description` | string | Sim | Descrição da ferramenta mostrada ao agente |
| `inputs` | object | Sim | Parâmetros da ferramenta (mesmo esquema que jobs personalizados) |
| `script` | string | Sim | Corpo do manipulador JavaScript |

Scripts suportam os mesmos tipos de `inputs` que jobs personalizados: `string`, `boolean` e `number`.

## Wrappers de Ação do GitHub (`safe-outputs.actions`)

Use `safe-outputs.actions` para montar qualquer Ação pública do GitHub como uma ferramenta MCP invocável uma vez. No momento da compilação, `gh aw compile` busca o `action.yml` da ação para resolver suas entradas e fixa a referência da ação em um SHA específico. O agente pode chamar a ferramenta uma vez por execução de fluxo de trabalho; a ação é executada dentro do job consolidated safe-outputs.

**Quando usar ações vs scripts vs jobs:**

| | Ações | Scripts | Jobs |
|---|---|---|---|
| Execução | No job consolidated safe-outputs, como uma etapa | Em processo, no job consolidated safe-outputs | Job separado do GitHub Actions |
| Reutilização | Qualquer Ação pública do GitHub | JavaScript inline personalizado | Job YAML inline personalizado |
| Secrets | Acesso total via `env:` | Não diretamente disponíveis | Acesso total aos secrets do repositório |
| Caso de uso | Reutilizar ações existentes do marketplace | Lógica leve | Fluxos de trabalho complexos de várias etapas |

### Definindo uma Ação

Sob `safe-outputs.actions`, defina cada ação com um campo `uses` (correspondente à sintaxe `uses` do GitHub Actions) e uma substituição de `description` opcional:

```yaml wrap title=".github/workflows/my-workflow.md"
---
safe-outputs:
  actions:
    add-smoked-label:
      uses: actions-ecosystem/action-add-labels@v1
      description: Adicionar a label 'smoked' ao pull request atual
      env:
        GITHUB_TOKEN: ${{ github.token }}
---
```

O agente chama `add_smoked_label` (traços normalizados para sublinhados). As entradas declaradas da ação tornam-se os parâmetros da ferramenta — os valores são passados como entradas de etapa em tempo de execução.

### Referência de Ação

| Propriedade | Tipo | Obrigatório | Descrição |
|----------|------|----------|-------------|
| `uses` | string | Sim | Referência da ação (`proprietário/repo@ref` ou `./caminho/para/ação-local`) |
| `description` | string | Não | Descrição da ferramenta mostrada ao agente (sobrescreve a própria descrição da ação) |
| `env` | object | Não | Variáveis de ambiente adicionais injetadas na etapa da ação |

> [!NOTE]
> Nomes de ação com traços são normalizados para sublinhados quando registrados como ferramentas MCP (ex: `add-smoked-label` torna-se `add_smoked_label`). O nome normalizado é o que o agente usa para chamar a ferramenta.

> [!TIP]
> Referências de ação são fixadas em um SHA no momento da compilação para reprodutibilidade. Execute `gh aw compile` novamente para atualizar SHAs fixados após um release de ação upstream.

## Importando Jobs Personalizados

Defina jobs em arquivos compartilhados sob `.github/workflows/shared/` e importe-os:

```aw wrap
---
on: issues
permissions:
  contents: read
imports:
  - shared/slack-notify.md
  - shared/jira-integration.md
---

# Manipulador de Issue

Manipule a issue e notifique via Slack e Jira.
```

Jobs com nomes duplicados causam erros de compilação - renomeie para resolver conflitos.

## Tratamento de erros

Use `core.setFailed()` para erros e valide entradas obrigatórias:

```javascript
if (!process.env.API_KEY) {
  core.setFailed('O secret API_KEY não está configurado');
  return;
}

try {
  const response = await fetch(url);
  if (!response.ok) {
    core.setFailed(`Erro da API (${response.status}): ${await response.text()}`);
    return;
  }
  core.info('Operação concluída com sucesso');
} catch (error) {
  core.setFailed(`Falha na solicitação: ${error.message}`);
}
```

## Segurança

Armazene secrets no GitHub Secrets e passe via variáveis de ambiente. Limite as permissões do job ao mínimo necessário e valide todas as entradas.

## Suporte ao modo Staged

Quando `GH_AW_SAFE_OUTPUTS_STAGED === 'true'`, pule a operação real e exiba uma visualização usando `core.summary`. Veja [Modo Staged](/gh-aw/reference/staged-mode/#staged-mode-for-custom-safe-output-jobs) para um exemplo completo.

## Solução de problemas

| Problema | Solução |
|-------|----------|
| Job ou script não aparecendo como ferramenta | Certifique-se de que `inputs` e `description` estão definidos; verifique o caminho da importação; execute `gh aw compile` |
| Secrets não disponíveis | Verifique se o secret existe nas configurações do repositório e o nome corresponde exatamente (diferencia maiúsculas de minúsculas) |
| Job falha silenciosamente | Adicione logs `core.info()` e garanta que `core.setFailed()` seja chamado em erros |
| Agente chama a ferramenta errada | Torne a `description` específica e única; mencione explicitamente o nome do job no prompt |

## Documentação relacionada

- [DeterministicOps](/gh-aw/patterns/deterministic-ops/) - Misturando computação e raciocínio de IA
- [Safe Outputs](/gh-aw/reference/safe-outputs/) - Tipos de safe output integrados
- [MCPs](/gh-aw/guides/mcps/) - Configuração do Protocolo de Contexto de Modelo
- [Frontmatter](/gh-aw/reference/frontmatter/) - Todas as opções de configuração
- [Importações](/gh-aw/reference/imports/) - Compartilhando configurações de fluxo de trabalho
