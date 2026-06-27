import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import LabelEncoder
from pathlib import Path
import joblib

BASE = Path("/Users/manoharazalki/F1-Analytics")
DATASET = BASE / "data" / "ml" / "f1_driver_race.parquet"
MODEL_OUTPUT = BASE / "ml" / "models" / "f1_winner_model.pkl"

mlflow.set_tracking_uri("sqlite:///mlflow/mlflow.db")
mlflow.set_experiment("F1-Winner-Prediction")

def load_dataset():
    return pd.read_parquet(DATASET)

def encode_column(df, col):
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    return df

def train_model():
    df = load_dataset()

    # Encode categorical columns
    df = encode_column(df, "circuit_id")
    df = encode_column(df, "driver_nationality")
    df = encode_column(df, "constructor_nationality")

    # Final feature list
    features = [
        "grid_position",
        "season",
        "round",
        "points",
        "circuit_id",
        "driver_nationality",
        "constructor_nationality"
    ]

    X = df[features]
    y = df["is_winner"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    with mlflow.start_run():
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=42
        )

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        mlflow.log_param("n_estimators", 200)
        mlflow.log_param("max_depth", 10)
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_score", f1)

        mlflow.sklearn.log_model(model, "model")

        Path(MODEL_OUTPUT).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, MODEL_OUTPUT)

        print(f"Model saved to {MODEL_OUTPUT}")
        print(f"Accuracy: {acc}, F1 Score: {f1}")

if __name__ == "__main__":
    train_model()
