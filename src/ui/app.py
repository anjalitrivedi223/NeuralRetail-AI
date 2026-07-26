import os
import pandas as pd
import numpy as np
import sqlalchemy as sa
import streamlit as st

# Database Connection String
DEFAULT_PG_URL = "postgresql://postgres:NeuralRetailPassword2026@localhost:5432/neural_retail_db"
DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_PG_URL)

@st.cache_data
def load_data():
    try:
        # Try connecting to PostgreSQL DB first
        engine = sa.create_engine(DATABASE_URL, connect_args={'connect_timeout': 3})
        df = pd.read_sql("SELECT * FROM transactions", engine)
        return df
    except Exception as e:
        # Fallback for Streamlit Cloud deployment if local DB is unreachable
        st.warning("⚠️ Cloud Mode: Local PostgreSQL database unreachable. Loading dataset directly from Excel/CSV file.")
        
        # Try reading local dataset file directly
        file_path = "sales_data.xlsx" # Apne Excel file ka exact naam yahan check kar lein
        if os.path.exists(file_path):
            return pd.read_excel(file_path)
        elif os.path.exists("Online Retail.xlsx"):
            return pd.read_excel("Online Retail.xlsx")
        else:
            # Emergency Mock Data if no dataset file found
            st.info("Generating demonstration dataset for UI...")
            dates = pd.date_range(end=pd.Timestamp.today(), periods=1000, freq='D')
            return pd.DataFrame({
                'transaction_id': range(1, 1001),
                'customer_id': np.random.randint(100, 200, size=1000),
                'amount': np.random.uniform(10, 500, size=1000),
                'transaction_date': dates
            })

# Load the dataset
df_raw = load_data()
# PAGE 5: DATA EXPLORER
elif page == "📋 Raw Data Explorer":
    st.header("📋 Database Transactions Explorer")
    st.dataframe(df_raw.head(100), use_container_width=True)
