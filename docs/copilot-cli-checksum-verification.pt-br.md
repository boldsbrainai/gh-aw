# Instalação do Copilot CLI: Verificação de Checksum SHA256

## Visão Geral

A partir desta implementação, todas as instalações do GitHub Copilot CLI nos fluxos de trabalho (workflows) do gh-aw agora incluem a verificação de checksum SHA256 para prevenir ataques à cadeia de suprimentos (supply chain attacks). Isso aborda a descoberta de segurança `unverified_script_exec` identificada pelo Poutine.

## Problema de Segurança

Anteriormente, os fluxos de trabalho baixavam e executavam o script instalador do Copilot CLI sem qualquer verificação de integridade:

```bash
export VERSION=0.0.369 && curl -fsSL https://gh.io/copilot-install | sudo bash
```

**Riscos de Segurança:**
- Se o `gh.io` ou a URL do script instalador for comprometida, código malicioso pode ser injetado.
- O script é executado com privilégios de `sudo`, permitindo acesso em nível de sistema.
- Não há como detectar downloads corrompidos ou adulterados.
- Confiança depositada em infraestrutura externa (redirecionamento gh.io).

## Solução

A nova implementação:
1. Baixa o binário do Copilot CLI diretamente dos releases do GitHub.
2. Baixa o arquivo de checksums do mesmo release.
3. Verifica o checksum SHA256 antes da instalação.
4. Falha rapidamente (fail-fast) se uma inconsistência de checksum for detectada.
5. Fornece um fallback gracioso para releases mais antigos sem checksums.

## Detalhes de Implementação

### Download Direto do Binário

Em vez de usar o script instalador, agora fazemos:

```bash
COPILOT_VERSION="v0.0.369"
COPILOT_REPO="github/copilot-cli"
COPILOT_PLATFORM="linux-x64"
COPILOT_ARCHIVE="copilot-${COPILOT_PLATFORM}.tar.gz"
COPILOT_URL="https://github.com/${COPILOT_REPO}/releases/download/${COPILOT_VERSION}/${COPILOT_ARCHIVE}"
CHECKSUMS_URL="https://github.com/${COPILOT_REPO}/releases/download/${COPILOT_VERSION}/checksums.txt"

# Baixar binário
curl -fsSL -o "/tmp/${COPILOT_ARCHIVE}" "${COPILOT_URL}"

# Baixar arquivo de checksums
curl -fsSL -o "/tmp/copilot-checksums.txt" "${CHECKSUMS_URL}"
```

### Verificação de Checksum

```bash
# Extrair o checksum esperado para nossa plataforma
EXPECTED_CHECKSUM=$(grep "${COPILOT_ARCHIVE}" /tmp/copilot-checksums.txt | awk '{print $1}')

# Computar o checksum real do binário baixado
ACTUAL_CHECKSUM=$(sha256sum "/tmp/${COPILOT_ARCHIVE}" | awk '{print $1}')

# Verificar correspondência
if [ "${ACTUAL_CHECKSUM}" = "${EXPECTED_CHECKSUM}" ]; then
  echo "✓ Verificação de checksum aprovada!"
else
  echo "✗ ERRO: Falha na verificação de checksum!"
  echo "  O binário baixado pode estar corrompido ou ter sido adulterado."
  exit 1
fi
```

### Fallback Gracioso

Para releases mais antigos do Copilot CLI que podem não ter arquivos de checksums:

```bash
curl -fsSL -o "/tmp/copilot-checksums.txt" "${CHECKSUMS_URL}" || {
  echo "Aviso: Arquivo de checksums não disponível para a versão ${COPILOT_VERSION}"
  echo "Prosseguindo sem verificação de checksum (fallback para releases antigos)"
  SKIP_CHECKSUM=true
}
```

## Localização do Código

A implementação está em:
- **Função**: `GenerateCopilotInstallerSteps` em `pkg/workflow/copilot_engine.go`
- **Testes**: `pkg/workflow/copilot_installer_test.go`

## Fluxos de Trabalho Afetados

Os seguintes 73 fluxos de trabalho agora usam a instalação do Copilot CLI com verificação de checksum:

1. ai-moderator.md
2. archie.md
3. artifacts-summary.md
4. brave.md
5. breaking-change-checker.md
6. ci-coach.md
7. ci-doctor.md
8. cli-consistency-checker.md
9. copilot-pr-merged-report.md
10. copilot-pr-nlp-analysis.md
11. copilot-pr-prompt-analysis.md
12. craft.md
13. daily-assign-issue-to-user.md
14. daily-copilot-token-report.md
15. daily-file-diet.md
16. daily-firewall-report.md
17. daily-malicious-code-scan.md
18. daily-news.md
19. daily-repo-chronicle.md
20. daily-workflow-updater.md
21. dependabot-go-checker.md
22. dev-hawk.md
23. dev.md
24. dictation-prompt.md
25. docs-noob-tester.md
26. example-permissions-warning.md
27. firewall-escape.md
28. firewall.md
29. glossary-maintainer.md
30. go-file-size-reduction-project64.campaign.md
31. grumpy-reviewer.md
32. hourly-ci-cleaner.md
33. human-ai-collaboration.md
34. incident-response.md
35. intelligence.md
36. issue-monster.md
37. issue-triage-agent.md
38. layout-spec-maintainer.md
39. mcp-inspector.md
40. mergefest.md
41. notion-issue-summary.md
42. org-health-report.md
43. pdf-summary.md
44. plan.md
45. poem-bot.md
46. portfolio-analyst.md
47. pr-nitpick-reviewer.md
48. python-data-charts.md
49. q.md
50. release.md
51. repo-tree-map.md
52. repository-quality-improver.md
53. research.md
54. security-compliance.md
55. slide-deck-maintainer.md
56. smoke-copilot-no-firewall.md
57. smoke-copilot-mcp-scripts.md
58. smoke-copilot.md
59. smoke-srt.md
60. stale-repo-identifier.md
61. super-linter.md
62. technical-doc-writer.md
63. test-discussion-expires.md
64. test-hide-older-comments.md
65. test-python-mcp-script.md
66. tidy.md
67. video-analyzer.md
68. weekly-issue-summary.md
69. (e quaisquer outros fluxos de trabalho usando o engine: copilot)

## Verificação

Para verificar se a verificação de checksum está funcionando, verifique os arquivos `.lock.yml` compilados. Procure por:

1. **Nenhum script instalador**: NÃO deve conter `gh.io/copilot-install`
2. **Download direto**: Deve conter `github.com/github/copilot-cli/releases/download`
3. **Verificação de checksum**: Deve conter `sha256sum` e a lógica de comparação de checksum

Exemplo de um fluxo de trabalho compilado:

```yaml
- name: Install GitHub Copilot CLI
  run: |
    COPILOT_VERSION="v0.0.369"
    COPILOT_REPO="github/copilot-cli"
    COPILOT_PLATFORM="linux-x64"
    # ... (baixar e verificar checksums)
    if [ "${ACTUAL_CHECKSUM}" = "${EXPECTED_CHECKSUM}" ]; then
      echo "✓ Checksum verification passed!"
    else
      echo "✗ ERROR: Checksum verification failed!"
      exit 1
    fi
```

## Benefícios de Segurança

1. **Proteção da Cadeia de Suprimentos**: Detecta se os releases do GitHub foram comprometidos.
2. **Verificação de Integridade**: Garante que o binário baixado corresponde ao release oficial.
3. **Detecção de Adulteração**: Identifica downloads corrompidos ou modificados.
4. **Superfície de Ataque Reduzida**: Elimina a dependência de redirecionamentos de terceiros (gh.io).
5. **Mensagens de Erro Claras**: Fornece feedback acionável em caso de falhas na verificação.

## Testes

Os testes unitários verificam:
- Tratamento de versão (com e sem o prefixo 'v').
- Geração de código de verificação de checksum.
- Tratamento de fallback para checksums ausentes.
- Integração com a compilação de fluxos de trabalho.

Executar testes:
```bash
make test-unit
# ou especificamente:
go test ./pkg/workflow -run TestGenerateCopilotInstallerSteps
```

## Issues Relacionadas

- Issue #6672: [plan] Adicionar verificação de checksum SHA256 para o script instalador do Copilot CLI
- Descoberta Poutine: `unverified_script_exec` em múltiplos fluxos de trabalho

## Melhorias Futuras

1. **Fixação de Checksum (Pinning)**: Considerar a fixação dos checksums esperados para versões conhecidas no código.
2. **Metadados de Release**: Usar a API do GitHub para buscar metadados de release para verificação adicional.
3. **Verificação Alternativa**: Explorar a verificação de assinatura GPG, se disponível.
4. **Monitoramento**: Adicionar telemetria para rastrear as taxas de sucesso/falha da verificação de checksum.
