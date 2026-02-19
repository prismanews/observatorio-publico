import os, json, requests, feedparser
from datetime import datetime

os.makedirs("datos", exist_ok=True)

# 1. SCRAPING BOE & ANÁLISIS POLÍTICO SEMÁNTICO
boe_docs = []
feed = feedparser.parse("https://www.boe.es/rss/boe.php")

for entry in feed.entries[:25]:
    texto = entry.title.lower()
    # Análisis heurístico de sesgo/temática
    if any(w in texto for w in ["ayuda", "subvención", "concesión"]): cat, color = "ECONOMÍA", "success"
    elif any(w in texto for w in ["ley", "reforma", "decreto"]): cat, color = "LEGISLATIVO", "accent"
    else: cat, color = "ADMINISTRATIVO", "primary"
    
    boe_docs.append({
        "titulo": entry.title,
        "link": entry.link,
        "categoria": cat,
        "resumen": entry.title.split(":")[0]
    })

# 2. ALERTAS ANTICORRUPCIÓN (Outliers)
alertas = []
# Simulación de detección basada en palabras clave de alto riesgo y volumen
for doc in boe_docs:
    if "directa" in doc['titulo'].lower() or "millones" in doc['titulo'].lower():
        alertas.append({
            "tipo": "RIESGO ALTO",
            "motivo": "Adjudicación o cuantía anómala detectada",
            "doc": doc['resumen']
        })

# 3. GENERAR MANIFEST PARA PWA
manifest = {
    "name": "Observatorio Público",
    "short_name": "Observatorio",
    "start_url": "index.html",
    "display": "standalone",
    "background_color": "#0f172a",
    "theme_color": "#0f172a",
    "icons": [{"src": "https://cdn-icons-png.flaticon.com/512/1055/1055644.png", "sizes": "512x512", "type": "image/png"}]
}
json.dump(manifest, open("manifest.json", "w"), indent=2)

# 4. GUARDAR DATOS
json.dump(boe_docs, open("datos/boe.json", "w"), ensure_ascii=False)
json.dump(alertas, open("datos/alertas.json", "w"), ensure_ascii=False)

# 5. GENERAR INDEX.HTML PROFESIONAL
timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Observatorio Público | Transparencia Real</title>
    <link rel="manifest" href="manifest.json">
    <link rel="stylesheet" href="estilo.css">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <header>
            <h1>Observatorio de Transparencia Pública</h1>
            <p>Datos actualizados: {timestamp}</p>
        </header>

        <div class="grid-layout">
            <section class="obs-card">
                <h2>🚨 Alertas de Riesgo</h2>
                <div id="alertas-container"></div>
            </section>

            <section class="obs-card">
                <h2>📍 Mapa de Actividad Municipal</h2>
                <div id="map"></div>
            </section>

            <section class="obs-card" style="grid-column: span 2;">
                <h2>📜 Últimas Resoluciones BOE (Analizadas)</h2>
                <div id="boe-lista"></div>
            </section>
        </div>
    </div>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="dashboard.js"></script>
</body>
</html>
"""
with open("index.html", "w", encoding="utf-8") as f: f.write(html_template)
