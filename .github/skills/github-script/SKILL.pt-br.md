---
name: github-script
description: Escreva JavaScript robusto para etapas de github-script do GitHub Actions.
---

# Melhores Práticas de Script de Ação do GitHub

Use estas diretrizes para JavaScript executado por `actions/github-script@v8`.

## Notas Importantes

- Esta ação fornece os pacotes `@actions/core` e `@actions/github` globalmente
- Não adicione import ou require para `@actions/core`
- Documentação de referência:
  - https://github.com/actions/toolkit/blob/main/packages/core/README.md
  - https://github.com/actions/toolkit/blob/main/packages/github/README.md

## Melhores Práticas

- Use `core.info`, `core.warning`, `core.error` para registro de log, não `console.log` ou `console.error`
- Use `core.setOutput` para definir saídas de ação
- Use `core.exportVariable` para definir variáveis de ambiente para etapas subsequentes
- Use `core.getInput` para obter entradas de ação, com `required: true` para entradas obrigatórias
- Use `core.setFailed` para marcar a ação como falha com uma mensagem de erro

## Resumo de Passo (Step Summary)

Use a função `core.summary.*` para escrever saída para o arquivo de resumo de passo.

- Use `core.summary.addRaw()` para adicionar conteúdo Markdown bruto (GitHub Flavored Markdown suportado)
- Certifique-se de chamar `core.summary.write()` para liberar gravações pendentes
- Chamadas de função de resumo podem ser encadeadas, por exemplo, `core.summary.addRaw(...).addRaw(...).write()`

## Erros Comuns

- Evite o tipo `any` tanto quanto possível, use tipos específicos ou `unknown` em vez disso
- Tratador de erro (catch handler): verifique se o erro é uma instância de Error antes de acessar a propriedade de mensagem

```js
catch (error) {
  core.setFailed(error instanceof Error ? error : String(error));
}
```

- `core.setFailed` também chama `core.error`, então não chame ambos

## Verificação de Tipo (Typechecking)

Execute `make js` para executar o compilador typescript.

Execute `make lint-cjs` para lintar os arquivos.

Execute `make fmt-cjs` após editar para formatar o arquivo.
---
