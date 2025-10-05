import streamlit as st
import pandas as pd
import numpy as np
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
from finance_dash import conn

def app(conn):
    st.title("📊 Investments")
