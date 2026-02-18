import pandas as pd
import requests
from datetime import datetime

# ======================================
# DATASET REAL BDNS SUBVENCIONES ESPAÑA
# ======================================

URL = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"

print("Descargando dataset oficial...")

try:
    df = pd.read_csv(URL, sep=";", encoding="latin1", low_memory=False)
except:
    print("Error dataset → usando demo")
    df = pd.DataFrame({
        "Beneficiario": ["Empresa A","ONG B","Uni C","Empresa A"],
        "Importe": [120000,50000,80000,60000],
        "Provincia": ["Madrid","Barcelona","Valencia","Madrid"]
    })

# ======================================
# LIMPIEZA
# ======================================

df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce")
df = df.dropna(subset=["Importe"])

if "Provincia" not in df.columns:
    df["Provincia"] = "Sin datos"

# ======================================
# KPIs
# ======================================

total = df["Importe"].sum()
media = df["Importe"].mean()
maximo = df["Importe"].max()

# Ranking beneficiarios
ranking = (
    df.groupby("Beneficiario")["Importe"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

# Provincias
provincias = (
    df.groupby("Provincia")["Importe"]
    .sum()
    .sort_values(ascending=False)
    .head(15)
)

# Alertas simples
alerta = ""
if maximo > media * 10:
    alerta = "⚠️ Posible subvención desproporcionada detectada."

# Fecha
fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

# ======================================
# HTML DASHBOARD
# ======================================

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Observatorio Público</title>
<link rel="stylesheet" href="estilo.css">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="manifest" href="manifest.json">
</head>

<body>

<div class="container">

<header class="obs-header">
<h1 class="obs-header__title">📡 Observatorio Transparencia Pública</h1>
<span class="obs-header__sync">Actualizado: {fecha}</span>
</header>

<div class="obs-card">

<div class="obs-stats">
<div class="obs-stats__item">
<span class="obs-stats__label">Total subvenciones</span>
<span class="obs-stats__value">{total:,.0f} €</span>
</div>

<div class="obs-stats__item">
<span class="obs-stats__label">Media</span>
<span class="obs-stats__value">{media:,.0f} €</span>
</div>

<div class="obs-stats__item">
<span class="obs-stats__label">Máxima</span>
<span class="obs-stats__value">{maximo:,.0f} €</span>
</div>
</div>
"""

if alerta:
    html += f'<div class="obs-alert">{alerta}</div>'

html += """

<h2>Ranking beneficiarios</h2>
<ul>
"""

for b, i in ranking.items():
    html += f"<li>{b}: {i:,.0f} €</li>"

html += "</ul>"

html += """

<h2>Mapa subvenciones por provincia</h2>
<canvas id="mapa"></canvas>

<h2>Evolución gasto</h2>
<canvas id="grafico"></canvas>

</div>
</div>

<script>

const provincias = """ + str(list(provincias.index)) + """;
const valores = """ + str(list(provincias.values)) + """;

new Chart(document.getElementById('mapa'),{
type:'bar',
data:{
labels:provincias,
datasets:[{
label:'Subvenciones €',
data:valores
}]
}
});

new Chart(document.getElementById('grafico'),{
type:'line',
data:{
labels:provincias,
datasets:[{
label:'Evolución',
data:valores
}]
}
});

</script>

</body>
</html>
"""

with open("index.html","w",encoding="utf-8") as f:
    f.write(html)

print("Observatorio actualizado correctamente")
