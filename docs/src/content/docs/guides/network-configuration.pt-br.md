---
title: Guia de Configuração de Rede
description: Configurações de rede comuns para registros de pacotes, CDNs e ferramentas de desenvolvimento
sidebar:
  order: 450
---

Este guia fornece exemplos práticos para configurar o acesso à rede nos Fluxos de Trabalho Agênticos do GitHub enquanto mantém a segurança.

## Quick Start

Configure o acesso à rede adicionando identificadores de ecossistema à lista `network.allowed`. Sempre inclua `defaults` para a infraestrutura básica:

```yaml
network:
  allowed:
    - defaults      # Obrigatório: Infraestrutura básica
    - python        # PyPI, conda (para projetos Python)
    - node          # npm, yarn, pnpm (para projetos Node.js)
    - go            # Proxy de módulos Go (para projetos Go)
    - containers    # Docker Hub, GHCR (para projetos de contêiner)
```

## Ecossistemas Disponíveis

| Ecossistema | Inclui | Use Para |
|-----------|----------|---------|
| `defaults` | Certificados, esquema JSON, espelhos Ubuntu | Todos os fluxos de trabalho (obrigatório) |
| `python` | PyPI, conda, pythonhosted.org | Pacotes Python |
| `python-native` | PyPI, conda, pythonhosted.org + crates.io | Pacotes Python com extensões nativas (pyo3/maturin) |
| `node` | npm, yarn, pnpm, Node.js | JavaScript/TypeScript |
| `go` | proxy.golang.org, sum.golang.org | Módulos Go |
| `containers` | Docker Hub, GHCR, Quay, GCR, MCR | Imagens de contêiner |
| `java` | Maven, Gradle | Dependências Java |
| `dotnet` | NuGet | Pacotes .NET |
| `julia` | pkg.julialang.org, storage.julialang.net | Pacotes Julia |
| `ruby` | RubyGems, Bundler | Gems Ruby |
| `rust` | crates.io | Crates Rust |
| `github` | githubusercontent.com | Recursos do GitHub |
| `terraform` | HashiCorp registry | Módulos Terraform |
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

# Automação DevOps
network:
  allowed:
    - defaults
    - terraform
    - containers
    - github
```

## Domínios Personalizados

Adicione domínios específicos para seus serviços. Tanto domínios base quanto padrões curinga (wildcards) são suportados:

```yaml
network:
  allowed:
    - defaults
    - python
    - "api.example.com"        # Corresponde a api.example.com e subdomínios
    - "*.cdn.example.com"      # Curinga: corresponde a qualquer subdomínio de cdn.example.com
```

**Comportamento do padrão curinga:**

- `*.example.com` corresponde a `sub.example.com`, `deep.nested.example.com` e `example.com`
- Apenas curingas simples no início são suportados (ex: `*.*.example.com` é inválido)

> [!TIP]
> Tanto `example.com` quanto `*.example.com` correspondem a subdomínios. Use curingas quando quiser documentar explicitamente que o acesso a subdomínios é esperado.

## Filtragem Específica por Protocolo

Restrinja domínios a protocolos específicos para maior segurança (motor Copilot com firewall AWF):

```yaml
engine: copilot
network:
  allowed:
    - defaults
    - "https://secure.api.example.com"   # Apenas HTTPS
    - "http://legacy.internal.com"       # Apenas HTTP
    - "example.org"                      # Ambos os protocolos (padrão)
sandbox:
  agent: awf  # Firewall habilitado
```

**Validação:** Protocolos inválidos (ex: `ftp://`) são rejeitados em tempo de compilação.

Veja [Permissões de Rede - Filtragem Específica por Protocolo](/gh-aw/reference/network/#protocol-specific-domain-filtering) para detalhes completos.

## Modo Estrito e Identificadores de Ecossistema

Os fluxos de trabalho usam [modo estrito](/gh-aw/reference/frontmatter/#strict-mode-strict) por padrão, o que impõe identificadores de ecossistema em vez de domínios individuais por segurança. Isso se aplica a todos os motores.

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
error: strict mode: network domains must be from known ecosystems (e.g., 'defaults',
'python', 'node') for all engines in strict mode. Custom domains are not allowed for
security. Did you mean: 'pypi.org' belongs to ecosystem 'python'?
````

Quando o modo estrito rejeita um domínio personalizado:

````text
error: strict mode: network domains must be from known ecosystems (e.g., 'defaults',
'python', 'node') for all engines in strict mode. Custom domains are not allowed for
security. Set 'strict: false' to use custom domains.
````

### Usando Domínios Personalizados

Para usar domínios personalizados (domínios que não estão em ecossistemas conhecidos), desabilite o modo estrito:

````yaml
---
strict: false    # Necessário para domínios personalizados
network:
  allowed:
    - python           # Identificador de ecossistema
    - "api.example.com"  # Domínio personalizado (permitido apenas com strict: false)
---
````

**Nota de Segurança**: Domínios personalizados ignoram a validação de ecossistema. Desabilite o modo estrito apenas quando necessário e certifique-se de que você confia nos domínios personalizados que permitir.

## Melhores Práticas de Segurança

1. **Comece com o mínimo** - Adicione apenas ecossistemas que você realmente usa
2. **Use identificadores de ecossistema** - Não liste domínios individuais (use `python` em vez de `pypi.org`, `files.pythonhosted.org`, etc.)
3. **Mantenha o modo estrito habilitado** - Fornece validação de segurança aprimorada (habilitado por padrão)
4. **Adicione incrementalmente** - Comece com `defaults`, adicione ecossistemas conforme necessário com base em negações de firewall

## Solução de Problemas de Bloqueio de Firewall

Veja a atividade do firewall com `gh aw logs --run-id <run-id>` para identificar domínios bloqueados:

```text
🔥 Firewall Log Analysis
Blocked Domains:
  ✗ registry.npmjs.org:443 (3 requests) → Adicione o ecossistema `node`
  ✗ pypi.org:443 (2 requests) → Adicione o ecossistema `python`
```

Mapeamentos comuns: npm/Node.js → `node`, PyPI/Python → `python`, Docker → `containers`, Módulos Go → `go`.

## Opções Avançadas

Desabilite todo o acesso à rede externa (a comunicação do motor ainda é permitida):

```yaml
network: {}
```

Veja listas completas de domínios de ecossistema no [código-fonte de domínios de ecossistema](https://github.com/github/gh-aw/blob/main/pkg/workflow/data/ecosystem_domains.json).

## Documentação relacionada

- [Referência de Permissões de Rede](/gh-aw/reference/network/) - Referência completa de configuração de rede
- [Referência de Playwright](/gh-aw/reference/playwright/) - Requisitos de rede e automação de navegador
- [Guia de Segurança](/gh-aw/introduction/architecture/) - Melhores práticas de segurança
- [Solução de Problemas](/gh-aw/troubleshooting/common-issues/) - Problemas comuns e soluções
