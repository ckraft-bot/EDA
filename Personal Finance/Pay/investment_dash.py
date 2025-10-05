import streamlit as st
import pandas as pd
import numpy as np
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
# from finance_dash import conn
import yfinance as yf
from datetime import date, timedelta

def investment_dashboard():
    st.title("📈 Investment Overview")
    # Today's date
    today = date.today()

    # x year lookback
    lookback_years = 1
    lookback_date = date(today.year - lookback_years, today.month, today.day)

    st.write(f"5-Year Historical Prices ({lookback_date} to {today})")

    etfs = {
        'VOO': 'Vanguard S&P 500 ETF',
        'XLK': 'Invests in technology companies within the S&P 500, including sectors like software and IT services.',            
        'CPNG':  'Invests in e-commerce company known as the Amazon of South Korea',
        'SOFI': 'Invests in fintech and finance technology solutions',
        'JAAA': 'Invests in high-quality collateralized loan obligations (CLOs)',
        'BLOK': 'Invests in companies involved in blockchain and data-sharing technologies'
    }

    my_stocks = list(etfs.keys())
    benchmark = '^GSPC'  # S&P 500 as reference
    st.write(f"my stocks: {my_stocks} + benchmark")
    
    # Download historical prices for all tickers + benchmark
    # ech = yf.download(my_stocks + [benchmark], start=lookback_date, end=today)['Adj Close']

    # # Show full table
    # st.dataframe(ech)

    # # Loop through each ticker individually
    # for ticker in my_stocks:
    #     st.subheader(f"{ticker} - {etfs[ticker]}")
    #     st.line_chart(ech[[ticker, benchmark]])  # Plot ticker vs S&P 500
