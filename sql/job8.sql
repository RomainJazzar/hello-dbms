USE `somecompany`;

-- Job 8: SomeCompany (CRUD + joins)
CREATE DATABASE IF NOT EXISTS SomeCompany;
USE SomeCompany;

DROP TABLE IF EXISTS Projects;
DROP TABLE IF EXISTS Employees;
DROP TABLE IF EXISTS Departments;

CREATE TABLE Employees (
  employee_id INT PRIMARY KEY,
  first_name VARCHAR(50),
  last_name VARCHAR(50),
  birthdate DATE,
  position VARCHAR(100),
  department_id INT
);

CREATE TABLE Departments (
  department_id INT PRIMARY KEY,
  department_name VARCHAR(100),
  department_head INT,
  location VARCHAR(100)
);

CREATE TABLE Projects (
  project_id INT PRIMARY KEY,
  project_name VARCHAR(100),
  start_date DATE,
  end_date DATE,
  department_id INT
);

ALTER TABLE Employees
  ADD CONSTRAINT fk_emp_dept FOREIGN KEY (department_id) REFERENCES Departments(department_id);

ALTER TABLE Departments
  ADD CONSTRAINT fk_dept_head FOREIGN KEY (department_head) REFERENCES Employees(employee_id);

ALTER TABLE Projects
  ADD CONSTRAINT fk_proj_dept FOREIGN KEY (department_id) REFERENCES Departments(department_id);

INSERT INTO Employees VALUES
(1,'John','Doe','1990-05-15','Software Engineer',1),
(2,'Jane','Smith','1985-08-20','Project Manager',2),
(3,'Mike','Johnson','1992-03-10','Data Analyst',1),
(4,'Emily','Brown','1988-12-03','UX Designer',1),
(5,'Alex','Williams','1995-06-28','Software Developer',1),
(6,'Sarah','Miller','1987-09-18','HR Specialist',3),
(7,'Ethan','Clark','1991-02-14','Database Administrator',1),
(8,'Olivia','Garcia','1984-07-22','Marketing Manager',2),
(9,'Emilia','Clark','1986-01-12','HR Manager',3),
(10,'Daniel','Taylor','1993-11-05','Systems Analyst',1),
(11,'William','Lee','1994-08-15','Software Engineer',1),
(12,'Sophia','Baker','1990-06-25','IT Manager',2);

INSERT INTO Departments VALUES
(1,'IT',11,'Headquarters'),
(2,'Project Management',2,'Branch Office West'),
(3,'Human Resources',6,'Branch Office East');

INSERT INTO Employees VALUES
(13,'Liam','Martin','1996-04-11','DevOps Engineer',1),
(14,'Noah','Bernard','1997-01-09','Junior Data Analyst',1),
(15,'Emma','Dubois','1992-10-02','Product Owner',2),
(16,'Chloe','Moreau','1991-06-19','Recruiter',3),
(17,'Lucas','Petit','1995-08-30','Frontend Developer',1),
(18,'Mia','Roux','1993-12-14','Scrum Master',2);

SELECT first_name, last_name, position FROM Employees;

UPDATE Employees SET position='Senior Data Analyst' WHERE employee_id=3;

DELETE FROM Employees WHERE employee_id=14;

SELECT e.first_name, e.last_name, d.department_name, d.location
FROM Employees e
JOIN Departments d ON d.department_id = e.department_id
ORDER BY d.department_name;

SELECT d.department_name, d.location, e.first_name AS head_first_name, e.last_name AS head_last_name
FROM Departments d
LEFT JOIN Employees e ON e.employee_id = d.department_head
ORDER BY d.department_name;

INSERT INTO Departments (department_id, department_name, department_head, location)
VALUES (4,'Marketing',8,'Branch Office South');

UPDATE Employees SET department_id=4 WHERE employee_id IN (8);

INSERT INTO Projects VALUES
(1,'Migration DB','2025-01-10','2025-03-01',1),
(2,'New Website','2025-02-01','2025-04-15',1),
(3,'Hiring Sprint','2025-01-20','2025-02-28',3),
(4,'Marketing Campaign','2025-02-15','2025-05-10',4);

SELECT d.department_name, COUNT(p.project_id) AS nb_projects
FROM Departments d
LEFT JOIN Projects p ON p.department_id = d.department_id
GROUP BY d.department_id, d.department_name
ORDER BY nb_projects DESC;
