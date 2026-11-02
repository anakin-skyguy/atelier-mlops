"""
Script de génération du Compte Rendu Officiel PDF complet pour l'Atelier Pratique MLOps
(Intégration de Git + DVC + MLflow — Classification Iris & Wine).
Inclut l'intégralité du code clé, des analyses, des 11 captures HD (thème clair 2x Retina)
et des réponses détaillées aux questions de réflexion.
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
            self.drawString(46, 806, "COMPTE RENDU — ATELIER PRATIQUE MLOPS : GIT + DVC + MLFLOW")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(549, 806, "MOHAMED AMINE BELGUEROUANI")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.75)
            self.line(46, 798, 549, 798)

        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(46, 42, 549, 42)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(46, 29, "MLOps & Industrialisation du Machine Learning — github.com/anakin-skyguy/atelier-mlops")
        self.drawRightString(549, 29, f"Page {self._pageNumber} sur {total_pages}")
        self.restoreState()


def get_scaled_image(path, max_width=500, max_height=340, border=True):
    """Charge et redimensionne proportionnellement une capture HD en conservant toute sa netteté."""
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
    im = Image(path, width=target_w, height=target_h)
    if not border:
        return im
    wrapper = Table([[im]], colWidths=[target_w + 4])
    wrapper.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD5E1")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    wrapper.hAlign = "CENTER"
    return wrapper


def make_code_box(text, code_style, width=503):
    t = Table([[Preformatted(text.strip(), code_style)]], colWidths=[width])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
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
                ("TOPPADDING", (0, 0), (-1, -1), 4.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return t


def add_figure(story, screenshots_dir, filename, caption_text, caption_style, max_w=500, max_h=330, border=True):
    flow_img = get_scaled_image(os.path.join(screenshots_dir, filename), max_width=max_w, max_height=max_h, border=border)
    if flow_img:
        story.append(KeepTogether([Spacer(1, 4), flow_img, Paragraph(caption_text, caption_style)]))


def generate_pdf(output_pdf_path, screenshots_dir):
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        leftMargin=46,
        rightMargin=46,
        topMargin=50,
        bottomMargin=50,
    )

    styles = getSampleStyleSheet()
    primary = colors.HexColor("#1E3A8A")
    secondary = colors.HexColor("#0284C7")
    dark = colors.HexColor("#0F172A")
    gray = colors.HexColor("#475569")

    title_style = ParagraphStyle("DocTitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=19, leading=24, textColor=primary, spaceAfter=4)
    subtitle_style = ParagraphStyle("DocSub", parent=styles["Normal"], fontName="Helvetica", fontSize=11, leading=15, textColor=secondary, spaceAfter=10)
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=primary, spaceBefore=13, spaceAfter=5, keepWithNext=True)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=secondary, spaceBefore=9, spaceAfter=4, keepWithNext=True)
    body = ParagraphStyle("Body", parent=styles["Normal"], fontName="Helvetica", fontSize=9.2, leading=13, textColor=dark, spaceAfter=5)
    bullet = ParagraphStyle("Bullet", parent=body, leftIndent=14, firstLineIndent=-10, spaceAfter=3)
    caption = ParagraphStyle("Caption", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8.3, leading=11, textColor=gray, alignment=1, spaceBefore=4, spaceAfter=9)
    code_style = ParagraphStyle("Code", parent=styles["Normal"], fontName="Courier", fontSize=7.4, leading=10.0, textColor=colors.HexColor("#1E293B"))
    th = ParagraphStyle("TH", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.2, leading=10.5, textColor=colors.white, alignment=1)
    tc = ParagraphStyle("TC", parent=styles["Normal"], fontName="Helvetica", fontSize=8, leading=10.5, textColor=dark)
    tcc = ParagraphStyle("TCC", parent=tc, alignment=1)
    tcb = ParagraphStyle("TCB", parent=tc, fontName="Helvetica-Bold")

    story = []

    # =========================================================================
    # CARTOUCHE D'IDENTIFICATION
    # =========================================================================
    story.append(Paragraph("Compte Rendu — Atelier Pratique MLOps", title_style))
    story.append(Paragraph("Intégration de Git + DVC + MLflow dans un Workflow Reproductible (Classification Iris &amp; Wine)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=primary, spaceBefore=0, spaceAfter=10))

    info_data = [
        [Paragraph("<b>Étudiant :</b> Mohamed Amine BELGUEROUANI", body), Paragraph("<b>Date :</b> 02 Novembre 2026", body)],
        [Paragraph("<b>Matière :</b> MLOps &amp; Industrialisation ML", body), Paragraph("<b>Datasets :</b> Iris (150 lignes) &amp; Wine (178 lignes)", body)],
        [Paragraph("<b>Outils :</b> Python 3.12, Git 2.52, DVC 3.67, MLflow 3.17", body), Paragraph("<b>Backend MLflow :</b> SQLite (<code>sqlite:///mlflow.db</code>)", body)],
        [Paragraph("<b>Repository GitHub :</b> <code>https://github.com/anakin-skyguy/atelier-mlops</code>", body), Paragraph("<b>Validation :</b> Pytest (4/4 passés) + Clone isolé HTTPS", body)],
    ]
    info_table = Table(info_data, colWidths=[275, 228])
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
    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 1 : ARCHITECTURE GÉNÉRALE
    # =========================================================================
    story.append(Paragraph("1. Architecture Générale et Complémentarité Git + DVC + MLflow", h1))
    story.append(
        Paragraph(
            "Contrairement au développement logiciel classique où seul le code détermine le comportement du programme, un modèle de "
            "Machine Learning dépend conjointement du <b>code source</b>, des <b>jeux de données</b> et des <b>hyperparamètres</b>. "
            "Cet atelier intègre trois briques complémentaires pour garantir traçabilité et reproductibilité :",
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
    story.append(styled_table(arch_rows, [148, 118, 118, 119], primary))

    # =========================================================================
    # SECTION 2 : TP 1 — GIT & GITHUB
    # =========================================================================
    story.append(Paragraph("2. TP 1 — Gestion du Code Source avec Git et Publication GitHub", h1))
    story.append(
        Paragraph(
            "Le dépôt Git a été structuré autour des branches <code>main</code> (versions stables publiées) et <code>develop</code> "
            "(intégration progressive), jalonné par <b>14 commits atomiques</b> et trois tags sémantiques annotés : "
            "<code>v1.0</code> (Random Forest 100 arbres), <code>v2.0</code> (Random Forest 200 arbres) et <code>v3.0</code> (pipeline complet RF + KNN + tests + CI).",
            body,
        )
    )
    story.append(
        Paragraph(
            "• <b>Configuration .gitignore &amp; .gitattributes :</b> Exclusion de <code>mlruns/</code>, <code>mlflow.db</code>, <code>.venv/</code> "
            "et <code>__pycache__/</code> tout en déléguant <code>models/.gitignore</code> à DVC. L'ajout de <code>* text=auto eol=lf</code> dans "
            "<code>.gitattributes</code> garantit des empreintes MD5 identiques entre Windows et Linux.",
            bullet,
        )
    )
    story.append(
        Paragraph(
            "• <b>Réponse à la question préliminaire (p. 3) :</b> Stocker directement des datasets volumineux dans Git duplique chaque révision dans "
            "<code>.git/objects</code>, ralentit fortement <code>git clone</code>, dépasse la limite de 100 Mo/fichier sur GitHub et produit des diffs illisibles.",
            bullet,
        )
    )

    add_figure(
        story,
        screenshots_dir,
        "01_github_repository.png",
        "Figure 1 — Dépôt GitHub publié (https://github.com/anakin-skyguy/atelier-mlops) : branches main/develop, 3 tags (v1.0, v2.0, v3.0) et arborescence MLOps sans fichiers binaires ni CSV.",
        caption,
        max_w=500,
        max_h=305,
    )
    add_figure(
        story,
        screenshots_dir,
        "02_git_branches_tags_log.png",
        "Figure 2 — Vérification CLI Git : dépôt distant GitHub, branches locales/distantes, tags annotés (v1.0, v2.0, v3.0) et graphe complet des commits.",
        caption,
        max_w=500,
        max_h=270,
        border=False,
    )

    # =========================================================================
    # SECTION 3 : TP 2 — DVC DATA VERSIONING & ROLLBACK
    # =========================================================================
    story.append(Paragraph("3. TP 2 — Versioning des Données avec DVC, Remotes et Restauration", h1))
    story.append(
        Paragraph(
            "Conformément au TP 2, deux datasets distincts ont été versionnés avec <code>dvc add</code> : le dataset principal "
            "<b>Iris</b> (<code>data/raw/iris.csv</code>, 150 lignes) et le second dataset <b>Wine</b> (<code>data/raw/wine.csv</code>, 178 lignes). "
            "Deux remotes sont configurés dans <code>.dvc/config</code> : <code>storage</code> (<code>../dvc-storage</code> local) et "
            "<code>github</code> (remote HTTPS par défaut adossé à la branche orpheline dédiée <code>dvc-storage</code> permettant un "
            "<code>dvc pull</code> immédiat sur toute machine externe).",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>Expérience de modification et restauration (TP 2 — Q7) :</b> Le dataset <code>wine.csv</code> a été réduit de 178 à 100 lignes "
            "(MD5 modifié de <code>2925c4a8...</code> vers <code>cc50fa13...</code>), puis restauré via "
            "<code>git checkout HEAD~1 -- data/raw/wine.csv.dvc &amp;&amp; dvc checkout</code>, rétablissant exactement les 178 lignes et le MD5 d'origine.",
            body,
        )
    )

    add_figure(
        story,
        screenshots_dir,
        "03_dvc_remotes_and_wine_rollback.png",
        "Figure 3 — Versioning DVC des datasets Iris et Wine : configuration des remotes, contenu des pointeurs .dvc et vérification par hachage MD5 de la restauration de wine.csv (178 → 100 → 178 lignes).",
        caption,
        max_w=500,
        max_h=245,
        border=False,
    )

    # =========================================================================
    # SECTION 4 : TP 3 — MLFLOW TRACKING & SCREENSHOTS HD
    # =========================================================================
    story.append(Paragraph("4. TP 3 — Suivi et Comparaison des Expérimentations dans MLflow UI", h1))
    story.append(
        Paragraph(
            "Le serveur de suivi MLflow s'appuie sur le backend relationnel SQLite (<code>sqlite:///mlflow.db</code>) au sein de l'expérience "
            "<code>TP_Iris_Classification</code>. Trois expérimentations ont été conduites sur le même découpage stratifié "
            "(<code>test_size=0.2</code> soit 120 observations d'entraînement et 30 de test, <code>random_state=42</code>) :",
            body,
        )
    )

    res_rows = [
        [
            Paragraph("Tag Git", th),
            Paragraph("Nom du Run MLflow", th),
            Paragraph("Modèle &amp; Hyperparamètres", th),
            Paragraph("Accuracy", th),
            Paragraph("Precision", th),
            Paragraph("Recall", th),
            Paragraph("F1-Score", th),
        ],
        [
            Paragraph("<b>v1.0</b>", tcc),
            Paragraph("<code>RandomForest_n100_d5</code>", tc),
            Paragraph("Random Forest (n=100, max_depth=5)", tc),
            Paragraph("<b>0.9333</b>", tcc),
            Paragraph("<b>0.9333</b>", tcc),
            Paragraph("<b>0.9333</b>", tcc),
            Paragraph("<b>0.9333</b>", tcc),
        ],
        [
            Paragraph("<b>v2.0</b>", tcc),
            Paragraph("<code>RandomForest_n200_d8</code>", tc),
            Paragraph("Random Forest (n=200, max_depth=8)", tc),
            Paragraph("0.9000", tcc),
            Paragraph("0.9024", tcc),
            Paragraph("0.9000", tcc),
            Paragraph("0.8997", tcc),
        ],
        [
            Paragraph("<b>v3.0</b>", tcc),
            Paragraph("<code>KNN_k5</code>", tc),
            Paragraph("K-Nearest Neighbors (n_neighbors=5)", tc),
            Paragraph("<b>1.0000</b>", tcc),
            Paragraph("<b>1.0000</b>", tcc),
            Paragraph("<b>1.0000</b>", tcc),
            Paragraph("<b>1.0000</b>", tcc),
        ],
    ]
    story.append(styled_table(res_rows, [44, 118, 141, 50, 50, 50, 50], primary))
    story.append(Spacer(1, 4))
    story.append(
        Paragraph(
            "<b>Analyse comparative :</b> L'augmentation de complexité du Random Forest entre <code>v1.0</code> (100 arbres, profondeur 5) et "
            "<code>v2.0</code> (200 arbres, profondeur 8) réduit l'accuracy de <code>0.9333</code> (28/30) à <code>0.9000</code> (27/30), illustrant un "
            "léger sur-ajustement aux frontières locales du jeu d'apprentissage. Le modèle <code>KNN_k5</code> atteint <code>1.0000</code> (30/30) sur ce "
            "pli de test grâce à la forte séparabilité géométrique des pétales/sépales ; compte tenu de la taille modeste du test (30 individus, soit "
            "3,33 % par erreur), une validation croisée stratifiée serait requise en production pour confirmer cet avantage.",
            body,
        )
    )

    add_figure(
        story,
        screenshots_dir,
        "04_mlflow_runs_table.png",
        "Figure 4 — Interface MLflow UI (mode Model training) : liste des 3 runs de TP_Iris_Classification affichant l'ensemble des métriques (accuracy, f1_score, precision, recall) et des hyperparamètres.",
        caption,
        max_w=500,
        max_h=175,
    )
    add_figure(
        story,
        screenshots_dir,
        "05_mlflow_compare_chart.png",
        "Figure 5 — Comparaison visuelle des 3 runs dans MLflow UI : graphique en coordonnées parallèles reliant max_depth, type de modèle, n_estimators et accuracy.",
        caption,
        max_w=500,
        max_h=215,
    )
    add_figure(
        story,
        screenshots_dir,
        "06_mlflow_compare_table.png",
        "Figure 6 — Tableau comparatif côte à côte dans MLflow UI : détails d'exécution, différences d'hyperparamètres surlignées et métriques complètes des 3 modèles.",
        caption,
        max_w=475,
        max_h=375,
    )
    add_figure(
        story,
        screenshots_dir,
        "07_mlflow_run_rf100.png",
        "Figure 7 — Fiche détaillée du run RandomForest_n100_d5 (tag v1.0 : Accuracy = 0.9333, n_estimators = 100, max_depth = 5).",
        caption,
        max_w=495,
        max_h=305,
    )
    add_figure(
        story,
        screenshots_dir,
        "08_mlflow_run_rf200.png",
        "Figure 8 — Fiche détaillée du run RandomForest_n200_d8 (tag v2.0 : Accuracy = 0.9000, F1 = 0.8997, n_estimators = 200, max_depth = 8).",
        caption,
        max_w=495,
        max_h=305,
    )
    add_figure(
        story,
        screenshots_dir,
        "09_mlflow_run_knn.png",
        "Figure 9 — Fiche détaillée du run KNN_k5 (tag v3.0 : Accuracy = 1.0000, n_neighbors = 5, random_state = 42, test_size = 0.2).",
        caption,
        max_w=495,
        max_h=295,
    )
    add_figure(
        story,
        screenshots_dir,
        "11_mlflow_artifacts_model_pkl.png",
        "Figure 10 — Onglet Artifacts dans MLflow UI : arborescence model/ dépliée confirmant l'enregistrement de l'artefact binaire model.pkl.",
        caption,
        max_w=495,
        max_h=185,
    )

    # =========================================================================
    # SECTION 5 : TP 4 — PIPELINE DVC, REPRODUCTIBILITÉ & CI/CD
    # =========================================================================
    story.append(Paragraph("5. TP 4 — Pipeline Intégré DVC, Reproductibilité et Extension CI/CD", h1))
    story.append(
        Paragraph(
            "Les fichiers <code>params.yaml</code> et <code>dvc.yaml</code> définissent de manière déclarative les deux stages du pipeline "
            "(<code>train</code> pour Random Forest et <code>train_knn</code> pour KNN), tandis que <code>dvc.lock</code> fige les hachages MD5 exacts "
            "de chaque entrée et sortie :",
            body,
        )
    )

    dvc_configs_code = """# params.yaml
train:
  n_estimators: 200
  max_depth: 8
  random_state: 42
  test_size: 0.2
knn:
  n_neighbors: 5

# dvc.yaml
stages:
  train:
    cmd: python src/train.py
    deps: [src/train.py, data/raw/iris.csv]
    params: [train.n_estimators, train.max_depth, train.random_state, train.test_size]
    outs: [models/model.pkl]
    metrics:
      - reports/metrics.json: {cache: false}
  train_knn:
    cmd: python src/train_knn.py
    deps: [src/train_knn.py, data/raw/iris.csv]
    params: [train.random_state, train.test_size, knn.n_neighbors]
    outs: [models/knn_model.pkl]
    metrics:
      - reports/metrics_knn.json: {cache: false}"""
    story.append(make_code_box(dvc_configs_code, code_style))
    story.append(Spacer(1, 4))

    story.append(
        Paragraph(
            "<b>Restauration multi-versions, reproductibilité sur machine isolée et tests CI (Section 12) :</b> "
            "La restauration de <code>v1.0</code> (<code>git checkout v1.0 &amp;&amp; dvc checkout</code>) rétablit instantanément le modèle à "
            "100 arbres (<code>accuracy = 0.93333</code>). En outre, un clone complet exécuté dans un répertoire vierge isolé hors du projet "
            "(sans dossier <code>../dvc-storage</code>) télécharge automatiquement les 4 fichiers suivis via <code>dvc pull</code> (HTTPS), valide "
            "<code>dvc repro</code> et passe <b>4/4 tests Pytest</b> (qualité de <code>iris.csv</code> et <code>wine.csv</code>, cohérence pipeline, "
            "inférence des modèles et seuils d'acceptation <code>accuracy &amp; f1_score &gt;= 0.85</code>).",
            body,
        )
    )

    add_figure(
        story,
        screenshots_dir,
        "10_dvc_dag_rollback_pytest.png",
        "Figure 11 — Exécution du pipeline intégré : graphe dvc dag, comparaison CLI v1.0 vs v2.0, démonstration de rollback vers v1.0 et validation Pytest (4 passed).",
        caption,
        max_w=500,
        max_h=385,
        border=False,
    )

    # =========================================================================
    # SECTION 6 : QUESTIONS DE RÉFLEXION (Q15 À Q22)
    # =========================================================================
    story.append(Paragraph("6. Réponses aux Questions de Réflexion (Section 16)", h1))
    qa = [
        (
            "Q15. Quelle est la différence entre Git et DVC ?",
            "Git est un système de contrôle de versions conçu pour le code source et les fichiers texte légers (.py, .yaml, .dvc, dvc.lock). DVC étend Git aux données volumineuses et aux modèles binaires en stockant leur contenu réel dans un cache adressé par empreinte MD5 (synchronisé avec un remote local ou cloud) tout en orchestrant l'exécution reproductible du pipeline.",
        ),
        (
            "Q16. Pourquoi éviter de stocker un dataset volumineux directement dans Git ?",
            "Chaque modification d'un fichier lourd est dupliquée dans l'historique .git de tous les collaborateurs, ce qui alourdit définitivement le dépôt, ralentit les opérations réseau (clone, fetch, push), dépasse les quotas des plateformes (limite de 100 Mo par fichier sur GitHub) et produit des diffs textuels inexploitables.",
        ),
        (
            "Q17. Quelle est la différence entre dvc add et dvc repro ?",
            "dvc add place un fichier statique existant (comme un dataset brut) sous suivi DVC en calculant son MD5 et en créant un fichier .dvc sans exécuter de traitement. dvc repro parcourt le graphe de dépendances défini dans dvc.yaml, compare les empreintes courantes des entrées et paramètres à dvc.lock, ne relance que les étapes modifiées et met à jour dvc.lock.",
        ),
        (
            "Q18. Quel est le rôle du fichier dvc.lock ?",
            "dvc.lock fige l'état exact résolu d'une exécution du pipeline : commandes lancées, valeurs effectives des hyperparamètres, tailles et hachages MD5 de toutes les dépendances (deps) et sorties (outs). Versionné dans Git, il associe de manière déterministe et vérifiable chaque commit à une version unique des données et des modèles.",
        ),
        (
            "Q19. Comment MLflow permet-il de comparer deux expérimentations ?",
            "Chaque exécution enregistrée dans le Backend Store (sqlite:///mlflow.db) conserve ses hyperparamètres, ses métriques et ses artefacts. La vue Compare de MLflow UI aligne côte à côte plusieurs runs en mettant en évidence les paramètres modifiés (Show diff only), compare les métriques et génère des graphiques interactifs (coordonnées parallèles, scatter/box plots), complétée par mlflow.search_runs().",
        ),
        (
            "Q20. Comment retrouver les données et le modèle associés à un commit Git précis ?",
            "En deux étapes : (1) exécuter <code>git checkout &lt;commit_ou_tag&gt;</code> (ex. <code>git checkout v1.0</code>) pour restaurer le code, <code>params.yaml</code>, <code>dvc.lock</code> et les fichiers <code>.dvc</code> de cet instant ; (2) exécuter <code>dvc checkout</code> (ou <code>dvc pull</code> si absent du cache local) afin de matérialiser exactement les datasets et le fichier modèle correspondants.",
        ),
        (
            "Q21. Pourquoi la reproductibilité est-elle importante dans un projet d'intelligence artificielle ?",
            "Un modèle d'IA dépend simultanément du code, des données, du prétraitement, des hyperparamètres et des graines aléatoires. La reproductibilité est indispensable pour valider scientifiquement l'impact d'une modification, garantir l'auditabilité et la traçabilité en production, effectuer un rollback fiable vers une version stable (v1.0) et collaborer sans écarts entre machines.",
        ),
        (
            "Q22. Quelle est la différence entre le versioning des modèles avec DVC et leur suivi avec MLflow ?",
            "DVC versionne le fichier physique du modèle (models/model.pkl) comme sortie déterministe du pipeline liée à un commit Git précis (orienté restauration et CI/CD). MLflow assure le suivi analytique de toutes les expérimentations (y compris exploratoires), la visualisation comparative des métriques et la gouvernance du cycle de vie via le Model Registry. Les deux outils sont donc complémentaires.",
        ),
    ]
    for q_title, q_ans in qa:
        story.append(KeepTogether([Paragraph(f"<b>{q_title}</b>", h2), Paragraph(q_ans, body)]))

    # =========================================================================
    # SECTION 7 : SYNTHÈSE DES LIVRABLES & CONCLUSION
    # =========================================================================
    story.append(Paragraph("7. Synthèse de Vérification des Livrables (Section 17) et Conclusion", h1))
    liv_rows = [
        [Paragraph("Livrable attendu (Grille /20)", th), Paragraph("Preuve &amp; Référence dans ce rapport", th), Paragraph("Statut", th)],
        [Paragraph("Git &amp; Repository GitHub (3 pts)", tcb), Paragraph("<code>github.com/anakin-skyguy/atelier-mlops</code> — Figures 1 &amp; 2 (main, develop, v1.0–v3.0)", tc), Paragraph("<b>Complet</b>", tcc)],
        [Paragraph("Versioning données DVC (4 pts)", tcb), Paragraph("<code>iris.csv.dvc</code>, <code>wine.csv.dvc</code>, double remote &amp; rollback MD5 — Figure 3", tc), Paragraph("<b>Complet</b>", tcc)],
        [Paragraph("Tracking MLflow UI (4 pts)", tcb), Paragraph("RF v1.0, RF v2.0 &amp; KNN k=5 comparés + artefacts — Figures 4 à 10", tc), Paragraph("<b>Complet</b>", tcc)],
        [Paragraph("Pipeline intégré DVC (4 pts)", tcb), Paragraph("<code>dvc.yaml</code>, <code>dvc.lock</code>, <code>params.yaml</code>, <code>dvc dag</code> — Section 5 &amp; Figure 11", tc), Paragraph("<b>Complet</b>", tcc)],
        [Paragraph("Reproductibilité &amp; Versions (3 pts)", tcb), Paragraph("Rollback v1.0, clone vierge HTTPS, Pytest 4/4 &amp; GitHub Actions — Figure 11", tc), Paragraph("<b>Complet</b>", tcc)],
        [Paragraph("Documentation &amp; Réflexion (2 pts)", tcb), Paragraph("README complet + Réponses détaillées aux questions Q15 à Q22 — Section 6", tc), Paragraph("<b>Complet</b>", tcc)],
    ]
    story.append(styled_table(liv_rows, [145, 298, 60], primary))
    story.append(Spacer(1, 5))
    story.append(
        Paragraph(
            "<b>Conclusion :</b> L'articulation de <b>Git</b> (versioning du code et des pointeurs), <b>DVC</b> (versioning des données et modèles, "
            "orchestration déterministe du pipeline) et <b>MLflow</b> (tracking analytique et comparaison visuelle des runs) permet de transformer un "
            "prototype Scikit-learn en un workflow MLOps rigoureux, auditable et intégralement reproductible.",
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
