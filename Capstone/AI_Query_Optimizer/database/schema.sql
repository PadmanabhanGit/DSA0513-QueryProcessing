-- Schema for AI Query Optimizer
CREATE DATABASE IF NOT EXISTS ai_query_optimizer;
USE ai_query_optimizer;

CREATE TABLE IF NOT EXISTS employees(
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  department VARCHAR(100),
  salary INT,
  hire_date DATE,
  city VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS departments(
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  manager VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS projects(
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(150),
  department VARCHAR(100),
  budget INT
);

-- Insert 20 sample employee records
INSERT INTO employees (name, department, salary, hire_date, city) VALUES
('Alice Johnson','Engineering',90000,'2018-03-14','Seattle'),
('Bob Smith','Sales',65000,'2019-06-20','Boston'),
('Carol White','Engineering',95000,'2017-11-05','San Francisco'),
('David Brown','HR',60000,'2020-02-28','Chicago'),
('Eva Green','Marketing',70000,'2019-09-10','Denver'),
('Frank Black','Engineering',88000,'2018-12-01','Seattle'),
('Grace Hall','Finance',76000,'2021-05-18','New York'),
('Hank King','Engineering',92000,'2016-07-15','San Francisco'),
('Ivy Lee','Sales',68000,'2020-08-03','Boston'),
('Jack Morgan','Marketing',72000,'2017-10-22','Austin'),
('Kara Nguyen','Engineering',87000,'2022-01-29','Seattle'),
('Liam O''Connor','Finance',81000,'2019-12-13','New York'),
('Mia Patel','HR',59000,'2021-07-05','Chicago'),
('Noah Quinn','Engineering',94000,'2018-04-11','San Francisco'),
('Olivia Roberts','Sales',66000,'2022-03-19','Boston'),
('Paul Sanchez','Engineering',85000,'2020-06-23','Seattle'),
('Quinn Turner','Marketing',73000,'2019-01-17','Austin'),
('Rita Vasquez','Finance',78000,'2020-10-25','New York'),
('Sam Walker','Engineering',91000,'2017-08-08','San Francisco'),
('Tina Young','HR',62000,'2018-05-12','Chicago');

INSERT INTO departments (name, manager) VALUES
('Engineering','Hank King'),
('Sales','Bob Smith'),
('Marketing','Eva Green'),
('Finance','Grace Hall'),
('HR','David Brown');

INSERT INTO projects (name, department, budget) VALUES
('Platform Upgrade','Engineering',400000),
('Customer Expansion','Sales',180000),
('Ad Campaign','Marketing',140000),
('Budget Reporting','Finance',90000),
('Hiring Drive','HR',60000);

CREATE TABLE IF NOT EXISTS query_history(
  id INT PRIMARY KEY AUTO_INCREMENT,
  query_text TEXT,
  execution_time FLOAT,
  predicted_time FLOAT,
  status VARCHAR(100),
  rows_returned INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
