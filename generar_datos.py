import pandas as pd
import requests
import json
import os
from datetime import datetime

# PDF informe
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ==============================
# CONFIGURACIÓN GENERAL
# ==============================

DATASET_SUBV = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"
CONTRATOS_LOCAL = "datos/contratos.csv"
API_JSON = "datos/api.json"
HISTORICO = "datos/historico.csv"

os.makedirs("datos", exist_ok=True)

print("Descargando subvenciones oficiales...")

# ==============================
# DESCARGA DATASET OFICIAL
# ==============================

try:
    r = requests.get(DATASET_SUBV, timeout=60)
    r.raise_for_status()
    open("datos/subvenciones.csv", "wb").write(r.content)
except Exception as e:
    print("Error descargando dataset:", e)
    exit()

# ==============================
# LIMPIEZA DATOS
# ==============================

df = pd.read_csv("datos/subvenciones.csv", sep=";", encoding="latin1", low_memory=False)

df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce")
df = df.dropna(subset=["Importe"])
df = df[df["Importe"] > 0]

df["Beneficiario"] = df.get("Beneficiario", "No identificado")

# ==============================
# MÉTRICAS PRINCIPALES
# ==============================

total = df["Importe"].sum()
media = df["Importe"].mean()
maximo = df["Importe"].max()

top_benef = (
    df.groupby("Beneficiario")["Importe"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

# ==============================
# MAPA SUBVENCIONES (POR PROVINCIA)
# ==============================

coords = {
    "Madrid": [40.4, -3.7],
    "Barcelona": [41.3, 2.1],
    "Valencia": [39.4, -0.3],
    "Sevilla": [37.3, -5.9],
    "Bilbao": [43.2, -2.9]
}

provincias = {}

if "Provincia" in df.columns:
    prov_sum = df.groupby("Provincia")["Importe"].sum()
    for p, v in prov_sum.items():
        if p in coords:
            provincias[p] = {
                "total": float(v),
                "coords": coords[p]
            }

# ==============================
# CONTRATOS PÚBLICOS (OPCIONAL)
# ==============================

if os.path.exists(CONTRATOS_LOCAL):
    contratos = pd.read_csv(CONTRATOS_LOCAL)
    contratos["Importe"] = pd.to_numeric(
        contratos["Importe"], errors="coerce"
    )
    total_contratos = contratos["Importe"].sum()
else:
    total_contratos = 0

# ==============================
# RANKING TRANSPARENCIA
# ==============================

if "Administracion" in df.columns:
    ranking = (
        df.groupby("Administracion")["Importe"]
        .count()
        .sort_values(ascending=False)
        .head(10)
    )
else:
    ranking = {}

# ==============================
# HISTÓRICO
# ==============================

fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

registro = pd.DataFrame([{
    "fecha": fecha,
    "total": total,
    "media": media
}])

if os.path.exists(HISTORICO):
    hist = pd.read_csv(HISTORICO)
    hist = pd.concat([hist, registro], ignore_index=True)
else:
    hist = registro

hist.to_csv(HISTORICO, index=False)

# ==============================
# INSIGHTS AUTOMÁTICOS
# ==============================

concentracion = top_benef.head(3).sum() / total * 100

insights = [
    f"Total subvenciones: {total:,.0f} €",
    f"Media subvención: {media:,.0f} €",
    f"Concentración top 3 beneficiarios: {concentracion:.1f}%"
]

if total_contratos:
    insights.append(f"Contratos públicos analizados: {total_contratos:,.0f} €")

# ==============================
# API JSON
# ==============================

api = {
    "fecha": fecha,
    "total_subvenciones": float(total),
    "media": float(media),
    "contratos_publicos": float(total_contratos),
    "provincias": provincias,
    "ranking_transparencia": dict(ranking),
    "insights": insights
}

json.dump(api, open(API_JSON, "w", encoding="utf-8"),
          indent=2, ensure_ascii=False)

# ==============================
# INFORME PDF AUTOMÁTICO
# ==============================

pdf = SimpleDocTemplate("datos/informe.pdf")
styles = getSampleStyleSheet()

contenido = [
    Paragraph("Informe Observatorio Público", styles["Title"]),
    Spacer(1, 20)
]

for i in insights:
    contenido.append(Paragraph(i, styles["Normal"]))

pdf.build(contenido)

# ==============================
# HTML FINAL CON MAPA
# ==============================

labels = hist["fecha"].astype(str).tolist()
datos = hist["total"].tolist()

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Observatorio Público</title>

<meta name="viewport" content="width=device-width, initial-scale=1">

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<link rel="stylesheet"
 href="https://unpkg.com/leaflet/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

<style>
body {{
font-family: system-ui;
background:#0b132b;
color:white;
max-width:900px;
margin:auto;
padding:20px;
}}
.card {{
background:#1c2541;
padding:20px;
margin:15px 0;
border-radius:12px;
}}
</style>
</head>

<body>

<h1>📊 Observatorio Público</h1>
<p>Actualizado: {fecha}</p>

<div class="card">
<h2>Total subvenciones</h2>
{total:,.0f} €
</div>

<h2>Evolución gasto público</h2>
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

<h2>Mapa subvenciones</h2>
<div id="map" style="height:400px"></div>

<script>
var map = L.map('map').setView([40.4,-3.7],6);

L.tileLayer(
'https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png'
).addTo(map);

fetch('datos/api.json')
.then(r=>r.json())
.then(data=>{
  for(const p in data.provincias){{
    var info=data.provincias[p];
    L.marker(info.coords)
     .addTo(map)
     .bindPopup(p+": "+info.total+" €");
  }}
});
</script>

</body>
</html>
"""

open("index.html", "w", encoding="utf-8").write(html)

print("OBSERVATORIO TOTAL GENERADO")
