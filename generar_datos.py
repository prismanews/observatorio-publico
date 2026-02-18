import pandas as pd
import requests
import json
from datetime import datetime

# ======================================================
# DATASET OFICIAL BDNS (Subvenciones públicas España)
# ======================================================

URL_SUBVENCIONES = (
    "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"
)

print("Descargando dataset oficial BDNS...")

try:
    df = pd.read_csv(
        URL_SUBVENCIONES,
        sep=";",
        encoding="latin1",
        low_memory=False
    )
except Exception as e:
    print("Error descargando dataset:", e)
    exit()


# ======================================================
# LIMPIEZA BÁSICA
# ======================================================

df = df.rename(columns=str.strip)

if "Importe" not in df.columns:
    print("Campo Importe no encontrado.")
    exit()

df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce")
df = df.dropna(subset=["Importe"])

# provincia suele venir como "Provincia Beneficiario"
provincia_col = next(
    (c for c in df.columns if "provincia" in c.lower()),
    None
)

beneficiario_col = next(
    (c for c in df.columns if "beneficiario" in c.lower()),
    None
)

if not provincia_col or not beneficiario_col:
    print("Columnas clave no detectadas.")
    exit()


# ======================================================
# MÉTRICAS PRINCIPALES
# ======================================================

total_subvenciones = df["Importe"].sum()
media_subvenciones = df["Importe"].mean()
max_subvencion = df["Importe"].max()

ranking_beneficiarios = (
    df.groupby(beneficiario_col)["Importe"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

ranking_provincias = (
    df.groupby(provincia_col)["Importe"]
    .sum()
    .sort_values(ascending=False)
)

# JSON para mapa (heatmap provincias)
mapa_provincias = ranking_provincias.reset_index().to_dict("records")

with open("mapa_subvenciones.json", "w", encoding="utf-8") as f:
    json.dump(mapa_provincias, f, ensure_ascii=False, indent=2)


# ======================================================
# GENERACIÓN HTML DASHBOARD
# ======================================================

fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Observatorio Transparencia Pública</title>
<link rel="stylesheet" href="estilo.css">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>

<body>

<header>
<h1>📡 Observatorio Transparencia Pública</h1>
<p>Datos oficiales de subvenciones públicas en España</p>
<p>Actualizado: {fecha}</p>
</header>

<section class="stats">
<div class="card">
<h2>Total subvenciones</h2>
<p>{total_subvenciones:,.0f} €</p>
</div>

<div class="card">
<h2>Media</h2>
<p>{media_subvenciones:,.0f} €</p>
</div>

<div class="card">
<h2>Máxima</h2>
<p>{max_subvencion:,.0f} €</p>
</div>
</section>

<section>
<h2>🏆 Ranking beneficiarios</h2>
<ul>
"""

for nombre, importe in ranking_beneficiarios.items():
    html += f"<li>{nombre}: {importe:,.0f} €</li>"

html += """
</ul>
</section>

<section>
<h2>🗺️ Ranking provincias</h2>
<ul>
"""

for prov, imp in ranking_provincias.head(15).items():
    html += f"<li>{prov}: {imp:,.0f} €</li>"

html += """
</ul>
<p>(Mapa interactivo en preparación)</p>
</section>

<footer>
Datos abiertos oficiales · BDNS · Proyecto ciudadano
</footer>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Observatorio generado correctamente")
