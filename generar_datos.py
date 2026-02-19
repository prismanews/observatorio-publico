import os
import json
import requests
import feedparser
import random
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import hashlib

# Configuración
os.makedirs("datos", exist_ok=True)
os.makedirs("api", exist_ok=True)

# Configuración de vigilancia
SECTORES_CRITICOS = [
    "defensa", "armamento", "consultoría", "obras", 
    "infraestructura", "sanidad", "digitalización", "educación",
    "seguridad", "justicia", "transporte", "energía"
]

ALERTAS_PATRON = [
    "directa", "excepcional", "urgencia", "millones", 
    "emergencia", "crítico", "alerta", "investigación",
    "irregularidad", "sobrecoste", "fraude", "corrupción"
]

# Datos de ejemplo para municipios españoles
MUNICIPIOS = [
    "Madrid", "Barcelona", "Valencia", "Sevilla", "Zaragoza",
    "Málaga", "Murcia", "Palma", "Las Palmas", "Bilbao",
    "Alicante", "Córdoba", "Valladolid", "Vigo", "Gijón"
]

MINISTERIOS = [
    "Ministerio de Hacienda",
    "Ministerio de Sanidad",
    "Ministerio de Transportes",
    "Ministerio de Educación",
    "Ministerio de Defensa",
    "Ministerio del Interior"
]

PARTIDOS = ["PSOE", "PP", "VOX", "SUMAR", "ERC", "JUNTS"]

# Funciones auxiliares
def generar_id(texto):
    return hashlib.md5(texto.encode()).hexdigest()[:8]

def formatear_fecha(dias_atras=0):
    fecha = datetime.now() - timedelta(days=dias_atras)
    return fecha.strftime("%d/%m/%Y")

def generar_importe():
    return random.randint(10000, 5000000)

# 1. Scraping BOE
print("📥 Obteniendo datos del BOE...")
boe_docs = []
alertas = []

try:
    feed = feedparser.parse("https://www.boe.es/rss/boe.php")
    entries = feed.entries[:50]  # Más entradas
    
    for entry in entries:
        texto = entry.title.lower()
        sector_detectado = next((s for s in SECTORES_CRITICOS if s in texto), None)
        
        # Categorización avanzada
        if any(w in texto for w in ["subvención", "ayuda", "beca", "subsidio"]):
            cat, color = "ECONOMÍA/AYUDAS", "#10b981"
        elif any(w in texto for w in ["contrato", "licitación", "adjudicación"]):
            cat, color = "CONTRATACIÓN", "#3b82f6"
        elif any(w in texto for w in ["ley", "real decreto", "normativa"]):
            cat, color = "LEGISLACIÓN", "#8b5cf6"
        elif sector_detectado:
            cat, color = f"SECTOR: {sector_detectado.upper()}", "#f59e0b"
        else:
            cat, color = "ADMINISTRATIVO", "#64748b"
        
        # Detección de alertas
        riesgo = any(p in texto for p in ALERTAS_PATRON)
        if riesgo or sector_detectado:
            alertas.append({
                "id": generar_id(entry.title),
                "tipo": "CRÍTICA" if riesgo else "AVISO",
                "msg": entry.title[:150] + "...",
                "motivo": "Sector estratégico" if sector_detectado else "Patrón de riesgo detectado",
                "link": entry.link,
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "impacto": random.choice(["ALTO", "MEDIO", "BAJO"])
            })
        
        boe_docs.append({
            "id": generar_id(entry.title),
            "titulo": entry.title,
            "link": entry.link,
            "categoria": cat,
            "color": color,
            "fecha": datetime.now().strftime("%Y-%m-%d")
        })
except Exception as e:
    print(f"⚠️ Error en scraping BOE: {e}")

# 2. Generar subvenciones simuladas
print("💰 Generando datos de subvenciones...")
subvenciones = []
for i in range(100):
    municipio = random.choice(MUNICIPIOS)
    importe = generar_importe()
    subvenciones.append({
        "id": f"SUB{i:04d}",
        "beneficiario": f"Empresa {random.choice(['Tecnológica', 'Constructora', 'Servicios', 'Industrial'])} {i}",
        "concepto": random.choice([
            "Digitalización PYME", "Eficiencia energética", "Formación profesional",
            "I+D+i", "Internacionalización", "Contratación juvenil"
        ]),
        "importe": importe,
        "municipio": municipio,
        "provincia": municipio if municipio in ["Madrid", "Barcelona"] else random.choice(["Madrid", "Barcelona", "Valencia", "Sevilla"]),
        "fecha": formatear_fecha(random.randint(0, 365)),
        "ministerio": random.choice(MINISTERIOS)
    })

# 3. Generar gasto público
print("💶 Generando datos de gasto público...")
gasto = []
for i in range(50):
    gasto.append({
        "id": f"GAS{i:04d}",
        "concepto": random.choice([
            "Infraestructuras", "Sanidad", "Educación", "Defensa", 
            "Pensiones", "Desempleo", "I+D", "Cultura"
        ]),
        "importe": random.randint(1000000, 100000000),
        "ministerio": random.choice(MINISTERIOS),
        "trimestre": random.randint(1, 4),
        "ano": 2024,
        "ejecucion": random.randint(60, 100)
    })

# 4. Generar promesas políticas
print("🗳️ Generando seguimiento de promesas...")
promesas = []
promesas_ejemplo = [
    "Creación de 500,000 empleos",
    "Construcción de viviendas públicas",
    "Mejora de la sanidad pública",
    "Reducción de impuestos",
    "Inversión en energías renovables",
    "Aumento de becas educativas",
    "Modernización de infraestructuras",
    "Lucha contra la corrupción"
]

for promesa in promesas_ejemplo:
    cumplimiento = random.randint(0, 100)
    promesas.append({
        "id": generar_id(promesa),
        "promesa": promesa,
        "partido": random.choice(PARTIDOS),
        "fecha": formatear_fecha(random.randint(0, 1000)),
        "cumplimiento": cumplimiento,
        "estado": "En progreso" if cumplimiento < 100 else "Completada",
        "inversion": generar_importe() * 10,
        "beneficiarios": random.randint(1000, 1000000)
    })

# 5. Generar alertas anticorrupción avanzadas
print("🚨 Generando alertas anticorrupción...")

# Detectar outliers en subvenciones
importes = [s["importe"] for s in subvenciones]
media = sum(importes) / len(importes)
desviacion = (sum((x - media) ** 2 for x in importes) / len(importes)) ** 0.5

for s in subvenciones:
    if s["importe"] > media + 2 * desviacion:
        alertas.append({
            "id": generar_id(f"outlier_{s['id']}"),
            "tipo": "CRÍTICA",
            "msg": f"Subvención anómala detectada: {s['beneficiario']}",
            "motivo": f"Importe muy superior a la media ({format_currency(s['importe'])})",
            "link": "#",
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "impacto": "ALTO"
        })

# Detectar concentración de beneficiarios
beneficiarios = {}
for s in subvenciones:
    beneficiarios[s["beneficiario"]] = beneficiarios.get(s["beneficiario"], 0) + 1

for ben, count in beneficiarios.items():
    if count > 3:
        alertas.append({
            "id": generar_id(f"concentracion_{ben}"),
            "tipo": "AVISO",
            "msg": f"Concentración de subvenciones: {ben}",
            "motivo": f"Ha recibido {count} subvenciones",
            "link": "#",
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "impacto": "MEDIO"
        })

# 6. Generar PDF profesional
print("📄 Generando informe PDF...")

def generar_pdf():
    doc = SimpleDocTemplate("datos/informe_transparencia.pdf", pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#0f172a')
    )
    story.append(Paragraph("Informe de Transparencia Pública", title_style))
    story.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Resumen ejecutivo
    story.append(Paragraph("Resumen Ejecutivo", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    resumen = f"""
    Este informe presenta un análisis detallado de la transparencia pública,
    incluyendo {len(boe_docs)} documentos del BOE, {len(subvenciones)} subvenciones
    y {len(alertas)} alertas de riesgo detectadas.
    """
    story.append(Paragraph(resumen, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Alertas críticas
    if alertas:
        story.append(Paragraph("Alertas de Riesgo", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        for alerta in alertas[:10]:
            story.append(Paragraph(
                f"• [{alerta['tipo']}] {alerta['msg']}",
                styles['Normal']
            ))
            story.append(Spacer(1, 5))
    
    # Tabla de subvenciones
    story.append(Spacer(1, 20))
    story.append(Paragraph("Principales Subvenciones", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    data = [["Beneficiario", "Concepto", "Importe", "Municipio"]]
    for s in subvenciones[:15]:
        data.append([
            s['beneficiario'][:20],
            s['concepto'][:15],
            f"{s['importe']:,} €",
            s['municipio']
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    
    doc.build(story)

generar_pdf()

# 7. Guardar JSONs
print("💾 Guardando datos...")
json.dump(boe_docs, open("datos/boe.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.dump(alertas, open("datos/alertas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.dump(subvenciones, open("datos/subvenciones.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.dump(gasto, open("datos/gasto.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.dump(promesas, open("datos/promesas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# 8. API simple
print("🌐 Generando API...")
api_content = """<?php
// API REST simple
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$data = [
    'boe' => json_decode(file_get_contents('../datos/boe.json'), true),
    'alertas' => json_decode(file_get_contents('../datos/alertas.json'), true),
    'subvenciones' => json_decode(file_get_contents('../datos/subvenciones.json'), true),
    'gasto' => json_decode(file_get_contents('../datos/gasto.json'), true),
    'promesas' => json_decode(file_get_contents('../datos/promesas.json'), true),
    'metadata' => [
        'fecha_actualizacion' => date('Y-m-d H:i:s'),
        'version' => '1.0.0'
    ]
];

echo json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
"""
open("api/datos.php", "w", encoding="utf-8").write(api_content)

# 9. Manifest mejorado para PWA
print("📱 Generando manifest PWA...")
manifest = {
    "name": "Observatorio de Transparencia Pública",
    "short_name": "ObsPub",
    "description": "Seguimiento de transparencia, subvenciones y gasto público",
    "start_url": "/observatorio-publico/",
    "display": "standalone",
    "background_color": "#f8fafc",
    "theme_color": "#0f172a",
    "icons": [
        {
            "src": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ]
}
json.dump(manifest, open("manifest.json", "w"), ensure_ascii=False, indent=2)

# 10. Generar HTML final
print("📝 Generando HTML...")
timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")

html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Observatorio de Transparencia Pública</title>
    <meta name="description" content="Seguimiento de transparencia, subvenciones y gasto público en España">
    <meta name="theme-color" content="#0f172a">
    
    <!-- PWA -->
    <link rel="manifest" href="manifest.json">
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/3135/3135715.png">
    
    <!-- CSS -->
    <link rel="stylesheet" href="estilo.css">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    
    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <header class="obs-header">
            <h1>🏛️ Observatorio de Transparencia Pública</h1>
            <p>Monitorizando la actividad del sector público español</p>
            <div style="display: flex; gap: 10px; justify-content: center;">
                <span class="badge" style="background: #10b981;">Última actualización: {timestamp}</span>
                <a href="datos/informe_transparencia.pdf" class="btn btn-primary" download>
                    📥 Descargar Informe PDF
                </a>
                <button class="btn btn-outline" id="refresh-btn">
                    🔄 Actualizar
                </button>
            </div>
        </header>

        <!-- Estadísticas rápidas -->
        <div class="obs-card" style="margin-bottom: 20px;" id="estadisticas">
            <!-- Se llena con JS -->
        </div>

        <!-- Tabs de navegación -->
        <div class="tabs">
            <div class="tab active" data-tab="resumen">📊 Resumen</div>
            <div class="tab" data-tab="subvenciones">💰 Subvenciones</div>
            <div class="tab" data-tab="gasto">💶 Gasto Público</div>
            <div class="tab" data-tab="boe">📜 BOE</div>
            <div class="tab" data-tab="promesas">🗳️ Promesas</div>
        </div>

        <div class="main-grid">
            <!-- Alertas -->
            <div class="obs-card">
                <h2 data-icon="🚨">Alertas de Riesgo</h2>
                <div class="alertas-container" id="alertas-box">
                    <div class="loading"></div>
                </div>
            </div>

            <!-- Mapa -->
            <div class="obs-card">
                <h2 data-icon="📍">Mapa Municipal</h2>
                <div id="map"></div>
                <p class="alerta-motivo" style="margin-top: 10px;">
                    Intensidad de color = volumen de subvenciones
                </p>
            </div>

            <!-- Subvenciones -->
            <div class="obs-card">
                <h2 data-icon="💰">Subvenciones Recientes</h2>
                <div id="subvenciones-lista">
                    <div class="loading"></div>
                </div>
            </div>

            <!-- Gasto Público -->
            <div class="obs-card">
                <h2 data-icon="💶">Gasto Público</h2>
                <div id="gasto-lista">
                    <div class="loading"></div>
                </div>
            </div>

            <!-- BOE -->
            <div class="obs-card" style="grid-column: span 2;">
                <h2 data-icon="📜">BOE Analizado</h2>
                <div id="boe-lista">
                    <div class="loading"></div>
                </div>
            </div>

            <!-- Promesas Políticas -->
            <div class="obs-card" style="grid-column: span 2;">
                <h2 data-icon="🗳️">Seguimiento de Promesas</h2>
                <div id="promesas-lista">
                    <div class="loading"></div>
                </div>
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="dashboard.js"></script>
    
    <!-- Service Worker para PWA -->
    <script>
        if ('serviceWorker' in navigator) {{
            navigator.serviceWorker.register('sw.js').catch(console.error);
        }}
    </script>
</body>
</html>"""

open("index.html", "w", encoding="utf-8").write(html_content)

# 11. Service Worker básico
sw_content = """// Service Worker para PWA
const CACHE_NAME = 'observatorio-v1';
const urlsToCache = [
    '/',
    '/estilo.css',
    '/dashboard.js',
    '/manifest.json',
    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => response || fetch(event.request))
    );
});"""

open("sw.js", "w", encoding="utf-8").write(sw_content)

print("✅ ¡Proyecto actualizado con éxito!")
print(f"📊 Datos generados: {len(boe_docs)} BOE, {len(subvenciones)} subvenciones, {len(alertas)} alertas")
print("🌐 Abre index.html en tu navegador para ver el resultado")
