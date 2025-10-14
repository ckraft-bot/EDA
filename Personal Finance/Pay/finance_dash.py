import streamlit as st
import pandas as pd
import numpy as np
import psycopg2
import plotly.express as px
import plotly.graph_objects as go

# --- Page configuration ---
st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Global Database connection (define FIRST, before imports) ---
@st.cache_resource
def get_connection():
    try:
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
    except psycopg2.Error as e:
        st.error(f"❌ Database connection failed: {e}")
        st.stop()

# --- Initialize connection ---
try:
    conn = get_connection()
    if conn.closed:
        conn = get_connection()
except Exception as e:
    st.error(f"Unable to connect to database: {e}")
    st.stop()

# --- Import page modules AFTER connection is created ---
import grocery_dash
import bill_dash
import investment_dash

# --- Sidebar page navigation ---
st.sidebar.title("📁 Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["Grocery Habits", "Bill History", "Investment Overview"],
    help="Choose a dashboard to view"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info("Personal finance tracking dashboard with spending analytics across multiple categories.")

# --- Page title and description ---
st.title("📊 Personal Finance Dashboard")
st.markdown("Track your spending, bills, and investments in one place.")

# --- Page content ---
if page == "Grocery Habits":
    st.header("🛒 Grocery Habits")
    st.markdown("Analyze your grocery spending trends, preferred stores, and monthly summaries.")
    try:
        grocery_dash.app(conn)
    except Exception as e:
        st.error(f"Error loading Grocery Habits: {e}")

elif page == "Bill History":
    st.header("💳 Bill History")
    st.markdown("Monitor your bills, payments, and spending trends over time.")
    try:
        bill_dash.app(conn)
    except Exception as e:
        st.error(f"Error loading Bill History: {e}")

elif page == "Investment Overview":
    st.header("📈 Investment Overview")
    st.markdown("Track your ETFs, stocks, and investment performance.")
    try:
        investment_dash.app(conn)
    except Exception as e:
        st.error(f"Error loading Investment Overview: {e}")