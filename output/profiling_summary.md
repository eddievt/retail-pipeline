# Profiling Summary

Statistics on the raw source files, before any cleaning.

## Overview

| Table | Rows | Columns | Exact duplicate rows | Distinct keys | Duplicate key values |
|---|---|---|---|---|---|
| orders | 8169 | 5 | 113 | 8055 | 114 |
| customers | 153 | 4 | 2 | 150 | 3 |
| products | 1796 | 4 | 2 | 1794 | 2 |

## Missing values by column

### orders

| Column | Missing | % of rows |
|---|---|---|
| order_id | 0 | 0.00% |
| customer_id | 100 | 1.22% |
| product_id | 0 | 0.00% |
| order_date | 2 | 0.02% |
| quantity | 0 | 0.00% |

### customers

| Column | Missing | % of rows |
|---|---|---|
| customer_id | 0 | 0.00% |
| customer_name | 0 | 0.00% |
| email | 2 | 1.31% |
| country | 1 | 0.65% |

### products

| Column | Missing | % of rows |
|---|---|---|
| product_id | 0 | 0.00% |
| product_name | 1 | 0.06% |
| price | 1 | 0.06% |
| category | 1 | 0.06% |

## Identified quality issues

Counted on the raw data. Each one is handled later by cleaning or by a DQ check.

| Table | Issue | Rows affected |
|---|---|---|
| orders | order_date missing or not a valid date | 5 |
| orders | order_date in the future | 1 |
| orders | quantity zero or negative | 140 |
| orders | customer_id not found in customers | 5 |
| orders | product_id not found in products | 10 |
| products | price missing, zero or negative | 5 |
| orders | product_id has extra spaces | 5 |
| customers | country has extra spaces | 1 |
| products | product_name has extra spaces | 457 |
| products | category has extra spaces | 3 |
| products | product_name not in uppercase | 11 |
| customers | customer_name has inconsistent casing or spelling | 3 |
| customers | country has inconsistent casing or spelling | 3 |
| products | category has inconsistent casing or spelling | 3 |
| customers | email missing @ | 1 |