# Frontend Nexus IA

Frontend em React + Vite para o portal editorial do Nexus IA.

O projeto saiu do template padrao do Vite e hoje ja possui uma estrutura de portal com:

- home editorial
- header, sidebar e footer integrados
- editorias fixas por categoria
- pagina de artigo com template estatico
- tela de `not-found` para rotas removidas ou invalidas
- camada mock de dados preparada para futura integracao com banco/API

## Stack

- React 19
- Vite 8
- CSS modular por componente/pagina
- roteamento simples baseado em `window.location.hash`

## Scripts

Dentro da pasta `Frontend`:

```bash
npm run dev
npm run build
npm run preview
npm run lint
```

No Windows, se o PowerShell bloquear `npm.ps1`, use:

```bash
npm.cmd run dev
```

## Estrutura atual

### Shell do app

O shell principal fica em [src/App.jsx](/d:/Projetos/Nexus%20AI/Frontend/src/App.jsx:1).

Ele controla:

- resolucao de rota por hash
- abertura e fechamento da sidebar
- rota das editorias
- rota de materia individual
- fallback para `not-found`

### Layout global

Os estilos base e o visual geral do portal ficam em:

- [src/index.css](/d:/Projetos/Nexus%20AI/Frontend/src/index.css:1)
- [src/styles/app-shell.css](/d:/Projetos/Nexus%20AI/Frontend/src/styles/app-shell.css:1)

O visual atual foi ajustado para uma linguagem mais editorial, com:

- fundo texturizado claro
- tipografia serifada nos titulos
- blocos com cara de jornal digital
- melhor responsividade para header, home e editorias

### Componentes principais

- [src/components/header](/d:/Projetos/Nexus%20AI/Frontend/src/components/header:1): cabecalho com navegacao principal
- [src/components/sidebar](/d:/Projetos/Nexus%20AI/Frontend/src/components/sidebar:1): menu lateral mobile/overlay
- [src/components/footer](/d:/Projetos/Nexus%20AI/Frontend/src/components/footer:1): rodape com mapa do portal
- [src/components/watch-strip](/d:/Projetos/Nexus%20AI/Frontend/src/components/watch-strip:1): faixa escura de destaques
- [src/components/brand-wordmark](/d:/Projetos/Nexus%20AI/Frontend/src/components/brand-wordmark:1): logo/wordmark

## Navegacao e rotas

O frontend usa hash routing simples, sem React Router neste momento.

Rotas de editoria:

- `#noticias`
- `#negocios`
- `#tecnologia`
- `#saude`
- `#clima`
- `#cultura`
- `#politica`
- `#ciencia`
- `#videos`

Rotas de conta:

- `#login`
- `#register`

Rota de materia:

- `#materia/<slug>`

Fallback:

- `#not-found`

Se a rota for invalida ou se a pagina tiver sido removida, o app renderiza [src/pages/not-found/index.jsx](/d:/Projetos/Nexus%20AI/Frontend/src/pages/not-found/index.jsx:1).

## Editorias fixas

As paginas de categoria foram convertidas para um modelo fixo e reutilizavel.

Em vez de cada pagina ter markup manual diferente, todas usam o componente:

- [src/components/editorial-page/index.jsx](/d:/Projetos/Nexus%20AI/Frontend/src/components/editorial-page/index.jsx:1)

Esse componente monta:

- cabecalho da editoria
- materia principal em destaque
- trilha lateral com recortes da editoria
- carrossel de materias clicaveis

As paginas em `src/pages/*` apenas apontam para a editoria correta:

- [src/pages/noticias/index.jsx](/d:/Projetos/Nexus%20AI/Frontend/src/pages/noticias/index.jsx:1)
- [src/pages/negocios/index.jsx](/d:/Projetos/Nexus%20AI/Frontend/src/pages/negocios/index.jsx:1)
- [src/pages/tecnologia/index.jsx](/d:/Projetos/Nexus%20AI/Frontend/src/pages/tecnologia/index.jsx:1)
- [src/pages/saude/index.jsx](/d:/Projetos/Nexus%20AI/Frontend/src/pages/saude/index.jsx:1)
- [src/pages/clima/index.jsx](/d:/Projetos/Nexus%20AI/Frontend/src/pages/clima/index.jsx:1)
- [src/pages/cultura/index.jsx](/d:/Projetos/Nexus%20AI/Frontend/src/pages/cultura/index.jsx:1)
- [src/pages/politica/index.jsx](/d:/Projetos/Nexus%20AI/Frontend/src/pages/politica/index.jsx:1)
- [src/pages/ciencia/index.jsx](/d:/Projetos/Nexus%20AI/Frontend/src/pages/ciencia/index.jsx:1)
- [src/pages/videos/index.jsx](/d:/Projetos/Nexus%20AI/Frontend/src/pages/videos/index.jsx:1)

## Pagina de artigo

Quando o usuario clica em uma materia dentro da editoria, o app abre uma pagina fixa de artigo.

O template fica em:

- [src/components/article-page/index.jsx](/d:/Projetos/Nexus%20AI/Frontend/src/components/article-page/index.jsx:1)

Esse template ja foi preparado para renderizar dados vindos do banco, incluindo:

- categoria
- titulo
- resumo
- autor
- data
- tempo de leitura
- local
- corpo do texto
- tags
- materias relacionadas

Hoje ele recebe esses dados de um dataset mock, mas a estrutura ja esta pronta para trocar a origem por API/backend.

## Camada de dados mock

Os dados de conteudo foram centralizados em:

- [src/data/contentData.js](/d:/Projetos/Nexus%20AI/Frontend/src/data/contentData.js:1)

Esse arquivo simula o banco de dados do portal e contem:

- configuracao visual/textual das editorias
- lista de materias com `slug`
- corpo das materias
- tags e metadados
- helpers para filtrar por categoria e buscar por slug

Funcoes principais:

- `getCategoryContent(page)`
- `getArticlesByPage(page)`
- `getArticleBySlug(slug)`
- `getRelatedArticles(article, limit)`

Ja os dados auxiliares do portal, como secoes do menu e blocos da home, continuam em:

- [src/data/portalData.js](/d:/Projetos/Nexus%20AI/Frontend/src/data/portalData.js:1)

## Fluxo atual do portal

O comportamento esperado hoje e:

1. O usuario entra na home.
2. Navega para uma editoria fixa, como `#ciencia`.
3. A editoria renderiza destaques e carrossel com base no dataset.
4. Ao clicar em uma materia, o app vai para `#materia/<slug>`.
5. A pagina de artigo renderiza o template fixo com os dados da materia.
6. Se o `slug` nao existir, a aplicacao cai em `not-found`.

## Mapeamento de navegacao

O mapeamento entre nome de secao e rota fica em:

- [src/utils/navigation.js](/d:/Projetos/Nexus%20AI/Frontend/src/utils/navigation.js:1)

La ficam:

- `mapSectionToPage`
- `normalizeSection`
- tabela de nomes para editorias do menu/footer

Tambem foi tratado o caso de rotas antigas ou removidas, como `laboratorio-ia`, para evitar abrir paginas que nao existem mais.

## O que foi feito no frontend

- substituicao do README padrao do Vite por documentacao do projeto
- revisao visual da home e do header
- correcao de navegacao entre categorias
- criacao das editorias `Ciencia`, `Clima` e `Videos`
- transformacao de `not-found` em pagina real de rota removida
- criacao de um modelo reutilizavel para editorias
- criacao de um modelo reutilizavel para artigo
- implementacao de rota `#materia/<slug>`
- simulacao de conteudo vindo do banco por meio de `contentData.js`

## Proximo passo sugerido

O proximo passo natural e substituir a camada mock por dados reais do backend.

As APIs que ja existem no backend para essa integracao sao:

- `GET /api/v1/home`
- `GET /api/v1/categories`
- `GET /api/v1/categories/{slug}`
- `GET /api/v1/categories/{slug}/articles`
- `GET /api/v1/articles/published`
- `GET /api/v1/articles/slug/{slug}`
- `GET /api/v1/articles/slug/{slug}/related`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

As APIs do painel editorial, separadas da navegacao publica do portal, ficam em `review`:

- `GET /api/v1/review/articles`
- `GET /api/v1/review/articles/pending`
- `GET /api/v1/review/articles/{article_id}`
- `POST /api/v1/review/articles`
- `PUT /api/v1/review/articles/{article_id}`
- `DELETE /api/v1/review/articles/{article_id}`
- `PATCH /api/v1/review/articles/{article_id}/approve`
- `PATCH /api/v1/review/articles/{article_id}/reject`
- `GET /api/v1/review/categories`
- `POST /api/v1/review/categories`
- `PUT /api/v1/review/categories/{category_id}`
- `DELETE /api/v1/review/categories/{category_id}`
- `GET /api/v1/review/tags`
- `POST /api/v1/review/tags`
- `PUT /api/v1/review/tags/{tag_id}`
- `DELETE /api/v1/review/tags/{tag_id}`

Regras importantes dessa integracao:

- so materias com status `publicada` devem aparecer no frontend
- a editoria `Noticias` e um alias de apresentacao para a categoria `Geral` do banco
- o slug da pagina de materia vem do backend e nao precisa existir como coluna no banco

Para isso, basta manter o contrato atual e trocar a origem:

- a home pode passar a usar `GET /api/v1/home`
- `getArticlesByPage(page)` passa a chamar `GET /api/v1/categories/{slug}/articles`
- `getArticleBySlug(slug)` passa a buscar `GET /api/v1/articles/slug/{slug}`
- `getRelatedArticles(article)` passa a usar `GET /api/v1/articles/slug/{slug}/related`

Assim, o layout permanece o mesmo e apenas a fonte de dados muda.

## Observacao

Durante esta etapa, a validacao por build nao foi concluida no ambiente por restricao de execucao/sandbox no comando do Vite. A estrutura de codigo foi atualizada e organizada para essa proxima integracao.
