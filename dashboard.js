async function init() {
    const boe = await fetch("datos/boe.json").then(r => r.json());
    const alertas = await fetch("datos/alertas.json").then(r => r.json());

    // Cargar Alertas
    const boxAlertas = document.getElementById("alertas-box");
    alertas.forEach(a => {
        boxAlertas.innerHTML += `<div class="alerta-item"><strong>${a.tipo}</strong>: ${a.msg}</div>`;
    });

    // Cargar BOE
    const boxBoe = document.getElementById("boe-lista");
    boe.forEach(b => {
        boxBoe.innerHTML += `
            <div style="margin-bottom:12px; border-bottom:1px solid #eee; padding-bottom:8px;">
                <span class="badge" style="background:${b.color}">${b.categoria}</span>
                <a href="${b.link}" target="_blank" style="color:#334155; text-decoration:none; display:block; margin-top:5px;">${b.titulo}</a>
            </div>`;
    });

    // Mapa Leaflet (Municipal aproximado)
    var map = L.map('map').setView([40.41, -3.70], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

    // Simulación de puntos calientes en municipios (puedes ampliarlo con un GeoJSON real)
    const puntos = [
        {name: "Madrid", lat: 40.41, lon: -3.70, info: "Alta concentración de contratos"},
        {name: "Barcelona", lat: 41.38, lon: 2.17, info: "Subvenciones transporte activas"}
    ];
    puntos.forEach(p => L.marker([p.lat, p.lon]).addTo(map).bindPopup(`<b>${p.name}</b><br>${p.info}`));
}

window.onload = init;
