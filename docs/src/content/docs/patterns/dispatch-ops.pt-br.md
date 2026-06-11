---
title: DispatchOps
description: Acione e teste fluxos de trabalho agenticos manualmente com entradas personalizadas usando workflow_dispatch
sidebar:
  badge: { text: 'Manual', variant: 'tip' }
---

DispatchOps permite a execução manual de fluxos de trabalho via interface do usuário ou CLI do GitHub, ideal para tarefas sob demanda, testes e fluxos de trabalho que necessitam de julgamento humano sobre o tempo de execução. O gatilho `workflow_dispatch` permite executar fluxos de trabalho com entradas personalizadas sempre que necessário.

Use DispatchOps para tarefas de pesquisa, comandos operacionais, testes de fluxos de trabalho durante o desenvolvimento, depuração de problemas em produção ou qualquer tarefa que não se encaixe em um gatilho de agenda ou evento.

## Como funciona o Workflow Dispatch

Fluxos de trabalho com `workflow_dispatch` podem ser acionados manualmente em vez de esperar por eventos como issues, pull requests ou agendamentos.

### Sintaxe Básica

Adicione `workflow_dispatch:` à seção `on:` no frontmatter do seu fluxo de trabalho:

```yaml
on:
  workflow_dispatch:
```

### Com Parâmetros de Entrada

Defina entradas para personalizar o comportamento do fluxo de trabalho em tempo de execução:

```yaml
on:
  workflow_dispatch:
    inputs:
      topic:
        description: 'Tópico de pesquisa'
        required: true
        type: string
      priority:
        description: 'Prioridade da tarefa'
        required: false
        type: choice
        options:
          - low
          - medium
          - high
        default: medium
      deploy_target:
        description: 'Ambiente de implantação'
        required: false
        type: environment
        default: staging
```

Tipos de entrada suportados: `string` (texto), `boolean` (checkbox), `choice` (dropdown), `environment` (dropdown de ambientes do GitHub).

### Tipo de Entrada de Ambiente

O tipo `environment` é populado automaticamente a partir de Configurações → Ambientes do repositório, retornando o nome selecionado como uma string. Nenhuma lista de `options` é necessária; especifique um `default` correspondente a um nome de ambiente existente. O tipo não impõe regras de proteção — use `manual-approval:` para portas de aprovação (veja [Portas de Aprovação de Ambiente](#portas-de-aprovação-de-ambiente)).

## Modelo de Segurança

### Requisitos de Permissão

A execução manual de fluxo de trabalho respeita o mesmo modelo de segurança que outros gatilhos:

- **Permissões do repositório** - O usuário deve ter acesso de escrita ou superior para acionar fluxos de trabalho
- **Controle de acesso baseado em função** - Use o campo `roles:` para restringir quem pode executar fluxos de trabalho:

```yaml
on:
  workflow_dispatch:
roles: [admin, maintainer]
```

- **Autorização de bot** - Use o campo `bots:` para permitir contas de bot específicas:

```yaml
on:
  workflow_dispatch:
bots: ["dependabot[bot]", "github-actions[bot]"]
```

### Proteção de Fork

Diferente de gatilhos de issue/PR, o `workflow_dispatch` só executa no repositório onde é definido — forks não podem acionar fluxos de trabalho no repositório pai. Isso fornece proteção inerente contra ataques baseados em fork.

### Portas de Aprovação de Ambiente

Exija aprovação manual antes da execução usando regras de proteção de ambiente do GitHub:

```yaml
on:
  workflow_dispatch:
manual-approval: production
```

Configure regras de aprovação, revisores necessários e temporizadores de espera nas Configurações → Ambientes do repositório. Veja a [documentação de ambiente do GitHub](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment) para detalhes de configuração.

## Executando Fluxos de Trabalho no GitHub.com

### Via Aba Actions

Vá para a aba **Actions**, selecione o fluxo de trabalho na barra lateral, clique em **Run workflow**, preencha quaisquer entradas e confirme. Apenas fluxos de trabalho com `workflow_dispatch:` na seção `on:` aparecem no dropdown — se o seu estiver faltando, verifique se ele foi compilado e se o `.lock.yml` foi enviado para o repositório.

## Executando Fluxos de Trabalho com CLI

O comando `gh aw run` fornece uma maneira mais rápida de acionar fluxos de trabalho a partir da linha de comando.

### Uso Básico

```bash
gh aw run workflow
```

Isso corresponde a fluxos de trabalho por prefixo de nome de arquivo, valida `workflow_dispatch:` e retorna a URL de execução imediatamente.

### Com Parâmetros de Entrada

Passe entradas usando a flag `--raw-field` ou `-f` no formato `chave=valor`:

```bash
gh aw run research --raw-field topic="computação quântica"
```

```bash
gh aw run scout \
  --raw-field topic="pesquisa em segurança de IA" \
  --raw-field priority=high
```

### Aguardar Conclusão

Monitore a execução do fluxo de trabalho e aguarde os resultados:

```bash
gh aw run research --raw-field topic="agentes de IA" --wait
```

`--wait` monitora o progresso em tempo real e sai com um código de sucesso/falha na conclusão.

### Opções Adicionais

```bash
gh aw run research --ref feature-branch              # Executar de um branch específico
gh aw run workflow --repo owner/repository           # Executar em outro repositório
gh aw run research --raw-field topic="IA" --verbose  # Saída detalhada
```

## Declarando e Referenciando Entradas

### Referenciando Entradas em Markdown

Acesse valores de entrada usando a sintaxe de expressão do GitHub Actions:

```aw wrap
---
on:
  workflow_dispatch:
    inputs:
      topic:
        description: 'Tópico de pesquisa'
        required: true
        type: string
      depth:
        description: 'Profundidade da análise'
        type: choice
        options:
          - brief
          - detailed
        default: brief
permissions:
  contents: read
safe-outputs:
  create-discussion:
---

# Assistente de Pesquisa

Pesquise o seguinte tópico: "${{ github.event.inputs.topic }}"

Profundidade da análise solicitada: ${{ github.event.inputs.depth }}

Forneça uma análise ${{ github.event.inputs.depth }} com principais descobertas e recomendações.
```

Referencie entradas com `${{ github.event.inputs.NOME_DA_ENTRADA }}` — os valores são interpolados no momento da compilação em todo o fluxo de trabalho.

### Lógica Condicional Baseada em Entradas

Use condicionais Handlebars para alterar o comportamento com base nos valores de entrada:

```markdown
{{#if (eq github.event.inputs.include_code "true")}}
Inclua trechos de código reais na sua análise.
{{else}}
Descreva padrões de código sem incluir código real.
{{/if}}

{{#if (eq github.event.inputs.priority "high")}}
URGENTE: Priorize velocidade sobre completude.
{{/if}}
```

## Padrão de Desenvolvimento: Teste de Branch

### Testando Mudanças no Fluxo de Trabalho

Adicione `workflow_dispatch:` a branches de recurso para testes antes de mesclar. Use [modo de teste](/gh-aw/experimental/trial-ops/) para testes isolados sem afetar o repositório de produção, ou execute a partir de um branch diretamente:

```bash
gh aw trial ./research.md --raw-field topic="consulta de teste"  # isolado, sem efeitos colaterais
gh aw run research --ref feature/improve-workflow          # executa contra repositório ao vivo
```

## Casos de Uso Comuns

**Pesquisa sob demanda:** Adicione uma entrada `topic` do tipo string e acione com `gh aw run research --raw-field topic="segurança de IA"` quando necessário.

**Operações manuais:** Use uma entrada `choice` com operações predefinidas (limpeza, sincronização, auditoria) para executar tarefas específicas sob demanda.

**Testes e depuração:** Adicione `workflow_dispatch` a fluxos de trabalho acionados por eventos (issues, PRs) com entradas de URL de teste opcionais para testar sem criar eventos reais.

**Teste de fluxo de trabalho agendado:** Combine `schedule` com `workflow_dispatch` para testar fluxos de trabalho agendados imediatamente, em vez de esperar pelo agendamento cron.

**Integração de sistema externo:** Quando um sistema externo (Jira, PagerDuty, Slack, API customizada) precisa fornecer um `client_payload` personalizado ou rotear por tipo de evento, prefira `repository_dispatch` em vez de `workflow_dispatch`. Ambos podem ser acionados via API, mas `repository_dispatch` é feito sob medida para chamadores externos: ele carrega um `client_payload` arbitrário, roteia por `event_type` e não requer conhecimento de um arquivo de fluxo de trabalho ou ref específico. Veja o [Gatilho de Dispatch de Repositório](/gh-aw/reference/triggers/#repository-dispatch-trigger-repository_dispatch) para detalhes de configuração.

## Solução de Problemas

**Fluxo de trabalho não listado na UI do GitHub:** Verifique se `workflow_dispatch:` existe na seção `on:`, compile o fluxo de trabalho (`gh aw compile workflow`) e envie tanto o arquivo `.md` quanto o `.lock.yml` para o repositório. A página de Actions pode precisar de um refresh.

**Erro "Workflow not found":** Use o nome do arquivo sem a extensão `.md` (`research` não `research.md`). Certifique-se de que o fluxo de trabalho existe em `.github/workflows/` e foi compilado.

**Erro "Workflow cannot be run":** Adicione `workflow_dispatch:` à seção `on:`, recompile e verifique se o `.lock.yml` inclui o gatilho antes de enviar.

**Permissão negada:** Verifique o acesso de escrita ao repositório e verifique o campo `roles:` no frontmatter do fluxo de trabalho. Para repositórios da organização, confirme sua função na organização.

**Entradas não aparecendo:** Verifique a sintaxe YAML e a indentação (2 espaços) em `workflow_dispatch.inputs`. Certifique-se de que os tipos de entrada são válidos (`string`, `boolean`, `choice`, `environment`), então recompile e envie.

**Contexto de branch errado:** Especifique o branch explicitamente com `--ref nome-do-branch` na CLI ou selecione o branch correto no dropdown do GitHub UI antes de executar.

## Documentação Relacionada

- [Fluxos de Trabalho Manuais](/gh-aw/examples/manual/) - Exemplos de fluxos de trabalho manuais
- [Referência de Gatilhos](/gh-aw/reference/triggers/) - Sintaxe completa de gatilho incluindo workflow_dispatch
- [TrialOps](/gh-aw/experimental/trial-ops/) - Testando fluxos de trabalho em isolamento
- [Comandos CLI](/gh-aw/setup/cli/) - Referência completa do comando gh aw run
- [Templating](/gh-aw/reference/templating/) - Usando expressões e condicionais
- [Melhores Práticas de Segurança](/gh-aw/introduction/architecture/) - Protegendo a execução de fluxo de trabalho
- [Início Rápido](/gh-aw/setup/quick-start/) - Começando com fluxos de trabalho agenticos
