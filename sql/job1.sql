USE `hello_dbms`;

-- Job 1 (world)
SELECT Population FROM world WHERE Name = 'Germany';

SELECT Name, Population
FROM world
WHERE Name IN ('Sweden','Norway','Denmark');

SELECT Name, SurfaceArea
FROM world
WHERE SurfaceArea > 200000 AND SurfaceArea < 300000;
