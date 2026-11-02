"""
Script de génération du compte-rendu professionnel PDF pour l'Atelier MLOps (Git + DVC + MLflow).
Auteur : Mohamed Amine BELGUEROUANI
"""

import os
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class NumberedCanvas(canvas.Canvas):
    """Canvas personnalisé pour numérotation dynamique 'Page X sur Y' et en-tête/pied de page."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#1E3A8A"))
            self.drawString(50, 804, "COMPTE RENDU — ATELIER PRATIQUE MLOPS : GIT + DVC + MLFLOW")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(545, 804, "MOHAMED AMINE BELGUEROUANI")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.75)
            self.line(50, 796, 545, 796)

        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(50, 44, 545, 44)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(50, 31, "MLOps & Industrialisation du Machine Learning — github.com/anakin-skyguy/atelier-mlops")
        self.drawRightString(545, 31, f"Page {self._pageNumber} sur {total_pages}")
        self.restoreState()


def get_scaled_image(path, max_width=485, max_height=255):
    if not os.path.exists(path):
        return None
    with PILImage.open(path) as img:
        w, h = img.size
    aspect = h / w
    target_w = min(w, max_width)
    target_h = target_w * aspect
    if target_h > max_height:
        target_h = max_height
        target_w = target_h / aspect
    return Image(path, width=target_w, height=target_h)


def make_code_box(text, code_style, width=495):
    t = Table([[Preformatted(text.strip(), code_style)]], colWidths=[width])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return t


def styled_table(rows, col_widths, primary_color):
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), primary_color),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return t


def generate_pdf(output_pdf_path, screenshots_dir):
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        leftMargin=50,
        rightMargin=50,
        topMargin=52,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()
    primary = colors.HexColor("#1E3A8A")
    secondary = colors.HexColor("#0284C7")
    dark = colors.HexColor("#0F172A")
    gray = colors.HexColor("#475569")

    title_style = ParagraphStyle("DocTitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=19, leading=24, textColor=primary, spaceAfter=4)
    subtitle_style = ParagraphStyle("DocSub", parent=styles["Normal"], fontName="Helvetica", fontSize=11, leading=15, textColor=secondary, spaceAfter=10)
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=primary, spaceBefore=14, spaceAfter=6, keepWithNext=True)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=secondary, spaceBefore=10, spaceAfter=4, keepWithNext=True)
    body = ParagraphStyle("Body", parent=styles["Normal"], fontName="Helvetica", fontSize=9.2, leading=13, textColor=dark, spaceAfter=5)
    bullet = ParagraphStyle("Bullet", parent=body, leftIndent=14, firstLineIndent=-10, spaceAfter=3)
    caption = ParagraphStyle("Caption", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8.3, leading=11, textColor=gray, alignment=1, spaceBefore=3, spaceAfter=9)
    code_style = ParagraphStyle("Code", parent=styles["Normal"], fontName="Courier", fontSize=7.1, leading=9.8, textColor=colors.HexColor("#1E293B"))
    th = ParagraphStyle("TH", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.2, leading=10.5, textColor=colors.white, alignment=1)
    tc = ParagraphStyle("TC", parent=styles["Normal"], fontName="Helvetica", fontSize=8, leading=10.5, textColor=dark)
    tcc = ParagraphStyle("TCC", parent=tc, alignment=1)
    tcb = ParagraphStyle("TCB", parent=tc, fontName="Helvetica-Bold")

    story = []

    # En-tête principal
    story.append(Paragraph("Compte Rendu — Atelier Pratique MLOps", title_style))
    story.append(Paragraph("Intégration de Git + DVC + MLflow dans un Workflow Reproductible (Classification Iris & Wine)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=primary, spaceBefore=0, spaceAfter=10))

    info_data = [
        [Paragraph("<b>Étudiant :</b> Mohamed Amine BELGUEROUANI", body), Paragraph("<b>Date :</b> 02 Novembre 2026", body)],
        [Paragraph("<b>Matière :</b> MLOps &amp; Cycle de Vie ML", body), Paragraph("<b>Datasets :</b> Iris (150 lignes) &amp; Wine (178 lignes)", body)],
        [Paragraph("<b>Stack :</b> Python 3.12, Git 2.52, DVC 3.67, MLflow 3.17", body), Paragraph("<b>Backend MLflow :</b> SQLite (<code>sqlite:///mlflow.db</code>)", body)],
        [Paragraph("<b>Dépôt GitHub :</b> <code>https://github.com/anakin-skyguy/atelier-mlops</code>", body), Paragraph("<b>Tests &amp; CI :</b> Pytest (4/4 passés) + GitHub Actions", body)],
    ]
    info_table = Table(info_data, colWidths=[265, 230])
    info_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(info_table)
    story.append(Spacer(1, 10))

    # 1. Architecture
    story.append(Paragraph("1. Architecture Générale et Complémentarité Git + DVC + MLflow", h1))
    story.append(
        Paragraph(
            "Un système de Machine Learning industrialisable dépend simultanément du <b>code source</b>, des <b>données</b> et des "
            "<b>hyperparamètres d'entraînement</b>. Cet atelier assemble trois outils spécialisés afin d'assurer une traçabilité "
            "et une reproductibilité de bout en bout :",
            body,
        )
    )

    arch_rows = [
        [Paragraph("Fonctionnalité MLOps", th), Paragraph("Git / GitHub", th), Paragraph("DVC", th), Paragraph("MLflow", th)],
        [Paragraph("Versioning du code source", tcb), Paragraph("Oui (commits, branches)", tcc), Paragraph("Non", tcc), Paragraph("Non (trace le SHA)", tcc)],
        [Paragraph("Versioning des datasets", tcb), Paragraph("Pointeurs .dvc", tcc), Paragraph("Oui (cache + remote)", tcc), Paragraph("Métadonnées", tcc)],
        [Paragraph("Pipeline ML reproductible", tcb), Paragraph("dvc.yaml &amp; dvc.lock", tcc), Paragraph("Oui (dvc repro / dag)", tcc), Paragraph("Tracking associé", tcc)],
        [Paragraph("Suivi des hyperparamètres", tcb), Paragraph("params.yaml", tcc), Paragraph("dvc params diff", tcc), Paragraph("Oui (log_params)", tcc)],
        [Paragraph("Suivi des métriques", tcb), Paragraph("reports/metrics*.json", tcc), Paragraph("dvc metrics show/diff", tcc), Paragraph("Oui (log_metrics)", tcc)],
        [Paragraph("Suivi des artefacts modèles", tcb), Paragraph("Exclus (.gitignore)", tcc), Paragraph("Oui (sorties outs:)", tcc), Paragraph("Oui (log_artifact)", tcc)],
        [Paragraph("Comparaison visuelle des runs", tcb), Paragraph("Non", tcc), Paragraph("Comparaison CLI", tcc), Paragraph("Oui (UI &amp; graphiques)", tcc)],
    ]
    story.append(styled_table(arch_rows, [145, 115, 115, 120], primary))
    story.append(Spacer(1, 6))

    # 2. TP 1 - Git
    story.append(Paragraph("2. TP 1 — Gestion du Code Source avec Git et Publication GitHub", h1))
    story.append(
        Paragraph(
            "Le dépôt a été structuré autour des branches <code>main</code> (versions stables publiées) et <code>develop</code> "
            "(intégration continue des travaux), avec <b>13 commits atomiques</b> signés sous l'identité de l'étudiant et jalonnés par "
            "trois tags annotés (<code>v1.0</code>, <code>v2.0</code>, <code>v3.0</code>).",
            body,
        )
    )
    story.append(
        Paragraph(
            "• <b>Configuration .gitignore adaptée à DVC :</b> Exclusion de <code>__pycache__/</code>, <code>.venv/</code>, <code>mlruns/</code> "
            "et <code>mlflow.db</code>, tout en laissant DVC administrer <code>data/raw/.gitignore</code> et <code>models/.gitignore</code>.",
            bullet,
        )
    )
    story.append(
        Paragraph(
            "• <b>Normalisation inter-plateformes (.gitattributes) :</b> L'ajout de <code>* text=auto eol=lf</code> dès l'initialisation évite "
            "toute divergence d'empreinte MD5 des dépendances Python entre Windows (CRLF) et Linux Ubuntu (LF) lors de <code>dvc status</code>.",
            bullet,
        )
    )

    git_log_text = """6a24c86 (HEAD -> main, tag: v3.0, develop) Documentation complete, captures MLflow UI haute resolution et README
9208786 Extension CI: Ajout des tests qualite donnees/modeles et workflow GitHub Actions
95f77fa TP3 & TP4: Ajout du modele KNN au pipeline DVC et suivi MLflow
adee5f3 TP2: Restauration de la version initiale du dataset Wine (178 lignes)
621a49e TP2: Modification du dataset Wine (echantillon de 100 lignes)
2b6ae97 TP2: Versioning du second dataset Wine (178 lignes) avec DVC
2691ffb (tag: v2.0) Experience Random Forest avec 200 arbres et max_depth=8
a54cbbb (tag: v1.0) Ajout du pipeline MLOps integre DVC et MLflow (Random Forest 100 arbres)
60bf79c Configuration des remotes DVC (local storage et distant HTTPS)
aad8dde Versioning du dataset Iris avec DVC
0559893 Initialisation de DVC
0a6e156 Ajout du script de preparation du second dataset (Wine)
a635cc1 Initialisation du projet Iris"""
    story.append(make_code_box(git_log_text, code_style))
    story.append(Spacer(1, 6))

    # 3. TP 2 - DVC Data Versioning
    story.append(Paragraph("3. TP 2 — Versioning des Données, Remotes DVC et Restauration", h1))
    story.append(
        Paragraph(
            "Deux jeux de données tabulaires ont été générés de façon déterministe et placés sous suivi DVC :",
            body,
        )
    )
    story.append(Paragraph("• <b>Dataset principal Iris (<code>data/raw/iris.csv</code>) :</b> 150 lignes, 5 colonnes — MD5 <code>4d301abed5efe50eccda350cde38e0eb</code> (2 778 octets).", bullet))
    story.append(Paragraph("• <b>Second dataset Wine (<code>data/raw/wine.csv</code>) :</b> 178 lignes, 14 colonnes — MD5 <code>2925c4a8cd201c79d97d3d283429ef23</code> (10 962 octets).", bullet))
    story.append(
        Paragraph(
            "• <b>Double Remote DVC (Local + HTTPS universel) :</b> Outre le remote local <code>storage</code> (<code>../dvc-storage</code>), "
            "un remote HTTPS par défaut <code>github</code> pointe vers la branche orpheline dédiée <code>dvc-storage</code> hébergeant uniquement "
            "le cache adressé par contenu (<code>files/md5/...</code>). Ainsi, <code>dvc pull</code> fonctionne immédiatement sur toute machine tierce et dans GitHub Actions.",
            bullet,
        )
    )
    story.append(
        Paragraph(
            "• <b>Expérience d'altération et restauration (TP 2.7) :</b> Après réduction de <code>wine.csv</code> à 100 lignes et commit du nouveau "
            "pointeur <code>wine.csv.dvc</code>, l'exécution de <code>git checkout HEAD~1 -- data/raw/wine.csv.dvc</code> suivie de "
            "<code>dvc checkout</code> a restauré intégralement les <b>178 lignes</b> avec une correspondance MD5 bit-à-bit exacte.",
            bullet,
        )
    )

    # 4. TP 3 - MLflow Tracking & Screenshots
    story.append(Paragraph("4. TP 3 — Suivi et Comparaison des Expérimentations avec MLflow", h1))
    story.append(
        Paragraph(
            "Les entraînements sont enregistrés dans <code>sqlite:///mlflow.db</code> sous l'expérience <code>TP_Iris_Classification</code> "
            "(découpage stratifié identique : <code>test_size=0.2</code> soit 120 train / 30 test, <code>random_state=42</code>) :",
            body,
        )
    )

    res_rows = [
        [
            Paragraph("Tag Git", th),
            Paragraph("Run MLflow", th),
            Paragraph("Algorithme &amp; Hyperparamètres", th),
            Paragraph("Accuracy", th),
            Paragraph("Precision", th),
            Paragraph("Recall", th),
            Paragraph("F1-Score", th),
        ],
        [
            Paragraph("<b>v1.0</b>", tcc),
            Paragraph("<code>RandomForest_n100_d5</code>", tc),
            Paragraph("Random Forest (n=100, depth=5)", tc),
            Paragraph("<b>0.9333</b>", tcc),
            Paragraph("<b>0.9333</b>", tcc),
            Paragraph("<b>0.9333</b>", tcc),
            Paragraph("<b>0.9333</b>", tcc),
        ],
        [
            Paragraph("<b>v2.0</b>", tcc),
            Paragraph("<code>RandomForest_n200_d8</code>", tc),
            Paragraph("Random Forest (n=200, depth=8)", tc),
            Paragraph("0.9000", tcc),
            Paragraph("0.9024", tcc),
            Paragraph("0.9000", tcc),
            Paragraph("0.8997", tcc),
        ],
        [
            Paragraph("<b>v3.0</b>", tcc),
            Paragraph("<code>KNN_k5</code>", tc),
            Paragraph("K-Nearest Neighbors (k=5)", tc),
            Paragraph("<b>1.0000</b>", tcc),
            Paragraph("<b>1.0000</b>", tcc),
            Paragraph("<b>1.0000</b>", tcc),
            Paragraph("<b>1.0000</b>", tcc),
        ],
    ]
    story.append(styled_table(res_rows, [45, 115, 135, 50, 50, 50, 50], primary))
    story.append(Spacer(1, 5))
    story.append(
        Paragraph(
            "<b>Interprétation :</b> Passer de 100 à 200 arbres (<code>max_depth</code> 5 → 8) dégrade l'accuracy de <code>0.9333</code> (28/30) "
            "à <code>0.9000</code> (27/30) par sur-ajustement sur un petit échantillon d'apprentissage (120 individus). Le classifieur "
            "<code>KNN_k5</code> obtient <code>1.0000</code> (30/30) grâce à la régularité géométrique des classes d'Iris, mais sur 30 individus "
            "de test (1 erreur = 3,33 %), une validation croisée stratifiée resterait nécessaire pour confirmer cet écart.",
            body,
        )
    )

    shots = [
        ("01_experiment_runs_list.png", "Figure 1 — Interface MLflow UI : tableau des runs de l'expérience TP_Iris_Classification avec métriques et hyperparamètres.", 225),
        ("03_compare_runs_metrics_table.png", "Figure 2 — Module Compare Runs de MLflow : graphique en coordonnées parallèles et tableau comparatif côte à côte des 3 modèles.", 330),
        ("04_run_rf100_detail.png", "Figure 3 — Fiche détaillée du run RandomForest_n100_d5 (v1.0 : Accuracy = 0.9333, F1 = 0.9333).", 225),
        ("05_run_knn_detail.png", "Figure 4 — Fiche détaillée du run KNN_k5 (v3.0 : n_neighbors = 5, Accuracy = 1.0000).", 225),
        ("06_run_artifacts_model.png", "Figure 5 — Onglet Artifacts dans MLflow UI confirmant l'enregistrement du modèle sérialisé (dossier model/).", 200),
    ]
    for fname, cap_txt, max_h in shots:
        img = get_scaled_image(os.path.join(screenshots_dir, fname), max_width=485, max_height=max_h)
        if img:
            story.append(KeepTogether([Spacer(1, 4), img, Paragraph(cap_txt, caption)]))

    # 5. TP 4 - Pipeline DVC, Reproductibilité & CI
    story.append(Paragraph("5. TP 4 — Pipeline Intégré DVC, Reproductibilité et Extension CI/CD", h1))
    story.append(
        Paragraph(
            "Le fichier déclaratif <code>dvc.yaml</code> orchestre les deux stages d'entraînement (<code>train</code> et <code>train_knn</code>) "
            "à partir de <code>data/raw/iris.csv</code> et <code>params.yaml</code>, tandis que <code>dvc.lock</code> fige les empreintes MD5 résolues :",
            body,
        )
    )
    dag_text = """$ dvc dag
  +-----------------------+
  | data\\raw\\iris.csv.dvc |
  +-----------------------+
         **        **
       **            **
      *                *
+-------+         +-----------+
| train |         | train_knn |
+-------+         +-----------+

$ dvc metrics diff v1.0 v2.0
Path                  Metric     v1.0     v2.0     Change
reports\\metrics.json  accuracy   0.93333  0.9      -0.03333
reports\\metrics.json  f1_score   0.93333  0.89975  -0.03358"""
    story.append(make_code_box(dag_text, code_style))
    story.append(Spacer(1, 5))

    story.append(Paragraph("5.1. Vérification de restauration et test sur environnement vierge isolé", h2))
    story.append(
        Paragraph(
            "Un test de bout en bout a été conduit dans un répertoire isolé hors du projet (sans accès à <code>../dvc-storage</code>) : "
            "après <code>git clone https://github.com/anakin-skyguy/atelier-mlops.git</code>, la commande <code>dvc pull</code> télécharge "
            "automatiquement les 4 artefacts via HTTPS (<code>iris.csv</code>, <code>wine.csv</code>, <code>model.pkl</code>, <code>knn_model.pkl</code>). "
            "Sur <code>main</code> comme après restauration de <code>v1.0</code> (<code>n=100, d=5</code>), <code>v2.0</code> (<code>n=200, d=8</code>) "
            "et <code>v3.0</code>, <code>dvc status</code> renvoie systématiquement <i>« Data and pipelines are up to date »</i>.",
            body,
        )
    )

    story.append(Paragraph("5.2. Contrôles qualité automatisés (Pytest) et GitHub Actions", h2))
    story.append(
        Paragraph(
            "Conformément aux recommandations de la Section 12, le fichier <code>tests/test_mlops.py</code> et le workflow "
            "<code>.github/workflows/mlops.yml</code> automatisent <code>dvc pull</code>, <code>dvc repro</code>, <code>dvc metrics show</code> "
            "et 4 tests unitaires/qualité (intégrité de <code>iris.csv</code> et <code>wine.csv</code>, cohérence de <code>params.yaml</code>/<code>dvc.lock</code>, "
            "inférence des modèles <code>.pkl</code> et respect du seuil d'acceptation <code>accuracy &amp; f1_score &gt;= 0.85</code> — <b>4 passed</b>).",
            body,
        )
    )

    # 6. Questions de réflexion
    story.append(Paragraph("6. Réponses aux Questions de Réflexion (Section 16)", h1))
    qa = [
        (
            "Q15. Quelle est la différence entre Git et DVC ?",
            "Git versionne le code source et les fichiers texte légers de configuration (.py, .yaml, .dvc, dvc.lock). DVC versionne les datasets volumineux et les binaires de modèles en stockant leur contenu dans un cache adressé par hachage MD5 (synchronisé avec un remote local ou cloud) et fournit un moteur de pipeline reproductible.",
        ),
        (
            "Q16. Pourquoi éviter de stocker un dataset volumineux directement dans Git ?",
            "Chaque révision d'un fichier massif alourdit définitivement l'historique .git de tous les clones, ralentit les opérations réseau (clone/fetch), dépasse les limites des plateformes (100 Mo/fichier sur GitHub) et produit des diffs textuels inutilisables.",
        ),
        (
            "Q17. Quelle est la différence entre dvc add et dvc repro ?",
            "dvc add enregistre un fichier statique existant (comme un dataset brut) dans le cache DVC et génère un pointeur .dvc sans exécuter de code. dvc repro parcourt le graphe de stages défini dans dvc.yaml, compare les empreintes des entrées/paramètres à dvc.lock, ne ré-exécute que les étapes modifiées et met à jour dvc.lock.",
        ),
        (
            "Q18. Quel est le rôle du fichier dvc.lock ?",
            "dvc.lock capture l'état exact résolu d'une exécution du pipeline : commandes, valeurs des hyperparamètres, tailles et empreintes MD5 de toutes les dépendances et sorties. Suivi par Git, il lie chaque commit à une version unique et vérifiable des données et des modèles.",
        ),
        (
            "Q19. Comment MLflow permet-il de comparer deux expérimentations ?",
            "MLflow enregistre dans son Backend Store (sqlite:///mlflow.db) les paramètres, métriques et artefacts de chaque run. Sa vue Compare aligne côte à côte les hyperparamètres différents, les métriques et trace des graphiques comparatifs (coordonnées parallèles, scatter/box plots), complétée par l'API mlflow.search_runs().",
        ),
        (
            "Q20. Comment retrouver les données et le modèle associés à un commit Git précis ?",
            "Il suffit d'exécuter <code>git checkout &lt;commit_ou_tag&gt;</code> (qui restaure <code>dvc.lock</code> et les fichiers <code>.dvc</code> de cet instant), puis <code>dvc checkout</code> (ou <code>dvc pull</code> si les objets sont absents du cache local) pour matérialiser exactement les fichiers de données et le modèle binaire correspondants.",
        ),
        (
            "Q21. Pourquoi la reproductibilité est-elle importante dans un projet d'intelligence artificielle ?",
            "Parce qu'un modèle dépend conjointement du code, des données, des hyperparamètres et de l'aléa numérique. La reproductibilité garantit la rigueur expérimentale (isoler l'effet d'un changement), l'auditabilité réglementaire, le rollback rapide en cas de régression en production et la collaboration fiable en équipe.",
        ),
        (
            "Q22. Quelle est la différence entre le versioning des modèles avec DVC et leur suivi avec MLflow ?",
            "DVC versionne le fichier physique du modèle comme sortie déterministe du pipeline couplée à un commit Git (orienté reproductibilité et restauration). MLflow journalise l'ensemble des runs exploratoires avec leurs métriques, graphiques et états dans le Model Registry (orienté analyse expérimentale et gouvernance du cycle de vie). Les deux outils sont complémentaires.",
        ),
    ]
    for q_title, q_ans in qa:
        story.append(KeepTogether([Paragraph(f"<b>{q_title}</b>", h2), Paragraph(q_ans, body)]))

    # 7. Récapitulatif des livrables (Section 17) & Conclusion
    story.append(Paragraph("7. Récapitulatif des Livrables Attendus (Section 17) et Conclusion", h1))
    liv_rows = [
        [Paragraph("Livrable attendu", th), Paragraph("Emplacement / Référence vérifiée", th), Paragraph("Statut", th)],
        [Paragraph("Lien du repository GitHub", tcb), Paragraph("<code>https://github.com/anakin-skyguy/atelier-mlops</code> (main, develop, v1.0–v3.0)", tc), Paragraph("<b>Validé</b>", tcc)],
        [Paragraph("Configurations DVC", tcb), Paragraph("<code>.dvc/config</code>, <code>data/raw/*.dvc</code>, <code>dvc.yaml</code>, <code>dvc.lock</code>", tc), Paragraph("<b>Validé</b>", tcc)],
        [Paragraph("Code Python &amp; Paramètres", tcb), Paragraph("<code>src/prepare_*.py</code>, <code>src/train.py</code>, <code>src/train_knn.py</code>, <code>params.yaml</code>", tc), Paragraph("<b>Validé</b>", tcc)],
        [Paragraph("Captures de l'interface MLflow", tcb), Paragraph("6 captures HD dans <code>docs/screenshots/</code> et intégrées aux Figures 1 à 5", tc), Paragraph("<b>Validé</b>", tcc)],
        [Paragraph("Comparaison d'expérimentations", tcb), Paragraph("RF v1.0 (0.9333) vs RF v2.0 (0.9000) vs KNN k=5 (1.0000) — Section 4", tc), Paragraph("<b>Validé</b>", tcc)],
        [Paragraph("Restauration &amp; Reproductibilité", tcb), Paragraph("Rollback Wine MD5 + Rollback v1.0/v2.0 + Clone isolé HTTPS + Pytest 4/4", tc), Paragraph("<b>Validé</b>", tcc)],
    ]
    story.append(styled_table(liv_rows, [135, 300, 60], primary))
    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            "<b>Conclusion :</b> L'intégration conjointe de <b>Git</b> (code et pointeurs), <b>DVC</b> (données volumineuses, modèles et pipeline "
            "déterministe) et <b>MLflow</b> (suivi analytique des expérimentations) transforme un simple script d'entraînement Scikit-learn en "
            "un véritable pipeline MLOps industrialisable, traçable, auditable et intégralement reproductible sur n'importe quel environnement.",
            body,
        )
    )

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF généré avec succès : {output_pdf_path} ({os.path.getsize(output_pdf_path)} octets)")


if __name__ == "__main__":
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    workspace_root = os.path.dirname(repo_root)
    shots_dir = os.path.join(repo_root, "docs", "screenshots")
    out_workspace = os.path.join(workspace_root, "COMPTE_RENDU_ATELIER_MLOPS_BELGUEROUANI_Mohamed_Amine.pdf")
    out_repo = os.path.join(repo_root, "docs", "COMPTE_RENDU_ATELIER_MLOPS_BELGUEROUANI_Mohamed_Amine.pdf")
    generate_pdf(out_workspace, shots_dir)
    generate_pdf(out_repo, shots_dir)
