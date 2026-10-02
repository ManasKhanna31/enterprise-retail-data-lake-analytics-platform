WITH customer_sales AS (
    SELECT
        c.customer_id,
        c.name,
        SUM(f.revenue) AS total_revenue
    FROM fact_sales f
    JOIN dim_customer c
        ON f.customer_key = c.customer_key
    GROUP BY c.customer_id, c.name
)
SELECT
    customer_id,
    name,
    total_revenue,
    RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank
FROM customer_sales
ORDER BY revenue_rank;