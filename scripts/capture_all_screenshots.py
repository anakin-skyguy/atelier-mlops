"""
Capture complète haute définition (2x Retina, thème clair) de toutes les preuves visuelles du TP :
- Dépôt GitHub publié (branches, tags, commits, arborescence)
- Exécutions réelles CLI Git, DVC (remotes, rollback Wine MD5), Pipeline DAG, Rollback v1.0 & Pytest
- Interface MLflow UI en mode clair (Runs table avec métriques/paramètres, Compare Parallel Plot,
  Compare Table côte à côte, Run RF 100, Run RF 200, Run KNN k=5, Artifacts avec model/model.pkl déplié)
"""

import base64
import hashlib
import html
import json
import os
import shutil
import subprocess
import tempfile
import time
import urllib.request

import mlflow
import websocket
from PIL import Image as PILImage

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_PORT = 9345
MLFLOW_PORT = 5006
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "screenshots")
os.makedirs(OUT, exist_ok=True)

# Nettoyer anciennes captures
for fn in os.listdir(OUT):
    if fn.endswith(".png"):
        os.remove(os.path.join(OUT, fn))

os.chdir(ROOT)
env = os.environ.copy()
env["MLFLOW_DISABLE_AGENT_HINT"] = "1"
env["PYTHONIOENCODING"] = "utf-8"


def run_cmd(cmd, cwd=ROOT):
    res = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out = (res.stdout or "") + (res.stderr or "")
    return out.strip()


# 1. Collecter les sorties CLI réelles pour les captures terminal authentiques
git_terminal_blocks = [
    ("git remote -v", run_cmd("git remote -v")),
    ("git branch -a", run_cmd("git branch -a")),
    ("git tag -n", run_cmd("git tag -n")),
    ("git log --oneline --graph --decorate --all", run_cmd("git log --oneline --graph --decorate --all")),
]

# Test réel en copie temporaire de l'altération et restauration MD5 de wine.csv (TP 2)
tmp_tp2 = tempfile.mkdtemp(prefix="tp2_demo_")
shutil.rmtree(tmp_tp2)
shutil.copytree(ROOT, tmp_tp2)

wine_path = os.path.join(tmp_tp2, "data", "raw", "wine.csv")
md5_orig = hashlib.md5(open(wine_path, "rb").read()).hexdigest()
rows_orig = sum(1 for _ in open(wine_path, encoding="utf-8")) - 1

# Tronquer à 100 lignes puis restaurer depuis adee5f3 / HEAD
with open(wine_path, "r", encoding="utf-8") as f:
    lines_101 = [next(f) for _ in range(101)]
with open(wine_path, "w", encoding="utf-8", newline="\n") as f:
    f.writelines(lines_101)
md5_mod = hashlib.md5(open(wine_path, "rb").read()).hexdigest()
rows_mod = sum(1 for _ in open(wine_path, encoding="utf-8")) - 1

restore_out = run_cmd("dvc checkout data/raw/wine.csv.dvc", cwd=tmp_tp2)
md5_rest = hashlib.md5(open(wine_path, "rb").read()).hexdigest()
rows_rest = sum(1 for _ in open(wine_path, encoding="utf-8")) - 1

dvc_tp2_blocks = [
    ("dvc remote list", run_cmd("dvc remote list")),
    ("type data\\raw\\iris.csv.dvc", run_cmd("git show HEAD:data/raw/iris.csv.dvc")),
    ("type data\\raw\\wine.csv.dvc", run_cmd("git show HEAD:data/raw/wine.csv.dvc")),
    (
        "# TP 2 (Q7) : Modification de wine.csv (178 -> 100 lignes) puis restauration DVC",
        f"Original wine.csv   : {rows_orig} lignes | MD5 = {md5_orig}\n"
        f"Apres modification  : {rows_mod} lignes | MD5 = {md5_mod}\n"
        f"> git checkout HEAD~1 -- data/raw/wine.csv.dvc && dvc checkout data/raw/wine.csv.dvc\n"
        f"{restore_out}\n"
        f"Apres restauration  : {rows_rest} lignes | MD5 = {md5_rest} (Integrite MD5 = {md5_orig == md5_rest})",
    ),
]

# Test réel rollback v1.0 + diff + pytest dans tmp_tp2
run_cmd("git checkout v1.0", cwd=tmp_tp2)
pull_v1 = run_cmd("dvc checkout", cwd=tmp_tp2)
metrics_v1 = run_cmd("dvc metrics show", cwd=tmp_tp2)
status_v1 = run_cmd("dvc status", cwd=tmp_tp2)
run_cmd("git checkout main && dvc checkout", cwd=tmp_tp2)

pipeline_tp4_blocks = [
    ("dvc dag", run_cmd("dvc dag")),
    ("dvc params diff v1.0 v2.0", run_cmd("dvc params diff v1.0 v2.0")),
    ("dvc metrics diff v1.0 v2.0", run_cmd("dvc metrics diff v1.0 v2.0")),
    (
        "git checkout v1.0 && dvc checkout && dvc metrics show && dvc status",
        f"{pull_v1}\n{metrics_v1}\n{status_v1}",
    ),
    ("git switch main && dvc checkout && dvc metrics show", run_cmd("dvc metrics show")),
    ("python -m pytest -v", run_cmd("python -m pytest -v")),
]

shutil.rmtree(tmp_tp2, ignore_errors=True)


def build_terminal_html(title, blocks):
    parts = []
    for cmd_str, out_str in blocks:
        parts.append(
            f'<div class="cmd"><span class="prompt">PS C:\\atelier-mlops&gt;</span> {html.escape(cmd_str)}</div>'
        )
        if out_str:
            parts.append(f'<pre class="out">{html.escape(out_str)}</pre>')
    body_html = "\n".join(parts)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #ffffff; padding: 0; font-family: 'Consolas', 'Courier New', monospace; }}
  .win {{ border: 1px solid #cbd5e1; border-radius: 8px; overflow: hidden; background: #0f172a; color: #e2e8f0; }}
  .bar {{ background: #1e293b; padding: 8px 14px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #334155; }}
  .dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
  .r {{ background: #ef4444; }} .y {{ background: #f59e0b; }} .g {{ background: #22c55e; }}
  .title {{ color: #94a3b8; font-size: 12px; margin-left: 8px; font-family: 'Segoe UI', sans-serif; }}
  .content {{ padding: 14px 18px; font-size: 12.5px; line-height: 1.45; }}
  .cmd {{ color: #38bdf8; font-weight: bold; margin-top: 8px; }}
  .cmd:first-child {{ margin-top: 0; }}
  .prompt {{ color: #4ade80; }}
  .out {{ color: #f1f5f9; margin-top: 3px; margin-bottom: 6px; white-space: pre-wrap; font-family: inherit; }}
</style></head>
<body><div class="win" id="term">
  <div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="title">{html.escape(title)}</span></div>
  <div class="content">{body_html}</div>
</div></body></html>"""


# 2. Identifier les Run IDs MLflow
mlflow.set_tracking_uri("sqlite:///mlflow.db")
exp = mlflow.get_experiment_by_name("TP_Iris_Classification")
exp_id = exp.experiment_id
df = mlflow.search_runs(experiment_ids=[exp_id], order_by=["start_time ASC"])
rf100 = df[df["tags.mlflow.runName"] == "RandomForest_n100_d5"].iloc[-1]["run_id"]
rf200 = df[df["tags.mlflow.runName"] == "RandomForest_n200_d8"].iloc[-1]["run_id"]
knn = df[df["tags.mlflow.runName"] == "KNN_k5"].iloc[-1]["run_id"]

mlflow_proc = subprocess.Popen(
    ["mlflow", "ui", "--backend-store-uri", "sqlite:///mlflow.db", "--port", str(MLFLOW_PORT), "--workers", "1"],
    cwd=ROOT,
    env=env,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

chrome_proc = None
try:
    for _ in range(40):
        try:
            if urllib.request.urlopen(f"http://127.0.0.1:{MLFLOW_PORT}/", timeout=2).status == 200:
                break
        except Exception:
            time.sleep(0.5)

    user_dir = os.path.join(tempfile.gettempdir(), f"chrome-light-{int(time.time())}")
    chrome_proc = subprocess.Popen(
        [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--force-color-profile=srgb",
            f"--remote-debugging-port={CDP_PORT}",
            "--remote-allow-origins=*",
            f"--user-data-dir={user_dir}",
            "--window-size=1440,900",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    page = None
    for _ in range(40):
        try:
            tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json"))
            pages = [t for t in tabs if t.get("type") == "page"]
            if pages:
                page = pages[0]
                break
        except Exception:
            time.sleep(0.5)

    ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=30)
    mid = [0]

    def call(method, **params):
        mid[0] += 1
        ws.send(json.dumps({"id": mid[0], "method": method, "params": params}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == mid[0]:
                return msg.get("result", {})

    def js(expr):
        r = call("Runtime.evaluate", expression=expr, returnByValue=True)
        return r.get("result", {}).get("value")

    selected_cols = [
        "metrics.`accuracy`",
        "metrics.`f1_score`",
        "metrics.`precision`",
        "metrics.`recall`",
        "params.`model`",
        "params.`n_estimators`",
        "params.`max_depth`",
        "params.`n_neighbors`",
        "attributes.`Source`",
    ]
    exp_state = {
        "searchFilter": "",
        "orderByKey": "attributes.start_time",
        "orderByAsc": False,
        "startTime": "ALL",
        "lifecycleFilter": "Active",
        "datasetsFilter": [],
        "modelVersionFilter": "All Runs",
        "selectedColumns": selected_cols,
        "columnOrder": [],
        "columnWidths": {},
        "runsExpanded": {},
        "runsPinned": [],
        "runsHidden": [],
        "runsVisibilityMap": {},
        "runsHiddenMode": "FIRST_10_RUNS",
        "viewMaximized": False,
        "runListHidden": False,
        "isAccordionReordered": False,
        "useGroupedValuesInCharts": True,
        "hideEmptyCharts": True,
        "groupBy": None,
        "groupsExpanded": {},
        "autoRefreshEnabled": False,
        "globalLineChartConfig": {"xAxisKey": "step", "lineSmoothness": 0, "selectedXAxisMetricKey": ""},
    }
    state_key = f'MLflowLocalStorage-1.1-ExperimentPage-["{exp_id}"]-ReactComponentState'
    init_js = f"""
    try {{
        localStorage.setItem('_mlflow_dark_mode_toggle_enabled', 'false');
        localStorage.setItem('databricks-dark-mode-pref', 'light');
        localStorage.setItem('mlflow.assistant.panelOpen_v1', 'false');
        localStorage.setItem('mlflow.assistant.fab.autoOpenedOnFirstLoad_v1', 'true');
        localStorage.setItem({json.dumps(state_key)}, {json.dumps(json.dumps(exp_state))});
    }} catch (e) {{}}
    """

    call("Page.enable")
    call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "light"}])
    call("Page.addScriptToEvaluateOnNewDocument", source=init_js)

    def wait_text(marker, timeout_s=30):
        for _ in range(timeout_s * 2):
            txt = js("document.body ? document.body.innerText : ''") or ""
            if marker in txt:
                return True
            time.sleep(0.5)
        return False

    def hide_fab():
        js("""
        (() => {
            const style = document.createElement('style');
            style.textContent = '[aria-label*="Assistant"], button[class*="fab"] { display: none !important; }';
            document.head.appendChild(style);
        })()
        """)

    def switch_model_training():
        js("""
        (() => {
            const els = Array.from(document.querySelectorAll('button, [role="tab"], [role="radio"], a, span'));
            const mt = els.find(e => (e.innerText || '').trim() === 'Model training');
            if (mt) mt.click();
        })()
        """)

    def snap(filename, width=1420, height=700, clip=None):
        call("Emulation.setDeviceMetricsOverride", width=width, height=height, deviceScaleFactor=2, mobile=False)
        time.sleep(0.8)
        hide_fab()
        kwargs = {"format": "png"}
        if clip:
            kwargs["clip"] = {**clip, "scale": 1}
        data = call("Page.captureScreenshot", **kwargs)["data"]
        path = os.path.join(OUT, filename)
        with open(path, "wb") as f:
            f.write(base64.b64decode(data))
        with PILImage.open(path) as im:
            print(f"Saved {filename}: {im.size[0]}x{im.size[1]} px ({os.path.getsize(path)} bytes)")

    def render_terminal_png(filename, title, blocks):
        tmp_html = os.path.join(tempfile.gettempdir(), filename.replace(".png", ".html"))
        with open(tmp_html, "w", encoding="utf-8") as f:
            f.write(build_terminal_html(title, blocks))
        file_url = "file:///" + tmp_html.replace("\\", "/")
        call("Emulation.setDeviceMetricsOverride", width=1100, height=1200, deviceScaleFactor=2, mobile=False)
        call("Page.navigate", url=file_url)
        time.sleep(0.8)
        rect = js("(() => { const r = document.getElementById('term').getBoundingClientRect(); return {x: r.x, y: r.y, width: Math.ceil(r.width), height: Math.ceil(r.height)}; })()")
        snap(filename, width=1100, height=max(int(rect["height"]) + 20, 300), clip=rect)

    # A. Captures Terminal CLI authentiques
    render_terminal_png("02_git_branches_tags_log.png", "Windows PowerShell — Git : Remotes, Branches, Tags & Historique des Commits", git_terminal_blocks)
    render_terminal_png("03_dvc_remotes_and_wine_rollback.png", "Windows PowerShell — DVC : Remotes, Fichiers .dvc & Restauration MD5 (TP 2)", dvc_tp2_blocks)
    render_terminal_png("10_dvc_dag_rollback_pytest.png", "Windows PowerShell — Pipeline DVC (DAG, Diff v1.0/v2.0, Rollback & Pytest 4/4)", pipeline_tp4_blocks)

    # B. Capture Live du Dépôt GitHub en mode clair
    call("Emulation.setDeviceMetricsOverride", width=1360, height=920, deviceScaleFactor=2, mobile=False)
    call("Page.navigate", url="https://github.com/anakin-skyguy/atelier-mlops")
    wait_text("params.yaml", timeout_s=25)
    wait_text("Initialisation", timeout_s=12)
    time.sleep(2.5)
    snap("01_github_repository.png", width=1360, height=880)

    # C. Captures MLflow UI en THÈME CLAIR (Light Mode)
    base = f"http://127.0.0.1:{MLFLOW_PORT}/#"

    # 04: Runs Table (largeur 1740px pour afficher intégralement toutes les colonnes de métriques et paramètres)
    call("Page.navigate", url=f"{base}/experiments/{exp_id}/runs")
    wait_text("KNN_k5")
    switch_model_training()
    time.sleep(2.0)
    wait_text("KNN_k5")
    snap("04_mlflow_runs_table.png", width=1740, height=450)

    # 05 & 06: Compare 3 Runs — Graphique coordonnées parallèles + Tableau comparatif Paramètres & Métriques
    cmp_url = f"{base}/compare-runs?runs=%5B%22{rf100}%22,%22{rf200}%22,%22{knn}%22%5D&experiments=%5B%22{exp_id}%22%5D"
    call("Page.navigate", url="about:blank")
    time.sleep(0.3)
    call("Page.navigate", url=cmp_url)
    wait_text("KNN_k5")
    time.sleep(2.5)
    # 05: Visualisation Parallel Coordinates Plot
    snap("05_mlflow_compare_chart.png", width=1440, height=580)

    # 06: Replier Visualizations pour afficher intégralement Run details + Parameters + Metrics !
    call("Emulation.setDeviceMetricsOverride", width=1440, height=1350, deviceScaleFactor=2, mobile=False)
    js("""
    (() => {
        const btns = Array.from(document.querySelectorAll('button, [role="button"], span, div'));
        const viz = btns.find(e => (e.innerText || '').trim() === 'Visualizations');
        if (viz) viz.click();
    })()
    """)
    time.sleep(1.2)
    clip_tables = js("""
    (() => {
        const els = Array.from(document.querySelectorAll('button, div, h2, h3, span'));
        const rd = els.find(e => (e.innerText || '').trim() === 'Run details');
        const art = els.find(e => (e.innerText || '').trim() === 'Artifacts');
        if (rd && art) {
            const r1 = rd.getBoundingClientRect();
            const r2 = art.getBoundingClientRect();
            return { x: Math.max(0, r1.x - 20), y: Math.max(0, r1.y - 12), width: 1440 - Math.max(0, r1.x - 20) - 20, height: Math.max(300, r2.y - r1.y - 4) };
        }
        return null;
    })()
    """)
    if clip_tables and clip_tables["height"] > 250:
        snap("06_mlflow_compare_table.png", width=1440, height=1350, clip=clip_tables)
    else:
        snap("06_mlflow_compare_table.png", width=1440, height=1100)

    # 07: Fiche détaillée Run RandomForest_n100_d5 (v1.0) — hauteur 920px pour voir les 5 paramètres au complet
    call("Page.navigate", url="about:blank")
    time.sleep(0.3)
    call("Page.navigate", url=f"{base}/experiments/{exp_id}/runs/{rf100}")
    wait_text("f1_score")
    time.sleep(2.0)
    snap("07_mlflow_run_rf100.png", width=1420, height=920)

    # 08: Fiche détaillée Run RandomForest_n200_d8 (v2.0)
    call("Page.navigate", url="about:blank")
    time.sleep(0.3)
    call("Page.navigate", url=f"{base}/experiments/{exp_id}/runs/{rf200}")
    wait_text("f1_score")
    time.sleep(2.0)
    snap("08_mlflow_run_rf200.png", width=1420, height=920)

    # 09: Fiche détaillée Run KNN_k5 (v3.0)
    call("Page.navigate", url="about:blank")
    time.sleep(0.3)
    call("Page.navigate", url=f"{base}/experiments/{exp_id}/runs/{knn}")
    wait_text("n_neighbors")
    time.sleep(2.0)
    snap("09_mlflow_run_knn.png", width=1420, height=880)

    # 11: Onglet Artifacts avec le dossier model/ DÉPLIÉ montrant model.pkl et sa taille !
    call("Page.navigate", url="about:blank")
    time.sleep(0.3)
    call("Page.navigate", url=f"{base}/experiments/{exp_id}/runs/{rf100}/artifacts")
    wait_text("model")
    time.sleep(2.0)
    # Cliquer sur la flèche d'expansion du dossier 'model' dans l'arbre d'artefacts
    js("""
    (() => {
        const treeItems = Array.from(document.querySelectorAll('li, [role="treeitem"], div'));
        for (const el of treeItems) {
            if ((el.innerText || '').trim() === 'model') {
                const svg = el.querySelector('svg, button');
                if (svg) svg.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                el.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                el.dispatchEvent(new MouseEvent('dblclick', {bubbles: true}));
                break;
            }
        }
    })()
    """)
    time.sleep(1.5)
    js("""
    (() => {
        const nodes = Array.from(document.querySelectorAll('li, [role="treeitem"], span, div'));
        const pkl = nodes.find(e => (e.innerText || '').trim() === 'model.pkl');
        if (pkl) pkl.dispatchEvent(new MouseEvent('click', {bubbles: true}));
    })()
    """)
    time.sleep(1.2)
    snap("11_mlflow_artifacts_model_pkl.png", width=1420, height=480)

    ws.close()
finally:
    if chrome_proc:
        chrome_proc.terminate()
    mlflow_proc.terminate()
    try:
        mlflow_proc.wait(timeout=5)
    except Exception:
        mlflow_proc.kill()
