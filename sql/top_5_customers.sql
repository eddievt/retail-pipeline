-- Top 5 customers by total revenue, from orders that passed every DQ check.
SELECT
    'top_5_customers_by_revenue' AS question,
    customer_id || ' - ' || customer_name AS label,
    ROUND(SUM(revenue), 2) AS value
FROM clean_orders
GROUP BY customer_id, customer_name
ORDER BY value DESC, label
LIMIT 5;