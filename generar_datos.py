import pandas as pd
import requests
from datetime import datetime

# ==============================
# DATASET PÚBLICO REAL (España)
# Base Nacional de Subvenciones
# ==============================

URL_DATOS = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"

print("Descargando dataset público oficial...")

try:
    df = pd.read_csv(URL_DATOS, sep=";", encoding="latin1", low_memory=False)
except Exception as e:
    print("Error dataset:", e)
    exit()

# ==============================
# LIMPIEZA PROFESIONAL
# ==============================

df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce")
df = df.dropna(subset=["Importe"])

df = df[df["Importe"] > 0]

# ==============================
# ANÁLISIS ÚTIL (NO SOLO SUMA)
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

# Insight automático potente
top1 = top.iloc[0]
concentracion = (top1 / total) * 100

fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

# ==============================
# GENERACIÓN WEB PROFESIONAL
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
<p>Datos públicos analizados automáticamente.</p>
<p class="fecha">Actualizado: {fecha}</p>
</header>

<section class="intro">
<h2>¿Para qué sirve este observatorio?</h2>
<ul>
<li>Visualizar el destino de subvenciones públicas</li>
<li>Detectar concentración de ayudas</li>
<li>Facilitar transparencia ciudadana</li>
<li>Traducir datos complejos en información clara</li>
</ul>
</section>

<section class="stats">
<h2>Total subvenciones analizadas</h2>
<p class="big">{total:,.0f} €</p>
<p>Media subvención: {media:,.0f} €</p>
<p>Mayor subvención detectada: {maximo:,.0f} €</p>
</section>

<section class="insight">
<h2>Insight automático</h2>
<p>
El principal beneficiario concentra aproximadamente
<b>{concentracion:.1f}%</b> del total analizado.
Esto puede indicar concentración de financiación pública.
</p>
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

<footer>
Fuente: Base Nacional de Subvenciones · Datos abiertos oficiales<br>
Proyecto independiente de análisis ciudadano para la transparencia pública.
</footer>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Observatorio generado correctamente")
