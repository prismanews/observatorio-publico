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

            # ALERTA AUTOMÁTICA (ejemplo base)
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

        titulo = entry.title.lower()

        categoria = "General"

        if "subvencion" in titulo:
            categoria = "Subvenciones"
        elif "ley" in titulo:
            categoria = "Legislación"
        elif "presupuesto" in titulo:
            categoria = "Economía"
        elif "real decreto" in titulo:
            categoria = "Normativa"

        resumen_simple = entry.title.split(":")[0]

        boe_docs.append({
            "titulo": entry.title,
            "link": entry.link,
            "categoria": categoria,
            "resumen": resumen_simple
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
# 4️⃣ HTML + SEO + DASHBOARD
# =========================================================

timestamp = datetime.utcnow().strftime("%d %B %Y · %H:%M UTC")

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>

<meta charset="UTF-8">
<title>Observatorio de Transparencia Pública</title>

<meta name="description" content="Observatorio independiente de subvenciones públicas, BOE simplificado y transparencia institucional.">
<meta name="keywords" content="subvenciones públicas, BOE explicado, transparencia pública, gasto público España">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="canonical" href="https://prismanews.github.io/observatorio-publico/">
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
