-- Sample SELECT queries for the AI Query Optimizer application

SELECT * FROM employees;
SELECT name, department, salary FROM employees WHERE salary > 80000 ORDER BY salary DESC;
SELECT department, AVG(salary) as avg_salary FROM employees GROUP BY department;
SELECT e.name, e.department, p.name as project, p.budget FROM employees e
JOIN projects p ON e.department = p.department
WHERE e.salary > 85000;
SELECT d.name AS department, d.manager, COUNT(e.id) AS employee_count
FROM departments d
LEFT JOIN employees e ON e.department = d.name
GROUP BY d.name, d.manager;
SELECT e.name, e.city, p.name AS project FROM employees e
JOIN projects p ON e.department = p.department
WHERE e.city = 'Seattle'
ORDER BY e.name;
