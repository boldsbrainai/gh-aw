---
emoji: "✏️"
name: Sessão do Editor ACE
description: Gera um link de sessão do editor ACE quando invocado com o comando /ace em comentários de pull request
on:
  slash_command:
    strategy: centralized
    name: ace
    events: [pull_request_comment]
strict: false
permissions:
  pull-requests: read
  issues: read
jobs:
  post_ace_link:
    runs-on: ubuntu-latest
    needs: [activation]
    if: needs.activation.outputs.activated == 'true'
    permissions:
      pull-requests: write
      issues: write
    steps:
      - name: Postar link da sessão do editor ACE
        uses: actions/github-script@v9
        with:
          script: |
            const prNumber = context.payload.issue.number;
            const repo = context.repo.repo;
            const owner = context.repo.owner;
            const actor = context.actor;
            const sessionId = `${owner}-${repo}-pr${prNumber}`;
            const aceUrl = `https://ace.com/session/${sessionId}`;

            await github.rest.issues.createComment({
              owner,
              repo,
              issue_number: prNumber,
              body: `👋 Olá @${actor}! Aqui está o seu link da sessão do editor ACE para este pull request:\n\n🔗 **${aceUrl}**\n\nCopie e cole este link no Slack para convidar seus colegas de equipe para a sessão! 🚀`,
            });
imports:
  - shared/otlp.md
tools:
  cli-proxy: true

---

Ação clássica que gera um link de sessão do editor ACE no comando slash de comentário de pull request.
