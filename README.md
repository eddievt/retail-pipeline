# Retail Orders Data Pipeline

## 1. Solution overview and technology

A single-command pipeline that turns three raw source files (orders, customers, products) into a clean, reporting-ready dataset. It profiles the raw data, cleans and standardizes it, joins the tables, runs automated data quality (DQ) checks, and answers the required business questions.

- **Python + pandas:** loading, profiling, cleaning, and DQ checks. Row-level rules are easy to read and unit test.
- **SQLite + SQL scripts (`sql/`):** the join and the business questions. SQLite is built into Python (nothing extra to install) and runs in memory, so every run starts fresh. The pipeline runs the SQL files automatically.

**Principle:** fix only what has one obvious correct answer; flag everything else with a reason; never drop rows silently; reconcile at the end.

```
data/*.csv → load as text → profile → clean & standardize → remove exact duplicates
           → LEFT JOIN in SQL → 9 DQ checks → passed rows → clean_orders.csv
                                            → failed rows → dq_report.csv
           → reconciliation (input = clean + failed + duplicates removed)
           → SQL business questions → analysis_results.csv
```

## 2. Dataset source and license

- **Source:** UCI Machine Learning Repository, *Online Retail II*: https://archive.ics.uci.edu/dataset/502/online+retail+ii
- **License:** Creative Commons Attribution 4.0 (CC BY 4.0)
- **Content:** 1,067,371 real transactions from a UK online gift retailer, Dec 2009 to Dec 2011. Prices are in GBP.

The raw file (43 MB) is not included. The three files in `data/` were derived from it as described below.

## 3. Dataset preparation and introduced data issues

`scripts/prepare_data.py` was run once to create `data/`. It uses fixed random seeds, so it produces identical files every run (verified by file hash). The pipeline does not run it.

**Preparation**
1. Combined both Excel sheets into one table (1,067,371 rows, matching UCI's published count).
2. Kept product codes starting with a digit, which excludes postage, fees, and discounts (6,093 rows).
3. Kept Sep 1 to Nov 30, 2011, then sampled 150 customers (seed 42) plus 100 orders with no customer ID.
4. `order_id` = invoice number + line number, assigned to unique rows so exact duplicates share an ID.
5. **Derived fields:** product name and price = most common value per product; category = keyword rules on the name; country = each customer's most common country; name = `Customer <id>`; email = `customer<id>@example.com` (reserved example domain).

**Result:** `orders.csv` 8,169 rows, `customers.csv` 153 rows, `products.csv` 1,796 rows.

**Real issues already in the source:** 100 missing customer IDs, 113 exact duplicate orders, 140 zero or negative quantities (cancellations), 457 product names with extra spaces, a product with no name and a zero price (`21395`), and one product under two IDs differing only by case (`82494L` / `82494l`).

**Introduced issues** (exact IDs in `docs/injected_issues.csv`; the pipeline never reads this file):

| Table | Issues introduced |
|---|---|
| orders | 6 invalid, missing, or future dates; 5 unknown customer IDs; 5 unknown product IDs; 5 product IDs with spaces or lowercase |
| products | 2 zero prices, 1 negative, 1 missing; 3 lowercase names; 3 categories with spaces or lowercase; 2 exact duplicates |
| customers | 3 inconsistent country spellings (`UK`, `united kingdom`, padded); 1 missing country; 2 uppercase names; 2 missing emails; 1 email without `@`; 1 duplicate differing only in casing; 2 exact duplicates |

## 4. Assumptions and record-handling decisions

**Loading and cleaning**
- All columns are loaded as text, so bad values are recorded rather than crashing the load or being silently converted.
- Text is trimmed and repeated spaces collapsed. IDs and product names are uppercased, names and categories title-cased, emails lowercased, and known country aliases mapped (`UK` → `United Kingdom`, configurable in `src/config.py`).
- **Standardize first, then deduplicate**, so duplicates that differ only by formatting are caught.
- Exact duplicate rows are removed, keeping one copy (113 orders, 3 customers, 2 products).
- If a customer or product ID still repeats with different data, the first record is kept and a warning is logged (this prevents fan-out in the join). This affects `82494L` / `82494l`; price 2.95 was kept over 8.29.

**Joining and checks**
- Orders are LEFT JOINed to customers and products, so unmatched orders are kept and flagged, not lost. The pipeline stops if the join changes the row count.
- Nine checks run on every order: order, customer, and product IDs present; order ID unique; date valid; customer matched; product matched; quantity > 0; price > 0.
- A valid date matches `YYYY-MM-DD HH:MM:SS` and is not in the future. The original text is kept for the DQ report.
- If an order ID appears twice with different data, **both** copies fail, since the correct version can't be determined.
- Each problem is reported once, at its root cause: a missing customer ID does not also fail "customer matched," and an unknown product does not also fail "price > 0."
- Orders failing any check are excluded from `clean_orders.csv` and listed in `dq_report.csv`.

**Business rules**
- Revenue = quantity × product price, rounded to 2 decimals.
- Cancellations (negative quantities) fail the quantity check, per the requirements, rather than being netted against sales.
- Orders from a customer with no country are kept and reported as `Unknown` in revenue by country, so total revenue stays correct.
- "Records failing checks" counts orders, not failures: 269 orders (273 failures; some orders fail more than one check). Removed duplicates are not counted as failures.

## 5. Prerequisites and how to run

**Requirements:** Python 3.9 or newer (tested on Python 3.9.6 with pandas 2.3.3). No database install is needed.

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run_pipeline.py
```

The run ends with `Pipeline completed successfully` (exit code 0) or `Pipeline FAILED: <reason>` (exit code 1). Every run recreates all files in `output/`.

## 6. Outputs

| File | Contents |
|---|---|
| `output/profiling_summary.md` | Raw data statistics: row counts, duplicates, distinct keys, nulls per column, and identified quality issues |
| `output/clean_orders.csv` | 7,787 orders that passed every check, with the 11 required columns |
| `output/dq_report.csv` | 9 `summary` rows (check, PASS/FAIL, rows failed) and 273 `exception` rows (order ID, check, column, failing value) |
| `output/analysis_results.csv` | `question, rank, label, value`: revenue by country, top 10 products, top 5 customers, and records failing checks |

**Reconciliation:** 8,169 input orders = 7,787 clean + 269 failed + 113 duplicates removed.

## 7. Known limitations and potential improvements

- **Price:** one list price per product (most common), not the price at the time of sale. Improvement: keep price history and use the price in effect on the order date.
- **Categories:** keyword-based approximations; about 37% fall under "Other." In production they would come from the product master data.
- **Sample:** 150 customers over 3 months, so results describe the sample. For example, the Netherlands ranks second because of one large customer.
- **Cancellations** are excluded, not netted against sales. The business should confirm the preferred treatment.
- **Duplicate IDs with different data** in customers or products are resolved by keeping the first record, which depends on file order. These should be confirmed with the data owner.
- **Country standardization** uses title case plus a small alias list; codes such as `USA` would need more aliases.
- **Email format** is profiled but not a DQ check, since it's not required for reporting.
- **Scale and operations:** fine for this volume. For larger data: a persistent database or Spark, a scheduler such as Airflow, and Docker for packaging.

## Project structure

```
run_pipeline.py        Entry point: runs every step in order
requirements.txt
data/                  Source files read by the pipeline
src/
  config.py            Paths, required columns, and rules
  load.py              Reads CSVs; fails fast on missing files or columns
  profiling.py         Writes profiling_summary.md
  clean.py             Standardization and duplicate removal
  database.py          In-memory SQLite and SQL file runner
  transform.py         Runs the join and checks the row count
  checks.py            DQ checks, DQ report, reconciliation
  analysis.py          Runs the business-question SQL files
  outputs.py           Splits passed/failed rows and writes CSVs
sql/                   Join and business-question queries
tests/                 Unit and end-to-end tests
scripts/               One-time data preparation (not part of the pipeline run)
docs/                  injected_issues.csv
output/                Generated outputs
```

## Tests

```bash
python -m pytest -v
```

10 tests: cleaning rules, each DQ check (including a control test where a valid order must pass everything), reconciliation failing when rows go missing, and an end-to-end run confirming revenue by country equals total revenue in `clean_orders.csv`.