"""Configuracao editorial compartilhada pelas APIs do frontend."""

from app.core.article_filters import slugify
from backend.categories.category_read_base import CategoryReadSummary
from backend.categories.category_read_schema import CategoryReadResponse


CATEGORY_PAGE_CONTENT = {
    "noticias": {
        "title": "Noticias",
        "description": (
            "A editoria principal concentra desdobramentos, atualizacoes e contexto para acompanhar "
            "o ritmo continuo da cobertura."
        ),
        "rail_title": "Frentes da editoria",
        "rail_items": [
            "Breaking news e desdobramentos ao longo do dia",
            "Chamadas de contexto para leitura rapida",
            "Blocos de continuidade para assuntos em andamento",
        ],
    },
    "negocios": {
        "title": "Negocios",
        "description": (
            "Empresas, mercado e impacto economico aparecem aqui com recorte editorial, "
            "leitura guiada e espaco para analise."
        ),
        "rail_title": "Pontos de acompanhamento",
        "rail_items": [
            "Resultados, aquisicoes e movimentos corporativos",
            "Mercado, investimento e operacao de produto",
            "Sinais economicos que afetam empresas e setores",
        ],
    },
    "tecnologia": {
        "title": "Tecnologia",
        "description": (
            "Software, plataformas, IA e infraestrutura se organizam em uma pagina fixa "
            "pronta para cobertura recorrente."
        ),
        "rail_title": "Assuntos em foco",
        "rail_items": [
            "Inteligencia artificial, plataformas e servicos digitais",
            "Infraestrutura, software e seguranca",
            "Produto, engenharia e lancamentos",
        ],
    },
    "saude": {
        "title": "Saude",
        "description": (
            "A editoria de saude combina servico, contexto e acompanhamento de pesquisas, "
            "hospitais e politicas publicas."
        ),
        "rail_title": "Guias da cobertura",
        "rail_items": [
            "Saude publica, hospitais e politica sanitaria",
            "Tratamentos, estudos e acompanhamento clinico",
            "Leitura de servico para o publico geral",
        ],
    },
    "clima": {
        "title": "Clima",
        "description": (
            "Previsoes, alertas e eventos extremos entram em uma estrutura pronta para "
            "atualizacao constante e leitura pratica."
        ),
        "rail_title": "Entradas da pagina",
        "rail_items": [
            "Alerta de chuva, calor e mudanca brusca de tempo",
            "Cobertura de impacto urbano e regional",
            "Contexto para semana, tendencia e risco",
        ],
    },
    "cultura": {
        "title": "Cultura",
        "description": (
            "Cinema, musica, livros e series aparecem com espaco para agenda, critica, "
            "lancamentos e desdobramentos."
        ),
        "rail_title": "Recortes editoriais",
        "rail_items": [
            "Estreias, festivais e agenda cultural",
            "Critica, bastidores e entrevistas",
            "Series, musica, cinema e literatura",
        ],
    },
    "politica": {
        "title": "Politica",
        "description": (
            "Agenda institucional, bastidores e impacto regulatorio sao organizados com "
            "hierarquia e continuidade de leitura."
        ),
        "rail_title": "Linhas da cobertura",
        "rail_items": [
            "Executivo, legislativo e judiciario",
            "Votacoes, articulacao e agenda oficial",
            "Contexto para medidas e impacto institucional",
        ],
    },
    "ciencia": {
        "title": "Ciencia",
        "description": (
            "Pesquisas, descobertas e inovacoes ganham uma pagina fixa com espaco para "
            "explicacao e aprofundamento."
        ),
        "rail_title": "Pistas de leitura",
        "rail_items": [
            "Estudos academicos e descoberta cientifica",
            "Universidades, laboratorios e missao espacial",
            "Explicadores com contexto e aplicacao pratica",
        ],
    },
    "videos": {
        "title": "Videos",
        "description": (
            "Clipes, entrevistas e trechos especiais ficam em uma editoria pensada "
            "para destaque visual e serie recorrente."
        ),
        "rail_title": "Formatos da editoria",
        "rail_items": [
            "Entrevistas, bastidores e programas especiais",
            "Cortes de cobertura e clipes curtos",
            "Series em episodios e faixas de reproducao",
        ],
    },
}

CATEGORY_ORDER = [
    "noticias",
    "negocios",
    "tecnologia",
    "saude",
    "clima",
    "cultura",
    "politica",
    "ciencia",
    "videos",
]

HOME_FEATURED_CATEGORY_LIMIT = 4
HOME_LATEST_ARTICLES_LIMIT = 6
HOME_WATCH_ARTICLES_LIMIT = 4
HOME_CATEGORY_ARTICLES_LIMIT = 3


def normalize_public_category_slug(value: str) -> str:
    """Normaliza a categoria exposta na API de leitura."""
    normalized_slug = slugify(value or "")
    if normalized_slug == "geral":
        return "noticias"
    return normalized_slug


def resolve_database_category_slug(value: str) -> str:
    """Mapeia o slug publico para o slug real salvo no banco."""
    normalized_slug = slugify(value or "")
    if normalized_slug == "noticias":
        return "geral"
    return normalized_slug


def resolve_public_category_name(category) -> str:
    """Define o nome apresentado ao frontend."""
    if normalize_public_category_slug(category.slug or category.name) == "noticias":
        return "Noticias"
    return category.name


def get_category_meta(category_slug: str, category_name: str) -> dict[str, object]:
    """Retorna metadados editoriais da categoria."""
    default_meta = {
        "title": category_name,
        "description": f"Leitura editorial de {category_name.lower()} com materias renderizadas pelo portal.",
        "rail_title": "Pontos da editoria",
        "rail_items": [
            "Pagina fixa preparada para destaque e continuidade",
            "Cards prontos para dados vindos do banco",
            "Leitura por categoria e materia individual",
        ],
    }
    return {**default_meta, **CATEGORY_PAGE_CONTENT.get(category_slug, {})}


def build_category_summary(category) -> CategoryReadSummary:
    """Converte uma categoria em resumo de leitura."""
    public_slug = normalize_public_category_slug(category.slug or category.name)
    public_name = resolve_public_category_name(category)
    category_meta = get_category_meta(public_slug, public_name)
    return CategoryReadSummary(
        id=category.id,
        name=public_name,
        slug=public_slug,
        title=str(category_meta["title"]),
        description=str(category_meta["description"]),
    )


def build_category_response(category) -> CategoryReadResponse:
    """Converte uma categoria em detalhe editorial."""
    public_slug = normalize_public_category_slug(category.slug or category.name)
    public_name = resolve_public_category_name(category)
    category_meta = get_category_meta(public_slug, public_name)
    return CategoryReadResponse(
        id=category.id,
        name=public_name,
        slug=public_slug,
        title=str(category_meta["title"]),
        description=str(category_meta["description"]),
        rail_title=str(category_meta["rail_title"]),
        rail_items=[str(item) for item in category_meta["rail_items"]],
    )


def category_sort_key(item: CategoryReadSummary) -> tuple[int, str]:
    """Ordena as categorias na sequencia editorial do frontend."""
    order_map = {slug: index for index, slug in enumerate(CATEGORY_ORDER)}
    return (order_map.get(item.slug, len(order_map)), item.name.lower())
