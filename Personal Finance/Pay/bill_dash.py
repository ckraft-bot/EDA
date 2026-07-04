import streamlit as st
import pandas as pd
import numpy as np
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- Cached data functions ---
@st.cache_data(ttl=3600)
def get_categories(_conn): # The underscore tells Streamlit, “don’t try to hash this parameter.” It still passes the _connection object into the function but is ignored for caching purposes.
    query = """
        SELECT DISTINCT category
        FROM main_schema."life_expenses"
        WHERE category IS NOT NULL
        ORDER BY category;
    """
    return pd.read_sql(query, _conn)['category'].tolist()

@st.cache_data(ttl=3600)
def get_years(_conn):
    query = """
        SELECT DISTINCT EXTRACT(YEAR FROM date)::INT AS year
        FROM main_schema."life_expenses"
        ORDER BY year DESC;
    """
    return pd.read_sql(query, _conn)['year'].tolist()

def app(_conn):
    categories = get_categories(_conn)
    years = get_years(_conn)

    # --- Filters ---
    st.markdown("### Filters")
    col1, col2 = st.columns([1, 3])

    with col1:
        year_filter = st.multiselect("Select Year", options=years, default=years)
    with col2:
        category_filter = st.multiselect("Select Category", options=categories, default=categories)

    # Build WHERE clause
    where_clause = ""
    params = []
    if year_filter or category_filter:
        conditions = []
        if year_filter:
            year_placeholders = ",".join(["%s"] * len(year_filter))
            conditions.append(f"EXTRACT(YEAR FROM date)::INT IN ({year_placeholders})")
            params.extend(year_filter)
        if category_filter:
            category_placeholders = ",".join(["%s"] * len(category_filter))
            conditions.append(f"category IN ({category_placeholders})")
            params.extend(category_filter)
        where_clause = "WHERE " + " AND ".join(conditions)

    # --- SECTION 1: Summary Statistics ---
    st.markdown("## 💰 Bill Summary")

    query_summary = f"""
        SELECT
            COUNT(*) AS total_bills,
            ROUND(SUM(payment_amount)::NUMERIC, 2) AS total_amount,
            ROUND(AVG(payment_amount)::NUMERIC, 2) AS avg_amount,
            MIN(date) AS earliest_date,
            MAX(date) AS latest_date
        FROM main_schema."life_expenses"
        {where_clause};
    """

    df_summary = pd.read_sql(query_summary, _conn, params=params)

    if df_summary.empty or df_summary['total_bills'].iloc[0] == 0:
        st.info("No bills found for selected filters.")
        return

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Bills", int(df_summary['total_bills'].iloc[0]))
    with col2:
        st.metric("Total Amount", f"${df_summary['total_amount'].iloc[0]:,.2f}")
    with col3:
        st.metric("Average Bill", f"${df_summary['avg_amount'].iloc[0]:,.2f}")
    # with col4:
    #     st.metric("Date Range", f"{df_summary['earliest_date'].iloc[0].strftime('%Y-%m-%d')} to {df_summary['latest_date'].iloc[0].strftime('%Y-%m-%d')}")

    # --- SECTION 2: Bills by Category ---
    st.markdown("## 📊 Spending by Category")

    query_category = f"""
        SELECT
            category,
            COUNT(*) AS bill_count,
            ROUND(SUM(payment_amount)::NUMERIC, 2) AS total_amount,
            ROUND(AVG(payment_amount)::NUMERIC, 2) AS avg_amount
        FROM main_schema."life_expenses"
        {where_clause}
        GROUP BY category
        ORDER BY total_amount DESC;
    """

    df_category = pd.read_sql(query_category, _conn, params=params)

    fig_category = px.pie(
        df_category,
        values="total_amount",
        names="category",
        title="Total Spending by Category",
        hover_data={"bill_count": True, "avg_amount": ":.2f"}
    )
    st.plotly_chart(fig_category, use_container_width=True)

    # Category table
    st.dataframe(
        df_category.rename(columns={
            'category': 'Category',
            'bill_count': 'Count',
            'total_amount': 'Total ($)',
            'avg_amount': 'Average ($)'
        }).style.format({'Total ($)': '${:,.2f}', 'Average ($)': '${:,.2f}'}),
        use_container_width=True,
        hide_index=True
    )

    # --- SECTION 3: Monthly Spending Trends ---
    st.markdown("## 📅 Monthly Spending Trends")

    query_monthly = f"""
        SELECT
            EXTRACT(YEAR FROM date)::INT AS year,
            EXTRACT(MONTH FROM date)::INT AS month,
            ROUND(SUM(payment_amount)::NUMERIC, 2) AS total_amount,
            COUNT(*) AS bill_count
        FROM main_schema."life_expenses"
        {where_clause}
        GROUP BY
            EXTRACT(YEAR FROM date)::INT,
            EXTRACT(MONTH FROM date)::INT
        ORDER BY
            EXTRACT(YEAR FROM date)::INT,
            EXTRACT(MONTH FROM date)::INT;
    """

    df_monthly = pd.read_sql(query_monthly, _conn, params=params)

    fig_monthly = px.line(
        df_monthly,
        x="month",
        y="total_amount",
        color="year",
        markers=True,
        title="Monthly Bill Spending Year-Over-Year",
        labels={"month": "Month", "total_amount": "Total Amount ($)", "year": "Year"},
        hover_data={"bill_count": True, "total_amount": ":.2f"}
    )
    fig_monthly.update_xaxes(tickmode='linear', tick0=1, dtick=1)
    st.plotly_chart(fig_monthly, use_container_width=True)

    # --- SECTION 4: Year-over-Year Comparison ---
    st.markdown("## 📈 Year-over-Year Comparison")

    query_yoy = f"""
        SELECT
            EXTRACT(YEAR FROM date)::INT AS year,
            COUNT(*) AS bill_count,
            ROUND(SUM(payment_amount)::NUMERIC, 2) AS total_amount,
            ROUND(AVG(payment_amount)::NUMERIC, 2) AS avg_amount
        FROM main_schema.life_expenses
        {where_clause}
        GROUP BY EXTRACT(YEAR FROM date)::INT
        ORDER BY EXTRACT(YEAR FROM date)::INT;
    """

    df_yoy = pd.read_sql(query_yoy, _conn, params=params)

    fig_yoy = px.bar(
        df_yoy,
        x="year",
        y="total_amount",
        title="Total Spending by Year",
        labels={"year": "Year", "total_amount": "Total Amount ($)"},
        text="total_amount",
        hover_data={"bill_count": True, "avg_amount": ":.2f"}
    )
    fig_yoy.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
    st.plotly_chart(fig_yoy, use_container_width=True)

    st.dataframe(
        df_yoy.rename(columns={
            'year': 'Year',
            'total_amount': 'Total ($)',
            'bill_count': 'Count',
            'avg_amount': 'Average ($)'
        }).style.format({'Total ($)': '${:,.2f}', 'Average ($)': '${:,.2f}'}),
        use_container_width=True,
        hide_index=True
    )

    # --- SECTION 5: Recent Bills ---
    st.markdown("## 📋 Recent Bills")

    query_recent = f"""
        SELECT DISTINCT ON (category, payment_for, payment_to)
            date,
            category,
            payment_for,
            payment_to,
            ROUND(payment_amount::NUMERIC, 2) AS payment_amount
        FROM main_schema.life_expenses
        {where_clause}
        ORDER BY
            category,
            payment_for,
            payment_to,
            date DESC;
    """

    df_recent = pd.read_sql(query_recent, _conn, params=params)

    st.dataframe(
        df_recent.rename(columns={
            'date': 'Date',
            'category': 'Category',
            'payment_for': 'Payment For',
            'payment_to': 'Payment To',
            'payment_amount': 'Amount ($)',
        }).style.format({'Amount ($)': '${:,.2f}'}),
        use_container_width=True,
        hide_index=True
    )