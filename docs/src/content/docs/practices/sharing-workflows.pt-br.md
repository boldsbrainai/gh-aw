---
title: Compartilhando Fluxos de Trabalho
description: Compartilhe, reutilize e governe GitHub Agentic Workflows entre repositórios e organizações.
---

Compartilhar fluxos de trabalho entre uma organização envolve várias camadas independentes. Cada camada pode ser adotada independentemente; as equipes não precisam de todas elas de uma vez.

O padrão empresarial recomendado é manter um repositório central `agentic-workflows` com modelos de fluxo de trabalho versionados e componentes compartilhados. Repositórios consumidores então usam `gh aw add` para instalar fluxos de trabalho completos e `imports:` para puxar módulos comuns.

## Camadas de Compartilhamento

### 1. Copiar e instalar fluxos de trabalho completos

Um repositório pode puxar um fluxo de trabalho completo de outro repositório:

```bash
gh aw add acme-org/agentic-workflows/ci-doctor@v1.2.0
```

O campo `source:` é automaticamente adicionado ao frontmatter do fluxo de trabalho instalado para que a origem e a versão sejam rastreadas. Use `gh aw add-wizard` para instalação interativa com prompts guiados. Use `gh aw add` para instalação via script ou CI.

Veja [Reutilizando Fluxos de Trabalho](/gh-aw/guides/packaging-imports/) para a referência completa do comando e opções.

### 2. Componentes de fluxo de trabalho reutilizáveis

Blocos de construção compartilhados — configurações de ferramenta, definições de servidor MCP, políticas de segurança e trechos de prompt — podem ser importados para qualquer fluxo de trabalho:

```yaml
imports:
  - acme-org/shared-workflows/shared/security-setup.md@v2.1.0
  - acme-org/shared-workflows/shared/mcp/tavily.md@v1.0.0
```

Importações remotas são armazenadas em cache sob `.github/aw/imports/` pelo commit SHA após a primeira busca. Isso permite compilação offline reprodutível e evita downloads redundantes quando múltiplas refs apontam para o mesmo commit.

Veja [Referência de Importações](/gh-aw/reference/imports/) para formatos de caminho, semântica de mesclagem e comportamento específico de campo.

### 3. Modelos parametrizados

Fluxos de trabalho compartilhados que declaram um `import-schema` aceitam parâmetros de tempo de execução via `uses`/`with`:

```yaml
imports:
  - uses: acme-org/shared-workflows/shared/reviewer.md@v1
    with:
      languages: ["go", "typescript"]
      severity: "high"
```

Isso permite que um componente compartilhado sirva múltiplos fluxos de trabalho consumidores com diferentes configurações sem exigir cópias separadas.

Veja [Referência de Importações](/gh-aw/reference/imports/#calling-a-parameterized-shared-workflow) para detalhes de declaração e validação de esquema.

### 4. Fluxo de versionamento e atualização

O compartilhamento de fluxo de trabalho empresarial precisa de um modelo de versionamento claro:

- **Tags de release exatas** (`@v1.2.0`) fixam em um release imutável específico. Elas não se movem por conta própria, então `gh aw update` continuará buscando essa mesma versão marcada, a menos que você mude a ref `source:` explicitamente.
- **Refs de release móveis** (`@v1`) seguem o release compatível mais recente dentro desse stream. Essas são as refs típicas para usar quando você quer que `gh aw update` escolha releases upstream mais novas automaticamente.
- **Refs de branch** (`@develop`) rastreiam o último commit em um branch — útil para integração de desenvolvimento.
- **Pinos SHA** (`@abc123def`) fornecem reprodutibilidade estrita e nunca se movem sem uma mudança explícita.

Para puxar mudanças upstream para um fluxo de trabalho já instalado:

```bash
gh aw update ci-doctor          # atualizar um fluxo de trabalho
gh aw update                    # atualizar todos os fluxos de trabalho rastreados
```

As atualizações usam uma mesclagem de 3 vias por padrão para preservar edições locais. Use `--no-merge` para substituir a cópia local pela versão upstream sem mesclar. Quando o `source:` registrado usa uma ref principal móvel como `@v1`, `gh aw update` permanece dentro dessa linha principal, a menos que `--major` seja passado.

### 5. Controles de compartilhamento privado e interno

Nem todos os fluxos de trabalho são seguros para compartilhar entre organizações. O GitHub Agentic Workflows fornece controles em múltiplos níveis:

- **`private: true`** no frontmatter bloqueia a instalação de um fluxo de trabalho em outros repositórios via `gh aw add`. Tentar adicionar um fluxo de trabalho privado de outro repositório falha com um erro.
- **Visibilidade do repositório** controla quais fluxos de trabalho são detectáveis. Repositórios privados exigem acesso antes que qualquer fluxo de trabalho possa ser buscado.
- **Catálogos internos da org** podem ser implementados colocando fluxos de trabalho em um repositório da organização privado ou interno, garantindo que apenas membros da organização possam instalá-los.

Veja [Fluxos de Trabalho Privados](/gh-aw/reference/frontmatter/#private-workflows-private) para detalhes de configuração.

### 6. Caching de importação e comportamento de bloqueio

Quando um fluxo de trabalho é compilado, importações remotas são resolvidas e bloqueadas. O `.lock.yml` compilado registra o commit SHA exato para cada importação remota, tornando as execuções reprodutíveis independentemente do movimento do branch upstream.

As importações são armazenadas em cache localmente em `.github/aw/imports/` pelo commit SHA. Importações em cache são usadas para todas as compilações subsequentes até que você as atualize explicitamente. Isso significa que o arquivo de bloqueio e o cache de importação juntos formam a garantia de reprodutibilidade para fluxos de trabalho compartilhados.

### 7. Modelo de execução entre repositórios

Separado de compartilhar definições de fluxo de trabalho, fluxos de trabalho podem operar entre repositórios em tempo de execução:

- Ler arquivos e metadados de outros repositórios durante a execução.
- Fazer checkout de código de repositórios de destino para análise ou modificação.
- Escrever safe outputs para repositórios de destino com autenticação explícita e listas de permissão.

```yaml
safe-outputs:
  create-issue:
    target-repo: "acme-org/target-repo"
    allowed-repos: ["acme-org/repo1", "acme-org/repo2"]
```

Operações entre repositórios requerem permissões de token do GitHub apropriadas e declarações explícitas de `allowed-repos`. Veja [Operações entre Repositórios](/gh-aw/reference/cross-repository/) para autenticação, permissões e configuração de safe output.

## Padrão Empresarial Recomendado

O padrão recomendado para organizações compartilharem fluxos de trabalho em escala:

1. **Um repositório `agentic-workflows` central** mantém modelos de fluxo de trabalho versionados e componentes compartilhados sob `workflows/` e `shared/`.
2. **Repositórios consumidores** usam `gh aw add acme-org/agentic-workflows/<workflow>@<version>` para instalar fluxos de trabalho completos.
3. **Módulos comuns** (configurações MCP, políticas de segurança, prompts compartilhados) residem em `shared/` e são importados via `imports:` em fluxos de trabalho consumidores.
4. **Tags de versão** no repositório central fornecem âncoras estáveis para consumidores de produção, enquanto branches suportam integração de desenvolvimento.
5. **`private: true`** marca fluxos de trabalho internos que não devem ser exportados para fora da organização.

Este modelo dá às equipes de plataforma propriedade centralizada e controle de atualização, enquanto dá às equipes consumidoras reprodutibilidade através de pinos de versão e a capacidade de preservar personalizações locais através de mesclagem de 3 vias.

## Questões de Governança

Quando fluxos de trabalho são compartilhados em uma organização, as decisões importantes geralmente são operacionais em vez de técnicas:

- Quem possui o fluxo de trabalho de origem e revisa mudanças propostas.
- Como as atualizações são testadas, marcadas e promovidas para repositórios consumidores.
- Quais repositórios podem consumir ou despachar para fluxos de trabalho compartilhados.
- Como segredos, permissões e safe outputs são padronizados entre consumidores.
- Quando uma equipe consumidora pode fazer fork de um fluxo de trabalho em vez de permanecer na versão compartilhada.

Essas decisões afetam a confiabilidade mais do que o formato do arquivo.

## Documentação Relacionada

- [Reutilizando Fluxos de Trabalho](/gh-aw/guides/packaging-imports/)
- [Referência de Importações](/gh-aw/reference/imports/)
- [Operações entre Repositórios](/gh-aw/reference/cross-repository/)
- [Fluxos de Trabalho Privados](/gh-aw/reference/frontmatter/#private-workflows-private)
- [SideRepoOps](/gh-aw/patterns/side-repo-ops/)
- [MultiRepoOps](/gh-aw/patterns/multi-repo-ops/)
