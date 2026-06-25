# Pipeline de Dados Geoespaciais com Python, Airflow e PostGIS

Projeto de engenharia de dados geoespaciais desenvolvido para demonstrar um fluxo completo de ingestão, limpeza, validação, carga em banco espacial e visualização em mapa.

O pipeline processa milhares de registros com coordenadas geográficas, transforma os dados em geometrias, valida inconsistências, carrega as informações em PostgreSQL/PostGIS e gera um mapa interativo com Folium.

## Tecnologias utilizadas

* Python
* Pandas
* GeoPandas
* PostgreSQL
* PostGIS
* Apache Airflow
* Docker
* SQLAlchemy
* GeoAlchemy2
* Folium
* Faker

## Objetivo do projeto

O objetivo é simular um pipeline real de dados geoespaciais, com etapas comuns em projetos de dados territoriais:

* ingestão de milhares de registros;
* limpeza e padronização dos dados;
* validação de datas, categorias e coordenadas;
* separação de registros inválidos;
* conversão de latitude/longitude em geometria;
* carga em PostgreSQL/PostGIS;
* criação de views analíticas;
* geração de mapa interativo.

## Arquitetura do pipeline

```text
Geração de dados simulados
        ↓
Limpeza e validação
        ↓
Carga no PostgreSQL/PostGIS
        ↓
Criação de views analíticas
        ↓
Geração de mapa interativo
```

## Estrutura do projeto

```text
pipeline-geoespacial-postgis/
│
├── dags/
│   └── geospatial_pipeline_dag.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── geo/
│
├── maps/
│   └── occurrences_map.html
│
├── sql/
│   ├── 01_create_tables.sql
│   └── 02_create_views.sql
│
├── src/
│   ├── generate_sample_data.py
│   ├── transform_validate.py
│   ├── load_postgis.py
│   ├── create_views.py
│   └── generate_map.py
│
├── Dockerfile.airflow
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Etapas do pipeline

### 1. Geração dos dados

O projeto gera uma base simulada com 50 mil registros de ocorrências, contendo:

* ID;
* data da ocorrência;
* categoria;
* descrição;
* cidade;
* UF;
* latitude;
* longitude.

Também são adicionados registros inválidos propositalmente para testar a etapa de validação.

### 2. Limpeza e validação

A etapa de validação verifica:

* datas inválidas;
* categorias vazias;
* latitude/longitude ausentes;
* coordenadas fora do Brasil;
* IDs duplicados.

Os registros válidos são convertidos em GeoDataFrame e salvos como GeoJSON.

Os registros inválidos são separados em um arquivo de rejeitados.

Resultado esperado:

```text
Registros brutos: 50004
Registros válidos: 50000
Registros rejeitados: 4
```

### 3. Carga no PostGIS

Os dados tratados são carregados em tabelas do schema `geo_project` no PostgreSQL/PostGIS:

* `geo_project.occurrences`
* `geo_project.rejected_occurrences`

A tabela de ocorrências possui uma coluna espacial do tipo `GEOMETRY(Point, 4326)`.

### 4. Views analíticas

O projeto cria views SQL para análise:

* total de ocorrências por cidade;
* total de ocorrências por categoria;
* evolução diária;
* ranking por cidade e categoria.

Exemplo de análise por cidade:

```text
Osasco    | SP | 10038
Campinas  | SP | 10029
Guarulhos | SP | 10024
Santos    | SP | 10000
São Paulo | SP | 9909
```

### 5. Visualização em mapa

O pipeline gera um mapa interativo em HTML com:

* mapa de calor;
* amostra de pontos;
* popup com categoria, cidade, data e ID;
* resumo por cidade.

Arquivo gerado:

```text
maps/occurrences_map.html
```

## Orquestração com Airflow

A DAG `geospatial_data_pipeline` orquestra todo o fluxo:

```text
generate_sample_data
        ↓
transform_and_validate_data
        ↓
load_data_to_postgis
        ↓
create_analytics_views
        ↓
generate_interactive_map
```

## Como executar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/IsaMoraess/pipeline-geoespacial-postgis.git
cd pipeline-geoespacial-postgis
```

### 2. Subir os containers

```bash
docker compose up -d --build
```

### 3. Acessar o Airflow

Abra no navegador:

```text
http://127.0.0.1:8080
```

Login:

```text
Usuário: admin
Senha: admin
```

### 4. Rodar a DAG

No Airflow, procure pela DAG:

```text
geospatial_data_pipeline
```

Ative a DAG e clique em **Trigger DAG**.

## Execução local sem Airflow

Também é possível executar as etapas manualmente:

```bash
python src/generate_sample_data.py
python src/transform_validate.py
python src/load_postgis.py
python src/create_views.py
python src/generate_map.py
```

## Resultado final

Ao final da execução, o pipeline:

* gera 50 mil registros simulados;
* valida e separa registros inconsistentes;
* carrega os dados no PostGIS;
* cria views analíticas;
* gera um mapa interativo em HTML;
* executa todo o processo via Airflow.

## Destaques técnicos

* Pipeline orquestrado com Apache Airflow;
* banco PostgreSQL com extensão PostGIS;
* manipulação geoespacial com GeoPandas;
* validação e tratamento de dados com Pandas;
* carga de dados espaciais no banco;
* visualização interativa com Folium;
* ambiente containerizado com Docker.

## Status

Projeto funcional e executado com sucesso.
