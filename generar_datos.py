import pandas as pd
import requests
from datetime import datetime
import os

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


# ===============================
# CONFIG
# ===============================

DATASET_URL = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"
HISTORICO = "datos/historico.csv"
PDF_FILE = "datos/informe.pdf"

os.makedirs("datos", exist_ok=True)


# ===============================
# DESCARGAR DATASET OFICIAL
# ===============================

print("Descargando dataset BDNS...")

try:
    df = pd.read_csv(DATASET_URL, sep=";", encoding="latin1", low_memory=False)
except Exception as e:
    print("Error dataset:", e)
    df = pd.DataFrame()


# ===============================
# LIMPIEZA DATOS
# ===============================

if not df.empty and "Importe" in df.columns:

    df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce")
    df = df.dropna(subset=["Importe"])

    total = df["Importe"].sum()
    media = df["Importe"].mean()
    mayor = df["Importe"].max()

    ranking = (
        df.groupby("Beneficiario")["Importe"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

else:
    total = media = mayor = 0
    ranking = {}


fecha = datetime.now().strftime("%d/%m/%Y %H:%M")


# ===============================
# HISTÓRICO AUTOMÁTICO
# ===============================

nuevo = pd.DataFrame([{
    "fecha": fecha,
    "total": total,
    "media": media
}])

if os.path.exists(HISTORICO):
    hist = pd.read_csv(HISTORICO)
    hist = pd.concat([hist, nuevo])
else:
    hist = nuevo

hist.to_csv(HISTORICO, index=False)


# ===============================
# INSIGHTS AUTOMÁTICOS
# ===============================

concentracion = ranking.iloc[0] / total * 100 if total > 0 else 0

if concentracion > 20:
    insight = "Alta concentración de subvenciones en pocos beneficiarios."
elif media > 200000:
    insight = "Subvenciones medias elevadas: posible concentración institucional."
else:
    insight = "Distribución relativamente equilibrada del gasto público."


# ===============================
# INFORME PDF AUTOMÁTICO
# ===============================

styles = getSampleStyleSheet()
doc = SimpleDocTemplate(PDF_FILE)

contenido = [
    Paragraph("Informe Observatorio Público", styles["Title"]),
    Spacer(1, 12),
    Paragraph(f"Fecha: {fecha}", styles["Normal"]),
    Paragraph(f"Total subvenciones: {total:,.0f} €", styles["Normal"]),
    Paragraph(f"Media: {media:,.0f} €", styles["Normal"]),
    Paragraph(insight, styles["Normal"])
]

doc.build(contenido)


# ===============================
# DASHBOARD HTML FINAL
# ===============================

labels = hist["fecha"].astype(str).tolist()
datos = hist["total"].tolist()

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Observatorio Público PRO</title>

<meta name="viewport" content="width=device-width, initial-scale=1">

<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body {{
font-family:system-ui;
background:#0b132b;
color:white;
max-width:900px;
margin:auto;
padding:20px;
}}

.card {{
background:#1c2541;
padding:20px;
border-radius:12px;
margin:15px 0;
}}

.big {{
font-size:2em;
font-weight:bold;
}}
</style>
</head>

<body>

<h1>📊 Observatorio Público</h1>
<p>Actualizado: {fecha}</p>

<div class="card">
<h2>Total subvenciones</h2>
<p class="big">{total:,.0f} €</p>
<p>Media: {media:,.0f} €</p>
<p>Mayor ayuda: {mayor:,.0f} €</p>
</div>

<div class="card">
<h2>Insight automático</h2>
<p>{insight}</p>
</div>

<div class="card">
<h2>Evolución histórica</h2>
<canvas id="graf"></canvas>
</div>

<script>
new Chart(document.getElementById('graf'), {{
type:'line',
data:{{
labels:{labels},
datasets:[{{label:'Total subvenciones', data:{datos}}}]
}}
}});
</script>

<div class="card">
<h2>Ranking beneficiarios</h2>
"""

for n, v in ranking.items():
    html += f"<p><b>{n}</b>: {v:,.0f} €</p>"

html += """

</div>

<div class="card">
<a href="datos/informe.pdf" target="_blank">📄 Descargar informe PDF</a>
</div>

<footer>
Proyecto ciudadano · Datos públicos oficiales · Transparencia institucional
</footer>

</body>
</html>
"""


with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)


print("Observatorio definitivo generado correctamente")
