USE `hello_dbms`;

-- Job 2 (world) - patterns
SELECT Name FROM world WHERE Name LIKE 'B%';
SELECT Name FROM world WHERE Name LIKE 'Al%';
SELECT Name FROM world WHERE Name LIKE '%y';
SELECT Name FROM world WHERE Name LIKE '%land';
SELECT Name FROM world WHERE Name LIKE '%w%';
SELECT Name FROM world WHERE Name LIKE '%oo%' OR Name LIKE '%ee%';
SELECT Name FROM world WHERE Name LIKE '%a%a%a%';
SELECT Name FROM world WHERE Name LIKE '_r%';
