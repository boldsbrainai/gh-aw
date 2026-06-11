---
title: Runners Auto-hospedados (Self-Hosted Runners)
description: Como configurar e executar fluxos de trabalho agênticos em runners auto-hospedados, ARC/Kubernetes e ambientes GHES.
---

Use o campo `runs-on` no frontmatter para direcionar um runner auto-hospedado em vez do padrão `ubuntu-latest`.

> [!NOTE]
> Os runners devem ser Linux com suporte a Docker. macOS e Windows não são suportados.
>
> Runners auto-hospedados devem permitir `sudo` para fluxos de trabalho agênticos. Este é um requisito para permitir que todos os recursos de segurança do GH-AW sejam habilitados. As necessidades técnicas específicas são:
>
> - O AWF (Agentic Workflow Firewall) aplica regras de `iptables` em nível de host à cadeia `DOCKER-USER` do kernel Linux para aplicar filtragem de rede de saída (egress) para todos os contêineres de agente na rede bridge do AWF. Este limite de segurança externo requer UID root.
>
> - O `iptables` em nível de contêiner, ACLs de proxy Squid e drop de capacidades adicionam defesa em profundidade adicional, mas não substituem a filtragem em nível de host.
>
Por esses motivos, um modo sem sudo não é suportado, incluindo configurações de ARC com `allowPrivilegeEscalation: false`.

## ARC com Docker-in-Docker (DinD)

Implantações do Actions Runner Controller (ARC) que usam um sidecar Docker-in-Docker dividem o contêiner runner e o contêiner daemon Docker em sistemas de arquivos separados, então montagens bind construídas da perspectiva do runner falham dentro do daemon.

`gh aw compile` emite uma sonda (probe) de tempo de execução nos fluxos de trabalho gerados que inspeciona `DOCKER_HOST` e anexa `--docker-host-path-prefix /tmp/gh-aw` à invocação do AWF quando o valor corresponde a `tcp://localhost:<port>` ou `tcp://127.0.0.1:<port>`. Nenhuma configuração em nível de fluxo de trabalho é necessária.

A sonda é limitada ao AWF `v0.25.43` ou mais recente. Fluxos de trabalho fixados em uma versão AWF mais antiga, ou executados em runners hospedados pelo GitHub (onde `DOCKER_HOST` não está definido ou aponta para um soquete Unix), não são afetados.

## Formatos runs-on

**String** — label de runner único:

```aw
---
on: issues
runs-on: self-hosted
---
```

**Array** — o runner deve ter *todos* os labels listados (AND lógico):

```aw
---
on: issues
runs-on: [self-hosted, linux, x64]
---
```

**Objeto** — grupo de runner nomeado, opcionalmente filtrado por labels:

```aw
---
on: issues
runs-on:
  group: my-runner-group
  labels: [linux, x64]
---
```

## Compartilhando configuração via importações

`runs-on` deve ser definido em cada fluxo de trabalho — não é mesclado a partir de importações. Outras configurações como `network` e `tools` podem ser compartilhadas:

```aw title=".github/workflows/shared/runner-config.md"
---
network:
  allowed:
    - defaults
    - private-registry.example.com
tools:
  bash: {}
---
```

```aw
---
on: issues
imports:
  - shared/runner-config.md
runs-on: [self-hosted, linux, x64]
---

Faça a triagem desta issue.
```

## Configurando o runner do job de detecção

Quando a [detecção de ameaças](/gh-aw/reference/threat-detection/) está habilitada, o job de detecção é executado no runner do job do agente por padrão. Substitua isso com `safe-outputs.threat-detection.runs-on`:

```aw
---
on: issues
runs-on: [self-hosted, linux, x64]
safe-outputs:
  create-issue: {}
  threat-detection:
    runs-on: ubuntu-latest
---
```

Isso é útil quando seu runner auto-hospedado não tem acesso à internet de saída para detecção de IA, ou quando você deseja executar o job de detecção em um runner mais barato.

## Configurando o runner do job de framework

Jobs de framework — ativação, pré-ativação, saídas seguras, desbloqueio, APM, update_cache_memory e push_repo_memory — usam `ubuntu-slim` por padrão. Use `runs-on-slim:` para substituir todos eles de uma só vez:

```aw
---
on: issues
runs-on: [self-hosted, linux, x64]
runs-on-slim: self-hosted
safe-outputs:
  create-issue: {}
---
```

> [!NOTE]
> `runs-on` controla apenas o job principal do agente. `runs-on-slim` controla todos os jobs de framework/gerados. `safe-outputs.runs-on` ainda tem precedência sobre `runs-on-slim` especificamente para jobs de safe-output.

## Configurando o runner do fluxo de trabalho de manutenção

O fluxo de trabalho gerado `agentics-maintenance.yml` usa `ubuntu-slim` como padrão para todos os seus jobs. Para usar um runner auto-hospedado para jobs de manutenção, defina `runs_on` em `.github/workflows/aw.json`:

**Label único:**

```json
{
  "maintenance": {
    "runs_on": "self-hosted"
  }
}
```

**Múltiplos labels** (o runner deve corresponder a todos):

```json
{
  "maintenance": {
    "runs_on": ["self-hosted", "linux", "x64"]
  }
}
```

Essa configuração se aplica a cada job em `agentics-maintenance.yml` (close-expired-entities, cleanup-cache-memory, run_operation, apply_safe_outputs, create_labels, validate_workflows e activity_report). Execute novamente `gh aw compile` após alterar `aw.json` para regenerar o fluxo de trabalho.

> [!NOTE]
> `aw.json` é separado do frontmatter do fluxo de trabalho individual. Ele fornece configurações em nível de repositório para fluxos de trabalho de infraestrutura gerados.

## Documentação relacionada

- [Frontmatter](/gh-aw/reference/frontmatter/#run-configuration-run-name-runs-on-runs-on-slim-timeout-minutes) — referência de sintaxe para `runs-on` e `runs-on-slim`
- [Importações](/gh-aw/reference/imports/) — campos importáveis e semântica de merge
- [Detecção de Ameaças](/gh-aw/reference/threat-detection/) — configuração do job de detecção
- [Acesso à Rede](/gh-aw/reference/network/) — configurando permissões de rede de saída
- [Sandbox](/gh-aw/reference/sandbox/) — requisitos de contêiner e Docker
- [Efêmeros](/gh-aw/reference/ephemerals/#maintenance-configuration) — referência completa de configuração de manutenção em `aw.json`
- [Configuração Empresarial](/gh-aw/reference/enterprise-configuration/) — endpoints de API personalizados para GHEC/GHES

## Requisitos de ambiente do runner

Os runners auto-hospedados devem atender a estes requisitos para que os fluxos de trabalho agênticos sejam executados de forma confiável.

### Docker

Um daemon Docker funcional é necessário. O gateway MCP e o sandbox são executados como contêineres.

- **Soquete Unix**: O Docker deve estar acessível via soquete Unix (geralmente `/var/run/docker.sock`). Se `DOCKER_HOST` não estiver definido, o gateway monta `/var/run/docker.sock`. Se `DOCKER_HOST` for `unix://...` ou um caminho absoluto puro, o gateway monta esse caminho de soquete. Outros esquemas (por exemplo `tcp://...`) são ignorados para montagens e retornam ao padrão `/var/run/docker.sock`.
- **Grupo Docker**: O usuário do runner deve estar no grupo `docker`, ou o soquete deve ser legível por todos.
- **ARC/Kubernetes**: Se estiver usando [actions-runner-controller](https://github.com/actions/actions-runner-controller) com Docker-in-Docker (dind), o sidecar dind deve compartilhar o soquete Docker via volume `emptyDir`. O gateway tentará verificar o soquete por até 10 segundos para lidar com condições de corrida na inicialização.

### Sistema de Arquivos

- **Use `RUNNER_TEMP` para estado transiente.** Coloque o estado do sandbox, downloads de ferramentas e saídas intermediárias em `$RUNNER_TEMP`, que é limpo entre jobs. Em runners compartilhados, evite gravar dados de fluxo de trabalho arbitrários em `/tmp` porque podem persistir entre jobs. O prefixo `/tmp/gh-aw` é reservado para a reescrita de caminho do AWF ARC DinD. `actions/setup` redefine `/tmp/gh-aw` no início do job, e a política de limpeza `/tmp` normal do seu runner deve lidar com dados obsoletos de jobs interrompidos.
- **Sem suposição de root ou sudo.** O usuário do runner pode não ter acesso root ou `sudo` (exceto para a configuração inicial de iptables, que requer `sudo`). Instalações de ferramentas, operações de arquivo e configuração de sandbox devem funcionar como o usuário runner sem privilégios.
- **Sem instalações globais.** Não instale pacotes em `/usr/local/`, `/opt/hostedtoolcache/` ou outros caminhos de todo o sistema. Eles podem ser somente leitura, compartilhados entre runners ou montados como somente leitura dentro do sandbox. Use locais graváveis delimitados por job em vez disso.
- **Sem caminhos `HOME` codificados.** O diretório home do runner pode não ser `/home/runner`. Use `$HOME` ou `$RUNNER_TEMP` em vez de caminhos codificados.

### Limpeza pós-job

Runners auto-hospedados persistem entre jobs. Fluxos de trabalho agênticos devem se limpar:

- Arquivos gravados em `$RUNNER_TEMP` são limpos automaticamente.
- Contêineres Docker na bridge `awf-net` são parados e removidos pelo teardown do sandbox.
- Se seu fluxo de trabalho criar arquivos fora de `$RUNNER_TEMP` (ex: em `$GITHUB_WORKSPACE`), a limpeza de workspace integrada do runner lidará com isso.

### Rede

Runners auto-hospedados precisam de acesso HTTPS de saída para:

- `api.githubcopilot.com` (ou seu endpoint Copilot empresarial)
- `github.com` (ou sua instância GHES)
- `ghcr.io` (para baixar a imagem do contêiner do gateway MCP)
- Quaisquer domínios listados na configuração `network.allowed` do seu fluxo de trabalho

## GHES (GitHub Enterprise Server)

Fluxos de trabalho agênticos podem ser executados no GHES com alguma configuração adicional.

### Compatibilidade de artefatos

O GHES não suporta o backend `@actions/artifact` v2.0.0+ usado por `upload-artifact@v4+` e `download-artifact@v4+`. Fluxos de trabalho compilados usam as versões de ação de artefato mais recentes por padrão, que falham no GHES com `GHESNotSupportedError`.

Habilite o modo de compatibilidade GHES em `.github/workflows/aw.json` para usar ações de artefato compatíveis v3.x:

```json
{
  "ghes": true
}
```

Ou compile com `--ghes` para geração de fluxo de trabalho única:

```bash
gh aw compile --ghes my-workflow.md
```

Isso faz com que o compilador emita `upload-artifact@v3.2.2` e `download-artifact@v3.1.0` em vez das versões mais recentes, que são compatíveis com todas as versões do GHES.

### Endpoint da API

Instâncias GHES precisam da configuração de motor `api-target`. Veja [Configuração Empresarial](/gh-aw/reference/enterprise-configuration/) para instruções completas de configuração.

```aw
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

## ARC (Actions Runner Controller)

Ao executar no [ARC](https://github.com/actions/actions-runner-controller) com Kubernetes:

### Sidecar Docker-in-Docker (dind)

O padrão dind do ARC padrão com um `emptyDir` compartilhado para o soquete Docker é suportado. O gateway MCP:

1. Resolve o caminho do soquete Docker a partir de `DOCKER_HOST` (suporta caminhos `unix://` e caminhos absolutos puros)
2. Detecta automaticamente o ID do grupo do soquete para permissões corretas
3. Tenta verificar o soquete por até 10 segundos para lidar com a condição de corrida em que o gateway inicia antes do `dockerd`

### Segurança de Pod

O pod do runner requer `privileged: true` tanto no sidecar dind quanto no contêiner runner. Isso é necessário para:

- `dockerd` no sidecar dind
- Regras de `iptables` para o firewall de fluxo de trabalho agêntico
- Configuração de chroot/sandbox no contêiner runner
