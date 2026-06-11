# ADR-25821: Contexto de Fonte no Estilo Rust e Síntese em Linguagem Natural para Erros do Compilador

**Data**: 11/04/2026
**Status**: Rascunho (Draft)
**Decisores**: pelikhan, Copilot

---

## Parte 1 — Narrativa (Amigável para Humanos)

### Contexto

O compilador de fluxo de trabalho (workflow) do gh-aw produz mensagens de erro quando um arquivo de workflow contém uma configuração inválida. Antes desta decisão, coexistiam dois problemas distintos de qualidade. Primeiro, quando o campo `engine:` recebia um valor do tipo errado (ex: um número inteiro em vez de uma string), o compilador apresentava jargões brutos do JSON Schema, como `'oneOf' failed, none matched: got number, want string; got number, want object`, não oferecendo ao usuário nenhuma orientação acionável. Segundo, quando era usado um nome de engine com tipo válido, mas não reconhecido (ex: um erro de digitação como `copiilot`), a mensagem de erro identificava corretamente o problema, mas omitia as linhas de contexto do arquivo de origem, tornando mais difícil localizar o ponto exato. Os dois caminhos de código tinham uma qualidade de saída inconsistente, e a lacuna era maior precisamente quando os usuários estavam mais confusos.

### Decisão

Adotaremos a renderização de erros do compilador no estilo Rust como o padrão para erros de validação de nível de campo no compilador de workflow: erros que podem ser localizados em uma linha de código específica incluirão ±3 linhas de contexto de origem para permitir que o usuário veja o código problemático in-line. Simultaneamente, introduziremos a síntese em linguagem natural (Inglês simples/Português claro) para falhas de conflito de tipo `oneOf` do JSON Schema: quando cada ramificação de uma restrição `oneOf` falha com uma incompatibilidade de tipo, o compilador extrai os tipos reais e esperados e produz uma frase como `expected string or object, got number` (esperado string ou objeto, recebido número). Para campos bem conhecidos (atualmente `/engine`), uma tabela de dicas específica do campo anexa uma lista de valores válidos e um exemplo de uso, criando uma saída comparável aos compiladores de linguagens modernas (Rust, Go 1.20+).

### Alternativas Consideradas

#### Alternativa 1: Mensagem genérica de "tipo errado" sem dicas de campo

A correção mais simples seria substituir o jargão do JSON Schema por uma mensagem estática como `"invalid value: expected a string or object"` para todas as falhas de tipo `oneOf`. Isso foi considerado porque não requer manutenção por campo. Foi rejeitada porque omite os valores válidos, que é a informação mais acionável para o usuário — saber que `claude`, `codex`, `copilot` e `gemini` são aceitos é mais útil do que saber o tipo abstrato.

#### Alternativa 2: Busca de lista de engines em tempo de execução a partir do catálogo

Uma alternativa à tabela de dicas estática seria buscar a lista de nomes de engines válidos dinamicamente de `NewEngineCatalog()` no momento da notificação do erro. Isso tornaria a dica automaticamente precisa se novos engines integrados fossem adicionados. Não foi escolhida porque a formatação de erro está em `pkg/parser` (um pacote de nível inferior), enquanto o catálogo de engines reside em uma camada de nível superior; puxar a referência do catálogo para o parser criaria uma dependência indesejada. A lista estática é uma troca deliberada: exige uma atualização manual quando os engines integrados mudam, mas preserva a fronteira do pacote.

#### Alternativa 3: Erro apenas com posição (status quo para erros de nome de engine)

O caminho `formatCompilerErrorWithPosition` existente já era usado para erros de digitação no nome do engine (ex: `copiilot`). Manter esse caminho e corrigir apenas a mensagem de conflito de tipo foi considerado como uma mudança mínima. Foi rejeitada porque as linhas de contexto da fonte têm baixo custo para serem adicionadas (o conteúdo do arquivo já está na memória neste local de chamada) e melhoram significativamente o valor diagnóstico, alinhando a saída com as expectativas do usuário estabelecidas por compiladores modernos.

### Consequências

#### Positivas
- Erros de conflito de tipo para `engine:` agora são acionáveis sem exigir que o usuário consulte a documentação.
- Erros de digitação no nome do engine agora mostram um trecho de código no estilo Rust com um ponteiro de coluna, igualando a qualidade da saída aos erros de validação de esquema.
- O predicado `isTypeConflictLine` agora é preciso: ele rejeita linhas de violação de restrição (ex: `minItems: got 0, want 1`) que anteriormente eram falsos positivos, reduzindo o ruído em outros caminhos de erro `oneOf`.

#### Negativas
- A tabela `knownOneOfFieldHints` em `pkg/parser/schema_errors.go` é uma lista estática de caminhos de campos e valores válidos. Ela ficará silenciosamente desatualizada se engines integrados forem adicionados ou removidos sem que a tabela também seja atualizada.
- `readSourceContextLines` sempre retorna uma janela fixa de 7 linhas (±3). Erros perto do início ou fim de um arquivo recebem preenchimento (padding) com strings vazias, o que exige que a lógica de renderização a jusante tolere linhas vazias graciosamente.

#### Neutras
- A renderização no estilo Rust exige que o chamador (atualmente `compiler_orchestrator_workflow.go`) passe o conteúdo do arquivo pré-carregado para `readSourceContextLines`. Isso torna o local da chamada um pouco mais verboso, mas mantém a preocupação de E/S na camada de orquestração.
- O campo `console.CompilerError.Context` já deve ser preenchido por outros caminhos de código; esta mudança adiciona um segundo local de chamada que o utiliza.

---

## Parte 2 — Especificação Normativa (RFC 2119)

> As palavras-chave **DEVE**, **NÃO DEVE**, **OBRIGATÓRIO**, **DEVERÁ**, **NÃO DEVERÁ**, **DEVERIA**, **NÃO DEVERIA**, **RECOMENDADO**, **PODE** e **OPCIONAL** nesta seção devem ser interpretadas conforme descrito em [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### Renderização de Erro de Nível de Campo

1. Quando um erro do compilador for localizado em uma linha de fonte específica e o conteúdo do arquivo estiver disponível na memória no local da chamada, a implementação **DEVE** incluir linhas de contexto da fonte no erro usando `formatCompilerErrorWithContext`.
2. As implementações **NÃO DEVEM** chamar `formatCompilerErrorWithPosition` para erros onde o conteúdo do arquivo já estiver carregado; `formatCompilerErrorWithContext` **DEVE** ser usado em seu lugar.
3. O contexto da fonte **DEVE** abranger uma janela de ±3 linhas ao redor da linha do erro (7 linhas no total), preenchida com strings vazias quando a janela se estender para antes do início do arquivo.
4. As implementações **DEVERIAM** passar `nil` como o argumento `cause` para `formatCompilerErrorWithContext` para erros de validação pura que não possuem um erro subjacente em Go para envolver.

### Síntese de Erro de Conflito de Tipo oneOf

1. Quando todos os suberros de uma restrição `oneOf` forem conflitos de tipo (ou seja, `cleanOneOfMessage` produz uma lista `meaningful` vazia), as implementações **DEVEM** chamar `synthesizeOneOfTypeConflictMessage` em vez de retornar a string de jargão bruto.
2. `synthesizeOneOfTypeConflictMessage` **DEVE** produzir uma mensagem no formato `"expected T1 or T2, got G"` (esperado T1 ou T2, recebido G) onde `T1`, `T2` são os nomes de tipo distintos esperados do JSON Schema e `G` é o tipo real.
3. Quando o caminho do JSON Schema do campo que falhou corresponder a uma chave em `knownOneOfFieldHints`, a mensagem sintetizada **DEVE** anexar o texto de dica correspondente.
4. `knownOneOfFieldHints` **DEVE** ser atualizado sempre que o conjunto de engines integrados em `NewEngineCatalog` mudar.
5. As implementações **NÃO DEVEM** incluir dicas específicas de campo para caminhos não presentes em `knownOneOfFieldHints`; campos desconhecidos **DEVERIAM** receber apenas a mensagem genérica de incompatibilidade de tipo.

### Detecção de Linha de Conflito de Tipo

1. `isTypeConflictLine` **DEVE** validar se ambos os tokens "got" e "want" em um padrão `"got X, want Y"` são nomes de tipos válidos do JSON Schema (`string`, `object`, `array`, `number`, `integer`, `boolean`, `null`) antes de classificar a linha como um conflito de tipo.
2. As implementações **NÃO DEVEM** classificar linhas de violação de restrição (ex: `"minItems: got 0, want 1"`) como conflitos de tipo.

### Conformidade

Uma implementação é considerada em conformidade com este ADR se satisfizer todos os requisitos **DEVE** e **NÃO DEVE** acima. A falha em atender a qualquer requisito **DEVE** ou **NÃO DEVE** constitui não conformidade.

---

*Este é um rascunho de ADR gerado pelo fluxo de trabalho [Design Decision Gate](https://github.com/github/gh-aw/actions/runs/24285718804). O autor do PR deve revisar, completar e finalizar este documento antes que o PR possa ser mesclado.*
