USE `hello_dbms`;

-- Job 9: Explore at least 6 variables (insights)
SELECT Name, Continent, Literacy
FROM world
WHERE Literacy IS NOT NULL
ORDER BY Literacy DESC
LIMIT 10;

SELECT Name, Continent, Literacy
FROM world
WHERE Literacy IS NOT NULL
ORDER BY Literacy ASC
LIMIT 10;

SELECT Name, Continent, NetMigration
FROM world
ORDER BY NetMigration DESC
LIMIT 10;

SELECT Name, Continent, NetMigration
FROM world
ORDER BY NetMigration ASC
LIMIT 10;

SELECT Name, Continent, Birthrate, Deathrate,
       (Birthrate - Deathrate) AS natural_growth
FROM world
ORDER BY natural_growth DESC
LIMIT 15;

SELECT Name, Continent, InfantMortality
FROM world
ORDER BY InfantMortality DESC
LIMIT 15;

SELECT Name, Continent, Arable, Crops, (Arable + Crops) AS arable_plus_crops
FROM world
ORDER BY arable_plus_crops DESC
LIMIT 15;

SELECT Name, Continent, GDP, Literacy
FROM world
WHERE GDP IS NOT NULL AND Literacy IS NOT NULL
ORDER BY GDP DESC
LIMIT 20;
