"""Generate synthetic dataset and train RandomForestRegressor.
Saves model to query_model.pkl and dataset to dataset/query_dataset.csv
"""
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
from config import PROJECT_ROOT, MODEL_PATH


def generate_synthetic(n=1200, random_state=42):
    rng = np.random.RandomState(random_state)
    query_length = rng.randint(20, 800, size=n)
    joins = rng.poisson(1.0, size=n)
    joins = np.clip(joins, 0, 6)
    conditions = rng.poisson(2.0, size=n)
    conditions = np.clip(conditions, 0, 10)
    group_by_count = rng.poisson(0.5, size=n)
    order_by_count = rng.poisson(0.5, size=n)

    # Base execution time (ms) given features + noise
    execution_time = (
        5 + query_length * 0.5 + joins * 50 + conditions * 20 + group_by_count * 40 + order_by_count * 30
    )
    execution_time = execution_time + rng.normal(0, execution_time * 0.05)

    df = pd.DataFrame({
        "query_length": query_length,
        "joins": joins,
        "conditions": conditions,
        "group_by_count": group_by_count,
        "order_by_count": order_by_count,
        "execution_time": execution_time,
    })
    return df


def train_and_save(df, model_path=MODEL_PATH):
    X = df[["query_length", "joins", "conditions", "group_by_count", "order_by_count"]]
    y = df["execution_time"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    print(f"Trained RandomForestRegressor. Test MSE: {mse:.2f}")
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")


def main():
    dataset_path = os.path.join(PROJECT_ROOT, "dataset")
    os.makedirs(dataset_path, exist_ok=True)
    df = generate_synthetic(n=1200)
    csv_path = os.path.join(dataset_path, "query_dataset.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved synthetic dataset to {csv_path}")
    train_and_save(df)


if __name__ == "__main__":
    main()
