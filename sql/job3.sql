USE `hello_dbms`;

-- Job 3 (students)
DROP TABLE IF EXISTS students;
CREATE TABLE students (
  student_id INT PRIMARY KEY,
  first_name VARCHAR(50),
  last_name VARCHAR(50),
  age INT,
  grade VARCHAR(5)
);

INSERT INTO students (student_id, first_name, last_name, age, grade) VALUES
(1, 'Alice', 'Johnson', 22, 'A+'),
(2, 'Bob', 'Smith', 20, 'B'),
(3, 'Charlie', 'Williams', 21, 'C'),
(4, 'David', 'Brown', 23, 'B+'),
(5, 'Eva', 'Davis', 19, 'A'),
(6, 'Frank', 'Jones', 22, 'C+');

SELECT * FROM students;
SELECT * FROM students WHERE age > 20;
SELECT * FROM students ORDER BY grade ASC;
SELECT * FROM students ORDER BY grade DESC;
