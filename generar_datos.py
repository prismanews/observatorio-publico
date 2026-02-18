import pandas as pd
import requests, json, os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# Configuración de entorno
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
        
        # Lectura con encoding español
        df = pd.read_csv(CSV_LOCAL, sep=";", encoding="latin1", on_bad_lines='skip', low_memory=False)
        cols = [str(c).lower() for c in df.columns]

        # Buscador de columnas por posición e inteligencia difusa
        idx_imp = next((i for i, c in enumerate(cols) if 'importe' in c), None)
        idx_ben = next((i for i, c in enumerate(cols) if any(x in c for x in ['beneficiario', 'nombre', 'razon'])), None)

        if idx_imp is not None:
            c_name = df.columns[idx_imp]
            df['Importe'] = df[c_name].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df['Importe'] = pd.to_numeric(df['Importe'], errors="coerce").fillna(0)
        else:
            df['Importe'] = 0

        if idx_ben is not None:
            df['Beneficiario'] = df[df.columns[idx_ben]].fillna("Desconocido").astype(str)
        else:
            df['Beneficiario'] = "Sin Datos"

    except Exception as e:
        print(f"Error en datos: {e}")
        df = pd.DataFrame({'Importe': [0], 'Beneficiario': ['Error de carga']})

    # Cálculos y conversión a tipos nativos de Python (Evita el TypeError de JSON)
    total_val = float(df['Importe'].sum())
    conteo_val = int(len(df))
    
    ranking_data = df.groupby('Beneficiario')['Importe'].sum().sort_values(ascending=False).head(5)
    # Convertimos índices y valores a listas estándar de Python
    labels_lista = [str(x) for x in ranking_data.index.tolist()]
    valores_lista = [float(x) for x in ranking_data.values.tolist()]

    # PDF de emergencia
    try:
        doc = SimpleDocTemplate(PDF_PATH, pagesize=A4)
        doc.build([Paragraph(f"Informe: {total_val:,.2f} EUR", getSampleStyleSheet()['Title'])])
    except:
        pass

    # HTML con el JSON ya convertido a tipos nativos
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
            <p>Sincronización: {fecha}</p>
        </header>
        <div class="boe-card">
            <div class="stat-group">
                <div class="stat-box"><strong>{total_val:,.2f} €</strong><br><small>Total Detectado</small></div>
                <div class="stat-box"><strong>{conteo_val}</strong><br><small>Registros</small></div>
            </div>
            <div style="padding:20px; height: 400px;"><canvas id="myChart"></canvas></div>
            <a href="{PDF_PATH}" class="btn-link">DESCARGAR INFORME PDF</a>
        </div>
    </div>
    <script>
        new Chart(document.getElementById('myChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(labels_lista)},
                datasets: [{{ 
                    label: 'Euros', 
                    data: {json.dumps(valores_lista)}, 
                    backgroundColor: '#5bc0be' 
                }}]
            }},
            options: {{ 
                indexAxis: 'y',
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }}
            }}
        }});
    </script>
</body>
</html>"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)

if __name__ == "__main__":
    procesar_observatorio()
