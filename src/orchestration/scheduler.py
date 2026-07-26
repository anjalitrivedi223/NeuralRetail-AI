import time
import random
import schedule
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

# Database connection configuration
DB_URL = "postgresql+psycopg2://postgres:NeuralRetailPassword2026@localhost:5432/neural_retail_db"

def run_automated_ingestion():
    print(f"\n[🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Core Pipeline Triggered...")
    try:
        engine = create_engine(DB_URL)
        categories = ["Electronics", "Apparel", "Home & Kitchen", "Beauty & Health", "Sports"]
        current_date = datetime.now().date()
        
        # 1. Mock Automated Row Generation
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
        
        # 2. Ingest into the database table
        df.to_sql("business_metrics", engine, if_exists="append", index=False)
        print(f"✅ Success: Ingested {len(df)} automated sales rows into 'business_metrics' table!")
        
    except Exception as e:
        print(f"❌ Pipeline Error: {str(e)}")

# Orchestration Job Rules
print("🚀 NeuralRetail Light-weight Orchestrator Active...")
print("📅 Task scheduled: Ingest new sales data every 10 seconds for real-time testing loop.")

# Real-time simulation framework
schedule.every(10).seconds.do(run_automated_ingestion)

if __name__ == "__main__":
    # Ingest immediately on first run
    run_automated_ingestion()
    
    # Keep running the scheduler loop
    while True:
        schedule.run_pending()
        time.convert_clocks = time.sleep(1)