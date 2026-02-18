import pandas as pd
import requests, json, os, feedparser
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


# =========================
# CONFIG
# =========================

SUBV_URL = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"

# GeoJSON provincias España (ligero y público)
GEOJSON_URL = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/spain-provinces.geojson"

CONTRATOS_RSS = "https://contrataciondelestado.es/rss/licitacionesPerfilesContratante.xml"

HIST = "datos/historico.csv"
API = "datos/api.json"
PDF = "datos/informe.pdf"
GEOJSON_LOCAL = "datos/spain.geojson"

os.makedirs("datos", exist_ok=True)


# =========================
# DESCARGAR GEOJSON ESPAÑA
# =========================

try:
    geo = requests.get(GEOJSON_URL, timeout=20).json()
    with open(GEOJSON_LOCAL, "w", encoding="utf-8") as f:
        json.dump(geo, f)
except:
    print("GeoJSON no descargado")


# =========================
# SUBVENCIONES OFICIALES
# =========================

try:
    df = pd.read_csv(SUBV_URL, sep=";", encoding="latin1", low_memory=False)
except:
    df = pd.DataFrame()

if not df.empty and "Importe" in df.columns:

    df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce")
    df = df.dropna(subset=["Importe"])

    total = df["Importe"].sum()
    media = df["Importe"].mean()
    maximo = df["Importe"].max()

    ranking = (
        df.groupby("Beneficiario")["Importe"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

else:
    total = media = maximo = 0
    ranking = pd.Series()


# =========================
# HEATMAP PROVINCIAS REAL
# =========================

heatmap = {}

if "Provincia" in df.columns:
    prov = df.groupby("Provincia")["Importe"].sum()

    max_val = prov.max()

    heatmap = {
        k: float(v/max_val) for k, v in prov.items()
    }


# =========================
# SCRAPING CONTRATOS RSS
# =========================

contratos_estimados = 0

try:
    feed = feedparser.parse(CONTRATOS_RSS)
    contratos_estimados = len(feed.entries) * 50000
except:
    pass


# =========================
# ALERTAS POSIBLE IRREGULARIDAD
# =========================

alertas = []

if not df.empty:

    std = df["Importe"].std()
    limite = media + 3 * std

    if maximo > limite:
        alertas.append("Subvención muy superior a la media.")

    if not ranking.empty:
        if ranking.iloc[0] / total > 0.25:
            alertas.append("Alta concentración en un beneficiario.")


# =========================
# HISTÓRICO
# =========================

fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

nuevo = pd.DataFrame([{
    "fecha": fecha,
    "total": total
}])

if os.path.exists(HIST):
    hist = pd.read_csv(HIST)
    hist = pd.concat([hist, nuevo])
else:
    hist = nuevo

hist.to_csv(HIST, index=False)


# =========================
# API JSON OBSERVATORIO
# =========================

api = {
    "fecha": fecha,
    "subvenciones_total": float(total),
    "media": float(media),
    "contratos_estimados": float(contratos_estimados),
    "ranking": ranking.to_dict(),
    "heatmap": heatmap,
    "alertas": alertas
}

with open(API, "w", encoding="utf-8") as f:
    json.dump(api, f, indent=2, ensure_ascii=False)


# =========================
# INFORME PDF AUTOMÁTICO
# =========================

styles = getSampleStyleSheet()

doc = SimpleDocTemplate(PDF)

contenido = [
    Paragraph("Informe Observatorio Público", styles["Title"]),
    Spacer(1, 12),
    Paragraph(f"Fecha: {fecha}", styles["Normal"]),
    Paragraph(f"Subvenciones totales: {total:,.0f} €", styles["Normal"]),
    Paragraph(f"Contratos estimados: {contratos_estimados:,.0f} €", styles["Normal"]),
]

for a in alertas:
    contenido.append(Paragraph(a, styles["Normal"]))

doc.build(contenido)


# =========================
# DASHBOARD HTML FINAL
# =========================

labels = hist["fecha"].astype(str).tolist()
datos = hist["total"].tolist()

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Observatorio Público</title>

<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Cache-Control" content="no-cache">

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<link rel="stylesheet"
 href="https://unpkg.com/leaflet/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

<style>
body {{
font-family:system-ui;
background:#0b132b;
color:white;
margin:0;
padding:10px;
}}

.card {{
background:#1c2541;
padding:15px;
border-radius:12px;
margin:10px 0;
}}
</style>
</head>

<body>

<h1>📊 Observatorio Público</h1>
<p>Actualizado: {fecha}</p>

<div class="card">
Subvenciones totales: {total:,.0f} €<br>
Media: {media:,.0f} €<br>
Contratos estimados: {contratos_estimados:,.0f} €
</div>

<div class="card">
<b>Alertas:</b><br>
{"<br>".join(alertas) if alertas else "Sin alertas relevantes"}
</div>

<h2>Evolución histórica</h2>
<canvas id="graf"></canvas>

<script>
new Chart(document.getElementById('graf'), {{
type:'line',
data:{{
labels:{labels},
datasets:[{{label:'Subvenciones',data:{datos}}}]
}}
}});
</script>

<h2>Mapa subvenciones España</h2>
<div id="map" style="height:450px"></div>

<script>
var map=L.map('map').setView([40.3,-3.7],6);

L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);

fetch('datos/spain.geojson')
.then(r=>r.json())
.then(geo=>{{
fetch('datos/api.json')
.then(r=>r.json())
.then(data=>{{
L.geoJSON(geo,{{
style:function(f){{
var p=f.properties.name;
var v=data.heatmap[p]||0;
return {{
fillColor:`rgba(255,0,0,${{v}})`,
weight:1,color:"#fff",
fillOpacity:0.6
}};
}}
}}).addTo(map);
}});
}});
</script>

<div class="card">
<a href="datos/informe.pdf">📄 Descargar informe PDF</a>
</div>

</body>
</html>
"""

open("index.html", "w", encoding="utf-8").write(html)

print("OBSERVATORIO COMPLETO CON MAPA REAL GENERADO")
