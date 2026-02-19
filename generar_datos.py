import os, json, requests, feedparser
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

os.makedirs("datos", exist_ok=True)

# 1. SCRAPING BOE Y ANÁLISIS POLÍTICO/ECONÓMICO
boe_docs = []
alertas = []
feed = feedparser.parse("https://www.boe.es/rss/boe.php")

for entry in feed.entries[:30]:
    texto = entry.title.lower()
    
    # Análisis heurístico ideológico/económico
    if any(w in texto for w in ["ayuda", "subvención", "concesión", "millones"]):
        cat, color = "ECONOMÍA/SUBVENCIONES", "#16a34a"
        # Detección de alertas anticorrupción básicas (Outliers por palabras clave)
        if any(w in texto for w in ["directa", "excepcional", "millones"]):
            alertas.append({"tipo": "CRÍTICA", "msg": f"Posible adjudicación directa o cuantía elevada: {entry.title[:80]}..."})
    elif any(w in texto for w in ["ley", "reforma", "decreto"]):
        cat, color = "LEGISLATIVO", "#3b82f6"
    else:
        cat, color = "ADMINISTRATIVO", "#64748b"
    
    boe_docs.append({
        "titulo": entry.title,
        "link": entry.link,
        "categoria": cat,
        "color": color,
        "fecha": datetime.now().strftime("%d/%m/%Y")
    })

# 2. GENERACIÓN DE PDF AUTOMÁTICO (Informe Mensual/Diario)
def generar_pdf():
    pdf_path = "datos/informe_transparencia.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "Informe del Observatorio de Transparencia")
    c.setFont("Helvetica", 10)
    c.drawString(50, 735, f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    y = 700
    c.drawString(50, y, "ALERTAS DETECTADAS:")
    y -= 20
    for a in alertas[:5]:
        c.drawString(60, y, f"- {a['msg']}")
        y -= 15
    c.save()

generar_pdf()

# 3. MANIFEST PARA APP MÓVIL (PWA)
manifest = {
    "name": "Observatorio Público",
    "short_name": "Observatorio",
    "start_url": "index.html",
    "display": "standalone",
    "background_color": "#0f172a",
    "theme_color": "#3b82f6",
    "icons": [{"src": "https://cdn-icons-png.flaticon.com/512/1212/1212161.png", "sizes": "512x512", "type": "image/png"}]
}
with open("manifest.json", "w") as f: json.dump(manifest, f)

# 4. GUARDAR DATOS JSON
with open("datos/boe.json", "w", encoding="utf-8") as f: json.dump(boe_docs, f, ensure_ascii=False)
with open("datos/alertas.json", "w", encoding="utf-8") as f: json.dump(alertas, f, ensure_ascii=False)

# 5. GENERAR INDEX.HTML (Estructura para PWA y Mapa)
html = f"""
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
            <h1>Observatorio Público</h1>
            <p>Monitoreo en tiempo real de la administración</p>
            <a href="datos/informe_transparencia.pdf" class="btn-pdf" download>📥 Descargar Informe PDF</a>
        </header>
        
        <div class="main-grid">
            <div class="obs-card">
                <h2>🚨 Alertas de Riesgo</h2>
                <div id="alertas-box"></div>
            </div>
            <div class="obs-card">
                <h2>📍 Mapa Municipal de Actividad</h2>
                <div id="map" style="height: 300px;"></div>
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
with open("index.html", "w", encoding="utf-8") as f: f.write(html)
