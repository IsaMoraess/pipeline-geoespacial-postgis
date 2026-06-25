from datetime import datetime
from pathlib import Path
import subprocess

from airflow.decorators import dag, task


PROJECT_ROOT = Path("/opt/airflow")


def run_command(command: str) -> None:
    result = subprocess.run(
        command,
        shell=True,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
    )

    print(result.stdout)

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError(f"Erro ao executar comando: {command}")


@dag(
    dag_id="geospatial_data_pipeline",
    description="Pipeline de dados geoespaciais com Python, GeoPandas, PostGIS e Folium",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["geospatial", "postgis", "portfolio"],
)
def geospatial_data_pipeline():

    @task
    def generate_sample_data():
        run_command("python src/generate_sample_data.py")

    @task
    def transform_and_validate_data():
        run_command("python src/transform_validate.py")

    @task
    def load_data_to_postgis():
        run_command("python src/load_postgis.py")

    @task
    def create_analytics_views():
        run_command("python src/create_views.py")

    @task
    def generate_interactive_map():
        run_command("python src/generate_map.py")

    generated = generate_sample_data()
    transformed = transform_and_validate_data()
    loaded = load_data_to_postgis()
    views = create_analytics_views()
    mapped = generate_interactive_map()

    generated >> transformed >> loaded >> views >> mapped


geospatial_data_pipeline()
