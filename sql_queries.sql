-- ================================================================
--  E-Commerce Sales Analytics — SQL Queries
--  Author: Abhishek Jha
--  Database: ecommerce_db (MySQL 8)
-- ================================================================

USE ecommerce_db;

-- Q1: Revenue and profit by region
SELECT
    r.region,
    COUNT(f.order_id)              AS total_orders,
    ROUND(SUM(f.sales), 2)         AS total_revenue,
    ROUND(SUM(f.profit), 2)        AS total_profit,
    ROUND(AVG(f.profit_margin), 2) AS avg_profit_margin_pct
FROM fact_orders f
JOIN dim_customer c ON f.customer_id = c.customer_id
JOIN dim_region r   ON c.region_id   = r.region_id
GROUP BY r.region
ORDER BY total_profit DESC;


-- Q2: Top 10 most profitable products
SELECT
    p.product_name,
    p.category,
    p.sub_category,
    ROUND(SUM(f.profit), 2)  AS total_profit,
    ROUND(SUM(f.sales), 2)   AS total_revenue,
    COUNT(f.order_id)         AS times_ordered
FROM fact_orders f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category, p.sub_category
ORDER BY total_profit DESC
LIMIT 10;


-- Q3: Category profit margin — which makes vs loses money
SELECT
    p.category,
    p.sub_category,
    ROUND(SUM(f.sales), 2)                   AS total_revenue,
    ROUND(SUM(f.profit), 2)                  AS total_profit,
    ROUND(SUM(f.profit)/SUM(f.sales)*100, 2) AS profit_margin_pct,
    SUM(f.is_loss)                           AS loss_orders
FROM fact_orders f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.category, p.sub_category
ORDER BY profit_margin_pct ASC;


-- Q4: Discount impact — at what % does profit go negative?
SELECT
    discount_band,
    COUNT(order_id)                     AS total_orders,
    ROUND(AVG(discount)*100, 1)         AS avg_discount_pct,
    ROUND(AVG(profit), 2)               AS avg_profit,
    ROUND(SUM(profit), 2)               AS total_profit,
    SUM(is_loss)                        AS loss_orders,
    ROUND(SUM(is_loss)/COUNT(*)*100, 1) AS loss_rate_pct
FROM fact_orders
GROUP BY discount_band
ORDER BY avg_discount_pct ASC;


-- Q5: Monthly revenue trend
SELECT
    order_year,
    order_month,
    order_month_name,
    ROUND(SUM(sales), 2)  AS monthly_revenue,
    ROUND(SUM(profit), 2) AS monthly_profit,
    COUNT(order_id)        AS orders
FROM fact_orders
GROUP BY order_year, order_month, order_month_name
ORDER BY order_year, order_month;


-- Q6: Customer segment performance
SELECT
    s.segment,
    COUNT(DISTINCT f.customer_id)            AS unique_customers,
    COUNT(f.order_id)                        AS total_orders,
    ROUND(SUM(f.sales), 2)                   AS total_revenue,
    ROUND(SUM(f.profit), 2)                  AS total_profit,
    ROUND(AVG(f.sales), 2)                   AS avg_order_value,
    ROUND(SUM(f.profit)/SUM(f.sales)*100, 2) AS profit_margin_pct
FROM fact_orders f
JOIN dim_customer c ON f.customer_id = c.customer_id
JOIN dim_segment s  ON c.segment_id  = s.segment_id
GROUP BY s.segment
ORDER BY total_profit DESC;


-- Q7: Shipping mode — speed vs profitability
SELECT
    sm.ship_mode,
    COUNT(f.order_id)              AS total_orders,
    ROUND(AVG(f.shipping_days), 1) AS avg_shipping_days,
    ROUND(SUM(f.sales), 2)         AS total_revenue,
    ROUND(SUM(f.profit), 2)        AS total_profit,
    ROUND(AVG(f.profit_margin), 2) AS avg_profit_margin_pct
FROM fact_orders f
JOIN dim_ship_mode sm ON f.ship_mode_id = sm.ship_mode_id
GROUP BY sm.ship_mode
ORDER BY avg_shipping_days ASC;


-- Q8: Loss-making products — consistently losing money
SELECT
    p.product_name,
    p.category,
    p.sub_category,
    COUNT(f.order_id)            AS times_ordered,
    SUM(f.is_loss)               AS loss_count,
    ROUND(SUM(f.profit), 2)      AS total_profit,
    ROUND(AVG(f.discount)*100,1) AS avg_discount_pct
FROM fact_orders f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category, p.sub_category
HAVING loss_count > 3
ORDER BY total_profit ASC
LIMIT 15;
