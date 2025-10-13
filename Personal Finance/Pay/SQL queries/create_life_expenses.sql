-- finance tracker
-- Drop table if exists
DROP TABLE IF EXISTS main_schema."life_expenses";

-- Create table matching CSV columns
CREATE TABLE main_schema."life_expenses" (
    id BIGSERIAL PRIMARY KEY, -- auto-incrementing unique ID
    date DATE NOT NULL,
    month INT GENERATED ALWAYS AS (EXTRACT(MONTH FROM date)) STORED, -- auto-computed month
    category TEXT,
    payment_for TEXT,
    payment_to TEXT,
    payment_from TEXT,
    payment_amount NUMERIC
);

-- use the command below to copy (truncate) table from csv import
gear_vault_db=> \COPY main_schema."life_expenses"(date, category, payment_for, payment_to, payment_from, payment_amount) FROM 'C:\\Users\\Clair\\Documents\\Code Development\\Python Local\\personal_finance\\Bills.csv' DELIMITER ',' CSV HEADER;

-- confimration of rows added to table
COPY 320

-- backfilling data with rental days
INSERT INTO main_schema."life_expenses" 
(date, category, payment_for, payment_to, payment_from, payment_amount)
VALUES
('YYYY-MM-DD', 'Bill', 'Rent', 'XXX Apartments', 'Checking XXXX', 500)