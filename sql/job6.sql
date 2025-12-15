USE `hello_dbms`;

-- Job 6 (world aggregations)
SELECT SUM(Population) AS world_population
FROM world;

SELECT Continent, SUM(Population) AS continent_population
FROM world
GROUP BY Continent
ORDER BY continent_population DESC;

SELECT Continent, SUM(GDP * Population) AS total_gdp_proxy
FROM world
GROUP BY Continent
ORDER BY total_gdp_proxy DESC;

SELECT SUM(GDP * Population) AS africa_total_gdp_proxy
FROM world
WHERE Continent='Africa';

SELECT COUNT(*) AS nb_countries
FROM world
WHERE SurfaceArea >= 1000000;

SELECT SUM(Population) AS baltic_population
FROM world
WHERE Name IN ('Estonia','Latvia','Lithuania');

SELECT Continent, COUNT(*) AS nb_countries
FROM world
GROUP BY Continent
ORDER BY nb_countries DESC;

SELECT Continent, SUM(Population) AS pop_total
FROM world
GROUP BY Continent
HAVING SUM(Population) >= 100000000
ORDER BY pop_total DESC;
