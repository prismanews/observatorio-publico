import pandas as pd
import requests, json, os, feedparser
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# --- Configuración y Carpetas ---
os.makedirs("datos", exist_ok=True)
PDF = "datos/informe.pdf"

# 1. PROCESAMIENTO DE SUBVENCIONES (Mejorado)
SUBV_URL = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"
try:
    r = requests.get(SUBV_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    with open("datos/data.csv", "wb") as f: f.write(r.content)
    df = pd.read_csv("datos/data.csv", sep=";", encoding="latin1", on_bad_lines='skip', low_memory=False)
    # Limpieza de importes españoles
    df["Importe"] = df["Importe"].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce").fillna(0)
    total = df["Importe"].sum()
    ranking = df.groupby("Beneficiario")["Importe"].sum().sort_values(ascending=False).head(5)
except:
    df, total, ranking = pd.DataFrame(), 0, pd.Series()

# 2. RESUMEN INTELIGENTE DEL BOE
boe_resumen = []
palabras_clave = {
    "💰 Ayudas": ["subvencion", "ayuda", "concesion", "beca"],
    "🏗️ Contratos": ["licitacion", "adjudicacion", "contrato", "formalizacion"],
    "📋 Normativa": ["ley", "decreto", "orden", "resolucion"]
}

try:
    feed = feedparser.parse("https://www.boe.es/rss/boe.php")
    for entry in feed.entries[:10]: # Analizamos las 10 últimas entradas
        texto = entry.title.lower()
        categoria = "🔍 Otros"
        for cat, keywords in palabras_clave.items():
            if any(k in texto for k in keywords):
                categoria = cat
                break
        boe_resumen.append({"titulo": entry.title, "link": entry.link, "cat": categoria})
except: pass

# 3. HTML DASHBOARD PROFESIONAL
fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
boe_html = "".join([f'<div class="boe-item"><b>{b["cat"]}:</b> <a href="{b["link"]}" target="_blank">{b["titulo"]}</a></div>' for b in boe_resumen])

html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Observatorio Transparencia</title>
    <link rel="stylesheet" href="estilo.css">
    <link rel="manifest" href="manifest.json">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <header>
            <div class="badge-live">DIRECTO</div>
            <h1>Observatorio Público</h1>
            <p>Monitor de Datos del Estado • {fecha}</p>
        </header>

        <section class="main-card">
            <small>DINERO PÚBLICO RASTREADO (HOY)</small>
            <div class="total-amount">{total:,.2f} €</div>
        </section>

        <div class="grid">
            <div class="panel">
                <h3>📰 Resumen Diario del BOE</h3>
                <div class="boe-list">{boe_html}</div>
            </div>
            <div class="panel">
                <h3>🏆 Mayores Adjudicatarios</h3>
                <canvas id="rankingChart"></canvas>
            </div>
        </div>

        <footer class="actions">
            <a href="datos/informe.pdf" class="btn-main">Descargar Informe Oficial PDF</a>
        </footer>
    </div>

    <script>
        const ctx = document.getElementById('rankingChart').getContext('2d');
        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: {list(ranking.index) if not ranking.empty else []},
                datasets: [{{
                    data: {list(ranking.values) if not ranking.empty else []},
                    backgroundColor: ['#4cc9f0', '#4361ee', '#3a0ca3', '#7209b7', '#f72585'],
                    borderWidth: 0
                }}]
            }},
            options: {{ plugins: {{ legend: {{ position: 'bottom', labels: {{ color: '#fff' }} }} }} }}
        }});
    </script>
</body>
</html>
"""
with open("index.html", "w", encoding="utf-8") as f: f.write(html_content)
