CREATE EXTENSION IF NOT EXISTS postgis;

CREATE SCHEMA IF NOT EXISTS geo_project;

DROP TABLE IF EXISTS geo_project.rejected_occurrences;
DROP TABLE IF EXISTS geo_project.occurrences;
DROP TABLE IF EXISTS geo_project.municipalities;

CREATE TABLE geo_project.occurrences (
    id BIGINT PRIMARY KEY,
    occurrence_date DATE,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    city_name VARCHAR(150),
    state_code CHAR(2),
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    geom GEOMETRY(Point, 4326) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE geo_project.municipalities (
    id SERIAL PRIMARY KEY,
    city_code VARCHAR(20),
    city_name VARCHAR(150) NOT NULL,
    state_code CHAR(2) NOT NULL,
    geom GEOMETRY(MultiPolygon, 4326) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE geo_project.rejected_occurrences (
    id BIGINT,
    reason TEXT NOT NULL,
    occurrence_date TEXT,
    category TEXT,
    latitude TEXT,
    longitude TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_occurrences_geom
ON geo_project.occurrences
USING GIST (geom);

CREATE INDEX idx_municipalities_geom
ON geo_project.municipalities
USING GIST (geom);
