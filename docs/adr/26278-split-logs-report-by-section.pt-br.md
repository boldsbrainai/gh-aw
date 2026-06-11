# ADR-26278: Dividir logs_report.go em Arquivos Focados em Domínio

**Data**: 2026-04-14
**Status**: Rascunho
**Decisores**: pelikhan, Copilot

---

## Parte 1 — Narrativa (Amigável)

### Contexto

`pkg/cli/logs_report.go` havia crescido para 1.065 linhas contendo mais de 15 funções de builder independentes cobrindo quatro domínios de relatório distintos (uso de ferramenta, MCP, logs de firewall/acesso e erros), sem estado compartilhado entre eles. Isso tornava o arquivo difícil de navegar—contribuidores tinham que rolar centenas de linhas para encontrar a função relevante para o domínio em que estavam trabalhando. O arquivo era um padrão anti-padrão clássico de "God file" dentro de um único pacote Go.

### Decisão

Dividiremos `pkg/cli/logs_report.go` em cinco arquivos dentro do mesmo pacote `cli`, cada um possuindo um domínio de relatório: `logs_report_tools.go`, `logs_report_mcp.go`, `logs_report_firewall.go`, `logs_report_errors.go` e um `logs_report.go` reduzido que mantém orquestração de nível superior e tipos de dados principais. Todos os arquivos permanecem no mesmo pacote Go (`package cli`), portanto, nenhuns caminhos de importação ou APIs públicas mudam. Nenhuma lógica é modificada; esta é uma reorganização puramente estrutural para melhorar a navegabilidade em nível de arquivo.

### Alternativas Consideradas

#### Alternativa 1: Manter tudo em um único arquivo

O arquivo poderia permanecer como está. Esta é a opção mais simples—sem conflitos de mesclagem, sem mudanças de navegação. Foi rejeitada porque 1.065 linhas sem estado compartilhado entre seções tornam a navegação no arquivo genuinamente dolorosa; encontrar um builder específico requer busca de texto ou rolagem por seções não relacionadas.

#### Alternativa 2: Extrair para um sub-pacote separado

Os domínios de relatório poderiam ter sido movidos para um sub-pacote dedicado (ex.: `pkg/cli/logsreport/`). Isso forneceria limites mais fortes de tempo de compilação e tornaria a separação de domínio visível no nível de importação. Não foi escolhida porque as funções builder referenciam identificadores não exportados em `cli` e movê-las exigiria exportar esses tipos ou reestruturar significativamente o limite do pacote—uma mudança muito além do escopo do problema de navegabilidade que está sendo resolvido.

#### Alternativa 3: Dividir por Tipo de Preocupação (Tipos vs. Builders)

Uma estrutura alternativa agruparia todos os tipos `*Summary` em um arquivo e todas as funções `build*` em outro, independentemente do domínio. Foi rejeitada porque não melhora a navegabilidade para o caso de uso principal: entender ou modificar toda a lógica relacionada a um domínio (ex.: análise de log de firewall). O agrupamento por domínio mantém tipos relacionados e seus builders colocados juntos.

### Consequências

#### Positivas
- Cada novo arquivo tem ≤ 200 linhas, bem dentro do limite de navegabilidade da equipe.
- Contribuidores trabalhando em um domínio de relatório (ex.: firewall) podem abrir um único arquivo focado.
- `logs_report.go` é reduzido de 1.065 para 417 linhas, com a maior parte restante atribuível a `buildLogsData` (a função de orquestração mantida intacta por especificação do issue).
- Sem mudanças na superfície da API—chamadores fora do pacote não são afetados.

#### Negativas
- A base de código agora tem mais arquivos, o que pode adicionar sobrecarga ao pesquisar tipos ou funções por todo o pacote pela primeira vez.
- Relacionamentos entre domínios (ex.: um tipo de `logs_report_tools.go` usado em `logs_report.go`) são menos imediatamente visíveis do que quando tudo estava em um arquivo.

#### Neutras
- A visibilidade intra-pacote do Go significa que todos os identificadores não exportados permanecem acessíveis em todos os arquivos divididos; nenhuma mudança de visibilidade é necessária.
- A função `buildLogsData` em `logs_report.go` (~191 linhas) permanece a maior unidade única e é uma candidata para futura decomposição se a complexidade crescer.
- Ferramentas de IDE e `go build` não são afetadas pelas divisões de arquivo intra-pacote.

---

## Parte 2 — Especificação Normativa (RFC 2119)

> As palavras-chave **DEVEM**, **NÃO DEVEM**, **OBRIGATÓRIO**, **SHALL**, **SHALL NOT**, **RECOMENDADO**, **MAY** e **OPCIONAL** nesta seção devem ser interpretadas conforme descrito em [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### Organização de Arquivo

1. Implementações **DEVEM** manter todos os arquivos `logs_report_*.go` no mesmo pacote Go (`package cli`).
2. Cada arquivo específico de domínio **DEVE** possuir todos os tipos e funções de builder para esse domínio, e **NÃO DEVE** conter funções de builder que pertençam a outro domínio.
3. Implementações **NÃO DEVEM** introduzir um novo sub-pacote apenas para abrigar os arquivos divididos; o limite do pacote `pkg/cli` existente **SHALL** ser mantido.
4. Implementações **DEVEM** manter cada arquivo `logs_report_*.go` abaixo de 250 linhas; se um arquivo crescer além desse limite, ele **DEVE** ser decomposto ainda mais ou a divisão reconsiderada.

### Orquestração e Tipos Principais

1. A função de orquestração de nível superior `buildLogsData` e os tipos de dados principais (`LogsData`, `LogsSummary`, `RunData`, `ContinuationData`) **DEVEM** permanecer em `logs_report.go`.
2. Implementações **NÃO DEVEM** duplicar definições de tipo em arquivos divididos; cada tipo **SHALL** ser definido em exatamente um arquivo.
3. Funções de renderização (`renderLogsConsole`, `renderLogsJSON`) e `writeSummaryFile` **DEVEM** permanecer em `logs_report.go` junto com a camada de orquestração.

### Mapeamento de Domínio para Arquivo

1. Tipos e builders de uso de ferramenta (`ToolUsageSummary`, `isValidToolName`, `buildToolUsageSummary`) **DEVEM** residir em `logs_report_tools.go`.
2. Builders MCP (`buildMCPFailuresSummary`, `buildMCPToolUsageSummary`) **DEVEM** residir em `logs_report_mcp.go`.
3. Tipos e builders de firewall e log de acesso (`AccessLogSummary`, `FirewallLogSummary`, `domainAggregation`, `aggregateDomainStats`, `convertDomainsToSortedSlices`, `buildAccessLogSummary`, `buildFirewallLogSummary`, `buildRedactedDomainsSummary`) **DEVEM** residir em `logs_report_firewall.go`.
4. Tipos e builders de resumo de erro (`ErrorSummary`, `addUniqueWorkflow`, `aggregateSummaryItems`, `buildCombinedErrorsSummary`, `buildMissingToolsSummary`, `buildMissingDataSummary`) **DEVEM** residir em `logs_report_errors.go`.

### Conformidade

Uma implementação é considerada em conformidade com este ADR se satisfizer todos os requisitos **DEVEM** e **NÃO DEVEM** acima. A falha em atender a qualquer requisito **DEVE** ou **NÃO DEVE** constitui não conformidade. As verificações principais de conformidade são: (a) todos os arquivos divididos estão em `package cli`, (b) nenhum novo sub-pacote é criado, (c) os builders e tipos de cada domínio estão colocados juntos em seu arquivo designado, e (d) a orquestração e tipos principais permanecem em `logs_report.go`.

---

*Este é um ADR de RASCUNHO gerado pelo workflow [Design Decision Gate](https://github.com/github/gh-aw/actions/runs/24422316567) workflow. O autor do PR deve revisar, completar e finalizar este documento antes que o PR possa ser mesclado.*
