-- IBM HR Analytics Employee Attrition dataset.
-- File name on Kaggle: WA_Fn-UseC_-HR-Employee-Attrition.csv
--
-- Import into a table called hr_raw:
--   .mode csv
--   .import --skip 1 data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv hr_raw
-- Check the column names with PRAGMA table_info(hr_raw); the first column
-- sometimes has a stray byte-order mark in its name.

SELECT COUNT(*) AS raw_rows FROM hr_raw;

-- Three columns hold the same value on every row, so they carry no
-- information (EmployeeCount, StandardHours, Over18). Leave them out.
DROP TABLE IF EXISTS employees;
CREATE TABLE employees AS
SELECT
    CAST(Age AS INT)               AS age,
    Attrition                      AS attrition,
    BusinessTravel                 AS business_travel,
    Department                     AS department,
    CAST(DistanceFromHome AS INT)  AS distance_from_home,
    CAST(Education AS INT)         AS education,
    Gender                         AS gender,
    JobRole                        AS job_role,
    CAST(JobLevel AS INT)          AS job_level,
    CAST(JobSatisfaction AS INT)   AS job_satisfaction,
    MaritalStatus                  AS marital_status,
    CAST(MonthlyIncome AS INT)     AS monthly_income,
    OverTime                       AS overtime,
    CAST(WorkLifeBalance AS INT)   AS work_life_balance,
    CAST(YearsAtCompany AS INT)    AS years_at_company,
    CAST(YearsSinceLastPromotion AS INT) AS years_since_promotion,
    CASE WHEN CAST(YearsAtCompany AS INT) <= 1  THEN '0 to 1'
         WHEN CAST(YearsAtCompany AS INT) <= 3  THEN '2 to 3'
         WHEN CAST(YearsAtCompany AS INT) <= 5  THEN '4 to 5'
         WHEN CAST(YearsAtCompany AS INT) <= 10 THEN '6 to 10'
         ELSE '11 plus' END       AS tenure_band,
    CASE WHEN CAST(MonthlyIncome AS INT) < 3000 THEN 'a. Under 3k'
         WHEN CAST(MonthlyIncome AS INT) < 6000 THEN 'b. 3k to 6k'
         WHEN CAST(MonthlyIncome AS INT) < 10000 THEN 'c. 6k to 10k'
         ELSE 'd. 10k plus' END   AS income_band
FROM hr_raw;

SELECT COUNT(*) AS clean_rows,
       SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) AS leavers,
       ROUND(100.0 * AVG(CASE WHEN attrition = 'Yes' THEN 1.0 ELSE 0 END), 1) AS attrition_pct
FROM employees;
