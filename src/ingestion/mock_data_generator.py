import os
import random
import pandas as pd
from datetime import datetime, timedelta

def generate_mock_data(num_rows=1000, output_path="src/ingestion/data/raw_transactions.csv"):
    print("⏳ Generating synthetic retail data...")
    
    # Folder structure check karna
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Lists for random choice
    products = ['Laptop', 'Smartphone', 'Wireless Headphones', 'Smart Watch', 'Tablet']
    categories = ['Electronics', 'Electronics', 'Accessories', 'Electronics', 'Electronics']
    prod_cat_map = dict(zip(products, categories))
    prod_price_map = {'Laptop': 1200, 'Smartphone': 800, 'Wireless Headphones': 150, 'Smart Watch': 250, 'Tablet': 450}
    
    data = []
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(num_rows):
        transaction_id = f"TXN_{10000 + i}"
        customer_id = f"CUST_{random.randint(1, 150)}" # 150 unique customers
        product = random.choice(products)
        category = prod_cat_map[product]
        base_price = prod_price_map[product]
        
        # Adding slight variation in price (discounts/tax)
        price = round(base_price * random.uniform(0.9, 1.1), 2)
        quantity = random.randint(1, 3)
        total_amount = round(price * quantity, 2)
        
        # Random dates over the last 30 days
        timestamp = start_date + timedelta(hours=random.randint(0, 720))
        
        data.append([transaction_id, customer_id, timestamp, product, category, quantity, price, total_amount])
    
    # Creating DataFrame
    columns = ['transaction_id', 'customer_id', 'timestamp', 'product_name', 'category', 'quantity', 'price', 'total_amount']
    df = pd.DataFrame(data, columns=columns)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"✅ Successfully generated and saved {num_rows} rows to: {output_path}")

if __name__ == "__main__":
    generate_mock_data()