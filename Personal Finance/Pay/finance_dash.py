import streamlit as st
import pandas as pd
import numpy as np
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
import grocery_dash, bill_dash, investment_dash

# --- Global Database connection ---
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

# --- Sidebar page navigation ---
st.sidebar.title("📁 Pages")
page = st.sidebar.radio(
    "Select Page",
    ["Grocery Habits", "Bill History", "Investment Overview"]
)

# --- Page title ---
st.title("📊 Personal Finance Dashboard")

# --- Page content ---
if page == "Grocery Habits":
    st.header("🛒 Grocery Habits")
    st.write("This page shows your grocery spending trends, popular stores, and monthly summaries.")
    grocery_dash.app(conn)

elif page == "Bill History":
    st.header("💳 Bill History")
    st.write("This page shows your bills, payments, and trends over time.")
    bill_dash.app(conn)

elif page == "Investment Overview":
    st.header("📈 Investment Overview")
    st.write("This page shows your ETFs, stocks, and investment performance.")
    investment_dash.app()
