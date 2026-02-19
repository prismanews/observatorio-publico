// Configuración
const CONFIG = {
    API_BASE: 'api/datos.php',
    REFRESH_INTERVAL: 300000, // 5 minutos
    MAP_CENTER: [40.4168, -3.7038],
    MAP_ZOOM: 6
};

// Estado de la aplicación
let appState = {
    boe: [],
    alertas: [],
    subvenciones: [],
    gasto: [],
    promesas: [],
    currentTab: 'resumen'
};

// Inicialización
async function init() {
    try {
        showLoading();
        await loadAllData();
        renderAll();
        setupEventListeners();
        startAutoRefresh();
        hideLoading();
    } catch (error) {
        console.error('Error initializing app:', error);
        showError('Error al cargar los datos. Por favor, recarga la página.');
    }
}

// Carga de datos
async function loadAllData() {
    try {
        const [boe, alertas, subvenciones, gasto, promesas] = await Promise.all([
            fetch('datos/boe.json').then(r => r.json()),
            fetch('datos/alertas.json').then(r => r.json()),
            fetch('datos/subvenciones.json').then(r => r.json()),
            fetch('datos/gasto.json').then(r => r.json()),
            fetch('datos/promesas.json').then(r => r.json())
        ]);

        appState = {
            ...appState,
            boe,
            alertas,
            subvenciones,
            gasto,
            promesas
        };
    } catch (error) {
        console.error('Error loading data:', error);
        throw error;
    }
}

// Renderizado completo
function renderAll() {
    renderAlertas();
    renderBoe();
    renderSubvenciones();
    renderGasto();
    renderPromesas();
    renderEstadisticas();
    initMap();
}

// Renderizar alertas
function renderAlertas() {
    const container = document.getElementById('alertas-box');
    if (!container) return;

    if (!appState.alertas.length) {
        container.innerHTML = '<div class="alert">No hay alertas activas</div>';
        return;
    }

    container.innerHTML = appState.alertas.map(alerta => `
        <div class="alerta-item ${alerta.tipo === 'CRÍTICA' ? 'critica' : 'aviso'}">
            <span class="alerta-tipo ${alerta.tipo === 'CRÍTICA' ? 'critica' : 'aviso'}">${alerta.tipo}</span>
            <div class="alerta-msg">${alerta.msg}</div>
            <div class="alerta-motivo">${alerta.motivo}</div>
            <a href="${alerta.link}" target="_blank" class="alerta-link">Ver detalles →</a>
        </div>
    `).join('');
}

// Renderizar BOE
function renderBoe() {
    const container = document.getElementById('boe-lista');
    if (!container) return;

    if (!appState.boe.length) {
        container.innerHTML = '<div class="alert">No hay documentos BOE disponibles</div>';
        return;
    }

    container.innerHTML = appState.boe.map(doc => `
        <div class="boe-item">
            <span class="badge" style="background: ${doc.color}">${doc.categoria}</span>
            <a href="${doc.link}" target="_blank" class="boe-titulo">${doc.titulo}</a>
            <a href="${doc.link}" target="_blank" class="boe-link">
                🔗 Ver en BOE
            </a>
        </div>
    `).join('');
}

// Renderizar subvenciones
function renderSubvenciones() {
    const container = document.getElementById('subvenciones-lista');
    if (!container) return;

    const subvenciones = appState.subvenciones.slice(0, 5);
    
    container.innerHTML = `
        <div class="stat-grid">
            <div class="stat-item">
                <div class="stat-value">${formatNumber(appState.subvenciones.length)}</div>
                <div class="stat-label">Total</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${formatCurrency(calculateTotal(appState.subvenciones))}</div>
                <div class="stat-label">Importe total</div>
            </div>
        </div>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Beneficiario</th>
                    <th>Importe</th>
                    <th>Municipio</th>
                </tr>
            </thead>
            <tbody>
                ${subvenciones.map(s => `
                    <tr>
                        <td>${s.beneficiario}</td>
                        <td>${formatCurrency(s.importe)}</td>
                        <td>${s.municipio}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
        <button class="btn btn-outline" style="margin-top: 15px; width: 100%;" onclick="verMas('subvenciones')">
            Ver todas las subvenciones →
        </button>
    `;
}

// Renderizar gasto público
function renderGasto() {
    const container = document.getElementById('gasto-lista');
    if (!container) return;

    const gastos = appState.gasto.slice(0, 5);
    
    container.innerHTML = `
        <div class="stat-grid">
            <div class="stat-item">
                <div class="stat-value">${formatCurrency(calculateTotal(appState.gasto))}</div>
                <div class="stat-label">Gasto total</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${appState.gasto.length}</div>
                <div class="stat-label">Partidas</div>
            </div>
        </div>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Concepto</th>
                    <th>Importe</th>
                    <th>Ministerio</th>
                </tr>
            </thead>
            <tbody>
                ${gastos.map(g => `
                    <tr>
                        <td>${g.concepto}</td>
                        <td>${formatCurrency(g.importe)}</td>
                        <td>${g.ministerio}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// Renderizar promesas políticas
function renderPromesas() {
    const container = document.getElementById('promesas-lista');
    if (!container) return;

    container.innerHTML = appState.promesas.map(p => `
        <div class="boe-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong>${p.promesa}</strong>
                <span class="badge" style="background: ${getPromesaColor(p.cumplimiento)}">
                    ${p.cumplimiento}% cumplida
                </span>
            </div>
            <div class="progress" style="margin: 10px 0;">
                <div class="progress-bar" style="width: ${p.cumplimiento}%"></div>
            </div>
            <small class="alerta-motivo">Fecha: ${p.fecha} | Partido: ${p.partido}</small>
        </div>
    `).join('');
}

// Renderizar estadísticas
function renderEstadisticas() {
    const stats = {
        totalAlertas: appState.alertas.length,
        alertasCriticas: appState.alertas.filter(a => a.tipo === 'CRÍTICA').length,
        totalBoe: appState.boe.length,
        totalSubvenciones: appState.subvenciones.length,
        totalGasto: formatCurrency(calculateTotal(appState.gasto)),
        fechaActualizacion: new Date().toLocaleString()
    };

    const statsHtml = `
        <div class="stat-grid">
            <div class="stat-item">
                <div class="stat-value">${stats.totalAlertas}</div>
                <div class="stat-label">Alertas totales</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.alertasCriticas}</div>
                <div class="stat-label">Críticas</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.totalBoe}</div>
                <div class="stat-label">Documentos BOE</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.totalSubvenciones}</div>
                <div class="stat-label">Subvenciones</div>
            </div>
        </div>
        <div class="alerta-motivo" style="text-align: right; margin-top: 10px;">
            Última actualización: ${stats.fechaActualizacion}
        </div>
    `;

    const statsContainer = document.getElementById('estadisticas');
    if (statsContainer) {
        statsContainer.innerHTML = statsHtml;
    }
}

// Inicializar mapa
function initMap() {
    if (!document.getElementById('map')) return;

    try {
        const map = L.map('map').setView(CONFIG.MAP_CENTER, CONFIG.MAP_ZOOM);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Cargar GeoJSON de municipios
        fetch('datos/municipios.geojson')
            .then(r => r.json())
            .then(geojson => {
                L.geoJSON(geojson, {
                    style: {
                        fillColor: '#3b82f6',
                        fillOpacity: 0.2,
                        color: '#2563eb',
                        weight: 1
                    },
                    onEachFeature: (feature, layer) => {
                        const subvenciones = appState.subvenciones.filter(
                            s => s.municipio === feature.properties.name
                        );
                        const total = calculateTotal(subvenciones);
                        
                        layer.bindPopup(`
                            <b>${feature.properties.name}</b><br>
                            Subvenciones: ${subvenciones.length}<br>
                            Importe total: ${formatCurrency(total)}
                        `);
                    }
                }).addTo(map);
            })
            .catch(err => console.error('Error loading GeoJSON:', err));

        // Añadir marcadores de actividad
        const puntosActividad = [
            { coords: [40.4168, -3.7038], nombre: 'Madrid', tipo: 'Administración Central' },
            { coords: [41.3851, 2.1734], nombre: 'Barcelona', tipo: 'Actividad Industrial' },
            { coords: [37.3891, -5.9845], nombre: 'Sevilla', tipo: 'Administración Autonómica' },
            { coords: [39.4699, -0.3763], nombre: 'Valencia', tipo: 'Actividad Portuaria' }
        ];

        puntosActividad.forEach(p => {
            const marker = L.marker(p.coords).addTo(map);
            marker.bindPopup(`<b>${p.nombre}</b><br>${p.tipo}`);
        });

    } catch (error) {
        console.error('Error initializing map:', error);
    }
}

// Utilidades
function formatNumber(num) {
    return new Intl.NumberFormat('es-ES').format(num);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function calculateTotal(items) {
    return items.reduce((sum, item) => sum + (item.importe || 0), 0);
}

function getPromesaColor(cumplimiento) {
    if (cumplimiento >= 75) return '#10b981';
    if (cumplimiento >= 50) return '#f59e0b';
    if (cumplimiento >= 25) return '#ef4444';
    return '#64748b';
}

function showLoading() {
    document.body.classList.add('loading');
}

function hideLoading() {
    document.body.classList.remove('loading');
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger';
    errorDiv.textContent = message;
    document.body.prepend(errorDiv);
    setTimeout(() => errorDiv.remove(), 5000);
}

function setupEventListeners() {
    // Tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            appState.currentTab = tab.dataset.tab;
            // Aquí podrías implementar cambio de vista
        });
    });

    // Botón de actualizar
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', async () => {
            showLoading();
            await loadAllData();
            renderAll();
            hideLoading();
        });
    }
}

function startAutoRefresh() {
    setInterval(async () => {
        await loadAllData();
        renderAll();
    }, CONFIG.REFRESH_INTERVAL);
}

function verMas(tipo) {
    console.log(`Ver más de ${tipo}`);
    // Aquí podrías implementar navegación a vista detallada
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', init);
