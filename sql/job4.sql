USE `hello_dbms`;

-- Job 4 (nobel)
DROP TABLE IF EXISTS nobel;
CREATE TABLE nobel (
  yr INT,
  subject VARCHAR(50),
  winner VARCHAR(200)
);

INSERT INTO nobel (yr, subject, winner) VALUES
(1986, 'Chemistry', 'Dudley R. Herschbach'),
(1986, 'Chemistry', 'Yuan T. Lee'),
(1986, 'Chemistry', 'John C. Polanyi'),
(1986, 'Literature', 'Wole Soyinka'),
(1986, 'Peace', 'Elie Wiesel'),
(1986, 'Physics', 'Ernst Ruska'),
(1986, 'Physics', 'Gerd Binnig'),
(1986, 'Physics', 'Heinrich Rohrer'),
(1967, 'Literature', 'Miguel Ángel Asturias'),
(1921, 'Physics', 'Albert Einstein'),
(1980, 'Literature', 'Czesław Miłosz'),
(1981, 'Literature', 'Elias Canetti'),
(1982, 'Literature', 'Gabriel García Márquez'),
(1983, 'Literature', 'William Golding'),
(1984, 'Literature', 'Jaroslav Seifert'),
(1985, 'Literature', 'Claude Simon'),
(1987, 'Literature', 'Joseph Brodsky'),
(1988, 'Literature', 'Naguib Mahfouz'),
(1989, 'Literature', 'Camilo José Cela');

SELECT * FROM nobel WHERE yr = 1986;
SELECT * FROM nobel WHERE yr = 1967 AND subject = 'Literature';
SELECT yr, subject FROM nobel WHERE winner = 'Albert Einstein';
SELECT yr, subject, winner
FROM nobel
WHERE subject = 'Literature' AND yr BETWEEN 1980 AND 1989
ORDER BY yr;
SELECT * FROM nobel WHERE subject = 'Mathematics';
SELECT COUNT(*) AS math_prizes FROM nobel WHERE subject = 'Mathematics';
