import pandas as pd
from sqlalchemy import create_engine
import os
import sys

# Adding src to path so we can import our config loader
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.config_loader import ConfigLoader

def run_ingestion_pipeline():
    print("🔄 Starting Day 2 Ingestion Pipeline...")
    
    # 1. Load Configurations
    config = ConfigLoader()
    raw_data_path = config.get("data.raw_path")
    processed_data_path = config.get("data.processed_path")
    
    db_user = config.get("database.user")
    db_password = config.get("database.password")
    db_host = config.get("database.host")
    db_port = config.get("database.port")
    db_name = config.get("database.name")

    # 2. Read Raw Data
    if not os.path.exists(raw_data_path):
        print(f"❌ Error: Raw data file not found at {raw_data_path}. Run mock_data_generator.py first!")
        return

    df = pd.read_csv(raw_data_path)
    print(f"📋 Read {len(df)} rows from raw CSV.")

    # 3. Data Cleaning / Processing Step
    print("🧹 Cleaning data (Handling dates and formatting)...")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Feature Engineering snippet: Total tax calculation as a sample transformation
    df['tax_amount'] = round(df['total_amount'] * 0.05, 2) 

    # 4. Save to Optimized Parquet format locally
    os.makedirs(os.path.dirname(processed_data_path), exist_ok=True)
    df.to_parquet(processed_data_path, index=False)
    print(f"💾 Optimized data saved locally as Parquet: {processed_data_path}")

    # 5. Ingest into Docker PostgreSQL Database
    print("🚀 Pushing data to Docker PostgreSQL container...")
    # Creating connection string
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(db_url)

    # Write data to a table named 'transactions'
    df.to_sql('transactions', con=engine, if_exists='replace', index=False)
    print("🎯 Success! Data successfully written to PostgreSQL table 'transactions'.")

if __name__ == "__main__":
    run_ingestion_pipeline()