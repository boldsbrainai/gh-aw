---
title: Runners Auto-Hospedados (Self-Hosted)
description: Como configurar e executar fluxos de trabalho agenticos em runners auto-hospedados, ARC/Kubernetes e ambientes GHES.
---

Use o campo de frontmatter `runs-on` para direcionar um runner auto-hospedado em vez do padrão `ubuntu-latest`.

> [!NOTE]
> Runners devem ser Linux com suporte a Docker. macOS e Windows não são suportados.
>
> Runners auto-hospedados devem permitir `sudo` para fluxos de trabalho agenticos. Este é um requisito para permitir que todos os recursos de segurança do GH-AW sejam habilitados. As necessidades técnicas específicas são:
>
> - O AWF (Firewall de Fluxo de Trabalho Agentico) aplica regras de `iptables` em nível de host à cadeia `DOCKER-USER` do kernel Linux para impor a filtragem de egresso de rede para todos os contêineres de agente na rede bridge AWF. Este limite de segurança externo requer root UID.
>
> - `iptables` em nível de contêiner, ACLs de proxy Squid e drop de capabilities adicionam defesa em profundidade adicional, mas não substituem a filtragem em nível de host.
>
Por essas razões, um modo sem sudo não é suportado, incluindo configurações ARC com `allowPrivilegeEscalation: false`.

## ARC com Docker-in-Docker (DinD)

Implantações do Actions Runner Controller (ARC) que usam um sidecar Docker-in-Docker separam o contêiner do runner e o contêiner do daemon do Docker em sistemas de arquivos distintos, portanto, as montagens de bind construídas da perspectiva do runner falham dentro do daemon.

`gh aw compile` emite uma sonda de tempo de execução em fluxos de trabalho gerados que inspeciona `DOCKER_HOST` e anexa `--docker-host-path-prefix /tmp/gh-aw` à invocação do AWF quando o valor corresponde a `tcp://localhost:<porta>` ou `tcp://127.0.0.1:<porta>`. Nenhuma configuração em nível de fluxo de trabalho é necessária.

A sonda é limitada ao AWF `v0.25.43` ou mais recente. Fluxos de trabalho fixados em uma versão AWF anterior, ou executando em runners hospedados pelo GitHub (onde `DOCKER_HOST` não está definido ou aponta para um soquete Unix), não são afetados.

## Formatos de runs-on

**String** — label de runner único:

```aw
---
on: issues
runs-on: self-hosted
---
```

**Array** — o runner deve ter *todas* as labels listadas (E lógico):

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
  group: meu-grupo-de-runner
  labels: [linux, x64]
---
```

## Compartilhando configuração via importações

`runs-on` deve ser definido em cada fluxo de trabalho — ele não é mesclado a partir de importações. Outras configurações como `network` e `tools` podem ser compartilhadas:

```aw title=".github/workflows/shared/runner-config.md"
---
network:
  allowed:
    - defaults
    - private-registry.exemplo.com
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

Quando a [detecção de ameaças](/gh-aw/reference/threat-detection/) está habilitada, o job de detecção executa no runner do job do agente por padrão. Substitua-o com `safe-outputs.threat-detection.runs-on`:

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

Isso é útil quando seu runner auto-hospedado não possui acesso à internet de saída para detecção de IA, ou quando você deseja executar o job de detecção em um runner mais barato.

## Configurando o runner do job de framework

Jobs de framework — ativação, pré-ativação, safe-outputs, desbloqueio, APM, update_cache_memory e push_repo_memory — têm como padrão `ubuntu-slim`. Use `runs-on-slim:` para substituir todos de uma vez:

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
> `runs-on` controla apenas o job do agente principal. `runs-on-slim` controla todos os jobs de framework/gerados. `safe-outputs.runs-on` ainda tem precedência sobre `runs-on-slim` especificamente para jobs de safe-output.

## Configurando o runner do fluxo de trabalho de manutenção

O fluxo de trabalho gerado `agentics-maintenance.yml` tem como padrão `ubuntu-slim` para todos os seus jobs. Para usar um runner auto-hospedado para jobs de manutenção, defina `runs_on` em `.github/workflows/aw.json`:

**Label única:**

```json
{
  "maintenance": {
    "runs_on": "self-hosted"
  }
}
```

**Labels múltiplas** (o runner deve corresponder a todas):

```json
{
  "maintenance": {
    "runs_on": ["self-hosted", "linux", "x64"]
  }
}
```

Esta configuração aplica-se a cada job em `agentics-maintenance.yml` (close-expired-entities, cleanup-cache-memory, run_operation, apply_safe_outputs, create_labels, validate_workflows e activity_report). Re-execute `gh aw compile` após alterar `aw.json` para regenerar o fluxo de trabalho.

> [!NOTE]
> `aw.json` é separado do frontmatter de fluxo de trabalho individual. Ele fornece configurações em nível de repositório para fluxos de trabalho de infraestrutura gerados.

## Documentação Relacionada

- [Frontmatter](/gh-aw/reference/frontmatter/#run-configuration-run-name-runs-on-runs-on-slim-timeout-minutes) — referência de sintaxe para `runs-on` e `runs-on-slim`
- [Importações](/gh-aw/reference/imports/) — campos importáveis e semântica de merge
- [Detecção de Ameaças](/gh-aw/reference/threat-detection/) — configuração do job de detecção
- [Acesso à Rede](/gh-aw/reference/network/) — configuração de permissões de rede de saída
- [Sandbox](/gh-aw/reference/sandbox/) — requisitos de contêiner e Docker
- [Efêmeros](/gh-aw/reference/ephemerals/#maintenance-configuration) — referência completa de configuração de manutenção do `aw.json`
- [Configuração Empresarial](/gh-aw/reference/enterprise-configuration/) — endpoints de API personalizados para GHEC/GHES

## Requisitos do ambiente do runner

Runners auto-hospedados devem atender a estes requisitos para que os fluxos de trabalho agenticos sejam executados de forma confiável.

### Docker

Um daemon Docker funcional é necessário. O gateway MCP e o sandbox executam como contêineres.

- **Soquete Unix**: O Docker deve ser acessível via soquete Unix (tipicamente `/var/run/docker.sock`). Se `DOCKER_HOST` não estiver definido, o gateway monta `/var/run/docker.sock`. Se `DOCKER_HOST` for `unix://...` ou um caminho absoluto, o gateway monta esse caminho de soquete. Outros esquemas (por exemplo `tcp://...`) são ignorados para montagens e o padrão volta para `/var/run/docker.sock`.
- **Grupo Docker**: O usuário do runner deve estar no grupo `docker`, ou o soquete deve ser legível por todos (world-readable).
- **ARC/Kubernetes**: Se estiver usando [actions-runner-controller](https://github.com/actions/actions-runner-controller) com Docker-in-Docker (dind), o sidecar dind deve compartilhar o soquete Docker via volume `emptyDir`. O gateway tentará novamente a verificação do soquete por até 10 segundos para lidar com condições de corrida na inicialização.

### Sistema de Arquivos

- **Use `RUNNER_TEMP` para estado transitório.** Coloque estado de sandbox, downloads de ferramentas e saídas intermediárias em `$RUNNER_TEMP`, que é limpo entre jobs. Em runners compartilhados, evite escrever dados de fluxo de trabalho arbitrários em `/tmp` pois eles podem persistir entre jobs. O prefixo `/tmp/gh-aw` é reservado para reescrita de caminho AWF ARC DinD. `actions/setup` redefine `/tmp/gh-aw` no início do job, e a política de limpeza `/tmp` normal do seu runner deve lidar com dados obsoletos de jobs interrompidos.
- **Sem premissa de root ou sudo.** O usuário do runner pode não ter acesso root ou `sudo` (exceto pela configuração inicial de iptables, que requer `sudo`). Instalações de ferramentas, operações de arquivo e configuração de sandbox devem funcionar como o usuário do runner não privilegiado.
- **Sem instalações globais.** Não instale pacotes em `/usr/local/`, `/opt/hostedtoolcache/` ou outros caminhos de todo o sistema. Eles podem ser somente leitura, compartilhados entre runners ou montados como somente leitura dentro do sandbox. Use locais graváveis no escopo do job em vez disso.
- **Sem caminhos `HOME` hardcoded.** O diretório home do runner pode não ser `/home/runner`. Use `$HOME` ou `$RUNNER_TEMP` em vez de caminhos hardcoded.

### Limpeza pós-job

Runners auto-hospedados persistem entre jobs. Fluxos de trabalho agenticos devem limpar após si mesmos:

- Arquivos escritos em `$RUNNER_TEMP` são limpos automaticamente.
- Contêineres Docker na bridge `awf-net` são parados e removidos pelo teardown do sandbox.
- Se o seu fluxo de trabalho criar arquivos fora de `$RUNNER_TEMP` (por exemplo, em `$GITHUB_WORKSPACE`), a limpeza de workspace embutida do runner lida com isso.

### Rede

Runners auto-hospedados precisam de acesso HTTPS de saída para:

- `api.githubcopilot.com` (ou seu endpoint empresarial Copilot)
- `github.com` (ou sua instância GHES)
- `ghcr.io` (para puxar a imagem de contêiner do gateway MCP)
- Quaisquer domínios listados na configuração `network.allowed` do seu fluxo de trabalho

## GHES (GitHub Enterprise Server)

Fluxos de trabalho agenticos podem executar no GHES com alguma configuração adicional.

### Compatibilidade de artefatos

O GHES não suporta o backend `@actions/artifact` v2.0.0+ usado por `upload-artifact@v4+` e `download-artifact@v4+`. Fluxos de trabalho compilados usam as versões mais recentes da ação de artefato por padrão, que falham no GHES com `GHESNotSupportedError`.

Habilite o modo de compatibilidade GHES em `.github/workflows/aw.json` para usar ações de artefato compatíveis v3.x:

```json
{
  "ghes": true
}
```

Ou compile com `--ghes` para geração de fluxo de trabalho pontual:

```bash
gh aw compile --ghes meu-fluxo-de-trabalho.md
```

Isso faz com que o compilador emita `upload-artifact@v3.2.2` e `download-artifact@v3.1.0` em vez das versões mais recentes, que são compatíveis com todas as versões do GHES.

### Endpoint da API

Instâncias GHES precisam da configuração de engine `api-target`. Veja [Configuração Empresarial](/gh-aw/reference/enterprise-configuration/) para instruções completas de configuração.

```aw
---
engine:
  id: copilot
  api-target: api.enterprise.github.com
network:
  allowed:
    - defaults
    - github.empresa.com
    - api.enterprise.github.com
---
```

## ARC (Actions Runner Controller)

Ao executar no [ARC](https://github.com/actions/actions-runner-controller) com Kubernetes:

### Sidecar Docker-in-Docker (dind)

O padrão dind ARC padrão com um `emptyDir` compartilhado para o soquete Docker é suportado. O gateway MCP:

1. Resolve o caminho do soquete Docker a partir de `DOCKER_HOST` (suporta caminhos `unix://` e caminhos absolutos)
2. Detecta automaticamente o ID do grupo do soquete para permissões corretas
3. Tenta novamente a verificação do soquete por até 10 segundos para lidar com a condição de corrida onde o gateway inicia antes do `dockerd`

### Segurança de Pod

O pod do runner requer `privileged: true` tanto no sidecar dind quanto no contêiner do runner. Isso é necessário para:

- `dockerd` no sidecar dind
- Regras de `iptables` para o firewall de fluxo de trabalho agentico
- Configuração de chroot/sandbox no contêiner do runner
