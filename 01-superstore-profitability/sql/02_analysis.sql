-- Profitability analysis

-- 1. Revenue, profit and margin by category
-- Margin = total profit / total sales. Never average the row-level margins.
SELECT category,
       ROUND(SUM(sales), 0)  AS revenue,
       ROUND(SUM(profit), 0) AS profit,
       ROUND(100.0 * SUM(profit) / SUM(sales), 1) AS margin_pct
FROM orders
GROUP BY category
ORDER BY profit DESC;

-- 2. Same by sub-category. Look for the ones with negative profit.
SELECT category, sub_category,
       ROUND(SUM(sales), 0)  AS revenue,
       ROUND(SUM(profit), 0) AS profit,
       ROUND(100.0 * SUM(profit) / SUM(sales), 1) AS margin_pct
FROM orders
GROUP BY category, sub_category
ORDER BY profit ASC;

-- 3. By region
SELECT region,
       ROUND(SUM(sales), 0)  AS revenue,
       ROUND(SUM(profit), 0) AS profit,
       ROUND(100.0 * SUM(profit) / SUM(sales), 1) AS margin_pct
FROM orders
GROUP BY region
ORDER BY profit DESC;

-- 4. Margin by discount band (the key query for this project)
SELECT discount_band,
       COUNT(*) AS order_lines,
       ROUND(SUM(sales), 0)  AS revenue,
       ROUND(SUM(profit), 0) AS profit,
       ROUND(100.0 * SUM(profit) / SUM(sales), 1) AS margin_pct,
       ROUND(100.0 * AVG(CASE WHEN profit < 0 THEN 1.0 ELSE 0 END), 1) AS pct_lines_losing_money
FROM orders
GROUP BY discount_band
ORDER BY discount_band;

-- 5. Busy but poor: products in the top 20% for revenue
-- and the bottom 20% for margin
WITH p AS (
    SELECT product_name, sub_category,
           SUM(sales)  AS revenue,
           SUM(profit) AS profit,
           SUM(profit) * 1.0 / NULLIF(SUM(sales), 0) AS margin
    FROM orders
    GROUP BY product_name, sub_category
),
r AS (
    SELECT *,
           NTILE(5) OVER (ORDER BY revenue DESC) AS revenue_quintile,
           NTILE(5) OVER (ORDER BY margin ASC)   AS margin_quintile_low_first
    FROM p
)
SELECT product_name, sub_category,
       ROUND(revenue, 0) AS revenue,
       ROUND(profit, 0)  AS profit,
       ROUND(margin * 100, 1) AS margin_pct
FROM r
WHERE revenue_quintile = 1 AND margin_quintile_low_first = 1
ORDER BY profit ASC
LIMIT 15;

-- 6. Profit lost on heavily discounted lines (discount above 30%).
-- High estimate: what those lines would have earned at the company-wide margin
-- of lines discounted 20% or less.
WITH base AS (
    SELECT SUM(profit) * 1.0 / SUM(sales) AS low_disc_margin
    FROM orders WHERE discount <= 0.2
)
SELECT COUNT(*)                                     AS heavy_lines,
       ROUND(SUM(o.sales), 0)                       AS heavy_sales,
       ROUND(SUM(o.profit), 0)                      AS actual_profit,
       ROUND(SUM(o.sales) * b.low_disc_margin, 0)   AS profit_at_low_discount_margin,
       ROUND(SUM(o.sales) * b.low_disc_margin - SUM(o.profit), 0) AS estimated_leak_high
FROM orders o, base b
WHERE o.discount > 0.3;

-- Low estimate: same idea, but each line is compared with the low-discount margin
-- of its own sub-category, so a product mix of cheap-margin items isn't blamed on discounts.
WITH sub AS (
    SELECT sub_category, SUM(profit) * 1.0 / SUM(sales) AS low_disc_margin
    FROM orders WHERE discount <= 0.2
    GROUP BY sub_category
)
SELECT ROUND(SUM(o.sales * s.low_disc_margin) - SUM(o.profit), 0) AS estimated_leak_low
FROM orders o JOIN sub s USING (sub_category)
WHERE o.discount > 0.3;

-- 7. Revenue and profit by year, to test the "revenue up, profit not" claim
SELECT SUBSTR(order_date, 1, 4) AS year,
       ROUND(SUM(sales), 0)  AS revenue,
       ROUND(SUM(profit), 0) AS profit,
       ROUND(100.0 * SUM(profit) / SUM(sales), 1) AS margin_pct
FROM orders
GROUP BY year
ORDER BY year;

-- 8. Where heavy discounting happens, by sub-category
SELECT sub_category,
       COUNT(*) AS heavy_lines,
       ROUND(SUM(profit), 0) AS profit_on_heavy_lines
FROM orders
WHERE discount > 0.3
GROUP BY sub_category
ORDER BY profit_on_heavy_lines ASC;
