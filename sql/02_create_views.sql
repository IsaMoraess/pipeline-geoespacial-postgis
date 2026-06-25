DROP VIEW IF EXISTS geo_project.vw_occurrences_by_city;
DROP VIEW IF EXISTS geo_project.vw_occurrences_by_category;
DROP VIEW IF EXISTS geo_project.vw_daily_occurrences;
DROP VIEW IF EXISTS geo_project.vw_city_category_ranking;

CREATE VIEW geo_project.vw_occurrences_by_city AS
SELECT
    city_name,
    state_code,
    COUNT(*) AS total_occurrences,
    MIN(occurrence_date) AS first_occurrence_date,
    MAX(occurrence_date) AS last_occurrence_date,
    ST_Centroid(ST_Collect(geom)) AS geom
FROM geo_project.occurrences
GROUP BY city_name, state_code
ORDER BY total_occurrences DESC;

CREATE VIEW geo_project.vw_occurrences_by_category AS
SELECT
    category,
    COUNT(*) AS total_occurrences,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM geo_project.occurrences
GROUP BY category
ORDER BY total_occurrences DESC;

CREATE VIEW geo_project.vw_daily_occurrences AS
SELECT
    occurrence_date,
    COUNT(*) AS total_occurrences
FROM geo_project.occurrences
GROUP BY occurrence_date
ORDER BY occurrence_date;

CREATE VIEW geo_project.vw_city_category_ranking AS
SELECT
    city_name,
    state_code,
    category,
    COUNT(*) AS total_occurrences
FROM geo_project.occurrences
GROUP BY city_name, state_code, category
ORDER BY total_occurrences DESC;
