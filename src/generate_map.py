from pathlib import Path

import folium
import geopandas as gpd
import pandas as pd
from folium.plugins import HeatMap, MarkerCluster
from sqlalchemy import create_engine


DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/geodb"
OUTPUT_PATH = Path("maps/occurrences_map.html")


def generate_map() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(DATABASE_URL)

    occurrences_query = """
        SELECT
            id,
            occurrence_date,
            category,
            city_name,
            state_code,
            latitude,
            longitude,
            geom
        FROM geo_project.occurrences;
    """

    city_query = """
        SELECT
            city_name,
            state_code,
            total_occurrences,
            ST_Y(geom) AS latitude,
            ST_X(geom) AS longitude
        FROM geo_project.vw_occurrences_by_city;
    """

    gdf = gpd.read_postgis(
        occurrences_query,
        con=engine,
        geom_col="geom",
    )

    city_df = pd.read_sql(city_query, con=engine)

    center_lat = gdf["latitude"].mean()
    center_lon = gdf["longitude"].mean()

    map_object = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=8,
        tiles="CartoDB positron",
    )

    heat_data = gdf[["latitude", "longitude"]].dropna().values.tolist()

    HeatMap(
        heat_data,
        name="Mapa de calor",
        radius=12,
        blur=18,
        min_opacity=0.3,
    ).add_to(map_object)

    marker_cluster = MarkerCluster(name="Amostra de ocorrências").add_to(map_object)

    sample_gdf = gdf.sample(
        n=min(2000, len(gdf)),
        random_state=42,
    )

    for _, row in sample_gdf.iterrows():
        popup_text = f"""
        <b>Categoria:</b> {row["category"]}<br>
        <b>Cidade:</b> {row["city_name"]}/{row["state_code"]}<br>
        <b>Data:</b> {row["occurrence_date"]}<br>
        <b>ID:</b> {row["id"]}
        """

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=3,
            popup=folium.Popup(popup_text, max_width=300),
            fill=True,
            fill_opacity=0.7,
            weight=1,
        ).add_to(marker_cluster)

    city_layer = folium.FeatureGroup(name="Resumo por cidade")

    for _, row in city_df.iterrows():
        popup_text = f"""
        <b>Cidade:</b> {row["city_name"]}/{row["state_code"]}<br>
        <b>Total de ocorrências:</b> {row["total_occurrences"]}
        """

        tooltip_text = f"{row["city_name"]}: {row["total_occurrences"]} ocorrências"

        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=tooltip_text,
        ).add_to(city_layer)

    city_layer.add_to(map_object)

    folium.LayerControl(collapsed=False).add_to(map_object)

    map_object.save(OUTPUT_PATH)

    print("Mapa gerado com sucesso.")
    print(f"Arquivo: {OUTPUT_PATH}")
    print(f"Total de ocorrências usadas no heatmap: {len(gdf)}")
    print(f"Total de pontos na amostra: {len(sample_gdf)}")
    print(f"Total de cidades no resumo: {len(city_df)}")


if __name__ == "__main__":
    generate_map()
