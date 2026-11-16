-- Budget variance analysis
-- Sign convention: variance = actual - budget.
-- For costs, positive = overspend (unfavourable).

-- 1. Overall position
SELECT SUM(budget)                                   AS budget,
       SUM(actual)                                   AS actual,
       SUM(actual) - SUM(budget)                     AS variance,
       ROUND(100.0 * (SUM(actual) - SUM(budget)) / SUM(budget), 2) AS variance_pct
FROM ledger;

-- 2. Variance by department
SELECT department,
       SUM(budget) AS budget,
       SUM(actual) AS actual,
       SUM(actual) - SUM(budget) AS variance,
       ROUND(100.0 * (SUM(actual) - SUM(budget)) / SUM(budget), 2) AS variance_pct
FROM ledger
GROUP BY department
ORDER BY variance DESC;

-- 3. Variance by account
SELECT account,
       SUM(budget) AS budget,
       SUM(actual) AS actual,
       SUM(actual) - SUM(budget) AS variance,
       ROUND(100.0 * (SUM(actual) - SUM(budget)) / SUM(budget), 2) AS variance_pct
FROM ledger
GROUP BY account
ORDER BY variance DESC;

-- 4. Ten biggest overspent department + account lines
SELECT department, account,
       SUM(actual) - SUM(budget) AS variance,
       ROUND(100.0 * (SUM(actual) - SUM(budget)) / SUM(budget), 1) AS variance_pct
FROM ledger
GROUP BY department, account
ORDER BY variance DESC
LIMIT 10;

-- 5. Monthly trend
SELECT month,
       SUM(budget) AS budget,
       SUM(actual) AS actual,
       ROUND(100.0 * (SUM(actual) - SUM(budget)) / SUM(budget), 2) AS variance_pct
FROM ledger
GROUP BY month
ORDER BY month;
