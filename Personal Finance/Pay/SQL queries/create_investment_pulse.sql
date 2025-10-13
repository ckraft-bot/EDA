CREATE TABLE IF NOT EXISTS main_schema."investment_pulse" (
    symbol TEXT PRIMARY KEY,
    name TEXT,
    current_price NUMERIC,
    one_year_return NUMERIC,
    daily_change NUMERIC,
    market_cap BIGINT,
    pe_ratio NUMERIC,
    dividend_yield NUMERIC,
    fifty_two_week_high NUMERIC,
    fifty_two_week_low NUMERIC,
    last_updated TIMESTAMP DEFAULT NOW()
);
