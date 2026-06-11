# Documentação Starlight

## Estrutura do Projeto

Dentro do seu projeto Astro + Starlight, você verá as seguintes pastas e arquivos:

```text
.
├── public/
├── src/
│   ├── assets/
│   ├── content/
│   │   └── docs/
│   └── content.config.ts
├── astro.config.mjs
├── package.json
└── tsconfig.json
```

O Starlight procura arquivos `.md` ou `.mdx` no diretório `src/content/docs/`. Cada arquivo é exposto como uma rota com base no nome do arquivo.

Imagens podem ser adicionadas em `src/assets/` e incorporadas no Markdown com um link relativo.

Ativos estáticos (static assets), como favicons, podem ser colocados no diretório `public/`.

## 🧞 Comandos

Todos os comandos são executados a partir da raiz do projeto, em um terminal:

| Comando                   | Ação                                              |
| :------------------------ | :------------------------------------------------ |
| `npm install`             | Instala as dependências                           |
| `npm run dev`             | Inicia o servidor de dev local em `localhost:4321`|
| `npm run build`           | Compila seu site de produção em `./dist/`        |
| `npm run preview`         | Visualiza sua build localmente, antes do deploy   |
| `npm run astro ...`       | Executa comandos CLI como `astro add`, `astro check` |
| `npm run astro -- --help` | Obtém ajuda usando o CLI do Astro                |

## ⚠️ Limitações Conhecidas do Modo de Desenvolvimento (Dev-Mode)

### Sitemap não disponível no modo dev

O sitemap (`/gh-aw/sitemap-index.xml`) é **gerado apenas durante uma build de produção** (`npm run build`). Ele não está disponível ao executar o servidor de desenvolvimento local (`npm run dev`).

Se uma pipeline de CI ou ferramenta automatizada verificar a URL do sitemap durante uma visualização (preview) local, ela receberá uma resposta 404. Para verificar o sitemap, execute `npm run build` seguido de `npm run preview`.

### Caminhos de descoberta de Robots/IA em sites de projeto do GitHub Pages

Este site de documentação é implantado como um **site de projeto** do GitHub Pages sob `/gh-aw/` (veja `base: '/gh-aw/'` em `astro.config.mjs`).

- O `robots.txt` é servido em `/gh-aw/robots.txt`
- O arquivo de descoberta de IA é servido em `/gh-aw/.well-known/ai.txt`
- Os arquivos de metadados de IA são servidos sob `/gh-aw/ai/`

Endpoints de nível raiz em `https://github.github.com/` (por exemplo, `/robots.txt`) são controlados pelo site principal `github.github.com`, não por este repositório.

## Quer saber mais?

Confira a [documentação do Starlight](https://starlight.astro.build/), leia a [documentação do Astro](https://docs.astro.build) ou entre no [servidor Discord do Astro](https://astro.build/chat).
