-- Load the Superstore CSV and clean it.
-- Column names below match the common Kaggle "Sample - Superstore" file.
-- Your copy may differ (for example "Order ID" vs order_id). Check with:
--   PRAGMA table_info(orders_raw);
--
-- Loading: run  python scripts/load_db.py  first. It reads the CSV (latin-1 encoding),
-- renames the columns to snake_case and creates data/superstore.db with a table orders_raw.
-- Then open that database in DB Browser for SQLite or the sqlite3 shell and run this file.

-- Step 1: row count. Write this number in your cleaning log.
SELECT COUNT(*) AS raw_rows FROM orders_raw;

-- Step 2: duplicate check. Same order, product, sales and quantity on more than one row.
SELECT order_id, product_id, COUNT(*) AS copies
FROM orders_raw
GROUP BY order_id, product_id, sales, quantity
HAVING COUNT(*) > 1;
-- On the standard file this returns one pair (US-2014-150119, a Hon chair). I keep
-- the first row of each pair and drop the second, and log it as 1 row removed.

-- Step 3: build the working table with proper types and discount bands.
-- scripts/load_db.py already turned the month/day/year dates into YYYY-MM-DD.
DROP TABLE IF EXISTS orders;
CREATE TABLE orders AS
WITH numbered AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY order_id, product_id, sales, quantity, discount, profit
               ORDER BY row_id
           ) AS rn
    FROM orders_raw
)
SELECT
    order_id,
    order_date,
    ship_mode,
    segment,
    region,
    state,
    category,
    sub_category,
    product_name,
    CAST(sales AS REAL)    AS sales,
    CAST(quantity AS INT)  AS quantity,
    CAST(discount AS REAL) AS discount,
    CAST(profit AS REAL)   AS profit,
    CASE WHEN CAST(discount AS REAL) = 0    THEN 'a. No discount'
         WHEN CAST(discount AS REAL) <= 0.2 THEN 'b. Up to 20%'
         WHEN CAST(discount AS REAL) <= 0.4 THEN 'c. 20 to 40%'
         ELSE 'd. Above 40%' END AS discount_band
FROM numbered
WHERE rn = 1;

-- Step 4: confirm nothing was lost, and check the totals
SELECT COUNT(*) AS clean_rows,
       ROUND(SUM(sales), 0)  AS total_sales,
       ROUND(SUM(profit), 0) AS total_profit,
       ROUND(100.0 * SUM(profit) / SUM(sales), 1) AS margin_pct
FROM orders;

-- Do NOT remove negative profit rows. Those are the story.
