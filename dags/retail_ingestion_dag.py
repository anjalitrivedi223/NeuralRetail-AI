from datetime import datetime, timedelta
import random
import pandas as pd
from sqlalchemy import create_engine
from airflow import DAG
from airflow.operators.python import PythonOperator

# 1. Database Connection String (Direct inside docker network)
DB_URL = "postgresql+psycopg2://postgres:NeuralRetailPassword2026@postgres_db:5432/neural_retail_db"

def auto_ingest_mock_sales():
    """Generates daily mock retail sales data and appends it to PostgreSQL"""
    engine = create_engine(DB_URL)
    
    categories = ["Electronics", "Apparel", "Home & Kitchen", "Beauty & Health", "Sports"]
    current_date = datetime.now().date()
    
    # Generate 5 random entries for the day
    mock_data = []
    for _ in range(5):
        mock_data.append({
            "date": current_date,
            "category": random.choice(categories),
            "total_revenue": round(random.uniform(200.0, 2500.0), 2),
            "total_items": random.randint(5, 50),
            "total_orders": random.randint(1, 15)
        })
    
    df = pd.DataFrame(mock_data)
    
    # Append directly to your existing get_business_metrics table structure
    df.to_sql("business_metrics", engine, if_exists="append", index=False)
    print(f" Successfully ingested {len(df)} automated retail rows for {current_date}!")

# 2. Define the DAG Structure
default_args = {
    "owner": "Anjali",
    "depends_on_past": False,
    "start_date": datetime(2026, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "neural_retail_daily_ingestion",
    default_args=default_args,
    description="Automated Daily Retail Data Ingestion Pipeline",
    schedule_interval="@daily",  # Run once every day at midnight
    catchup=False
) as dag:

    ingest_task = PythonOperator(
        task_id="auto_generate_and_ingest_sales",
        python_callable=auto_ingest_mock_sales
    )

    ingest_task