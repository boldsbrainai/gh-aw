# ADR-25819: Etapa Unificada de Detecção de Erros do Copilot com Sem-Repetição em Erros de Política

**Data**: 11/04/2026
**Status**: Rascunho (Draft)
**Decisores**: Desconhecido (gerado a partir do diff do PR #25819)

---

## Parte 1 — Narrativa (Amigável para Humanos)

### Contexto

O engine Copilot do gh-aw deve lidar com duas classes de falha distintas e não transitórias que se manifestam em tempo de execução:
(1) **erros de acesso à inferência** — o `COPILOT_GITHUB_TOKEN` é válido, mas carece de acesso à inferência do Copilot (apresentado como "Access denied by policy settings"); e
(2) **erros de política MCP** — uma política de empresa ou organização desabilitou os servidores MCP para o Copilot CLI, fazendo com que todos os servidores MCP configurados sejam silenciosamente bloqueados (apresentado como "MCP servers were blocked by policy").
Antes desta mudança, cada classe de falha era detectada por um script bash dedicado (`detect_inference_access_error.sh` e `detect_mcp_policy_error.sh`) injetado como etapas separadas pós-execução, e o script driver do Copilot repetia (retry) em *todas* as falhas — incluindo esses erros permanentes de configuração.
A duplicação aumentava a carga de manutenção, os scripts bash eram difíceis de testar unitariamente e a repetição em erros de política desperdiçava processamento sem qualquer chance de sucesso.

### Decisão

Consolidaremos ambos os scripts de detecção de erros em um único script Node.js (`detect_copilot_errors.cjs`) que varre o log stdio do agente em busca de ambos os padrões de erro em uma única passagem e define ambas as saídas (outputs) da etapa do GitHub Actions de forma atômica.
Escolhemos JavaScript em vez de bash porque a lógica de detecção já roda no mesmo runtime Node.js que o driver do Copilot, permitindo testes unitários baseados em Jest com constantes compartilhadas e eliminando uma classe de problemas de citação (quoting) e portabilidade do bash.
Além disso, adicionaremos um caminho explícito de saída antecipada no loop de repetição do driver para erros de política MCP: quando o padrão `MCP_POLICY_BLOCKED_PATTERN` é detectado, o driver sai do loop de repetição imediatamente em vez de aguardar e invocar novamente o Copilot CLI, pois a configuração de política é uma restrição externa persistente que nenhuma quantidade de repetições pode resolver.
O compilador Go (`generateCopilotErrorDetectionStep`) é atualizado para emitir uma única etapa em vez de duas funções separadas.

### Alternativas Consideradas

#### Alternativa 1: Reter dois scripts bash separados, adicionar um terceiro para política MCP

A mudança mais simples teria sido adicionar apenas o comportamento de não-repetição no driver e manter os dois scripts de detecção bash inalterados, adicionando um terceiro script bash para detecção de política MCP.
Isso foi rejeitado porque aumentaria a contagem de scripts de runtime para três, manteria a detecção baseada em bash que é difícil de testar unitariamente e perderia a oportunidade de definir ambas as saídas atômicas e compartilhar constantes de padrões entre o script de detecção e o driver.

#### Alternativa 2: Consolidação em um único script bash

Ambos os padrões de detecção behemoth poderiam ter sido mesclados em um único script bash (substituindo os dois scripts bash existentes) sem mudar para JavaScript.
Isso foi rejeitado porque a lógica de repetição do driver já está implementada em JavaScript e já precisava da constante `MCP_POLICY_BLOCKED_PATTERN` para a decisão de não-repetição; duplicar o padrão em bash e JavaScript criaria um ponto único de divergência onde uma atualização futura de padrão poderia ser feita em apenas um lugar.

#### Alternativa 3: Sinalização de erro estruturada do Copilot CLI

A solução ideal a longo prazo seria o Copilot CLI emitir códigos de saída legíveis por máquina ou saídas estruturadas para cada classe de falha, tornando a raspagem de logs (log scraping) desnecessária.
Isso não era viável no momento desta decisão porque os sinais de erro originam-se dentro do binário do Copilot CLI, que é uma base de código separada fora do controle do gh-aw.
Esta opção permanece aberta para adoção futura quando erros estruturados estiverem disponíveis a montante (upstream).

### Consequências

#### Positivas
- Ambos os tipos de erro são detectados em uma única passagem de varredura de log, reduzindo E/S em arquivos de log grandes.
- As constantes de padrão (`INFERENCE_ACCESS_ERROR_PATTERN`, `MCP_POLICY_BLOCKED_PATTERN`) são compartilhadas entre `detect_copilot_errors.cjs` e `copilot_driver.cjs`, garantindo que estejam sempre em sincronia.
- O script de detecção é coberto por testes unitários Jest com strings de fixture explícitas, oferecendo maior confiança do que os scripts bash baseados em `grep`.
- A repetição em erros de política MCP é eliminada, evitando desperdício de orçamento de processamento e logs confusos de múltiplas tentativas quando um problema de nível de configuração nunca se resolverá sozinho.
- Orientações acionáveis (como reabilitar servidores MCP em configurações de empresa/org) são apresentadas em issues de falha via um template Markdown com divulgação progressiva.

#### Negativas
- A etapa de detecção depende do Node.js estar disponível em `${RUNNER_TEMP}/gh-aw/actions/`; se a ação de configuração falhar ao copiar os scripts, nenhum tipo de erro será detectado.
- A detecção permanece baseada em raspagem de logs, o que é frágil contra mudanças nas mensagens do Copilot CLI. Qualquer reformulação futura das strings de erro exigirá uma atualização coordenada de padrões no gh-aw.
- A saída antecipada de não-repetição significa que um soluço de rede transitório que coincidentemente produza uma linha de log semelhante à política MCP não seria repetido (embora tais coincidências sejam consideradas improváveis dada a especificidade do padrão).

#### Neutras
- Os dois scripts bash (`detect_inference_access_error.sh`, `detect_mcp_policy_error.sh`) são removidos, reduzindo o número total de scripts de runtime em dois.
- Todos os arquivos de trava (lock files) de workflow compilados (`.lock.yml`) são regenerados para referenciar `detect-copilot-errors` em vez de `detect-inference-error` e para incluir a nova saída `mcp_policy_error`.
- As funções do compilador Go `generateInferenceAccessErrorDetectionStep` (e a agora removida `generateMCPPolicyErrorDetectionStep`) são substituídas pela única função `generateCopilotErrorDetectionStep`.

---

## Parte 2 — Especificação Normativa (RFC 2119)

> As palavras-chave **DEVE**, **NÃO DEVE**, **OBRIGATÓRIO**, **DEVERÁ**, **NÃO DEVERÁ**, **DEVERIA**, **NÃO DEVERIA**, **RECOMENDADO**, **PODE** e **OPCIONAL** nesta seção devem ser interpretadas conforme descrito em [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### Script de Detecção de Erros

1. As implementações **DEVEM** usar um único passo JavaScript (`detect_copilot_errors.cjs`) para detectar tanto `inference_access_error` quanto `mcp_policy_error` a partir do log stdio do agente em uma única execução.
2. As implementações **NÃO DEVEM** usar scripts bash separados para detecção individual de tipos de erro do Copilot CLI; toda a detecção de erro específica do Copilot **DEVE** ser consolidada em `detect_copilot_errors.cjs`.
3. O script de detecção **DEVE** definir tanto `inference_access_error` quanto `mcp_policy_error` as saídas de etapa do GitHub Actions, independentemente de qual erro (se houver) foi detectado.
4. A etapa de detecção **DEVE** ser executada com `if: always()` e `continue-on-error: true` para que falhas de detecção não bloqueiem a conclusão do fluxo de trabalho.
5. As constantes de padrão usadas para varredura de log **DEVEM** ser exportadas de `detect_copilot_errors.cjs` (via `module.exports`) para que possam ser importadas e reutilizadas por outros scripts (ex: o driver) sem duplicação.

### Comportamento de Repetição do Driver

1. O driver do Copilot **NÃO DEVE** repetir uma execução cuja saída corresponda a `MCP_POLICY_BLOCKED_PATTERN`; ele **DEVE** sair do loop de repetição imediatamente e propagar o código de saída.
2. O driver **DEVERIA** registrar uma mensagem legível por humanos ao ignorar uma repetição devido a um erro de política, explicando que a falha é um problema de configuração em vez de um erro transitório.
3. Para todas as outras classes de falha, as regras de repetição do driver **DEVEM** permanecer inalteradas: até `MAX_RETRIES` tentativas com back-off exponencial.

### Geração de Etapa do Compilador (Go)

1. O compilador Go **DEVE** emitir exatamente uma etapa `detect-copilot-errors` para o engine Copilot (substituindo quaisquer etapas separadas anteriores de detecção de inferência/MCP).
2. O compilador **NÃO DEVE** emitir etapas `detect-inference-error` ou `detect-mcp-policy-error` separadas.
3. As saídas do job do agente **DEVEM** incluir tanto `inference_access_error` quanto `mcp_policy_error` conectadas de `steps.detect-copilot-errors.outputs.*` para o engine Copilot.
4. Essas saídas **NÃO DEVEM** ser emitidas para engines que não sejam Copilot.

### Conformidade

Uma implementação é considerada em conformidade com este ADR se satisfizer todos os requisitos **DEVE** e **NÃO DEVE** acima. Falha em atender a qualquer requisito **DEVE** ou **NÃO DEVE** constitui não conformidade.

---

*ADR criado pelo [agente adr-writer]. Revise e finalize antes de alterar o status de Rascunho para Aceito.*
