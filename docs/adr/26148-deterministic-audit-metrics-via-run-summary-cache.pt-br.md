# ADR-26148: Métricas de Auditoria Determinísticas via Cache de run_summary.json e Exclusão de workflow-logs/

**Data**: 2026-04-14
**Status**: Rascunho
**Decisores**: pelikhan, Copilot

---

## Parte 1 — Narrativa (Amigável)

### Contexto

O comando `audit` relatava `token_usage` e `turns` altamente inconsistentes em invocações repetidas para a mesma execução de workflow (observado: 9 turns / 381k tokens em uma chamada, 22 turns / 4.7M tokens em outra). Dois erros compostos causaram isso: (1) `AuditWorkflowRun` reprocessava incondicionalmente todos os arquivos de log locais a cada chamada, mesmo quando um `run_summary.json` totalmente computado já estava em disco; e (2) o caminhamento (walk) de arquivo de log em `extractLogMetrics` não excluía o diretório `workflow-logs/`, que `downloadWorkflowRunLogs` povoa com a saída de passo do GitHub Actions — arquivos que capturam o mesmo stdout do agente já presente nos logs de artefato do agente, inflando as contagens de tokens em aproximadamente 12×.

### Decisão

Adotaremos uma **estratégia de cache-first** para `AuditWorkflowRun`: antes de realizar qualquer chamada de API ou processamento de log, verificar se um `run_summary.json` válido existe em disco (validado pela versão da CLI). Se um cache hit for encontrado, reconstruir `ProcessedRun` a partir do resumo em cache e retornar imediatamente via um helper compartilhado `renderAuditReport`, contornando toda a lógica de re-download e re-parse. Adicionalmente, **excluiremos o diretório `workflow-logs/`** do walk de log em `extractLogMetrics` retornando `filepath.SkipDir` sempre que o walk visitar um diretório chamado `workflow-logs`, impedindo que capturas de stdout do executor do GitHub Actions sejam contadas como dados de artefato do agente. Juntas, essas duas mudanças garantem que chamadas `audit` repetidas para a mesma execução produzam métricas idênticas.

### Alternativas Consideradas

#### Alternativa 1: Invalidar e sobrescrever o cache a cada chamada

Em vez de tratar o `run_summary.json` em cache como autoritativo, reprocessar logs a cada chamada e sobrescrever o cache. Isso manteria o cache "fresco", mas perpetuaria o problema de inconsistência: o reprocessamento de log pode produzir valores diferentes dependendo de quais arquivos estão presentes no momento (ex.: se `workflow-logs/` foi povoado entre chamadas). Foi rejeitada porque a consistência das métricas de auditoria em chamadas repetidas é o requisito primário.

#### Alternativa 2: Excluir arquivos de `workflow-logs/` por padrão de nome em vez de Skip de diretório

Em vez de pular o diretório `workflow-logs/` inteiro com `filepath.SkipDir`, excluir seletivamente arquivos individuais cujos nomes correspondem a padrões de log de executor do GitHub Actions conhecidos (ex.: `*_Run log step.txt`). Isso seria frágil: convenções de nomenclatura de arquivo do GitHub Actions podem mudar, e qualquer arquivo não reconhecido inflaria silenciosamente as métricas novamente. Pular o diretório inteiro pelo nome é mais simples, robusto e alinha com como `downloadWorkflowRunLogs` coloca sua saída.

#### Alternativa 3: Armazenar métricas canônicas em um arquivo de lock separado

Registrar apenas as métricas (uso de token, turns) em um arquivo de lock dedicado separado do `run_summary.json`, e ler esse arquivo de lock em chamadas subsequentes. Isso adiciona complexidade ao sistema de arquivos sem benefício significativo sobre a reutilização da estrutura `run_summary.json` existente. O `loadRunSummary` atual já realiza validação de versão da CLI, fornecendo um mecanismo de invalidação automática limpo.

### Consequências

#### Positivas
- Chamadas `audit` repetidas para a mesma execução agora são determinísticas e produzem saída idêntica.
- O caminho de cache-hit contorna todas as chamadas de API e re-parsing de arquivos, tornando auditorias subsequentes significativamente mais rápidas.
- O helper de função `renderAuditReport` elimina a lógica duplicada de renderização + finalização que existia anteriormente tanto no caminho de fresh-download quanto no (agora) caminho de cache-hit.
- A invalidação de cache na atualização da CLI é automática via a verificação de `CLIVersion` existente em `loadRunSummary`.

#### Negativas
- A primeira chamada bem-sucedida de `audit` torna-se a fonte canônica da verdade. Se os arquivos de log estavam incompletos na primeira execução (ex.: download parcial), as métricas em cache estarão erradas até que o cache seja limpo manualmente ou a CLI seja atualizada.
- A exclusão de `workflow-logs/` é uma heurística baseada em nome de diretório. Se `downloadWorkflowRunLogs` alterar o nome do diretório de saída, a exclusão para de funcionar silenciosamente.
- Adicionar um helper de nível superior (`renderAuditReport`) aumenta a superfície da API interna do pacote.

#### Neutras
- O formato `run_summary.json` é inalterado; apenas a ordenação de leitura/escrita é ajustada (save-before-render no caminho de fresh-download).
- Testes existentes para `loadRunSummary` e `saveRunSummary` permanecem válidos; novos testes de regressão foram adicionados para o caminho de cache-hit e a exclusão de `workflow-logs/`.

---

## Parte 2 — Especificação Normativa (RFC 2119)

> As palavras-chave **DEVEM**, **NÃO DEVEM**, **OBRIGATÓRIO**, **SHALL**, **SHALL NOT**, **RECOMENDADO**, **MAY** e **OPCIONAL** nesta seção devem ser interpretadas conforme descrito em [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### Estratégia de Auditoria Cache-First

1. Implementações **DEVEM** verificar um `run_summary.json` válido em disco antes de iniciar qualquer chamada de API ou processamento de arquivo de log em `AuditWorkflowRun`.
2. Implementações **DEVEM** tratar um cache hit ( `run_summary.json` válido com `CLIVersion` correspondente) como a fonte autoritativa de métricas e retornar imediatamente sem reprocessar logs.
3. Implementações **NÃO DEVEM** sobrescrever um `run_summary.json` existente ao servir um cache hit; o arquivo em cache **DEVE** permanecer inalterado.
4. Implementações **DEVEM** persistir `run_summary.json` em disco antes de chamar o passo de renderização no caminho de fresh-download, para que uma falha de renderização não impeça futuros cache hits.
5. Implementações **DEVEM** registrar uma mensagem (no nível de verbosidade apropriado) indicando que um resumo em cache está sendo usado, incluindo o timestamp original `ProcessedAt`.

### Extração de Métrica de Log

1. Implementações **DEVEM** pular o diretório `workflow-logs/` (e seus conteúdos) ao caminhar pelo diretório de saída de execução em `extractLogMetrics`.
2. Implementações **DEVEM** usar `filepath.SkipDir` (ou equivalente) para excluir toda a subárvore `workflow-logs/`, não arquivos individuais dentro dela.
3. Implementações **NÃO DEVEM** incluir dados de uso de token encontrados em `workflow-logs/` nos totais de `LogMetrics.TokenUsage` ou `LogMetrics.Turns`.
4. Implementações **MAY** registrar uma mensagem de depuração ao pular o diretório `workflow-logs/` para auxiliar em diagnósticos futuros.

### Caminho de Renderização Compartilhado

1. Implementações **DEVEM** usar uma única função compartilhada (atualmente `renderAuditReport`) para construir e emitir o relatório de auditoria, invocada tanto pelo caminho de cache-hit quanto pelo caminho de fresh-download.
2. A função de renderização compartilhada **NÃO DEVE** re-extrair métricas de arquivos de log; ela **DEVE** usar apenas as métricas passadas a ela pelo chamador.

### Conformidade

Uma implementação é considerada em conformidade com este ADR se satisfizer todos os requisitos **DEVEM** e **NÃO DEVEM** acima. A falha em atender a qualquer requisito **DEVE** ou **NÃO DEVE** constitui não conformidade.

---

*Este é um ADR de RASCUNHO gerado pelo workflow [Design Decision Gate](https://github.com/github/gh-aw/actions/runs/24396807146) workflow. O autor do PR deve revisar, completar e finalizar este documento antes que o PR possa ser mesclado.*
