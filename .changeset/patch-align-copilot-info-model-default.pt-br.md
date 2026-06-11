---
"gh-aw": patch
---

Alinhou o fallback `GH_AW_INFO_MODEL` para o mecanismo Copilot com o fallback `COPILOT_MODEL`. Ambos agora usam `'claude-sonnet-4.6'` (correspondente a `CopilotBYOKDefaultModel`) para que o modelo registrado nos metadados de execução corresponda ao modelo realmente usado pela CLI do Copilot.
