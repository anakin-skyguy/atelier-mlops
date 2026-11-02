"""
Capture automatisée haute résolution de l'interface MLflow UI via Chrome DevTools Protocol.
Démarre MLflow UI (--workers 1), capture 6 vues complètes et arrête proprement le serveur.
"""

import base64
import json
import os
import subprocess
import tempfile
import time
import urllib.request

import mlflow
import websocket

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_PORT = 9340
MLFLOW_PORT = 5005
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "screenshots")
os.makedirs(OUT, exist_ok=True)

os.chdir(ROOT)
mlflow.set_tracking_uri("sqlite:///mlflow.db")
exp = mlflow.get_experiment_by_name("TP_Iris_Classification")
exp_id = exp.experiment_id
df = mlflow.search_runs(experiment_ids=[exp_id], order_by=["start_time ASC"])

rf100 = df[df["tags.mlflow.runName"] == "RandomForest_n100_d5"].iloc[-1]["run_id"]
rf200 = df[df["tags.mlflow.runName"] == "RandomForest_n200_d8"].iloc[-1]["run_id"]
knn = df[df["tags.mlflow.runName"] == "KNN_k5"].iloc[-1]["run_id"]
print(f"Runs: rf100={rf100}, rf200={rf200}, knn={knn}")

env = os.environ.copy()
env["MLFLOW_DISABLE_AGENT_HINT"] = "1"
mlflow_proc = subprocess.Popen(
    ["mlflow", "ui", "--backend-store-uri", "sqlite:///mlflow.db", "--port", str(MLFLOW_PORT), "--workers", "1"],
    cwd=ROOT,
    env=env,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

chrome_proc = None
try:
    # Attendre le démarrage de MLflow UI
    for _ in range(40):
        try:
            if urllib.request.urlopen(f"http://127.0.0.1:{MLFLOW_PORT}/", timeout=2).status == 200:
                break
        except Exception:
            time.sleep(0.5)

    user_dir = os.path.join(tempfile.gettempdir(), "chrome-mlflow-clean")
    chrome_proc = subprocess.Popen(
        [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            f"--remote-debugging-port={CDP_PORT}",
            "--remote-allow-origins=*",
            f"--user-data-dir={user_dir}",
            "--window-size=1680,1050",
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
        localStorage.setItem('mlflow.assistant.panelOpen_v1', 'false');
        localStorage.setItem('mlflow.assistant.fab.autoOpenedOnFirstLoad_v1', 'true');
        localStorage.setItem({json.dumps(state_key)}, {json.dumps(json.dumps(exp_state))});
    }} catch (e) {{}}
    """

    call("Page.enable")
    call("Page.addScriptToEvaluateOnNewDocument", source=init_js)
    call("Emulation.setDeviceMetricsOverride", width=1680, height=1000, deviceScaleFactor=1, mobile=False)

    base = f"http://127.0.0.1:{MLFLOW_PORT}/#"

    def wait_text(marker, timeout_s=30):
        for _ in range(timeout_s * 2):
            txt = js("document.body ? document.body.innerText : ''") or ""
            if marker in txt:
                return True
            time.sleep(0.5)
        return False

    def switch_model_training_if_present():
        js("""
        (() => {
            const els = Array.from(document.querySelectorAll('button, [role="tab"], [role="radio"], a, span'));
            const mt = els.find(e => (e.innerText || '').trim() === 'Model training');
            if (mt) mt.click();
        })()
        """)

    def snap(filename, width=1680, height=1000):
        call("Emulation.setDeviceMetricsOverride", width=width, height=height, deviceScaleFactor=1, mobile=False)
        time.sleep(1.0)
        data = call("Page.captureScreenshot", format="png")["data"]
        path = os.path.join(OUT, filename)
        with open(path, "wb") as f:
            f.write(base64.b64decode(data))
        print(f"Saved {filename} ({os.path.getsize(path)} bytes)")

    # 1. Runs table with metrics & params columns
    call("Page.navigate", url=f"{base}/experiments/{exp_id}/runs")
    wait_text("KNN_k5")
    switch_model_training_if_present()
    time.sleep(2.5)
    wait_text("KNN_k5")
    snap("01_experiment_runs_list.png", 1680, 920)

    # 2. Compare runs (Parallel Coordinates + Run details) & 3. Full compare table
    cmp_url = f"{base}/compare-runs?runs=%5B%22{rf100}%22,%22{rf200}%22,%22{knn}%22%5D&experiments=%5B%22{exp_id}%22%5D"
    call("Page.navigate", url="about:blank")
    time.sleep(0.3)
    call("Page.navigate", url=cmp_url)
    wait_text("KNN_k5")
    time.sleep(2.5)
    snap("02_compare_runs.png", 1680, 1050)

    # Expand tall viewport to capture full Parameters + Metrics comparison tables below chart
    snap("03_compare_runs_metrics_table.png", 1680, 1750)

    # 4. Run detail RF 100
    call("Page.navigate", url="about:blank")
    time.sleep(0.3)
    call("Page.navigate", url=f"{base}/experiments/{exp_id}/runs/{rf100}")
    wait_text("f1_score")
    time.sleep(2.0)
    snap("04_run_rf100_detail.png", 1680, 1000)

    # 5. Run detail KNN
    call("Page.navigate", url="about:blank")
    time.sleep(0.3)
    call("Page.navigate", url=f"{base}/experiments/{exp_id}/runs/{knn}")
    wait_text("n_neighbors")
    time.sleep(2.0)
    snap("05_run_knn_detail.png", 1680, 1000)

    # 6. Artifacts tab of RF 100 showing model/model.pkl
    js("""
    (() => {
        const tabs = Array.from(document.querySelectorAll('[role="tab"], a, button'));
        const art = tabs.find(e => (e.innerText || '').trim().startsWith('Artifacts'));
        if (art) art.click();
    })()
    """)
    call("Page.navigate", url=f"{base}/experiments/{exp_id}/runs/{rf100}/artifacts")
    wait_text("model")
    time.sleep(2.0)
    js("""
    (() => {
        const items = Array.from(document.querySelectorAll('span, div, button'));
        const folder = items.find(e => (e.innerText || '').trim() === 'model');
        if (folder) folder.click();
    })()
    """)
    time.sleep(1.5)
    snap("06_run_artifacts_model.png", 1680, 920)

    ws.close()
finally:
    if chrome_proc:
        chrome_proc.terminate()
    mlflow_proc.terminate()
    try:
        mlflow_proc.wait(timeout=5)
    except Exception:
        mlflow_proc.kill()
