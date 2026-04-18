# NexusAI
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/48ff92cf-e21d-484e-830f-bb04dbd83b42" />


`NexusAI` e um pipeline simples para coleta de noticias, geracao de materia com IA local e salvamento estruturado no banco.

O objetivo atual do projeto e entregar o fluxo basico:

1. buscar noticias em APIs ou RSS
2. salvar em `raw_articles`
3. evitar duplicadas
4. enviar a noticia bruta para o Ollama local
5. gerar uma materia estruturada
6. salvar em `generated_articles` com categoria, tags e relacao com a fonte usada

## Visao geral

O diagrama abaixo representa a ideia central do pipeline do projeto, da coleta da noticia bruta ate o salvamento da materia gerada:

![Fluxo basico do NexusAI](docs/EstruturaBasica.png)

## Estado atual

### Ja funciona

- conexao com PostgreSQL
- criacao automatica das tabelas
- comunicacao com Ollama local
- prompt externo em `prompts/article.txt`
- coleta por API HTTP
- coleta por RSS com varias fontes nacionais e internacionais
- persistencia em `raw_articles`
- deduplicacao por `original_url`, titulo normalizado e `content_hash`
- filtro de qualidade minima na coleta
- limpeza de HTML e ruido antes de salvar texto bruto
- geracao de materia com categoria e tags
- persistencia em `generated_articles`
- relacao entre materia gerada e fonte usada em `generated_article_sources`
- tratamento de falha por artigo sem abortar a execucao inteira
- registro de falhas em `processing_failures`
- normalizacao editorial basica de titulos gerados

### O que ainda falta

- configurar uma `NEWS_API_KEY` real para coleta por API
- adicionar mais provedores de API alem do formato atual
- melhorar a deduplicacao semantica entre noticias parecidas
- criar testes automatizados
- adicionar migrations de banco
- expor uma API propria do sistema para consulta e revisao
- melhorar ainda mais a qualidade editorial de titulos e resumos gerados

## Fluxo atual

```text
API / RSS
   ->
collectors
   ->
raw_articles
   ->
Ollama local
   ->
generated_articles
   ->
generated_article_sources
```

Em caso de erro no Ollama para um artigo especifico:

```text
raw_article
   ->
falha por artigo
   ->
processing_failures
```

## Estrutura

```text
app/
  main.py
  config.py
  db.py
  models.py
  collectors/
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

## Banco de dados

O projeto usa PostgreSQL.
<img width="1219" height="1290" alt="image" src="https://github.com/user-attachments/assets/eb21006d-89ae-486a-aa95-96170ac37ce7" />


O modelo abaixo resume as tabelas e relacoes principais do portal de noticias com IA:

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

## Fontes configuradas

Atualmente o projeto consegue trabalhar com varias fontes RSS por padrao, incluindo:

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
- `NYT HomePage`
- `TechCrunch`
- `Wired`
- `Ars Technica`
- `ScienceDaily`

Alguns feeds podem falhar temporariamente ou responder bloqueio HTTP. O coletor RSS ignora esses casos sem derrubar o lote inteiro.

Sem `NEWS_API_KEY`, a parte de API HTTP nao roda, mas o pipeline continua funcional via RSS.

## Filtro atual

O projeto aplica um filtro basico antes de salvar a noticia bruta:

- exige titulo e URL validos
- exige tamanho minimo de titulo e conteudo
- exige score minimo de qualidade
- remove parametros de rastreamento da URL
- bloqueia termos promocionais ou de baixo valor
- bloqueia prefixos como `saiba como`, `confira`, `entenda como`
- deduplica por URL normalizada, titulo normalizado e `content_hash`
- limpa HTML, imagens, links e blocos estruturados antes de salvar texto

Essas regras ficam principalmente em [app/core/article_filters.py](/d:/Projetos/Nexus%20AI/app/core/article_filters.py:1).

## Configuracao

Exemplo de `.env` atual:

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
RSS_DEFAULT_FEEDS=NASA RSS|https://www.nasa.gov/feed/;NASA Technology|https://www.nasa.gov/technology/feed/;NASA Artemis|https://www.nasa.gov/missions/artemis/feed/;ESA Science|https://sci.esa.int/newssyndication/rss/sciweb.xml;Camara Ultimas Noticias|https://www.camara.leg.br/noticias/rss/ultimas-noticias;Camara Politica|https://www.camara.leg.br/noticias/rss/dinamico/POLITICA;Senado Noticias|https://www12.senado.leg.br/noticias/rss;IBGE Agencia de Noticias|https://agenciadenoticias.ibge.gov.br/agencia-rss;G1|https://g1.globo.com/rss/g1/;Tecnoblog|https://tecnoblog.net/feed/;Canaltech|https://canaltech.com.br/rss/;Olhar Digital|https://olhardigital.com.br/feed/;InfoMoney|https://www.infomoney.com.br/feed/;Exame|https://exame.com/feed/;BBC News|http://feeds.bbci.co.uk/news/rss.xml;CNN|http://rss.cnn.com/rss/edition.rss;NYT HomePage|https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml;TechCrunch|https://techcrunch.com/feed/;The Verge|https://www.theverge.com/rss/index.xml;Wired|https://www.wired.com/feed/rss;Ars Technica|http://feeds.arstechnica.com/arstechnica/index;ScienceDaily|https://www.sciencedaily.com/rss/all.xml
PIPELINE_MAX_ITEMS_PER_RUN=3
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

Dependencias atuais:

- `SQLAlchemy`
- `psycopg[binary]`
- `requests`
- `python-dotenv`

## Execucao

Para rodar o pipeline:

```bash
python -m app.main
```

Esse comando:

1. inicializa o banco
2. coleta noticias das fontes configuradas
3. salva em `raw_articles`
4. envia para o Ollama
5. salva as materias geradas no banco
6. registra falhas por artigo em `processing_failures`, se houver

## Teste com banco limpo

Para testar o fluxo do zero, voce pode limpar o conteudo operacional e rodar novamente:

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
python -m app.main
```

## Observacoes

- sem `NEWS_API_KEY`, a coleta por API nao roda
- o pipeline continua funcional via RSS
- o limite `PIPELINE_MAX_ITEMS_PER_RUN` controla quantos artigos entram em cada rodada do Ollama
- o timeout do Ollama foi aumentado para reduzir abortos em artigos lentos
- falhas de um artigo nao interrompem a rodada inteira
- hoje o pipeline trabalha no modo mais simples: uma noticia bruta gera uma materia

## Proximo alvo

Fechar bem o basico combinado:

1. coletar noticias reais
2. salvar no banco sem duplicar
3. gerar materia com Ollama
4. salvar categoria, tags e vinculo com a fonte
5. registrar falhas sem perder a rodada

Depois disso, o proximo nivel natural e:

- melhorar a qualidade editorial
- suportar mais fontes e APIs
- criar API de consulta e revisao
- preparar frontend ou painel
