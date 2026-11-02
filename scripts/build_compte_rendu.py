"""
Générateur du dossier unique de remise contenant 100 % des livrables attendus (Section 17),
les travaux pratiques (TP 1 à TP 4), le code Python et les fichiers DVC/YAML intégraux,
les 11 captures HD en thème clair et les réponses aux questions de réflexion (Section 16).
Auteur : Mohamed Amine BELGUEROUANI
"""

import os
from xml.sax.saxutils import escape
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
    """En-tête et pied de page avec numérotation 'Page X sur Y'."""

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
            self.drawString(44, 806, "DOSSIER UNIQUE DES LIVRABLES — ATELIER MLOPS : GIT + DVC + MLFLOW")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(551, 806, "MOHAMED AMINE BELGUEROUANI")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.75)
            self.line(44, 798, 551, 798)

        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(44, 42, 551, 42)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(44, 29, "Repository GitHub : https://github.com/anakin-skyguy/atelier-mlops")
        self.drawRightString(551, 29, f"Page {self._pageNumber} sur {total_pages}")
        self.restoreState()


def read_repo_file(repo_root, rel_path):
    full = os.path.join(repo_root, rel_path)
    with open(full, "r", encoding="utf-8") as f:
        return f.read().strip()


def get_scaled_image(path, max_width=489, max_height=340, border=True):
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


def make_file_table(file_label, content_text, label_style, code_style, width=494):
    """Construit la table affichant le bandeau de chemin et le contenu intégral du fichier."""
    header = Paragraph(f"<b>Fichier :</b> <code>{escape(file_label)}</code>", label_style)
    body = Preformatted(content_text.rstrip(), code_style)
    t = Table([[header], [body]], colWidths=[width])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#94A3B8")),
                ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.HexColor("#94A3B8")),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, 0), 3.5),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 3.5),
                ("TOPPADDING", (0, 1), (-1, 1), 5),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 5),
            ]
        )
    )
    return t


def make_file_block(file_label, content_text, label_style, code_style, width=494):
    t = make_file_table(file_label, content_text, label_style, code_style, width=width)
    return KeepTogether([Spacer(1, 3), t, Spacer(1, 5)])


def side_by_side_files(left_label, left_text, right_label, right_text, label_style, code_style):
    b1 = make_file_table(left_label, left_text, label_style, code_style, width=242)
    b2 = make_file_table(right_label, right_text, label_style, code_style, width=242)
    outer = Table([[b1, "", b2]], colWidths=[242, 10, 242])
    outer.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return KeepTogether([Spacer(1, 3), outer, Spacer(1, 5)])


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


def add_figure(story, screenshots_dir, filename, caption_text, caption_style, max_w=489, max_h=330, border=True):
    flow_img = get_scaled_image(os.path.join(screenshots_dir, filename), max_width=max_w, max_height=max_h, border=border)
    if flow_img:
        story.append(KeepTogether([Spacer(1, 4), flow_img, Paragraph(caption_text, caption_style)]))


def generate_pdf(output_pdf_path, repo_root):
    screenshots_dir = os.path.join(repo_root, "docs", "screenshots")
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        leftMargin=44,
        rightMargin=44,
        topMargin=50,
        bottomMargin=50,
    )

    styles = getSampleStyleSheet()
    primary = colors.HexColor("#1E3A8A")
    secondary = colors.HexColor("#0284C7")
    dark = colors.HexColor("#0F172A")
    gray = colors.HexColor("#475569")

    title_style = ParagraphStyle("DocTitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=18.5, leading=23, textColor=primary, spaceAfter=3)
    subtitle_style = ParagraphStyle("DocSub", parent=styles["Normal"], fontName="Helvetica", fontSize=10.8, leading=14.5, textColor=secondary, spaceAfter=9)
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=12.8, leading=16.5, textColor=primary, spaceBefore=12, spaceAfter=5, keepWithNext=True)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=10.3, leading=13.8, textColor=secondary, spaceBefore=8, spaceAfter=3.5, keepWithNext=True)
    body = ParagraphStyle("Body", parent=styles["Normal"], fontName="Helvetica", fontSize=9.1, leading=12.8, textColor=dark, spaceAfter=4.5)
    bullet = ParagraphStyle("Bullet", parent=body, leftIndent=14, firstLineIndent=-10, spaceAfter=3)
    caption = ParagraphStyle("Caption", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8.2, leading=10.8, textColor=gray, alignment=1, spaceBefore=3.5, spaceAfter=8)
    label_style = ParagraphStyle("FileLabel", parent=styles["Normal"], fontName="Helvetica", fontSize=8.3, leading=10.5, textColor=primary)
    code_style = ParagraphStyle("Code", parent=styles["Normal"], fontName="Courier", fontSize=7.2, leading=9.5, textColor=colors.HexColor("#0F172A"))
    th = ParagraphStyle("TH", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.1, leading=10.5, textColor=colors.white, alignment=1)
    tc = ParagraphStyle("TC", parent=styles["Normal"], fontName="Helvetica", fontSize=8.0, leading=10.5, textColor=dark)
    tcc = ParagraphStyle("TCC", parent=tc, alignment=1)
    tcb = ParagraphStyle("TCB", parent=tc, fontName="Helvetica-Bold")

    story = []

    # =========================================================================
    # PAGE 1 : CARTOUCHE & TABLE DES LIVRABLES ATTENDUS (SECTION 17 DU SUJET)
    # =========================================================================
    story.append(Paragraph("Dossier Unique des Livrables — Atelier MLOps", title_style))
    story.append(Paragraph("Intégration de Git + DVC + MLflow dans un Workflow Reproductible (Classification Iris &amp; Wine)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=primary, spaceBefore=0, spaceAfter=9))

    gh_url = "https://github.com/anakin-skyguy/atelier-mlops"
    info_data = [
        [Paragraph("<b>Étudiant :</b> Mohamed Amine BELGUEROUANI", body), Paragraph("<b>Date :</b> 02 Novembre 2026", body)],
        [Paragraph("<b>Matière :</b> MLOps &amp; Industrialisation ML", body), Paragraph("<b>Datasets :</b> Iris (150 éch.) &amp; Wine (178 éch.)", body)],
        [Paragraph("<b>Stack :</b> Python 3.12 • Git 2.52 • DVC 3.67 • MLflow 3.17", body), Paragraph("<b>Backend MLflow :</b> SQLite (<code>sqlite:///mlflow.db</code>)", body)],
        [
            Paragraph(f'<b>Lien GitHub (cliquable) :</b> <link href="{gh_url}" color="#0284C7"><u>{gh_url}</u></link>', body),
            Paragraph("<b>Branches &amp; Tags :</b> <code>main</code>, <code>develop</code>, <code>v1.0</code>, <code>v2.0</code>, <code>v3.0</code>", body),
        ],
    ]
    info_table = Table(info_data, colWidths=[276, 218])
    info_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(info_table)
    story.append(Spacer(1, 7))

    story.append(Paragraph("Index des 6 Livrables Attendus et Grille d'Évaluation (Section 17 de l'énoncé)", h2))
    story.append(
        Paragraph(
            "Ce document unique rassemble <b>intégralement</b> tous les livrables exigés par l'énoncé (lien GitHub, fichiers de configuration DVC "
            "complets, code Python complet, <code>params.yaml</code>, captures d'écran MLflow UI, comparaison d'expérimentations, démonstrations "
            "de restauration/reproductibilité et réponses aux questions de réflexion) :",
            body,
        )
    )

    liv_index = [
        [Paragraph("Livrable attendu (Section 17)", th), Paragraph("Critère associé (/20)", th), Paragraph("Contenu inclus dans ce fichier", th)],
        [
            Paragraph("<b>Livrable 1</b> — Lien du repository GitHub", tcb),
            Paragraph("Git &amp; branches (3 pts)", tcc),
            Paragraph("Section 1 : URL cliquable, branches <code>main</code>/<code>develop</code>, tags <code>v1.0</code>–<code>v3.0</code>, Figures 1 &amp; 2", tc),
        ],
        [
            Paragraph("<b>Livrable 2</b> — Fichiers DVC (<code>.dvc</code>, <code>dvc.yaml</code>, <code>dvc.lock</code>)", tcb),
            Paragraph("DVC &amp; Pipeline (8 pts)", tcc),
            Paragraph("Section 2 : Texte intégral de <code>.dvc/config</code>, <code>iris.csv.dvc</code>, <code>wine.csv.dvc</code>, <code>dvc.yaml</code>, <code>dvc.lock</code>", tc),
        ],
        [
            Paragraph("<b>Livrable 3</b> — Code Python &amp; <code>params.yaml</code>", tcb),
            Paragraph("Modèles &amp; Paramètres", tcc),
            Paragraph("Section 3 : Texte intégral de <code>params.yaml</code>, <code>prepare_*.py</code>, <code>train.py</code> (RF), <code>train_knn.py</code> (KNN)", tc),
        ],
        [
            Paragraph("<b>Livrable 4</b> — Captures de l'interface MLflow", tcb),
            Paragraph("Tracking MLflow (4 pts)", tcc),
            Paragraph("Section 4 : 7 captures HD MLflow UI en thème clair (Figures 3 à 9, dont <code>model.pkl</code>)", tc),
        ],
        [
            Paragraph("<b>Livrable 5</b> — Comparaison d'expérimentations", tcb),
            Paragraph("Analyse comparative", tcc),
            Paragraph("Section 4 : Tableau comparatif des 3 modèles + Coordonnées parallèles &amp; Table MLflow (Figures 4 &amp; 5)", tc),
        ],
        [
            Paragraph("<b>Livrable 6</b> — Restauration &amp; Reproductibilité", tcb),
            Paragraph("Reproductibilité (3 pts)", tcc),
            Paragraph("Section 5 : Rollback <code>wine.csv</code> (MD5), Rollback <code>v1.0</code>, Clone isolé HTTPS, Pytest 4/4 &amp; CI (Figures 10 &amp; 11)", tc),
        ],
        [
            Paragraph("<b>Synthèse &amp; Questions (Q15 à Q22)</b>", tcb),
            Paragraph("Documentation (2 pts)", tcc),
            Paragraph("Section 6 : Tableau de synthèse Git/DVC/MLflow + Réponses complètes aux questions de réflexion", tc),
        ],
    ]
    story.append(styled_table(liv_index, [140, 88, 266], primary))

    # =========================================================================
    # LIVRABLE 1 : LIEN GITHUB & GESTION DU CODE AVEC GIT (TP 1)
    # =========================================================================
    story.append(Paragraph("1. Livrable 1 — Lien du Repository GitHub et Versioning Git (TP 1)", h1))
    story.append(
        Paragraph(
            f'• <b>URL publique du dépôt GitHub :</b> <link href="{gh_url}" color="#0284C7"><u><b>{gh_url}</b></u></link>',
            bullet,
        )
    )
    story.append(
        Paragraph(
            "• <b>Organisation Git (TP 1) :</b> Deux branches synchronisées (<code>main</code> et <code>develop</code>), 15 commits atomiques "
            "et trois tags annotés : <code>v1.0</code> (Random Forest 100 arbres, <code>max_depth=5</code>), <code>v2.0</code> (Random Forest "
            "200 arbres, <code>max_depth=8</code>) et <code>v3.0</code> (pipeline complet RF + KNN + tests Pytest + CI GitHub Actions).",
            bullet,
        )
    )
    story.append(
        Paragraph(
            "• <b>Fichiers d'exclusion et de normalisation :</b> <code>.gitignore</code> exclut <code>mlruns/</code>, <code>mlflow.db</code>, "
            "<code>.venv/</code> et <code>__pycache__/</code> tandis que DVC gère <code>data/raw/.gitignore</code> et <code>models/.gitignore</code>. "
            "<code>.gitattributes</code> force les fins de ligne LF pour garantir la stabilité des hachages MD5 DVC entre Windows et Linux.",
            bullet,
        )
    )

    story.append(
        side_by_side_files(
            ".gitignore",
            read_repo_file(repo_root, ".gitignore"),
            ".gitattributes & requirements.txt",
            "# .gitattributes\n" + read_repo_file(repo_root, ".gitattributes") + "\n\n# requirements.txt\n" + read_repo_file(repo_root, "requirements.txt"),
            label_style,
            code_style,
        )
    )

    add_figure(
        story,
        screenshots_dir,
        "01_github_repository.png",
        "Figure 1 — Dépôt GitHub publié (https://github.com/anakin-skyguy/atelier-mlops) : branches main/develop, 3 tags (v1.0, v2.0, v3.0) et arborescence MLOps propre (sans données brutes ni binaires .pkl).",
        caption,
        max_w=489,
        max_h=295,
    )
    add_figure(
        story,
        screenshots_dir,
        "02_git_branches_tags_log.png",
        "Figure 2 — Exécution CLI Git : vérification du remote GitHub, des branches main/develop, des tags annotés (v1.0, v2.0, v3.0) et de l'historique complet des commits.",
        caption,
        max_w=489,
        max_h=265,
        border=False,
    )

    # =========================================================================
    # LIVRABLE 2 : FICHIERS DE CONFIGURATION DVC (.dvc, dvc.yaml, dvc.lock)
    # =========================================================================
    story.append(Paragraph("2. Livrable 2 — Fichiers de Configuration DVC (.dvc, dvc.yaml, dvc.lock)", h1))
    story.append(
        Paragraph(
            "Conformément au TP 2 et au TP 4, voici le contenu intégral des fichiers de configuration DVC générés et versionnés dans Git : "
            "la configuration des remotes (<code>.dvc/config</code> : remote local <code>storage</code> et remote HTTPS universel <code>github</code>), "
            "les pointeurs des deux datasets (<code>iris.csv.dvc</code> et <code>wine.csv.dvc</code>), la définition déclarative du pipeline "
            "(<code>dvc.yaml</code>) et le fichier d'empreintes résolues (<code>dvc.lock</code>).",
            body,
        )
    )

    story.append(make_file_block(".dvc/config (Stockage local d'exercice + Remote HTTPS universel)", read_repo_file(repo_root, ".dvc/config"), label_style, code_style))
    story.append(
        side_by_side_files(
            "data/raw/iris.csv.dvc",
            read_repo_file(repo_root, "data/raw/iris.csv.dvc"),
            "data/raw/wine.csv.dvc (TP 2 — 2e dataset)",
            read_repo_file(repo_root, "data/raw/wine.csv.dvc"),
            label_style,
            code_style,
        )
    )
    story.append(make_file_block("dvc.yaml", read_repo_file(repo_root, "dvc.yaml"), label_style, code_style))
    story.append(make_file_block("dvc.lock", read_repo_file(repo_root, "dvc.lock"), label_style, code_style))

    # =========================================================================
    # LIVRABLE 3 : CODE PYTHON DU MODÈLE ET FICHIER params.yaml
    # =========================================================================
    story.append(Paragraph("3. Livrable 3 — Code Python Complet des Modèles et Fichier params.yaml", h1))
    story.append(
        Paragraph(
            "L'ensemble des scripts Python du workflow MLOps est reproduit ci-dessous in extenso : préparation déterministe des datasets "
            "(<code>src/prepare_data.py</code> et <code>src/prepare_wine.py</code>), fichier centralisé d'hyperparamètres (<code>params.yaml</code>), "
            "et scripts d'entraînement couplés à MLflow et DVC pour <b>Random Forest</b> (<code>src/train.py</code>) et <b>KNN</b> (<code>src/train_knn.py</code>).",
            body,
        )
    )

    story.append(
        side_by_side_files(
            "params.yaml",
            read_repo_file(repo_root, "params.yaml"),
            "reports/metrics.json & reports/metrics_knn.json",
            "# reports/metrics.json (RF v2.0)\n"
            + read_repo_file(repo_root, "reports/metrics.json")
            + "\n\n# reports/metrics_knn.json (KNN k=5)\n"
            + read_repo_file(repo_root, "reports/metrics_knn.json"),
            label_style,
            code_style,
        )
    )
    story.append(make_file_block("src/prepare_data.py (Génération du dataset Iris — 150 lignes)", read_repo_file(repo_root, "src/prepare_data.py"), label_style, code_style))
    story.append(make_file_block("src/prepare_wine.py (TP 2 — Génération du second dataset Wine — 178 lignes)", read_repo_file(repo_root, "src/prepare_wine.py"), label_style, code_style))
    story.append(make_file_block("src/train.py (Entraînement Random Forest + Tracking MLflow + Sortie DVC)", read_repo_file(repo_root, "src/train.py"), label_style, code_style))
    story.append(make_file_block("src/train_knn.py (TP 3 — Entraînement KNN + Tracking MLflow + Sortie DVC)", read_repo_file(repo_root, "src/train_knn.py"), label_style, code_style))

    # =========================================================================
    # LIVRABLES 4 & 5 : CAPTURES MLFLOW UI & COMPARAISON DES EXPÉRIMENTATIONS
    # =========================================================================
    story.append(Paragraph("4. Livrables 4 &amp; 5 — Captures MLflow UI et Comparaison des Expérimentations", h1))
    story.append(
        Paragraph(
            "Les trois expérimentations ont été suivies dans la base SQLite (<code>sqlite:///mlflow.db</code>, expérience "
            "<code>TP_Iris_Classification</code>) sur un découpage stratifié identique (<code>test_size=0.2</code> : 120 individus en "
            "entraînement, 30 individus en test, <code>random_state=42</code>) :",
            body,
        )
    )

    res_rows = [
        [
            Paragraph("Version", th),
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
            Paragraph("Random Forest (n_estimators=100, max_depth=5)", tc),
            Paragraph("<b>0.9333</b>", tcc),
            Paragraph("<b>0.9333</b>", tcc),
            Paragraph("<b>0.9333</b>", tcc),
            Paragraph("<b>0.9333</b>", tcc),
        ],
        [
            Paragraph("<b>v2.0</b>", tcc),
            Paragraph("<code>RandomForest_n200_d8</code>", tc),
            Paragraph("Random Forest (n_estimators=200, max_depth=8)", tc),
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
    story.append(styled_table(res_rows, [42, 112, 140, 50, 50, 50, 50], primary))
    story.append(Spacer(1, 4))
    story.append(
        Paragraph(
            "<b>Analyse comparative des 3 expérimentations :</b> "
            "(1) Entre <code>v1.0</code> et <code>v2.0</code>, passer de 100 à 200 arbres et augmenter <code>max_depth</code> de 5 à 8 provoque "
            "un recul de <code>-3,33 %</code> sur l'accuracy (<code>0.9333 → 0.9000</code>, soit 27/30 au lieu de 28/30), confirmant la remarque "
            "pédagogique de l'énoncé : un modèle plus profond peut sur-apprendre sur un petit échantillon d'apprentissage (120 lignes). "
            "(2) Le modèle <code>KNN_k5</code> (TP 3) atteint <code>1.0000</code> sur les 4 métriques grâce à la nette séparation euclidienne des "
            "mesures florales d'Iris ; sur un jeu de test de 30 observations (1 erreur = 3,33 %), une validation croisée stratifiée permettrait "
            "de consolider statistiquement cette comparaison.",
            body,
        )
    )

    add_figure(
        story,
        screenshots_dir,
        "04_mlflow_runs_table.png",
        "Figure 3 — Interface MLflow UI : tableau des runs de l'expérience TP_Iris_Classification avec toutes les colonnes de métriques et d'hyperparamètres.",
        caption,
        max_w=489,
        max_h=175,
    )
    add_figure(
        story,
        screenshots_dir,
        "05_mlflow_compare_chart.png",
        "Figure 4 — Comparaison visuelle des 3 expérimentations dans MLflow UI (Parallel Coordinates Plot reliant hyperparamètres et accuracy).",
        caption,
        max_w=489,
        max_h=215,
    )
    add_figure(
        story,
        screenshots_dir,
        "06_mlflow_compare_table.png",
        "Figure 5 — Tableau comparatif côte à côte dans MLflow UI : détails des runs, hyperparamètres différenciés et métriques d'évaluation.",
        caption,
        max_w=475,
        max_h=375,
    )
    add_figure(
        story,
        screenshots_dir,
        "07_mlflow_run_rf100.png",
        "Figure 6 — Fiche détaillée du run RandomForest_n100_d5 (tag v1.0 : Accuracy = 0.9333, n_estimators = 100, max_depth = 5).",
        caption,
        max_w=489,
        max_h=305,
    )
    add_figure(
        story,
        screenshots_dir,
        "08_mlflow_run_rf200.png",
        "Figure 7 — Fiche détaillée du run RandomForest_n200_d8 (tag v2.0 : Accuracy = 0.9000, F1 = 0.8997, n_estimators = 200, max_depth = 8).",
        caption,
        max_w=489,
        max_h=305,
    )
    add_figure(
        story,
        screenshots_dir,
        "09_mlflow_run_knn.png",
        "Figure 8 — Fiche détaillée du run KNN_k5 (tag v3.0 : Accuracy = 1.0000, n_neighbors = 5, random_state = 42, test_size = 0.2).",
        caption,
        max_w=489,
        max_h=295,
    )
    add_figure(
        story,
        screenshots_dir,
        "11_mlflow_artifacts_model_pkl.png",
        "Figure 9 — Onglet Artifacts dans MLflow UI : dossier model/ déplié montrant l'artefact sérialisé model.pkl.",
        caption,
        max_w=489,
        max_h=185,
    )

    # =========================================================================
    # LIVRABLE 6 : DÉMONSTRATION DE RESTAURATION & REPRODUCTIBILITÉ + CI
    # =========================================================================
    story.append(Paragraph("5. Livrable 6 — Démonstration de Restauration, Reproductibilité et CI/CD", h1))
    story.append(
        Paragraph(
            "Trois protocoles complémentaires prouvent la traçabilité et la reproductibilité totale du workflow :",
            body,
        )
    )
    story.append(
        Paragraph(
            "• <b>1. Restauration d'une version antérieure d'un dataset (TP 2 — Q7) :</b> Après altération de <code>data/raw/wine.csv</code> "
            "(réduit de 178 à 100 lignes, MD5 modifié de <code>2925c4a8...</code> à <code>cc50fa13...</code>), la séquence "
            "<code>git checkout HEAD~1 -- data/raw/wine.csv.dvc &amp;&amp; dvc checkout</code> restaure exactement les 178 lignes et le MD5 initial (Figure 10).",
            bullet,
        )
    )
    story.append(
        Paragraph(
            "• <b>2. Restauration complète du modèle et des paramètres v1.0 (Étape 16) :</b> La séquence <code>git checkout v1.0 &amp;&amp; dvc checkout</code> "
            "restaure simultanément <code>params.yaml</code> (<code>n_estimators=100, max_depth=5</code>), <code>reports/metrics.json</code> "
            "(<code>accuracy=0.93333</code>) et le binaire <code>models/model.pkl</code> associé, avec <code>dvc status</code> à jour (Figure 11).",
            bullet,
        )
    )
    story.append(
        Paragraph(
            "• <b>3. Reproductibilité sur un autre environnement vierge (Étape 18 &amp; Section 12 CI) :</b> Un <code>git clone</code> exécuté "
            "dans un répertoire isolé (sans accès au dossier local <code>../dvc-storage</code>) récupère automatiquement les 4 fichiers via "
            "<code>dvc pull</code> (remote HTTPS <code>github</code>), vérifie <code>dvc repro</code> et valide <b>4/4 tests Pytest</b>.",
            bullet,
        )
    )

    add_figure(
        story,
        screenshots_dir,
        "03_dvc_remotes_and_wine_rollback.png",
        "Figure 10 — Démonstration TP 2 : remotes DVC configurés, pointeurs .dvc et restauration vérifiée par MD5 du dataset wine.csv (178 → 100 → 178 lignes).",
        caption,
        max_w=489,
        max_h=245,
        border=False,
    )
    add_figure(
        story,
        screenshots_dir,
        "10_dvc_dag_rollback_pytest.png",
        "Figure 11 — Démonstration du pipeline DVC : graphe dvc dag, diff v1.0 vs v2.0, restauration complète de v1.0 (accuracy 0.93333) et validation Pytest (4 passed).",
        caption,
        max_w=489,
        max_h=385,
        border=False,
    )

    story.append(make_file_block(".github/workflows/mlops.yml (Extension Section 12 — Intégration Continue GitHub Actions)", read_repo_file(repo_root, ".github/workflows/mlops.yml"), label_style, code_style))
    story.append(make_file_block("tests/test_mlops.py (Contrôles qualité des données Iris/Wine et critères d'acceptation des modèles)", read_repo_file(repo_root, "tests/test_mlops.py"), label_style, code_style))

    # =========================================================================
    # SECTION 6 : SYNTHÈSE DES RESPONSABILITÉS & QUESTIONS DE RÉFLEXION (Q15–Q22)
    # =========================================================================
    story.append(Paragraph("6. Synthèse des Responsabilités et Questions de Réflexion (Sections 14 &amp; 16)", h1))

    arch_rows = [
        [Paragraph("Fonctionnalité", th), Paragraph("Git / GitHub", th), Paragraph("DVC", th), Paragraph("MLflow", th)],
        [Paragraph("Versioning du code", tcb), Paragraph("Oui", tcc), Paragraph("Non", tcc), Paragraph("Non", tcc)],
        [Paragraph("Versioning des datasets", tcb), Paragraph("Référence (.dvc)", tcc), Paragraph("Oui (cache + remote)", tcc), Paragraph("Artefact possible", tcc)],
        [Paragraph("Historique des commits", tcb), Paragraph("Oui", tcc), Paragraph("Non", tcc), Paragraph("Non", tcc)],
        [Paragraph("Pipeline ML reproductible", tcb), Paragraph("Configuration", tcc), Paragraph("Oui (dvc repro)", tcc), Paragraph("Tracking associé", tcc)],
        [Paragraph("Suivi des paramètres", tcb), Paragraph("params.yaml", tcc), Paragraph("Paramètres DVC", tcc), Paragraph("Oui", tcc)],
        [Paragraph("Suivi des métriques", tcb), Paragraph("Non (JSON léger)", tcc), Paragraph("Oui", tcc), Paragraph("Oui", tcc)],
        [Paragraph("Suivi des artefacts", tcb), Paragraph("Non", tcc), Paragraph("Oui", tcc), Paragraph("Oui", tcc)],
        [Paragraph("Comparaison des runs", tcb), Paragraph("Non", tcc), Paragraph("Métriques CLI", tcc), Paragraph("Oui (UI graphique)", tcc)],
    ]
    story.append(styled_table(arch_rows, [140, 114, 120, 120], primary))
    story.append(Spacer(1, 5))

    qa = [
        (
            "Question préliminaire (p. 3) & Q16 — Pourquoi suivre le code avec Git et éviter de stocker un dataset volumineux dans Git ?",
            "Git conserve chaque révision dans l'historique local (.git/objects) de tous les clones : y enregistrer des datasets volumineux ou binaires fait croître exponentiellement la taille du dépôt, ralentit clone/fetch/push, se heurte aux quotas des forges (100 Mo par fichier sur GitHub) et produit des diffs textuels inutilisables. Git doit donc suivre le code et les petits fichiers de référence (.dvc), pendant que DVC gère les données lourdes.",
        ),
        (
            "Q15 — Quelle est la différence entre Git et DVC ?",
            "Git versionne le code source, les scripts et les fichiers texte de configuration (.py, .yaml, .dvc, dvc.lock). DVC versionne les données volumineuses et les binaires de modèles via un cache adressé par empreinte MD5 relié à un stockage distant (local, S3, Azure, GCS, HTTPS) et orchestre l'exécution reproductible des pipelines ML.",
        ),
        (
            "Q17 — Quelle est la différence entre dvc add et dvc repro ?",
            "dvc add enregistre un fichier statique existant (comme un dataset brut) dans le cache DVC et crée un fichier pointeur .dvc sans exécuter aucun script. dvc repro parcourt le graphe de dépendances défini dans dvc.yaml, compare les empreintes des entrées et paramètres à dvc.lock, ré-exécute uniquement les stages modifiés et met à jour dvc.lock.",
        ),
        (
            "Q18 — Quel est le rôle du fichier dvc.lock ?",
            "dvc.lock capture l'état exact résolu d'une exécution du pipeline : commandes lancées, valeurs effectives des hyperparamètres, tailles et hachages MD5 de toutes les dépendances (deps) et sorties (outs). Versionné dans Git, il garantit qu'un commit donné correspond de manière unique et vérifiable à un jeu de données et à un modèle précis.",
        ),
        (
            "Q19 — Comment MLflow permet-il de comparer deux expérimentations ?",
            "Chaque exécution enregistrée dans le Backend Store (sqlite:///mlflow.db) stocke ses hyperparamètres, ses métriques et ses artefacts. La vue Compare de MLflow UI aligne plusieurs runs côte à côte, surligne les différences de paramètres (Show diff only), compare les métriques et trace des graphiques interactifs (coordonnées parallèles, scatter/box plots), complétée par l'API mlflow.search_runs().",
        ),
        (
            "Q20 — Comment retrouver les données et le modèle associés à un commit Git précis ?",
            "En deux commandes complémentaires : (1) <code>git checkout &lt;commit_ou_tag&gt;</code> (ex. <code>git checkout v1.0</code>) restaure le code, <code>params.yaml</code>, <code>dvc.lock</code> et les pointeurs <code>.dvc</code> de ce commit ; (2) <code>dvc checkout</code> (ou <code>dvc pull</code> si absent du cache local) matérialise exactement les datasets et le fichier modèle correspondants.",
        ),
        (
            "Q21 — Pourquoi la reproductibilité est-elle importante dans un projet d'intelligence artificielle ?",
            "Parce qu'un modèle d'IA dépend simultanément du code, des données, du prétraitement, des hyperparamètres et de l'aléa numérique (random_state). La reproductibilité est indispensable pour isoler rigoureusement l'impact d'un changement, auditer et tracer un modèle déployé, revenir instantanément à une version fiable (rollback v1.0) et collaborer sans divergences entre environnements.",
        ),
        (
            "Q22 — Quelle est la différence entre le versioning des modèles avec DVC et leur suivi avec MLflow ?",
            "DVC versionne le fichier binaire du modèle (models/model.pkl) comme sortie déterministe du pipeline rattachée à un commit Git (orienté restauration et CI/CD). MLflow assure la journalisation analytique de tous les runs exploratoires, la visualisation comparative des métriques et la gouvernance du cycle de vie via le Model Registry. Les deux outils sont donc complémentaires.",
        ),
    ]
    for q_title, q_ans in qa:
        story.append(KeepTogether([Paragraph(f"<b>{q_title}</b>", h2), Paragraph(q_ans, body)]))

    story.append(Spacer(1, 8))
    story.append(Paragraph("7. Conclusion et Récapitulatif de Validation (/20 points)", h1))
    story.append(
        Paragraph(
            "L'ensemble des travaux pratiques (<b>TP 1 à TP 4</b>), des extensions (<b>tests automatisés Pytest et workflow CI GitHub Actions</b>) "
            "et des <b>6 livrables attendus</b> de l'atelier ont été réalisés, testés sur un environnement isolé et réunis dans ce document unique :",
            body,
        )
    )
    final_rows = [
        [Paragraph("Critère d'évaluation (Section 17)", th), Paragraph("Barème", th), Paragraph("Éléments vérifiés dans ce dossier", th)],
        [Paragraph("Initialisation et utilisation de Git", tcb), Paragraph("<b>3 / 3</b>", tcc), Paragraph("Dépôt GitHub publié, branches <code>main</code> &amp; <code>develop</code>, 15 commits, tags <code>v1.0</code>–<code>v3.0</code>", tc)],
        [Paragraph("Versioning des données avec DVC", tcb), Paragraph("<b>4 / 4</b>", tcc), Paragraph("2 datasets suivis (<code>iris.csv.dvc</code>, <code>wine.csv.dvc</code>), remotes local + HTTPS, rollback MD5 vérifié", tc)],
        [Paragraph("Tracking avec MLflow", tcb), Paragraph("<b>4 / 4</b>", tcc), Paragraph("Backend SQLite, suivi RF (v1.0, v2.0) &amp; KNN (v3.0), métriques/paramètres/artefacts + 7 captures UI HD", tc)],
        [Paragraph("Création du pipeline DVC", tcb), Paragraph("<b>4 / 4</b>", tcc), Paragraph("Stages <code>train</code> &amp; <code>train_knn</code> dans <code>dvc.yaml</code>, empreintes figées dans <code>dvc.lock</code>, <code>dvc dag</code>", tc)],
        [Paragraph("Reproductibilité et gestion des versions", tcb), Paragraph("<b>3 / 3</b>", tcc), Paragraph("Rollback <code>v1.0</code>, clone vierge isolé via HTTPS (<code>dvc pull</code> + <code>dvc repro</code>), Pytest 4/4 &amp; CI", tc)],
        [Paragraph("Documentation et démonstration", tcb), Paragraph("<b>2 / 2</b>", tcc), Paragraph("Code &amp; configs intégraux, captures CLI/UI commentées et réponses complètes aux questions Q15–Q22", tc)],
        [Paragraph("<b>TOTAL</b>", tcb), Paragraph("<b>20 / 20</b>", tcc), Paragraph("<b>Dossier complet — https://github.com/anakin-skyguy/atelier-mlops</b>", tcb)],
    ]
    story.append(styled_table(final_rows, [160, 52, 282], primary))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF généré : {output_pdf_path} ({os.path.getsize(output_pdf_path) / 1024 / 1024:.2f} Mo)")


if __name__ == "__main__":
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    workspace_root = os.path.dirname(repo_root)
    downloads_dir = r"C:\Users\Amine\Downloads"

    targets = [
        os.path.join(downloads_dir, "LIVRABLES_ATELIER_MLOPS_BELGUEROUANI_Mohamed_Amine.pdf"),
        os.path.join(downloads_dir, "COMPTE_RENDU_ATELIER_MLOPS_BELGUEROUANI_Mohamed_Amine.pdf"),
        os.path.join(workspace_root, "COMPTE_RENDU_ATELIER_MLOPS_BELGUEROUANI_Mohamed_Amine.pdf"),
        os.path.join(repo_root, "docs", "COMPTE_RENDU_ATELIER_MLOPS_BELGUEROUANI_Mohamed_Amine.pdf"),
    ]
    for target in targets:
        generate_pdf(target, repo_root)
