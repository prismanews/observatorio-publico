async function cargarDashboard() {

  const subv = await fetch("datos/subvenciones.json").then(r => r.json());
  const alertas = await fetch("datos/alertas.json").then(r => r.json());

  // Alertas
  const ul = document.getElementById("alertas");
  alertas.forEach(a => {
    const li = document.createElement("li");
    li.textContent = a.organismo + " — " + a.objeto;
    ul.appendChild(li);
  });

  // Dashboard gráfico
  const ctx = document.getElementById("graficoSubvenciones");

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: subv.map(s => s.organismo),
      datasets: [{
        label: "Subvenciones detectadas",
        data: subv.map(() => 1)
      }]
    }
  });
}

cargarDashboard();
