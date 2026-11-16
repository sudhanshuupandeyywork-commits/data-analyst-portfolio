-- Load the ledger CSV into a table.
-- SQLite: run these in the sqlite3 shell, or import the CSV through DB Browser.
--   .mode csv
--   .import --skip 1 data/raw/ledger.csv ledger_raw

CREATE TABLE IF NOT EXISTS ledger (
    month       TEXT,     -- first day of the month, YYYY-MM-DD
    department  TEXT,
    account     TEXT,
    budget      REAL,
    actual      REAL
);

-- sanity check: 12 months x 6 departments x 6 accounts = 432 rows
SELECT COUNT(*) AS row_count FROM ledger;

-- totals should tie back to the CSV
SELECT SUM(budget) AS total_budget, SUM(actual) AS total_actual FROM ledger;
