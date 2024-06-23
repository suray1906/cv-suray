--Простая выборка
--1.	Выбрать названия всех отделов. 
SELECT dept_name from empoyees.department;
--2.	Выбрать названия всех должностей (без повторений).
select distinct title from employees.title; 
--Выборка с упорядочением
--1.	Выбрать названия всех отделов с упорядочением по возрастанию. 
select dept_name from employees.department  order by dept_name asc;
--2.	Выбрать названия всех должностей (без повторений) с упорядочением по убыванию.
select distinct title from employees.title order by title desc;

Создать тип данных сертификат
set search_path to employees, public;

--1.	Найти номер и дату рождения служащего Tzvetan Zielinski.


set search_path to employees, public;
select id, birth_date, first_name, last_name 
from employee
where first_name = 'Tzvetan' and last_name ='Zielinski';

--2.	Выбрать имена и фамилии служащих, поступивших на работу после 20 апреля 1999 г. 
set search_path to employees, public;
select first_name, last_name, hire_date
from employee
where hire_date> '1999-04-20'

--3.	Найти номера, имена и фамилии служащих, фамилии которых начинаются в буквы “Z”.


set search_path to employees, public;
select first_name, last_name, hire_date
from employee
where left(last_name,1) = 'Z';

--4.	Найти номера, имена и фамилии служащих, фамилии которых содержат 8 букв.
set search_path to employees, public;
select first_name, last_name, hire_date
from employee
where length(last_name)=8;

--5.	Найти номера и размер зарплаты служащих, которые получали (получают) зарплату в диапазоне от 80000 до 90000.


select employee_id, amount
from salary
where amount between  80000 and 90000


-- 6.	Найти номера и размер зарплаты служащих, которые в настоящее время получают зарплату, большую 90000.
select employee_id, amount
from salary
where amount>90000 and (current_date between from_date and to_date)

--SECOND LESSON
SET search_path TO employees, public;

alter table certificates add column
certificate_type cert_type not NULL defaul 'U';
select * from certificates;
--7.	Найти номера служащих, которые являлись менеджерами отделов в 1999 г.

set search_path to employees, public;
SELECT employee_id
FROM department_manager
 WHERE from_date <= '1999-12-31' AND to_date >= '1999-01-01';
--8.	Найти список названий должностей, занимаемых служащими в настоящее время.
SET search_path TO employees, public;
SELECT DISTINCT title 
FROM title 
WHERE CURRENT_DATE BETWEEN from_date AND to_date;

--9.	Выдать число служащих мужского пола.
SET search_path TO employees, public;
SELECT COUNT(*) 
FROM employee 
WHERE gender = 'M';

--10.	Выдать число служащих с фамилией Sommer.
SET search_path TO employees, public;
SELECT COUNT(*) 
FROM employee 
WHERE last_name = 'Sommer';

--11.	Работал ли когда-либо инженером служащий с номером 10009? (Ответить yes или no).
SET search_path TO employees, public;
SELECT 
    CASE 
        WHEN (SELECT COUNT(*) FROM title WHERE employee_id = 10009 AND title = 'Engineer') > 0 
        THEN 'yes' 
        ELSE 'no' 
    END;



--Выборка с группировкой
--1.	Выдать число служащих женского и мужского пола. 
select count(*), gender from employee group by gender

--2.	Выдать номера отделов и число служащих, работающих в них в настоящее время.
SELECT department_id, COUNT(*) 
FROM department_employee 
WHERE CURRENT_DATE BETWEEN from_date AND to_date
GROUP BY department_id;
--3.	Выдать номера отделов и число служащих, работавших в них 1 мая 1998 г.

--4.	Найти номера отделов, в которых в настоящее время работает больше 20 человек.
select department_id, count(*)  
from department_employee de 
where current_date between de.from_date and de.to_date
group by de.department_id 
having  count(*)   > 20;
--5.	Найти максимальную, минимальную и среднюю зарплату служащего с номером 10020 за все время его работы.
sql
   SET search_path TO employees, public;
   SELECT MAX(amount) AS max_salary, MIN(amount) AS min_salary, AVG(amount) AS avg_salary
   FROM salary
   WHERE employee_id = 10020;
   

--6.	Выдать названия должностей и число служащих, которые их занимали или занимают.

sql
   SET search_path TO employees, public;
   SELECT title, COUNT(employee_id) AS num_employees
   FROM title
   GROUP BY title;
   

--7.	Найти даты, в которые на работу было принято более одного служащего, а также число этих служащих.
SET search_path TO employees, public;
SELECT hire_date, COUNT(id) AS num_hired
FROM employee
GROUP BY hire_date
HAVING COUNT(id) > 1;

--8.	Найти номера отделов, у которых в настоящее время имеется более одного менеджера.

sql
   SET search_path TO employees, public;
   SELECT department_id, COUNT(employee_id) AS num_managers
   FROM department_manager
   WHERE CURRENT_DATE BETWEEN from_date AND to_date
   GROUP BY department_id
   HAVING COUNT(employee_id) > 1;
   
--9.	Найти номера служащих, которые в настоящее время получают более одной зарплаты.

sql
   SET search_path TO employees, public;
   SELECT employee_id
   FROM salary
   WHERE CURRENT_DATE BETWEEN from_date AND to_date
   GROUP BY employee_id
   HAVING COUNT(*) > 1;
   
   
   
   
   
--   Вложенный запрос
--1.	Найти номера, имена и фамилии служащих, которые в настоящее время занимают должность старшего инженера.
SET search_path TO employees, public;
SELECT id, first_name, last_name
FROM employee
WHERE id IN (
    SELECT employee_id   
	FROM title 
    WHERE title = 'Senior Engineer' AND CURRENT_DATE BETWEEN from_date AND to_date);
--2.	Найти номера, имена и фамилии служащих, которые в настоящее время работают более чем в одном отделе.
SELECT id, first_name, last_name
FROM employee
WHERE id IN (
    SELECT employee_id
    FROM department_employee
    WHERE CURRENT_DATE BETWEEN from_date AND to_date
    GROUP BY employee_id
    HAVING COUNT(department_id) > 1
);

--3.	Найти номера и имена служащих, которые когда-либо являлись менеджерами.
SET search_path TO employees, public;
SELECT id, first_name, last_name
FROM employee
WHERE id IN ( 
   SELECT employee_id 
   FROM department_manager
   );
--4.	Найти номера и имена служащих, работающих в настоящее время в отделах с числом служащих, большим 50.

SELECT id, first_name, last_name
FROM employee
WHERE id IN (
    SELECT employee_id
    FROM department_employee
    WHERE CURRENT_DATE BETWEEN from_date AND to_date AND department_id IN (
        SELECT department_id
        FROM department_employee
        GROUP BY department_id
        HAVING COUNT(employee_id) > 50
    )
);
   
--5.	Найти номера и имена служащих, получающих в настоящее время минимальную зарплату.

SELECT id, first_name, last_name
FROM employee
WHERE id IN (
    SELECT employee_id 
    FROM salary
    WHERE amount = (
        SELECT MIN(amount) 
        FROM salary
        WHERE CURRENT_DATE BETWEEN from_date AND to_date
    ) AND CURRENT_DATE BETWEEN from_date AND to_date
);
   
--6.	Найти номера и имена служащих, получающих в настоящее время зарплату, большую 90000.

SELECT id, first_name, last_name
FROM employee
WHERE id IN (
    SELECT employee_id
    FROM salary
    WHERE amount > 90000 AND CURRENT_DATE BETWEEN from_date AND to_date
);
   
--7.	Найти названия отделов, в которых в настоящее время имеется более одного менеджера.


SELECT dept_name
FROM department
WHERE id IN (
    SELECT department_id
    FROM department_manager
    WHERE CURRENT_DATE BETWEEN from_date AND to_date
    GROUP BY department_id
    HAVING COUNT(employee_id) > 1
);
   