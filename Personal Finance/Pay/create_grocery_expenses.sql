-- Drop table if exists
DROP TABLE IF EXISTS main_schema."grocery_expenses";

-- Create the table
CREATE TABLE main_schema."grocery_expenses" (
    id BIGSERIAL PRIMARY KEY,        -- auto-incrementing unique ID
    date DATE NOT NULL,              -- actual date
    month INT GENERATED ALWAYS AS (EXTRACT(MONTH FROM date)) STORED,  -- auto-computed month
    store TEXT,
    money_spent NUMERIC
);


-- use the command below to copy (truncate) table from csv import
\COPY main_schema."grocery_expenses"(date, store, money_spent) FROM 'C:\\Users\\Clair\\Documents\\Code Development\\Python Local\\personal_finance\\Grocery Habit.csv' DELIMITER ',' CSV HEADER;

-- confimration of rows added to table
COPY 234
