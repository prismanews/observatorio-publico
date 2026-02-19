import os
import json
import requests
import pandas as pd
import feedparser
from io import StringIO
from datetime import datetime

os.makedirs("datos", exist_ok=True)

print("Iniciando generación del Observatorio...")

# =========================================================
# 1️⃣ SUBVENCIONES BDNS (ROBUSTO)
# =========================================================

subvenciones = []

try:
    url = "https://www.infosubvenciones.es/bdnstrans/GE/es/convocatorias.csv"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers, timeout=30)

    if r.status_code == 200:

        df = pd.read_csv(
            StringIO(r.text),
            sep=";",
            encoding="latin1",
            on_bad_lines="skip"
        )

        df.columns = [c.strip() for c in df.columns]

        columnas_necesarias = {"Organo", "Descripcion", "Importe"}

        if columnas_necesarias.issubset(set(df.columns)):

            df = df.rename(columns={
                "Organo": "organismo",
                "Descripcion": "objeto",
                "Importe": "importe"
            })

            df["importe"] = pd.to_numeric(df["importe"], errors="coerce")

            df = df[["organismo", "objeto", "importe"]].dropna()

            df = df.sort_values("importe", ascending=False).head(20)

            subvenciones = df.to_dict(orient="records")

            print(f"BDNS integrada: {len(subvenciones)} registros")

        else:
            print("BDNS: columnas no coinciden")

    else:
        print("BDNS error HTTP:", r.status_code)

except Exception as e:
    print("Error BDNS:", e)


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

    print(f"BOE integrado: {len(boe_docs)} registros")

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
# 4️⃣ ESTADÍSTICAS
# =========================================================

total_subv = len(subvenciones)
importe_total = sum(
    s.get("importe", 0)
    for s in subvenciones
    if isinstance(s.get("importe"), (int, float))
)

timestamp = datetime.utcnow()
timestamp_str = timestamp.strftime("%d %B %Y · %H:%M UTC")


# =========================================================
# 5️⃣ GENERAR HTML
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

if subvenciones:
    for s in subvenciones[:10]:
        html += f"<li><b>{s['organismo']}</b>: {s['importe']:,.0f} € — {s['objeto']}</li>"
else:
    html += "<li>No se pudieron cargar subvenciones en esta actualización.</li>"

html += "</ul>"

html += "<h2>BOE reciente</h2><ul>"

for b in boe_docs[:10]:
    html += f"<li><a href='{b['link']}' target='_blank'>{b['titulo']}</a></li>"

html += """

</ul>

<p style="margin-top:40px;font-size:0.85rem;color:#666;">
Fuentes oficiales: BDNS · BOE · Procesado automáticamente
</p>

</section>
</div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Observatorio generado correctamente")
