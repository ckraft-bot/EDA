-- This query calculates the total life costs per year by combining expenses from life_expenses and grocery_expenses tables.
SELECT
    COALESCE(le.year, ge.year) AS year,
    COALESCE(le.paid, 0) AS bills_paid,
    COALESCE(ge.total_spent, 0) AS groceries_paid,
    ROUND(COALESCE(le.paid, 0) + COALESCE(ge.total_spent, 0), 2) AS total_expenses
FROM
(
    SELECT 
        EXTRACT(YEAR FROM date) AS year,
        SUM(payment_amount) AS paid
    FROM main_schema."life_expenses"
    GROUP BY EXTRACT(YEAR FROM date)
) le
FULL OUTER JOIN
(
    SELECT
        EXTRACT(YEAR FROM date) AS year,
        SUM(money_spent) AS total_spent
    FROM main_schema."grocery_expenses"
    GROUP BY EXTRACT(YEAR FROM date)
) ge
ON le.year = ge.year
WHERE COALESCE(le.year, ge.year) >= 2023
ORDER BY year;



-- BILLS
-- view first 10 rows of life expenses
SELECT * FROM main_schema."life_expenses" LIMIT 10;

-- view distinct categories and subcategories in life expenses
SELECT DISTINCT CATEGORY AS category_high_level, PAYMENT_FOR AS subcategory 
FROM main_schema.life_expenses
ORDER BY category_high_level;

-- 1. How are my bills split by category?
WITH categorized AS (
  SELECT
    CASE 
      -- Bills
      WHEN PAYMENT_FOR = 'Phone' THEN 'Phone' 
      WHEN PAYMENT_FOR = 'HOA dues' THEN 'HOA'
      WHEN PAYMENT_FOR = 'Rent' THEN 'Rent'
      
      -- Insurance
      WHEN PAYMENT_FOR IN ('Home Insurance', 'Renters Insurance', 'Auto Insurance') THEN 'Insurance'
      
      -- Loans
      WHEN PAYMENT_FOR IN ('House Loan A', 'House Loan B') THEN 'Mortgage'
      
      -- Subscriptions
      WHEN PAYMENT_FOR IN ('Study', 'Entertainment', 'Dev', 'Hobby', 'iCloud+', 'Streaming', 'Printer') THEN 'Subscriptions'
      
      -- Utilities
      WHEN PAYMENT_FOR IN ('Electricity', 'Water', 'Wifi', 'Sewar') THEN 'Utilities'
      
      ELSE CATEGORY 
    END AS CATEGORY_NAME
  FROM main_schema."life_expenses"
  WHERE PAYMENT_FOR IN (
    'Rent', 
    'Phone', 
    'HOA dues', 
    'House Loan A', 
    'House Loan B',
    'Electricity',
    'Water',
    'Wifi',
    'Sewar',
    'Home Insurance',
    'Renters Insurance',
    'Auto Insurance',
    'Study',
    'Entertainment',
    'Dev',
    'Hobby',
    'iCloud+',
    'Streaming',
    'Printer'
  )
)
SELECT
  CATEGORY_NAME,
  COUNT(*) AS PAYMENTS,
  ROUND(
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
    2
  ) AS PERCENTAGE
FROM categorized
GROUP BY CATEGORY_NAME
ORDER BY PERCENTAGE DESC;


-- 2. Total paid per year
SELECT 
  EXTRACT(YEAR FROM date) AS YEAR,
  SUM(payment_amount) AS PAID
FROM main_schema."life_expenses"
GROUP BY 
  EXTRACT(YEAR FROM date)
ORDER BY 
  YEAR;

-- 3. Total paid per month
SELECT 
  EXTRACT(YEAR FROM date) AS year,
  EXTRACT(MONTH FROM date) AS month,
  SUM(payment_amount) AS paid
FROM main_schema."life_expenses"
GROUP BY 
  EXTRACT(YEAR FROM date),
  EXTRACT(MONTH FROM date)
ORDER BY 
  year,
  month;

-- 4. Total paid per month in current year (2025)
SELECT 
  EXTRACT(YEAR FROM date) AS year,
  EXTRACT(MONTH FROM date) AS month,
  SUM(payment_amount) AS paid
FROM main_schema."life_expenses"
WHERE EXTRACT(YEAR FROM date) = 2025
GROUP BY 
  EXTRACT(YEAR FROM date),
  EXTRACT(MONTH FROM date)
ORDER BY 
  month;

-- 4a. What's the cost breakdown of Feb (the most expensive month this year)?
SELECT 
    date,
    category,
    payment_for,
    payment_to,
    payment_amount
FROM main_schema."life_expenses"
WHERE EXTRACT(YEAR FROM date) = 2025
  AND EXTRACT(MONTH FROM date) = 2
  ORDER BY payment_amount DESC;



-- GROCERY 
-- 1. places shopped by frequency in all years, popularity
SELECT 
    store,
    COUNT(*) AS visit_count,
    MIN(date) AS first_visit,
    MAX(date) AS last_visit,
    SUM(money_spent) AS total_spent_here
FROM main_schema."grocery_expenses"
GROUP BY store
ORDER BY visit_count DESC;

-- 2. times shopped year over year 
SELECT 
    EXTRACT(YEAR FROM date) AS year,
    COUNT(*) AS visit_count,
    SUM(money_spent) AS total_spent,
    ROUND(AVG(money_spent), 2) AS avg_spent
FROM main_schema."grocery_expenses"
GROUP BY year
ORDER BY year;

-- 3. Yearly spending sum year-over-year
SELECT
    EXTRACT(YEAR FROM date) AS year,
    SUM(money_spent) AS total_spent
FROM main_schema."grocery_expenses"
GROUP BY year
ORDER BY year;

-- 4. Monthly spending habits year-over-year
SELECT
    EXTRACT(YEAR FROM date) AS year,
    month,
    -- COUNT(*) AS visit_count,
    SUM(money_spent) AS total_spent,
    ROUND(AVG(money_spent), 2) AS avg_spent
FROM main_schema."grocery_expenses"
GROUP BY year, month
ORDER BY month, year;

-- 5. Monthly spending habits by store, year-over-year
-- only include rows where each store has data for that month across all three years
WITH store_months_with_all_years AS (
    SELECT 
        store,
        month
    FROM main_schema."grocery_expenses"
    WHERE EXTRACT(YEAR FROM date) IN (2023, 2024, 2025)
    GROUP BY store, month
    HAVING COUNT(DISTINCT EXTRACT(YEAR FROM date)) = 3
)
SELECT
    g.store,
    EXTRACT(YEAR FROM g.date) AS year,
    g.month,
    SUM(g.money_spent) AS total_spent,
    ROUND(AVG(g.money_spent), 2) AS avg_spent
FROM main_schema."grocery_expenses" g
JOIN store_months_with_all_years s
  ON g.store = s.store
  AND g.month = s.month
WHERE g.store IN ('Food City', 'AFG', 'Walmart')
  AND EXTRACT(YEAR FROM g.date) IN (2023, 2024, 2025)
GROUP BY g.store, year, g.month
ORDER BY g.store, g.month, year;


