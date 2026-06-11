---
title: Memória Cache
description: Guia para usar cache-memory para armazenamento persistente de arquivos entre execuções de fluxo de trabalho com cache do GitHub Actions.
sidebar:
  order: 1500
---

A Memória Cache (cache-memory) fornece armazenamento persistente de arquivos entre execuções de fluxo de trabalho via cache do GitHub Actions com retenção de 7 dias. O compilador configura automaticamente o diretório de cache, operações de restaurar/salvar e chaves de fallback progressivas em `/tmp/gh-aw/cache-memory/` (padrão) ou `/tmp/gh-aw/cache-memory-{id}/` (caches adicionais).

## Habilitando a Memória Cache

```aw wrap
---
tools:
  cache-memory: true
---
```

Armazena arquivos em `/tmp/gh-aw/cache-memory/` usando uma chave de cache com escopo de fluxo de trabalho. Use operações padrão de arquivo para armazenar/recuperar JSON/YAML, arquivos de texto ou subdiretórios.

## Configuração avançada

```aw wrap
---
tools:
  cache-memory:
    key: custom-memory-${{ github.repository_owner }}
    retention-days: 30  # 1-90 dias, estende o acesso além da expiração do cache
    allowed-extensions: [".json", ".txt", ".md"]  # Restringir tipos de arquivo (padrão: vazio/todos os tipos permitidos)
---
```

> [!NOTE]
> Não inclua `${{ github.run_id }}` em uma chave fornecida pelo usuário — o compilador a anexa automaticamente à chave de salvamento e gera chaves de restauração estáveis a partir do prefixo.

### Restrições de tipo de arquivo

O campo `allowed-extensions` restringe quais tipos de arquivo podem ser escritos na memória cache. Por padrão, todos os tipos de arquivo são permitidos (array vazio). Quando especificado, apenas arquivos com extensões listadas podem ser armazenados.

```aw wrap
---
tools:
  cache-memory:
    allowed-extensions: [".json", ".jsonl", ".txt"]  # Apenas estas extensões permitidas
---
```

Se arquivos com extensões não permitidas forem encontrados, o fluxo de trabalho relatará falhas de validação.

## Múltiplas configurações

```aw wrap
---
tools:
  cache-memory:
    - id: default
      key: memory-default
    - id: session
      key: memory-session-${{ github.run_id }}
    - id: logs
      retention-days: 7
---
```

Monta em `/tmp/gh-aw/cache-memory/` (padrão) ou `/tmp/gh-aw/cache-memory-{id}/`. O `id` determina o nome da pasta; `key` tem como padrão um prefixo com escopo de fluxo de trabalho derivado do nome saneado do fluxo de trabalho.

## Mesclando de fluxos de trabalho compartilhados

```aw wrap
---
imports:
  - shared/mcp/server-memory.md
tools:
  cache-memory: true
---
```

Regras de mesclagem: **Single→Single** (local sobrescreve), **Single→Multiple** (local converte para array), **Multiple→Multiple** (mesclar por `id`, local vence).

## Comportamento

Cache do GitHub Actions: retenção de 7 dias, 10GB por repositório, política LRU (Least Recently Used) de remoção. Adicione `retention-days` para fazer upload de artefatos (1-90 dias) para acesso estendido.

Os caches são acessíveis entre branches com chaves de salvamento únicas por execução. O compilador gera automaticamente um prefixo de chaves de restauração removendo `${{ github.run_id }}` da chave de salvamento, para que cada execução possa recorrer ao cache da execução anterior. Para `scope: repo`, uma chave de restauração adicional sem o ID do fluxo de trabalho é adicionada para permitir o compartilhamento de cache entre fluxos de trabalho.

Chaves personalizadas fornecidas pelo usuário anexam automaticamente `-${{ github.run_id }}` se ainda não estiver presente.

## Melhores práticas

Use nomes descritivos de arquivos/diretórios, chaves de cache hierárquicas (`project-${{ github.repository_owner }}-${{ github.workflow }}`) e escopo apropriado (padrão de fluxo de trabalho ou todo o repositório/usuário). Monitore o crescimento dentro do limite de 10GB.

## Comparação com Repo Memory

| Recurso | Memória Cache | Repo Memory |
|---------|--------------|-------------|
| Armazenamento | GitHub Actions Cache | Branches Git |
| Retenção | 7 dias | Ilimitada |
| Limite de tamanho | 10GB/repositório | Limites do repositório |
| Controle de versão | Não | Sim |
| Desempenho | Rápido | Mais lento |
| Melhor para | Temporário/sessões | Longo prazo/histórico |

Para retenção ilimitada com controle de versão, veja [Repo Memory](/gh-aw/reference/repo-memory/).

## Limpeza automática

O fluxo de trabalho de [manutenção agentic](/gh-aw/reference/ephemerals/#cache-memory-cleanup) limpa automaticamente entradas obsoletas de memória cache em uma programação. Os caches são agrupados por prefixo de chave (tudo antes do ID da execução), e apenas a entrada mais recente por grupo é mantida. Entradas mais antigas são excluídas para evitar crescimento desenfreado de armazenamento.

Você também pode acionar a limpeza manualmente a partir da interface do GitHub Actions executando o fluxo de trabalho `Agentic Maintenance` com a operação `clean_cache_memories`.

## Solução de problemas

- **Arquivos não persistindo**: Verifique a consistência da chave de cache e os logs para mensagens de restaurar/salvar.
- **Problemas de acesso a arquivos**: Crie subdiretórios primeiro, verifique as permissões, use caminhos absolutos.
- **Problemas de tamanho de cache**: Monitore o crescimento, limpe periodicamente ou use chaves baseadas em tempo para expiração automática.
- **Configuração incorreta do caminho de cache**: Quando o agente chama `missing_data` com `reason: "cache_memory_miss"`, o manipulador de conclusão abre automaticamente uma issue de falha sinalizando um possível problema no caminho do cache. Verifique se o prompt do agente referencia o caminho correto (`/tmp/gh-aw/cache-memory/` por padrão, ou `/tmp/gh-aw/cache-memory-{id}/` para caches nomeados) e se a chave de cache é consistente entre execuções.

## Cache com integridade

Quando um fluxo de trabalho usa `tools.github.min-integrity`, a memória cache aplica automaticamente isolamento de nível de integridade. As chaves de cache incluem o nível de integridade do fluxo de trabalho e um hash da política de proteção para que a alteração de qualquer campo de política force uma falha de cache (cache miss).

O compilador gera etapas de branching baseadas em git ao redor do agente. Antes do agente executar, ele faz checkout do branch de integridade correspondente e mescla de todos os branches de integridade superior (integridade superior sempre vence conflitos). Após a execução do agente, as alterações são confirmadas nesse branch. O agente em si vê apenas arquivos simples — o diretório `.git/` viaja transparentemente no arquivo tar do cache do Actions.

### Semântica de mesclagem

| Integridade da execução | Vê dados escritos por | Não pode ver |
|---|---|---|
| `merged` | `merged` apenas | `approved`, `unapproved`, `none` |
| `approved` | `approved` + `merged` | `unapproved`, `none` |
| `unapproved` | `unapproved` + `approved` + `merged` | `none` |
| `none` | todos os níveis | — |

Isso evita que um agente de integridade inferior contamine dados que uma execução de integridade superior leria posteriormente.

> [!NOTE]
> Caches existentes sofrerão cache miss na primeira execução após a atualização para uma versão que inclui esse recurso — intencional, pois dados legados não têm procedência de integridade.

## Segurança

Não armazene dados confidenciais na memória cache. A memória cache segue as permissões do repositório.

Logs de acesso. Com [detecção de ameaças](/gh-aw/reference/threat-detection/), o cache só salva após a validação ser bem-sucedida (restaurar→modificar→fazer upload de artefato→validar→salvar).

## Exemplos

Veja [Grumpy Code Reviewer](https://github.com/github/gh-aw/blob/main/.github/workflows/grumpy-reviewer.md) para rastrear o histórico de revisão de PR.

## Documentação relacionada

- [Repo Memory](/gh-aw/reference/repo-memory/) - Armazenamento persistente baseado em branch git com retenção ilimitada
- [Frontmatter](/gh-aw/reference/frontmatter/) - Guia completo de configuração de frontmatter
- [Safe Outputs](/gh-aw/reference/safe-outputs/) - Processamento de saída e automação
- [Documentação do Cache do GitHub Actions](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows) - Documentação oficial do cache do GitHub
