# NexusAI

Projeto em Python para um portal de noticias com IA, dividido em duas frentes
na mesma base:

- pipeline editorial que coleta, deduplica e gera materias
- backend HTTP do portal, organizado em `backend/`

O projeto faz isto:

1. coleta noticias de `api`, `rss` e `json_feed`
2. salva o material bruto em `raw_articles`
3. evita duplicidade comparando com `raw_articles`
4. gera a materia final com IA
5. salva o resultado em `generated_articles`

![Fluxo basico do NexusAI](docs/EstruturaBasica.png)

## Estado Atual

Nesta branch, o projeto possui:

- pipeline principal em `Engine/app/`, funcional e testado
- backend do portal em `backend/`, com Swagger e estrutura modular
- suporte a multiplos modos de IA no pipeline: `gemini`, `ollama` e `agentic_ollama`

Status do backend do portal nesta etapa:

- CRUD de `users`, `articles`, `categories` e `tags` ja exposto
- modulos `auth`, `users`, `articles`, `categories`, `tags`, `review` e `config` ja separados
- integracao com `Engine.app.db` e `Engine.app.models` reaproveitada
- autenticacao basica com JWT ja exposta em `auth`
- rotas de leitura para o frontend ja separadas das rotas administrativas
- home agregada do portal ja exposta por `GET /api/v1/home`
- entidade `review` expandida para funcionar como painel editorial central

## Inicio Rapido

Se voce quer apenas rodar o projeto, siga estes passos.

### 1. Instale as dependencias Python

Windows PowerShell:

```powershell
python -m pip install -r requirements.txt
```

Linux/macOS:

```bash
python -m pip install -r requirements.txt
```

Importante:

- `fastapi[standard]` agora faz parte das dependencias
- isso habilita a CLI `fastapi`, usada para subir a API do portal de forma mais simples

### 2. Instale o Ollama e deixe o servidor ativo

O projeto depende do servidor HTTP do Ollama.
Sem isso, a etapa de geracao nao funciona.

Suba o servidor:

Windows PowerShell:

```powershell
ollama serve
```

Linux/macOS:

```bash
ollama serve
```

Em outro terminal, carregue o modelo:

Windows PowerShell:

```powershell
ollama pull llama3
ollama run llama3
```

Linux/macOS:

```bash
ollama pull llama3
ollama run llama3
```

### 3. Crie o arquivo `.env`

Crie um arquivo chamado `.env` na raiz do projeto e cole este exemplo:

```env
# Database
DATABASE_URL=postgresql://postgres:12345@localhost:5432/nexusai
DATABASE_ECHO=false

# AI
AI_PROVIDER=agentic_ollama
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_TIMEOUT_SECONDS=180
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

# API
NEWS_API_SOURCE_NAME=NewsAPI
NEWS_API_KEY=
NEWS_API_URL=https://newsapi.org/v2/top-headlines
NEWS_API_COUNTRY=us
NEWS_API_LANGUAGE=en
NEWS_API_QUERY=technology
NEWS_API_PAGE_SIZE=10

# RSS
RSS_PAGE_SIZE=10
RSS_DEFAULT_FEEDS=NASA RSS|https://www.nasa.gov/feed/;NASA Technology|https://www.nasa.gov/technology/feed/;NASA Artemis|https://www.nasa.gov/missions/artemis/feed/;ESA Science|https://sci.esa.int/newssyndication/rss/sciweb.xml;Camara Ultimas Noticias|https://www.camara.leg.br/noticias/rss/ultimas-noticias;Camara Politica|https://www.camara.leg.br/noticias/rss/dinamico/POLITICA;Senado Noticias|https://www12.senado.leg.br/noticias/rss;IBGE Agencia de Noticias|https://agenciadenoticias.ibge.gov.br/agencia-rss;G1|https://g1.globo.com/rss/g1/;Tecnoblog|https://tecnoblog.net/feed/;Canaltech|https://canaltech.com.br/rss/;Olhar Digital|https://olhardigital.com.br/feed/;InfoMoney|https://www.infomoney.com.br/feed/;Exame|https://exame.com/feed/;BBC News|http://feeds.bbci.co.uk/news/rss.xml;CBS News|https://www.cbsnews.com/latest/rss/main;AP News|https://apnews.com/hub/apf-topnews?output=rss;CNN|http://rss.cnn.com/rss/edition.rss;NBC News|https://feeds.nbcnews.com/nbcnews/public/news;Al Jazeera English|https://www.aljazeera.com/xml/rss/all.xml;DW English|https://rss.dw.com/rdf/rss-en-all;France 24 English|https://www.france24.com/en/rss;NHK World Japan|https://www3.nhk.or.jp/rss/news/cat0.xml;The Guardian World|https://www.theguardian.com/world/rss;The Guardian Science|https://www.theguardian.com/science/rss;The Guardian Environment|https://www.theguardian.com/environment/rss;The Guardian Culture|https://www.theguardian.com/culture/rss;MarketWatch RSS|https://www.marketwatch.com/site/rss;Investing RSS Global|https://www.investing.com/webmaster-tools/rss;Investing RSS BR|https://br.investing.com/webmaster-tools/rss;NYT HomePage|https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml;TechCrunch|https://techcrunch.com/feed/;The Verge|https://www.theverge.com/rss/index.xml;Wired|https://www.wired.com/feed/rss;Ars Technica|http://feeds.arstechnica.com/arstechnica/index;ScienceDaily|https://www.sciencedaily.com/rss/all.xml

# JSON Feed
JSON_FEED_PAGE_SIZE=10
JSON_DEFAULT_FEEDS=Daring Fireball|https://daringfireball.net/feeds/json

# Pipeline
PIPELINE_MAX_ITEMS_PER_RUN=12
PIPELINE_CANDIDATE_POOL_MULTIPLIER=1
PIPELINE_GENERATION_BUFFER=4
MAX_RAW_ARTICLES_PER_SOURCE=3
MAX_ARTICLES_PER_SOURCE_PER_RUN=3
MAX_ARTICLES_PER_CATEGORY_PER_RUN=2
MIN_DISTINCT_CATEGORIES_PER_RUN=2
DEDUPLICATION_LOOKBACK_DAYS=15

# Filters
MIN_TITLE_LENGTH=20
MIN_CONTENT_LENGTH=40
MIN_QUALITY_SCORE=1
BLOCKED_TITLE_TERMS=webinar,sponsored,advertisement,press release
BLOCKED_TITLE_PREFIXES=saiba como,confira,entenda como,veja como
ALLOWED_CATEGORIES=Geral,Tecnologia,Ciencia,Espaco,Negocios,Politica,Saude,Esportes
MAX_TAGS_PER_ARTICLE=5
```

Se quiser usar coleta por API real, preencha:

```env
NEWS_API_KEY=sua_chave_aqui
```

Se quiser usar Gemini no lugar do Ollama:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=sua_chave_aqui
```

### 4. Prepare o banco

Windows PowerShell:

```powershell
alembic upgrade head
```

Linux/macOS:

```bash
alembic upgrade head
```

### 5. Rode o pipeline

Windows PowerShell:

```powershell
python -m Engine.app.main
```

Linux/macOS:

```bash
python -m Engine.app.main
```

### 6. Rode o backend do portal

Windows PowerShell:

```powershell
fastapi dev
```

Linux/macOS:

```bash
fastapi dev
```

Swagger:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

### 7. Rode os testes

Windows PowerShell:

```powershell
python -m pytest
```

Linux/macOS:

```bash
python -m pytest
```

Resumo curto:

- `ollama serve` sobe o servidor do Ollama
- `ollama run llama3` carrega o modelo
- `alembic upgrade head` prepara o banco
- `python -m Engine.app.main` roda uma execucao do pipeline
- `fastapi dev` sobe a API do portal em modo de desenvolvimento
- `AI_PROVIDER=agentic_ollama` ativa o fluxo com 4 agentes usando Ollama

## O Que Ja Funciona

- conexao com PostgreSQL
- schema versionado com Alembic
- configuracao centralizada por `.env`
- coleta por `rss`
- coleta por `json_feed`
- coleta por `api` quando `NEWS_API_KEY` estiver preenchida
- persistencia de noticias brutas em `raw_articles`
- deduplicacao por `original_url`, titulo normalizado e `content_hash`
- limite de ate `3` noticias brutas variadas por fonte por rodada
- geracao de materia com Ollama local
- fluxo agentico com 4 agentes sobre Ollama: fatos, estrutura, redator e supervisor/editor
- salvamento de categoria, tags, imagens e videos
- registro de falhas em `processing_failures`
- testes automatizados da parte principal do fluxo
- backend HTTP inicial do portal com FastAPI
- Swagger do backend do portal
- CRUD de `users`, `articles`, `categories` e `tags`
- leitura publica do frontend com filtros por artigos `publicada`
- rota agregada `GET /api/v1/home` para abastecer a capa do portal
- painel editorial em `review` para listar, editar, aprovar, rejeitar e apagar artigos
- painel editorial em `review` para gerenciar tags e categorias

## O Que Ainda Esta Em Aberto

- autenticacao real em `auth`
- fluxo editorial mais completo antes da publicacao
- politicas de permissao por `role`

## Como O Fluxo Funciona

```text
API / RSS / JSON Feed
   ->
collectors
   ->
raw_articles
   ->
deduplicacao em raw_articles
   ->
selecao de candidatos
   ->
Ollama
   ->
generated_articles
   ->
generated_article_sources
```

Regra importante:

- a deduplicacao oficial acontece em `raw_articles`
- `generated_articles` nao entra na comparacao semantica
- `generated_article_sources` impede gerar duas vezes da mesma `raw_article`

## Estrutura Do Projeto

```text
Engine/
  app/
    main.py
    config.py
    db.py
    models.py
    ai/
      agentic.py
      gemini.py
      ollama.py
      agents/
        facts_agent.py
        structure_agent.py
        writer_agent.py
        editor_agent.py
    collectors/
      news_api.py
      rss.py
      json_feed.py
    core/
      article_filters.py
      pipeline.py
  prompts/
    article.txt
    agents/
      facts_agent.txt
      structure_agent.txt
      writer_agent.txt
      editor_agent.txt
backend/
  main.py
  auth/
  users/
  articles/
  categories/
  tags/
  review/
  config/
migrations/
  env.py
  versions/
    20260418_0001_initial_schema.py
scripts/
  migrations.py
docs/
  EstruturaBasica.png
  BancoDeDados.png
tests/
  test_article_filters.py
  test_json_feed_collector.py
  test_pipeline_deduplication.py
  test_pipeline_diversity.py
  test_pipeline_selection.py
  test_rss_collector.py
```

## O Papel De Cada Parte

### Aplicacao

- `Engine/app/main.py`
  Entrada principal. Dispara uma rodada do pipeline.
- `Engine/app/config.py`
  Le e valida o `.env`.
- `Engine/app/db.py`
  Configura engine e sessoes do SQLAlchemy.
- `Engine/app/models.py`
  Define as tabelas e relacoes ORM.

### Backend Do Portal

- `backend/main.py`
  Entrada principal da API HTTP do portal.
- `backend/auth/`
  Estrutura de autenticacao. Nesta etapa ainda em scaffold.
- `backend/users/`
  Rotas e servicos de usuarios.
- `backend/articles/`
  CRUD editorial e leitura de materias para o frontend.
- `backend/categories/`
  CRUD editorial e leitura de categorias para o frontend.
- `backend/tags/`
  Rotas e servicos de tags editoriais.
- `backend/review/`
  Painel editorial central para revisao e administracao de artigos, tags e categorias.
- `backend/config/`
  Configuracao editorial compartilhada e APIs agregadas, como `GET /home`.
- os arquivos de acesso a banco ficam dentro dos modulos de dominio
  como `article_repository.py`, `user_repository.py`,
  `category_repository.py` e `tag_repository.py`.

### Coletores

- `Engine/app/collectors/rss.py`
  Coleta noticias de RSS/XML.
- `Engine/app/collectors/json_feed.py`
  Coleta noticias de JSON Feed.
- `Engine/app/collectors/news_api.py`
  Coleta noticias de API HTTP.

### IA

- `Engine/app/ai/agentic.py`
  Concentra o fluxo agentico com Ollama e coordena os quatro agentes editoriais.
- `Engine/app/ai/gemini.py`
  Cliente alternativo da Gemini API.
- `Engine/app/ai/ollama.py`
  Cliente direto do Ollama para geracao em passo unico.
- `Engine/app/ai/agents/`
  Agentes especializados de fatos, estrutura, redacao e supervisao editorial.
- `Engine/prompts/agents/`
  Prompts separados para cada agente do fluxo agentico.

### Nucleo

- `Engine/app/core/article_filters.py`
  Limpeza, normalizacao, extracao de midias e heuristicas simples.
- `Engine/app/core/pipeline.py`
  Orquestra coleta, deduplicacao, selecao, geracao e persistencia.

### Banco e migrations

- `migrations/env.py`
  Liga o Alembic ao projeto.
- `migrations/versions/20260418_0001_initial_schema.py`
  Cria o schema inicial.
- `scripts/migrations.py`
  Atalho para comandos do Alembic.

## Banco De Dados

O banco principal do projeto e PostgreSQL.

![Modelo de banco de dados do NexusAI](docs/BancoDeDados.png)

Tabelas principais:

- `news_sources`
- `raw_articles`
- `generated_articles`
- `generated_article_sources`
- `categories`
- `tags`
- `processing_failures`
- `users`

## Configuracao

O `.env` e a fonte oficial das configuracoes de execucao.

- ele guarda banco, IA, fontes, pipeline e filtros
- `Engine/app/config.py` le e converte esses valores
- os coletores usam apenas o que a configuracao ja carregou
- `AI_PROVIDER` escolhe entre `gemini`, `ollama` e `agentic_ollama`
- `GEMINI_API_KEY` so precisa estar preenchida quando `AI_PROVIDER=gemini`

O bloco de exemplo acima ja pode ser copiado para criar o arquivo local.

## Dependencias

Instalacao:

Windows PowerShell:

```powershell
python -m pip install -r requirements.txt
```

Linux/macOS:

```bash
python -m pip install -r requirements.txt
```

Principais dependencias:

- `alembic`
- `pytest`
- `SQLAlchemy`
- `psycopg[binary]`
- `requests`
- `python-dotenv`

## Migrations

O projeto usa Alembic para versionar o schema do banco.

Comandos principais:

Windows PowerShell:

```powershell
alembic upgrade head
alembic stamp head
python scripts/migrations.py current
python scripts/migrations.py history
python scripts/migrations.py upgrade
python scripts/migrations.py stamp
```

Linux/macOS:

```bash
alembic upgrade head
alembic stamp head
python scripts/migrations.py current
python scripts/migrations.py history
python scripts/migrations.py upgrade
python scripts/migrations.py stamp
```

Resumo:

- `upgrade head` aplica o que falta no banco
- `stamp head` marca o banco como atualizado sem executar DDL

## Execucao

Para rodar o pipeline:

Windows PowerShell:

```powershell
python -m Engine.app.main
```

Linux/macOS:

```bash
python -m Engine.app.main
```

Importante:

- `Engine.app.main` nao cria schema manualmente
- o banco deve estar alinhado via Alembic
- em banco novo, rode antes `alembic upgrade head`
- por padrao, o projeto pode ser configurado para rodar so com Ollama usando `AI_PROVIDER=agentic_ollama`

Para rodar a API do portal:

Windows PowerShell:

```powershell
fastapi dev
```

Linux/macOS:

```bash
fastapi dev
```

Importante:

- a API do portal usa o mesmo banco do projeto
- nesta etapa ela compartilha `Engine.app.db` e `Engine.app.models`
- o Swagger fica disponivel em `/docs`
- o `entrypoint` da CLI FastAPI esta configurado em `pyproject.toml`
- execute o comando a partir da raiz do projeto

Para uma execucao sem auto-reload:

Windows PowerShell:

```powershell
fastapi run
```

Linux/macOS:

```bash
fastapi run
```

## Testes

Para rodar todos os testes:

Windows PowerShell:

```powershell
python -m pytest
```

Linux/macOS:

```bash
python -m pytest
```

Status atual:

- rotas de auth e de leitura do frontend testadas
- `GET /api/v1/home` validado com apenas materias `publicada`
- APIs de categoria e artigo por `slug` prontas para o frontend
- painel `review` testado para operacoes de revisor em artigos, tags e categorias

Rotas expostas hoje pelo backend do portal:

- `GET /api/v1/auth/status`
- `GET /api/v1/auth/status/protected`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/users`
- `GET /api/v1/users/{user_id}`
- `POST /api/v1/users`
- `PUT /api/v1/users/{user_id}`
- `DELETE /api/v1/users/{user_id}`
- `GET /api/v1/home`
- `GET /api/v1/articles`
- `GET /api/v1/articles/published`
- `GET /api/v1/articles/slug/{slug}`
- `GET /api/v1/articles/slug/{slug}/related`
- `GET /api/v1/articles/{article_id}`
- `POST /api/v1/articles`
- `PUT /api/v1/articles/{article_id}`
- `DELETE /api/v1/articles/{article_id}`
- `GET /api/v1/categories`
- `GET /api/v1/categories/{slug}`
- `GET /api/v1/categories/{slug}/articles`
- `GET /api/v1/categories/id/{category_id}`
- `POST /api/v1/categories`
- `PUT /api/v1/categories/id/{category_id}`
- `DELETE /api/v1/categories/id/{category_id}`
- `GET /api/v1/tags`
- `GET /api/v1/tags/{tag_id}`
- `POST /api/v1/tags`
- `PUT /api/v1/tags/{tag_id}`
- `DELETE /api/v1/tags/{tag_id}`
- `GET /api/v1/review/articles`
- `GET /api/v1/review/articles/pending`
- `GET /api/v1/review/articles/{article_id}`
- `POST /api/v1/review/articles`
- `PUT /api/v1/review/articles/{article_id}`
- `DELETE /api/v1/review/articles/{article_id}`
- `PATCH /api/v1/review/articles/{article_id}/approve`
- `PATCH /api/v1/review/articles/{article_id}/reject`
- `GET /api/v1/review/categories`
- `GET /api/v1/review/categories/{category_id}`
- `POST /api/v1/review/categories`
- `PUT /api/v1/review/categories/{category_id}`
- `DELETE /api/v1/review/categories/{category_id}`
- `GET /api/v1/review/tags`
- `GET /api/v1/review/tags/{tag_id}`
- `POST /api/v1/review/tags`
- `PUT /api/v1/review/tags/{tag_id}`
- `DELETE /api/v1/review/tags/{tag_id}`

Regras importantes das rotas consumidas pelo frontend:

- apenas materias com `generated_articles.status = "publicada"` aparecem em `home`, `categories` e `articles/published`
- a categoria `Geral` continua no banco, mas e exposta ao frontend como `noticias`
- o slug do artigo e virtual, derivado de `title + id`, sem alterar o schema do banco

Regras importantes da area de revisao:

- as rotas de `review` exigem um `reviewer_id` valido com role `revisor`
- o revisor pode editar artigo completo, incluindo `title`, `summary`, `body`, `tags`, `category_id`, `image_urls`, `video_urls` e `status`
- ao publicar ou rejeitar via `review`, o backend pode preencher `reviewed_by` automaticamente com o proprio revisor

## Consultas Uteis

Ver noticias brutas:

```sql
SELECT
  id,
  source_id,
  original_title,
  original_url,
  original_image_urls,
  original_video_urls,
  published_at
FROM raw_articles
ORDER BY id DESC;
```

Ver materias geradas com fonte, categoria e tags:

```sql
SELECT
  ga.id,
  ns.name AS source_name,
  ga.title,
  ga.summary,
  c.name AS category,
  ga.image_urls,
  ga.video_urls,
  ARRAY_REMOVE(ARRAY_AGG(t.name ORDER BY t.id), NULL) AS tags,
  ga.created_at
FROM generated_articles ga
JOIN generated_article_sources gas ON gas.generated_article_id = ga.id
JOIN raw_articles ra ON ra.id = gas.raw_article_id
JOIN news_sources ns ON ns.id = ra.source_id
LEFT JOIN categories c ON c.id = ga.category_id
LEFT JOIN LATERAL json_array_elements_text(ga.tags) AS tag_id_txt ON true
LEFT JOIN tags t ON t.id = tag_id_txt::int
GROUP BY
  ga.id,
  ns.name,
  ga.title,
  ga.summary,
  c.name,
  ga.created_at
ORDER BY ga.id DESC;
```

Ver falhas de processamento:

```sql
SELECT id, raw_article_id, stage, error_type, message, created_at
FROM processing_failures
ORDER BY id DESC;
```

## Proximos Passos

1. melhorar a qualidade editorial do texto gerado
2. implementar autenticacao real no backend do portal
3. reforcar permissoes por `role` nos CRUDs e no fluxo editorial
4. ampliar a cobertura de testes
5. preparar painel ou frontend
