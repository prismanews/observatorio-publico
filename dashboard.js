async function init() {
    try {
        const boe = await fetch("datos/boe.json").then(r => r.json());
        const alertas = await fetch("datos/alertas.json").then(r => r.json());

        // 1. Renderizar Alertas (Corregido para que nunca esté vacío)
        const boxAlertas = document.getElementById("alertas-box");
        boxAlertas.innerHTML = "";
        alertas.forEach(a => {
            boxAlertas.innerHTML += `
                <div class="alerta-item" style="border-left-color: ${a.tipo === 'CRÍTICA' ? '#ef4444' : '#3b82f6'}">
                    <strong>${a.tipo}</strong>: ${a.msg}<br>
                    <small>Motivo: ${a.motivo}</small>
                </div>`;
        });

        // 2. Renderizar Lista BOE
        const boxBoe = document.getElementById("boe-lista");
        boe.forEach(b => {
            boxBoe.innerHTML += `
                <div style="margin-bottom:10px; border-bottom:1px solid #eee; padding-bottom:5px;">
                    <span class="badge" style="background:${b.color}">${b.categoria}</span>
                    <a href="${b.link}" target="_blank" style="color:#1e293b; text-decoration:none; display:block; margin-top:3px;">${b.titulo}</a>
                </div>`;
        });

        // 3. Mapa Real (Leaflet)
        var map = L.map('map').setView([40.41, -3.70], 5);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

        // Añadimos puntos donde hay actividad del BOE
        L.marker([40.41, -3.70]).addTo(map).bindPopup('<b>Madrid</b><br>Sede Administrativa Central.');
        L.marker([41.38, 2.17]).addTo(map).bindPopup('<b>Barcelona</b><br>Actividad industrial detectada.');

    } catch (e) { console.error("Error:", e); }
}
window.onload = init;
