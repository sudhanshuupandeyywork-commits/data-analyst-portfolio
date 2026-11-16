"""
Builds the practice ledger for the budget variance project.

The data is simulated. Real company ledgers are confidential, so I made one
with a fixed random seed. Two problems are planted on purpose so there is
something to find:

  1. Engineering / Contractors drifts upward by 1.5% of budget each month
  2. Travel spikes by 35% in March and September in every department

Run from the project root:  python scripts/make_ledger.py
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(21)

# annual budget per department, in thousands
depts = {"Sales": 900, "Marketing": 600, "Engineering": 1500,
         "Operations": 800, "HR": 250, "Finance": 300}

# share of each department's budget that goes to each account
shares = {"Salaries": .55, "Software": .12, "Travel": .06,
          "Contractors": .12, "Marketing Spend": .05, "Facilities": .10}

rows = []
for m in range(1, 13):
    for dept, annual_k in depts.items():
        for acc, share in shares.items():
            budget = annual_k * 1000 * share / 12
            drift = 1 + (0.015 * m if (dept == "Engineering" and acc == "Contractors") else 0)
            spike = 1.35 if (acc == "Travel" and m in (3, 9)) else 1.0
            noise = rng.normal(1.0, 0.07)
            actual = budget * drift * spike * noise
            rows.append((f"2026-{m:02d}-01", dept, acc, round(budget), round(actual)))

ledger = pd.DataFrame(rows, columns=["month", "department", "account", "budget", "actual"])
ledger.to_csv("data/raw/ledger.csv", index=False)
print(f"Wrote {len(ledger)} rows")
print("Total budget:", f"{ledger['budget'].sum():,}")
print("Total actual:", f"{ledger['actual'].sum():,}")
