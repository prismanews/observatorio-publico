import pandas as pd
import requests, json, os, feedparser
from datetime import datetime

# --- CONFIGURACIÓN DE RUTAS ---
os.makedirs("datos", exist_ok=True)

def obtener_boe_simplificado():
    """FASE 2: Resúmenes automáticos del BOE vía RSS"""
    noticias = []
    try:
        # RSS de la sección de Ayudas y Subvenciones del BOE
        url_rss = "https://www.boe.es/rss/boe.php?s=3" 
        feed = feedparser.parse(url_rss)
        for entry in feed.entries[:5]: # Top 5 alertas legales
            noticias.append({
                "titulo": entry.title.split(".-")[-1].strip(),
                "link": entry.link,
                "fecha": datetime.now().strftime("%d/%m")
            })
    except:
        noticias = [{"titulo": "Servicio BOE temporalmente no disponible", "link": "#", "fecha": "-"}]
    return noticias

def obtener_subvenciones():
    """FASE 1: Datos de la BDNS"""
    try:
        url = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        with open("datos/data.csv", "wb") as f: f.write(r.content)
        
        df = pd.read_csv("datos/data.csv", sep=";", encoding="latin1", on_bad_lines='skip')
        df.columns = [str(c).lower().strip() for c in df.columns]
        
        # Localizador de columnas inteligente
        c_imp = next((c for c in df.columns if 'importe' in c), None)
        c_ben = next((c for c in df.columns if 'beneficiario' in c), None)
        
        df['Importe'] = df[c_imp].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df['Importe'] = pd.to_numeric(df['Importe'], errors="coerce").fillna(0)
        df['Beneficiario'] = df[c_ben].fillna("N/A").astype(str)
        
        return {
            "total": float(df['Importe'].sum()),
            "conteo": int(len(df)),
            "ranking": df.groupby('Beneficiario')['Importe'].sum().sort_values(ascending=False).head(5).to_dict()
        }
    except:
        return {"total": 0, "conteo": 0, "ranking": {}}

def generar_plataforma():
    data_sub = obtener_subvenciones()
    data_boe = obtener_boe_simplificado()
    fecha_act = datetime.now().strftime("%d/%m/%Y %H:%M")

    # --- HTML UNIFICADO (DASHBOARD) ---
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Observatorio Transparencia</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            :root {{ --bg: #f4f7f6; --dark: #0b132b; --accent: #5bc0be; --white: #ffffff; }}
            body {{ font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; color: var(--dark); }}
            .nav {{ background: var(--dark); color: white; padding: 1rem; text-align: center; font-weight: bold; letter-spacing: 1px; }}
            .container {{ max-width: 1100px; margin: 20px auto; padding: 0 20px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; }}
            .module {{ background: var(--white); border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
            .tag {{ background: var(--accent); color: var(--dark); padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; }}
            h3 {{ margin-top: 0; border-bottom: 2px solid var(--bg); padding-bottom: 10px; font-size: 1.1rem; }}
            .stat {{ font-size: 2rem; font-weight: 800; color: var(--dark); margin: 10px 0; }}
            .boe-link {{ display: block; padding: 10px; margin: 8px 0; background: var(--bg); border-radius: 6px; text-decoration: none; color: var(--dark); font-size: 0.9rem; transition: 0.2s; }}
            .boe-link:hover {{ border-left: 4px solid var(--accent); background: #ebf0ef; }}
            .footer {{ text-align: center; padding: 40px; font-size: 0.8rem; color: #888; }}
        </style>
    </head>
    <body>
        <div class="nav">🛰️ OBSERVATORIO DE TRANSPARENCIA PÚBLICA</div>
        <div class="container">
            <p><small>Sincronización global: {fecha_act}</small></p>
            
            <div class="grid">
                <div class="module">
                    <span class="tag">FASE 1: GASTO DIRECTO</span>
                    <h3>💰 Subvenciones Detectadas</h3>
                    <div class="stat">{data_sub['total']:,.2f} €</div>
                    <canvas id="chartSub"></canvas>
                </div>

                <div class="module">
                    <span class="tag">FASE 2: ALERTAS LEGALES</span>
                    <h3>📜 Últimas del BOE</h3>
                    {"".join([f'<a href="{n["link"]}" class="boe-link"><strong>{n["fecha"]}</strong> - {n["titulo"]}</a>' for n in data_boe])}
                </div>

                <div class="module" style="opacity: 0.6; background: #eee;">
                    <span class="tag" style="background:#ccc">FASE 4: FACT-CHECKING</span>
                    <h3>🗳️ Promesas vs Realidad</h3>
                    <p>Módulo en desarrollo. Requiere integración de NLP para análisis de programas electorales.</p>
                </div>
            </div>
        </div>
        <div class="footer">Datos obtenidos de BDNS y BOE.es - Automatizado con GitHub Actions</div>

        <script>
            new Chart(document.getElementById('chartSub'), {{
                type: 'doughnut',
                data: {{
                    labels: {json.dumps(list(data_sub['ranking'].keys()))},
                    datasets: [{{ 
                        data: {json.dumps(list(data_sub['ranking'].values()))}, 
                        backgroundColor: ['#0b132b', '#1c2541', '#3a506b', '#5bc0be', '#6fffe9'] 
                    }}]
                }},
                options: {{ plugins: {{ legend: {{ position: 'bottom', labels: {{ boxWidth: 12, font: {{ size: 10 }} }} }} }} }}
            }});
        </script>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f: f.write(html)

if __name__ == "__main__":
    generar_plataforma()
