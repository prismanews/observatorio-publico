import pandas as pd
import requests, json, os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# --- Configuración de Rutas ---
os.makedirs("datos", exist_ok=True)
PDF_PATH = "datos/informe.pdf"
CSV_LOCAL = "datos/data.csv"

def limpiar_columna_moneda(df, columna):
    """Limpia formatos europeos de moneda (1.000,00 -> 1000.00)"""
    df[columna] = df[columna].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    return pd.to_numeric(df[columna], errors="coerce").fillna(0)

def procesar_observatorio():
    SUBV_URL = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(SUBV_URL, headers=headers, timeout=30)
        with open(CSV_LOCAL, "wb") as f:
            f.write(r.content)
        
        # Leemos con flexibilidad de encoding
        df = pd.read_csv(CSV_LOCAL, sep=";", encoding="latin1", on_bad_lines='skip', low_memory=False)
        
        # --- BUSCADOR INTELIGENTE DE COLUMNAS (Evita el KeyError) ---
        col_map = {
            'importe': next((c for c in df.columns if 'importe' in c.lower()), None),
            'beneficiario': next((c for c in df.columns if 'beneficiario' in c.lower() or 'nombre' in c.lower()), None),
            'provincia': next((c for c in df.columns if 'provincia' in c.lower()), None)
        }

        # Validamos que al menos tenemos el importe
        if col_map['importe']:
            df['Importe'] = limpiar_columna_moneda(df, col_map['importe'])
        else:
            df['Importe'] = 0

        # Renombramos para normalizar el resto del script
        df = df.rename(columns={col_map['beneficiario']: 'Beneficiario', col_map['provincia']: 'Provincia'})

    except Exception as e:
        print(f"⚠️ Error en descarga/lectura: {e}")
        df = pd.DataFrame(columns=['Importe', 'Beneficiario', 'Provincia'])

    # 2. CÁLCULOS
    total = df["Importe"].sum()
    conteo = len(df)
    ranking = df.groupby("Beneficiario")["Importe"].sum().sort_values(ascending=False).head(5) if not df.empty else pd.Series()

    # ALERTAS ANTICORRUPCIÓN
    alertas = []
    if not df.empty and total > 0:
        umbral = df["Importe"].mean() + (df["Importe"].std() * 3)
        if df["Importe"].max() > umbral:
            alertas.append("Adjudicación individual sospechosa (fuera de rango estadístico).")
        if (df["Importe"] == 0).sum() / len(df) > 0.5:
            alertas.append("Alta opacidad: +50% de registros sin importe.")

    # 3. GENERAR PDF
    def generar_pdf():
        doc = SimpleDocTemplate(PDF_PATH, pagesize=A4)
        styles = getSampleStyleSheet()
        story = [
            Paragraph("Informe de Control de Transparencia", styles['Title']),
            Spacer(1, 12),
            Paragraph(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']),
            Paragraph(f"Total Auditado: {total:,.2f} €", styles['Heading2']),
            Spacer(1, 10)
        ]
        if alertas:
            story.append(Paragraph("Alertas Críticas:", styles['Heading3']))
            for al in alertas:
                story.append(Paragraph(f"• {al}", styles['Normal']))
        doc.build(story)

    generar_pdf()

    # 4. GENERAR HTML (Estructura para el CSS profesional)
    fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Observatorio Transparencia</title>
        <link rel="stylesheet" href="estilo.css">
        <link rel="manifest" href="manifest.json">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <div class="container">
            <header class="boe-header" style="border-radius: 12px 12px 0 0;">
                <h2>🚀 OBSERVATORIO DE TRANSPARENCIA</h2>
                <p>Última actualización: {fecha_str}</p>
            </header>

            <div class="boe-card" style="margin-top: -10px;">
                <div class="boe-body">
                    <div class="stat-group">
                        <div class="stat-box">
                            <span class="stat-label">Fondos Auditados</span>
                            <span class="stat-value money">{total:,.2f}</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-label">Expedientes</span>
                            <span class="stat-value">{conteo}</span>
                        </div>
                    </div>

                    <div class="grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div class="card-inner">
                            <h3>📊 Top Beneficiarios</h3>
                            <canvas id="chartRanking"></canvas>
                        </div>
                        <div class="card-inner">
                            <h3>⚠️ Alertas de Riesgo</h3>
                            { "".join([f'<div class="error-msg">{a}</div>' for a in alertas]) if alertas else '<p style="color:green">No se detectan anomalías.</p>' }
                        </div>
                    </div>

                    <div class="actions">
                        <a href="{PDF_PATH}" class="btn-link">Descargar Informe Oficial (PDF)</a>
                    </div>
                </div>
            </div>
        </div>

        <script>
            const ctx = document.getElementById('chartRanking');
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: {json.dumps(list(ranking.index))},
                    datasets: [{{
                        data: {json.dumps(list(ranking.values))},
                        backgroundColor: ['#0b132b', '#1c2541', '#3a506b', '#5bc0be', '#6fffe9']
                    }}]
                }},
                options: {{ plugins: {{ legend: {{ position: 'bottom' }} }} }}
            }});
        </script>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    procesar_observatorio()
