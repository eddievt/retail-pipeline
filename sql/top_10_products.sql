-- Top 10 products by total revenue, from orders that passed every DQ check.
SELECT
    'top_10_products_by_revenue' AS question,
    product_id || ' - ' || product_name AS label,
    ROUND(SUM(revenue), 2) AS value
FROM clean_orders
GROUP BY product_id, product_name
ORDER BY value DESC, label
LIMIT 10;