import pandas as pd
import requests
from datetime import datetime
import os

# ===============================
# CONFIG DATASET OFICIAL ESPAÑA
# ===============================

URL_DATOS = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"
HISTORICO = "datos/historico.csv"

print("Descargando dataset oficial BDNS...")

try:
    df = pd.read_csv(URL_DATOS, sep=";", encoding="latin1", low_memory=False)
except Exception as e:
    print("Error dataset:", e)
    exit()

# ===============================
# LIMPIEZA ROBUSTA
# ===============================

if "Importe" not in df.columns:
    print("Dataset inesperado")
    exit()

df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce")
df = df.dropna(subset=["Importe"])

if "Beneficiario" not in df.columns:
    df["Beneficiario"] = "No identificado"

df = df[df["Importe"] > 0]

# ===============================
# MÉTRICAS PRINCIPALES
# ===============================

total = df["Importe"].sum()
media = df["Importe"].mean()
mayor = df["Importe"].max()

top_benef = (
    df.groupby("Beneficiario")["Importe"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

# ===============================
# HISTÓRICO AUTOMÁTICO
# ===============================

os.makedirs("datos", exist_ok=True)

registro = pd.DataFrame([{
    "fecha": datetime.now(),
    "total": total,
    "media": media,
    "mayor": mayor
}])

if os.path.exists(HISTORICO):
    hist = pd.read_csv(HISTORICO)
    hist = pd.concat([hist, registro])
else:
    hist = registro

hist.to_csv(HISTORICO, index=False)

# ===============================
# INSIGHTS AUTOMÁTICOS
# ===============================

concentracion = top_benef.head(3).sum() / total * 100

insights = []

if concentracion > 40:
    insights.append("Alta concentración: pocas entidades reciben gran parte de las ayudas.")
else:
    insights.append("Distribución relativamente diversificada de subvenciones.")

if media > 100000:
    insights.append("Importe medio elevado: predominan ayudas grandes.")
else:
    insights.append("Importe medio moderado.")

if mayor > 1_000_000:
    insights.append("Existe al menos una subvención de gran volumen.")

# ===============================
# GENERAR HTML DASHBOARD
# ===============================

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Observatorio Público</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="estilo.css">
</head>

<body>

<header>
<h1>📊 Observatorio Público</h1>
<p>Datos abiertos oficiales analizados automáticamente para mejorar la transparencia.</p>
<p class="fecha">Actualizado: {fecha}</p>
</header>

<section class="grid">
<div class="card big">
<h2>Total subvenciones</h2>
<p>{total:,.0f} €</p>
</div>

<div class="card">
<h3>Media</h3>
<p>{media:,.0f} €</p>
</div>

<div class="card">
<h3>Mayor subvención</h3>
<p>{mayor:,.0f} €</p>
</div>
</section>

<section>
<h2>Top beneficiarios</h2>
"""

for n, v in top_benef.items():
    html += f"<div class='fila'><b>{n}</b> {v:,.0f} €</div>"

html += f"""
</section>

<section class="insights">
<h2>🧠 Insights automáticos</h2>
<ul>
{''.join(f"<li>{i}</li>" for i in insights)}
</ul>
</section>

<footer>
Proyecto ciudadano · Datos públicos oficiales · Transparencia institucional
</footer>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Dashboard generado correctamente")
