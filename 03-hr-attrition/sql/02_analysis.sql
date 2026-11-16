-- Attrition analysis
-- attrition_pct = leavers / employees in the group.
-- Always look at the employees column next to the rate. A rate from
-- 10 people is not worth reporting on its own.

-- 1. Overall
SELECT COUNT(*) AS employees,
       SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) AS leavers,
       ROUND(100.0 * AVG(CASE WHEN attrition = 'Yes' THEN 1.0 ELSE 0 END), 1) AS attrition_pct
FROM employees;

-- 2. By department
SELECT department,
       COUNT(*) AS employees,
       SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) AS leavers,
       ROUND(100.0 * AVG(CASE WHEN attrition = 'Yes' THEN 1.0 ELSE 0 END), 1) AS attrition_pct
FROM employees
GROUP BY department
ORDER BY attrition_pct DESC;

-- 3. By job role, ignoring roles with fewer than 20 people
SELECT job_role,
       COUNT(*) AS employees,
       SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) AS leavers,
       ROUND(100.0 * AVG(CASE WHEN attrition = 'Yes' THEN 1.0 ELSE 0 END), 1) AS attrition_pct
FROM employees
GROUP BY job_role
HAVING COUNT(*) >= 20
ORDER BY attrition_pct DESC;

-- 4. Overtime
SELECT overtime,
       COUNT(*) AS employees,
       ROUND(100.0 * AVG(CASE WHEN attrition = 'Yes' THEN 1.0 ELSE 0 END), 1) AS attrition_pct
FROM employees
GROUP BY overtime;

-- 5. Tenure
SELECT tenure_band,
       COUNT(*) AS employees,
       ROUND(100.0 * AVG(CASE WHEN attrition = 'Yes' THEN 1.0 ELSE 0 END), 1) AS attrition_pct
FROM employees
GROUP BY tenure_band
ORDER BY MIN(years_at_company);

-- 6. Income band
SELECT income_band,
       COUNT(*) AS employees,
       ROUND(100.0 * AVG(CASE WHEN attrition = 'Yes' THEN 1.0 ELSE 0 END), 1) AS attrition_pct
FROM employees
GROUP BY income_band
ORDER BY income_band;

-- 7. Overtime and tenure together: does overtime matter more for new joiners?
SELECT overtime, tenure_band,
       COUNT(*) AS employees,
       ROUND(100.0 * AVG(CASE WHEN attrition = 'Yes' THEN 1.0 ELSE 0 END), 1) AS attrition_pct
FROM employees
GROUP BY overtime, tenure_band
HAVING COUNT(*) >= 20
ORDER BY overtime, MIN(years_at_company);

-- 8. Lift: how many times the company average is each department?
WITH overall AS (
    SELECT AVG(CASE WHEN attrition = 'Yes' THEN 1.0 ELSE 0 END) AS rate FROM employees
)
SELECT e.department,
       ROUND(AVG(CASE WHEN e.attrition = 'Yes' THEN 1.0 ELSE 0 END) / o.rate, 2) AS lift
FROM employees e, overall o
GROUP BY e.department
ORDER BY lift DESC;
