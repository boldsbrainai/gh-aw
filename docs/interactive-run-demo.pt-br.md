# Demonstração do Modo Interativo

Um passo a passo rápido do modo interativo para `gh aw run`.

## Uso

```bash
$ gh aw run
```

## Seleção de Fluxo de Trabalho (Workflow)

```
Selecione um workflow para executar:

  > test-interactive
    1 entrada(s) obrigatória(s), 2 entrada(s) opcional(ais)
  
  /_ Digite para filtrar...
```

## Coleta de Entrada

```
┃ Digite o valor para 'task_description'
┃ > Corrigir a vulnerabilidade de segurança no módulo de autenticação_

┃ Digite o valor para 'priority'
┃ > alta_

┃ Digite o valor para 'dry_run'
┃ > false_
```

## Execução

```
✓ Fluxo de trabalho disparado com sucesso!

Para executar este fluxo de trabalho novamente, use:
⚙ gh aw run test-interactive -F task_description="Corrigir bug" -F priority="alta" -F dry_run="false"
```

## Exemplos de Erro

**Ambiente de CI:**
```bash
$ CI=true gh aw run
✗ o modo interativo não pode ser usado em ambientes de CI
```

**Flag inválida:**
```bash
$ gh aw run --repeat 3
✗ a flag --repeat não é suportada no modo interativo
```
