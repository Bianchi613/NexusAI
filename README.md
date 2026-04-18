# NexusAI

`NexusAI` e um backend de pipeline para portal de noticias com IA. O fluxo principal ja esta funcional: coleta noticias de `api`, `rss` e `json_feed`, filtra o material bruto, evita duplicacoes, envia o conteudo para o Ollama local e salva a materia gerada no PostgreSQL com categoria, tags, imagens, videos e vinculo com a fonte original.

## Visao Geral

O projeto foi pensado para operar neste fluxo:

1. coletar noticias de APIs, RSS e JSON Feed
2. salvar noticias brutas em `raw_articles`
3. evitar duplicidade por URL, titulo normalizado e hash de conteudo
4. gerar materia estruturada com o Ollama local
5. salvar a materia final em `generated_articles`
6. registrar a relacao entre materia gerada e noticia bruta em `generated_article_sources`
7. registrar falhas por artigo em `processing_failures`, sem abortar a rodada inteira

![Fluxo basico do NexusAI](docs/EstruturaBasica.png)

## Status do Nucleo

O nucleo do projeto esta quase completo e ja cobre o basico combinado.

### Ja funciona

- conexao com PostgreSQL
- criacao automatica das tabelas via SQLAlchemy
- base inicial de migrations com Alembic
- leitura de configuracao por `.env`
- integracao com Ollama local
- prompt externo em `prompts/article.txt`
- coleta por RSS com varias fontes nacionais e internacionais
- suporte estrutural a JSON Feed
- suporte a coleta por API HTTP quando `NEWS_API_KEY` estiver configurada
- persistencia de noticias brutas em `raw_articles`
- deduplicacao por `original_url`, titulo normalizado e `content_hash`
- limpeza de HTML, tabelas, ruido e texto malformado antes da geracao
- filtro leve de qualidade para evitar lixo obvio
- geracao de titulo, resumo, corpo, categoria e tags
- persistencia de multiplas imagens em `raw_articles` e `generated_articles`
- persistencia de videos em `raw_articles` e `generated_articles`
- persistencia da materia gerada em `generated_articles`
- relacao entre materia e fonte original em `generated_article_sources`
- criacao automatica de categorias e tags
- tratamento de erro por artigo sem derrubar o lote inteiro
- registro de falhas em `processing_failures`
- rotacao de fontes na selecao do lote

### O que ainda falta

- melhorar a qualidade editorial de alguns titulos e resumos gerados
- adicionar testes automatizados
- criar migrations de banco
- expor uma API propria para consulta, revisao e publicacao
- evoluir a deduplicacao para casos semanticamente parecidos
- adicionar um painel ou frontend para revisao

## Fluxo Atual

```text
API / RSS / JSON Feed
   ->
collectors
   ->
raw_articles
   ->
filtros e deduplicacao
   ->
Ollama local
   ->
generated_articles
   ->
generated_article_sources
```

Em caso de erro ao processar um artigo:

```text
raw_article
   ->
falha por artigo
   ->
processing_failures
```

## Estrutura do Projeto

```text
app/
  main.py
  config.py
  db.py
  models.py
alembic.ini
migrations/
  env.py
  versions/
    20260418_0001_initial_schema.py
  collectors/
    json_feed.py
    news_api.py
    rss.py
  ai/
    ollama.py
  core/
    article_filters.py
    pipeline.py
prompts/
  article.txt
docs/
requirements.txt
.env
```

## Banco de Dados

O projeto usa PostgreSQL como banco principal.

![Modelo de banco de dados do NexusAI](docs/BancoDeDados.png)

Tabelas principais do fluxo atual:

- `news_sources`
- `raw_articles`
- `generated_articles`
- `generated_article_sources`
- `categories`
- `tags`
- `processing_failures`
- `users`

## Fontes Configuradas

Atualmente o projeto possui varias RSS configuradas por padrao:

- `NASA RSS`
- `NASA Technology`
- `NASA Artemis`
- `ESA Science`
- `Camara Ultimas Noticias`
- `Camara Politica`
- `Senado Noticias`
- `IBGE Agencia de Noticias`
- `G1`
- `Tecnoblog`
- `Canaltech`
- `Olhar Digital`
- `InfoMoney`
- `Exame`
- `BBC News`
- `CNN`
- `The Guardian World`
- `NYT HomePage`
- `TechCrunch`
- `The Verge`
- `Wired`
- `Ars Technica`
- `ScienceDaily`

JSON Feed configurado por padrao:

- `Daring Fireball`

Observacoes importantes:

- alguns feeds podem falhar temporariamente ou responder de forma inconsistente
- o coletor RSS ignora falhas isoladas e continua a rodada
- JSON Feed ja e suportado como formato nativo e pode ser configurado por `JSON_DEFAULT_FEEDS`
- o projeto ja inclui como exemplo de `json_feed` a fonte `Daring Fireball`
- sem `NEWS_API_KEY`, a parte de API HTTP nao roda, mas o pipeline continua funcional por RSS

## Filtros e Deduplicacao

O projeto aplica um filtro propositalmente leve antes de salvar a noticia bruta:

- exige titulo e URL validos
- exige tamanho minimo de titulo e conteudo
- aplica score minimo de qualidade
- bloqueia termos promocionais ou claramente fracos
- bloqueia prefixos como `saiba como`, `confira` e `entenda como`
- remove parametros de rastreamento da URL
- deduplica por URL normalizada, titulo normalizado e hash de conteudo
- limpa HTML, imagens, videos, tabelas e blocos estruturados antes da geracao

As regras ficam principalmente em [app/core/article_filters.py](/d:/Projetos/Nexus%20AI/app/core/article_filters.py:1).

## Configuracao

Exemplo de `.env` alinhado com o estado atual do projeto:

```env
APP_NAME=NexusAI
APP_ENV=development
DATABASE_URL=postgresql://postgres:12345@localhost:5432/nexusai
DATABASE_ECHO=false
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_TIMEOUT_SECONDS=180
NEWS_API_KEY=
NEWS_API_URL=https://newsapi.org/v2/top-headlines
NEWS_API_COUNTRY=us
NEWS_API_LANGUAGE=en
NEWS_API_QUERY=technology
NEWS_API_PAGE_SIZE=10
RSS_DEFAULT_FEED_URL=https://www.nasa.gov/feed/
RSS_DEFAULT_SOURCE_NAME=NASA RSS
RSS_PAGE_SIZE=10
JSON_FEED_DEFAULT_URL=https://daringfireball.net/feeds/json
JSON_FEED_DEFAULT_SOURCE_NAME=Daring Fireball
JSON_FEED_PAGE_SIZE=10
RSS_DEFAULT_FEEDS=NASA RSS|https://www.nasa.gov/feed/;NASA Technology|https://www.nasa.gov/technology/feed/;NASA Artemis|https://www.nasa.gov/missions/artemis/feed/;ESA Science|https://sci.esa.int/newssyndication/rss/sciweb.xml;Camara Ultimas Noticias|https://www.camara.leg.br/noticias/rss/ultimas-noticias;Camara Politica|https://www.camara.leg.br/noticias/rss/dinamico/POLITICA;Senado Noticias|https://www12.senado.leg.br/noticias/rss;IBGE Agencia de Noticias|https://agenciadenoticias.ibge.gov.br/agencia-rss;G1|https://g1.globo.com/rss/g1/;Tecnoblog|https://tecnoblog.net/feed/;Canaltech|https://canaltech.com.br/rss/;Olhar Digital|https://olhardigital.com.br/feed/;InfoMoney|https://www.infomoney.com.br/feed/;Exame|https://exame.com/feed/;BBC News|http://feeds.bbci.co.uk/news/rss.xml;CNN|http://rss.cnn.com/rss/edition.rss;The Guardian World|https://www.theguardian.com/world/rss;NYT HomePage|https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml;TechCrunch|https://techcrunch.com/feed/;The Verge|https://www.theverge.com/rss/index.xml;Wired|https://www.wired.com/feed/rss;Ars Technica|http://feeds.arstechnica.com/arstechnica/index;ScienceDaily|https://www.sciencedaily.com/rss/all.xml
JSON_DEFAULT_FEEDS=Daring Fireball|https://daringfireball.net/feeds/json
PIPELINE_MAX_ITEMS_PER_RUN=12
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
- `SQLAlchemy`
- `psycopg[binary]`
- `requests`
- `python-dotenv`

## Migrations

O projeto agora usa Alembic para versionar o schema do banco.

Instalar dependencias:

```bash
python -m pip install -r requirements.txt
```

Criar ou atualizar o banco ate a ultima versao:

```bash
alembic upgrade head
```

Se o seu banco atual ja foi criado manualmente e ja esta compativel com o schema atual, o caminho mais seguro e marcar a migration inicial sem recriar as tabelas:

```bash
alembic stamp head
```

Depois disso, os proximos ajustes de schema devem virar novas migrations.

## Execucao

Para rodar o pipeline:

```bash
python -m app.main
```

Observacao:

- o `app.main` nao faz mais criacao automatica de schema
- antes de rodar em um banco novo, execute `alembic upgrade head`

Esse comando:

1. inicializa o banco
2. coleta noticias das fontes configuradas
3. deduplica o lote
4. salva as noticias brutas
5. preserva os links de imagens e videos encontrados nas fontes
6. envia os artigos selecionados ao Ollama
7. salva as materias geradas com categoria, tags, imagens e videos
8. registra falhas por artigo, se houver

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

## Teste com Banco Limpo

Para testar o fluxo do zero:

```sql
TRUNCATE TABLE
    processing_failures,
    generated_article_sources,
    generated_articles,
    raw_articles,
    categories,
    tags,
    news_sources
RESTART IDENTITY CASCADE;
```

Depois execute:

```bash
alembic upgrade head
python -m app.main
```

## Observacoes

- `PIPELINE_MAX_ITEMS_PER_RUN` controla quantos artigos entram em cada rodada do Ollama
- o valor padrao atual esta em `12`
- `OLLAMA_TIMEOUT_SECONDS` foi aumentado para reduzir abortos em artigos lentos
- falhas de um artigo nao interrompem a rodada inteira
- hoje o pipeline opera no modo mais simples: uma noticia bruta gera uma materia
- os formatos padrao tratados pelo sistema agora sao `api`, `rss` e `json_feed`
- `raw_articles.original_image_urls` guarda as imagens encontradas na fonte
- `raw_articles.original_video_urls` guarda os videos encontrados na fonte
- `generated_articles.image_urls` herda as imagens da noticia base usada na geracao
- `generated_articles.video_urls` herda os videos da noticia base usada na geracao
- a parte estrutural do backend ja esta praticamente pronta para a proxima etapa

## Proximos Passos

Os proximos ganhos mais valiosos para o projeto sao:

1. melhorar a qualidade editorial do texto gerado
2. criar API de consulta e revisao
3. adicionar testes automatizados
4. preparar painel ou frontend
5. evoluir publicacao e fluxo de revisao
