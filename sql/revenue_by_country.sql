-- Total revenue by country, highest first.
-- Runs on clean_orders, so only rows that passed every DQ check are counted.
SELECT
    'revenue_by_country' AS question,
     COALESCE(country, 'Unknown') AS label,
    ROUND(SUM(revenue), 2) AS value
FROM clean_orders
GROUP BY COALESCE(country, 'Unknown')
ORDER BY value DESC, label;