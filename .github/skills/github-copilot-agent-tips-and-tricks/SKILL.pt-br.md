---
name: github-copilot-agent-tips-and-tricks
description: Dicas práticas para revisar e melhorar PRs do agente Copilot.
---


# Dicas e Truques do Agente GitHub Copilot

Use este guia para encontrar, revisar e trabalhar com pull requests do agente de codificação Copilot no gh-aw.

## Identificando PRs do Agente Copilot

### Convenção de Nomenclatura de Branch

Branches do agente de codificação Copilot usam o prefixo `copilot/`, o que os torna fáceis de identificar e filtrar.

**Exemplos deste repositório:**
- `copilot/add-cache-for-imported-workflows`
- `copilot/fix-istruthy-bundling-issue`
- `copilot/update-audit-command-copilot`
- `copilot/refactor-mcp-tool-rendering`

### Atribuição de Autor

PRs do agente de codificação Copilot são normalmente criados por:
- `app/github-copilot` - A conta de bot do GitHub Copilot
- Desenvolvedores individuais usando o Copilot como assistente

## Pesquisando PRs do Agente Copilot

### Usando a CLI do GitHub (`gh`)

**Pré-requisitos:**
```bash
# Autentique com a CLI do GitHub
gh auth login
```

**Pesquise por autor (bot do GitHub Copilot):**
```bash
# Liste todos os PRs criados pelo bot Copilot
gh pr list --author "app/github-copilot" --limit 100

# Inclua PRs fechados
gh pr list --author "app/github-copilot" --state all --limit 100

# Obtenha saída JSON detalhada
gh pr list --author "app/github-copilot" --json number,title,author,headRefName,createdAt,state
```

**Pesquise por prefixo de branch:**
```bash
# Encontre todos os PRs de branches copilot/*
gh pr list --search "head:copilot/" --state all

# Combine com outros filtros
gh pr list --search "head:copilot/ is:open"
gh pr list --search "head:copilot/ is:merged"
```

**Filtre com jq:**
```bash
# Extraia campos específicos
gh pr list --limit 100 --json author,number,title,headRefName \
  --jq '.[] | select(.headRefName | startswith("copilot/")) | {number, title, branch: .headRefName}'

# Filtre por autor contendo "copilot"
gh pr list --limit 100 --json author,number,title \
  --jq '.[] | select(.author.login | contains("copilot"))'
```

### Usando Comandos Git

**Liste branches copilot:**
```bash
# Branches copilot locais e remotos
git branch -a | grep copilot

# Apenas branches copilot remotos
git branch -r | grep copilot
```

**Pesquise o histórico de commits:**
```bash
# Encontre commits com "copilot" na mensagem
git log --all --grep="copilot" --oneline

# Encontre commits por autor copilot
git log --all --author="copilot" --oneline

# Mostre gráfico com commits relacionados a copilot
git log --all --grep="copilot" --oneline --graph
```

**Encontre PRs copilot mesclados:**
```bash
# Pesquise por commits de merge
git log --all --merges --grep="copilot" --oneline

# Com números de PR
git log --all --merges --oneline | grep -i copilot
```

## Padrões Comuns de PR do Agente Copilot

### Exemplos Recentes do Repositório gh-aw

Com base na análise deste repositório, PRs do agente de codificação Copilot normalmente abordam:

1. **Refatoração e Organização de Código**
   - Exemplo: "Refatorar ALL_TOOLS para arquivo JSON separado com filtragem em tempo de execução"
   - Exemplo: "Eliminar lógica duplicada de renderização de tabela de ferramenta MCP"

2. **Melhorias de Documentação**
   - Exemplo: "Documentar áreas de aplicação de modo estrito e flag CLI no esquema"
   - Exemplo: "Adicionar documentação de referência abrangente de modo estrito"

3. **Correções de Bugs**
   - Exemplo: "Corrigir asserções de teste JavaScript para tratamento de erro loadAgentOutput"
   - Exemplo: "Remover função formatFileSize() duplicada"

4. **Melhorias de Teste**
   - Exemplo: "Adicionar testes de integração para configuração do Playwright MCP em todas as engines"

5. **Correções de Segurança**
   - Exemplo: "Corrigir risco de injeção de template no fluxo de trabalho copilot-session-insights"

### Metadados de PR para Verificar

Ao revisar PRs do agente de codificação Copilot, preste atenção em:
- **Nome da branch**: Deve seguir o padrão `copilot/descriptive-name`
- **Mensagens de commit**: Muitas vezes incluem commits de "Plano inicial"
- **Descrição do PR**: Deve explicar o problema e a solução
- **Issues vinculadas**: Podem referenciar issues sendo abordadas

## Dicas de Fluxo de Trabalho

### Encontrando PRs Relacionados

```bash
# Encontre PRs relacionados a uma funcionalidade específica
gh pr list --search "head:copilot/ refactor" --state all

# Encontre PRs em um intervalo de datas
gh pr list --search "head:copilot/ created:>=2024-01-01" --state all

# Encontre PRs com etiquetas específicas
gh pr list --search "head:copilot/ label:enhancement"
```

### Revisando PRs do Copilot

```bash
# Confira um PR copilot localmente
gh pr checkout <PR-number>

# Visualize diff do PR
gh pr diff <PR-number>

# Visualize detalhes do PR
gh pr view <PR-number>

# Visualize PR no navegador
gh pr view <PR-number> --web
```

### Rastreando Contribuições do Copilot

```bash
# Conte PRs copilot mesclados
gh pr list --author "app/github-copilot" --state merged --json number --jq 'length'

# Liste PRs copilot recentes com datas
gh pr list --author "app/github-copilot" --state all --limit 20 \
  --json number,title,createdAt,state \
  --jq '.[] | "\(.number): \(.title) (\(.state)) - \(.createdAt)"'

# Exporte para CSV para análise
gh pr list --author "app/github-copilot" --state all --limit 100 \
  --json number,title,createdAt,state,author \
  --jq -r '.[] | [.number, .title, .state, .createdAt] | @csv' > copilot-prs.csv
```

## Depuração

### Problemas de Autenticação

Se você vir prompts "gh auth login":
```bash
# Autentique com a CLI do GitHub
gh auth login

# Ou defina variável de ambiente de token
export GH_TOKEN="seu-token-github"
```

### Nenhum Resultado Encontrado

Se as pesquisas não retornarem resultados:
1. Verifique se você está no repositório correto
2. Verifique se o nome do autor está correto (tente `app/github-copilot` ou `github-copilot`)
3. Tente pesquisar por prefixo de branch: `gh pr list --search "head:copilot/"`
4. Verifique se os PRs existem: `git branch -r | grep copilot`

### Limites de Taxa (Rate Limiting)

Se você atingir os limites de taxa da API do GitHub:
```bash
# Verifique o status do limite de taxa
gh api rate_limit

# Use solicitações autenticadas (limites mais altos)
gh auth login
```

## Melhores Práticas

1. **Use pesquisa por prefixo de branch** quando a pesquisa por autor estiver indisponível
2. **Exporte listas de PR** regularmente para rastreamento e análise
3. **Revise o histórico de commits** para entender a abordagem de implementação do Copilot
4. **Procure por commits de "Plano inicial"** para ver o processo de planejamento do Copilot
5. **Verifique se os testes passam** antes de mesclar (merge) PRs do Copilot
6. **Revise implicações de segurança** especialmente para mudanças no fluxo de trabalho

## Recursos Adicionais

- Documentação da CLI do GitHub: https://cli.github.com/manual/
- Documentação do GitHub Copilot: https://docs.github.com/en/copilot
- Filtragem de branch Git: https://git-scm.com/docs/git-branch
- Processamento JSON jq: https://stedolan.github.io/jq/manual/
---
