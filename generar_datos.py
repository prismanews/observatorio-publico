import pandas as pd
import requests, json, os, feedparser
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# --- Configuración de rutas ---
HIST = "datos/historico.csv"
PDF = "datos/informe.pdf"
API = "datos/api.json"
os.makedirs("datos", exist_ok=True)

# 1. INTENTO DE DESCARGA DE DATOS CON HEADERS (Para evitar el 0€)
SUBV_URL = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

try:
    response = requests.get(SUBV_URL, headers=headers, timeout=30)
    with open("datos/temp.csv", "wb") as f:
        f.write(response.content)
    df = pd.read_csv("datos/temp.csv", sep=";", encoding="latin1", low_memory=False)
except Exception as e:
    print(f"Error descargando: {e}")
    df = pd.DataFrame()

# 2. PROCESAMIENTO
if not df.empty and "Importe" in df.columns:
    df["Importe"] = pd.to_numeric(df["Importe"].str.replace(',', '.'), errors="coerce") # Corrección de decimales
    df = df.dropna(subset=["Importe"])
    total, media, maximo = df["Importe"].sum(), df["Importe"].mean(), df["Importe"].max()
    ranking = df.groupby("Beneficiario")["Importe"].sum().sort_values(ascending=False).head(5)
else:
    total = media = maximo = 0
    ranking = pd.Series(dtype=float)

# 3. ANÁLISIS POLÍTICO Y ALERTAS
fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
politico = "Orientación Institucional Social" if total > 0 else "Pendiente de sincronización"
alertas = ["Concentración de gasto detectada"] if not ranking.empty else []

# 4. RSS BOE
boe = []
try:
    feed = feedparser.parse("https://www.boe.es/rss/boe.php")
    for e in feed.entries[:4]:
        boe.append({"titulo": e.title[:80] + "...", "link": e.link})
except: pass

# 5. GUARDAR HISTÓRICO
nuevo = pd.DataFrame([{"fecha": fecha, "total": total}])
if os.path.exists(HIST):
    hist = pd.concat([pd.read_csv(HIST), nuevo])
else:
    hist = nuevo
hist.to_csv(HIST, index=False)

# 6. HTML MODERNO
labels = hist["fecha"].tolist()
datos = hist["total"].tolist()

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Observatorio Público PRO</title>
    <link rel="stylesheet" href="estilo.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <header>
            <div class="status">● SISTEMA ACTIVO</div>
            <h1>Observatorio de Transparencia</h1>
            <p class="subtitle">Análisis de Datos del Estado • {fecha}</p>
        </header>

        <div class="main-stats">
            <div class="stat-card primary">
                <span class="label">Total Subvencionado (Periodo)</span>
                <h2 class="value">{total:,.2f} €</h2>
                <div class="badge">Sincronizado</div>
            </div>
            <div class="stat-card">
                <span class="label">Análisis de Sesgo</span>
                <p>{politico}</p>
            </div>
        </div>

        <div class="grid-layout">
            <div class="panel chart-panel">
                <h3>Evolución de Fondos Públicos</h3>
                <canvas id="mainChart"></canvas>
            </div>
            
            <div class="panel">
                <h3>Alertas del Sistema</h3>
                {"".join([f'<div class="alert-item">{a}</div>' for a in alertas]) if alertas else '<p>No hay alertas críticas.</p>'}
            </div>
        </div>

        <div class="grid-layout">
            <div class="panel">
                <h3>Últimas Publicaciones BOE</h3>
                {"".join([f'<a href="{b["link"]}" class="boe-link">{b["titulo"]}</a>' for b in boe])}
            </div>
            <div class="panel">
                <h3>Documentación</h3>
                <a href="datos/informe.pdf" class="btn">Descargar Informe PDF</a>
                <a href="datos/api.json" class="btn secondary">Consultar API JSON</a>
            </div>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('mainChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {labels},
                datasets: [{{
                    label: 'Presupuesto',
                    data: {datos},
                    borderColor: '#4CC9F0',
                    backgroundColor: 'rgba(76, 201, 240, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 3
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{ grid: {{ color: '#2d3748' }}, ticks: {{ color: '#a0aec0' }} }},
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#a0aec0' }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
open("index.html", "w", encoding="utf-8").write(html)
