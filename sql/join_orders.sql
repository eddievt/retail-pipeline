-- Join every order to its customer and product.
-- LEFT JOIN keeps orders whose customer or product is missing,
-- so the data quality checks can flag them instead of losing them.
SELECT
    o.order_id,
    o.customer_id,
    c.customer_name,
    c.country,
    o.product_id,
    p.product_name,
    p.category,
    o.order_date,
    o.order_date_raw,
    o.quantity,
    p.price,
    ROUND(o.quantity * p.price, 2) AS revenue,
    c.customer_id IS NOT NULL AS customer_found,
    p.product_id IS NOT NULL AS product_found
FROM orders AS o
LEFT JOIN customers AS c ON o.customer_id = c.customer_id
LEFT JOIN products AS p ON o.product_id = p.product_id;