import streamlit as st
import pandas as pd
import numpy as np
import psycopg2
import plotly.express as px
import plotly.graph_objects as go

# --- Database connection ---
@st.cache_resource
def get_connection():
    conn = psycopg2.connect(
        host="ep-dry-breeze-a85tfkd4-pooler.eastus2.azure.neon.tech",
        database="gear_vault_db",
        user="neondb_owner",
        password="npg_Ilg2G7Vdsntr",
        port=5432,
        sslmode="require"
    )
    conn.autocommit = True
    return conn

conn = get_connection()
if conn.closed:
    conn = get_connection()

# --- Fidgets ---
st.segmented_control("Filter", ["Open", "Closed"])
st.pills("Domain", ["Groceries", "Bills", "Invetments"])
# st.feedback("thumbs")
st.button("Insert Data")
# st.toggle("Enable")

# --- Page layout ---
st.title("📊 Grocery Habits")

# --- Query for dynamic filter options ---
query_years = """
    SELECT DISTINCT EXTRACT(YEAR FROM date)::INT AS year
    FROM main_schema."grocery_expenses"
    ORDER BY year;
"""
query_stores = """
    SELECT DISTINCT store
    FROM main_schema."grocery_expenses"
    ORDER BY store;
"""

years = pd.read_sql(query_years, conn)['year'].tolist()
stores = pd.read_sql(query_stores, conn)['store'].dropna().tolist()

# --- Filters on top ---
# st.markdown("### Filters")
# col1, col2 = st.columns([1, 3])

# with col1:
#     year_filter = st.multiselect("Select Year", options=years)

# with col2:
#     store_filter = st.multiselect("Select Store(s)", options=stores, default=stores)


# --- SECTION 1: Summary ---
st.markdown("## 🏪 Your Prefered Stores (All Years)")

query_popular_stores = """
    SELECT 
        store,
        COUNT(*) AS visit_count,
        MIN(date) AS first_visit,
        MAX(date) AS last_visit,
        SUM(money_spent) AS total_spent_here
    FROM main_schema."grocery_expenses"
    GROUP BY store
    ORDER BY visit_count DESC;
"""
df_popular = pd.read_sql(query_popular_stores, conn)

# Display summary text
st.write(f"You have shopped at {len(df_popular)} different stores.")
st.write(f"Earliest visit: {df_popular['first_visit'].min()} | Most recent visit: {df_popular['last_visit'].max()}")

# Horizontal bar chart
fig_popular = px.bar(
    df_popular,
    x="visit_count",
    y="store",
    orientation="h",
    text_auto=True,
    hover_data={
        "visit_count": True,
        "total_spent_here": True,
        "first_visit": True,
        "last_visit": True
    },
)

# Reverse Y-axis so most visited store is at the top
fig_popular.update_layout(yaxis=dict(autorange="reversed"))

st.plotly_chart(fig_popular, use_container_width=True)


# --- SECTION 2: yearly summary statistics ---
st.markdown("## 📅 Spending Statistics Year Over Year")

query_yoy = """
    SELECT 
        EXTRACT(YEAR FROM date) AS year,
        COUNT(*) AS visit_count,
        MIN(money_spent) AS min_spent,
        MAX(money_spent) AS max_spent,
        ROUND(AVG(money_spent), 2) AS avg_spent,
        SUM(money_spent) AS total_spent
    FROM main_schema."grocery_expenses"
    GROUP BY year
    ORDER BY year;
"""

df_yoy = pd.read_sql(query_yoy, conn)

# --- Build layered chart ---
fig_yoy = go.Figure()

# 1. Bar chart for total spending
fig_yoy.add_bar(
    x=df_yoy["year"],
    y=df_yoy["total_spent"],
    name="Total Spent ($)",
    marker_color="rgba(0, 128, 255, 0.6)",
    yaxis="y1"
)

# 2️. Shaded range for min–max spending per year
fig_yoy.add_traces([
    go.Scatter(
        x=pd.concat([df_yoy["year"], df_yoy["year"][::-1]]),
        y=pd.concat([df_yoy["max_spent"], df_yoy["min_spent"][::-1]]),
        fill="toself",
        fillcolor="rgba(0, 128, 255, 0.1)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        name="Range (Min–Max)"
    )
])

# 3. Line chart for average spending
fig_yoy.add_scatter(
    x=df_yoy["year"],
    y=df_yoy["avg_spent"],
    mode="lines+markers",
    name="Average Spent ($)",
    line=dict(color="orange", width=3),
    yaxis="y2"
)

# --- Layout customization ---
fig_yoy.update_layout(
    # title="💰 Year-Over-Year Spending Overview",
    xaxis=dict(title="Year", dtick=1),
    yaxis=dict(title="Total Spending ($)", side="left"),
    yaxis2=dict(
        title="Average Spending ($)",
        overlaying="y",
        side="right",
        showgrid=False
    ),
    legend=dict(
        x=0.01, y=0.99,
        bgcolor="rgba(255,255,255,0.7)",
        bordercolor="gray", borderwidth=1
    ),
    bargap=0.3,
    template="plotly_white",
)

st.dataframe(df_yoy)
st.plotly_chart(fig_yoy, use_container_width=True)


# --- SECTION 3: Monthly spending habits YOY ---
st.markdown("## 📆 Monthly Spending Trends by Year")
query_monthly = """
    SELECT
        EXTRACT(YEAR FROM date) AS year,
        month,
        SUM(money_spent) AS total_spent,
        ROUND(AVG(money_spent), 2) AS avg_spent
    FROM main_schema."grocery_expenses"
    GROUP BY year, month
    ORDER BY month, year;
"""
df_monthly = pd.read_sql(query_monthly, conn)
fig_monthly = px.line(
    df_monthly,
    x="month",
    y="total_spent",
    color="year",
    markers=True,
    title="Monthly Spending YOY",
)
st.plotly_chart(fig_monthly, use_container_width=True)


# --- SECTION 4: Monthly spending by store (year-over-year) ---
# st.markdown("## 🛒 Monthly Spending by Store (YOY)")
# query_store_yoy = """
#     SELECT
#         store,
#         EXTRACT(YEAR FROM date) AS year,
#         month,
#         SUM(money_spent) AS total_spent,
#         ROUND(AVG(money_spent), 2) AS avg_spent
#     FROM main_schema."grocery_expenses"
#     GROUP BY store, year, month
#     ORDER BY store, month, year;
# """
# df_store_yoy = pd.read_sql(query_store_yoy, conn)
# fig_store_yoy = px.line(
#     df_store_yoy,
#     x="month",
#     y="total_spent",
#     color="year",
#     facet_col="store",
#     facet_col_wrap=3,
#     title="Store-by-Store Spending Trends (Year-Over-Year)",
# )
# st.plotly_chart(fig_store_yoy, use_container_width=True)


