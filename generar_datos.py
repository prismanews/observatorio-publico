import requests
import pandas as pd
from datetime import datetime

URL_DATOS = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"

fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

print("Descargando datos públicos...")

try:
    df = pd.read_csv(URL_DATOS, sep=";", encoding="latin1", low_memory=False)
    
    df = df.dropna(subset=["Importe"])
    df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce")
    df = df.dropna(subset=["Importe"])

    top_beneficiarios = (
        df.groupby("Beneficiario")["Importe"]
        .sum()
        .sort_values(ascending=False)
        .head(20)
    )

    total_subvenciones = df["Importe"].sum()

    contenido = ""
    for nombre, importe in top_beneficiarios.items():
        contenido += f"""
        <div class="card">
            <b>{nombre}</b>
            <span>{importe:,.0f} €</span>
        </div>
        """

except Exception as e:
    print("Error datos:", e)

    total_subvenciones = "No disponible"
    contenido = "<p>No se pudieron cargar datos públicos.</p>"


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
<p>Datos abiertos analizados automáticamente.</p>
<p class="fecha">Actualizado: {fecha}</p>
</header>

<section class="stats">
<h2>Total subvenciones</h2>
<p class="big">{total_subvenciones}</p>
</section>

<section>
<h2>Top beneficiarios</h2>
{contenido}
</section>

<footer>
Proyecto ciudadano · Datos públicos oficiales
</footer>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("index.html generado")
