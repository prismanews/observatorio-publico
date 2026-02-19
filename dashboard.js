async function init() {
    try {
        const boe = await fetch("datos/boe.json").then(r => r.json());
        const alertas = await fetch("datos/alertas.json").then(r => r.json());

        // 1. Renderizar Alertas
        const boxAlertas = document.getElementById("alertas-box");
        boxAlertas.innerHTML = alertas.length ? "" : "No hay alertas críticas hoy.";
        alertas.forEach(a => {
            boxAlertas.innerHTML += `
                <div class="alerta-item" style="border-left-color: ${a.tipo === 'CRÍTICA' ? '#ef4444' : '#f59e0b'}">
                    <strong>${a.tipo}</strong>: ${a.msg}<br>
                    <a href="${a.link}" target="_blank" style="font-size:0.8rem; color: #3b82f6;">Ver en BOE →</a>
                </div>`;
        });

        // 2. Renderizar Lista BOE
        const boxBoe = document.getElementById("boe-lista");
        boe.forEach(b => {
            boxBoe.innerHTML += `
                <div style="margin-bottom:12px; border-bottom:1px solid #f1f5f9; padding-bottom:8px;">
                    <span class="badge" style="background:${b.color}">${b.categoria}</span>
                    <a href="${b.link}" target="_blank" style="color:#1e293b; text-decoration:none; display:block; margin-top:5px;">${b.titulo}</a>
                </div>`;
        });

        // 3. Inicializar Mapa (Leaflet)
        var map = L.map('map').setView([40.41, -3.70], 5);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap'
        }).addTo(map);

        // Puntos de ejemplo (puedes añadir más dinámicamente)
        L.marker([40.41, -3.70]).addTo(map).bindPopup('<b>Madrid</b><br>Sede Central: 24 alertas.');
        L.marker([41.38, 2.17]).addTo(map).bindPopup('<b>Barcelona</b><br>Actividad económica detectada.');

    } catch (e) {
        console.error("Error en el Observatorio:", e);
    }
}

window.onload = init;
