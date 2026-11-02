from sklearn.datasets import load_wine
import pandas as pd
import os

wine = load_wine()
df = pd.DataFrame(wine.data, columns=wine.feature_names)
df["target"] = wine.target

os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/wine.csv", index=False, lineterminator="\n")

print("Dataset Wine généré avec succès")
print("Nombre de lignes :", len(df))
