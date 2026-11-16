-- Which lines are over budget by more than 5% three months running?
-- One bad month is noise. Three in a row is a pattern worth a conversation.

WITH monthly AS (
    SELECT month, department, account, budget, actual,
           (actual - budget) * 1.0 / NULLIF(budget, 0) AS var_pct
    FROM ledger
),
flagged AS (
    SELECT *,
           CASE WHEN var_pct > 0.05 THEN 1 ELSE 0 END AS over_flag
    FROM monthly
),
streaks AS (
    SELECT *,
           SUM(over_flag) OVER (
               PARTITION BY department, account
               ORDER BY month
               ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
           ) AS over_last3
    FROM flagged
)
SELECT department, account,
       MIN(month) AS first_flagged_month,
       COUNT(*)   AS months_in_streak,
       ROUND(AVG(var_pct) * 100, 1) AS avg_var_pct
FROM streaks
WHERE over_last3 = 3
GROUP BY department, account
ORDER BY months_in_streak DESC;
