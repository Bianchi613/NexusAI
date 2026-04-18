# NexusAI

Pipeline simples para:

1. coletar noticias
2. gerar materia com IA local
3. salvar o resultado estruturado

## Estrutura

```text
app/
  main.py
  config.py
  db.py
  models.py
  collectors/
    news_api.py
  ai/
    ollama.py
  core/
    pipeline.py
prompts/
  article.txt
requirements.txt
.env
```

## Execucao inicial

```bash
python -m app.main
```

