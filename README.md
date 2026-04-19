# NexusAI

Backend de pipeline para portal de noticias com IA.

O projeto faz 4 coisas principais:

1. coleta noticias de `api`, `rss` e `json_feed`
2. salva o material bruto em `raw_articles`
3. evita duplicidade comparando com `raw_articles`
4. gera a materia final com IA e salva em `generated_articles`

![Fluxo basico do NexusAI](docs/EstruturaBasica.png)

## Inicio Rapido

Se a ideia for apenas rodar o projeto sem ler o resto todo, use este caminho:

### 1. Instale as dependencias

```bash
python -m pip install -r requirements.txt
```

### 2. Configure o `.env`

O minimo para funcionar e:

```env
DATABASE_URL=postgresql://postgres:12345@localhost:5432/nexusai
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://127.0.0.1:11434
```

Se quiser coleta por API tambem, preencha:

```env
NEWS_API_KEY=sua_chave_aqui
```

### 3. Prepare o banco

```bash
alembic upgrade head
```

### 4. Rode o pipeline

```bash
python -m app.main
```

### 5. Rode os testes

```bash
python -m pytest
```

Resumo bem direto:

- `alembic upgrade head` prepara a estrutura do banco
- `python -m app.main` executa uma rodada do pipeline
- `python -m pytest` valida se o projeto continua funcionando

## O Que Ja Funciona

- conexao com PostgreSQL
- schema versionado com Alembic
- configuracao centralizada por `.env`
- coleta por `rss`
- coleta por `json_feed`
- coleta por `api` quando `NEWS_API_KEY` estiver preenchida
- persistencia de noticias brutas em `raw_articles`
- deduplicacao por `original_url`, titulo normalizado e `content_hash`
- limite de ate `3` noticias brutas variadas por fonte em cada rodada
- geracao de materia com Ollama local
- salvamento de categoria e tags
- salvamento de imagens e videos em `raw_articles` e `generated_articles`
- registro de falhas em `processing_failures`
- testes automatizados da parte principal do fluxo

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
Ollama local
   ->
generated_articles
   ->
generated_article_sources
```

Regra importante:

- a deduplicacao oficial acontece em `raw_articles`
- `generated_articles` nao entra na comparacao semantica de duplicidade
- `generated_article_sources` existe para impedir gerar duas vezes da mesma `raw_article`

## Estrutura Do Projeto

```text
app/
  main.py                  # entrada principal
  config.py                # leitura e validacao do .env
  db.py                    # engine e sessoes do SQLAlchemy
  models.py                # modelos ORM
  ai/
    ollama.py              # cliente da IA local
  collectors/
    news_api.py            # coleta por API HTTP
    rss.py                 # coleta por RSS/XML
    json_feed.py           # coleta por JSON Feed
  core/
    article_filters.py     # limpeza, normalizacao e heuristicas
    pipeline.py            # orquestracao do fluxo principal
migrations/
  env.py                   # integracao do Alembic com o projeto
  versions/
    20260418_0001_initial_schema.py
scripts/
  migrations.py            # helper para comandos do Alembic
prompts/
  article.txt              # prompt usado pela IA
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

## Papel De Cada Parte

### Aplicacao

- `app/main.py`
  Dispara uma rodada completa do pipeline.
- `app/config.py`
  Le o `.env`, converte valores e expõe `settings`.
- `app/db.py`
  Centraliza conexao com banco e criacao de sessoes.
- `app/models.py`
  Define as tabelas e relacoes do sistema.

### Coletores

- `app/collectors/rss.py`
  Le feeds RSS e transforma cada item em `RawArticle`.
- `app/collectors/json_feed.py`
  Faz o mesmo para fontes em JSON Feed.
- `app/collectors/news_api.py`
  Coleta noticias de API HTTP quando houver chave configurada.

### IA

- `app/ai/ollama.py`
  Monta o prompt, chama o Ollama e devolve um payload estruturado.

### Nucleo

- `app/core/article_filters.py`
  Faz limpeza de HTML, normalizacao, extracao de imagens e videos, filtros de qualidade e heuristicas simples.
- `app/core/pipeline.py`
  Junta tudo: coleta, deduplicacao, selecao, geracao e persistencia.

### Banco

- `migrations/env.py`
  Liga o Alembic ao banco configurado no projeto.
- `migrations/versions/20260418_0001_initial_schema.py`
  Cria o schema inicial.
- `scripts/migrations.py`
  Atalho para os comandos mais comuns do Alembic.

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

- `.env` guarda valores visiveis de `api`, `rss`, `json_feed`, banco, IA e pipeline
- `app/config.py` le e valida esses valores
- os coletores usam apenas o que a `config.py` ja carregou

Exemplo de `.env`:

```env
# =========================================================
# App
# Identificacao basica da aplicacao e ambiente atual.
# APP_ENV pode ser development, test ou production.
# =========================================================
APP_NAME=NexusAI
APP_ENV=development

# =========================================================
# Database
# URL principal do PostgreSQL.
# Formato esperado:
# postgresql://usuario:senha@host:porta/nome_do_banco
# DATABASE_ECHO=true mostra SQL no terminal para debug.
# =========================================================
DATABASE_URL=postgresql://postgres:12345@localhost:5432/nexusai
DATABASE_ECHO=false

# =========================================================
# AI
# Configuracao do provedor local de IA.
# OLLAMA_MODEL e o modelo usado para gerar a materia.
# OLLAMA_BASE_URL e a URL do servidor Ollama local.
# OLLAMA_TIMEOUT_SECONDS e o tempo maximo por requisicao.
# =========================================================
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_TIMEOUT_SECONDS=180

# =========================================================
# API
# Configuracao de fonte baseada em API HTTP.
# Se NEWS_API_KEY ficar vazio, a coleta por API nao roda.
# NEWS_API_SOURCE_NAME e o nome salvo em news_sources.
# NEWS_API_URL define o endpoint principal da API.
# NEWS_API_QUERY ajuda a filtrar o tema buscado.
# NEWS_API_PAGE_SIZE controla quantos itens a API tenta trazer.
# =========================================================
NEWS_API_SOURCE_NAME=NewsAPI
NEWS_API_KEY=
NEWS_API_URL=https://newsapi.org/v2/top-headlines
NEWS_API_COUNTRY=us
NEWS_API_LANGUAGE=en
NEWS_API_QUERY=technology
NEWS_API_PAGE_SIZE=10

# =========================================================
# RSS
# RSS_PAGE_SIZE define quantos itens por feed entram no lote bruto.
# RSS_DEFAULT_FEEDS e a lista oficial de feeds RSS do projeto.
# Formato:
# Nome da Fonte|URL;Nome da Fonte|URL;...
# =========================================================
RSS_PAGE_SIZE=10
RSS_DEFAULT_FEEDS=NASA RSS|https://www.nasa.gov/feed/;NASA Technology|https://www.nasa.gov/technology/feed/;NASA Artemis|https://www.nasa.gov/missions/artemis/feed/;ESA Science|https://sci.esa.int/newssyndication/rss/sciweb.xml;Camara Ultimas Noticias|https://www.camara.leg.br/noticias/rss/ultimas-noticias;Camara Politica|https://www.camara.leg.br/noticias/rss/dinamico/POLITICA;Senado Noticias|https://www12.senado.leg.br/noticias/rss;IBGE Agencia de Noticias|https://agenciadenoticias.ibge.gov.br/agencia-rss;G1|https://g1.globo.com/rss/g1/;Tecnoblog|https://tecnoblog.net/feed/;Canaltech|https://canaltech.com.br/rss/;Olhar Digital|https://olhardigital.com.br/feed/;InfoMoney|https://www.infomoney.com.br/feed/;Exame|https://exame.com/feed/;BBC News|http://feeds.bbci.co.uk/news/rss.xml;CNN|http://rss.cnn.com/rss/edition.rss;The Guardian World|https://www.theguardian.com/world/rss;NYT HomePage|https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml;TechCrunch|https://techcrunch.com/feed/;The Verge|https://www.theverge.com/rss/index.xml;Wired|https://www.wired.com/feed/rss;Ars Technica|http://feeds.arstechnica.com/arstechnica/index;ScienceDaily|https://www.sciencedaily.com/rss/all.xml

# =========================================================
# JSON Feed
# Mesmo conceito do RSS, mas para fontes no padrao JSON Feed.
# JSON_FEED_PAGE_SIZE define quantos itens por feed entram no lote bruto.
# JSON_DEFAULT_FEEDS usa o mesmo formato:
# Nome da Fonte|URL;Nome da Fonte|URL;...
# =========================================================
JSON_FEED_PAGE_SIZE=10
JSON_DEFAULT_FEEDS=Daring Fireball|https://daringfireball.net/feeds/json

# =========================================================
# Pipeline
# Regras principais da rodada de coleta e geracao.
#
# PIPELINE_MAX_ITEMS_PER_RUN
# Quantidade maxima de materias finais que tentamos gerar por execucao.
#
# PIPELINE_CANDIDATE_POOL_MULTIPLIER
# Multiplicador do pool de candidatos antes da geracao.
#
# PIPELINE_GENERATION_BUFFER
# Buffer extra somado ao pool de candidatos.
#
# MAX_RAW_ARTICLES_PER_SOURCE
# Limite de noticias brutas variadas por fonte em cada rodada.
#
# MAX_ARTICLES_PER_SOURCE_PER_RUN
# Limite por fonte na etapa de selecao para geracao.
#
# MAX_ARTICLES_PER_CATEGORY_PER_RUN
# Evita concentrar muitas materias finais na mesma categoria.
#
# MIN_DISTINCT_CATEGORIES_PER_RUN
# Forca diversidade minima de categorias no lote gerado.
#
# DEDUPLICATION_LOOKBACK_DAYS
# Janela de comparacao em raw_articles para titulo e content_hash.
# A URL continua sendo comparada globalmente.
# =========================================================
PIPELINE_MAX_ITEMS_PER_RUN=12
PIPELINE_CANDIDATE_POOL_MULTIPLIER=1
PIPELINE_GENERATION_BUFFER=4
MAX_RAW_ARTICLES_PER_SOURCE=3
MAX_ARTICLES_PER_SOURCE_PER_RUN=3
MAX_ARTICLES_PER_CATEGORY_PER_RUN=2
MIN_DISTINCT_CATEGORIES_PER_RUN=2
DEDUPLICATION_LOOKBACK_DAYS=15

# =========================================================
# Filters
# Regras basicas para descartar material fraco, promocional ou ruidoso.
# =========================================================
MIN_TITLE_LENGTH=20
MIN_CONTENT_LENGTH=40
MIN_QUALITY_SCORE=1
BLOCKED_TITLE_TERMS=webinar,sponsored,advertisement,press release
BLOCKED_TITLE_PREFIXES=saiba como,confira,entenda como,veja como
ALLOWED_CATEGORIES=Geral,Tecnologia,Ciencia,Espaco,Negocios,Politica,Saude,Esportes
MAX_TAGS_PER_ARTICLE=5
```

## Dependencias

Instalacao:

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

```bash
alembic upgrade head
alembic stamp head
python scripts/migrations.py current
python scripts/migrations.py history
python scripts/migrations.py upgrade
python scripts/migrations.py stamp
```

Resumo:

- `upgrade head`
  aplica tudo que falta no banco
- `stamp head`
  marca o banco como atualizado sem executar DDL

## Execucao

Para rodar o pipeline:

```bash
python -m app.main
```

Importante:

- `app.main` nao cria schema manualmente
- a estrutura do banco deve estar alinhada via Alembic
- em banco novo, rode antes `alembic upgrade head`

## Testes

Para rodar todos os testes:

```bash
python -m pytest
```

Status atual:

- `15` testes passando

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
2. criar API de consulta e revisao
3. ampliar a cobertura de testes
4. preparar painel ou frontend
5. evoluir publicacao e fluxo de revisao
