# Atelier Pratique MLOps — Intégration de Git + DVC + MLflow

**Auteur :** Mohamed Amine BELGUEROUANI  
**Dépôt GitHub :** [https://github.com/anakin-skyguy/atelier-mlops](https://github.com/anakin-skyguy/atelier-mlops)  
**Technologies :** Python 3.12 • Scikit-learn • Git & GitHub • DVC 3.67 • MLflow 3.17 (SQLite) • Pytest • GitHub Actions

---

## 1. Objectif et Architecture MLOps

Ce projet implémente un workflow MLOps complet, versionné, traçable et reproductible autour de la classification du dataset **Iris** (et du dataset **Wine** pour les manipulations avancées de versioning de données) :

| Outil | Responsabilité dans le workflow |
| :--- | :--- |
| **Git & GitHub** | Versioning du code source (`src/`, `tests/`), des configurations (`params.yaml`, `dvc.yaml`, `dvc.lock`, `.dvc`), gestion des branches (`main`, `develop`), tags (`v1.0`, `v2.0`, `v3.0`) et CI GitHub Actions. |
| **DVC** | Versioning des datasets (`iris.csv`, `wine.csv`) et des modèles sérialisés (`model.pkl`, `knn_model.pkl`), orchestration du pipeline reproductible (`dvc repro`, `dvc dag`) et stockage distant. |
| **MLflow** | Suivi des expérimentations (`sqlite:///mlflow.db`), journalisation des hyperparamètres, métriques (`accuracy`, `precision`, `recall`, `f1_score`) et artefacts de modèles, comparaison visuelle des runs. |

---

## 2. Structure du Projet

```text
atelier-mlops/
├── .dvc/
│   └── config                        # Configuration des remotes DVC (github HTTPS + storage local)
├── .github/
│   └── workflows/
│       └── mlops.yml                 # Pipeline CI GitHub Actions (dvc pull -> dvc repro -> pytest)
├── data/
│   └── raw/
│       ├── iris.csv.dvc              # Métadonnées DVC du dataset Iris (150 lignes)
│       └── wine.csv.dvc              # Métadonnées DVC du second dataset Wine (178 lignes, TP 2)
├── docs/
│   └── screenshots/                  # Captures haute résolution de l'interface MLflow UI
├── models/                           # Modèles entraînés suivis par DVC (model.pkl, knn_model.pkl)
├── reports/
│   ├── metrics.json                  # Métriques Random Forest suivies par DVC
│   └── metrics_knn.json              # Métriques KNN suivies par DVC
├── scripts/
│   ├── capture_all_screenshots.py    # Capture automatisée 2x Retina (thème clair) de toutes les preuves
│   └── build_compte_rendu.py         # Génération du Compte Rendu officiel PDF (10 pages)
├── src/
│   ├── prepare_data.py               # Génération déterministe de data/raw/iris.csv
│   ├── prepare_wine.py               # Génération déterministe de data/raw/wine.csv (TP 2)
│   ├── train.py                      # Entraînement Random Forest + tracking MLflow
│   └── train_knn.py                  # Entraînement KNN + tracking MLflow (TP 3)
├── tests/
│   └── test_mlops.py                 # Contrôles qualité données, configuration et seuils d'acceptation
├── .gitattributes                    # Normalisation LF inter-plateformes (Windows / Linux)
├── .gitignore                        # Exclusion des caches Python, MLflow DB et binaires DVC
├── dvc.yaml                          # Définition déclarative des stages du pipeline (train, train_knn)
├── dvc.lock                          # Empreintes MD5 exactes des dépendances, paramètres et sorties
├── params.yaml                       # Hyperparamètres centralisés (Random Forest & KNN)
└── requirements.txt                  # Dépendances Python du projet
```

---

## 3. Reproduire le Projet sur n'importe quelle Machine

Grâce au remote DVC HTTPS configuré par défaut (`github` pointant vers le stockage adressé par contenu sur la branche dédiée `dvc-storage`) en complément du remote local d'exercice (`storage` -> `../dvc-storage`), **le projet est reproductible immédiatement depuis un simple `git clone` sur n'importe quelle machine** :

```bash
git clone https://github.com/anakin-skyguy/atelier-mlops.git
cd atelier-mlops
pip install -r requirements.txt

# Récupérer les datasets et modèles versionnés depuis le remote DVC HTTPS
dvc pull

# Vérifier et exécuter le pipeline reproductible
dvc repro
dvc metrics show

# Exécuter les contrôles de qualité des données et tests d'acceptation des modèles
python -m pytest -v

# Visualiser les expérimentations dans MLflow UI
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000 --workers 1
```

Pour restaurer une version antérieure précise (code, hyperparamètres, données et modèle binaire associé) :

```bash
git checkout v1.0
dvc pull
dvc metrics show   # Restaure accuracy = 0.93333 et le RandomForest à 100 arbres (max_depth=5)
```

---

## 4. Résultats et Comparaison des Expérimentations

Découpage stratifié identique pour toutes les expériences : `test_size = 0.2` (120 observations d'entraînement, 30 observations de test), `random_state = 42`.

| Version / Tag | Run MLflow | Modèle & Hyperparamètres | Accuracy | Precision (w) | Recall (w) | F1-Score (w) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **`v1.0`** | `RandomForest_n100_d5` | Random Forest (`n_estimators=100`, `max_depth=5`) | **0.9333** | **0.9333** | **0.9333** | **0.9333** |
| **`v2.0`** | `RandomForest_n200_d8` | Random Forest (`n_estimators=200`, `max_depth=8`) | 0.9000 | 0.9024 | 0.9000 | 0.8997 |
| **`v3.0`** | `KNN_k5` | K-Nearest Neighbors (`n_neighbors=5`) | **1.0000** | **1.0000** | **1.0000** | **1.0000** |

### Analyse critique des résultats
1. **Random Forest (`v1.0` vs `v2.0`) :** Doubler le nombre d'arbres (`100 -> 200`) et augmenter la profondeur maximale (`5 -> 8`) n'améliore pas la généralisation ; l'accuracy recule de `0.9333` (28/30) à `0.9000` (27/30), illustrant un léger surapprentissage sur un petit jeu d'entraînement de 120 lignes.
2. **KNN (`k=5`) :** Le classifieur par plus proches voisins atteint `1.0000` (30/30) sur ce pli de test car les classes d'Iris sont géométriquement bien séparées dans l'espace des 4 variables morphologiques. Toutefois, sur un échantillon de test de 30 individus (où 1 erreur représente `3.33 %`), une validation croisée stratifiée serait requise avant d'affirmer une supériorité statistique générale.

---

## 5. Captures de l'Interface MLflow (`docs/screenshots/`)

| Fichier | Description |
| :--- | :--- |
| `01_github_repository.png` | Dépôt GitHub publié (`main`, `develop`, tags `v1.0`–`v3.0`, 14+ commits) |
| `02_git_branches_tags_log.png` | Vérification CLI Git : remotes, branches, tags annotés et graphe des commits |
| `03_dvc_remotes_and_wine_rollback.png` | Remotes DVC, fichiers `.dvc` et restauration MD5 de `wine.csv` (TP 2) |
| `04_mlflow_runs_table.png` | Tableau des runs `TP_Iris_Classification` en thème clair avec métriques et paramètres |
| `05_mlflow_compare_chart.png` | Graphique en coordonnées parallèles comparant les 3 expérimentations |
| `06_mlflow_compare_table.png` | Tableau comparatif côte à côte (Détails, Paramètres et Métriques) |
| `07_mlflow_run_rf100.png` | Fiche détaillée du run `RandomForest_n100_d5` (`v1.0`) |
| `08_mlflow_run_rf200.png` | Fiche détaillée du run `RandomForest_n200_d8` (`v2.0`) |
| `09_mlflow_run_knn.png` | Fiche détaillée du run `KNN_k5` (`v3.0`) |
| `10_dvc_dag_rollback_pytest.png` | Graphe `dvc dag`, `dvc diff v1.0 v2.0`, rollback `v1.0` et `pytest -v` (4/4 passés) |
| `11_mlflow_artifacts_model_pkl.png` | Onglet Artifacts déplié confirmant l'enregistrement de `model/model.pkl` |

---

## 6. Synthèse des Réponses aux Questions de Réflexion (Section 16)

- **Q15 — Différence entre Git et DVC :** Git versionne le code source et les fichiers texte légers de métadonnées (`.dvc`, `dvc.yaml`, `dvc.lock`), tandis que DVC versionne les datasets volumineux et les binaires de modèles via un cache adressé par empreinte MD5 et un stockage distant (local, S3, Azure, GCS, HTTPS).
- **Q16 — Pourquoi éviter de stocker un dataset volumineux dans Git :** Chaque modification d'un fichier massif alourdit définitivement l'historique `.git`, ralentit les opérations `clone`/`fetch`, se heurte aux quotas des forges (ex. limite de 100 Mo par fichier sur GitHub) et produit des diffs textuels inexploitables sur les binaires.
- **Q17 — Différence entre `dvc add` et `dvc repro` :** `dvc add` place un fichier statique existant (comme un dataset brut) sous suivi DVC en générant un fichier `.dvc`. `dvc repro` orchestre l'exécution du graphe de dépendances défini dans `dvc.yaml`, ne ré-exécutant que les étapes dont le code, les données ou les paramètres ont changé par rapport à `dvc.lock`.
- **Q18 — Rôle de `dvc.lock` :** Véritable « photographie cryptographique » d'une exécution du pipeline, `dvc.lock` fige les empreintes MD5 et tailles exactes de toutes les entrées, les valeurs résolues des hyperparamètres et les empreintes des sorties générées, garantissant une reproductibilité déterministe.
- **Q19 — Comparaison d'expérimentations dans MLflow :** MLflow centralise paramètres, métriques et artefacts de chaque run dans un backend relationnel (`sqlite:///mlflow.db`) et offre un module de comparaison côte à côte (tableaux différentiels, coordonnées parallèles, nuages de points) ainsi qu'une API programmatique (`mlflow.search_runs`).
- **Q20 — Retrouver les données et le modèle d'un commit Git précis :** Exécuter `git checkout <commit_ou_tag>` pour restaurer les pointeurs `.dvc` et `dvc.lock` de cet instant, puis `dvc checkout` (ou `dvc pull` si absent du cache local) pour matérialiser exactement les fichiers de données et le modèle correspondants.
- **Q21 — Importance de la reproductibilité en IA :** Un modèle dépend simultanément du code, des données, des hyperparamètres et de l'aléa statistique (`random_state`). La reproductibilité est indispensable pour l'auditabilité scientifique et réglementaire, le débogage de régressions en production, le retour arrière rapide (*rollback*) et le travail collaboratif fiable.
- **Q22 — Versioning de modèles avec DVC vs suivi avec MLflow :** DVC assure le versioning physique des fichiers binaires produits par le pipeline en les couplant strictement à un commit Git précis (idéal pour `git+dvc checkout` et CI/CD). MLflow assure le suivi expérimental riche (historique de tous les essais exploratoires, graphiques comparatifs, métadonnées d'exécution et cycle de vie dans le Model Registry). Les deux approches se complètent mutuellement.
