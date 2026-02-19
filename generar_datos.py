import os
import json
import requests
import feedparser
from datetime import datetime

os.makedirs("datos", exist_ok=True)

print("Generando Observatorio...")

# =========================================================
# 1️⃣ SUBVENCIONES AUTOMÁTICAS (datos abiertos)
# =========================================================

subvenciones = []
alertas = []

try:
    url = "https://datos.gob.es/apidata/catalog/dataset?q=subvenciones"
    r = requests.get(url, timeout=30)

    if r.status_code == 200:
        datasets = r.json().get("result", {}).get("items", [])

        for d in datasets[:15]:
            registro = {
                "organismo": d.get("publisher", {}).get("label", "Organismo público"),
                "objeto": d.get("title", ""),
                "importe": 0
            }

            subvenciones.append(registro)

            if "millones" in registro["objeto"].lower():
                alertas.append(registro)

except Exception as e:
    print("Error subvenciones:", e)


# =========================================================
# 2️⃣ BOE SIMPLIFICADO
# =========================================================

boe_docs = []

try:
    feed = feedparser.parse("https://www.boe.es/rss/boe.php")

    for entry in feed.entries[:20]:

        titulo_lower = entry.title.lower()

        categoria = "General"

        if "subvencion" in titulo_lower:
            categoria = "Subvenciones"
        elif "ley" in titulo_lower:
            categoria = "Legislación"
        elif "presupuesto" in titulo_lower:
            categoria = "Economía"
        elif "real decreto" in titulo_lower:
            categoria = "Normativa"

        resumen = entry.title.split(":")[0]

        boe_docs.append({
            "titulo": entry.title,
            "link": entry.link,
            "categoria": categoria,
            "resumen": resumen
        })

except Exception as e:
    print("Error BOE:", e)


# =========================================================
# 3️⃣ GUARDAR JSON
# =========================================================

json.dump(subvenciones, open("datos/subvenciones.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

json.dump(alertas, open("datos/alertas.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

json.dump(boe_docs, open("datos/boe.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)


# =========================================================
# 4️⃣ HTML + SEO COMPLETO
# =========================================================

timestamp = datetime.utcnow().strftime("%d %B %Y · %H:%M UTC")

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>

<meta charset="UTF-8">
<title>Observatorio de Transparencia Pública</title>

<link rel="canonical" href="https://prismanews.github.io/observatorio-publico/">

<meta name="description" content="Observatorio independiente de transparencia pública: subvenciones, BOE simplificado y análisis institucional en España.">
<meta name="keywords" content="subvenciones públicas España, BOE explicado, transparencia pública, datos abiertos España">
<meta name="robots" content="index, follow">

<meta property="og:title" content="Observatorio de Transparencia Pública">
<meta property="og:description" content="Datos públicos explicados: subvenciones, normativa BOE y transparencia institucional.">
<meta property="og:url" content="https://prismanews.github.io/observatorio-publico/">
<meta property="og:type" content="website">

<meta name="viewport" content="width=device-width, initial-scale=1">

<link rel="stylesheet" href="estilo.css">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

</head>

<body>
<div class="container">

<header class="obs-header">
<h1>Observatorio de Transparencia Pública</h1>
<span>Última actualización: {timestamp}</span>
</header>

<section class="obs-card">

<h2>📊 Dashboard</h2>
<canvas id="graficoSubvenciones"></canvas>

<h2>🚨 Alertas subvenciones</h2>
<ul id="alertas"></ul>

<h2>📜 BOE simplificado</h2>
<ul>
"""

for b in boe_docs[:10]:
    html += f"<li><b>[{b['categoria']}]</b> {b['resumen']}</li>"

html += """

</ul>

<script src="dashboard.js"></script>

</section>
</div>
</body>
</html>
"""

open("index.html", "w", encoding="utf-8").write(html)

print("Observatorio actualizado")
