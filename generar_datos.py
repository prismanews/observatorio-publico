import pandas as pd
import requests, json, os, feedparser
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


# ==================================================
# CONFIG
# ==================================================

SUBV_URL = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"

GEO_PROV = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/spain-provinces.geojson"
GEO_MUN = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/spain-municipalities.geojson"

BOE_RSS = "https://www.boe.es/rss/boe.php"

HIST = "datos/historico.csv"
PDF = "datos/informe.pdf"
API = "datos/api.json"

os.makedirs("datos", exist_ok=True)


# ==================================================
# GEOJSON ESPAÑA (PROV + MUNICIPIOS)
# ==================================================

for url, file in [(GEO_PROV,"datos/provincias.geojson"),
                  (GEO_MUN,"datos/municipios.geojson")]:
    try:
        geo = requests.get(url,timeout=20).json()
        json.dump(geo, open(file,"w",encoding="utf-8"))
    except:
        print("GeoJSON no descargado:", url)


# ==================================================
# SUBVENCIONES OFICIALES
# ==================================================

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
    ranking = pd.Series(dtype=float)


# ==================================================
# HEATMAP MUNICIPAL (si existe campo)
# ==================================================

heatmap = {}

if "Municipio" in df.columns:

    mun = df.groupby("Municipio")["Importe"].sum()
    max_val = mun.max()

    heatmap = {k:float(v/max_val) for k,v in mun.items()}


# ==================================================
# ALERTAS ANTICORRUPCIÓN AVANZADAS
# ==================================================

alertas = []

if not df.empty:

    std = df["Importe"].std()
    limite = media + 3*std

    if maximo > limite:
        alertas.append("Subvención extremadamente alta detectada.")

    if not ranking.empty and ranking.iloc[0]/total > 0.25:
        alertas.append("Concentración anómala en un beneficiario.")

    if os.path.exists(HIST):
        hist = pd.read_csv(HIST)
        if len(hist)>3:
            if total > hist["total"].mean()*1.4:
                alertas.append("Incremento fuerte del gasto público.")


# ==================================================
# HISTÓRICO
# ==================================================

fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

nuevo = pd.DataFrame([{"fecha":fecha,"total":total}])

if os.path.exists(HIST):
    hist = pd.read_csv(HIST)
    hist = pd.concat([hist,nuevo])
else:
    hist = nuevo

hist.to_csv(HIST,index=False)


# ==================================================
# ANÁLISIS POLÍTICO PROFUNDO (GRATIS)
# ==================================================

texto = " ".join(df.columns).lower()

prog = ["igualdad","social","clima","sanidad","educacion"]
cons = ["empresa","mercado","defensa","seguridad","impuestos"]

p = sum(w in texto for w in prog)
c = sum(w in texto for w in cons)

if abs(p-c)<2:
    politico="Cobertura institucional neutra."
elif p>c:
    politico="Orientación institucional más social."
else:
    politico="Orientación institucional económica."


# ==================================================
# SCRAPING BOE AUTOMÁTICO
# ==================================================

boe = []

try:
    feed = feedparser.parse(BOE_RSS)
    for e in feed.entries[:5]:
        boe.append({"titulo":e.title,"link":e.link})
except:
    pass


# ==================================================
# API JSON PÚBLICA
# ==================================================

api = {
    "fecha":fecha,
    "subvenciones_total":float(total),
    "ranking":ranking.to_dict(),
    "alertas":alertas,
    "analisis_politico":politico,
    "boe":boe,
    "heatmap":heatmap
}

json.dump(api,open(API,"w",encoding="utf-8"),
          indent=2,ensure_ascii=False)


# ==================================================
# PDF AUTOMÁTICO
# ==================================================

styles=getSampleStyleSheet()
doc=SimpleDocTemplate(PDF)

contenido=[
    Paragraph("Informe Observatorio Público",styles["Title"]),
    Spacer(1,12),
    Paragraph(f"Fecha: {fecha}",styles["Normal"]),
    Paragraph(f"Total subvenciones: {total:,.0f} €",styles["Normal"]),
    Paragraph(politico,styles["Normal"])
]

for a in alertas:
    contenido.append(Paragraph(a,styles["Normal"]))

doc.build(contenido)


# ==================================================
# MANIFEST APP INSTALABLE
# ==================================================

manifest={
"name":"Observatorio Público",
"short_name":"Observatorio",
"start_url":"./",
"display":"standalone",
"background_color":"#0b132b",
"theme_color":"#0b132b"
}

json.dump(manifest,open("manifest.json","w"))


# ==================================================
# HTML FINAL DASHBOARD
# ==================================================

labels=hist["fecha"].astype(str).tolist()
datos=hist["total"].tolist()

html=f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Observatorio Público TOTAL</title>

<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="manifest" href="manifest.json">

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<link rel="stylesheet"
 href="https://unpkg.com/leaflet/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

<style>
body{{font-family:system-ui;background:#0b132b;color:white;padding:10px}}
.card{{background:#1c2541;padding:15px;border-radius:12px;margin:10px 0}}
</style>
</head>

<body>

<h1>📊 Observatorio Público</h1>
<p>Actualizado: {fecha}</p>

<div class="card">
Subvenciones totales: {total:,.0f} €
</div>

<div class="card">
<b>Análisis político:</b><br>{politico}
</div>

<div class="card">
<b>Alertas:</b><br>
{"<br>".join(alertas) if alertas else "Sin alertas"}
</div>

<h2>Evolución</h2>
<canvas id="graf"></canvas>

<script>
new Chart(document.getElementById('graf'),{{
type:'line',
data:{{labels:{labels},
datasets:[{{label:'Subvenciones',data:{datos}}}]}}
}});
</script>

<h2>BOE relevante</h2>
"""

for b in boe:
    html+=f"<p><a href='{b['link']}' target='_blank'>{b['titulo']}</a></p>"

html+="""

<div class="card">
<a href="datos/informe.pdf">📄 Informe PDF</a>
</div>

</body>
</html>
"""

open("index.html","w",encoding="utf-8").write(html)

print("OBSERVATORIO TOTAL DEFINITIVO GENERADO")
