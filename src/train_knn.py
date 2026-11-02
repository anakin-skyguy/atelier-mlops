import os
import yaml
import json
import joblib
import mlflow
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score
)

with open("params.yaml", "r", encoding="utf-8") as file:
    all_params = yaml.safe_load(file)

params = {
    "random_state": all_params["train"]["random_state"],
    "test_size": all_params["train"]["test_size"],
    "n_neighbors": all_params["knn"]["n_neighbors"],
}

df = pd.read_csv("data/raw/iris.csv")
X = df.drop("target", axis=1)
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=params["test_size"],
    random_state=params["random_state"], stratify=y
)

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("TP_Iris_Classification")

run_name = f"KNN_k{params['n_neighbors']}"

with mlflow.start_run(run_name=run_name):
    model = KNeighborsClassifier(n_neighbors=params["n_neighbors"])
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(
            y_test, predictions, average="weighted"
        ),
        "recall": recall_score(
            y_test, predictions, average="weighted"
        ),
        "f1_score": f1_score(
            y_test, predictions, average="weighted"
        )
    }

    mlflow.log_param("model", "KNN")
    mlflow.log_params(params)
    mlflow.log_metrics(metrics)

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/knn_model.pkl")
    mlflow.log_artifact("models/knn_model.pkl", artifact_path="model")

    os.makedirs("reports", exist_ok=True)
    with open("reports/metrics_knn.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(metrics, f, indent=4)
        f.write("\n")

    print("Métriques KNN :", metrics)
    print("Modèle KNN entraîné et enregistré.")
