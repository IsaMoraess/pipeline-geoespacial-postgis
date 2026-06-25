from pathlib import Path
import os

import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine, text


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/geodb")

CLEAN_GEOJSON_PATH = Path("data/processed/occurrences_clean.geojson")
REJECTED_CSV_PATH = Path("data/processed/rejected_occurrences.csv")


def load_data_to_postgis() -> None:
    engine = create_engine(DATABASE_URL)

    occurrences_gdf = gpd.read_file(CLEAN_GEOJSON_PATH)
    rejected_df = pd.read_csv(REJECTED_CSV_PATH)

    occurrences_gdf["occurrence_date"] = pd.to_datetime(
        occurrences_gdf["occurrence_date"],
        errors="coerce"
    ).dt.date

    occurrences_gdf = occurrences_gdf.rename_geometry("geom")

    occurrences_gdf = occurrences_gdf[
        [
            "id",
            "occurrence_date",
            "category",
            "description",
            "city_name",
            "state_code",
            "latitude",
            "longitude",
            "geom",
        ]
    ]

    rejected_df = rejected_df[
        [
            "id",
            "reason",
            "occurrence_date",
            "category",
            "latitude",
            "longitude",
        ]
    ]

    with engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE geo_project.occurrences RESTART IDENTITY;"))
        connection.execute(text("TRUNCATE TABLE geo_project.rejected_occurrences;"))

    occurrences_gdf.to_postgis(
        name="occurrences",
        con=engine,
        schema="geo_project",
        if_exists="append",
        index=False,
    )

    rejected_df.to_sql(
        name="rejected_occurrences",
        con=engine,
        schema="geo_project",
        if_exists="append",
        index=False,
    )

    with engine.connect() as connection:
        valid_count = connection.execute(
            text("SELECT COUNT(*) FROM geo_project.occurrences;")
        ).scalar()

        rejected_count = connection.execute(
            text("SELECT COUNT(*) FROM geo_project.rejected_occurrences;")
        ).scalar()

    print("Carga no PostGIS concluída com sucesso.")
    print(f"Registros válidos carregados: {valid_count}")
    print(f"Registros rejeitados carregados: {rejected_count}")


if __name__ == "__main__":
    load_data_to_postgis()
