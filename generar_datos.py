import pandas as pd
import requests, json, os, feedparser
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# --- Rutas y Directorios ---
os.makedirs("datos", exist_ok=True)
HIST = "datos/historico.csv"
PDF = "datos/informe.pdf"
API = "datos/api.json"

# 1. DESCARGA REALISTA (Evitamos el error 0)
SUBV_URL = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"
headers = {"User-Agent": "Mozilla/5.0"}

try:
    # Descargamos el CSV oficial
    r = requests.get(SUBV_URL, headers=headers, timeout=30)
    with open("datos/data.csv", "wb") as f:
        f.write(r.content)
    
    # Lectura cuidadosa: el CSV español usa encoding latin1 y separador ;
    df = pd.read_csv("datos/data.csv", sep=";", encoding="latin1", on_bad_lines='skip', low_memory=False)
    
    # Limpieza de importes: Quitar puntos de miles y cambiar coma por punto decimal
    if "Importe" in df.columns:
        df["Importe"] = df["Importe"].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce").fillna(0)
except Exception as e:
    print(f"Error: {e}")
    df = pd.DataFrame()

# 2. CÁLCULOS Y ALERTAS ANTICORRUPCIÓN
total = df["Importe"].sum() if not df.empty else 0
ranking = df.groupby("Beneficiario")["Importe"].sum().sort_values(ascending=False).head(5) if not df.empty else pd.Series()

alertas = []
if not df.empty:
    umbral = df["Importe"].mean() + (df["Importe"].std() * 3)
    if df["Importe"].max() > umbral:
        alertas.append("Detección de adjudicación individual fuera de rango estadístico.")
    if len(df[df["Importe"] == 0]) / len(df) > 0.5:
        alertas.append("Alta opacidad: gran cantidad de registros sin importe declarado.")

# 3. MAPA POR PROVINCIAS (Simulado con datos de departamentos/provincias del CSV)
mapa_data = {}
if "Provincia" in df.columns:
    mapa_data = df.groupby("Provincia")["Importe"].sum().to_dict()

# 4. GENERAR PDF PROFESIONAL
def generar_pdf():
    doc = SimpleDocTemplate(PDF, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Informe de Control de Transparencia", styles['Title']),
        Spacer(1, 12),
        Paragraph(f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']),
        Paragraph(f"Total Auditado: {total:,.2f} €", styles['Heading2']),
        Spacer(1, 10),
        Paragraph("Alertas detectadas:", styles['Heading3'])
    ]
    for al in alertas:
        story.append(Paragraph(f"• {al}", styles['Normal']))
    doc.build(story)

generar_pdf()

# 5. HTML CON DASHBOARD + MAPA + PWA
fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
labels_graf = list(ranking.index)
datos_graf = list(ranking.values)

html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Observatorio Público</title>
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#0b132b">
    <link rel="stylesheet" href="estilo.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 Observatorio Pro</h1>
            <p>Sincronización: {fecha}</p>
        </header>

        <div class="main-card">
            <small>FONDO TOTAL DETECTADO</small>
            <div class="total-big">{total:,.2f} €</div>
        </div>

        <div class="grid">
            <div class="card">
                <h3>📊 Top 5 Beneficiarios</h3>
                <canvas id="chartRanking"></canvas>
            </div>
            <div class="card">
                <h3>🔎 Alertas Anticorrupción</h3>
                {"".join([f'<div class="alert">⚠️ {a}</div>' for a in alertas]) if alertas else "No hay alertas activas."}
            </div>
        </div>

        <div class="card">
            <h3>🗺️ Distribución Geográfica</h3>
            <p>Sección en desarrollo: Datos vinculados a {len(mapa_data)} provincias.</p>
        </div>

        <div class="actions">
            <a href="datos/informe.pdf" class="btn">📄 Descargar PDF</a>
            <a href="https://github.com/prismanews/observatorio-publico" class="btn secondary">🛠️ Ver Dataset</a>
        </div>
    </div>

    <script>
        new Chart(document.getElementById('chartRanking'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(labels_graf)},
                datasets: [{{
                    label: 'Euros',
                    data: {json.dumps(datos_graf)},
                    backgroundColor: '#5bc0be'
                }}]
            }},
            options: {{ indexAxis: 'y', plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ ticks: {{ color: '#fff' }} }}, y: {{ ticks: {{ color: '#fff' }} }} }} }}
        }});
    </script>
</body>
</html>
"""
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_template)
