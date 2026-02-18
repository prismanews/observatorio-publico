import requests
import pandas as pd
from datetime import datetime


# ==============================
# CONFIGURACIÓN
# ==============================

# Dataset público ejemplo (BDNS subvenciones)
URL_DATOS = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"


print("Descargando datos públicos...")

try:
    df = pd.read_csv(URL_DATOS, sep=";", encoding="latin1", low_memory=False)
except Exception as e:
    print("Error descargando datos:", e)
    exit()


# ==============================
# LIMPIEZA DATOS
# ==============================

df = df.dropna(subset=["Importe"])
df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce")

df = df.dropna(subset=["Importe"])


# ==============================
# ANÁLISIS SIMPLE
# ==============================

top_beneficiarios = (
    df.groupby("Beneficiario")["Importe"]
    .sum()
    .sort_values(ascending=False)
    .head(20)
)

total_subvenciones = df["Importe"].sum()

fecha = datetime.now().strftime("%d/%m/%Y %H:%M")


# ==============================
# GENERAR WEB HTML
# ==============================

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Observatorio Público</title>
<link rel="stylesheet" href="estilo.css">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>

<header>
<h1>📊 Observatorio Público</h1>
<p>Datos abiertos analizados automáticamente para mejorar la transparencia.</p>
<p class="fecha">Actualizado: {fecha}</p>
</header>

<section class="stats">
<h2>Total subvenciones analizadas</h2>
<p class="big">{total_subvenciones:,.0f} €</p>
</section>

<section>
<h2>Top beneficiarios</h2>
"""

for nombre, importe in top_beneficiarios.items():
    html += f"""
    <div class="card">
        <b>{nombre}</b>
        <span>{importe:,.0f} €</span>
    </div>
    """

html += """
</section>

<footer>
Datos públicos oficiales · Proyecto ciudadano de transparencia
</footer>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Web generada correctamente")
