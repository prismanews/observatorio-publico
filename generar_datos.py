import os
import json
import requests
import feedparser
from datetime import datetime

os.makedirs("datos", exist_ok=True)

print("Generando Observatorio...")

# =========================================================
# 1️⃣ SUBVENCIONES AUTOMÁTICAS DESDE DATOS ABIERTOS
# =========================================================

subvenciones = []

try:
    url = "https://datos.gob.es/apidata/catalog/dataset?q=subvenciones"

    r = requests.get(url, timeout=30)

    if r.status_code == 200:
        data = r.json()

        datasets = data.get("result", {}).get("items", [])

        for d in datasets[:10]:
            subvenciones.append({
                "organismo": d.get("publisher", {}).get("label", "Organismo público"),
                "objeto": d.get("title", ""),
                "importe": 0
            })

        print(f"Datasets subvenciones detectados: {len(subvenciones)}")

    else:
        print("Error API datos abiertos:", r.status_code)

except Exception as e:
    print("Error subvenciones:", e)


# =========================================================
# 2️⃣ BOE RSS
# =========================================================

boe_docs = []

try:
    feed = feedparser.parse("https://www.boe.es/rss/boe.php")

    for entry in feed.entries[:15]:
        boe_docs.append({
            "titulo": entry.title,
            "link": entry.link,
            "fecha": entry.published
        })

    print("BOE OK")

except Exception as e:
    print("Error BOE:", e)


# =========================================================
# 3️⃣ GUARDAR JSON
# =========================================================

with open("datos/subvenciones.json", "w", encoding="utf-8") as f:
    json.dump(subvenciones, f, ensure_ascii=False, indent=2)

with open("datos/boe.json", "w", encoding="utf-8") as f:
    json.dump(boe_docs, f, ensure_ascii=False, indent=2)


# =========================================================
# 4️⃣ HTML
# =========================================================

timestamp = datetime.utcnow().strftime("%d %B %Y · %H:%M UTC")

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Observatorio Público</title>
<link rel="stylesheet" href="estilo.css">
</head>

<body>
<div class="container">

<header class="obs-header">
<h1>Observatorio de Transparencia Pública</h1>
<span>Última actualización: {timestamp}</span>
</header>

<section class="obs-card">

<h2>Subvenciones detectadas</h2>
<ul>
"""

for s in subvenciones:
    html += f"<li>{s['organismo']} — {s['objeto']}</li>"

html += "</ul><h2>BOE reciente</h2><ul>"

for b in boe_docs:
    html += f"<li><a href='{b['link']}'>{b['titulo']}</a></li>"

html += "</ul></section></div></body></html>"

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Observatorio actualizado")
