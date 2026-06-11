# ADR-25902: Pré-Limpeza de Diretórios de Firewall obsoletos e Propagação de Funcionalidades no Job de Detecção

**Data**: 2026-04-12
**Status**: Rascunho
**Decisores**: Desconhecido (inferido do PR #25902 pelo Copilot)

---

## Parte 1 — Narrativa (Amigável)

### Contexto

O PR #25868 mesclou arquivos de auditoria/log do firewall (squid.conf, cache.log, access.log, etc.) no artefato unificado do agente. Quando o job de detecção baixa este artefato, ele extrai para `/tmp/gh-aw/`, o que pré-popula `sandbox/firewall/logs` e `sandbox/firewall/audit` com arquivos de uma execução de agente concluída. O contêiner squid do AWF (Agent Workflow Firewall) então trava na inicialização com código de saída 1 porque o squid não consegue inicializar quando esses diretórios já estão povoados por uma execução anterior. Separadamente, `buildPullAWFContainersStep` construía um `WorkflowData` minimalista sem o campo `Features`, então quando a flag de funcionalidade `copilot-requests` era habilitada, a imagem `cli-proxy` era omitida silenciosamente do pré-pull de contêineres do job de detecção.

### Decisão

Adicionaremos uma função `buildCleanFirewallDirsStep()` que executa `rm -rf` em `AWFProxyLogsDir` e `AWFAuditDir` como o primeiro passo no job de detecção, imediatamente após o download do artefato e antes de qualquer inicialização de contêiner. Também propagaremos `Features: data.Features` para dentro do `WorkflowData` minimalista construído dentro de `buildPullAWFContainersStep()`, correspondendo ao padrão de propagação já usado em `buildDetectionEngineExecutionStep()`. Essas duas correções são agrupadas porque ambas corrigem falhas silenciosas na fase de inicialização do job de detecção.

### Alternativas Consideradas

#### Alternativa 1: Excluir diretórios de Firewall do artefato do agente

O passo de upload de artefato do job de agente poderia ser modificado para excluir `sandbox/firewall/logs` e `sandbox/firewall/audit` do artefato unificado. Isso impediria que o job de detecção recebesse arquivos obsoletos. Não foi escolhida porque exige mudanças na lógica de construção de artefatos do job de agente (uma preocupação separada), arrisca excluir acidentalmente metadados de firewall que futuros passos de detecção podem precisar e não corrige a causa raiz—o contêiner squid do job de detecção deve tolerar qualquer estado pré-existente nos seus diretórios de trabalho.

#### Alternativa 2: Reconfigurar o Squid para ignorar conteúdos de diretório pré-existentes

O contêiner squid poderia ser iniciado com flags de configuração ou um wrapper de inicialização que limpa ou ignora diretórios de cache e log existentes. Isso tornaria o job de detecção resiliente independentemente dos conteúdos do artefato. Não foi escolhida porque exige mudanças na imagem do contêiner AWF ou nos seus scripts de inicialização, que são mantidos em um repositório separado (`gh-aw-firewall`), tornando a correção mais invasiva e lenta para implantar do que um passo de pré-limpeza no workflow compilado.

#### Alternativa 3: Reestruturar o artefato para usar um caminho de extração diferente

O job de detecção poderia baixar o artefato do agente para um local temporário e copiar seletivamente apenas os arquivos necessários (prompt.txt, agent_output.json, patches), nunca extraindo para `/tmp/gh-aw/`. Isso impediria totalmente que qualquer conteúdo de artefato poluísse os diretórios de firewall. Não foi escolhida porque exige um refactor significativo de `buildAgentOutputDownloadSteps` e das convenções de caminho de artefato seguidas por múltiplos passos a jusante (downstream), tornando-a uma mudança de maior risco do que uma pré-limpeza direcionada.

### Consequências

#### Positivas
- O contêiner squid do job de detecção inicia de forma confiável, independentemente do que o artefato do agente depositou nos diretórios de firewall.
- A imagem `cli-proxy` é incluída corretamente no pré-pull de contêineres do job de detecção quando a flag de funcionalidade `copilot-requests` está habilitada, evitando lacunas silenciosas de funcionalidade entre o job de agente e o job de detecção.
- A correção é mínima e localizada—uma nova função e uma adição de campo—com baixo risco de regressão.

#### Negativas
- O passo de pré-limpeza é executado incondicionalmente em cada invocação do job de detecção, mesmo quando os diretórios de firewall estão vazios. Isso adiciona um `rm -rf` trivialmente rápido a cada job de detecção, mas é efetivamente um no-op em ambientes que não incluem arquivos de firewall no artefato.
- O passo de limpeza deleta permanentemente os conteúdos de `AWFProxyLogsDir` e `AWFAuditDir` antes que o contêiner squid seja executado. Se lógica futura precisar preservar o estado do firewall vindo do artefato para propósitos de detecção, este passo precisaria ser revisitado.

#### Neutras
- A mudança na propagação de `Features` coloca `buildPullAWFContainersStep` em alinhamento com o padrão existente em `buildDetectionEngineExecutionStep`, reduzindo a inconsistência em como o job de detecção constrói seu `WorkflowData` minimalista.
- Testes (`TestCleanFirewallDirsStepPresent`, `TestCleanFirewallDirsStepOrdering`, `TestBuildPullAWFContainersStepPropagatesFeatures`) codificam a restrição de ordenação e o requisito de propagação de funcionalidade como documentação executável.

---

## Parte 2 — Especificação Normativa (RFC 2119)

> As palavras-chave **DEVEM**, **NÃO DEVEM**, **OBRIGATÓRIO**, **SHALL**, **SHALL NOT**, **RECOMENDADO**, **MAY** e **OPCIONAL** nesta seção devem ser interpretadas conforme descrito em [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### Inicialização do Job de Detecção

1. O job de detecção **DEVE** executar um passo de limpeza de diretório de firewall antes de qualquer passo de inicialização de contêiner AWF.
2. O passo de limpeza **DEVE** remover `AWFProxyLogsDir` e `AWFAuditDir` usando `rm -rf`, tolerando o caso onde esses diretórios não existem.
3. O passo de limpeza **NÃO DEVE** ser condicionado à saída do guard de detecção — ele **SHALL** ser executado incondicionalmente para que os contêineres nunca encontrem estado obsoleto.
4. Implementações **DEVEM** usar as constantes simbólicas `constants.AWFProxyLogsDir` e `constants.AWFAuditDir` em vez de caminhos hardcoded, para que mudanças de caminho sejam propagadas automaticamente.

### Propagação de WorkflowData em Pré-Pull de Contêiner

1. `buildPullAWFContainersStep` **DEVE** propagar o campo `Features` do `WorkflowData` pai para dentro do `WorkflowData` minimalista que ele constrói para `collectDockerImages`.
2. Qualquer campo do `WorkflowData` pai que afete quais imagens de contêiner são coletadas (incluindo `ActionCache` e `Features`) **DEVE** ser propagado para dentro do `WorkflowData` minimalista usado para coleta de imagens no job de detecção.
3. Implementações **NÃO DEVEM** omitir campos de flag de funcionalidade ao construir instâncias minimalistas de `WorkflowData` para sub-passos do job de detecção, pois a omissão altera silenciosamente o comportamento de seleção de imagem.

### Conformidade

Uma implementação é considerada em conformidade com este ADR se satisfizer todos os requisitos **DEVEM** e **NÃO DEVEM** acima. Especificamente: o ordenamento de passos do job de detecção coloca a limpeza do diretório de firewall antes de qualquer passo de pull de contêiner, o passo de limpeza é executado incondicionalmente e `buildPullAWFContainersStep` propaga `Features` (e `ActionCache`) do `WorkflowData` pai. A falha em atender a qualquer requisito **DEVE** ou **NÃO DEVE** constitui não conformidade.

---

*Este é um ADR de RASCUNHO gerado pelo workflow [Design Decision Gate](https://github.com/github/gh-aw/actions/runs/24307339373). O autor do PR deve revisar, completar e finalizar este documento antes que o PR possa ser mesclado.*
