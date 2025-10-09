import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date
from finance_dash import conn  # ✅ uses the global cached connection


def app():
    st.title("📈 Investment Overview")

    today = date.today()
    lookback_years = 1
    lookback_date = date(today.year - lookback_years, today.month, today.day)

    etfs = {
        'VOO': 'Vanguard S&P 500 ETF',
        'XLK': 'Tech sector ETF (S&P 500 tech companies)',
        'CPNG': 'Coupang — South Korea e-commerce',
        'SOFI': 'SoFi Technologies — fintech solutions',
        'JAAA': 'Janus Henderson AAA CLO ETF',
        'BLOK': 'Amplify Transformational Data Sharing ETF (Blockchain exposure)'
    }

    symbols = list(etfs.keys())
    benchmark = "^GSPC"
    all_symbols = symbols + [benchmark]

    st.write(f"📊 Fetching data for: {', '.join(symbols)} + benchmark ({benchmark})")

    # Download price data
    data = yf.download(all_symbols, start=lookback_date, end=today)['Adj Close']

    returns = (data.iloc[-1] / data.iloc[0] - 1) * 100
    daily_change = (data.iloc[-1] / data.iloc[-2] - 1) * 100

    # --- Create or update table ---
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS main_schema.investment_pulse (
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
        """)

        # --- Insert or update each ETF ---
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}

            current_price = round(data.iloc[-1][symbol], 2)
            one_year_return = round(returns[symbol], 2)
            daily_chg = round(daily_change[symbol], 2)
            market_cap = info.get("marketCap")
            pe_ratio = info.get("trailingPE")
            dividend_yield = info.get("dividendYield")
            high_52 = info.get("fiftyTwoWeekHigh")
            low_52 = info.get("fiftyTwoWeekLow")

            cur.execute("""
            INSERT INTO main_schema.investment_pulse (
                symbol, name, current_price, one_year_return, daily_change,
                market_cap, pe_ratio, dividend_yield, fifty_two_week_high,
                fifty_two_week_low
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol)
            DO UPDATE SET
                name = EXCLUDED.name,
                current_price = EXCLUDED.current_price,
                one_year_return = EXCLUDED.one_year_return,
                daily_change = EXCLUDED.daily_change,
                market_cap = EXCLUDED.market_cap,
                pe_ratio = EXCLUDED.pe_ratio,
                dividend_yield = EXCLUDED.dividend_yield,
                fifty_two_week_high = EXCLUDED.fifty_two_week_high,
                fifty_two_week_low = EXCLUDED.fifty_two_week_low,
                last_updated = NOW();
            """, (
                symbol, etfs[symbol], current_price, one_year_return, daily_chg,
                market_cap, pe_ratio, dividend_yield, high_52, low_52
            ))

        conn.commit()  # ✅ commit after all inserts

    st.success("✅ Investment pulse successfully written to NeonDB!")

    # --- Optional: read back results to confirm ---
    df = pd.read_sql("SELECT * FROM main_schema.investment_pulse ORDER BY one_year_return DESC;", conn)
    st.dataframe(df)
    st.write("Data last updated:", df['last_updated'].max())