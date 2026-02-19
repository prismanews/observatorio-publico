import os
import json
import pandas as pd
import feedparser
from datetime import datetime

os.makedirs("datos", exist_ok=True)

print("Iniciando generación del Observatorio...")

# =========================================================
# 1️⃣ SUBVENCIONES BDNS
# =========================================================

subvenciones = []

try:
    url = "https://www.infosubvenciones.es/bdnstrans/GE/es/convocatorias.csv"
    df = pd.read_csv(url, sep=";", encoding="latin1")

    df = df.rename(columns={
        "Descripcion": "objeto",
        "Importe": "importe",
        "Organo": "organismo"
    })

    df = df[["organismo", "objeto", "importe"]].dropna()
    df["importe"] = pd.to_numeric(df["importe"], errors="coerce")

    df = df.sort_values("importe", ascending=False).head(20)

    subvenciones = df.to_dict(orient="records")

    print("Subvenciones BDNS integradas")

except Exception as e:
    print("Error BDNS (continúa ejecución):", e)


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
            "fecha": entry.published,
            "resumen": entry.title[:160] + "..."
        })

    print("BOE RSS integrado")

except Exception as e:
    print("Error BOE (continúa ejecución):", e)


# =========================================================
# 3️⃣ GUARDAR JSON
# =========================================================

with open("datos/subvenciones.json", "w", encoding="utf-8") as f:
    json.dump(subvenciones, f, ensure_ascii=False, indent=2)

with open("datos/boe.json", "w", encoding="utf-8") as f:
    json.dump(boe_docs, f, ensure_ascii=False, indent=2)


# =========================================================
# 4️⃣ ESTADÍSTICAS
# =========================================================

total_subv = len(subvenciones)
importe_total = sum(
    s.get("importe", 0) for s in subvenciones if isinstance(s.get("importe"), (int, float))
)

timestamp = datetime.utcnow()
timestamp_str = timestamp.strftime("%d %B %Y · %H:%M UTC")

# =========================================================
# 5️⃣ GENERAR HTML PROFESIONAL
# =========================================================

html = f"""
<!-- build: {timestamp.isoformat()} -->
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Observatorio de Transparencia Pública</title>
<link rel="stylesheet" href="estilo.css">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
</head>

<body>
<div class="container">

<header class="obs-header">
<h1 class="obs-header__title">Observatorio de Transparencia Pública</h1>
<span class="obs-header__sync">
Última actualización: {timestamp_str}
</span>
</header>

<section class="obs-card">

<div class="obs-stats">
<div class="obs-stats__item">
<span class="obs-stats__label">Subvenciones analizadas</span>
<span class="obs-stats__value">{total_subv}</span>
</div>

<div class="obs-stats__item">
<span class="obs-stats__label">Importe total</span>
<span class="obs-stats__value">{importe_total:,.0f} €</span>
</div>

<div class="obs-stats__item">
<span class="obs-stats__label">Normas BOE recientes</span>
<span class="obs-stats__value">{len(boe_docs)}</span>
</div>
</div>

<h2>Top Subvenciones</h2>
<ul>
"""

for s in subvenciones[:10]:
    html += f"<li><b>{s.get('organismo','')}</b>: {s.get('importe',0):,.0f} € — {s.get('objeto','')}</li>"

html += "</ul>"

html += """
<h2>BOE reciente</h2>
<ul>
"""

for b in boe_docs[:10]:
    html += f"<li><a href='{b['link']}' target='_blank'>{b['titulo']}</a></li>"

html += """

</ul>

<p style="margin-top:40px;font-size:0.85rem;color:#666;">
Datos oficiales: BDNS · BOE · Procesado automáticamente
</p>

</section>
</div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Observatorio generado correctamente")
