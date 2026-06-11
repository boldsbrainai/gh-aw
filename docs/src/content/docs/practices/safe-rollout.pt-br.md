---
title: Rollout Seguro
description: Passe de comportamento apenas de relatório ou em estágios para escritas diretas em produção com evidência e controle.
---

Rollout seguro é a prática de aumentar a autonomia do fluxo de trabalho em etapas em vez de habilitar escritas diretas em produção imediatamente.

A principal questão não é se um fluxo de trabalho é útil, mas se ele é confiável o suficiente para agir no sistema ao vivo. Na prática, as equipes geralmente seguem uma escada: apenas relatório primeiro, depois comportamento em estágios, então uma técnica de escrita segura mais realista se necessário, e finalmente escritas diretas em produção.

## Escada de Rollout

A progressão usual é:

1. Comece no modo apenas de relatório.
2. Habilite comportamento `staged` (em estágios) quando escritas propostas precisam ser pré-visualizadas.
3. Use avaliação em sombra quando o modo de pré-visualização não é suficiente e o caminho real de escrita precisa ser exercitado com segurança.
4. Promova o mesmo fluxo de trabalho para escritas diretas em produção.

`staged` e avaliação em sombra não são intercambiáveis. O modo `staged` é suficiente quando a pergunta é o que o fluxo de trabalho faria. A avaliação em sombra é necessária quando a pergunta é se o caminho real de escrita se comporta corretamente em um alvo seguro fora de produção.

## Quando o modo Staged é Suficiente

Use o modo `staged` quando o risco principal for a qualidade da decisão em vez do comportamento operacional.

Geralmente é suficiente quando mantenedores só precisam revisar ações propostas, comparar alternativas ou inspecionar se o julgamento do fluxo de trabalho é razoável antes que qualquer escrita seja permitida.

## Quando a Avaliação em Sombra é Necessária

Use avaliação em sombra quando o modo `staged` for muito fraco porque o caminho real de escrita em si precisa de validação.

Isso é um bom ajuste quando:

- o fluxo de trabalho deve atualizar objetos reais de destino para provar que o comportamento está correto
- concorrência, deduplicação ou serialização precisam ser testadas em uma superfície viva (ao vivo)
- mantenedores precisam inspecionar o estado real produzido, não apenas a intenção proposta
- escritas entre repositórios, permissões ou limites de despacho precisam ser exercitados com segurança

A avaliação em sombra é uma técnica dentro do rollout seguro, não um padrão de nível superior separado.

## Regras de Design

### A verdade da produção permanece autoritativa

Não deixe que a superfície de avaliação se torne a nova fonte da verdade. Eventos de produção e ações humanas confiáveis posteriores devem permanecer autoritativos.

### Snapshots de previsão devem ser explícitos

Se a comparação posterior importar, persista o que o fluxo de trabalho previu no momento da decisão. Não reconstrua previsões a partir de logs.

### Evidência de correção precisa de proveniência

Nem toda edição posterior deve contar como verdade confiável. Registre proveniência como tipo de ator, fonte manual versus automatizada, status de confiança e papel do repositório de origem.

### Superfícies de avaliação devem permanecer descartáveis

Mantenha o alvo de sombra leve. Ele deve suportar medição e rollout, não se tornar um segundo plano de controle de longa duração.

## Forma de Exemplo

A divisão de repositório comum é:

- repositório de produção: emite eventos ao vivo e contém a verdade humana autoritativa posterior
- repositório de ops: persiste previsões, coleta correções, publica relatórios e atualiza instruções
- repositório de sombra: alvo de escrita temporário fora de produção durante o rollout

Essa forma é frequentemente útil, mas ainda é orientação de rollout em vez de um padrão primário.

## Documentação Relacionada

- [SideRepoOps](/gh-aw/patterns/side-repo-ops/)
- [MultiRepoOps](/gh-aw/patterns/multi-repo-ops/)
- [Modo Staged](/gh-aw/reference/staged-mode/)
- [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/)
