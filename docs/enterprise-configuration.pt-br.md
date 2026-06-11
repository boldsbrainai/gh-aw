# Configuração de Endpoint de API Personalizado

Este guia explica como configurar os GitHub Agentic Workflows para usar endpoints de API personalizados para o GitHub Enterprise Cloud (GHEC), GitHub Enterprise Server (GHES) ou endpoints de IA personalizados.

## Visão Geral

Os GitHub Agentic Workflows suportam endpoints de API personalizados através do campo de configuração `engine.api-target`. Isso permite que você especifique endpoints personalizados para:

- **GitHub Enterprise Cloud (GHEC)** - Endpoints de API do Copilot específicos do locatário (tenant)
- **GitHub Enterprise Server (GHES)** - Endpoints de API do Copilot corporativos
- **Endpoints de IA Personalizados** - Endpoints personalizados compatíveis com OpenAI ou Anthropic

## Configuração

Para configurar um endpoint de API personalizado, adicione o campo `api-target` à configuração do seu engine:

**Configuração Básica:**

```yaml
---
engine:
  id: copilot
  api-target: api.acme.ghe.com
network:
  allowed:
    - defaults
    - acme.ghe.com
    - api.acme.ghe.com
---
```

O campo `api-target` aceita um hostname (sem protocolo ou caminho) e funciona com qualquer engine agentic.

## Exemplos

### GitHub Enterprise Cloud (GHEC)

Para locatários (tenants) GHEC (domínios terminando em `.ghe.com`), especifique seu endpoint de API específico do locatário:

**Configuração do Fluxo de Trabalho (Workflow):**

```yaml
---
engine:
  id: copilot
  api-target: api.acme.ghe.com
network:
  allowed:
    - defaults
    - acme.ghe.com
    - api.acme.ghe.com
---
```

**Domínios necessários na lista de permissões (allowlist) de rede:**
- `acme.ghe.com` - O domínio do seu locatário GHEC (operações git, interface web)
- `api.acme.ghe.com` - Seu endpoint de API do Copilot específico do locatário
- `raw.githubusercontent.com` - Acesso a conteúdo bruto (se estiver usando o servidor MCP do GitHub)

### GitHub Enterprise Server (GHES)

Para instâncias GHES (domínios personalizados), especifique o endpoint corporativo do Copilot:

**Configuração do Fluxo de Trabalho (Workflow):**

```yaml
---
engine:
  id: copilot
  api-target: api.enterprise.githubcopilot.com
network:
  allowed:
    - defaults
    - github.company.com
    - api.enterprise.githubcopilot.com
---
```

**Domínios necessários na lista de permissões (allowlist) de rede:**
- `github.company.com` - Sua instância GHES (operações git, interface web)
- `api.enterprise.githubcopilot.com` - Endpoint de API do Copilot corporativo (usado para todas as instâncias GHES)

### Endpoints de IA Personalizados

O campo `api-target` funciona com qualquer engine agentic, permitindo que você use endpoints de IA personalizados:

**Configuração do Fluxo de Trabalho (Workflow):**

```yaml
---
engine:
  id: codex
  api-target: api.custom.ai-provider.com
network:
  allowed:
    - defaults
    - api.custom.ai-provider.com
---
```

## Exemplos Completos

### GHEC com Servidor MCP do GitHub

```yaml
---
description: Workflow para ambiente GHEC com acesso à API do GitHub
on:
  workflow_dispatch:
permissions:
  contents: read
engine:
  id: copilot
  api-target: api.acme.ghe.com
tools:
  github:
    mode: remote
    toolsets: [default]
network:
  allowed:
    - defaults
    - acme.ghe.com
    - api.acme.ghe.com
    - raw.githubusercontent.com
---

# Seu prompt de workflow aqui
```

### GHES com Endpoint Personalizado

```yaml
---
description: Workflow para ambiente GHES
on:
  issue_comment:
    types: [created]
permissions:
  contents: read
engine:
  id: copilot
  api-target: api.enterprise.githubcopilot.com
network:
  allowed:
    - defaults
    - github.company.com
    - api.enterprise.githubcopilot.com
---

# Seu prompt de workflow aqui
```

### Provedor de IA Personalizado

```yaml
---
description: Workflow com endpoint de IA personalizado
on:
  workflow_dispatch:
permissions:
  contents: read
engine:
  id: codex
  api-target: api.custom.ai-provider.com
network:
  allowed:
    - defaults
    - api.custom.ai-provider.com
---

# Seu prompt de workflow aqui
```

## Verificação

Para verificar se sua configuração está funcionando corretamente:

### 1. Verifique o Fluxo de Trabalho Compilado

Após compilar seu workflow, verifique o arquivo `.lock.yml` gerado:

```bash
gh aw compile seu-workflow.md
```

Procure por:
- Flag `--copilot-api-target` no comando AWF (se estiver usando o engine Copilot)
- Hostname do endpoint de API correto no valor da flag

### 2. Verifique as Execuções do Fluxo de Trabalho

Nas execuções de workflow do GitHub Actions:
1. Vá para o job do agente.
2. Verifique a etapa "Run Copilot Agent" (ou equivalente).
3. Verifique se o comando AWF inclui o alvo de API correto.
4. Verifique os logs do AWF para mensagens de conexão de API.

## Solução de Problemas (Troubleshooting)

### Endpoint de API Errado

**Problema:** O tráfego está indo para o endpoint de API errado.

**Soluções:**
1. Verifique se `engine.api-target` está definido corretamente no frontmatter do seu workflow.
2. Verifique se o domínio está na sua lista `network.allowed`.
3. Revise os logs do AWF na execução do workflow para mensagens de configuração de endpoint.
4. Certifique-se de que não está usando uma URL completa (use apenas o hostname: `api.acme.ghe.com` e não `https://api.acme.ghe.com`).

### Domínio Não Autorizado (Not Whitelisted)

**Problema:** As solicitações são bloqueadas com erros de rede.

**Solução:** Adicione o domínio ausente à sua lista `network.allowed`:
- Para GHEC: `[acme.ghe.com, api.acme.ghe.com]`
- Para GHES: `[github.company.com, api.enterprise.githubcopilot.com]`
- Para IA personalizada: `[api.custom.ai-provider.com]`

### Problemas com o Servidor MCP do GitHub

**Problema:** O servidor MCP do GitHub falha ao conectar-se à sua instância corporativa.

**Soluções:**
1. Certifique-se de que seu domínio GHEC/GHES está em `network.allowed`.
2. Verifique se o token do GitHub possui escopos apropriados para o seu locatário corporativo.
3. Use `mode: remote` para o servidor MCP do GitHub quando estiver no GHEC/GHES.

## Compatibilidade de Artefatos no GHES

O GitHub Enterprise Server (GHES) não suporta `@actions/artifact` v2.0.0+, o que significa que
`actions/upload-artifact@v4+` e `actions/download-artifact@v4+` falham com um erro
`GHESNotSupportedError` em instâncias corporativas.

### Detecção Automática (Recomendado)

Ao executar `gh aw init` dentro de um repositório cujo remoto git aponta para uma instância GHES,
o CLI detecta automaticamente a implantação e escreve `ghes: true` em
`.github/workflows/aw.json`:

```bash
gh aw init
```

Saída:

```
GHES deployment detected (ghes.example.com): set ghes: true in .github/workflows/aw.json for artifact compatibility
```

### Configuração Manual

**Opção 1: aw.json (padrão para todo o repositório)**

Adicione `ghes: true` ao `.github/workflows/aw.json` para habilitar a compatibilidade com GHES para todos
os workflows compilados no repositório:

```json
{
  "ghes": true
}
```

**Opção 2: Flag de compilação --ghes**

Passe `--ghes` para `gh aw compile` para uma compilação única sem modificar o `aw.json`:

```bash
gh aw compile --ghes meu-workflow.md
```

A flag do CLI tem precedência sobre a configuração do `aw.json`.

### O Que Muda

Quando o modo de compatibilidade com GHES está ativo, o compilador emite:

| Action | Padrão | Compatível com GHES |
|--------|---------|-----------------|
| `actions/upload-artifact` | `@v7` (mais recente) | `@v3.2.2` |
| `actions/download-artifact` | `@v4` (mais recente) | `@v3.1.0` |

Todas as outras ações não são afetadas.

## Documentação Relacionada

- [Configuração de Firewall do AWF](https://github.com/github/gh-aw-firewall) - Documentação detalhada do AWF
- [Variáveis de Ambiente do GitHub Actions](https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables) - Variáveis padrão do GitHub Actions
- [Permissões de Rede](network.md) - Configuração de acesso à rede
- [Configuração de Ferramentas](tools.md) - Configuração de servidor MCP e ferramentas
