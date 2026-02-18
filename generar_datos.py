import pandas as pd
import requests
from datetime import datetime

# ===============================
# DATASET OFICIAL ESPAÑA
# BDNS - Subvenciones públicas
# ===============================
URL_DATOS = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"


print("Descargando dataset oficial...")

try:
    df = pd.read_csv(URL_DATOS, sep=";", encoding="latin1", low_memory=False)
except Exception as e:
    print("Error descargando dataset:", e)
    exit()


# ===============================
# LIMPIEZA DATOS
# ===============================

df = df.dropna(subset=["Importe"])
df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce")
df = df.dropna(subset=["Importe"])

total = df["Importe"].sum()
media = df["Importe"].mean()
maximo = df["Importe"].max()

top = (
    df.groupby("Beneficiario")["Importe"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)


# ===============================
# INSIGHT AUTOMÁTICO SOCIAL
# ===============================

concentracion = top.iloc[0] / total * 100

if concentracion > 20:
    insight = "Alta concentración de subvenciones en pocos beneficiarios."
elif media > 500000:
    insight = "Importe medio elevado en subvenciones públicas."
else:
    insight = "Distribución relativamente equilibrada del gasto público."


fecha = datetime.now().strftime("%d/%m/%Y %H:%M")


# ===============================
# GENERAR HTML FINAL
# ===============================

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Observatorio Público</title>

<link rel="stylesheet" href="estilo.css">

<meta name="viewport" content="width=device-width, initial-scale=1">

<!-- MAPA Leaflet -->
<link rel="stylesheet"
 href="https://unpkg.com/leaflet/dist/leaflet.css"/>

<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

</head>

<body>

<header>
<h1>📊 Observatorio Público</h1>
<p>Datos oficiales analizados automáticamente para transparencia ciudadana.</p>
<p class="fecha">Actualizado: {fecha}</p>
</header>

<section class="stats">
<h2>Total subvenciones</h2>
<p class="big">{total:,.0f} €</p>

<div class="mini">
Media: {media:,.0f} €<br>
Máxima: {maximo:,.0f} €
</div>
</section>

<section class="insight">
<h2>Insight automático</h2>
<p>{insight}</p>
</section>

<section>
<h2>Top beneficiarios</h2>
"""

for nombre, importe in top.items():
    html += f"""
    <div class="card">
        <b>{nombre}</b>
        <span>{importe:,.0f} €</span>
    </div>
    """

html += """

</section>

<section>
<h2>Mapa orientativo España</h2>
<div id="mapa" style="height:400px;"></div>
</section>

<footer>
Proyecto ciudadano · Datos oficiales abiertos · Transparencia pública
</footer>


<script>

// MAPA SIN ERRORES PYTHON (llaves escapadas)
var map = L.map('mapa').setView([40.4168, -3.7038], 6);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {{
    attribution: '© OpenStreetMap'
}}).addTo(map);

L.marker([40.4168, -3.7038]).addTo(map)
.bindPopup("Centro político-administrativo");

</script>

</body>
</html>
"""


with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)


print("Observatorio actualizado correctamente.")
