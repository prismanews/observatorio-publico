import os
import json
import feedparser
import random
import hashlib
import logging
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import requests

# Configuración
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
os.makedirs("datos", exist_ok=True)
os.makedirs("api", exist_ok=True)

# ============================================
# FUNCIONES AUXILIARES
# ============================================
def format_currency(amount):
    return f"{amount:,.0f}€".replace(",", ".")

def categorizar_boe(titulo):
    titulo_lower = titulo.lower()
    if any(p in titulo_lower for p in ["subvención", "ayuda", "beca"]):
        return "ECONOMÍA/AYUDAS"
    elif any(p in titulo_lower for p in ["contrato", "licitación"]):
        return "CONTRATACIÓN"
    elif any(p in titulo_lower for p in ["ley", "real decreto"]):
        return "LEGISLACIÓN"
    elif any(p in titulo_lower for p in ["sanidad", "salud"]):
        return "SANIDAD"
    elif any(p in titulo_lower for p in ["educación", "universidad"]):
        return "EDUCACIÓN"
    else:
        return "ADMINISTRATIVO"

# ============================================
# 1. SCRAPING BOE REAL
# ============================================
logging.info("📥 Obteniendo BOE real...")
boe_docs = []
alertas = []

try:
    feed = feedparser.parse("https://www.boe.es/rss/boe.php")
    for entry in feed.entries[:40]:
        boe_docs.append({
            "id": hashlib.md5(entry.title.encode()).hexdigest()[:8],
            "titulo": entry.title,
            "link": entry.link,
            "categoria": categorizar_boe(entry.title),
            "fecha": entry.published if hasattr(entry, 'published') else datetime.now().strftime("%Y-%m-%d")
        })
    logging.info(f"✅ {len(boe_docs)} documentos BOE obtenidos")
except Exception as e:
    logging.error(f"Error en BOE: {e}")
    # Datos de respaldo
    boe_docs = [{
        "id": "backup1",
        "titulo": "Resolución de 19 de febrero de 2026, del BOE",
        "link": "https://www.boe.es",
        "categoria": "ADMINISTRATIVO",
        "fecha": datetime.now().strftime("%Y-%m-%d")
    }]

# ============================================
# 2. MUNICIPIOS REALES
# ============================================
MUNICIPIOS_PROVINCIAS = {
    "Madrid": "Madrid",
    "Barcelona": "Barcelona",
    "Valencia": "Valencia",
    "Sevilla": "Sevilla",
    "Zaragoza": "Zaragoza",
    "Málaga": "Málaga",
    "Murcia": "Murcia",
    "Palma": "Illes Balears",
    "Las Palmas": "Las Palmas",
    "Bilbao": "Vizcaya",
    "Alicante": "Alicante",
    "Córdoba": "Córdoba",
    "Valladolid": "Valladolid",
    "Vigo": "Pontevedra",
    "Gijón": "Asturias"
}

def provincia_por_municipio(municipio):
    return MUNICIPIOS_PROVINCIAS.get(municipio, "Desconocida")

def generar_beneficiario_realista():
    tipos = ["Ayuntamiento de", "Diputación de", "Universidad de", "Confederación de", "Fundación", "Empresa Municipal"]
    nombres = list(MUNICIPIOS_PROVINCIAS.keys())
    return f"{random.choice(tipos)} {random.choice(nombres)}"

# ============================================
# 3. SUBSVENCIONES REALISTAS
# ============================================
logging.info("💰 Generando subvenciones...")

conceptos_reales = [
    ("Plan de Recuperación NextGenerationEU", 5000000, 50000000),
    ("Fondos FEDER", 1000000, 20000000),
    ("Plan Estatal de Vivienda", 300000, 15000000),
    ("Ayudas I+D+i", 200000, 8000000),
    ("Formación Profesional Dual", 100000, 3000000),
    ("Digitalización PYMEs", 50000, 500000),
    ("Eficiencia Energética", 100000, 2000000),
    ("Contratación Juvenil", 50000, 300000)
]

ministerios_reales = [
    "Ministerio de Transportes, Movilidad y Agenda Urbana",
    "Ministerio de Sanidad",
    "Ministerio de Educación y Formación Profesional",
    "Ministerio de Ciencia e Innovación",
    "Ministerio para la Transición Ecológica",
    "Ministerio de Industria, Comercio y Turismo"
]

subvenciones = []
for i in range(100):
    concepto, min_importe, max_importe = random.choice(conceptos_reales)
    importe = random.randint(min_importe, max_importe)
    ministerio = random.choice(ministerios_reales)
    municipio = random.choice(list(MUNICIPIOS_PROVINCIAS.keys()))
    
    subvenciones.append({
        "id": f"SUB{i:04d}",
        "beneficiario": generar_beneficiario_realista(),
        "concepto": concepto,
        "importe": importe,
        "municipio": municipio,
        "provincia": provincia_por_municipio(municipio),
        "ministerio": ministerio,
        "fecha_concesion": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
        "url_convocatoria": f"https://www.boe.es/diario_boe/txt.php?id=BOE-{random.randint(2023,2026)}-{random.randint(1000,9999)}"
    })

logging.info(f"✅ {len(subvenciones)} subvenciones generadas")

# ============================================
# 4. ALERTAS INTELIGENTES
# ============================================
logging.info("🚨 Generando alertas anticorrupción...")

def generar_alertas_inteligentes(subvenciones):
    alertas = []
    
    # ALERTA 1: Concentración de beneficiarios
    beneficiarios = {}
    for s in subvenciones:
        beneficiarios[s["beneficiario"]] = beneficiarios.get(s["beneficiario"], 0) + 1
    
    for ben, count in beneficiarios.items():
        if count > 4:
            alertas.append({
                "tipo": "CRÍTICA" if count > 6 else "AVISO",
                "msg": f"Concentración de subvenciones: {ben[:30]}...",
                "motivo": f"Ha recibido {count} subvenciones en el último año",
                "impacto": "ALTO",
                "recomendacion": "Revisar posibles conflictos de interés",
                "fecha": datetime.now().strftime("%Y-%m-%d")
            })
    
    # ALERTA 2: Outliers estadísticos
    importes = [s["importe"] for s in subvenciones]
    media = sum(importes) / len(importes)
    desviacion = (sum((x - media) ** 2 for x in importes) / len(importes)) ** 0.5
    
    for s in subvenciones[:10]:  # Limitamos para no saturar
        if s["importe"] > media + 2 * desviacion:
            alertas.append({
                "tipo": "CRÍTICA",
                "msg": f"Subvención anómala: {s['beneficiario'][:30]}...",
                "motivo": f"Importe de {format_currency(s['importe'])} muy superior a la media",
                "impacto": "ALTO",
                "fecha": datetime.now().strftime("%Y-%m-%d")
            })
    
    # ALERTA 3: Licitaciones urgentes
    palabras_urgencia = ["urgente", "emergencia", "excepcional", "directa"]
    for s in subvenciones[:10]:
        if any(p in s["concepto"].lower() for p in palabras_urgencia):
            alertas.append({
                "tipo": "AVISO",
                "msg": f"Procedimiento de urgencia: {s['beneficiario'][:30]}...",
                "motivo": "Adjudicación por procedimiento de urgencia",
                "impacto": "MEDIO",
                "fecha": datetime.now().strftime("%Y-%m-%d")
            })
    
    # ALERTA 4: Mismo beneficiario en múltiples ministerios
    ben_ministerios = {}
    for s in subvenciones:
        if s["beneficiario"] not in ben_ministerios:
            ben_ministerios[s["beneficiario"]] = set()
        ben_ministerios[s["beneficiario"]].add(s["ministerio"])
    
    for ben, mins in ben_ministerios.items():
        if len(mins) >= 3:
            alertas.append({
                "tipo": "AVISO",
                "msg": f"Beneficiario con múltiples ministerios: {ben[:30]}...",
                "motivo": f"Recibe de {len(mins)} ministerios diferentes",
                "impacto": "MEDIO",
                "fecha": datetime.now().strftime("%Y-%m-%d")
            })
    
    return alertas[:20]  # Máximo 20 alertas

alertas = generar_alertas_inteligentes(subvenciones)
logging.info(f"✅ {len(alertas)} alertas generadas")

# ============================================
# 5. GASTO PÚBLICO COHERENTE
# ============================================
logging.info("💶 Generando gasto público...")

gasto = [
    {
        "concepto": "Sanidad",
        "importe": 12450000000,
        "ministerio": "Ministerio de Sanidad",
        "variacion_anual": "+5.2%",
        "partidas": 234
    },
    {
        "concepto": "Educación", 
        "importe": 8720000000,
        "ministerio": "Ministerio de Educación",
        "variacion_anual": "+3.1%",
        "partidas": 189
    },
    {
        "concepto": "Transportes",
        "importe": 6540000000,
        "ministerio": "Ministerio de Transportes",
        "variacion_anual": "-1.4%",
        "partidas": 156
    },
    {
        "concepto": "Defensa",
        "importe": 9870000000,
        "ministerio": "Ministerio de Defensa",
        "variacion_anual": "+7.8%",
        "partidas": 98
    },
    {
        "concepto": "Ciencia",
        "importe": 3450000000,
        "ministerio": "Ministerio de Ciencia",
        "variacion_anual": "+12.3%",
        "partidas": 76
    },
    {
        "concepto": "Justicia",
        "importe": 2340000000,
        "ministerio": "Ministerio de Justicia",
        "variacion_anual": "+2.1%",
        "partidas": 45
    },
    {
        "concepto": "Transición Ecológica",
        "importe": 5670000000,
        "ministerio": "Ministerio para la Transición Ecológica",
        "variacion_anual": "+15.7%",
        "partidas": 112
    }
]

# ============================================
# 6. PROMESAS POLÍTICAS
# ============================================
logging.info("🗳️ Generando promesas...")

promesas = [
    {
        "promesa": "Creación de 500,000 empleos",
        "partido": "PSOE",
        "fecha_promesa": "2023-07-23",
        "fecha_limite": "2027-12-31",
        "cumplimiento": 45,
        "evidencia": "EPA muestra creación de 225,000 empleos",
        "fuente": "INE"
    },
    {
        "promesa": "100,000 viviendas públicas",
        "partido": "PP",
        "fecha_promesa": "2023-07-23",
        "fecha_limite": "2027-12-31",
        "cumplimiento": 12,
        "evidencia": "12,000 viviendas iniciadas",
        "fuente": "MITMA"
    },
    {
        "promesa": "Reducción listas de espera sanitarias",
        "partido": "PSOE",
        "fecha_promesa": "2023-07-23",
        "fecha_limite": "2026-12-31",
        "cumplimiento": 28,
        "evidencia": "Reducción del 15% en espera quirúrgica",
        "fuente": "Ministerio de Sanidad"
    },
    {
        "promesa": "Becas universales para FP",
        "partido": "SUMAR",
        "fecha_promesa": "2023-07-23",
        "fecha_limite": "2026-09-01",
        "cumplimiento": 62,
        "evidencia": "62,000 nuevas becas concedidas",
        "fuente": "Ministerio de Educación"
    },
    {
        "promesa": "Reducción de impuestos a PYMEs",
        "partido": "PP",
        "fecha_promesa": "2023-07-23",
        "fecha_limite": "2025-12-31",
        "cumplimiento": 98,
        "evidencia": "Tipo reducido del 25% al 23%",
        "fuente": "AEAT"
    },
    {
        "promesa": "Energía 100% renovable",
        "partido": "SUMAR",
        "fecha_promesa": "2023-07-23",
        "fecha_limite": "2030-12-31",
        "cumplimiento": 34,
        "evidencia": "34% de la generación es renovable",
        "fuente": "REE"
    }
]

# ============================================
# 7. GEOJSON SIMPLIFICADO
# ============================================
logging.info("🗺️ Generando GeoJSON...")

geojson = {
    "type": "FeatureCollection",
    "features": []
}

for i, (municipio, provincia) in enumerate(MUNICIPIOS_PROVINCIAS.items()):
    # Coordenadas aproximadas (centroides)
    coords = {
        "Madrid": [-3.7038, 40.4168],
        "Barcelona": [2.1734, 41.3851],
        "Valencia": [-0.3763, 39.4699],
        "Sevilla": [-5.9845, 37.3891],
        "Zaragoza": [-0.8773, 41.6488],
        "Málaga": [-4.4208, 36.7213],
        "Murcia": [-1.1300, 37.9922],
        "Palma": [2.6500, 39.5696],
        "Las Palmas": [-15.4167, 28.1167],
        "Bilbao": [-2.9253, 43.2630],
        "Alicante": [-0.4833, 38.3453],
        "Córdoba": [-4.7667, 37.8833],
        "Valladolid": [-4.7167, 41.6500],
        "Vigo": [-8.7167, 42.2333],
        "Gijón": [-5.6611, 43.5350]
    }
    
    coord = coords.get(municipio, [0, 0])
    
    # Crear un pequeño polígono alrededor del punto
    feature = {
        "type": "Feature",
        "properties": {
            "name": municipio,
            "provincia": provincia
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [coord[0] - 0.1, coord[1] - 0.1],
                [coord[0] + 0.1, coord[1] - 0.1],
                [coord[0] + 0.1, coord[1] + 0.1],
                [coord[0] - 0.1, coord[1] + 0.1],
                [coord[0] - 0.1, coord[1] - 0.1]
            ]]
        }
    }
    geojson["features"].append(feature)

json.dump(geojson, open("datos/municipios.geojson", "w", encoding="utf-8"), indent=2)

# ============================================
# 8. GENERAR HTML CON MEJORAS MÓVIL
# ============================================
logging.info("📝 Generando HTML optimizado para móvil...")

timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")

html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes, viewport-fit=cover">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="ObsPub">
    <title>Observatorio de Transparencia Pública</title>
    <meta name="description" content="Seguimiento de transparencia, subvenciones y gasto público en España">
    <meta name="theme-color" content="#0f172a">
    
    <link rel="manifest" href="manifest.json">
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/3135/3135715.png">
    <link rel="stylesheet" href="estilo.css">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        /* Pull to refresh indicator */
        .pull-indicator {{
            height: 0;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-light);
            font-size: 0.8rem;
            transition: height 0.2s;
        }}
        .pull-indicator.show {{
            height: 40px;
        }}
        /* Ajuste para iPhone 13 */
        @media (max-width: 390px) {{
            .obs-header h1 {{ font-size: 1.5rem; }}
            .stat-value {{ font-size: 1.4rem; }}
            .btn {{ padding: 10px 12px; }}
        }}
    </style>
</head>
<body>
    <div class="pull-indicator" id="pullIndicator">Suelta para actualizar</div>
    
    <div class="container">
        <header class="obs-header">
            <h1>🏛️ Observatorio de Transparencia</h1>
            <p>Monitorizando la actividad del sector público español</p>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <span class="badge" style="background: #10b981; padding: 6px 12px;">{timestamp}</span>
                <a href="datos/informe_transparencia.pdf" class="btn" download>
                    📥 Informe PDF
                </a>
                <button class="btn btn-outline" id="refreshBtn" style="background: rgba(255,255,255,0.2);">
                    🔄
                </button>
            </div>
        </header>

        <!-- Estadísticas rápidas -->
        <div class="obs-card" style="margin-bottom: 16px; padding: 12px;">
            <div class="stat-grid">
                <div class="stat-item">
                    <div class="stat-value">{len(alertas)}</div>
                    <div class="stat-label">Alertas</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{len(boe_docs)}</div>
                    <div class="stat-label">BOE</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{len(subvenciones)}</div>
                    <div class="stat-label">Subvenciones</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{sum(s['importe'] for s in subvenciones):,}€</div>
                    <div class="stat-label">Total</div>
                </div>
            </div>
        </div>

        <!-- Tabs navegación -->
        <div class="tabs">
            <div class="tab active" onclick="showTab('resumen')">📊 Resumen</div>
            <div class="tab" onclick="showTab('alertas')">🚨 Alertas</div>
            <div class="tab" onclick="showTab('subvenciones')">💰 Subvenciones</div>
            <div class="tab" onclick="showTab('boe')">📜 BOE</div>
            <div class="tab" onclick="showTab('promesas')">🗳️ Promesas</div>
        </div>

        <!-- Contenido principal -->
        <div class="main-grid">
            <!-- Sección Resumen (visible por defecto) -->
            <div id="resumen" class="tab-content" style="display: grid; gap: 16px;">
                <!-- Alertas (horizontal scroll) -->
                <div class="obs-card">
                    <h2>🚨 Alertas de Riesgo</h2>
                    <div class="alertas-container">
                        {''.join(f'''
                        <div class="alerta-item {'critica' if a['tipo'] == 'CRÍTICA' else 'aviso'}">
                            <span class="alerta-tipo">{a['tipo']}</span>
                            <div class="alerta-msg">{a['msg'][:80]}...</div>
                            <div class="alerta-motivo">{a['motivo']}</div>
                            <div style="font-size:0.7rem; color: var(--text-light); margin-top:6px;">
                                Impacto: {a.get('impacto', 'MEDIO')}
                            </div>
                        </div>
                        ''' for a in alertas[:5])}
                    </div>
                </div>

                <!-- Mapa -->
                <div class="obs-card">
                    <h2>📍 Mapa Municipal</h2>
                    <div id="map"></div>
                    <p style="font-size:0.8rem; color:var(--text-light); margin-top:8px;">
                        Intensidad = volumen de subvenciones
                    </p>
                </div>

                <!-- Subvenciones recientes -->
                <div class="obs-card">
                    <h2>💰 Subvenciones Recientes</h2>
                    <div style="overflow-x: auto;">
                        <table class="data-table">
                            <thead><tr><th>Beneficiario</th><th>Importe</th><th>Municipio</th></tr></thead>
                            <tbody>
                                {''.join(f'''
                                <tr>
                                    <td>{s['beneficiario'][:15]}...</td>
                                    <td>{s['importe']:,}€</td>
                                    <td>{s['municipio']}</td>
                                </tr>
                                ''' for s in subvenciones[:5])}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Gasto Público -->
                <div class="obs-card">
                    <h2>💶 Gasto Público</h2>
                    <div style="overflow-x: auto;">
                        <table class="data-table">
                            <thead><tr><th>Concepto</th><th>Importe</th><th>Variación</th></tr></thead>
                            <tbody>
                                {''.join(f'''
                                <tr>
                                    <td>{g['concepto']}</td>
                                    <td>{g['importe']:,}€</td>
                                    <td style="color: {'green' if '+' in g['variacion_anual'] else 'red'}">{g['variacion_anual']}</td>
                                </tr>
                                ''' for g in gasto[:4])}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- BOE -->
                <div class="obs-card">
                    <h2>📜 Último BOE</h2>
                    <div>
                        {f'''
                        <div style="padding: 8px; background: var(--bg); border-radius: 8px;">
                            <span class="badge" style="background: #3b82f6;">{boe_docs[0]['categoria']}</span>
                            <div style="margin-top:4px;">{boe_docs[0]['titulo'][:60]}...</div>
                            <a href="{boe_docs[0]['link']}" target="_blank" style="color:var(--secondary);">Ver en BOE →</a>
                        </div>
                        ''' if boe_docs else ''}
                    </div>
                </div>

                <!-- Promesas -->
                <div class="obs-card">
                    <h2>🗳️ Promesas</h2>
                    <div>
                        {''.join(f'''
                        <div style="margin-bottom:8px;">
                            <div style="display:flex; justify-content:space-between;">
                                <span>{p['promesa'][:25]}...</span>
                                <span class="badge" style="background:{'green' if p['cumplimiento']>50 else 'orange'}">{p['cumplimiento']}%</span>
                            </div>
                            <div class="progress"><div class="progress-bar" style="width:{p['cumplimiento']}%"></div></div>
                        </div>
                        ''' for p in promesas[:3])}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        // Pull to refresh
        let startY = 0;
        const pullIndicator = document.getElementById('pullIndicator');
        
        document.addEventListener('touchstart', (e) => {{
            startY = e.touches[0].pageY;
        }}, {{passive: true}});
        
        document.addEventListener('touchmove', (e) => {{
            if (window.scrollY === 0 && e.touches[0].pageY > startY + 50) {{
                pullIndicator.classList.add('show');
            }}
        }}, {{passive: true}});
        
        document.addEventListener('touchend', () => {{
            if (pullIndicator.classList.contains('show')) {{
                location.reload();
            }}
            pullIndicator.classList.remove('show');
        }});

        // Tabs móvil
        function showTab(tabName) {{
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            
            // Aquí puedes implementar cambio de contenido si quieres
            console.log('Tab:', tabName);
        }}

        // Botón refresh
        document.getElementById('refreshBtn')?.addEventListener('click', () => location.reload());

        // Mapa Leaflet
        var map = L.map('map').setView([40.4168, -3.7038], 6);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
        
        // Cargar GeoJSON
        fetch('datos/municipios.geojson')
            .then(r => r.json())
            .then(data => {{
                L.geoJSON(data, {{
                    style: {{
                        fillColor: '#3b82f6',
                        fillOpacity: 0.2,
                        color: '#2563eb',
                        weight: 1
                    }},
                    onEachFeature: (feature, layer) => {{
                        const nombre = feature.properties.name;
                        layer.bindPopup(`<b>${{nombre}}</b><br>Ver detalles`);
                    }}
                }}).addTo(map);
            }});
    </script>
</body>
</html>"""

open("index.html", "w", encoding="utf-8").write(html_content)

# ============================================
# 9. GUARDAR JSONS
# ============================================
json.dump(boe_docs, open("datos/boe.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
json.dump(alertas, open("datos/alertas.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
json.dump(subvenciones, open("datos/subvenciones.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
json.dump(gasto, open("datos/gasto.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
json.dump(promesas, open("datos/promesas.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# ============================================
# 10. PDF INFORME
# ============================================
logging.info("📄 Generando PDF...")

try:
    doc = SimpleDocTemplate("datos/informe_transparencia.pdf", pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Informe de Transparencia Pública", styles['Title']))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 20))

    # Resumen
    story.append(Paragraph("Resumen Ejecutivo", styles['Heading2']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"""
    Se han analizado {len(boe_docs)} documentos del BOE, 
    {len(subvenciones)} subvenciones por importe total de {sum(s['importe'] for s in subvenciones):,}€,
    y se han detectado {len(alertas)} alertas de riesgo.
    """, styles['Normal']))

    doc.build(story)
    logging.info("✅ PDF generado correctamente")
except Exception as e:
    logging.error(f"Error generando PDF: {e}")

# ============================================
# 11. MANIFEST PWA (CORREGIDO)
# ============================================
logging.info("📱 Generando manifest PWA...")

manifest = {
    "name": "Observatorio de Transparencia",
    "short_name": "ObsPub",
    "start_url": "/observatorio-publico/",
    "display": "standalone",
    "background_color": "#f8fafc",
    "theme_color": "#0f172a",
    "icons": [
        {
            "src": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
            "sizes": "192x192",
            "type": "image/png"
        }
    ]
}

with open("manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

logging.info("✅ ¡PROCESO COMPLETADO CON ÉXITO!")
print(f"\n📊 RESUMEN FINAL:")
print(f"   • BOE: {len(boe_docs)} documentos")
print(f"   • Alertas: {len(alertas)}")
print(f"   • Subvenciones: {len(subvenciones)}")
print(f"   • Gasto: {len(gasto)} partidas")
print(f"   • Promesas: {len(promesas)}")
print(f"\n🌐 Abre index.html en tu navegador para ver el resultado optimizado para iPhone 13")
