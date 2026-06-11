---
title: Guia de Configuração de Rede
description: Configurações de rede comuns para registros de pacotes, CDNs e ferramentas de desenvolvimento
sidebar:
  order: 450
---

Este guia fornece exemplos práticos para configurar o acesso à rede em GitHub Agentic Workflows enquanto mantém a segurança.

## Início Rápido

Configure o acesso à rede adicionando identificadores de ecossistema à lista `network.allowed`. Sempre inclua `defaults` para a infraestrutura básica:

```yaml
network:
  allowed:
    - defaults      # Obrigatório: Infraestrutura básica
    - python        # PyPI, conda (para projetos Python)
    - node          # npm, yarn, pnpm (para projetos Node.js)
    - go            # Proxy de módulo Go (para projetos Go)
    - containers    # Docker Hub, GHCR (para projetos de contêiner)
```

## Ecossistemas Disponíveis

| Ecossistema | Inclui | Use Para |
|-----------|----------|---------|
| `defaults` | Certificados, esquema JSON, espelhos do Ubuntu | Todos os fluxos de trabalho (obrigatório) |
| `python` | PyPI, conda, pythonhosted.org | Pacotes Python |
| `python-native` | PyPI, conda, pythonhosted.org + crates.io | Pacotes Python com extensões nativas (pyo3/maturin) |
| `node` | npm, yarn, pnpm, Node.js | JavaScript/TypeScript |
| `go` | proxy.golang.org, sum.golang.org | Módulos Go |
| `containers` | Docker Hub, GHCR, Quay, GCR, MCR | Imagens de contêiner |
| `java` | Maven, Gradle | Dependências Java |
| `dotnet` | NuGet | Pacotes .NET |
| `julia` | pkg.julialang.org, storage.julialang.net | Pacotes Julia |
| `ruby` | RubyGems, Bundler | Gemas Ruby |
| `rust` | crates.io | Crates Rust |
| `github` | githubusercontent.com | Recursos do GitHub |
| `terraform` | Registro HashiCorp | Módulos Terraform |
| `playwright` | Downloads de navegador | Testes web ([referência](/gh-aw/reference/playwright/)) |
| `linux-distros` | Debian, Ubuntu, Alpine | Pacotes Linux |

## Padrões de Configuração Comuns

```yaml
# Projeto Python com contêineres
network:
  allowed:
    - defaults
    - python
    - containers

# Desenvolvimento web full-stack
network:
  allowed:
    - defaults
    - node
    - playwright
    - github

# Automação de DevOps
network:
  allowed:
    - defaults
    - terraform
    - containers
    - github
```

## Domínios Personalizados

Adicione domínios específicos para seus serviços. Tanto domínios base quanto padrões de wildcard são suportados:

```yaml
network:
  allowed:
    - defaults
    - python
    - "api.exemplo.com"        # Corresponde a api.exemplo.com e subdomínios
    - "*.cdn.exemplo.com"      # Wildcard: corresponde a qualquer subdomínio de cdn.exemplo.com
```

**Comportamento do padrão wildcard:**

- `*.exemplo.com` corresponde a `sub.exemplo.com`, `profundo.aninhado.exemplo.com` e `exemplo.com`
- Apenas wildcards únicos no início são suportados (por exemplo, `*.*.exemplo.com` é inválido)

> [!TIP]
> Tanto `exemplo.com` quanto `*.exemplo.com` correspondem a subdomínios. Use wildcards quando quiser documentar explicitamente que o acesso a subdomínios é esperado.

## Filtragem Específica por Protocolo

Restrinja domínios a protocolos específicos para segurança aprimorada (engine Copilot com firewall AWF):

```yaml
engine: copilot
network:
  allowed:
    - defaults
    - "https://secure.api.exemplo.com"   # Apenas HTTPS
    - "http://legacy.interno.com"       # Apenas HTTP
    - "exemplo.org"                      # Ambos os protocolos (padrão)
sandbox:
  agent: awf  # Firewall habilitado
```

**Validação:** Protocolos inválidos (por exemplo, `ftp://`) são rejeitados em tempo de compilação.

Veja [Permissões de Rede - Filtragem Específica por Protocolo](/gh-aw/reference/network/#protocol-specific-domain-filtering) para detalhes completos.

## Modo Estrito e Identificadores de Ecossistema

Os fluxos de trabalho usam [modo estrito](/gh-aw/reference/frontmatter/#strict-mode-strict) por padrão, o que impõe identificadores de ecossistema em vez de domínios individuais para segurança. Isso se aplica a todas as engines.

````yaml
# ❌ Rejeitado no modo estrito
network:
  allowed:
    - "pypi.org"       # Erro: use o ecossistema 'python' em vez disso
    - "npmjs.org"      # Erro: use o ecossistema 'node' em vez disso

# ✅ Aceito no modo estrito
network:
  allowed:
    - python           # Identificador de ecossistema
    - node             # Identificador de ecossistema
````

### Mensagens de Erro

Quando o modo estrito rejeita um domínio que pertence a um ecossistema conhecido, a mensagem de erro sugere o identificador do ecossistema:

````text
erro: modo estrito: domínios de rede devem ser de ecossistemas conhecidos (ex: 'defaults',
'python', 'node') para todas as engines em modo estrito. Domínios personalizados não são
permitidos por segurança. Você quis dizer: 'pypi.org' pertence ao ecossistema 'python'?
````

Quando o modo estrito rejeita um domínio personalizado:

````text
erro: modo estrito: domínios de rede devem ser de ecossistemas conhecidos (ex: 'defaults',
'python', 'node') para todas as engines em modo estrito. Domínios personalizados não são
permitidos por segurança. Defina 'strict: false' para usar domínios personalizados.
````

### Usando Domínios Personalizados

Para usar domínios personalizados (domínios não pertencentes a ecossistemas conhecidos), desabilite o modo estrito:

````yaml
---
strict: false    # Necessário para domínios personalizados
network:
  allowed:
    - python           # Identificador de ecossistema
    - "api.exemplo.com"  # Domínio personalizado (permitido apenas com strict: false)
---
````

**Nota de Segurança**: Domínios personalizados contornam a validação de ecossistema. Apenas desabilite o modo estrito quando necessário e certifique-se de que você confia nos domínios personalizados que permite.

## Melhores Práticas de Segurança

1. **Comece de forma mínima** - Adicione apenas ecossistemas que você realmente usa
2. **Use identificadores de ecossistema** - Não liste domínios individuais (use `python` em vez de `pypi.org`, `files.pythonhosted.org`, etc.)
3. **Mantenha o modo estrito habilitado** - Fornece validação de segurança aprimorada (habilitado por padrão)
4. **Adicione incrementalmente** - Comece com `defaults`, adicione ecossistemas conforme necessário com base em negações de firewall

## Resolução de Problemas de Bloqueio de Firewall

Veja a atividade do firewall com `gh aw logs --run-id <run-id>` para identificar domínios bloqueados:

```text
🔥 Análise de Log de Firewall
Domínios Bloqueados:
  ✗ registry.npmjs.org:443 (3 solicitações) → Adicione ecossistema `node`
  ✗ pypi.org:443 (2 solicitações) → Adicione ecossistema `python`
```

Mapeamentos comuns: npm/Node.js → `node`, PyPI/Python → `python`, Docker → `containers`, Módulos Go → `go`.

## Opções Avançadas

Desabilite todo o acesso à rede externa (a comunicação da engine ainda é permitida):

```yaml
network: {}
```

Veja as listas completas de domínios de ecossistema na [fonte de domínios de ecossistema](https://github.com/github/gh-aw/blob/main/pkg/workflow/data/ecosystem_domains.json).

## Documentação Relacionada

- [Referência de Permissões de Rede](/gh-aw/reference/network/) - Referência completa de configuração de rede
- [Referência de Playwright](/gh-aw/reference/playwright/) - Automação de navegador e requisitos de rede
- [Guia de Segurança](/gh-aw/introduction/architecture/) - Melhores práticas de segurança
- [Resolução de Problemas](/gh-aw/troubleshooting/common-issues/) - Problemas comuns e soluções
