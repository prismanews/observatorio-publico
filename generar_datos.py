import pandas as pd
from datetime import datetime

# ==============================
# CONFIGURACIÓN
# ==============================

URL_DATOS = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"

print("Descargando datos públicos...")

try:
    df = pd.read_csv(URL_DATOS, sep=";", encoding="latin1", low_memory=False)
except Exception as e:
    print("❌ Error descargando datos:", e)
    exit()

print("Datos descargados correctamente")


# ==============================
# LIMPIEZA DE DATOS
# ==============================

# Normalizar nombres columnas por si cambian ligeramente
df.columns = df.columns.str.strip()

# Buscar columnas relevantes
col_importe = [c for c in df.columns if "Importe" in c][0]
col_beneficiario = [c for c in df.columns if "Beneficiario" in c][0]

df = df.dropna(subset=[col_importe])
df[col_importe] = pd.to_numeric(df[col_importe], errors="coerce")
df = df.dropna(subset=[col_importe])


# ==============================
# ANÁLISIS SIMPLE
# ==============================

top_beneficiarios = (
    df.groupby(col_beneficiario)[col_importe]
    .sum()
    .sort_values(ascending=False)
    .head(20)
)

total_subvenciones = df[col_importe].sum()
num_registros = len(df)

fecha = datetime.now().strftime("%d/%m/%Y %H:%M")


# ==============================
# GENERAR HTML
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
<p>Datos abiertos analizados automáticamente.</p>
<p class="fecha">Actualizado: {fecha}</p>
</header>

<section class="stats">
<div>
<h2>Total subvenciones</h2>
<p class="big">{total_subvenciones:,.0f} €</p>
</div>

<div>
<h2>Registros analizados</h2>
<p class="big">{num_registros:,}</p>
</div>
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
Proyecto ciudadano · Datos públicos oficiales · Transparencia
</footer>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ index.html generado correctamente")
