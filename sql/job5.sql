USE `hello_dbms`;

-- Job 5 (world)
SELECT Name, Population
FROM world
WHERE Population > (SELECT Population FROM world WHERE Name='Russia')
ORDER BY Population DESC;

SELECT Name, GDP
FROM world
WHERE Continent='Europe' AND GDP > (SELECT GDP FROM world WHERE Name='Italy')
ORDER BY GDP DESC;

SELECT Name, Population
FROM world
WHERE Population > (SELECT Population FROM world WHERE Name='United Kingdom')
  AND Population < (SELECT Population FROM world WHERE Name='Germany')
ORDER BY Population DESC;

SELECT Name,
       CONCAT(ROUND(Population / (SELECT Population FROM world WHERE Name='Germany') * 100), '%') AS pourcentage
FROM world
WHERE Continent='Europe'
ORDER BY Population DESC;

SELECT w1.Continent, w1.Name, w1.SurfaceArea
FROM world w1
JOIN (
  SELECT Continent, MAX(SurfaceArea) AS max_area
  FROM world
  GROUP BY Continent
) w2
ON w1.Continent = w2.Continent AND w1.SurfaceArea = w2.max_area
ORDER BY w1.Continent;

SELECT Continent
FROM world
GROUP BY Continent
HAVING MAX(Population) <= 25000000;
