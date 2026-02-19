import os
import json
import random
from datetime import datetime

# -------------------------------
# 1. CREAR DATOS
# -------------------------------

os.makedirs("datos", exist_ok=True)

datos = {
    "actualizado": datetime.utcnow().strftime("%d %B %Y · %H:%M UTC"),
    "subvenciones": [
        {
            "organismo": "Ministerio de Cultura",
            "importe": random.randint(20000, 120000),
            "objeto": "Proyectos culturales"
        },
        {
            "organismo": "Comunidad Autónoma",
            "importe": random.randint(15000, 90000),
            "objeto": "Innovación digital"
        }
    ]
}

with open("datos/observatorio.json", "w", encoding="utf-8") as f:
    json.dump(datos, f, ensure_ascii=False, indent=2)

# -------------------------------
# 2. GENERAR HTML AUTOMÁTICO
# -------------------------------

total_importe = sum(s["importe"] for s in datos["subvenciones"])

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Observatorio Público</title>
<link rel="stylesheet" href="estilo.css">
<link rel="manifest" href="manifest.json">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>

<body>

<div class="container">

<header class="obs-header">
<h1 class="obs-header__title">Observatorio de Transparencia Pública</h1>
<span class="obs-header__sync">
Última actualización: {datos['actualizado']}
</span>
</header>

<section class="obs-card">

<div class="obs-stats">

<div class="obs-stats__item">
<span class="obs-stats__label">Subvenciones analizadas</span>
<span class="obs-stats__value">{len(datos['subvenciones'])}</span>
</div>

<div class="obs-stats__item">
<span class="obs-stats__label">Importe total</span>
<span class="obs-stats__value">{total_importe:,.0f} €</span>
</div>

</div>

<h2>Detalle subvenciones</h2>
<ul>
"""

for s in datos["subvenciones"]:
    html += f"<li><b>{s['organismo']}</b>: {s['importe']:,.0f} € — {s['objeto']}</li>"

html += """

</ul>

<p style="margin-top:40px;font-size:0.85rem;color:#666;">
Datos generados automáticamente · Proyecto Observatorio Público
</p>

</section>
</div>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Observatorio generado correctamente")
