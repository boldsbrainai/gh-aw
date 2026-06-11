# ADR-0002: Permitir Segredos (Secrets) em Vinculações env: de Nível de Etapa Sob Modo Estrito (Strict Mode)

**Data**: 11/04/2026
**Status**: Rascunho (Draft)
**Decisores**: pelikhan, Copilot

---

## Parte 1 — Narrativa (Amigável para Humanos)

### Contexto

O compilador de fluxo de trabalho (workflow) impõe um "modo estrito" (strict mode) que restringe quais expressões do GitHub Actions os autores podem usar em campos de etapas (steps) definidos pelo usuário, com o objetivo de evitar que segredos vazem para o ambiente de trabalho do agente. Antes desta mudança, o modo estrito aplicava uma regra de "tudo ou nada": a presença de *qualquer* expressão `${{ secrets.* }}` em `pre-steps`, `steps` ou `post-steps` era um erro, independentemente de onde a expressão aparecia dentro da etapa. Isso forçava autores que precisavam de credenciais de ferramentas (tokens de API, chaves OAuth, tokens SonarQube, etc.) a desativar o modo estrito inteiramente via `strict: false`, abrindo mão de todas as outras proteções que o modo oferece. A plataforma GitHub Actions já distingue entre superfícies controladas de segredos: um segredo vinculado ao mapa `env:` de uma etapa é automaticamente mascarado pelo runner antes que possa aparecer nos logs, enquanto um segredo interpolado diretamente em uma string de script `run:` pode ser exibido (echoed), registrado ou passado para um processo externo antes que o mascaramento entre em vigor.

### Decisão

Introduziremos uma classificação por campo de referências a segredos dentro de uma etapa, distinguindo vinculações "seguras" (campos `env:`, que são automaticamente mascarados pelo GitHub Actions, e entradas `with:` para etapas de ação `uses:`, que são passadas para ações externas e mascaradas pelo runner) de interpolações inline "inseguras" (`run:` e todos os outros campos de etapa). No modo estrito, apenas referências inseguras a segredos serão tratadas como erros; segredos que aparecem exclusivamente em vinculações seguras serão permitidos. Implementamos isso por meio de um novo auxiliar `classifyStepSecrets()` que divide as referências a segredos de uma etapa e atualizamos `validateStepsSectionSecrets()` para bloquear apenas a partição insegura sob o modo estrito.

### Alternativas Consideradas

#### Alternativa 1: Manter o bloqueio existente de "tudo ou nada"

Manter a política atual — todas as referências a `secrets.*` são erros no modo estrito — é a abordagem mais simples. Foi rejeitada porque cria um custo ergonômico inaceitável: workflows que precisam fornecer tokens de API para ferramentas de varredura (um padrão comum no mundo real) devem desativar o modo estrito inteiramente, removendo a proteção contra outras classes de vazamento de segredos que o modo estrito previne. Os próprios jobs gerados pelo framework já usam vinculações `env:` para segredos, tornando inconsistente bloquear esse mesmo padrão em etapas definidas pelo usuário.

#### Alternativa 2: Permitir todos os segredos no modo estrito

Relaxar o modo estrito para permitir segredos em todos os lugares (equivalente ao modo não estrito, mas sem o aviso) facilitaria ao máximo o fardo do autor. Foi rejeitada porque remove a proteção central que o modo estrito foi projetado para fornecer: evitar a interpolação inline acidental de segredos em strings de comando onde eles podem ser observados antes que a lógica de mascaramento do runner seja acionada.

#### Alternativa 3: Introduzir uma anotação por etapa para optar pela permissão

Uma terceira opção seria manter os segredos bloqueados por padrão, mas permitir que os autores anotassem etapas individuais (ex: com uma flag `allow-secrets: true`) para optar pelo acesso aos segredos. Isso foi rejeitado como desnecessariamente complexo: o padrão de vinculação `env:` já é um idioma bem estabelecido do GitHub Actions, portanto, usar a localização estrutural da referência (nome do campo `env` vs. qualquer outro campo) como sinal fornece uma fronteira de segurança equivalente sem exigir nova sintaxe.

### Consequências

#### Positivas
- Workflows que fornecem credenciais de ferramentas via vinculações `env:` ou entradas `with:` (para etapas de ação `uses:`) não precisam mais desativar o modo estrito inteiramente, preservando todas as outras proteções do modo estrito.
- A política de imposição agora reflete como os próprios jobs gerados pelo framework lidam com segredos, tornando o modelo de segurança internamente consistente.
- A mensagem de erro para segredos bloqueados agora sugere explicitamente vinculações `env:` e entradas `with:` como alternativas, melhorando a experiência do desenvolvedor.
- O comportamento se alinha com a garantia nativa de mascaramento do GitHub Actions: as vinculações `env:` e entradas `with:` são mascaradas pelo runner antes da execução do comando.
- Workflows corporativos que usam gerenciadores de segredos centralizados (ex: Conjur, HashiCorp Vault) via GitHub Actions dedicados agora podem usar o modo estrito, passando credenciais de autenticação via entradas `with:`.

#### Negativas
- A política de segurança agora é mais matizada: os revisores devem entender a distinção entre `env:`/`with:` vs. inline, em vez de uma regra geral simples, aumentando a superfície de raciocínio.
- A função `classifyStepSecrets()` deve ser mantida precisa à medida que o modelo de dados de etapa evolui; um campo classificado incorretamente poderia rebaixar silenciosamente um segredo de "inseguro" para "seguro".
- O modo não estrito ainda emite um aviso para todos os segredos (incluindo os vinculados de forma segura), o que pode ser ligeiramente enganoso agora que vinculações seguras são permitidas no modo estrito.

#### Neutras
- Workflows existentes que usavam `strict: false` especificamente para permitir vinculações seguras podem agora remover essa sobreposição e adotar o modo estrito, mas essa migração é voluntária.
- Testes unitários e de integração devem agora cobrir tanto o caminho permitido de "apenas vinculação segura" quanto o caminho bloqueado de "misto seguro + execução" para manter a cobertura adequada.

---

## Parte 2 — Especificação Normativa (RFC 2119)

> As palavras-chave **DEVE**, **NÃO DEVE**, **OBRIGATÓRIO**, **DEVERÁ**, **NÃO DEVERÁ**, **DEVERIA**, **NÃO DEVERIA**, **RECOMENDADO**, **PODE** e **OPCIONAL** nesta seção devem ser interpretadas conforme descrito em [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### Classificação de Segredos

1. As implementações **DEVEM** classificar cada referência `${{ secrets.* }}` dentro de uma etapa pelo nome do campo YAML no qual ela aparece.
2. Uma referência a segredo encontrada dentro de um mapeamento `env:` bem formado (ou seja, o valor de `env:` é um mapa YAML de pares chave-valor) **DEVE** ser classificada como uma referência *segura*.
3. Uma referência a segredo encontrada dentro de um valor `env:` malformado (ex: `env:` é uma string simples ou uma sequência YAML) **DEVE** ser classificada como uma referência *insegura*, pois o runner não pode aplicar mascaramento por variável a tais valores.
4. Uma referência a segredo encontrada dentro de um mapeamento `with:` bem formado em uma etapa que também possui um campo `uses:` **DEVE** ser classificada como uma referência *segura*, pois as entradas `with:` são passadas para a ação externa (não interpoladas em scripts shell) e o runner mascara valores derivados de segredos.
5. Uma referência a segredo encontrada dentro de um mapeamento `with:` em uma etapa que NÃO possui um campo `uses:` **DEVE** ser classificada como uma referência *insegura*.
6. Uma referência a segredo encontrada dentro de um valor `with:` malformado (ex: `with:` é uma string simples ou uma sequência YAML) **DEVE** ser classificada como uma referência *insegura*.
7. Uma referência a segredo encontrada em qualquer outro campo de etapa (incluindo, mas não se limitando a `run:`, `name:`, `if:`) **DEVE** ser classificada como uma referência *insegura*.
8. Um valor de etapa que não seja um mapa YAML (ex: uma string bruta) **DEVE** tratar todas as referências a segredos dentro dele como referências *inseguras*.
9. Quando uma etapa contém referências *seguras* a segredos E qualquer campo que não seja `env:`/`with:` referencia `GITHUB_ENV`, as implementações **DEVEM** reclassificar todas as referências *seguras* naquela etapa como *inseguras*, pois a escrita em `GITHUB_ENV` persiste segredos para etapas subsequentes (incluindo a etapa do agente).

### Imposição do Modo Estrito

1. Quando o modo estrito está ativo, as implementações **DEVEM** retornar um erro se uma ou mais referências *inseguras* a segredos forem encontradas em uma seção `pre-steps`, `steps` ou `post-steps`.
2. Quando o modo estrito está ativo, as implementações **NÃO DEVEM** retornar um erro apenas pela presença de referências *seguras* a segredos em uma seção.
3. A mensagem de erro para segredos bloqueados no modo estrito **DEVERIA** sugerir o uso de vinculações `env:` de nível de etapa (para etapas `run:`) ou entradas `with:` (para etapas de ação `uses:`) como alternativas à interpolação inline.
4. O `GITHUB_TOKEN` integrado **DEVE** ser filtrado tanto das listas de referências *inseguras* quanto das *seguras* antes da imposição do modo estrito, pois ele está presente em cada ambiente de runner por padrão.

### Comportamento do Modo Não Estrito

1. Quando o modo estrito não está ativo, as implementações **DEVEM** emitir um aviso (para stderr) se quaisquer referências a segredos — sejam elas vinculadas ao ambiente ou inseguras — forem encontradas em uma seção de etapas.
2. As implementações **NÃO DEVEM** retornar um erro no modo não estrito para referências a segredos em seções de etapas; o aviso é apenas informativo.
3. As implementações **DEVERIAM** deduplicar os identificadores de referência a segredos antes de incluí-los em mensagens de aviso ou erro.

### Conformidade

Uma implementação é considerada em conformidade com este ADR se satisfizer todos os requisitos **DEVE** e **NÃO DEVE** acima. Em particular: permitir referências *inseguras* a segredos no modo estrito, ou bloquear referências *seguras* no modo estrito, são ambos comportamentos não conformes.

---

*Este é um rascunho de ADR gerado pelo fluxo de trabalho [Design Decision Gate](https://github.com/github/gh-aw/actions/runs/24279167784). O autor do PR deve revisar, completar e finalizar este documento antes que o PR possa ser mesclado.*
