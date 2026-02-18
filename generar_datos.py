import pandas as pd
import requests, json, os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# --- Configuración de Rutas ---
os.makedirs("datos", exist_ok=True)
PDF_PATH = "datos/informe.pdf"
CSV_LOCAL = "datos/data.csv"

def limpiar_moneda(df, col):
    df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    return pd.to_numeric(df[col], errors="coerce").fillna(0)

def procesar_observatorio():
    URL = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(URL, headers=headers, timeout=30)
        with open(CSV_LOCAL, "wb") as f:
            f.write(r.content)
        
        # Probamos con el encoding típico de la administración española
        df = pd.read_csv(CSV_LOCAL, sep=";", encoding="latin1", on_bad_lines='skip', low_memory=False)
        
        # --- DETECTIVE DE COLUMNAS ---
        # Listamos las columnas reales para depurar si falla
        cols = df.columns.tolist()
        print(f"Columnas detectadas: {cols}")

        # Buscamos la mejor coincidencia para cada campo crítico
        c_imp = next((c for c in cols if 'importe' in c.lower()), None)
        c_ben = next((c for c in cols if 'beneficiario' in c.lower() or 'nombre' in c.lower() or 'persona' in c.lower()), None)
        c_pro = next((c for c in cols if 'provincia' in c.lower() or 'comunidad' in c.lower()), None)

        # Normalizamos el DataFrame
        new_df = pd.DataFrame()
        new_df['Importe'] = limpiar_moneda(df, c_imp) if c_imp else [0]*len(df)
        new_df['Beneficiario'] = df[c_ben].fillna("Desconocido") if c_ben else ["Sin Datos"]*len(df)
        new_df['Provincia'] = df[c_pro].fillna("N/A") if c_pro else ["N/A"]*len(df)
        
        df = new_df

    except Exception as e:
        print(f"Error crítico: {e}")
        df = pd.DataFrame(columns=['Importe', 'Beneficiario', 'Provincia'])

    # 2. CÁLCULOS SEGUROS
    total = df["Importe"].sum() if not df.empty else 0
    conteo = len(df)
    ranking = df.groupby("Beneficiario")["Importe"].sum().sort_values(ascending=False).head(5) if not df.empty else pd.Series(dtype=float)

    alertas = []
    if not df.empty and total > 0:
        std = df["Importe"].std()
        mean = df["Importe"].mean()
        if not pd.isna(std) and df["Importe"].max() > (mean + (std * 3)):
            alertas.append("Detección de adjudicación individual fuera de rango estadístico.")

    # 3. GENERAR PDF E HTML (Simplificado para evitar errores de renderizado)
    fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Generar PDF
    doc = SimpleDocTemplate(PDF_PATH, pagesize=A4)
    styles = getSampleStyleSheet()
    doc.build([Paragraph("Informe Transparencia", styles['Title']), Paragraph(f"Total: {total:,.2f} €", styles['Normal'])])

    # Generar HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <link rel="stylesheet" href="estilo.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <div class="container">
            <header class="boe-header">
                <h2>OBSERVATORIO PRO</h2>
                <p>Sincronización: {fecha_str}</p>
            </header>
            <div class="boe-card">
                <div class="stat-group">
                    <div class="stat-box"><span class="stat-label">Total</span><span class="stat-value">{total:,.2f} €</span></div>
                    <div class="stat-box"><span class="stat-label">Registros</span><span class="stat-value">{conteo}</span></div>
                </div>
                <div style="padding:20px">
                    <h3>Top Beneficiarios</h3>
                    <canvas id="chart"></canvas>
                </div>
                {"".join([f'<div class="error-msg">{a}</div>' for a in alertas])}
                <a href="{PDF_PATH}" class="btn-link">Descargar PDF</a>
            </div>
        </div>
        <script>
            new Chart(document.getElementById('chart'), {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(list(ranking.index))},
                    datasets: [{{ label: 'Euros', data: {json.dumps(list(ranking.values))}, backgroundColor: '#5bc0be' }}]
                }},
                options: {{ indexAxis: 'y' }}
            }});
        </script>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    procesar_observatorio()
