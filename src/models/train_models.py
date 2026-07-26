import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
import mlflow
import mlflow.sklearn

# Adding src to path for config loader
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.config_loader import ConfigLoader

def train_sales_forecaster():
    print("🧠 Initializing Day 3 Model Training & MLflow Tracking...")
    
    # 1. Load configurations & setup MLflow connection
    config = ConfigLoader()
    db_user = config.get("database.user")
    db_password = config.get("database.password")
    db_host = config.get("database.host")
    db_port = config.get("database.port")
    db_name = config.get("database.name")
    
    tracking_uri = config.get("mlflow.tracking_uri")
    experiment_name = config.get("mlflow.experiment_name")
    
    # MLflow ko batana ki hamara server kahan chal raha hai
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
    
    # 2. Fetch Data from PostgreSQL
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(db_url)
    df = pd.read_sql("SELECT quantity, price, total_amount FROM transactions", con=engine)
    
    # 3. Features and Target Definition
    X = df[['quantity', 'price']]  # Inputs
    y = df['total_amount']          # What we want to predict
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. MLflow Run Shuru Karte Hain
    with mlflow.start_run(run_name="Baseline_Linear_Regression"):
        print("🚀 Training Model and Logging to MLflow Server...")
        
        # Model Training
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Predictions & Evaluation
        predictions = model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        print(f"📊 Evaluation Metrics -> MAE: {mae:.2f}, R2 Score: {r2:.2f}")
        
        # Hyperparameters aur Metrics ko MLflow Dashboard par bhejna
        mlflow.log_param("model_type", "LinearRegression")
        mlflow.log_param("test_size", 0.2)
        mlflow.log_metric("MAE", mae)
        mlflow.log_metric("R2_Score", r2)
        
        # Saath hi poore trained model build ko save karna (Artifact Logging)
        import skops.io as sio
        sio.dump(model, "sales_forecaster_model.skops")
        mlflow.log_artifact("sales_forecaster_model.skops")
        print("🎯 Success! Parameters, metrics, and model artifact logged to MLflow Dashboard.")

if __name__ == "__main__":
    train_sales_forecaster()