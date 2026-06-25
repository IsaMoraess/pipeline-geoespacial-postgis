from pathlib import Path
import os

from sqlalchemy import create_engine


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5433/geodb",
)

SQL_PATH = Path("sql/02_create_views.sql")


def create_views() -> None:
    engine = create_engine(DATABASE_URL)

    sql = SQL_PATH.read_text()

    with engine.begin() as connection:
        connection.exec_driver_sql(sql)

    print("Views analíticas criadas com sucesso.")


if __name__ == "__main__":
    create_views()
