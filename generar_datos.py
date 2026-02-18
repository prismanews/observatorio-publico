import pandas as pd
import requests, json, os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# Configuración básica
os.makedirs("datos", exist_ok=True)
PDF_PATH = "datos/informe.pdf"
CSV_LOCAL = "datos/data.csv"

def procesar_observatorio():
    URL = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        r = requests.get(URL, headers=headers, timeout=30)
        with open(CSV_LOCAL, "wb") as f:
            f.write(r.content)
        
        # Lectura con encoding flexible
        df = pd.read_csv(CSV_LOCAL, sep=";", encoding="latin1", on_bad_lines='skip', low_memory=False)
        cols = [c.lower() for c in df.columns]

        # Buscador de columnas robusto
        idx_imp = next((i for i, c in enumerate(cols) if 'importe' in c), None)
        idx_ben = next((i for i, c in enumerate(cols) if any(x in c for x in ['beneficiario', 'nombre', 'razon'])), None)

        # Extraer y limpiar datos
        if idx_imp is not None:
            col_name = df.columns[idx_imp]
            df['Importe'] = df[col_name].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df['Importe'] = pd.to_numeric(df['Importe'], errors="coerce").fillna(0)
        else:
            df['Importe'] = 0

        if idx_ben is not None:
            df['Beneficiario'] = df[df.columns[idx_ben]].fillna("Desconocido")
        else:
            df['Beneficiario'] = "Sin Datos"

    except Exception as e:
        print(f"Error: {e}")
        df = pd.DataFrame(columns=['Importe', 'Beneficiario'])

    # Cálculos
    total = df['Importe'].sum()
    conteo = len(df)
    ranking = df.groupby('Beneficiario')['Importe'].sum().sort_values(ascending=False).head(5)

    # Generar PDF simple
    try:
        doc = SimpleDocTemplate(PDF_PATH, pagesize=A4)
        doc.build([Paragraph(f"Total: {total:,.2f} EUR", getSampleStyleSheet()['Title'])])
    except:
        pass

    # Generar HTML (Estructura limpia para evitar IndentationError)
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="estilo.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <header class="boe-header">
            <h2>OBSERVATORIO DE TRANSPARENCIA</h2>
            <p>Actualizado: {fecha}</p>
        </header>
        <div class="boe-card">
            <div class="stat-group">
                <div class="stat-box"><strong>{total:,.2f} €</strong><br><small>Total Auditado</small></div>
                <div class="stat-box"><strong>{conteo}</strong><br><small>Expedientes</small></div>
            </div>
            <div style="padding:20px"><canvas id="myChart"></canvas></div>
            <a href="{PDF_PATH}" class="btn-link">DESCARGAR INFORME PDF</a>
        </div>
    </div>
    <script>
        new Chart(document.getElementById('myChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(list(ranking.index))},
                datasets: [{{ label: 'Euros', data: {json.dumps(list(ranking.values))}, backgroundColor: '#5bc0be' }}]
            }},
            options: {{ indexAxis: 'y' }}
        }});
    </script>
</body>
</html>"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)

if __name__ == "__main__":
    procesar_observatorio()
