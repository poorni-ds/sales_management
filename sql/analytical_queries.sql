-- Sales Intelligence Hub — Analytical Queries Deliverable
-- These match what's wired up in pages/Query_Explorer.py (with %s branch
-- filters swapped out for literal values here so they can be run directly
-- in a MySQL client for grading/review).

-- =========================================================
-- BASIC QUERIES
-- =========================================================

-- 1. Retrieve all records from customer_sales
SELECT * FROM customer_sales;

-- 2. Retrieve all records from branch
SELECT * FROM branch;

-- 3. Retrieve all records from payment_split
SELECT * FROM payment_split;

-- 4. Display all sales with status = 'Open'
SELECT * FROM customer_sales WHERE status = 'Open';

-- 5. Retrieve all sales belonging to the Chennai branch
SELECT cs.*
FROM customer_sales cs
JOIN branch b ON cs.branch_id = b.branch_id
WHERE b.branch_name = 'Chennai';

-- =========================================================
-- AGGREGATION QUERIES
-- =========================================================

-- 6. Total gross sales across all branches
SELECT SUM(gross_sales) AS total_gross_sales FROM customer_sales;

-- 7. Total received amount across all sales
SELECT SUM(received_amount) AS total_received FROM customer_sales;

-- 8. Total pending amount across all sales
SELECT SUM(pending_amount) AS total_pending FROM customer_sales;

-- 9. Count of sales per branch
SELECT b.branch_name, COUNT(cs.sale_id) AS total_sales_count
FROM branch b
LEFT JOIN customer_sales cs ON b.branch_id = cs.branch_id
GROUP BY b.branch_name;

-- 10. Average gross sales amount
SELECT AVG(gross_sales) AS avg_gross_sales FROM customer_sales;

-- =========================================================
-- JOIN-BASED QUERIES
-- =========================================================

-- 11. Sales details along with branch name
SELECT cs.*, b.branch_name
FROM customer_sales cs
JOIN branch b ON cs.branch_id = b.branch_id;

-- 12. Sales details along with total payment received (via payment_split)
SELECT cs.sale_id, cs.name, cs.gross_sales, SUM(ps.amount_paid) AS total_paid
FROM customer_sales cs
JOIN payment_split ps ON cs.sale_id = ps.sale_id
GROUP BY cs.sale_id, cs.name, cs.gross_sales;

-- 13. Branch-wise total gross sales (JOIN + GROUP BY)
SELECT b.branch_name, SUM(cs.gross_sales) AS total_gross
FROM customer_sales cs
JOIN branch b ON cs.branch_id = b.branch_id
GROUP BY b.branch_name
ORDER BY total_gross DESC;

-- 14. Sales along with payment method used
SELECT cs.sale_id, cs.name, cs.product_name, ps.payment_method, ps.amount_paid
FROM customer_sales cs
JOIN payment_split ps ON cs.sale_id = ps.sale_id;

-- 15. Sales along with branch admin name
SELECT cs.sale_id, cs.name, cs.gross_sales, b.branch_admin_name
FROM customer_sales cs
JOIN branch b ON cs.branch_id = b.branch_id;

-- =========================================================
-- FINANCIAL TRACKING QUERIES (bonus, beyond the required 15)
-- =========================================================

-- 16. Sales where pending amount is greater than 5000
SELECT * FROM customer_sales WHERE pending_amount > 5000;

-- 17. Top 3 highest gross sales
SELECT * FROM customer_sales ORDER BY gross_sales DESC LIMIT 3;

-- 18. Branch with the highest total gross sales
SELECT b.branch_name, SUM(cs.gross_sales) AS total_gross
FROM customer_sales cs
JOIN branch b ON cs.branch_id = b.branch_id
GROUP BY b.branch_name
ORDER BY total_gross DESC
LIMIT 1;

-- 19. Monthly sales summary (group by month & year)
SELECT YEAR(date) AS year, MONTH(date) AS month,
       SUM(gross_sales) AS total_gross,
       SUM(received_amount) AS total_received
FROM customer_sales
GROUP BY YEAR(date), MONTH(date)
ORDER BY year, month;

-- 20. Payment method-wise total collection
SELECT payment_method, SUM(amount_paid) AS total_collected
FROM payment_split
GROUP BY payment_method;
