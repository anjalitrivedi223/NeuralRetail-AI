import pandas as pd
from sqlalchemy import create_engine
import os
import sys

# Adding src to path for config loader
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.config_loader import ConfigLoader

def perform_eda():
    print("📊 Fetching data from PostgreSQL for EDA...")
    
    # 1. Database Connection
    config = ConfigLoader()
    db_user = config.get("database.user")
    db_password = config.get("database.password")
    db_host = config.get("database.host")
    db_port = config.get("database.port")
    db_name = config.get("database.name")
    
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(db_url)
    
    # 2. Read from Database SQL
    query = "SELECT * FROM transactions"
    df = pd.read_sql(query, con=engine)
    
    print(f"✅ Data loaded successfully! Shape: {df.shape[0]} rows, {df.shape[1]} columns.\n")
    
    # 3. Business Insights
    print("====== 📈 BUSINESS INSIGHTS ======")
    
    # Insight A: Total Revenue
    total_sales = df['total_amount'].sum()
    print(f"💰 Total Revenue Generated: ${total_sales:,.2f}")
    
    # Insight B: Best Selling Products
    print("\n📦 Top 3 Best Selling Products (by Quantity):")
    top_products = df.groupby('product_name')['quantity'].sum().sort_values(ascending=False).head(3)
    for prod, qty in top_products.items():
        print(f"   - {prod}: {qty} units sold")
        
    # Insight C: Category Performance
    print("\n🏢 Revenue by Product Category:")
    cat_sales = df.groupby('category')['total_amount'].sum().sort_values(ascending=False)
    for cat, revenue in cat_sales.items():
        print(f"   - {cat}: ${revenue:,.2f}")
    print("==================================")

if __name__ == "__main__":
    perform_eda()