# Modo Interativo para `gh aw run`

## Visão Geral

O comando `gh aw run` agora suporta um modo interativo que é ativado quando chamado sem argumentos. Isso fornece uma experiência guiada para selecionar e executar fluxos de trabalho (workflows).

## Uso

Basta executar o comando sem argumentos:

```bash
gh aw run
```

## Funcionalidades

### 1. Seleção de Fluxo de Trabalho (Workflow)

- Exibe uma lista filtrável de fluxos de trabalho que suportam `workflow_dispatch`.
- Mostra descrições dos fluxos de trabalho com contagem de entradas (obrigatórias/opcionais).
- Usa as teclas de seta para navegação e Enter para selecionar.
- Pressione `/` para filtrar fluxos de trabalho por nome.

### 2. Informações do Fluxo de Trabalho

Após selecionar um fluxo de trabalho, exibe:

- Nome do fluxo de trabalho.
- Lista de entradas (obrigatórias e opcionais).
- Valores padrão para entradas opcionais.
- Descrições das entradas.

### 3. Coleta de Entrada

- Solicita cada entrada do fluxo de trabalho.
- Mostra descrições e valores padrão.
- Valida entradas obrigatórias.
- Permite valores vazios para entradas opcionais com valores padrão.

### 4. Confirmação de Execução

- Confirma a execução do fluxo de trabalho com um resumo das entradas.
- Opções para prosseguir ou cancelar.

### 5. Exibição do Comando

Após a execução, mostra o comando CLI equivalente:

```bash
gh aw run nome-do-workflow -F input1=valor1 -F input2=valor2
```

Isso permite que você execute novamente o fluxo de trabalho facilmente com as mesmas entradas.

## Flags Suportadas

Todas as flags padrão do comando `run` funcionam no modo interativo:

- `--repo proprietario/repositorio` - Alvo para um repositório diferente.
- `--ref branch` - Executar em uma branch específica.
- `--engine copilot` - Substituir o engine de IA.
- `--push` - Fazer push das alterações antes de executar.

## Limitações

As seguintes flags NÃO são suportadas no modo interativo:

- `--repeat` - Use o comando exibido para execuções repetidas.
- `--enable-if-needed` - Habilite os fluxos de trabalho manualmente primeiro.
- `-F` / `--raw-field` - As entradas são coletadas interativamente.

## Detecção de CI

O modo interativo é desativado automaticamente em ambientes de CI:

```bash
CI=true gh aw run  # Retorna erro: o modo interativo não pode ser usado em CI
```

## Exemplos

### Execução Interativa Básica

```bash
$ gh aw run
# Exibe a lista de fluxos de trabalho
# Selecione o fluxo de trabalho com as teclas de seta
# Preencha as entradas
# Confirme e execute
```

### Execução Interativa com Substituição de Repositório

```bash
$ gh aw run --repo proprietario/repositorio
# Mesmo fluxo interativo, mas direcionado a um repositório diferente
```

### Usando o Comando Exibido

Após a conclusão da execução interativa:

```bash
✓ Fluxo de trabalho disparado com sucesso!

Para executar este fluxo de trabalho novamente, use:
gh aw run test-workflow -F task_description="Corrigir bug" -F priority="alta"
```

Copie e cole este comando para execuções futuras.

## Detalhes Técnicos

### Filtragem de Fluxos de Trabalho

Apenas fluxos de trabalho com gatilhos `workflow_dispatch` ou `schedule` são exibidos. Isso é determinado verificando a seção `on:` no frontmatter do fluxo de trabalho.

### Tipos de Entrada

Suporta todos os tipos de entrada de `workflow_dispatch`:

- `string` - Entrada de texto.
- `boolean` - Use o tipo string com os valores 'true'/'false' (requisito do GitHub Actions).
- `choice` - Ainda não implementado na interface do usuário (use via CLI).
- `number` - Tratado como entrada de string.

**Nota**: As entradas de `workflow_dispatch` do GitHub Actions devem usar padrões de string, mesmo para tipos booleanos. Use `type: string` com `default: 'false'` em vez de `type: boolean` com `default: false`.

### Detecção de TTY

Recorre a uma lista de texto numerada em ambientes sem TTY (ex: saída via pipe).

## Solução de Problemas (Troubleshooting)

### Nenhum Fluxo de Trabalho Encontrado

Se você vir "no runnable workflows found":

1. Certifique-se de que os fluxos de trabalho tenham `workflow_dispatch:` na seção `on:`.
2. Verifique se os fluxos de trabalho estão no diretório `.github/workflows/`.
3. Verifique se os fluxos de trabalho têm a extensão `.md`.

### Erros de Validação de Entrada

Se a validação de entrada falhar:

- Verifique se todas as entradas obrigatórias foram fornecidas.
- Verifique se os nomes das entradas correspondem às definições do fluxo de trabalho.
- Use o comando exibido para ver o formato esperado.

### Modo Interativo Não Inicia

Se o modo interativo não ativar:

- Certifique-se de que nenhum argumento de fluxo de trabalho foi fornecido.
- Verifique se você não está em um ambiente de CI.
- Verifique se o binário está atualizado.
