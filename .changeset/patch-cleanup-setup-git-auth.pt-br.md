---
"gh-aw": patch
---

Limpar os auxiliares de `actions/setup` removendo os ramos antigos `GH_AW_ALLOWED_BOTS`, simplificando as verificações de status dos bots e incorporando a configuração de autenticação do Git usada ao buscar/enviar ramos, para que os auxiliares/testes não utilizados possam ser descartados.
