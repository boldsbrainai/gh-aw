---
"gh-aw": patch
---

Adicionar um wrapper para o driver da CLI do Copilot que repita tentativas em caso de falhas parciais da sessão com a opção `--resume`, melhorando a confiabilidade quando erros transitórios no meio da sessão (incluindo CAPIError 400) ocorrem após a saída já ter sido gerada.
