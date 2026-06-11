---
name: gh-agent-task
description: Use os comandos gh agent-task para criar, executar e monitorar tarefas de agente.
---


# Extensão de Tarefa de Agente da CLI do GitHub

A extensão `gh agent-task` cria tarefas de codificação do GitHub Copilot a partir da CLI. Uma tarefa é uma issue do GitHub que aciona alterações de código automatizadas a partir de instruções em linguagem natural.

**Repositório**: https://github.com/github/agent-task (extensão interna do GitHub)

## Visão Geral

Tarefas de agente são issues do GitHub que:
- Contêm instruções em linguagem natural para alterações de código
- Acionam o GitHub Copilot para executar a tarefa autonomamente
- Criam pull requests com as alterações implementadas
- Fornecem um fluxo de trabalho para revisar e mesclar (merge) modificações de código automatizadas

## Instalação

Instale via CLI do GitHub:

```bash
gh extension install github/agent-task
```

**Nota**: Esta extensão requer autenticação com um Personal Access Token (PAT) que tenha permissões apropriadas para criar issues e pull requests.

## Comandos Principais

### Criar Tarefa de Agente

Crie uma nova tarefa de agente a partir de uma descrição:

```bash
# Crie tarefa com descrição em linha
gh agent-task create "Corrigir o bug no fluxo de autenticação"

# Crie tarefa a partir de arquivo
gh agent-task create --from-file task-description.md

# Especifique branch base
gh agent-task create --base develop "Implementar nova funcionalidade"

# Crie em repositório diferente
gh agent-task create --repo owner/repo "Atualizar documentação"
```

**Parâmetros de Comando:**
- **Descrição** (posicional): Descrição em linguagem natural da tarefa
- **`--from-file <caminho>`**: Leia a descrição da tarefa a partir do arquivo
- **`--base <branch>`**: Branch base para o pull request (padrão: branch padrão do repositório)
- **`--repo <owner/repo>`**: Repositório de destino (padrão: repositório atual)

**Formato de Saída:**
O comando gera a URL da tarefa de agente criada:
```
https://github.com/owner/repo/issues/123
```

### Listar Tarefas de Agente

Liste tarefas de agente em um repositório:

```bash
# Liste todas as tarefas de agente
gh agent-task list

# Liste com filtros
gh agent-task list --state open
gh agent-task list --state closed
gh agent-task list --state all
```

### Visualizar Tarefa de Agente

Visualize detalhes de uma tarefa de agente específica:

```bash
# Visualize pelo número
gh agent-task view 123

# Visualize pela URL
gh agent-task view https://github.com/owner/repo/issues/123
```

### Atualizar Tarefa de Agente

Atualize uma tarefa de agente existente:

```bash
# Atualize descrição
gh agent-task update 123 "Descrição de tarefa atualizada"

# Atualize a partir de arquivo
gh agent-task update 123 --from-file updated-description.md
```

## Formato de Descrição de Tarefa

Descrições de tarefa de agente devem ser instruções claras e específicas em linguagem natural:

**Bom Exemplo:**
```markdown
# Refatorar Autenticação de Usuário

Refatore o fluxo de autenticação de usuário em `src/auth/login.js` para:
1. Usar async/await em vez de callbacks
2. Adicionar tratamento de erro adequado com mensagens de erro específicas
3. Adicionar validação de entrada para formato de e-mail
4. Atualizar testes para cobrir a nova implementação

Mantenha compatibilidade retroativa com a API existente.
```

**Mau Exemplo:**
```markdown
Corrigir autenticação
```

**Melhores Práticas:**
- Seja específico sobre o que precisa mudar
- Referencie caminhos de arquivo quando relevante
- Inclua critérios de aceitação
- Especifique quaisquer restrições ou requisitos
- Mencione expectativas de teste

## Integração com Fluxos de Trabalho Agentic do GitHub

A extensão `gh agent-task` é usada pelo recurso de saída segura `create-agent-task` no GitHub Agentic Workflows (gh-aw).

### Configuração de Saída Segura

```yaml
safe-outputs:
  create-agent-task:
    base: main                       # Branch base para o PR da tarefa do agente
    target-repo: "owner/target-repo" # Criação de tarefa em repositório cruzado
```

### Exemplo de Fluxo de Trabalho

```yaml
on:
  issues:
    types: [labeled]
permissions:
  contents: read
  actions: read
engine: claude
safe-outputs:
  create-agent-task:
    base: main

# Delegador de Tarefa de Código

Quando uma issue for etiquetada com "code-task", analise os requisitos e crie uma tarefa de agente de codificação GitHub Copilot com instruções detalhadas para implementar as alterações solicitadas.
```

### Detalhes de Implementação

O processador de saída segura:
1. Lê a saída do agente da execução do fluxo de trabalho
2. Extrai itens `create_agent_task` da saída estruturada
3. Escreve descrições de tarefa em arquivos temporários
4. Executa `gh agent-task create --from-file <arquivo> --base <branch>`
5. Captura a URL e o número da tarefa criada
6. Relata resultados no resumo do job

**Variáveis de Ambiente:**
- `GITHUB_AW_AGENT_TASK_BASE`: Branch base para o pull request
- `GITHUB_AW_TARGET_REPO`: Repositório de destino para criação de tarefa em repositório cruzado
- `GITHUB_AW_SAFE_OUTPUTS_STAGED`: Flag do modo de preview

## Requisitos de Autenticação

A criação de tarefa de agente requer permissões elevadas além do `GITHUB_TOKEN` padrão:

**Permissões Necessárias:**
- `contents: write` - Para criar branches e commits
- `issues: write` - Para criar a issue da tarefa do agente
- `pull-requests: write` - Para criar pull requests

**Precedência de Token:**
1. `COPILOT_GITHUB_TOKEN` - Token dedicado a operações Copilot (recomendado)
2. `GH_AW_GITHUB_TOKEN` - Token de override geral (legado)
3. Token personalizado via campo de configuração `github-token`

**Nota**: O `GITHUB_TOKEN` padrão **não** é suportado pois carece das permissões necessárias. Os secrets `COPILOT_CLI_TOKEN` e `GH_AW_COPILOT_TOKEN` não são mais suportados desde a v0.26+.

### Configurando a Autenticação

Armazene seu Personal Access Token em secrets do repositório:

```bash
# Nas configurações do seu repositório, adicione o secret:
# Nome: COPILOT_GITHUB_TOKEN (recomendado)
# Valor: ghp_SeuPersonalAccessToken
```

:::note[Compatibilidade Retroativa]
O nome de token legado `GH_AW_GITHUB_TOKEN` ainda é suportado para compatibilidade retroativa. O token `GH_AW_COPILOT_TOKEN` não é mais suportado desde a v0.26+.
:::

## Tratamento de Erro

### Erros de Autenticação

```
Erro: falha ao criar tarefa de agente
autenticação necessária
```

**Solução**: Configure `COPILOT_GITHUB_TOKEN` ou o legado `GH_AW_GITHUB_TOKEN` com um PAT.

### Erros de Permissão

```
Erro: 403 Proibido
Recurso não acessível pela integração
```

**Solução**: Garanta que o token tenha permissões `contents: write`, `issues: write` e `pull-requests: write`.

### Repositório Não Encontrado

```
Erro: repositório não encontrado
```

**Solução**: Verifique se o repositório de destino existe e se o token tem acesso a ele.

## Testando em Modo Staged

Quando `safe-outputs.staged: true`, tarefas de agente são pré-visualizadas sem criação:

```yaml
safe-outputs:
  staged: true
  create-agent-task:
```

**Saída Staged:**
```markdown
## 🎭 Modo Staged: Preview de Criação de Tarefas de Agente

As seguintes tarefas de agente seriam criadas se o modo staged estivesse desabilitado:

### Tarefa 1

**Descrição:**
Refatorar autenticação para usar o padrão async/await

**Branch Base:** main

**Repositório de Destino:** owner/repo
```

## Padrões Comuns

### Tarefas de Agente Acionadas por Issue

```yaml
on:
  issues:
    types: [labeled]
engine: claude
safe-outputs:
  create-agent-task:

Quando a issue for etiquetada com "needs-implementation", crie uma tarefa de agente com instruções de implementação.
```

### Melhorias de Código Agendadas

```yaml
on:
  schedule:
    - cron: "0 9 * * 1"  # Segunda-feira 9AM
engine: copilot
safe-outputs:
  create-agent-task:
    base: develop

Analise a base de código por oportunidades de melhoria e crie tarefas de agente para as 3 principais melhorias.
```

### Delegação de Tarefa em Repositório Cruzado

```yaml
on: workflow_dispatch
engine: claude
safe-outputs:
  create-agent-task:
    target-repo: "organization/backend-repo"
    base: main

Crie tarefa de agente no repositório backend para implementar as alterações de API descritas nesta issue.
```

## Melhores Práticas

### Diretrizes de Descrição da Tarefa

1. **Seja Específico**: Inclua caminhos de arquivo, nomes de função e requisitos exatos
2. **Inclua Contexto**: Explique por que a alteração é necessária
3. **Defina Sucesso**: Especifique critérios de aceitação ou resultados esperados
4. **Mencione Testes**: Solicite cobertura de teste para as alterações
5. **Set Constraints**: Note quaisquer requisitos de compatibilidade ou limitações

### Considerações de Segurança

1. **Segurança do Token**: Armazene PATs como secrets, nunca commite no repositório
2. **Escopo de Permissão**: Use permissões mínimas necessárias em tokens
3. **Acesso ao Repositório**: Valide o repositório de destino antes da criação da tarefa
4. **Processo de Revisão**: Estabeleça fluxo de trabalho de revisão para código gerado por agente

### Diretrizes Operacionais

1. **Monitore o Uso**: Rastreie taxas de criação e conclusão de tarefa de agente
2. **Revise a Saída**: Sempre revise pull requests gerados por agente
3. **Itere**: Refine descrições de tarefa baseadas no desempenho do agente
4. **Documente**: Mantenha padrões para tipos comuns de tarefa

## Depuração

### Falha Silenciosa na Criação de Tarefa

**Symptoma**: Sem erro, mas nenhuma tarefa criada

**Verifique**:
1. Verifique se `COPILOT_GITHUB_TOKEN` está definido nos secrets do repositório
2. Confirme se o token tem permissões necessárias
3. Verifique logs do job para mensagens de erro
4. Verifique se o repositório de destino existe e é acessível

### Tarefa de Agente Não Aciona Copilot

**Sintoma**: Tarefa criada, mas sem PR automatizado

**Causas Possíveis**:
1. GitHub Copilot não habilitado para o repositório
2. Descrição da tarefa pouco clara ou ambígua
3. Configurações do repositório bloqueando PRs automatizados
4. Problemas no serviço Copilot

**Solução**: Verifique configurações do Copilot no repositório e refine a descrição da tarefa.

### Falha em Tarefas de Repositório Cruzado

**Sintoma**: Erro ao criar tarefas em repositório diferente

**Verifique**:
1. Token tem acesso ao repositório de destino
2. Repositório de destino existe e está escrito corretamente
3. Token tem permissões necessárias no repositório de destino

## Estrutura de Saída

Quando usada via saídas seguras, o job create-agent-task fornece saídas:

```yaml
outputs:
  task_number: "123"
  task_url: "https://github.com/owner/repo/issues/123"
```

**Uso em Jobs Dependentes:**
```yaml
jobs:
  follow_up:
    needs: create_agent_task
    steps:
      - name: Notificar equipe
        run: |
          echo "Tarefa de agente criada: ${{ needs.create_agent_task.outputs.task_url }}"
```

## Referências

- [Documentação do GitHub Copilot](https://docs.github.com/en/copilot)
- [Extensões da CLI do GitHub](https://docs.github.com/en/github-cli/github-cli/using-github-cli-extensions)
- [Documentação de Saídas Seguras](https://github.github.com/gh-aw/reference/safe-outputs/)
- [Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
