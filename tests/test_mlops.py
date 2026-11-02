"""
Tests unitaires, contrôles de qualité des données et critères d'acceptation des modèles
(Conformément aux recommandations de la Section 12 — Extension CI MLOps).
"""

import json
import os
import joblib
import pandas as pd
import yaml


def test_iris_data_quality():
    """Contrôle de qualité du dataset Iris versionné par DVC."""
    assert os.path.exists("data/raw/iris.csv"), "data/raw/iris.csv introuvable (exécuter dvc pull)"
    df = pd.read_csv("data/raw/iris.csv")
    assert len(df) == 150, f"Attendu 150 lignes, obtenu {len(df)}"
    assert df.shape[1] == 5, f"Attendu 5 colonnes, obtenu {df.shape[1]}"
    assert df.isnull().sum().sum() == 0, "Présence de valeurs manquantes dans iris.csv"
    assert set(df["target"].unique()) == {0, 1, 2}, "Classes cibles inattendues dans iris.csv"


def test_wine_data_quality():
    """Contrôle de qualité du second dataset Wine versionné par DVC (TP 2)."""
    assert os.path.exists("data/raw/wine.csv"), "data/raw/wine.csv introuvable (exécuter dvc pull)"
    df = pd.read_csv("data/raw/wine.csv")
    assert len(df) == 178, f"Attendu 178 lignes restaurées, obtenu {len(df)}"
    assert df.isnull().sum().sum() == 0, "Présence de valeurs manquantes dans wine.csv"


def test_pipeline_configuration():
    """Vérifie la cohérence de params.yaml, dvc.yaml et dvc.lock."""
    with open("params.yaml", "r", encoding="utf-8") as f:
        params = yaml.safe_load(f)
    assert "train" in params and "knn" in params
    assert 0 < params["train"]["test_size"] < 1
    assert params["train"]["n_estimators"] >= 10
    assert params["knn"]["n_neighbors"] >= 1
    assert os.path.exists("dvc.yaml") and os.path.exists("dvc.lock")


def test_models_inference_and_acceptance():
    """Vérifie le chargement des modèles et les seuils d'acceptation (accuracy & F1 >= 0.85)."""
    df = pd.read_csv("data/raw/iris.csv")
    sample_X = df.drop("target", axis=1).iloc[:5]

    for model_path, metrics_path in [
        ("models/model.pkl", "reports/metrics.json"),
        ("models/knn_model.pkl", "reports/metrics_knn.json"),
    ]:
        assert os.path.exists(model_path), f"Modèle manquant : {model_path}"
        model = joblib.load(model_path)
        preds = model.predict(sample_X)
        assert len(preds) == 5
        assert set(preds).issubset({0, 1, 2})

        assert os.path.exists(metrics_path), f"Fichier métriques manquant : {metrics_path}"
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)
        for key in ("accuracy", "precision", "recall", "f1_score"):
            assert key in metrics, f"Métrique {key} absente de {metrics_path}"
            assert metrics[key] >= 0.85, f"{key}={metrics[key]:.4f} sous le seuil d'acceptation (0.85)"
