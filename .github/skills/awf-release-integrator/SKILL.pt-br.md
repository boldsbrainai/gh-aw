---
name: awf-release-integrator
description: Atualize o gh-aw para a versão mais recente do gh-aw-firewall e identifique tarefas de especificação de acompanhamento.
---

# Integrador de Release AWF

Use esta skill ao atualizar `github/gh-aw` para uma versão mais recente do `github/gh-aw-firewall`.

## Objetivo

Finalizar a atualização da versão de forma limpa, reconstruir os artefatos gerados e revisar as alterações de release/especificação upstream para quaisquer tarefas de acompanhamento que devam acompanhar a atualização.

## Fontes necessárias

Consulte estas fontes antes de editar qualquer coisa:

1. Os metadados e o corpo da última release do `github/gh-aw-firewall`.
2. Os pins de versão atuais do gh-aw em `pkg/constants/version_constants.go`.
3. A especificação canônica de fontes de configuração AWF em `specs/awf-config-sources-spec.md`.
4. O esquema AWF embutido em `pkg/workflow/schemas/awf-config.schema.json`.
5. Código de integração de configuração AWF em:
   - `pkg/workflow/awf_config.go`
   - `pkg/workflow/awf_helpers.go`
   - testes AWF relacionados em `pkg/workflow/`

Para revisão de especificação upstream, compare estes arquivos da release ou tag `github/gh-aw-firewall` alvo:

- `docs/awf-config-spec.md`
- `docs/awf-config.schema.json`
- `src/awf-config-schema.json`
- quaisquer ativos de release como `awf-config.schema.json`

## Procedimento de atualização

1. Leia `pkg/constants/version_constants.go` e registre:
   - `DefaultFirewallVersion`
   - cada constante `AWF*MinVersion`
2. Procure pela última release do `github/gh-aw-firewall`.
3. Se a tag da última release corresponder à `DefaultFirewallVersion`, relate que nenhuma atualização de versão é necessária e continue apenas com a revisão de especificação/notas de release se explicitamente solicitado.
4. Se uma release mais nova existir, atualize os pins do gh-aw:
   - atualize `DefaultFirewallVersion`
   - atualize quaisquer constantes `AWF*MinVersion` que precisem ser movidas porque a nova release introduz ou altera flags/funcionalidades restritas (gated)
5. Revise as notas de release para:
   - novas flags
   - flags removidas ou obsoletas
   - adições de esquema/configuração
   - correções de segurança
   - alterações comportamentais que podem exigir novos testes, docs ou atualizações de ADR/especificação
6. Revise a especificação AWF upstream e as alterações de esquema em relação a:
   - `pkg/workflow/schemas/awf-config.schema.json`
   - `specs/awf-config-sources-spec.md`
   - código local de geração e validação de configuração AWF
7. Atualize quaisquer arquivos gh-aw diretamente relacionados necessários para uma integração completa, como:
   - cópias de esquema embutidas
   - auxiliares/testes com restrição de versão
   - especificações ou ADRs documentando comportamento AWF recém-surgido
8. Adicione ou atualize um changeset de patch quando a atualização alterar comportamento enviado.

## Validação necessária

Após editar, execute o fluxo de reconstrução AWF completo exatamente nesta ordem. O segundo
`make recompile` é necessário para atualizar os pins de SHA de imagem resolvidos durante a primeira passagem.

```bash
make build
make recompile
make recompile
```

Em seguida, execute a validação focada para qualquer código Go ou lógica de esquema tocado, especialmente testes relacionados ao AWF.

## Saída esperada

Resuma:

- versão AWF atual do gh-aw → release alvo
- constantes atualizadas
- destaques das notas de release
- diferenças de especificação/esquema revisadas
- recomendações adicionais de acompanhamento que ainda não foram implementadas

## Heurísticas de revisão

Ao decidir se mais do que uma atualização de versão é necessária, verifique especificamente para:

- novas propriedades de esquema AWF não representadas no gh-aw
- novas flags de CLI que precisam de gates `AWF*MinVersion`
- campos de configuração presentes no esquema, mas ausentes da geração/validação do gh-aw
- desvio (drift) que deve atualizar `specs/awf-config-sources-spec.md`
- testes cujas versões AWF fixadas ou URLs de esquema precisam de atualização
