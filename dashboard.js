// Mejoras táctiles para iPhone
document.addEventListener('touchstart', function(){}, {passive: true});

// Pull to refresh simulado
let startY = 0;
document.addEventListener('touchstart', (e) => {
    startY = e.touches[0].pageY;
}, {passive: true});

document.addEventListener('touchmove', (e) => {
    if (window.scrollY === 0 && e.touches[0].pageY > startY + 50) {
        document.querySelector('.pull-indicator').style.display = 'flex';
    }
}, {passive: true});

document.addEventListener('touchend', () => {
    if (document.querySelector('.pull-indicator').style.display === 'flex') {
        location.reload();
    }
});

// Ajuste de altura del mapa en móvil
function ajustarMapa() {
    const map = document.getElementById('map');
    if (map && window.innerWidth <= 390) {
        map.style.height = '220px';
    }
}
window.addEventListener('resize', ajustarMapa);
ajustarMapa();
