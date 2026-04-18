# NexusAI

`NexusAI` e um pipeline simples para coleta de noticias, geracao de materia com IA local e salvamento estruturado no banco.

O objetivo atual do projeto e entregar o fluxo basico:

1. buscar noticias em APIs ou RSS
2. salvar em `raw_articles`
3. evitar duplicadas
4. enviar a noticia bruta para o Ollama local
5. gerar uma materia estruturada
6. salvar em `generated_articles` com categoria, tags e relacao com a fonte usada

## Estado atual

### Ja funciona

- conexao com PostgreSQL
- criacao automatica das tabelas
- comunicacao com Ollama local
- prompt externo em `prompts/article.txt`
- coleta por API HTTP
- coleta por RSS como fallback gratuito
- persistencia em `raw_articles`
- deduplicacao basica por `original_url` e `content_hash`
- geracao de materia com categoria e tags
- persistencia em `generated_articles`
- relacao entre materia gerada e fonte usada em `generated_article_sources`

### O que ainda falta

- configurar uma `NEWS_API_KEY` real para coleta por API
- adicionar mais fontes alem do fallback RSS atual
- melhorar a deduplicacao para casos de mesma noticia em URLs diferentes
- tratar falhas de API e Ollama com mais robustez
- revisar consistencia editorial de categorias e tags
- criar testes automatizados
- adicionar migrations de banco
- expor uma API propria do sistema para consulta e revisao

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
    pipeline.py
prompts/
  article.txt
docs/
requirements.txt
.env
```

## Banco de dados

O projeto usa PostgreSQL.

Tabelas principais do fluxo atual:

- `news_sources`
- `raw_articles`
- `generated_articles`
- `generated_article_sources`
- `categories`
- `tags`
- `users`

## Configuracao

Exemplo de `.env` atual:

```env
APP_NAME=NexusAI
APP_ENV=development
DATABASE_URL=postgresql://postgres:12345@localhost:5432/nexusai
DATABASE_ECHO=false
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_TIMEOUT_SECONDS=120
NEWS_API_KEY=
NEWS_API_URL=https://newsapi.org/v2/top-headlines
NEWS_API_COUNTRY=us
NEWS_API_LANGUAGE=en
NEWS_API_QUERY=technology
NEWS_API_PAGE_SIZE=10
RSS_DEFAULT_FEED_URL=https://www.nasa.gov/feed/
RSS_DEFAULT_SOURCE_NAME=NASA RSS
RSS_PAGE_SIZE=10
PIPELINE_MAX_ITEMS_PER_RUN=1
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

## Observacoes

- sem `NEWS_API_KEY`, a coleta por API nao roda
- mesmo sem chave, o projeto consegue usar RSS como fallback
- o limite `PIPELINE_MAX_ITEMS_PER_RUN` existe para evitar execucoes muito lentas enquanto o fluxo ainda esta em validacao
- hoje o pipeline trabalha no modo mais simples: uma noticia bruta gera uma materia

## Proximo alvo

Fechar bem o basico combinado:

1. coletar noticias reais
2. salvar no banco sem duplicar
3. gerar materia com Ollama
4. salvar categoria, tags e vinculo com a fonte

Depois disso, o proximo nivel natural e:

- melhorar a qualidade editorial
- suportar mais fontes
- criar API de consulta e revisao
- preparar frontend ou painel
