---
title: Geração de Manifesto Dependabot
description: Geração automática de manifesto de dependência para rastrear dependências de runtime em fluxos de trabalho agentic, permitindo que o Dependabot detecte e atualize ferramentas obsoletas.
sidebar:
  order: 750
---

O comando `gh aw compile --dependabot` escaneia fluxos de trabalho em busca de ferramentas de runtime (`npx`, `pip install`, `go install`), gera manifestos de dependência (`package.json`, `requirements.txt`, `go.mod`) e configura o Dependabot para monitorar atualizações

## Uso

Execute `gh aw compile --dependabot` para compilar todos os fluxos de trabalho e gerar manifestos em `.github/workflows/`.

> [!IMPORTANT]
> Deve compilar **todos os fluxos de trabalho** - não pode ser usado com arquivos específicos ou flag `--dir`.

**Pré-requisitos**: Node.js/npm necessário para geração de `package-lock.json`. Manifestos Pip e Go geram sem ferramentas adicionais.

## Regra de ignorar `gh-aw-actions` gerenciada pelo compilador

`gh aw compile` sempre reconcilia a regra de ignorar gerenciada pelo compilador para `github/gh-aw-actions/**` quando seu repositório já tem um bloco de atualização `github-actions` em `.github/dependabot.yml` (isso não se limita a execuções `--dependabot`).

- Sem operação se `.github/dependabot.yml` não existir
- Sem operação se não houver bloco de atualização `package-ecosystem: github-actions`
- Preserva entradas `ignore` definidas pelo usuário

```yaml
updates:
  - package-ecosystem: github-actions
    directory: "/.github/workflows"
    schedule:
      interval: weekly
    ignore:
      - dependency-name: "github/gh-aw-actions/**" # Gerenciado por gh aw compile. Bloqueado na versão do compilador gh-aw; não atualizar.
      - dependency-name: "actions/checkout" # definido pelo usuário, preservado
```

## Arquivos Gerados

| Ecossistema | Manifesto | Arquivo de Lock |
|-----------|----------|-----------|
| **npm** | `package.json` | `package-lock.json` (via `npm install --package-lock-only`) |
| **pip** | `requirements.txt` | - |
| **Go** | `go.mod` | - |

Todos os ecossistemas atualizam `.github/dependabot.yml` com programações de atualização semanais. Configurações existentes são preservadas; apenas ecossistemas ausentes são adicionados.

## Manipulando PRs do Dependabot

> [!WARNING]
> **Nunca mescle PRs do Dependabot que apenas modificam arquivos de manifesto.** Essas alterações são sobrescritas na próxima compilação.

**Fluxo de trabalho correto**: Atualize arquivos `.md` fonte, então recompile para regenerar manifestos.

```bash
# Encontre fluxos de trabalho afetados
grep -r "@playwright/test@1.41.0" .github/workflows/*.md

# Edite arquivos .md de fluxo de trabalho (altere a versão)
# npx @playwright/test@1.41.0 → npx @playwright/test@1.42.0

# Regenerar manifestos
gh aw compile --dependabot

# Confirmar (Dependabot fecha automaticamente seu PR)
git add .github/workflows/
git commit -m "chore: update @playwright/test to 1.42.0"
git push
```

### Manipulando dependências transitivas (Servidores MCP)

Quando o Dependabot sinaliza dependências transitivas (ex: `@modelcontextprotocol/sdk`, `hono` de `@sentry/mcp-server`), atualize a **configuração MCP compartilhada** em vez disso:

```bash
# Localize a configuração MCP compartilhada (ex: .github/workflows/shared/mcp/sentry.md)
# Atualize a versão no array args:
# args: ["@sentry/mcp-server@0.27.0"] → args: ["@sentry/mcp-server@0.29.0"]

# Regenerar manifestos
gh aw compile --dependabot

# Regenerar package-lock.json para capturar atualizações de dependência transitiva
cd .github/workflows && npm install --package-lock-only

# Confirmar alterações
git add .github/workflows/
git commit -m "chore: update @sentry/mcp-server to 0.29.0"
git push
```

**Por quê?** O compilador gera `package.json` a partir das configurações do servidor MCP em arquivos de fluxo de trabalho. Editar `package.json` diretamente será sobrescrito na próxima compilação.

## Modelo de prompt do Agente de IA

```markdown
Um PR do Dependabot atualizou dependências em .github/workflows/.

Corrija o fluxo de trabalho:
1. Identifique quais arquivos .md referenciam a dependência obsoleta
2. Atualize as versões nos arquivos de fluxo de trabalho
3. Execute `gh aw compile --dependabot` para regenerar manifestos
4. Verifique se os manifestos correspondem ao PR do Dependabot
5. Confirme e envie (Dependabot fecha automaticamente)

PR afetado: [link]
Dependência atualizada: [nome@versão]
```

## Solução de problemas

| Problema | Solução |
|-------|----------|
| **package-lock.json não criado** | Instale Node.js/npm a partir de [nodejs.org](https://nodejs.org/) |
| **Dependência não detectada** | Evite variáveis de shell (`${TOOL}`); use nomes de pacote literais |
| **Dependabot não abrindo PRs** | Verifique se `.github/dependabot.yml` é um YAML válido e se os arquivos de manifesto existem |

## Documentação relacionada

- [Comandos CLI](/gh-aw/setup/cli/#compile) - Referência completa do comando de compilação
- [Processo de Compilação](/gh-aw/reference/compilation-process/) - Como a compilação funciona
- [Documentação do GitHub Dependabot](https://docs.github.com/en/code-security/dependabot) - Guia oficial do Dependabot
