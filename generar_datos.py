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

# 1. ANÁLISIS DE DATOS
for entry in feed.entries[:30]:
    texto = entry.title.lower()
    sector_detectado = next((s for s in SECTORES_CRITICOS if s in texto), "General")
    
    cat, color = ("ADMINISTRATIVO", "#64748b")
    if sector_detectado != "General":
        cat, color = f"SECTOR: {sector_detectado.upper()}", "#3b82f6"
    if any(w in texto for w in ["subvención", "ayuda"]):
        cat, color = "ECONOMÍA/AYUDAS", "#16a34a"

    riesgo = any(p in texto for p in ALERTAS_PATRON)
    if riesgo or sector_detectado != "General":
        alertas.append({
            "tipo": "CRÍTICA" if riesgo else "AVISO",
            "msg": entry.title[:110] + "...",
            "motivo": "Patrón de riesgo o sector estratégico",
            "link": entry.link
        })
    
    boe_docs.append({"titulo": entry.title, "link": entry.link, "categoria": cat, "color": color})

# 2. GENERAR PDF
c = canvas.Canvas("datos/informe_transparencia.pdf", pagesize=letter)
c.setFont("Helvetica-Bold", 16); c.drawString(50, 750, "Informe de Riesgos - Observatorio Público")
c.setFont("Helvetica", 10); y = 710
for a in alertas[:15]:
    c.drawString(50, y, f"- [{a['tipo']}] {a['msg']}")
    y -= 20
c.save()

# 3. GUARDAR JSON Y MANIFEST PWA
with open("datos/boe.json", "w", encoding="utf-8") as f: json.dump(boe_docs, f, ensure_ascii=False)
with open("datos/alertas.json", "w", encoding="utf-8") as f: json.dump(alertas, f, ensure_ascii=False)
with open("manifest.json", "w") as f:
    json.dump({"name":"Observatorio Público","short_name":"ObsPub","start_url":"index.html","display":"standalone","background_color":"#0f172a","theme_color":"#3b82f6","icons":[{"src":"https://cdn-icons-png.flaticon.com/512/1212/1212161.png","sizes":"512x512","type":"image/png"}]}, f)

# 4. GENERAR EL NUEVO INDEX.HTML
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
            <p>Actualizado: {timestamp}</p>
            <a href="datos/informe_transparencia.pdf" class="btn-pdf" download>📥 Descargar Informe PDF</a>
        </header>
        <div class="main-grid">
            <div class="obs-card">
                <h2>🚨 Alertas de Riesgo</h2>
                <div id="alertas-box">Cargando alertas...</div>
            </div>
            <div class="obs-card">
                <h2>📍 Mapa Municipal (Actividad)</h2>
                <div id="map" style="height: 300px; border-radius: 8px;"></div>
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
with open("index.html", "w", encoding="utf-8") as f: f.write(html_content)
