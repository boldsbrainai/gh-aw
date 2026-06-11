---
emoji: "🔢"
description: Monitora e atualiza ferramentas CLI agentic (Claude Code, GitHub Copilot CLI, OpenAI Codex, GitHub MCP Server, Playwright MCP, Playwright CLI, Playwright Browser, MCP Gateway) para novas versões
on:
  schedule: diário
  workflow_dispatch:
permissions:
  contents: read
  pull-requests: read
  issues: read
strict: false
engine: claude
network: 
   allowed: [padrões, node, go, "api.github.com", "ghcr.io"]
imports:
  - ../skills/jqschema/SKILL.md
  - shared/reporting.md
  - shared/otlp.md
tools:
  cli-proxy: true
  web-fetch:
  cache-memory: true
  bash:
    - "*"
  edit:
safe-outputs:
  create-issue:
    expires: 2d
    title-prefix: "[ca] "
    labels: [automation, dependencies, cookie]
    close-older-issues: true
timeout-minutes: 45

---

# Verificador de Versão da CLI (CLI Version Checker)

Monitore e atualize ferramentas CLI agentic: Claude Code, GitHub Copilot CLI, OpenAI Codex, GitHub MCP Server, Playwright MCP, Playwright CLI, Playwright Browser e MCP Gateway.

**Repositório**: ${{ github.repository }} | **Execução**: ${{ github.run_id }}

## Processo

**EFICIÊNCIA EM PRIMEIRO LUGAR**: Antes de começar:
1. Verifique a memória cache em `/tmp/gh-aw/cache-memory/` para verificações de versão anteriores e saídas de ajuda
2. Se as versões em cache existirem e forem recentes (< 24h), verifique se as atualizações são necessárias antes de prosseguir
3. Se nenhuma mudança de versão for detectada, saia antecipadamente com sucesso

**CRÍTICO**: Se ALGUMA mudança de versão for detectada, você DEVE criar uma issue usando `safe-outputs.create-issue`. Não pule a criação da issue, mesmo para pequenas atualizações.

Para cada ferramenta CLI/servidor MCP:
1. Busque a versão mais recente no registro NPM ou nas releases do GitHub (use comandos `npm view` para metadados do pacote)
2. Compare com a versão atual em `./pkg/constants/constants.go`
3. Se existir uma versão mais nova, pesquise as mudanças e prepare a atualização

### Fontes de Versão
- **Claude Code**: Use `npm view @anthropic-ai/claude-code version` (mais rápido que web-fetch)
  - Sem repositório GitHub público
- **Copilot CLI**: Use `npm view @github/copilot version`
  - Repositório: https://github.com/github/copilot-cli
  - **CRÍTICO**: Sempre tente buscar e analisar profundamente o conteúdo do repositório Copilot
  - Notas de Lançamento: https://github.com/github/copilot-cli/releases
  - Changelog: https://github.com/github/copilot-cli/blob/main/CHANGELOG.md (ou similar)
  - README: https://github.com/github/copilot-cli/blob/main/README.md
- **Codex**: Use `npm view @openai/codex version`
  - Repositório: https://github.com/openai/codex
  - Notas de Lançamento: https://github.com/openai/codex/releases
- **GitHub MCP Server**: `https://api.github.com/repos/github/github-mcp-server/releases/latest`
  - Notas de Lançamento: https://github.com/github/github-mcp-server/releases
- **Playwright MCP**: Use `npm view @playwright/mcp version`
  - Repositório: https://github.com/microsoft/playwright
  - Pacote: https://www.npmjs.com/package/@playwright/mcp
- **Playwright CLI**: Use `npm view @playwright/cli version`
  - Repositório: https://github.com/microsoft/playwright-cli
  - Pacote: https://www.npmjs.com/package/@playwright/cli
- **Playwright Browser**: `https://api.github.com/repos/microsoft/playwright/releases/latest`
  - Notas de Lançamento: https://github.com/microsoft/playwright/releases
  - Imagem Docker: `mcr.microsoft.com/playwright:v{VERSION}`
- **MCP Gateway**: `https://api.github.com/repos/github/gh-aw-mcpg/releases/latest`
  - Repositório: https://github.com/github/gh-aw-mcpg
  - Notas de Lançamento: https://github.com/github/gh-aw-mcpg/releases
  - Imagem Docker: `ghcr.io/github/gh-aw-mcpg:v{VERSION}`
  - Usado como container padrão sandbox.agent (veja `pkg/constants/constants.go`)
**Otimização**: Busque todas as versões em paralelo usando múltiplos comandos `npm view` ou chamadas `WebFetch` em um único turno.

### Pesquisa e Análise
Para cada atualização, analise versões intermediárias:
- Categorize as mudanças: Quebra de compatibilidade (Breaking), Funcionalidades (Features), Correções (Fixes), Segurança (Security), Desempenho (Performance)
- Avalie o impacto nos fluxos de trabalho do gh-aw
- Documente os requisitos de migração
- Atribua nível de risco (Baixo/Médio/Alto)

**Notas de Lançamento do GitHub (quando disponíveis)**:
- **Codex**: Busque notas de lançamento em https://github.com/openai/codex/releases/tag/rust-v{VERSION}
  - Analise a seção "Destaques" para mudanças principais
  - Analise a seção "PRs mesclados" ou "PRs mesclados" para mudanças detalhadas
  - **CRÍTICO**: Converta referências de PR/issue (ex: `#6211`) para URLs completas, pois referem-se a repositórios externos (ex: `https://github.com/openai/codex/pull/6211`)
- **GitHub MCP Server**: Busque notas de lançamento em https://github.com/github/github-mcp-server/releases/tag/v{VERSION}
  - Analise o corpo da release para entradas de changelog
  - **CRÍTICO**: Converta referências de PR/issue (ex: `#1105`) para URLs completas, pois referem-se a repositórios externos (ex: `https://github.com/github/github-mcp-server/pull/1105`)
- **Playwright Browser**: Busque notas de lançamento em https://github.com/microsoft/playwright/releases/tag/v{VERSION}
  - Analise o corpo da release para entradas de changelog
  - **CRÍTICO**: Converta referências de PR/issue para URLs completas (ex: `https://github.com/microsoft/playwright/pull/12345`)
- **Copilot CLI**: **SEMPRE tente uma análise profunda** - Repositório: https://github.com/github/copilot-cli
  - **CRÍTICO**: Leia e analise minuciosamente toda a documentação disponível:
    1. **Notas de Lançamento**: Busque em https://github.com/github/copilot-cli/releases/tag/v{VERSION}
       - Analise os destaques da release e descrições de funcionalidades
       - Extraia mudanças que quebram a compatibilidade e avisos de depreciação
       - Observe novos comandos, flags e opções de configuração
    2. **CHANGELOG.md**: Leia em https://github.com/github/copilot-cli/blob/main/CHANGELOG.md (ou equivalente)
       - Compare versões para identificar todas as mudanças entre a versão atual e a nova
       - Categorize as mudanças: Quebra de compatibilidade, Funcionalidades, Correções, Segurança, Desempenho
    3. **README.md**: Revise https://github.com/github/copilot-cli/blob/main/README.md
       - Verifique padrões de uso atualizados e exemplos
       - Observe novas capacidades ou opções de configuração
    4. **Mudanças na Documentação**: Procure por mudanças em arquivos de documentação que indiquem novas funcionalidades
  - Se o repositório estiver inacessível (repositório privado), documente a limitação de acesso na issue, mas ainda assim:
    - Use `npm view @github/copilot --json` para metadados detalhados do pacote
    - Compare a saída de ajuda da CLI entre as versões (veja a seção "Instalação e Descoberta de Ferramentas" abaixo)
    - Verifique quaisquer anúncios de lançamento ou postagens de blog publicamente disponíveis
  - **CRÍTICO**: Converta referências de PR/issue para URLs completas (ex: `https://github.com/github/copilot-cli/pull/123`)
- **Claude Code**: Sem repositório público, confie nos metadados do NPM e na saída de ajuda da CLI
- **Playwright MCP**: Verifique metadados do pacote NPM, usa versionamento do Playwright
- **Playwright CLI**: Verifique metadados do pacote NPM e releases do GitHub para mudanças
  - Busque notas de lançamento em https://github.com/microsoft/playwright-cli/releases/tag/v{VERSION}
  - **CRÍTICO**: Converta referências de PR/issue para URLs completas (ex: `https://github.com/microsoft/playwright-cli/pull/123`)
- **MCP Gateway**: Busque notas de lançamento em https://github.com/github/gh-aw-mcpg/releases/tag/{VERSION}
  - Analise o corpo da release para entradas de changelog
  - **CRÍTICO**: Converta referências de PR/issue para URLs completas (ex: `https://github.com/github/gh-aw-mcpg/pull/123`)
  - Nota: Usado como container padrão sandbox.agent na configuração do MCP Gateway
**Fallback de Metadados NPM**: Quando as notas de lançamento do GitHub não estiverem disponíveis, use:
- `npm view <pacote> --json` para metadados do pacote
- Compare as saídas de ajuda da CLI entre as versões
- Verifique o changelog da versão na descrição do pacote
- **CRÍTICO**: Converta referências de PR/issue para URLs completas

### Instalação e Descoberta de Ferramentas
**OTIMIZAÇÃO DE CACHE**: 
- Antes de instalar, verifique a memória cache para saídas de ajuda anteriores (principal e subcomandos)
- Apenas instale e execute `--help` se a versão tiver mudado
- Armazene saídas de ajuda principal em memória cache em `/tmp/gh-aw/cache-memory/[ferramenta]-[versão]-help.txt`
- Armazene saídas de ajuda de subcomando em memória cache em `/tmp/gh-aw/cache-memory/[ferramenta]-[versão]-[subcomando]-help.txt`

Para cada atualização de ferramenta CLI:
1. Instale a nova versão globalmente (pule se já instalado a partir da verificação de cache):
   - Claude Code: `npm install -g @anthropic-ai/claude-code@<versão>`
   - Copilot CLI: `npm install -g @github/copilot@<versão>`
   - Codex: `npm install -g @openai/codex@<versão>`
   - Playwright MCP: `npm install -g @playwright/mcp@<versão>`
   - Playwright CLI: `npm install -g @playwright/cli@<versão>`
2. Invoque a ajuda para descobrir comandos e flags (compare com a saída em cache se disponível):
   - Execute `claude-code --help`
   - Execute `copilot --help` ou `copilot help copilot`
   - Execute `codex --help`
   - Execute `npx @playwright/mcp@<versão> --help` (se disponível)
   - Execute `playwright-cli --help` (se disponível)
3. **Explore a ajuda de subcomando** para cada ferramenta (especialmente Copilot CLI):
   - Identifique todos os subcomandos disponíveis a partir da saída de ajuda principal
   - Para cada subcomando, execute seu comando de ajuda (ex: `copilot help config`, `copilot help environment`, `copilot config --help`)
   - Armazene cada saída de ajuda de subcomando em memória cache em `/tmp/gh-aw/cache-memory/[ferramenta]-[versão]-[subcomando]-help.txt`
   - **Subcomandos prioritários para Copilot CLI**: `config`, `environment` (solicitados explicitamente)
   - Exemplos de comandos:
     - `copilot help copilot`
     - `copilot help config` ou `copilot config --help`
     - `copilot help environment` ou `copilot environment --help`
4. Compare a saída de ajuda com a versão anterior para identificar:
   - Novos comandos ou subcomandos
   - Novas flags ou opções de linha de comando
   - Recursos depreciados ou removidos
   - Comportamentos padrão alterados
   - **NOVO**: Mudanças na funcionalidade ou flags de subcomando
5. Salve todas as saídas de ajuda (principal e subcomandos) em memória cache para execuções futuras

### Processo de Atualização
1. Edite `./pkg/constants/constants.go` com a(s) nova(s) versão(ões)
2. **OBRIGATÓRIO**: Execute `make recompile` para atualizar fluxos de trabalho (DEVE ser executado após quaisquer mudanças de constante)
3. Verifique as mudanças com `git status`
4. **OBRIGATÓRIO**: Crie uma issue via safe-outputs com análise detalhada (NÃO pule esta etapa)

## Formato da Issue

**Siga o Padrão de Estrutura de Relatório definido em `shared/reporting.md`.**

Para cada CLI atualizada, inclua:
- **Versão**: antiga → nova (liste versões intermediárias se houver múltiplas)
- **Linha do Tempo de Lançamento**: datas e intervalos
- **Mudanças**: Categorizadas como Breaking/Features/Fixes/Security/Performance
- **Avaliação de Impacto**: Nível de risco, recursos afetados, notas de migração
- **Links de Changelog**: Use URLs simples sem crases
- **Mudanças na CLI**: Novos comandos, flags ou recursos removidos descobertos via ajuda
- **Mudanças de Subcomando**: Mudanças na funcionalidade ou flags de subcomando (especialmente `config` e `environment` para Copilot CLI)
- **Notas de Lançamento do GitHub**: Inclua destaques e resumos de PR quando disponíveis nas releases do GitHub

**IMPORTANTE**: Use headers `###` ou menores para todos os headers. Envolva changelogs completos e guias de migração em tags `<details>` conforme mostrado no Padrão de Estrutura de Relatório.

**Regras de Formatação de URL**:
- Use URLs simples sem crases em volta dos nomes dos pacotes
- **CORRETO**: https://www.npmjs.com/package/@github/copilot
- **INCORRETO**: `https://www.npmjs.com/package/@github/copilot` (tem crases)
- **INCORRETO**: https://www.npmjs.com/package/`@github/copilot` (nome do pacote envolvido em crases)

**Formatação de Link de Pull Request**:
- **CRÍTICO**: Sempre use URLs completas para pull requests que se referem a repositórios externos
- **CORRETO**: https://github.com/openai/codex/pull/6211
- **INCORRETO**: #6211 (referência relativa só funciona para o mesmo repositório)
- Ao copiar referências de PR de notas de lançamento, converta `#1234` para URLs completas como `https://github.com/owner/repo/pull/1234`

## Diretrizes
- Apenas atualize versões estáveis (sem pré-lançamentos)
- Priorize atualizações de segurança
- Documente todas as versões intermediárias
- **USE COMANDOS NPM**: Use `npm view` em vez de web-fetch para consultas de metadados de pacotes
- **VERIFIQUE O CACHE PRIMEIRO**: Antes de reanalisar versões, verifique a memória cache para resultados recentes
- **BUSCA EM PARALELO**: Busque todas as versões em paralelo usando múltiplos comandos npm/WebFetch em um turno
- **SAÍDA ANTECIPADA**: Se nenhuma mudança de versão for detectada, salve o carimbo de data/hora da verificação no cache e saia com sucesso
- **BUSQUE NOTAS DE LANÇAMENTO DO GITHUB**: Para ferramentas com repositórios GitHub públicos, busque notas de lançamento para obter informações detalhadas do changelog
  - Codex: Sempre busque em https://github.com/openai/codex/releases
  - GitHub MCP Server: Sempre busque em https://github.com/github/github-mcp-server/releases
  - Playwright Browser: Sempre busque em https://github.com/microsoft/playwright/releases
  - MCP Gateway: Sempre busque em https://github.com/github/gh-aw-mcpg/releases
  - Copilot CLI: Tente buscar, mas pode estar inacessível (repositório privado)
  - Playwright MCP: Verifique metadados do pacote NPM, usa versionamento do Playwright
  - Playwright CLI: Busque em https://github.com/microsoft/playwright-cli/releases
- **EXPLORE SUBCOMANDOS**: Instale e teste ferramentas CLI para descobrir novos recursos via `--help` e explore cada subcomando
  - Para Copilot CLI, verifique explicitamente: `config`, `environment` e qualquer outro subcomando disponível
  - Use comandos como `copilot help <subcomando>` ou `<ferramenta> <subcomando> --help`
- Compare a saída de ajuda entre a versão antiga e a nova (tanto ajuda principal quanto ajuda de subcomando)
- **SALVE NO CACHE**: Armazene saídas de ajuda (principal e subcomandos) e resultados de verificação de versão em memória cache
- **OBRIGATÓRIO**: Sempre execute `make recompile` após atualizar constantes para regenerar arquivos de bloqueio de fluxo de trabalho
- **NÃO FAÇA COMMIT** de arquivos `*.lock.yml` ou `pkg/workflow/js/*.js` diretamente

## Problemas Comuns de Análise JSON

Ao usar comandos npm ou outras ferramentas CLI, sua saída pode incluir mensagens informativas com símbolos Unicode que quebram a análise JSON:

**Padrões de Problema**:
- `Unexpected token 'ℹ', "ℹ Timeout "... is not valid JSON`
- `Unexpected token '⚠', "⚠ pip pack"... is not valid JSON`
- `Unexpected token '✓', "✓ Success"... is not valid JSON`

**Soluções**:

### 1. Filtrar stderr (Recomendado)
Redirecione stderr para suprimir avisos/informações do npm:
```bash
npm view @github/copilot version 2>/dev/null
npm view @anthropic-ai/claude-code --json 2>/dev/null
```

### 2. Use grep para filtrar a saída
Remova linhas com símbolos Unicode antes de analisar:
```bash
npm view @github/copilot --json | grep -v "^[ℹ⚠✓]"
```

### 3. Use jq para extração confiável
Deixe o jq lidar com entrada malformada:
```bash
# Extraia apenas o campo de versão, ignorando linhas não-JSON
npm view @github/copilot --json 2>/dev/null | jq -r '.version'
```

### 4. Verifique a saída da ferramenta antes de analisar
Sempre valide JSON antes de tentar analisar:
```bash
output=$(npm view package --json 2>/dev/null)
if echo "$output" | jq empty 2>/dev/null; then
  # JSON válido, seguro para analisar
  version=$(echo "$output" | jq -r '.version')
else
  # JSON inválido, trate o erro
  echo "Aviso: a saída do npm não é JSON válido"
fi
```

**Melhor Prática**: Combine filtragem de stderr com extração jq para resultados mais confiáveis:
```bash
npm view @github/copilot --json 2>/dev/null | jq -r '.version'
```

## Tratamento de Erros
- **SALVE O PROGRESSO**: Antes de sair por erros, salve o estado atual na memória cache
- **RECOMECE APÓS REINICIAR**: Verifique a memória cache na inicialização para retomar de onde você parou
- Tente novamente falhas no registro NPM uma vez após 30s
- Continue se a busca de changelog individual falhar
- Pule a criação de PR se a recompilação falhar
- Saia com sucesso se nenhuma atualização for encontrada
- Documente pesquisas incompletas se limitado pela taxa (rate-limited)

{{#runtime-import shared/noop-reminder.md}}
