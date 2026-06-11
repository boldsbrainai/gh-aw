---
"gh-aw": patch
---

Correção da falha de autenticação do copilot-driver com `--continue`: quando a mensagem "Nenhuma informação de autenticação encontrada" aparece durante uma tentativa de repetição com `--continue` (as credenciais da sessão podem ter sido corrompidas devido a uma saída prematura), o sistema recorre a uma nova execução em vez de interromper imediatamente, proporcionando ao trabalho uma rota de recuperação por meio da autenticação via variável de ambiente.
