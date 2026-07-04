# Personal Finance Dashboard

This project contains a Streamlit-based personal finance dashboard for viewing grocery spending, bill history, and investment overview in one place.

## How to start the app

1. Open a terminal in the repository root:
   ```powershell
   cd "..\Personal Finance"
   ```

2. Install the required Python packages:
   ```powershell
   python -m pip install streamlit pandas numpy psycopg2-binary plotly
   ```

3. Start the dashboard:
   ```powershell
   streamlit run Pay\finance_dash.py
   ```
   If Streamlit is not recognized, use:
   ```powershell
   python -m streamlit run Pay\finance_dash.py
   ```

4. Open the local URL shown in the terminal, usually:
   ```text
   http://localhost:8501
   ```

## What the app includes

- Grocery Habits dashboard
- Bill History dashboard
- Investment Overview dashboard

## Notes

- The app connects to a PostgreSQL database configured in the dashboard script.
- To stop the app, press Ctrl+C in the terminal.

