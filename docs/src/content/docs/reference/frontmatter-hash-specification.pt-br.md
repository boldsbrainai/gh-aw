---
title: Especificação de Hash de Frontmatter
description: Especificação para computar hashes determinísticos de frontmatter de fluxo de trabalho agentic
version: 1.0.0
status: Rascunho
publication_date: 2026-05-07
---

# Especificação de Hash de Frontmatter

**Versão**: 1.0.0  
**Status**: Rascunho  
**Data de Publicação**: 07/05/2026  
**Versão Mais Recente**: [frontmatter-hash-specification](/gh-aw/reference/frontmatter-hash-specification/)  
**Editor**: Equipe do GitHub Agentic Workflows

---

Este documento especifica o algoritmo para computar um hash determinístico de frontmatter de fluxo de trabalho agentic, incluindo contribuições de fluxos de trabalho importados.

## Objetivo

O hash de frontmatter fornece:
1. **Detecção de bloqueio obsoleto (stale lock)**: Identificar quando o arquivo de bloqueio compilado está fora de sincronia com o fluxo de trabalho de origem (ex: após editar o arquivo `.md` sem recompilar)
2. **Reprodutibilidade**: Garantir que configurações idênticas produzam hashes idênticos entre linguagens (Go e JavaScript)
3. **Detecção de alteração**: Verificar se a configuração do fluxo de trabalho não foi alterada entre a compilação e a execução

## Conformidade

### Classes de Conformidade

- **Conformidade Básica**: Uma implementação DEVE computar um hash SHA-256 determinístico a partir da entrada de frontmatter canonizada e DEVE produzir a mesma saída para entrada idêntica.
- **Conformidade Total**: Uma implementação DEVE satisfazer a Conformidade Básica e DEVE implementar verificações de consistência entre idiomas entre as implementações em Go e JavaScript.

### Notação de Requisitos

As palavras-chave **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY** e **OPTIONAL** neste documento devem ser interpretadas como descrito em [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

## Algoritmo de Hash

### 1. Coleta de Entrada

Colete todo o frontmatter do fluxo de trabalho principal e de todos os fluxos de trabalho importados em **ordem de largura (BFS traversal)**:

1. **Frontmatter do fluxo de trabalho principal**: O frontmatter do arquivo de fluxo de trabalho raiz
2. **Frontmatter do fluxo de trabalho importado**: Frontmatter de cada arquivo importado na ordem de processamento BFS
   - Inclui arquivos importados transitivamente (importações de importações)
   - Arquivos de agente (`.github/agents/*.md`) apenas contribuem com conteúdo markdown, não frontmatter

#### Regras de Travessia BFS e Desempate

A travessia BFS processa importações nível por nível, começando do fluxo de trabalho raiz. Quando um arquivo de fluxo de trabalho importa vários arquivos, eles são enfileirados da esquerda para a direita na ordem em que aparecem na lista `imports:`. Esta ordenação é preservada em cada nível.

**Manipulação de importação em diamante**: Se um arquivo de fluxo de trabalho aparecer mais de uma vez no grafo de importação (uma dependência de "diamante"), a **primeira ocorrência** na ordem BFS determina onde o frontmatter desse arquivo é mesclado; todas as ocorrências subsequentes do mesmo arquivo **DEVEM ser silenciosamente ignoradas**. Implementações DEVEM detectar caminhos de importação duplicados usando comparação de caminho canônico (diferencia maiúsculas/minúsculas, sem normalização de barra final) e descartar duplicatas sem erro.

**Exemplo (grafo de diamante)**:

```
root.md  →  imports: [a.md, b.md]
a.md     →  imports: [shared.md]
b.md     →  imports: [shared.md]
```

Ordem da fila BFS: `[root.md, a.md, b.md, shared.md]`  
`shared.md` aparece duas vezes, mas é processado apenas uma vez (após `a.md` na ordem da fila).  
Ordem de entrada do hash canônico: root → a → b → shared.

Esta regra garante que o hash seja determinístico, independentemente do caminho de travessia que primeiro descobre uma dependência compartilhada.

### 2. Seleção de Campo

Inclua os seguintes campos de frontmatter na computação de hash:

**Configuração Principal:**
- `engine` - Especificação do motor de IA
- `on` - Triggers do fluxo de trabalho
- `permissions` - Permissões do GitHub Actions
- `tracker-id` - Identificador de rastreador do fluxo de trabalho

**Ferramenta e Integração:**
- `tools` - Configurações de ferramenta (GitHub, Playwright etc.)
- `mcp-servers` - Configurações de servidor MCP
- `network` - Permissões de acesso à rede
- `safe-outputs` - Configurações de safe output
- `mcp-scripts` - Configurações de safe input

**Configuração de Runtime:**
- `runtimes` - Especificações de versão de runtime (Node.js, Python etc.)
- `services` - Serviços de container
- `cache` - Configuração de cache

**Estrutura do Fluxo de Trabalho:**
- `steps` - Passos personalizados do fluxo de trabalho
- `post-steps` - Passos pós-execução
- `jobs` - Definições de job do GitHub Actions

**Metadados:**
- `description` - Descrição do fluxo de trabalho
- `labels` - Labels do fluxo de trabalho
- `bots` - Lista de bots autorizados
- `timeout-minutes` - Timeout do fluxo de trabalho
- `secret-masking` - Configuração de mascaramento de segredo

**Metadados de Importação:**
- `imports` - Lista de caminhos de fluxo de trabalho importados (para rastreabilidade)
- `inputs` - Definições de parâmetro de entrada

**Campos Excluídos:**
- Conteúdo do corpo markdown (não faz parte do frontmatter)
- Variações de comentários e espaços em branco
- Ordenação de campos (normalizada durante o processamento)

### 3. Serialização JSON Canônica

Transforme o frontmatter coletado em uma representação JSON canônica:

#### 3.1 Estratégia de Mesclagem

Para cada fluxo de trabalho na ordem BFS:
1. Analise o frontmatter em um objeto estruturado
2. Mescle com o frontmatter acumulado usando estas regras:
   - **Substituir**: `engine`, `on`, `tracker-id`, `description`, `timeout-minutes`
   - **Mesclagem profunda**: `tools`, `mcp-servers`, `network`, `permissions`, `runtimes`, `cache`, `services`
   - **Anexar**: `steps`, `post-steps`, `safe-outputs`, `mcp-scripts`, `jobs`
   - **União**: `labels`, `bots` (deduplicados)
   - **Rastrear**: `imports` (lista de todos os caminhos importados)

#### 3.2 Regras de Normalização

Aplique estas regras de normalização para garantir saída determinística:

1. **Ordenação de Chave**: Ordene todas as chaves de objeto alfabeticamente em todos os níveis
2. **Ordenação de Array**: Preserve a ordem do array como está (sem ordenação de elementos do array)
3. **Espaço em Branco**: Use espaço em branco mínimo (sem pretty-printing)
4. **Formato Numérico**: Represente números sem expoentes (ex: `120` não `1.2e2`)
5. **Valores Booleanos**: Use `true` e `false` em minúsculas
6. **Manipulação de Null**: Inclua valores `null` explicitamente
7. **Containers Vazios**: Inclua objetos vazios `{}` e arrays vazios `[]`
8. **Escape de String**: Use escape padrão JSON (aspas, barras invertidas, caracteres de controle)

#### 3.3 Formato de Serialização

O JSON canônico inclui todos os campos de frontmatter mais informações de versão:

```json
{
  "bots": ["copilot"],
  "cache": {},
  "description": "Daily audit of workflow runs",
  "engine": "claude",
  "imports": ["shared/mcp/gh-aw.md", "shared/jqschema.md"],
  "jobs": {},
  "labels": ["audit", "automation"],
  "mcp-servers": {},
  "network": {"allowed": ["api.github.com"]},
  "on": {"schedule": "daily"},
  "permissions": {"actions": "read", "contents": "read"},
  "post-steps": [],
  "runtimes": {"node": {"version": "20"}},
  "mcp-scripts": {},
  "safe-outputs": {"create-discussion": {"category": "audits"}},
  "services": {},
  "steps": [],
  "template-expressions": ["${{ env.MY_VAR }}"],
  "timeout-minutes": 30,
  "tools": {"repo-memory": {"branch-name": "memory/audit"}},
  "tracker-id": "audit-workflows-daily",
  "versions": {
    "agents": "v0.0.84",
    "awf": "v0.11.2",
    "gh-aw": "dev"
  }
}
```

### 4. Informações de Versão

O hash inclui números de versão para garantir alterações de hash quando dependências são atualizadas:

- **gh-aw**: A versão do compilador (ex: "0.1.0" ou "dev")
- **awf**: A versão do firewall (ex: "v0.11.2")
- **agents**: A versão do gateway MCP (ex: "v0.0.84")

Isso garante que a atualização de qualquer componente invalide hashes existentes.

1. **Serializar**: Converter o frontmatter mesclado e normalizado em JSON canônico
2. **Adicionar Versões**: Incluir informações de versão para gh-aw, awf (firewall) e agents (gateway MCP)
3. **Hash**: Computar o hash SHA-256 da string JSON (codificada em UTF-8)
4. **Codificar**: Representar o hash como uma string hexadecimal minúscula (64 caracteres)

**Exemplo:**
```
Input JSON: {"engine":"copilot","on":{"schedule":"daily"},"versions":{"agents":"v0.0.84","awf":"v0.11.2","gh-aw":"dev"}}
SHA-256: a1b2c3d4e5f6...  (64 caracteres hexadecimais)
```

### 5. Consistência Entre Idiomas

Ambas as implementações em Go e JavaScript DEVEM:
- Usar a mesma seleção de campo e regras de mesclagem
- Produzir JSON canônico idêntico (byte-a-byte)
- Usar função de hash SHA-256
- Codificar saída como hexadecimal minúsculo

**Casos de teste** devem verificar hashes idênticos entre ambas as implementações para:
- Frontmatter vazio
- Fluxos de trabalho de arquivo único (sem importações)
- Importações de múltiplos níveis (2+ níveis de profundidade)
- Todos os tipos de campo (strings, números, booleanos, arrays, objetos)
- Caracteres especiais e escape
- Todos os fluxos de trabalho no repositório

## Notas de Implementação

### Implementação em Go

A implementação atual em Go (`pkg/parser/frontmatter_hash.go`) usa uma **abordagem baseada em texto** que diverge do modelo de seleção de campo descrito na Seção 2 ("Seleção de Campo") desta especificação:

- **Comportamento atual**: Todo o texto de frontmatter normalizado é hasheado como uma única string opaca (chave `frontmatter-text` no JSON canônico), juntamente com uma lista ordenada de caminhos de arquivo importados e seus textos normalizados. Isso significa que _todos_ os campos de frontmatter — incluindo os excluídos como comentários — afetam o valor do hash.
- **Comportamento especificado**: A especificação pede a seleção de campos nomeados individuais e mesclagem por tipo (substituir, mesclagem profunda, anexar, união).

**Implicação**: A abordagem baseada em texto é mais conservadora (qualquer alteração no frontmatter invalida o hash, incluindo alterações apenas de espaço em branco após a normalização) e mais simples de implementar entre idiomas. A compensação é que ela não pode suportar exclusão seletiva de campo sem modificar o passo de normalização de texto.

**Status de sincronização** (verificado em 06/05/2026): A implementação em Go é consistente com a implementação em JavaScript em `actions/setup/js/` para a abordagem baseada em texto. Ambas produzem hashes idênticos para a mesma entrada. O modelo de seleção de campo na Seção 2 documenta a intenção lógica; a implementação baseada em texto é o comportamento de runtime autoritativo até que uma revisão futura os alinhe.

**Resolução** (08/05/2026): O projeto adota oficialmente a **abordagem baseada em texto** como comportamento de runtime autoritativo (opção b). A Seção 2 ("Seleção de Campo") documenta o modelo lógico pretendido para alinhamento futuro, mas não é normativa até que um marco de migração dedicado seja agendado. Nenhuma alteração imediata nas implementações em Go ou JavaScript é necessária. Uma futura revisão v2.0.0 desta especificação PODE alinhar ambas as implementações ao modelo de seleção de campo se a exclusão seletiva de campo se tornar um requisito concreto; essa revisão DEVE incluir vetores de teste atualizados entre idiomas e um guia de migração. Até lá, implementações DEVEM continuar a usar a abordagem baseada em texto e NÃO DEVEM excluir seletivamente campos da entrada de hash.

- Use `crypto/sha256` para hashing (`crypto/sha256.Sum256`)
- Use `hex.EncodeToString()` para codificação hexadecimal

### Implementação em JavaScript

- Usa a mesma abordagem baseada em texto que a implementação em Go
- Usa Node.js `crypto.createHash('sha256')` para hashing
- Usa `.digest('hex')` para codificação hexadecimal
- A suíte de testes entre idiomas em JavaScript em `pkg/parser/frontmatter_hash_cross_language_test.go` verifica saída idêntica entre as duas implementações

### Armazenamento e Verificação de Hash

1. **Compilação**: O compilador Go computa o hash e o escreve no arquivo de log do fluxo de trabalho
2. **Execução**: A ação personalizada JavaScript:
   - Lê o hash do arquivo de log
   - Recomputa o hash do arquivo de fluxo de trabalho
   - Compara os dois hashes
   - Cria uma issue no GitHub se eles divergirem (indicando modificação no frontmatter)

## Salvaguardas

Esta seção descreve riscos conhecidos associados ao mecanismo de hash de frontmatter e as mitigações recomendadas.

### S-1: Risco de Colisão de Hash

O SHA-256 produz uma saída de 256 bits, dando uma probabilidade de colisão de aproximadamente 2⁻¹²⁸ para quaisquer duas entradas distintas sob o paradoxo do aniversário. Para o número esperado de fluxos de trabalho compilados em um repositório (tipicamente <10.000), a probabilidade de uma colisão acidental é negligenciável e não requer mitigação na camada de aplicação.

No entanto, implementações NÃO DEVEM confiar no hash como um compromisso criptográfico ou limite de segurança. O hash é uma verificação de integridade apenas para detecção de bloqueio obsoleto.

**Mitigação**: Se casos de uso futuros exigirem maior resistência à colisão (ex: armazenamento endereçável por conteúdo), implementações SHOULD atualizar para SHA-512 ou SHA3-256 e incrementar a versão da especificação.

### S-2: Limites de Detecção de Violação

O hash de frontmatter detecta desvio acidental entre a origem `.md` e o arquivo `.lock.yml` compilado. Ele NÃO impede a violação intencional. Qualquer usuário com acesso de escrita ao repositório pode modificar ambos os arquivos simultaneamente:

1. Edite a origem `.md`.
2. Recompile para regenerar o `.lock.yml` com o novo hash.
3. Comita ambos os arquivos em um único push.

Este bypass é por design — o mecanismo de hash destina-se a capturar bloqueios obsoletos acidentais, não a impor um limite de segurança.

**Mitigação**: Aplique revisões de código obrigatórias por meio de regras de proteção de branch. Exija commits assinados para fluxos de trabalho críticos. Use fluxos de trabalho separados de compilação e merge com branches protegidos para evitar pushes diretos no branch padrão.

### S-3: Inclusão de Configuração Sensível na Entrada de Hash

O JSON canônico usado para computação de hash inclui todos os campos de frontmatter, alguns dos quais podem codificar informações de topologia sensíveis (ex: endereços de servidor MCP em `mcp-servers:`, nomes de segredo em `mcp-scripts:` ou nomes de branch em `tools.repo-memory`). Essas informações são incorporadas no arquivo `.lock.yml` no momento da compilação e estão visíveis para qualquer pessoa que possa ler o repositório.

**Mitigação**: Trate a visibilidade do repositório como o limite principal de controle de acesso. Evite armazenar valores de segredo no frontmatter (use segredos do GitHub Actions em vez disso). Audite periodicamente arquivos de bloqueio em busca de configuração sensível inadvertidamente comitada.

### S-4: Recompilação Forçada por Bump de Versão

O hash inclui `versions.gh-aw`, `versions.awf` e `versions.agents`. A atualização de qualquer um desses componentes invalidará todos os hashes existentes, disparando avisos de bloqueio obsoleto em todos os fluxos de trabalho até que sejam recompilados. Em um repositório com muitos fluxos de trabalho, isso pode criar uma onda ruidosa de issues falsas positivas de bloqueio obsoleto.

**Mitigação**: Coordene atualizações de componentes com um passo de recompilação em lote `make recompile`. Automatize a recompilação no PR de atualização para que os arquivos de bloqueio estejam sempre atualizados após um bump de versão.

### S-5: Divergência de Hash Entre Idiomas

As implementações em Go e JavaScript devem produzir JSON canônico idêntico byte-a-byte. Qualquer divergência na ordenação de chaves, representação numérica ou manipulação de nulo/indefinido entre as duas implementações fará com que o runtime JavaScript relate uma incompatibilidade falsa de bloqueio obsoleto para cada execução de fluxo de trabalho.

**Mitigação**: Mantenha um arquivo de vetor de teste compartilhado (no mínimo: frontmatter vazio, fluxo de trabalho de campo único, importações de múltiplos níveis, todos os tipos de campo). Execute testes de hash entre idiomas no CI. Qualquer alteração no algoritmo de serialização em qualquer idioma DEVE ser acompanhada por vetores de teste atualizados verificados em ambas as implementações.

### S-6: Tamanho Máximo de Entrada de Frontmatter

Payloads de frontmatter muito grandes podem causar uso excessivo de memória e latência de computação de hash durante a compilação e verificação em runtime. Isso pode degradar a confiabilidade do CI e aumentar falsos positivos de bloqueio obsoleto devido a timeout ou pressão de recursos.

**Mitigação**: Implementações SHOULD impor um tamanho máximo de entrada de frontmatter cumulativo e DEVEM falhar deterministicamente com um erro descritivo quando o limite for excedido. Um limite de 1 MiB para a entrada de frontmatter normalizada combinada é RECOMENDADO, a menos que requisitos específicos do repositório justifiquem um limite superior.

---

## Notas de Sincronização

Esta seção mapeia a especificação de hash de frontmatter para os arquivos de origem que a implementam. Use este mapeamento para verificar se as alterações de especificação são refletidas em ambas as implementações.

| Componente | Arquivo(s) |
|-----------|---------|
| Computação de hash em Go | `pkg/parser/frontmatter_hash.go` (`computeFrontmatterHashTextBased`, `computeFrontmatterHashTextBasedWithReader`) |
| Computação de hash em JavaScript | `actions/setup/js/frontmatter_hash.cjs` |
| Teste entre idiomas | `pkg/parser/frontmatter_hash_cross_language_test.go` |
| Normalização de texto | `pkg/parser/frontmatter_hash.go` (`normalizeFrontmatterText`) |
| Processamento de importação | `pkg/parser/frontmatter_hash.go` (`processImportsTextBased`) |

Após qualquer alteração no algoritmo de hash:
1. Atualize a implementação em Go em `pkg/parser/frontmatter_hash.go`
2. Atualize a implementação em JavaScript em `actions/setup/js/frontmatter_hash.cjs`
3. Execute o teste entre idiomas: `go test ./pkg/parser/ -run TestFrontmatterHash`
4. Execute `make recompile` para regenerar todos os arquivos de bloqueio com hashes novos
5. Verifique a consistência entre idiomas para os casos de teste listados na Seção 5

**Comportamento de runtime**: abordagem baseada em texto é autoritativa (ver Notas de Implementação § Resolução).

**Log de resolução (12/05/2026)**: Status de sincronização re-verificado após revisão SPDD. Abordagem mantida:
a canonização baseada em texto permanece autoritativa em runtime, e a Seção 2 de seleção de campo permanece documentada apenas como intenção de design de estado futuro. Nenhuma alteração imediata nas implementações em Go ou JavaScript é necessária.

---

## Considerações de Segurança

- O hash **não é criptograficamente seguro** para autenticação (sem HMAC/assinatura)
- O hash é projetado para **detectar arquivos de bloqueio obsoletos** — ele captura casos em que o frontmatter mudou desde que o arquivo de bloqueio foi compilado pela última vez
- O hash **não garante proteção contra violação**: qualquer pessoa com acesso de escrita ao repositório pode modificar tanto a origem `.md` quanto o arquivo `.lock.yml` juntos, ignorando a detecção
- Valide sempre as origens do fluxo de trabalho por meio de processos adequados de revisão de código

## Versionamento

Esta é a versão 1.0 da especificação de hash de frontmatter.

Versões futuras podem:
- Adicionar campos adicionais
- Alterar regras de normalização
- Usar algoritmos de hash diferentes

Alterações de versão serão documentadas e a compatibilidade retroativa mantida sempre que possível.

### Versões Futuras (Planejamento v2.0.0)

De acordo com a **Resolução (08/05/2026)** nas Notas de Implementação, o algoritmo baseado em texto permanece autoritativo até que um marco de migração dedicado seja aprovado.

Issue de rastreamento: [#31983](https://github.com/github/gh-aw/issues/31983)

O projeto **NÃO DEVE** agendar uma migração v2.0.0 para o modelo de seleção de campo até que todas as seguintes tarefas rastreadas estejam concluídas:

- [ ] Confirmar e documentar um caso de uso de exclusão seletiva de campo em [#31983](https://github.com/github/gh-aw/issues/31983).
- [ ] Esboçar um guia de migração em [#31983](https://github.com/github/gh-aw/issues/31983), incluindo etapas de invalidação de arquivo de bloqueio e recompilação.
- [ ] Escrever vetores de teste entre idiomas candidatos v2.0.0 em [#31983](https://github.com/github/gh-aw/issues/31983) e verificar se passam no CI.
- [ ] Aprovar um plano de implementação em [#31983](https://github.com/github/gh-aw/issues/31983), incluindo análise de impacto de compatibilidade retroativa.

Até que esses pré-requisitos sejam atendidos, implementações **DEVEM** continuar usando o algoritmo baseado em texto e **NÃO DEVEM** excluir seletivamente campos de frontmatter da entrada de hash.

## Apêndice A: Vetores de Teste Entre Idiomas (Algoritmo Baseado em Texto)

Os seguintes vetores são normativos para o algoritmo atual baseado em texto autoritativo.

Status de validação: Cada hash de vetor é verificado para corresponder em ambas as implementações via testes entre idiomas automatizados no CI.

### FH-TV-001

Hash esperado: `4c8309afbcf816cd80c0824dce2b50047834b29e14b34b96953e88ae81048c46`

Este vetor representa um bloco de frontmatter intencionalmente vazio (`---` seguido imediatamente por `---`) em vez de um arquivo sem delimitador de frontmatter. Eles são tratados como formas de entrada diferentes para testes de conformidade e DEVEM ser validados independentemente; este vetor define apenas a forma de bloco-vazio-explícito.

```yaml
---
---

# Fluxo de Trabalho Vazio
```

### FH-TV-002

Hash esperado: `b9def9907e3328e2e03e8c47c315723df39788f251627313b1a984bb61b9cbce`

```yaml
---
engine: copilot
description: Fluxo de trabalho de teste
on:
  schedule: daily
---

# Fluxo de Trabalho de Teste
```

### FH-TV-003

Hash esperado: `8c63a05ef42cbfaff9be87a06257282cb4dcb952f71481d9d65ec3037003dbe8`

```yaml
---
engine: claude
description: Fluxo de trabalho complexo
tracker-id: complex-test
timeout-minutes: 30
on:
  schedule: daily
  workflow_dispatch: true
permissions:
  contents: read
tools:
  playwright:
    version: v1.41.0
labels:
  - test
  - complex
bots:
  - copilot
---

# Fluxo de Trabalho Complexo
```
