import pandas as pd
import sqlalchemy as sa

# 1. Update your Excel file path here
EXCEL_FILE_PATH = "Online Retail.xlsx" 

# Database Connection URL
DATABASE_URL = "postgresql://postgres:NeuralRetailPassword2026@localhost:5432/neural_retail_db"

def load_excel_to_db():
    try:
        print(f"Reading Excel file: {EXCEL_FILE_PATH}...")
        df = pd.read_excel(EXCEL_FILE_PATH)
        print(f"Loaded {len(df)} rows from Excel.")

        # Clean column names
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

        # Engine creation
        engine = sa.create_engine(DATABASE_URL)

        # Write to PostgreSQL 'transactions' table
        df.to_sql("transactions", engine, if_exists="replace", index=False)
        print("✅ Real Excel dataset successfully loaded into PostgreSQL 'transactions' table!")

    except Exception as e:
        print(f"❌ Error loading Excel dataset: {e}")

if __name__ == "__main__":
    load_excel_to_db()