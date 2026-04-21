# Frontend Nexus IA

Frontend do portal editorial Nexus IA, construído em React + Vite com navegação por hash, integração com backend e páginas públicas organizadas por editoria, matéria, autenticação e conteúdo institucional.

O projeto já não está mais em uma fase apenas visual. Hoje ele consome APIs reais para:

- home do portal
- editorias por categoria
- leitura de matéria dinâmica por `slug`
- listagem de matérias publicadas
- login, cadastro e sessão do usuário
- busca lateral baseada nas matérias publicadas
- página de vídeos derivada das matérias que possuem `video_url`

## Stack

- React 19
- Vite 8
- JavaScript com JSX
- CSS por componente/página
- cliente HTTP próprio baseado em `fetch`
- roteamento simples com `window.location.hash`

## Scripts

Dentro da pasta `Frontend`:

```bash
npm run dev
npm run build
npm run preview
npm run lint
```

Se o PowerShell bloquear `npm.ps1`, use:

```bash
npm.cmd run dev
```

## Configuração da API

O frontend usa como base:

- `VITE_API_BASE_URL`

Se a variável não for informada, o app usa por padrão:

```text
/api/v1
```

Em desenvolvimento, o Vite já está configurado para proxy:

- `/api` -> `http://127.0.0.1:8000`

Arquivo relacionado:

- `vite.config.js`
- `src/services/api-client.js`

## Estrutura principal

### Shell da aplicação

O shell principal fica em `src/App.jsx`.

Ele controla:

- leitura da rota atual pelo hash
- resolução de aliases de páginas
- navegação entre home, editorias, auth e páginas institucionais
- abertura da matéria dinâmica por `#materia/<slug>`
- fallback para `not-found`
- sincronização básica da sessão autenticada

### Componentes centrais

- `src/components/header`: cabeçalho principal, navegação superior e retração da barra de editorias no scroll
- `src/components/sidebar`: menu lateral com busca de matérias publicadas
- `src/components/footer`: rodapé com navegação interna e links institucionais
- `src/components/editorial-page`: template reutilizável para editorias
- `src/components/article-page`: template da matéria dinâmica
- `src/components/watch-strip`: faixa inferior de destaques/carrossel
- `src/components/info-page`: bloco reutilizável para páginas institucionais
- `src/components/brand-wordmark`: marca do portal

### Camada de serviços

- `src/services/api-client.js`: cliente HTTP base, tratamento de erro e raiz da API
- `src/services/portal-api.js`: home, editorias, matérias publicadas, matéria por slug e vídeos
- `src/services/auth-api.js`: login, cadastro, token em `localStorage` e `GET /auth/me`

### Utilitários

- `src/utils/navigation.js`: mapeamento entre nomes visuais e páginas internas
- `src/utils/video-embed.js`: normalização de links de vídeo para YouTube, Vimeo, arquivo direto ou link externo

## Rotas disponíveis

O projeto usa hash routing simples. As principais rotas são:

### Públicas

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

### Matéria dinâmica

- `#materia/<slug>`

### Autenticação

- `#login`
- `#register`

### Institucionais

- `#terms-of-use`
- `#privacy-policy`
- `#contato`
- `#about`

### Fallback

- `#not-found`

Também existem aliases tratados no `App.jsx`, como:

- `#inicio` -> `#home`
- `#termos-de-uso` -> `#terms-of-use`
- `#politica-de-privacidade` -> `#privacy-policy`
- `#sobre-o-nexus-ia` -> `#about`

## Páginas implementadas

### Home

A home já está integrada ao backend e consome `fetchHomeData()`.

Ela renderiza:

- matéria principal
- grid com últimas matérias
- bloco de mais lidas
- faixa inferior com destaques
- editorias destacadas

Arquivo principal:

- `src/pages/home/index.jsx`

### Editorias fixas

As páginas de categoria usam o mesmo template editorial, trocando apenas o `page`.

Páginas atuais:

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

A página `videos` não depende de uma categoria específica do banco. Ela é montada no frontend a partir de matérias publicadas com `video_url`.

### Matéria dinâmica

A leitura da matéria é feita por slug com:

- `GET /articles/slug/{slug}`

A tela renderiza:

- categoria
- título
- resumo
- autor
- data formatada
- tempo de leitura
- localização
- imagem principal
- vídeo incorporado quando existir
- corpo em parágrafos
- tags
- matérias relacionadas

Se o `slug` não existir ou a matéria não estiver mais disponível, a aplicação cai em `not-found`.

### Login e cadastro

As telas públicas de autenticação já estão conectadas ao backend:

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

O token de acesso fica salvo em `localStorage`.

Arquivos:

- `src/pages/login/index.jsx`
- `src/pages/register/index.jsx`
- `src/services/auth-api.js`

### Páginas institucionais

Já existem páginas próprias para:

- termos de uso
- política de privacidade
- contato
- sobre o Nexus IA

Elas usam o componente reutilizável `info-page` e são acessadas pelo footer.

## Busca lateral

A sidebar carrega matérias publicadas quando aberta e permite busca textual simples no frontend.

A busca considera:

- título
- resumo
- excerpt
- categoria
- label

Hoje o comportamento é:

- carrega `fetchPublishedArticles()`
- filtra localmente no navegador
- abre a matéria ao clicar no resultado

Arquivo principal:

- `src/components/sidebar/index.jsx`

## Vídeos na plataforma

O frontend já trata matérias com vídeo.

Fluxo atual:

1. A matéria publicada chega com `video_url`.
2. `portal-api.js` mapeia esse campo.
3. `video-embed.js` decide como incorporar o link.
4. A matéria pode exibir:
   - `iframe` para YouTube/Vimeo
   - player nativo para arquivo direto
   - fallback com link externo quando não houver embed suportado
5. A página `#videos` reúne automaticamente as matérias publicadas que têm vídeo.

## Contratos de API usados pelo frontend

Atualmente o frontend depende destes endpoints públicos:

- `GET /api/v1/home`
- `GET /api/v1/categories/{slug}`
- `GET /api/v1/articles/published`
- `GET /api/v1/articles/slug/{slug}`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

Observações importantes:

- somente matérias publicadas devem aparecer no frontend
- `Noticias` é o nome visual da editoria ligada à categoria geral
- a página `videos` é derivada no frontend, com base nas matérias que já têm `video_url`

## Estado atual do frontend

O que já está funcionando no código:

- navegação principal do portal
- home integrada ao backend
- editorias integradas ao backend
- matéria dinâmica por `slug`
- fallback para matéria/página inexistente
- login e cadastro conectados ao backend
- leitura da sessão com `auth/me`
- busca lateral sobre matérias publicadas
- renderização de imagem nas vitrines e matérias
- suporte a vídeo em editoria e matéria
- páginas institucionais acessíveis pelo footer

## Limitações e pendências conhecidas

- a busca ainda não é uma busca real de backend ou full-text; ela filtra localmente as matérias já carregadas
- o bloco "Mais lidas" ainda não representa analytics real de leitura; hoje ele reaproveita a lista disponível no fluxo editorial
- os ícones de redes sociais do footer ainda são visuais e não apontam para URLs reais
- parte do texto institucional ainda é conteúdo-base e pode ser refinada depois
- existe texto com codificação quebrada em alguns pontos do frontend, principalmente na sidebar, e isso ainda precisa de revisão

## Observação sobre validação

Neste ambiente, a validação final por `vite build` não foi concluída por restrição de execução local do processo do Vite (`spawn EPERM` em tentativas anteriores). O README foi atualizado com base no estado atual do código presente no repositório.
