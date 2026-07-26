import pandas as pd
import numpy as np
import sqlalchemy as sa
import xgboost as xgb

DATABASE_URL = "postgresql://postgres:NeuralRetailPassword2026@localhost:5432/neural_retail_db"

def run_customer_analytics():
    print("🔄 Connecting to DB for Fast Customer Analytics...")
    engine = sa.create_engine(DATABASE_URL)
    
    # Generate Synthetic Customer Cohort Data instantly
    np.random.seed(42)
    n_customers = 200
    
    recency = np.random.randint(1, 180, size=n_customers)
    frequency = np.random.randint(1, 50, size=n_customers)
    monetary = np.random.uniform(50.0, 5000.0, size=n_customers)
    
    cust_df = pd.DataFrame({
        'customer_id': [f"CUST_{1000+i}" for i in range(n_customers)],
        'recency_days': recency,
        'frequency': frequency,
        'monetary_value': monetary,
        'avg_basket_size': np.random.randint(1, 15, size=n_customers)
    })
    
    # Churn Label
    cust_df['is_churned'] = (cust_df['recency_days'] > 90).astype(int)
    
    # Fast Segment Assignment
    conditions = [
        (cust_df['monetary_value'] > 3000) & (cust_df['recency_days'] < 60),
        (cust_df['frequency'] > 25) & (cust_df['recency_days'] < 90),
        (cust_df['recency_days'] >= 90) & (cust_df['recency_days'] < 140),
        (cust_df['recency_days'] >= 140)
    ]
    segment_names = ["VIP / Champions", "Loyal Regulars", "At-Risk Customers", "Hibernating / Lost"]
    cust_df['segment_name'] = np.select(conditions, segment_names, default="Loyal Regulars")
    
    # Train Fast XGBoost Model
    X = cust_df[['recency_days', 'frequency', 'monetary_value', 'avg_basket_size']]
    y = cust_df['is_churned']
    
    model = xgb.XGBClassifier(n_estimators=10, max_depth=2, random_state=42)
    model.fit(X, y)
    
    cust_df['churn_probability'] = np.round(model.predict_proba(X)[:, 1], 2)
    cust_df['risk_level'] = pd.cut(cust_df['churn_probability'], bins=[-0.1, 0.3, 0.7, 1.0], labels=['Low', 'Medium', 'High'])
    
    # Save to Postgres DB
    cust_df.to_sql('customer_analytics', engine, if_exists='replace', index=False)
    print("✅ Customer Analytics DB update COMPLETE!")

if __name__ == "__main__":
    run_customer_analytics()