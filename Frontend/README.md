# Frontend Nexus IA

Frontend do portal editorial Nexus IA, construido em React + Vite com navegacao por hash, integracao real com o backend e uma camada publica de leitura separada da area de revisao editorial.

Hoje o frontend ja consome APIs reais para:

- home do portal
- editorias por categoria
- leitura dinamica de materia por `slug`
- busca publica de materias
- login, cadastro e sessao do usuario
- videos derivados de materias com `video_url`
- pagina de revisao para usuarios com role `revisor`

## Stack

- React 19
- Vite 8
- JavaScript com JSX
- CSS por componente e por pagina
- cliente HTTP proprio baseado em `fetch`
- roteamento simples com `window.location.hash`

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

## Configuracao da API

O frontend usa:

- `VITE_API_BASE_URL`

Se a variavel nao for informada, o valor padrao e:

```text
/api/v1
```

Em desenvolvimento, o Vite ja esta configurado com proxy:

- `/api` -> `http://127.0.0.1:8000`

Arquivos relacionados:

- `vite.config.js`
- `src/services/api-client.js`

## Estrutura principal

### Shell da aplicacao

O shell principal fica em `src/App.jsx`.

Ele controla:

- leitura da rota atual pelo hash
- resolucao de aliases de paginas
- navegacao entre home, editorias, auth, review e paginas institucionais
- abertura da materia dinamica por `#materia/<slug>`
- fallback para `not-found`
- sincronizacao da sessao autenticada
- redirecionamento automatico de revisor para `#review`

### Componentes centrais

- `src/components/header`: cabecalho principal, acesso a auth e atalho para review de revisores
- `src/components/sidebar`: menu lateral com busca integrada ao backend
- `src/components/footer`: rodape com navegacao interna e links institucionais
- `src/components/editorial-page`: template reutilizavel para editorias
- `src/components/article-page`: template da materia dinamica
- `src/components/watch-strip`: faixa inferior de destaques
- `src/components/info-page`: bloco reutilizavel para paginas institucionais
- `src/components/brand-wordmark`: marca do portal

### Camada de servicos

- `src/services/api-client.js`: cliente HTTP base, raiz da API e tratamento de erro
- `src/services/portal-api.js`: home, editorias, materia publica, busca e videos
- `src/services/auth-api.js`: login, cadastro, token em `localStorage` e `GET /auth/me`
- `src/services/review-api.js`: integracao com o modulo `review`

### Utilitarios

- `src/utils/navigation.js`: mapeamento entre nomes visuais e paginas internas
- `src/utils/video-embed.js`: resolve links de video para YouTube, Vimeo, arquivo direto ou link externo

## Rotas disponiveis

O projeto usa hash routing simples. As principais rotas sao:

### Publicas

- `#home`
- `#noticias`
- `#negocios`
- `#tecnologia`
- `#saude`
- `#clima`
- `#cultura`
- `#politica`
- `#ciencia`
- `#videos`

### Materia dinamica

- `#materia/<slug>`

### Autenticacao

- `#login`
- `#register`

### Revisao

- `#review`

### Institucionais

- `#terms-of-use`
- `#privacy-policy`
- `#contato`
- `#about`

### Fallback

- `#not-found`

Tambem existem aliases tratados no `App.jsx`, como:

- `#inicio` -> `#home`
- `#termos-de-uso` -> `#terms-of-use`
- `#politica-de-privacidade` -> `#privacy-policy`
- `#sobre-o-nexus-ia` -> `#about`

## Paginas implementadas

### Home

A home consome `fetchHomeData()` e renderiza:

- materia principal
- grid com ultimas materias
- bloco de mais lidas
- faixa inferior com destaques
- editorias destacadas

Arquivo principal:

- `src/pages/home/index.jsx`

### Editorias fixas

As paginas de categoria usam o mesmo template editorial, trocando apenas o `page`.

Paginas atuais:

- `src/pages/noticias`
- `src/pages/negocios`
- `src/pages/tecnologia`
- `src/pages/saude`
- `src/pages/clima`
- `src/pages/cultura`
- `src/pages/politica`
- `src/pages/ciencia`
- `src/pages/videos`

As editorias normais consomem:

- `GET /categories/{slug}`

A pagina `videos` e derivada no frontend a partir das materias publicadas que possuem `video_url`.

### Materia dinamica

A leitura da materia e feita por:

- `GET /articles/slug/{slug}`

A tela renderiza:

- categoria
- titulo
- resumo
- autor editorial
- data formatada
- tempo de leitura
- localizacao
- imagem principal
- video incorporado quando existir
- corpo em paragrafos
- tags
- materias relacionadas
- fontes originais vinculadas
- autor original e link da fonte quando existirem

Se o `slug` nao existir ou a materia nao estiver mais disponivel, a aplicacao cai em `not-found`.

Arquivos principais:

- `src/components/article-page/index.jsx`
- `src/components/article-page/article-page.css`

### Login e cadastro

As telas publicas de autenticacao estao conectadas ao backend:

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

O token de acesso fica salvo em `localStorage`.

Comportamento atual:

- usuario comum entra e segue para `#home`
- usuario com role `revisor` entra e e redirecionado para `#review`

Arquivos:

- `src/pages/login/index.jsx`
- `src/pages/register/index.jsx`
- `src/services/auth-api.js`

### Frontend de review

A area de revisao foi implementada no frontend e integrada ao modulo `review` do backend.

Ela ja permite:

- listar materias da fila editorial
- abrir detalhe de artigo para revisao
- criar nova materia
- editar artigo existente
- aprovar e publicar
- rejeitar
- apagar artigo
- listar, criar, editar e apagar categorias
- listar, criar, editar e apagar tags

O acesso fica disponivel apenas para usuarios autenticados com role `revisor`.

Arquivos:

- `src/pages/review/index.jsx`
- `src/pages/review/review.css`
- `src/services/review-api.js`

### Paginas institucionais

Ja existem paginas proprias para:

- termos de uso
- politica de privacidade
- contato
- sobre o Nexus IA

Essas paginas usam o componente reutilizavel `info-page` e sao acessadas pelo footer.

## Busca lateral

A sidebar agora usa busca via API em vez de carregar tudo e filtrar localmente.

Fluxo atual:

1. o usuario abre a sidebar
2. digita pelo menos 2 caracteres
3. o frontend aplica debounce curto
4. chama `GET /articles/search?q=...`
5. renderiza os resultados clicaveis

Arquivo principal:

- `src/components/sidebar/index.jsx`

## Videos na plataforma

O frontend trata materias com video.

Fluxo atual:

1. a materia publicada chega com `video_url`
2. `portal-api.js` mapeia esse campo
3. `video-embed.js` decide como incorporar o link
4. a materia pode exibir:
   - `iframe` para YouTube ou Vimeo
   - player nativo para arquivo direto
   - fallback com link externo quando nao houver embed suportado
5. a pagina `#videos` reune automaticamente as materias publicadas que tem video

## Contratos de API usados pelo frontend

### Portal publico

- `GET /api/v1/home`
- `GET /api/v1/categories/{slug}`
- `GET /api/v1/articles/published`
- `GET /api/v1/articles/search`
- `GET /api/v1/articles/slug/{slug}`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

### Review

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

Observacoes importantes:

- somente materias publicadas devem aparecer na camada publica
- `Noticias` e o nome visual da editoria ligada a categoria geral
- a pagina `videos` e derivada no frontend a partir de materias que ja possuem `video_url`
- a area `review` usa o `user_id` autenticado como `reviewer_id`, seguindo o contrato atual do backend

## Estado atual do frontend

O que ja esta funcionando no codigo:

- navegacao principal do portal
- home integrada ao backend
- editorias integradas ao backend
- materia dinamica por `slug`
- renderizacao de fontes originais na pagina da materia
- fallback para materia ou pagina inexistente
- login e cadastro conectados ao backend
- leitura da sessao com `auth/me`
- redirecionamento de revisor para a area de review
- busca lateral via API
- renderizacao de imagem nas vitrines e materias
- suporte a video em editoria e materia
- paginas institucionais acessiveis pelo footer
- frontend de review conectado ao backend

## Limitacoes e pendencias conhecidas

- a busca publica ja usa API, mas ainda nao e full-text de banco nem tem pagina dedicada de resultados
- o bloco "Mais lidas" ainda nao representa analytics real de leitura
- os icones de redes sociais do footer ainda sao visuais e nao apontam para URLs reais
- parte do texto institucional ainda pode ser refinada depois
- a area de review ainda pode ganhar paginação, busca interna, filtros extras e preview publico da materia
- a API de `review` ainda depende de `reviewer_id` no contrato atual, em vez de deduzir o revisor apenas pelo token

## Observacao sobre validacao

As validacoes recentes executadas nesta etapa foram:

- `npm.cmd run lint`
- `python -m compileall backend`

Ambas passaram para o conjunto atual de mudancas integradas entre frontend e backend.
