import pandas as pd
import json
import os
from datetime import datetime

# ==============================
# CONFIGURACIÓN
# ==============================

DATASET_URL = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"
HISTORICO = "datos/historico.csv"
API_JSON = "datos/api.json"

print("Descargando dataset oficial...")

try:
    df = pd.read_csv(DATASET_URL, sep=";", encoding="latin1", low_memory=False)
except Exception as e:
    print("Error dataset:", e)
    exit()

# ==============================
# LIMPIEZA
# ==============================

df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce")
df = df.dropna(subset=["Importe"])
df = df[df["Importe"] > 0]

if "Beneficiario" not in df.columns:
    df["Beneficiario"] = "No identificado"

# ==============================
# MÉTRICAS PRINCIPALES
# ==============================

total = df["Importe"].sum()
media = df["Importe"].mean()
maximo = df["Importe"].max()

top = (
    df.groupby("Beneficiario")["Importe"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

# ==============================
# DETECCIÓN AVANZADA ANOMALÍAS
# ==============================

z = (df["Importe"] - media) / df["Importe"].std()
anomalias = df[z > 3]

alertas = []

if len(anomalias) > 0:
    alertas.append(f"{len(anomalias)} subvenciones estadísticamente anómalas.")

if maximo > media * 15:
    alertas.append("Subvención extremadamente alta detectada.")

# ==============================
# HISTÓRICO AUTOMÁTICO
# ==============================

os.makedirs("datos", exist_ok=True)

registro = pd.DataFrame([{
    "fecha": fecha,
    "total": total,
    "media": media,
    "maximo": maximo
}])

if os.path.exists(HISTORICO):
    hist = pd.read_csv(HISTORICO)
    hist = pd.concat([hist, registro])
else:
    hist = registro

hist.to_csv(HISTORICO, index=False)

# ==============================
# EXPORT JSON (API)
# ==============================

api = {
    "fecha": fecha,
    "total": float(total),
    "media": float(media),
    "maximo": float(maximo),
    "top": top.to_dict(),
    "alertas": alertas
}

with open(API_JSON, "w") as f:
    json.dump(api, f, indent=2)

# ==============================
# HTML PRO++ DASHBOARD
# ==============================

hist_labels = hist["fecha"].astype(str).tolist()
hist_totales = hist["total"].tolist()

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Observatorio Público PRO++</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body {{
font-family:system-ui;
background:#0b132b;
color:#fff;
margin:0;
padding:20px;
}}

header {{
text-align:center;
margin-bottom:40px;
}}

.grid {{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
gap:20px;
}}

.card {{
background:#1c2541;
padding:20px;
border-radius:12px;
}}

.insights {{
background:#3a0f0f;
padding:20px;
margin-top:30px;
border-radius:12px;
}}
</style>
</head>

<body>

<header>
<h1>📊 Observatorio Público PRO++</h1>
<p>Datos abiertos oficiales analizados automáticamente.</p>
<p>Actualizado: {fecha}</p>
</header>

<section class="grid">
<div class="card">
<h2>Total</h2>
<p>{total:,.0f} €</p>
</div>

<div class="card">
<h2>Media</h2>
<p>{media:,.0f} €</p>
</div>

<div class="card">
<h2>Mayor</h2>
<p>{maximo:,.0f} €</p>
</div>
</section>

<h2>Evolución subvenciones</h2>
<canvas id="grafica"></canvas>

<script>
const ctx = document.getElementById('grafica');

new Chart(ctx, {{
type:'line',
data:{{
labels:{hist_labels},
datasets:[{{
label:'Total subvenciones',
data:{hist_totales},
borderWidth:2
}}]
}}
}});
</script>

<section>
<h2>Top beneficiarios</h2>
"""

for n,v in top.items():
    html += f"<p><b>{n}</b> — {v:,.0f} €</p>"

html += "<section class='insights'><h2>Alertas</h2><ul>"

for a in alertas:
    html += f"<li>{a}</li>"

html += """
</ul></section>

<footer>
Proyecto ciudadano de transparencia · Datos oficiales
</footer>

</body>
</html>
"""

with open("index.html","w",encoding="utf-8") as f:
    f.write(html)

print("Observatorio PRO++ generado")
