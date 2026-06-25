from pathlib import Path

import geopandas as gpd
import pandas as pd


RAW_PATH = Path("data/raw/occurrences.csv")
PROCESSED_DIR = Path("data/processed")
CLEAN_GEOJSON_PATH = PROCESSED_DIR / "occurrences_clean.geojson"
REJECTED_CSV_PATH = PROCESSED_DIR / "rejected_occurrences.csv"


def add_reason(current_reason: str, new_reason: str) -> str:
    if pd.isna(current_reason) or current_reason == "":
        return new_reason
    return f"{current_reason}; {new_reason}"


def transform_and_validate() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(RAW_PATH)

    initial_rows = len(df)

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    df["validation_reason"] = ""

    df["occurrence_date_parsed"] = pd.to_datetime(
        df["occurrence_date"],
        errors="coerce"
    )

    df["latitude_numeric"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude_numeric"] = pd.to_numeric(df["longitude"], errors="coerce")

    invalid_date_mask = df["occurrence_date_parsed"].isna()
    empty_category_mask = df["category"].isna() | (df["category"].astype(str).str.strip() == "")
    missing_coordinates_mask = df["latitude_numeric"].isna() | df["longitude_numeric"].isna()

    outside_brazil_mask = (
        ~missing_coordinates_mask
        & (
            ~df["latitude_numeric"].between(-34, 6)
            | ~df["longitude_numeric"].between(-74, -34)
        )
    )

    duplicated_id_mask = df["id"].duplicated(keep=False)

    validation_rules = [
        (invalid_date_mask, "data inválida"),
        (empty_category_mask, "categoria vazia"),
        (missing_coordinates_mask, "latitude/longitude ausente ou inválida"),
        (outside_brazil_mask, "coordenada fora do Brasil"),
        (duplicated_id_mask, "id duplicado"),
    ]

    for mask, reason in validation_rules:
        df.loc[mask, "validation_reason"] = df.loc[mask, "validation_reason"].apply(
            lambda current: add_reason(current, reason)
        )

    rejected_df = df[df["validation_reason"] != ""].copy()
    valid_df = df[df["validation_reason"] == ""].copy()

    valid_df["occurrence_date"] = valid_df["occurrence_date_parsed"].dt.date
    valid_df["latitude"] = valid_df["latitude_numeric"]
    valid_df["longitude"] = valid_df["longitude_numeric"]
    valid_df["category"] = valid_df["category"].str.strip().str.title()
    valid_df["city_name"] = valid_df["city_name"].str.strip().str.title()
    valid_df["state_code"] = valid_df["state_code"].str.strip().str.upper()

    valid_df = valid_df[
        [
            "id",
            "occurrence_date",
            "category",
            "description",
            "city_name",
            "state_code",
            "latitude",
            "longitude",
        ]
    ]

    gdf = gpd.GeoDataFrame(
        valid_df,
        geometry=gpd.points_from_xy(valid_df["longitude"], valid_df["latitude"]),
        crs="EPSG:4326"
    )

    rejected_df = rejected_df[
        [
            "id",
            "validation_reason",
            "occurrence_date",
            "category",
            "latitude",
            "longitude",
        ]
    ].rename(columns={"validation_reason": "reason"})

    gdf.to_file(CLEAN_GEOJSON_PATH, driver="GeoJSON")
    rejected_df.to_csv(REJECTED_CSV_PATH, index=False)

    print("Validação concluída com sucesso.")
    print(f"Registros brutos: {initial_rows}")
    print(f"Registros válidos: {len(gdf)}")
    print(f"Registros rejeitados: {len(rejected_df)}")
    print(f"GeoJSON limpo: {CLEAN_GEOJSON_PATH}")
    print(f"CSV de rejeitados: {REJECTED_CSV_PATH}")


if __name__ == "__main__":
    transform_and_validate()
