import pandas as pd
import json
import os
from datetime import datetime

# ============================
# CONFIG
# ============================

DATASET_URL = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"
HIST = "datos/historico.csv"
API = "datos/api.json"

print("Descargando dataset oficial…")

try:
    df = pd.read_csv(DATASET_URL, sep=";", encoding="latin1", low_memory=False)
except Exception as e:
    print("Error dataset:", e)
    exit()

# ============================
# LIMPIEZA
# ============================

df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce")
df = df.dropna(subset=["Importe"])
df = df[df["Importe"] > 0]

df["Beneficiario"] = df.get("Beneficiario", "No identificado")

# ============================
# CLASIFICACIÓN SECTOR
# ============================

def sector(x):
    x = str(x).lower()
    if "universidad" in x:
        return "Educación"
    if "fundación" in x or "ong" in x:
        return "Social"
    if "ministerio" in x or "ayuntamiento" in x:
        return "Administración"
    if "sl" in x or "sa" in x:
        return "Empresa"
    return "Otros"

df["Sector"] = df["Beneficiario"].apply(sector)

sector_total = df.groupby("Sector")["Importe"].sum().sort_values(ascending=False)

# ============================
# MÉTRICAS CLAVE
# ============================

total = df["Importe"].sum()
media = df["Importe"].mean()
maximo = df["Importe"].max()

top = df.groupby("Beneficiario")["Importe"].sum().sort_values(ascending=False).head(10)

fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

# ============================
# HISTÓRICO EVOLUCIÓN
# ============================

os.makedirs("datos", exist_ok=True)

nuevo = pd.DataFrame([{
    "fecha": fecha,
    "total": total,
    "media": media
}])

if os.path.exists(HIST):
    hist = pd.read_csv(HIST)
    hist = pd.concat([hist, nuevo])
else:
    hist = nuevo

hist.to_csv(HIST, index=False)

# Comparación temporal
insights = []

if len(hist) > 1:
    ultimo = hist.iloc[-2]["total"]
    cambio = ((total - ultimo) / ultimo) * 100

    if cambio > 10:
        insights.append(f"Aumento notable del gasto público (+{cambio:.1f}%).")
    elif cambio < -10:
        insights.append(f"Reducción significativa del gasto ({cambio:.1f}%).")

# Concentración
concentracion = top.head(3).sum() / total * 100
if concentracion > 40:
    insights.append("Alta concentración de ayudas en pocos beneficiarios.")

# Sector dominante
sector_top = sector_total.index[0]
insights.append(f"El sector dominante es: {sector_top}.")

# ============================
# EXPORT API
# ============================

api = {
    "fecha": fecha,
    "total": float(total),
    "media": float(media),
    "maximo": float(maximo),
    "sectores": sector_total.to_dict(),
    "top": top.to_dict(),
    "insights": insights
}

with open(API, "w") as f:
    json.dump(api, f, indent=2)

# ============================
# HTML DASHBOARD PRO++++
# ============================

labels = hist["fecha"].astype(str).tolist()
datos = hist["total"].tolist()

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Observatorio Público PRO++++</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body {{
font-family:system-ui;
background:#0b132b;
color:#fff;
padding:20px;
}}

.card {{
background:#1c2541;
padding:20px;
margin:10px 0;
border-radius:12px;
}}

.insights {{
background:#3a0f0f;
padding:20px;
border-radius:12px;
margin-top:20px;
}}
</style>
</head>

<body>

<h1>📊 Observatorio Público PRO++++</h1>
<p>Datos abiertos oficiales analizados automáticamente.</p>
<p>Actualizado: {fecha}</p>

<div class="card">
<h2>Total subvenciones</h2>
{total:,.0f} €
</div>

<div class="card">
<h2>Media</h2>
{media:,.0f} €
</div>

<h2>Evolución temporal</h2>
<canvas id="graf"></canvas>

<script>
new Chart(document.getElementById('graf'), {{
type:'line',
data:{{
labels:{labels},
datasets:[{{label:'Total',data:{datos}}}]
}}
}});
</script>

<div class="insights">
<h2>Insights automáticos</h2>
<ul>
{''.join(f"<li>{i}</li>" for i in insights)}
</ul>
</div>

</body>
</html>
"""

with open("index.html","w",encoding="utf-8") as f:
    f.write(html)

print("Observatorio PRO++++ generado")
