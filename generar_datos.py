    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="estilo.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <div class="container">
            <header class="obs-header">
                <h2 class="obs-header__title">Observatorio Público</h2>
                <span class="obs-header__sync">Sincronizado: {fecha_str}</span>
            </header>

            <main class="obs-card">
                <div class="obs-stats">
                    <div class="obs-stats__item">
                        <span class="obs-stats__label">Total Auditado</span>
                        <span class="obs-stats__value">{total:,.2f} €</span>
                    </div>
                    <div class="obs-stats__item">
                        <span class="obs-stats__label">Contratos</span>
                        <span class="obs-stats__value">{conteo}</span>
                    </div>
                </div>

                <div class="obs-content">
                    <h3 class="obs-content__title">📊 Top 5 Beneficiarios</h3>
                    <canvas id="chart"></canvas>
                </div>

                { "".join([f'<div class="obs-alert">⚠️ {a}</div>' for a in alertas]) }

                <div class="obs-actions">
                    <a href="{PDF_PATH}" class="btn btn--primary">📄 Descargar Informe PDF</a>
                </div>
            </main>
        </div>
        <script>
            new Chart(document.getElementById('chart'), {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(list(ranking.index))},
                    datasets: [{{ 
                        label: 'Euros', 
                        data: {json.dumps(list(ranking.values))}, 
                        backgroundColor: '#5bc0be' 
                    }}]
                }},
                options: {{ indexAxis: 'y', responsive: true }}
            }});
        </script>
    </body>
    </html>
    """
