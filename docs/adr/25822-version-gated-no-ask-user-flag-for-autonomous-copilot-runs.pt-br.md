# ADR-25822: Flag --no-ask-user com Version-Gating para Execuções Autônomas do Agente Copilot

**Data**: 2026-04-11
**Status**: Rascunho
**Decisores**: pelikhan, Agente Copilot SWE

---

## Parte 1 — Narrativa (Amigável)

### Contexto

O engine agentic do Copilot orquestra execuções via CLI no GitHub Actions. Prompts interativos na CLI do Copilot podem bloquear execuções totalmente automatizadas, uma vez que não há operador humano para responder. A flag `--no-ask-user` foi introduzida na Copilot CLI v1.0.19 para suprimir todos os prompts interativos, permitindo a execução headless/autônoma. No entanto, fluxos de trabalho (workflows) podem estar fixados (pinned) em uma versão explícita da Copilot CLI (ex.: por estabilidade ou teste), e emitir `--no-ask-user` em uma versão da CLI que não reconhece a flag faz com que a execução falhe imediatamente na inicialização. Portanto, é necessário um mecanismo para emitir a flag condicionalmente com base na versão efetiva da CLI.

### Decisão

Adicionaremos um helper de version-gate (`copilotSupportsNoAskUser`) que inspeciona a `EngineConfig.Version` do workflow e retorna `true` apenas quando a versão da CLI configurada for ≥ 1.0.19 (a versão mínima que aceita `--no-ask-user`). A flag é emitida durante a construção de argumentos em `GetExecutionSteps` tanto para trabalhos (jobs) de agente quanto de detecção quando a versão a suporta. Versões não especificadas e `"latest"` são tratadas como sempre suportadas; strings que não seguem o semver (ex.: nomes de branch) são tratadas de forma conservadora como não suportadas. Este padrão espelha os helpers existentes `awfSupportsExcludeEnv` e `awfSupportsCliProxy`, estendendo a convenção estabelecida de version-gate nesta base de código.

### Alternativas Consideradas

#### Alternativa 1: Sempre emitir --no-ask-user incondicionalmente

Emitir a flag para todos os jobs de agente independentemente da versão da CLI configurada. É mais simples (sem verificação de versão) e garante que todas as execuções se beneficiem do modo autônomo. Foi rejeitada porque quebraria imediatamente qualquer workflow fixado em uma versão da CLI anterior à 1.0.19: a CLI trata flags desconhecidas como erros fatais, o que impediria esses usuários de executar qualquer coisa sem uma atualização forçada de versão.

#### Alternativa 2: Exigir que os chamadores optem via uma chave de configuração explícita de workflow

Adicionar um campo `noAskUser: true` ao YAML do workflow ou à struct `EngineConfig`, exigindo que os autores dos workflows habilitem a flag explicitamente. Isso dá aos autores controle total. Foi rejeitada porque a flag é incondicionalmente desejável para qualquer execução automatizada — não há cenário onde uma versão moderna da CLI deva manter prompts interativos em um contexto de CI — tornando o opt-in explícito um atrito desnecessário sem benefício de segurança.

#### Alternativa 3: Usar uma sonda de capacidade da CLI em tempo de execução (parsing de --help)

Detectar suporte invocando a CLI com `--help` no momento da geração do workflow e fazendo o parse da saída em busca de `--no-ask-user`. Isso seria perfeitamente preciso sem hard-coding de um número de versão. Foi rejeitada porque introduz uma dependência de execução de subprocesso no momento da geração do passo (que atualmente não possui efeitos colaterais externos), adiciona latência e cria uma dependência frágil no texto de ajuda da CLI. Uma comparação de semver contra uma constante bem conhecida é mais simples, auditável e fácil de atualizar.

### Consequências

#### Positivas
- Execuções autônomas de agente são habilitadas por padrão para todos os workflows usando Copilot CLI ≥ 1.0.19, eliminando o risco de execuções travarem em prompts interativos.
- O padrão de version-gate é consistente com helpers existentes (`awfSupportsExcludeEnv`, `awfSupportsCliProxy`), reduzindo a sobrecarga cognitiva para contribuidores familiarizados com a base de código.
- O tratamento conservador de strings de versão que não são semver garante que a flag nunca seja emitida em casos ambíguos, protegendo contra comportamentos inesperados da CLI.

#### Negativas
- Uma constante de versão (`CopilotNoAskUserMinVersion = "1.0.19"`) deve ser mantida precisa conforme a CLI evolui; se uma regressão fizer com que uma versão mais antiga também aceite a flag, a constante seria desnecessariamente restritiva (embora não prejudicial).
- A detecção de se um job é um "job de agente" vs. um "job de detecção" depende do sentinela `SafeOutputs == nil`, que é uma convenção implícita em vez de um enum explícito de tipo de job. Futuros refactors de `WorkflowData` devem preservar esse invariante ou atualizar a proteção.

#### Neutras
- A declaração da variável `isDetectionJob` foi movida para cima em `GetExecutionSteps` para ser compartilhada tanto pelo bloco `--no-ask-user` quanto pelo bloco existente `--autopilot`. Este é um refactor puro sem mudança comportamental.
- Arquivos de lock foram regenerados como parte da atualização do grafo de dependências disparada pela mudança no código.

---

## Parte 2 — Especificação Normativa (RFC 2119)

> As palavras-chave **DEVEM**, **NÃO DEVEM**, **OBRIGATÓRIO**, **SHALL**, **SHALL NOT**, **RECOMENDADO**, **MAY** e **OPCIONAL** nesta seção devem ser interpretadas conforme descrito em [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### Emissão de Flag

1. Implementações **DEVEM** emitir `--no-ask-user` para a lista de argumentos da Copilot CLI tanto para jobs de agente quanto de detecção quando a versão efetiva da CLI for ≥ `CopilotNoAskUserMinVersion` (atualmente `1.0.19`).
2. Implementações **NÃO DEVEM** emitir `--no-ask-user` quando a versão efetiva da CLI for uma string semver estritamente menor que `CopilotNoAskUserMinVersion`.
3. Implementações **NÃO DEVEM** emitir `--no-ask-user` quando a versão efetiva da CLI for uma string que não é semver (ex.: nome de branch), tratando tais casos de forma conservadora como não suportados.
4. Implementações **DEVEM** tratar uma versão não especificada (`EngineConfig` nil ou `EngineConfig.Version` vazio) como suportada, uma vez que `DefaultCopilotVersion` é sempre ≥ `CopilotNoAskUserMinVersion`.
5. Implementações **DEVEM** tratar a string literal `"latest"` (case-insensitive) como suportada, uma vez que `latest` sempre resolve para uma release atual.

### Helper de Version Gate

1. A lógica de version-gate **DEVE** ser encapsulada em uma função helper dedicada (`copilotSupportsNoAskUser`) seguindo o mesmo padrão de `awfSupportsExcludeEnv` e `awfSupportsCliProxy`.
2. A versão mínima suportada **DEVE** ser definida como a constante nomeada `CopilotNoAskUserMinVersion` em `pkg/constants/version_constants.go`; ela **NÃO DEVE** ser inlined como um literal de string nos locais de chamada.
3. Quando `CopilotNoAskUserMinVersion` for atualizada, os testes unitários correspondentes **DEVEM** ser atualizados para refletir a nova versão limite.

### Testes

1. O comportamento de emissão da flag **DEVE** ser coberto por testes de integração que exercitem `GetExecutionSteps` com a matriz completa de combinações de versão e tipo de job.
2. O helper de version-gate **DEVE** ser coberto por testes unitários que incluam: config nil, versão vazia, `"latest"`, a versão mínima exata, uma versão acima da mínima, uma versão abaixo da mínima e uma string que não é semver.
3. Testes **NÃO DEVEM** usar mocks para a lógica de comparação de versão; a função `compareVersions` real **DEVE** ser exercitada.

### Conformidade

Uma implementação é considerada em conformidade com este ADR se satisfizer todos os requisitos **DEVEM** e **NÃO DEVEM** acima. Em particular: `--no-ask-user` **DEVE** ser gated pela versão da CLI (≥ 1.0.19 ou não especificada/latest). A falha em atender a qualquer requisito **DEVEM** ou **NÃO DEVE** constitui não conformidade.

---

*ADR criado pelo agente [adr-writer agent]. Revise e finalize antes de alterar o status de Rascunho para Aceito.*
