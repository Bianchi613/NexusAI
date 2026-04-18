from app.db import init_db
from app.core.pipeline import NewsPipeline


def main() -> None:
    init_db()
    pipeline = NewsPipeline()
    result = pipeline.run()
    print(f"Pipeline finalizado. Materias geradas: {len(result)}")


if __name__ == "__main__":
    main()
