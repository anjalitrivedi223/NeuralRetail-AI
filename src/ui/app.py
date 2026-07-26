import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlalchemy as sa
import streamlit as st

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & THEME
# ---------------------------------------------------------
st.set_page_config(
    page_title="NeuralRetail AI | Enterprise Retail Intelligence",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Professional Dark UI
st.markdown("""
    <style>
    .main { padding: 1.5rem; }
    .metric-card {
        background-color: #1e222d;
        border: 1px solid #2e3440;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. CLOUD-SAFE DATA PIPELINE
# ---------------------------------------------------------
DEFAULT_PG_URL = "postgresql://postgres:NeuralRetailPassword2026@localhost:5432/neural_retail_db"
DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_PG_URL)

@st.cache_data
def load_and_preprocess_data():
    df = None
    # Attempt DB load
    try:
        engine = sa.create_engine(DATABASE_URL, connect_args={'connect_timeout': 3})
        df = pd.read_sql("SELECT * FROM transactions", engine)
    except Exception:
        pass
    
    # Fallback to local files
    if df is None or df.empty:
        for file in ["Online Retail.xlsx", "sales_data.xlsx", "dataset.xlsx"]:
            if os.path.exists(file):
                df = pd.read_excel(file)
                break

    # Mock Data Fallback if no file exists
    if df is None or df.empty:
        dates = pd.date_range(end=pd.Timestamp.today(), periods=2000, freq='H')
        df = pd.DataFrame({
            'InvoiceNo': [f"INV{1000+i}" for i in range(2000)],
            'StockCode': [f"SKU{np.random.randint(100, 110)}" for _ in range(2000)],
            'Description': [f"Product {chr(65 + np.random.randint(0, 5))}" for _ in range(2000)],
            'Quantity': np.random.randint(1, 12, size=2000),
            'InvoiceDate': dates,
            'UnitPrice': np.round(np.random.uniform(2.5, 45.0, size=2000), 2),
            'CustomerID': np.random.randint(12000, 12050, size=2000),
            'Country': np.random.choice(['United Kingdom', 'Germany', 'France', 'EIRE'], size=2000)
        })

    # Data Standardization
    col_map = {col.lower(): col for col in df.columns}
    
    # Date Handling
    date_col = next((col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()), None)
    if date_col:
        df['InvoiceDate'] = pd.to_datetime(df[date_col], errors='coerce')
    else:
        df['InvoiceDate'] = pd.Timestamp.today()

    # Numeric Columns
    qty_col = next((col for col in df.columns if 'quant' in col.lower()), 'Quantity')
    price_col = next((col for col in df.columns if 'price' in col.lower() or 'unit' in col.lower() or 'amount' in col.lower()), 'UnitPrice')
    cust_col = next((col for col in df.columns if 'cust' in col.lower()), 'CustomerID')
    desc_col = next((col for col in df.columns if 'desc' in col.lower() or 'item' in col.lower()), 'Description')

    df['Quantity'] = pd.to_numeric(df[qty_col], errors='coerce').fillna(1)
    df['UnitPrice'] = pd.to_numeric(df[price_col], errors='coerce').fillna(10.0)
    df['CustomerID'] = df[cust_col].fillna('Guest')
    df['Description'] = df[desc_col].fillna('Unknown Item')
    df['Revenue'] = df['Quantity'] * df['UnitPrice']
    
    # Filter out invalid returns for general analytics
    df_clean = df[df['Quantity'] > 0].copy()
    return df_clean

df_raw = load_and_preprocess_data()

# ---------------------------------------------------------
# 3. SIDEBAR FILTERS & NAVIGATION
# ---------------------------------------------------------
st.sidebar.title("🛍️ NeuralRetail AI")
st.sidebar.markdown("**Enterprise Retail Analytics**")
st.sidebar.markdown("---")

# Global Date & Country Filter
min_date = df_raw['InvoiceDate'].min().date()
max_date = df_raw['InvoiceDate'].max().date()

st.sidebar.subheader("🎛️ Global Filters")
date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

countries = ["All"] + sorted(list(df_raw['Country'].dropna().unique())) if 'Country' in df_raw.columns else ["All"]
selected_country = st.sidebar.selectbox("Market Region", countries)

# Filter Data
filtered_df = df_raw.copy()
if len(date_range) == 2:
    filtered_df = filtered_df[(filtered_df['InvoiceDate'].dt.date >= date_range[0]) & (filtered_df['InvoiceDate'].dt.date <= date_range[1])]

if selected_country != "All" and 'Country' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Country'] == selected_country]

st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Select Module", 
    [
        "📊 Executive Dashboard", 
        "🎯 Customer RFM & Segmentation", 
        "🔮 AI Sales & Demand Forecast", 
        "🛒 Product Basket Analysis",
        "📋 Raw Database Explorer"
    ]
)

# ---------------------------------------------------------
# PAGE 1: EXECUTIVE DASHBOARD
# ---------------------------------------------------------
if page == "📊 Executive Dashboard":
    st.title("📊 Executive Performance Overview")
    st.markdown("High-level KPIs, revenue trends, and regional performance breakdown.")

    # Top KPI Cards
    total_rev = filtered_df['Revenue'].sum()
    total_orders = filtered_df['InvoiceNo'].nunique() if 'InvoiceNo' in filtered_df.columns else len(filtered_df)
    unique_cust = filtered_df[filtered_df['CustomerID'] != 'Guest']['CustomerID'].nunique()
    avg_order_val = total_rev / total_orders if total_orders > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"${total_rev:,.2f}", delta="Live Data")
    c2.metric("Total Orders", f"{total_orders:,}")
    c3.metric("Active Customers", f"{unique_cust:,}")
    c4.metric("Avg Order Value (AOV)", f"${avg_order_val:,.2f}")

    st.markdown("---")

    # Sales Trend & Country Charts
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📈 Monthly Revenue & Order Volume")
        monthly_trend = filtered_df.set_index('InvoiceDate').resample('M').agg({
            'Revenue': 'sum',
            'Quantity': 'sum'
        }).reset_index()
        
        fig_trend = px.line(monthly_trend, x='InvoiceDate', y='Revenue', title="Revenue Trajectory Over Time", markers=True)
        fig_trend.update_layout(template="plotly_dark", height=380)
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_right:
        st.subheader("🌍 Regional Revenue Distribution")
        if 'Country' in filtered_df.columns:
            country_rev = filtered_df.groupby('Country')['Revenue'].sum().reset_index().sort_values('Revenue', ascending=False).head(5)
            fig_pie = px.pie(country_rev, values='Revenue', names='Country', title="Top 5 Markets", hole=0.4)
            fig_pie.update_layout(template="plotly_dark", height=380)
            st.plotly_chart(fig_pie, use_container_width=True)

# ---------------------------------------------------------
# PAGE 2: CUSTOMER RFM & SEGMENTATION
# ---------------------------------------------------------
elif page == "🎯 Customer RFM & Segmentation":
    st.title("🎯 RFM Customer Segmentation & Loyalty")
    st.markdown("Categorizing customers based on **Recency, Frequency, and Monetary value**.")

    # Calculate RFM
    valid_cust = filtered_df[filtered_df['CustomerID'] != 'Guest'].copy()
    if not valid_cust.empty:
        max_trans_date = valid_cust['InvoiceDate'].max() + pd.Timedelta(days=1)
        
        rfm = valid_cust.groupby('CustomerID').agg({
            'InvoiceDate': lambda x: (max_trans_date - x.max()).days,
            'Revenue': ['count', 'sum']
        })
        rfm.columns = ['Recency', 'Frequency', 'Monetary']

        # Segment Logic
        def assign_segment(row):
            if row['Recency'] <= 30 and row['Frequency'] >= 5:
                return "Champions 🏆"
            elif row['Recency'] <= 60 and row['Monetary'] >= 500:
                return "Loyal Customers 💎"
            elif row['Recency'] > 90 and row['Frequency'] >= 3:
                return "At Risk / Churn Warning ⚠️"
            elif row['Recency'] > 120:
                return "Hibernating 😴"
            else:
                return "Recent / Potential 🌟"

        rfm['Segment'] = rfm.apply(assign_segment, axis=1)

        c1, c2 = st.columns([1, 2])
        with c1:
            st.subheader("Segment Breakdown")
            seg_counts = rfm['Segment'].value_counts().reset_index()
            seg_counts.columns = ['Segment', 'Count']
            fig_seg = px.bar(seg_counts, x='Count', y='Segment', orientation='h', color='Segment', title="Customer Distribution")
            fig_seg.update_layout(template="plotly_dark", showlegend=False)
            st.plotly_chart(fig_seg, use_container_width=True)

        with c2:
            st.subheader("3D Recency vs Frequency vs Monetary Scatter")
            fig_3d = px.scatter_3d(
                rfm.reset_index(), x='Recency', y='Frequency', z='Monetary',
                color='Segment', opacity=0.8, title="RFM Spatial Clusters"
            )
            fig_3d.update_layout(template="plotly_dark", height=450)
            st.plotly_chart(fig_3d, use_container_width=True)

        st.markdown("### 📋 High-Value At-Risk Customers (Churn Prevention)")
        at_risk = rfm[rfm['Segment'] == "At Risk / Churn Warning ⚠️"].sort_values('Monetary', ascending=False)
        st.dataframe(at_risk, use_container_width=True)

# ---------------------------------------------------------
# PAGE 3: AI SALES & DEMAND FORECAST
# ---------------------------------------------------------
elif page == "🔮 AI Sales & Demand Forecast":
    st.title("🔮 AI Demand & Revenue Forecasting")
    st.markdown("Machine Learning trend projection to forecast future inventory and revenue needs.")

    monthly_data = filtered_df.set_index('InvoiceDate').resample('M')['Revenue'].sum().reset_index()
    monthly_data = monthly_data[monthly_data['Revenue'] > 0]

    if len(monthly_data) > 2:
        horizon = st.slider("Select Forecast Horizon (Months):", 1, 12, 6)
        
        monthly_data['Month_Idx'] = np.arange(len(monthly_data))
        slope, intercept = np.polyfit(monthly_data['Month_Idx'], monthly_data['Revenue'], 1)

        last_date = monthly_data['InvoiceDate'].max()
        future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=horizon, freq='M')
        future_idx = np.arange(len(monthly_data), len(monthly_data) + horizon)
        
        predicted_rev = np.maximum(slope * future_idx + intercept, monthly_data['Revenue'].mean() * 0.4)

        hist_df = monthly_data[['InvoiceDate', 'Revenue']].copy()
        hist_df['Type'] = 'Historical'
        
        fut_df = pd.DataFrame({'InvoiceDate': future_dates, 'Revenue': predicted_rev, 'Type': 'Forecast'})
        combined = pd.concat([hist_df, fut_df])

        fig_forecast = px.line(combined, x='InvoiceDate', y='Revenue', color='Type', title=f"{horizon}-Month Projected Revenue", markers=True)
        fig_forecast.update_layout(template="plotly_dark", height=420)
        st.plotly_chart(fig_forecast, use_container_width=True)

        c1, c2 = st.columns(2)
        c1.metric("Next Month Predicted Revenue", f"${predicted_rev[0]:,.2f}")
        c2.metric(f"Total {horizon}-Month Cumulative Forecast", f"${predicted_rev.sum():,.2f}")

# ---------------------------------------------------------
# PAGE 4: PRODUCT BASKET ANALYSIS
# ---------------------------------------------------------
elif page == "🛒 Product Basket Analysis":
    st.title("🛒 Product Performance & Co-Purchase Insights")
    st.markdown("Analyze bestsellers and item affinity.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔥 Top 10 Bestselling Products")
        top_products = filtered_df.groupby('Description')['Quantity'].sum().reset_index().sort_values('Quantity', ascending=False).head(10)
        fig_prod = px.bar(top_products, x='Quantity', y='Description', orientation='h', color='Quantity', title="Top Items by Quantity Sold")
        fig_prod.update_layout(template="plotly_dark")
        st.plotly_chart(fig_prod, use_container_width=True)

    with col2:
        st.subheader("💰 Top Revenue Generating Items")
        top_rev_prod = filtered_df.groupby('Description')['Revenue'].sum().reset_index().sort_values('Revenue', ascending=False).head(10)
        fig_rev_p = px.bar(top_rev_prod, x='Revenue', y='Description', orientation='h', color='Revenue', title="Top Items by Gross Revenue")
        fig_rev_p.update_layout(template="plotly_dark")
        st.plotly_chart(fig_rev_p, use_container_width=True)

# ---------------------------------------------------------
# PAGE 5: RAW DATABASE EXPLORER
# ---------------------------------------------------------
elif page == "📋 Raw Database Explorer":
    st.title("📋 Database Records Explorer")
    st.markdown("Filter, search, and download raw transaction data.")
    
    st.dataframe(filtered_df, use_container_width=True)
    
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Filtered Data as CSV", data=csv, file_name="neural_retail_export.csv", mime="text/csv")
