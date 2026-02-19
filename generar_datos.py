import os, json, requests, feedparser
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

os.makedirs("datos", exist_ok=True)

# CONFIGURACIÓN DE VIGILANCIA
SECTORES_CRITICOS = ["defensa", "armamento", "consultoría", "obras", "infraestructura", "sanidad", "digitalización"]
ALERTAS_PATRON = ["directa", "excepcional", "urgencia", "millones", "emergencia"]

boe_docs = []
alertas = []
feed = feedparser.parse("https://www.boe.es/rss/boe.php")

for entry in feed.entries[:30]:
    texto = entry.title.lower()
    sector_detectado = next((s for s in SECTORES_CRITICOS if s in texto), "General")
    
    cat, color = ("ADMINISTRATIVO", "#64748b")
    if sector_detectado != "General":
        cat, color = f"SECTOR: {sector_detectado.upper()}", "#3b82f6"
    if any(w in texto for w in ["subvención", "ayuda"]):
        cat, color = "ECONOMÍA/AYUDAS", "#16a34a"

    riesgo = any(p in texto for p in ALERTAS_PATRON)
    # Si detectamos un sector crítico o un patrón de riesgo, lo añadimos a alertas
    if riesgo or sector_detectado != "General":
        alertas.append({
            "tipo": "CRÍTICA" if riesgo else "AVISO",
            "msg": entry.title[:110] + "...",
            "motivo": "Sector estratégico o adjudicación especial",
            "link": entry.link
        })
    
    boe_docs.append({"titulo": entry.title, "link": entry.link, "categoria": cat, "color": color})

# [span_0](start_span)GENERAR PDF (Usando reportlab que ya tienes en el YAML[span_0](end_span))
def generar_pdf():
    c = canvas.Canvas("datos/informe_transparencia.pdf", pagesize=letter)
    c.setFont("Helvetica-Bold", 16); c.drawString(50, 750, "Análisis de Riesgo - Observatorio Público")
    c.setFont("Helvetica", 10); y = 710
    for a in alertas[:15]:
        c.drawString(50, y, f"- [{a['tipo']}] {a['msg']}")
        y -= 20
    c.save()
generar_pdf()

# GUARDAR JSON Y MANIFEST PWA
json.dump(boe_docs, open("datos/boe.json", "w", encoding="utf-8"), ensure_ascii=False)
json.dump(alertas, open("datos/alertas.json", "w", encoding="utf-8"), ensure_ascii=False)
json.dump({"name":"Observatorio Público","short_name":"ObsPub","start_url":"index.html","display":"standalone","icons":[{"src":"https://cdn-icons-png.flaticon.com/512/1212/1212161.png","sizes":"512x512"}]}, open("manifest.json", "w"))

# GENERAR INDEX.HTML DINÁMICO
timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Observatorio Público</title>
    <link rel="manifest" href="manifest.json">
    <link rel="stylesheet" href="estilo.css">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
</head>
<body>
    <div class="container">
        <header class="obs-header">
            <h1>Observatorio de Transparencia</h1>
            <p>Estado de la Administración: {timestamp}</p>
            <a href="datos/informe_transparencia.pdf" class="btn-pdf" download>📥 Descargar Informe PDF</a>
        </header>
        <div class="main-grid">
            <div class="obs-card">
                <h2>🚨 Alertas de Riesgo</h2>
                <div id="alertas-box">Buscando anomalías...</div>
            </div>
            <div class="obs-card">
                <h2>📍 Mapa Municipal (Actividad)</h2>
                <div id="map" style="height: 350px; border-radius: 8px;"></div>
            </div>
            <div class="obs-card" style="grid-column: span 2;">
                <h2>📜 BOE Analizado Automáticamente</h2>
                <div id="boe-lista"></div>
            </div>
        </div>
    </div>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="dashboard.js"></script>
</body>
</html>
"""
open("index.html", "w", encoding="utf-8").write(html_content)
