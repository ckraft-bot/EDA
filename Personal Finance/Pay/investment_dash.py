import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date
from finance_dash import conn  # Global cached NeonDB connection


def app(conn):
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

    benchmark = "^GSPC"
    all_symbols = list(etfs.keys()) + [benchmark]

    st.info(f"📊 Fetching data for: {', '.join(all_symbols)}")

    # --- Download data from Yahoo Finance ---
    data = yf.download(
        all_symbols,
        start=lookback_date,
        end=today,
        group_by='ticker',
        auto_adjust=True,
        threads=True
    )

    # --- Robust extraction of adjusted close ---
    adj_close = pd.DataFrame()
    for symbol in all_symbols:
        try:
            if isinstance(data.columns, pd.MultiIndex):
                if 'Adj Close' in data[symbol].columns:
                    adj_close[symbol] = data[symbol]['Adj Close']
                elif 'Close' in data[symbol].columns:
                    adj_close[symbol] = data[symbol]['Close']
            else:
                if symbol in data.columns:
                    adj_close[symbol] = data[symbol]
                elif 'Adj Close' in data.columns:
                    adj_close[symbol] = data['Adj Close']
                elif 'Close' in data.columns:
                    adj_close[symbol] = data['Close']
            if adj_close[symbol].isna().all():
                st.warning(f"No valid data for {symbol}, skipping.")
                adj_close.drop(columns=symbol, inplace=True)
        except Exception as e:
            st.warning(f"Error fetching {symbol}: {e}")

    # Drop any fully empty columns
    adj_close = adj_close.dropna(axis=1, how='all')
    valid_symbols = [s for s in all_symbols if s in adj_close.columns]

    if not valid_symbols:
        st.error("❌ No valid data returned from Yahoo Finance.")
        return

    st.success(f"✅ Successfully fetched data for: {', '.join(valid_symbols)}")

    # --- Calculate returns ---
    returns = (adj_close.iloc[-1] / adj_close.iloc[0] - 1) * 100
    daily_change = (adj_close.iloc[-1] / adj_close.iloc[-2] - 1) * 100

    # --- Insert/update DB table ---
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

        for symbol in valid_symbols:
            if symbol == benchmark:
                continue  # skip benchmark in DB
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}

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
                symbol,
                etfs.get(symbol, symbol),
                round(adj_close.iloc[-1][symbol], 2),
                round(returns[symbol], 2),
                round(daily_change[symbol], 2),
                info.get("marketCap"),
                info.get("trailingPE"),
                info.get("dividendYield"),
                info.get("fiftyTwoWeekHigh"),
                info.get("fiftyTwoWeekLow"),
            ))

        conn.commit()

    st.success("✅ Investment pulse successfully written to NeonDB!")

    # --- Display table in Streamlit ---
    df = pd.read_sql("SELECT * FROM main_schema.investment_pulse ORDER BY one_year_return DESC;", conn)
    st.dataframe(df)
    st.write("Data last updated:", df['last_updated'].max())
