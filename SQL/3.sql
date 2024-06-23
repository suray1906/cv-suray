set search_path to employees, public;


select * from certificates join department_employee using(employee_id)

set search_path to employees, public;
--alter table certificates add column 
--cert_type cert_type not NULL default 'U'; 
--1.	Найти номера, имена, фамилии служащих, поступивших на работу после 
--20 апреля 1999 г., и номера отделов, в которых в настоящее время они работают.
set search_path to employees, public;
select 
	e.id,
	e.first_name,
	e.last_name,
	de.department_id

from
employee e join
department_employee de on e.id = de.employee_id
where current_date between from_date and to_date
and e.hire_date > '1999-04-20';

--2.	Найти номера, имена, фамилии служащих, поступивших на работу после 20 апреля 1999 г.,
-- размер их текущей зарплаты и номера отделов, в которых в настоящее время они работают.

SET search_path TO employees, public;

SELECT 
    e.id ,
    e.first_name,
    e.last_name,
    s.amount,
    de.department_id
FROM employee e 
JOIN department_employee de ON e.id = de.employee_id
JOIN salary s ON e.id = s.employee_id
WHERE e.hire_date > '1999-04-20'
AND current_date BETWEEN de.from_date AND de.to_date
AND current_date BETWEEN s.from_date AND s.to_date;

--3.	Найти номера, имена, фамилии служащих, поступивших на работу после 20 апреля 1999 г.,
-- размер их текущей зарплаты, названия текущих должностей и номера отделов, в которых в настоящее время они работают.
SET search_path TO employees, public;

SELECT 
    e.id,
    e.first_name,
    e.last_name,
    s.amount,
    t.title,
    de.department_id
FROM employee e 
JOIN department_employee de ON e.id = de.employee_id
JOIN salary s ON e.id = s.employee_id
JOIN title t ON e.id = t.employee_id
WHERE e.hire_date > '1999-04-20'
AND current_date BETWEEN de.from_date AND de.to_date
AND current_date BETWEEN s.from_date AND s.to_date
AND current_date BETWEEN t.from_date AND COALESCE(t.to_date, current_date);


--4.	Найти номера, имена, фамилии служащих, поступивших на работу после 20 апреля 1999 г.
-- и получающих в настоящее время зарплату, выше средней по всей компании, а также номера отделов, в которых в настоящее время они работают.


SET search_path TO employees, public;

SELECT 
    id,
    first_name,
    last_name,
    department_id
FROM employee e 
JOIN department_employee de ON e.id = de.employee_id
JOIN salary s ON e.id = s.employee_id
WHERE amount > (select AVG(amount) from salary where current_date BETWEEN from_date AND to_date)
AND current_date BETWEEN de.from_date AND de.to_date
AND current_date BETWEEN s.from_date AND s.to_date
AND e.hire_date > '1999-04-20';

--5.	Найти номера, имена, фамилии служащих, которые в настоящее время являются менеджерами отделов, в которых они работают.
SET search_path TO employees, public;
SELECT     e.id,
    e.first_name,    e.last_name,
    dm.department_id
FROM employee e 
JOIN department_manager dm ON e.id = dm.employee_id
JOIN department_employee de ON e.id = de.employee_id AND dm.department_id = de.department_id
WHERE current_date BETWEEN dm.from_date AND dm.to_date
AND current_date BETWEEN de.from_date AND de.to_date;


--6.	Найти номера, имена, фамилии служащих, которые являлись или являются менеджерами отделов.
SET search_path TO employees, public;

SELECT DISTINCT
    e.id,
    e.first_name,
    e.last_name
FROM employee e 
JOIN department_manager dm ON e.id = dm.employee_id;

--7.	Найти номера, имена, фамилии служащих, которые за время работы сменили больше всего должностей.
select id, first_name, last_name from employee e join (
select employee_id from title group by employee_id having count(*) =
(select max(c) from (select count(*) as c from title group by employee_id) as foo)) as tmp
on e.id = tmp.employee_id;

--8.	Выдать номера отделов и размеры максимальной, минимальной и средней зарплаты
-- служащих этих отделов на 20 апреля 1999 г.
SELECT department_id, min(amount), max(amount) FROM department_employee de join salary s using(employee_id)
where '1999-04-20' between de.from_date and de.to_date
and '1999-04-20' between s.from_date and s.to_date
group by department_id;
--9.	Выдать номера отделов и название должностей, занимаемых служащими этих отделов в настоящее время.
SELECT department_id, title FROM department_employee de join title s using(employee_id)
where current_date between de.from_date and de.to_date
and current_date between s.from_date and s.to_date
group by department_id, title

--10.	Найти номера, имена, фамилии служащих, получающих в настоящее время зарплату, 
--не меньшую зарплаты хотя бы одного менеджера своего текущего отдела.

SELECT id, first_name, last_name 
FROM employee e 
JOIN department_employee de ON e.id = de.employee_id
JOIN salary s USING(employee_id)
JOIN (
    SELECT department_id, MIN(amount) as manager_amount 
    FROM department_manager dm 
    JOIN salary s USING(employee_id)
    WHERE current_date BETWEEN dm.from_date AND dm.to_date
    AND current_date BETWEEN s.from_date AND s.to_date
    GROUP BY department_id
) AS tmp USING (department_id)
WHERE current_date BETWEEN de.from_date AND de.to_date
AND current_date BETWEEN s.from_date AND s.to_date
AND amount >= manager_amount;






select id, first_name, last_name from 
employee e join department_employee de on e.id = de.employee_id
join salary s using(employee_id)

join (select department_id, min(amount) as manager_amount FROM department_manager dm join salary s using(employee_id)
where '1999-04-20' between dm.from_date and dm.to_date
and '1999-04-20' between s.from_date and s.to_date
group by department_id) as tmp using (department_id)

where current_date between de.from_date and de.to_date
and current_date between s.from_date and s.to_date
and amount >= manager_amount;

--11.	Найти номера, номера отделов, имена, фамилии служащих, получающих в настоящее время зарплату, минимальную в своем отделе.

SET search_path TO employees, public;

SELECT 
    e.id,
    swm.department_id,
    e.first_name,
    e.last_name
FROM employee e
JOIN (
    SELECT 
        s.employee_id,
        de.department_id,
        s.amount,
        MIN(s.amount) OVER(PARTITION BY de.department_id) as min_amount
    FROM salary s
    JOIN department_employee de ON s.employee_id = de.employee_id
    WHERE current_date BETWEEN s.from_date AND s.to_date
    AND current_date BETWEEN de.from_date AND de.to_date
) AS swm ON e.id = swm.employee_id
WHERE swm.amount = swm.min_amount;
--12.	Найти номера, имена, фамилии служащих, получающих в настоящее время зарплату, не меньшую зарплаты хотя бы одного служащего, являющегося в настоящее время менеджером какого-либо отдела.
SET search_path TO employees, public;

SELECT 
    e.id,
    e.first_name,
    e.last_name
FROM employee e
JOIN salary s ON e.id = s.employee_id
WHERE current_date BETWEEN s.from_date AND s.to_date
AND s.amount >= (
    SELECT MIN(s.amount)
    FROM salary s
    JOIN department_manager dm ON s.employee_id = dm.employee_id
    WHERE current_date BETWEEN s.from_date AND s.to_date
    AND current_date BETWEEN dm.from_date AND dm.to_date
);

--13.	Найти номера, имена, фамилии служащих, работающих в настоящее время в отделах, менеджеры которых в настоящее время получают наименьшую среди всех менеджеров зарплату.
SET search_path TO employees, public;

SELECT 
    e.id,
    e.first_name,
    e.last_name
FROM employee e
JOIN department_employee de ON e.id = de.employee_id
WHERE current_date BETWEEN de.from_date AND de.to_date
AND de.department_id IN (
    SELECT dm.department_id
    FROM department_manager dm
    JOIN salary s ON dm.employee_id = s.employee_id
    WHERE current_date BETWEEN dm.from_date AND dm.to_date
    AND current_date BETWEEN s.from_date AND s.to_date
    AND s.amount = (
        SELECT MIN(s.amount)
        FROM department_manager dm
        JOIN salary s ON dm.employee_id = s.employee_id
        WHERE current_date BETWEEN dm.from_date AND dm.to_date
        AND current_date BETWEEN s.from_date AND s.to_date
    )
);


--14.	Найти названия отделов, номера, имена и фамилии их менеджеров для отделов, служащие которых в настоящее время получают минимальную среди всех отделов среднюю зарплату.
SET search_path TO employees, public;

SELECT 
    d.dept_name,
    dm.employee_id as manager_id,
    e.first_name,
    e.last_name
FROM department_manager dm
JOIN employee e ON dm.employee_id = e.id
JOIN department d ON dm.department_id = d.id
WHERE current_date BETWEEN dm.from_date AND dm.to_date
AND dm.department_id IN (
    SELECT department_id
    FROM (
        SELECT 
            de.department_id,
            AVG(s.amount) as avg_salary
        FROM department_employee de
        JOIN salary s ON de.employee_id = s.employee_id
        WHERE current_date BETWEEN de.from_date AND de.to_date
        AND current_date BETWEEN s.from_date AND s.to_date
        GROUP BY de.department_id
        HAVING AVG(s.amount) = (
            SELECT MIN(avg_salary)
            FROM (
                SELECT 
                    department_id,
                    AVG(amount) as avg_salary
                FROM department_employee de_inner
                JOIN salary s_inner ON de_inner.employee_id = s_inner.employee_id
                WHERE current_date BETWEEN de_inner.from_date AND de_inner.to_date
                AND current_date BETWEEN s_inner.from_date AND s_inner.to_date
                GROUP BY de_inner.department_id
            ) AS inner_subquery
        )
    ) AS outer_subquery
);

--15.	Найти минимальную и максимальную зарплату старшего инженера за все время.
SET search_path TO employees, public;

SELECT 
    MIN(s.amount) as min_salary,
    MAX(s.amount) as max_salary
FROM salary s
JOIN title t ON s.employee_id = t.employee_id
WHERE t.title = 'Senior Engineer';

--16.	Найти текущую минимальную и максимальную зарплату старшего инженера в каждом отделе, в котором работают служащие в такой должности.
SET search_path TO employees, public;

SELECT 
    de.department_id,
    MIN(s.amount) as min_salary,
    MAX(s.amount) as max_salary
FROM salary s
JOIN title t ON s.employee_id = t.employee_id
JOIN department_employee de ON s.employee_id = de.employee_id
WHERE t.title = 'Senior Engineer'
AND current_date BETWEEN s.from_date AND s.to_date
AND current_date BETWEEN t.from_date AND t.to_date
AND current_date BETWEEN de.from_date AND de.to_date
GROUP BY de.department_id;


SET search_path TO employees, public;

SELECT 
    t.title,
    AVG(s.amount) as avg_salary
FROM salary s
JOIN title t ON s.employee_id = t.employee_id
WHERE current_date BETWEEN s.from_date AND s.to_date
AND current_date BETWEEN t.from_date AND t.to_date
GROUP BY t.title
HAVING AVG(s.amount) = (
    SELECT MAX(avg_salary)
    FROM (
        SELECT 
            title,
            AVG(amount) as avg_salary
        FROM salary s_inner
        JOIN title t_inner ON s_inner.employee_id = t_inner.employee_id
        WHERE current_date BETWEEN s_inner.from_date AND s_inner.to_date
        AND current_date BETWEEN t_inner.from_date AND t_inner.to_date
        GROUP BY title
    ) AS inner_subquery
);


--18.	Найти номера, имена, фамилии служащих, работающих в настоящее время в должности инженера и получающих зарплату, большую средней текущей зарплаты инженера.
SET search_path TO employees, public;

SELECT 
    e.id,
    e.first_name,
    e.last_name
FROM employee e
JOIN salary s ON e.id = s.employee_id
JOIN title t ON e.id = t.employee_id
WHERE t.title = 'Engineer'
AND current_date BETWEEN s.from_date AND s.to_date
AND current_date BETWEEN t.from_date AND t.to_date
AND s.amount > (
    SELECT AVG(s_inner.amount)
    FROM salary s_inner
    JOIN title t_inner ON s_inner.employee_id = t_inner.employee_id
    WHERE t_inner.title = 'Engineer'
    AND current_date BETWEEN s_inner.from_date AND s_inner.to_date
    AND current_date BETWEEN t_inner.from_date AND t_inner.to_date
);


--19.	Найти номера, имена, фамилии служащих, работающих в настоящее время в должности инженера и получающих зарплату, большую средней текущей зарплаты старшего инженера.
SET search_path TO employees, public;

SELECT 
    e.id,
    e.first_name,
    e.last_name
FROM employee e
JOIN salary s ON e.id = s.employee_id
JOIN title t ON e.id = t.employee_id
WHERE t.title = 'Engineer'
AND current_date BETWEEN s.from_date AND s.to_date
AND current_date BETWEEN t.from_date AND t.to_date
AND s.amount > (
    SELECT AVG(s_inner.amount)
    FROM salary s_inner
    JOIN title t_inner ON s_inner.employee_id = t_inner.employee_id
    WHERE t_inner.title = 'Senior Engineer'
    AND current_date BETWEEN s_inner.from_date AND s_inner.to_date
    AND current_date BETWEEN t_inner.from_date AND t_inner.to_date
);


--20.	Найти номера, имена, фамилии служащих, работающих в настоящее время в должности инженера и получающих зарплату, большую средней текущей зарплаты менеджера отдела.


SET search_path TO employees, public;

SELECT 
    e.id,
    e.first_name,
    e.last_name
FROM employee e
JOIN salary s ON e.id = s.employee_id
JOIN title t ON e.id = t.employee_id
WHERE t.title = 'Engineer'
AND current_date BETWEEN s.from_date AND s.to_date
AND current_date BETWEEN t.from_date AND t.to_date
AND s.amount > (
    SELECT AVG(s_inner.amount)
    FROM salary s_inner
    JOIN department_manager dm ON s_inner.employee_id = dm.employee_id
    WHERE current_date BETWEEN s_inner.from_date AND s_inner.to_date
    AND current_date BETWEEN dm.from_date AND dm.to_date
);


--21.	Найти номера, имена, фамилии служащих, являющихся в настоящее время в менеджерами отделов и получающих зарплату, большую средней текущей зарплаты менеджера.
--22.	Найти номера, имена, фамилии служащих, работающих в настоящее время в должности инженера и получающих зарплату, большую средней текущей зарплаты инженера.
--23.	Найти номера и названия отделов, в которых в настоящее время работает наибольшее число служащих в должности «инженер».
--24.	Найти номера и названия отделов, в которых в настоящее время работает больше инженеров, чем старших инженеров.
--25.	Найти номера и названия отделов, в которых в настоящее время не работает ни один служащий в должности «Technique Leader».
--26.	Найти номера и названия отделов, в которых в настоящее время не работает ни один служащий, когда-либо занимавший должность «Technique Leader».
--27.	Найти номера, имена, фамилии служащих, которые в настоящее время являются менеджерами отделов, но когда-либо занимали должность инженера.
--28.	Для каждого отдела найти их названия, все должности, которые в настоящее время занимают служащие этого отдела, и для каждой должности найти число служащих, занимающих в настоящее время эту должность.
--29.	Найти отделы, в которых в настоящее время служащие занимают все возможные должности.
--30.	Найти номера, имена, фамилии служащих, которые в настоящее время являются менеджерами отделов и получают зарплату, меньшую текущей максимальной зарплаты служащих своего отдела.


### Задача 21
Найти менеджеров отделов с зарплатой выше средней для менеджеров:

```sql
SELECT e.id, e.first_name, e.last_name
FROM employee e
JOIN department_manager dm ON e.id = dm.employee_id
JOIN salary s ON e.id = s.employee_id
WHERE CURRENT_DATE BETWEEN dm.from_date AND dm.to_date
AND CURRENT_DATE BETWEEN s.from_date AND s.to_date
AND s.amount > (
    SELECT AVG(s_inner.amount)
    FROM department_manager dm_inner
    JOIN salary s_inner ON dm_inner.employee_id = s_inner.employee_id
    WHERE CURRENT_DATE BETWEEN dm_inner.from_date AND dm_inner.to_date
    AND CURRENT_DATE BETWEEN s_inner.from_date AND s_inner.to_date
);
```

### Задача 22
Найти инженеров с зарплатой выше средней для инженеров:

```sql
SELECT e.id, e.first_name, e.last_name
FROM employee e
JOIN salary s ON e.id = s.employee_id
JOIN title t ON e.id = t.employee_id
WHERE t.title = 'Engineer'
AND CURRENT_DATE BETWEEN s.from_date AND s.to_date
AND s.amount > (
    SELECT AVG(s_inner.amount)
    FROM salary s_inner
    JOIN title t_inner ON s_inner.employee_id = t_inner.employee_id
    WHERE t_inner.title = 'Engineer'
    AND CURRENT_DATE BETWEEN s_inner.from_date AND s_inner.to_date
);
```

### Задача 23
Найти отделы с наибольшим числом инженеров:

```sql
SELECT de.department_id, COUNT(*) as num_engineers
FROM department_employee de
JOIN title t ON de.employee_id = t.employee_id
WHERE t.title = 'Engineer'
AND CURRENT_DATE BETWEEN de.from_date AND de.to_date
GROUP BY de.department_id
ORDER BY num_engineers DESC
LIMIT 1;
```

### Задача 24
Найти отделы с большим числом инженеров, чем старших инженеров:

```sql
SELECT de.department_id
FROM department_employee de
JOIN title t ON de.employee_id = t.employee_id
WHERE CURRENT_DATE BETWEEN de.from_date AND de.to_date
GROUP BY de.department_id
HAVING COUNT(CASE WHEN t.title = 'Engineer' THEN 1 END) > COUNT(CASE WHEN t.title = 'Senior Engineer' THEN 1 END);
```

### Задача 25
Найти отделы без «Technique Leader»:

```sql
SELECT d.dept_name, de.department_id
FROM departments d
LEFT JOIN (
    SELECT de.department_id
    FROM department_employee de
    JOIN title t ON de.employee_id = t.employee_id
    WHERE t.title = 'Technique Leader'
    AND CURRENT_DATE BETWEEN de.from_date AND de.to_date
    GROUP BY de.department_id
) as t_leader ON d.dept_no = t_leader.department_id
WHERE t_leader.department_id IS NULL;
```

### Задача 26
Отделы без бывших «Technique Leader»:

```sql
SELECT d.dept_name, de.department_id
FROM departments d
LEFT JOIN (
    SELECT de.department_id
    FROM department_employee de
    JOIN title t ON de.employee_id = t.employee_id
    WHERE t.title = 'Technique Leader'
    GROUP BY de.department_id
) as ex_t_leader ON d.dept_no = ex_t_leader.department_id
WHERE ex_t_leader.department_id IS NULL;
```

### Задача 27
Найти менеджеров, бывших инженерами:

```sql
SELECT e.id, e.first_name, e.last_name
FROM employee e
JOIN department_manager dm ON e.id = dm.employee_id
WHERE CURRENT_DATE BETWEEN dm.from_date AND dm.to_date
AND EXISTS (
    SELECT 1
    FROM title t
    WHERE t.employee_id = e.id
    AND t.title = 'Engineer'
);
```

### Задача 28
Должности и их количество в каждом отделе:

```sql
SELECT de.department_id, t.title, COUNT(*) as num_positions
FROM department_employee de
JOIN title t ON de.employee_id = t.employee_id
WHERE CURRENT_DATE BETWEEN de.from_date AND de.to_date
GROUP BY de.department_id, t.title;
```

### Задача 29
Отделы с всеми возможными должностями:

```sql
SET search_path TO employees, public;

WITH all_positions AS (
    SELECT DISTINCT title FROM title
),
department_positions AS (
    SELECT 
        de.department_id,
        t.title
    FROM department_employee de
    JOIN title t ON de.employee_id = t.employee_id
    WHERE CURRENT_DATE BETWEEN de.from_date AND de.to_date
    GROUP BY de.department_id, t.title
),
departments_with_all_positions AS (
    SELECT 
        dp.department_id
    FROM department_positions dp
    GROUP BY dp.department_id
    HAVING COUNT(DISTINCT dp.title) = (SELECT COUNT(*) FROM all_positions)
)
SELECT 
    d.dept_name,
    daw.department_id
FROM departments_with_all_positions daw
JOIN departments d ON daw.department_id = d.dept_no;

```

### Задача 30
Менеджеры с зарплатой меньше максимальной в их отделе:

```sql
SELECT e.id, e.first_name, e.last_name
FROM employee e
JOIN department_manager dm ON e.id = dm.employee_id
JOIN salary s ON e.id = s.employee_id
JOIN (
    SELECT de.department_id, MAX(s.amount) as max_salary
    FROM department_employee de
    JOIN salary s ON de.employee_id = s.employee_id
    WHERE CURRENT_DATE BETWEEN de.from_date AND de.to_date
    AND CURRENT_DATE BETWEEN s.from_date AND s.to_date
    GROUP BY de.department_id
) as max_salaries ON dm.department_id = max_salaries.department_id
WHERE CURRENT_DATE BETWEEN s.from_date AND s.to_date
AND s.amount < max_salaries.max_salary;
```

