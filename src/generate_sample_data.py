from pathlib import Path
import random

import pandas as pd
from faker import Faker


fake = Faker("pt_BR")

OUTPUT_PATH = Path("data/raw/occurrences.csv")
TOTAL_RECORDS = 50_000

CATEGORIES = [
    "Furto",
    "Roubo",
    "Acidente",
    "Iluminação pública",
    "Buraco na via",
    "Ocorrência ambiental",
]

CITIES = [
    ("São Paulo", "SP", -23.5505, -46.6333),
    ("Campinas", "SP", -22.9056, -47.0608),
    ("Santos", "SP", -23.9608, -46.3336),
    ("Guarulhos", "SP", -23.4545, -46.5333),
    ("Osasco", "SP", -23.5329, -46.7918),
]


def random_coordinate(base_lat: float, base_lon: float) -> tuple[float, float]:
    lat = base_lat + random.uniform(-0.08, 0.08)
    lon = base_lon + random.uniform(-0.08, 0.08)
    return round(lat, 6), round(lon, 6)


def generate_occurrences() -> pd.DataFrame:
    records = []

    for occurrence_id in range(1, TOTAL_RECORDS + 1):
        city_name, state_code, base_lat, base_lon = random.choice(CITIES)
        latitude, longitude = random_coordinate(base_lat, base_lon)

        records.append(
            {
                "id": occurrence_id,
                "occurrence_date": fake.date_between(start_date="-2y", end_date="today"),
                "category": random.choice(CATEGORIES),
                "description": fake.sentence(nb_words=8),
                "city_name": city_name,
                "state_code": state_code,
                "latitude": latitude,
                "longitude": longitude,
            }
        )

    df = pd.DataFrame(records)

    invalid_rows = pd.DataFrame(
        [
            {
                "id": TOTAL_RECORDS + 1,
                "occurrence_date": "data_invalida",
                "category": "Roubo",
                "description": "Registro inválido para teste",
                "city_name": "São Paulo",
                "state_code": "SP",
                "latitude": -23.5505,
                "longitude": -46.6333,
            },
            {
                "id": TOTAL_RECORDS + 2,
                "occurrence_date": fake.date(),
                "category": "",
                "description": "Categoria vazia para teste",
                "city_name": "Campinas",
                "state_code": "SP",
                "latitude": -22.9056,
                "longitude": -47.0608,
            },
            {
                "id": TOTAL_RECORDS + 3,
                "occurrence_date": fake.date(),
                "category": "Acidente",
                "description": "Latitude ausente para teste",
                "city_name": "Santos",
                "state_code": "SP",
                "latitude": None,
                "longitude": -46.3336,
            },
            {
                "id": TOTAL_RECORDS + 4,
                "occurrence_date": fake.date(),
                "category": "Furto",
                "description": "Coordenada fora do Brasil para teste",
                "city_name": "Osasco",
                "state_code": "SP",
                "latitude": 80.0,
                "longitude": 120.0,
            },
        ]
    )

    return pd.concat([df, invalid_rows], ignore_index=True)


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = generate_occurrences()
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Arquivo gerado: {OUTPUT_PATH}")
    print(f"Total de registros: {len(df)}")


if __name__ == "__main__":
    main()
