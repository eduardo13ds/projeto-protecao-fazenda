function updateCardColors(value, elementId, thresholds, descriptionElementId) {
    const card = document.getElementById(elementId);
    const description = document.getElementById(descriptionElementId);

    if (!card || !description) return; // Element not found

    if (value <= thresholds.low) {
        card.className = "card text-center dynamic-card green";
        description.textContent = `${value} - Baixo`;
    } else if (value <= thresholds.medium) {
        card.className = "card text-center dynamic-card blue";
        description.textContent = `${value} - Moderado`;
    } else {
        card.className = "card text-center dynamic-card red";
        description.textContent = `${value} - Crítico`;
    }
}

function fetchLatestData(areaId = null) {
    let url = "/latest-data";
    if (areaId !== null) {
        url += `/${areaId}`;
    }

    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            const mainAlertBanner = document.getElementById("custom-heavy-rain-alert");
            const headerAlertStatus = document.getElementById("header-alert-status");

            if (Object.keys(data).length === 0) {
                console.log(`Sem dados para a área ${areaId}`);
                if (mainAlertBanner) mainAlertBanner.classList.add("d-none");
                if (headerAlertStatus) {
                    headerAlertStatus.textContent = "Sem Alertas";
                    headerAlertStatus.classList.remove("alert-active");
                    headerAlertStatus.classList.add("alert-inactive");
                }
                // Clear other data fields or show placeholder
                document.getElementById("probabilidade-texto").textContent = "--% - Indefinido";
                document.getElementById("temperatura-texto").textContent = "--°C - Indefinido";
                document.getElementById("humidade-texto").textContent = "--% - Indefinido";
                document.getElementById("campo-eletrico-texto").textContent = "-- mA - Indefinido";
                const listaRazoes = document.getElementById("razoes-lista");
                if (listaRazoes) listaRazoes.innerHTML = "<li class='list-group-item'>Sem dados de razões.</li>";

                const areaDropdown = document.getElementById("areaDropdown");
                if (areaDropdown) {
                     areaDropdown.textContent = `Área: ${areaId !== null ? areaId : '--'}`;
                }
                return;
            }

            updateCardColors(data.current_mA || 0, "card-campo-eletrico", {
                low: 10, medium: 20,
            }, "campo-eletrico-texto");
            updateCardColors(data.temperatura || 0, "card-temperatura", {low: 20, medium: 30}, "temperatura-texto");
            updateCardColors(data.humidade || 0, "card-humidade", {low: 50, medium: 70}, "humidade-texto");

            const currentProb = data.probabilidade !== undefined ? parseInt(data.probabilidade) : null;

            if (currentProb !== null) {
                updateCardColors(currentProb, "card-probabilidade", {low: 50, medium: 75}, "probabilidade-texto");

                if (currentProb > 75) { // Alert condition
                    if (mainAlertBanner) {
                        mainAlertBanner.classList.remove("d-none"); // Show main alert
                        if (typeof updateAlert === "function") {
                            updateAlert(data.probabilidade || "--", data.humidade || "--", data.current_mA || "--", data.area || "N/A");
                        }
                    }
                    if (headerAlertStatus) {
                        headerAlertStatus.textContent = "Alerta Ativo";
                        headerAlertStatus.classList.remove("alert-inactive");
                        headerAlertStatus.classList.add("alert-active");
                    }
                } else { // No alert condition
                    if (mainAlertBanner) mainAlertBanner.classList.add("d-none"); // Hide main alert
                    if (headerAlertStatus) {
                        headerAlertStatus.textContent = "Sem Alertas";
                        headerAlertStatus.classList.remove("alert-active");
                        headerAlertStatus.classList.add("alert-inactive");
                    }
                }
            } else { // No probability data
                if (mainAlertBanner) mainAlertBanner.classList.add("d-none");
                if (headerAlertStatus) {
                    headerAlertStatus.textContent = "Sem Alertas";
                    headerAlertStatus.classList.remove("alert-active");
                    headerAlertStatus.classList.add("alert-inactive");
                }
                 document.getElementById("probabilidade-texto").textContent = "--% - Indefinido";
            }

            if (Array.isArray(data.razoes) && data.razoes.length > 0) {
                const lista = document.getElementById("razoes-lista");
                if (lista) {
                    lista.innerHTML = "";
                    data.razoes.forEach((razao) => {
                        const li = document.createElement("li");
                        li.classList.add("list-group-item");
                        li.textContent = razao;
                        lista.appendChild(li);
                    });
                }
            } else {
                 const lista = document.getElementById("razoes-lista");
                 if (lista) lista.innerHTML = "<li class='list-group-item'>Nenhuma razão específica no momento.</li>";
            }

            const areaDropdown = document.getElementById("areaDropdown");
            if (areaDropdown) {
                if (data.area !== undefined) {
                    areaDropdown.textContent = `Área: ${data.area}`;
                } else if (areaId !== null) {
                     areaDropdown.textContent = `Área: ${areaId}`;
                } else {
                    areaDropdown.textContent = `Área: --`;
                }
            }
        })
        .catch((error) => {
            console.error("Error fetching data:", error);
            const mainAlertBanner = document.getElementById("custom-heavy-rain-alert");
            const headerAlertStatus = document.getElementById("header-alert-status");
            if (mainAlertBanner) mainAlertBanner.classList.add("d-none");
            if (headerAlertStatus) {
                headerAlertStatus.textContent = "Erro Conexão";
                headerAlertStatus.classList.remove("alert-inactive");
                headerAlertStatus.classList.add("alert-active"); // Style as active to draw attention to error
            }
        });
}

// Obter o ID da área da URL atual (se existir)
function getCurrentAreaId() {
    const path = window.location.pathname;
    // Matches /<digits> or /<digits>/
    const match = path.match(/\/(\d+)(?:\/)?$/);
    return match ? parseInt(match[1]) : null;
}

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar com a área atual
    const currentAreaId = getCurrentAreaId();
    fetchLatestData(currentAreaId); // Fetch data once on load
    setInterval(() => fetchLatestData(currentAreaId), 5000); // Refresh data every 5 seconds (adjust as needed)

    // Update area dropdown text based on currentAreaId from URL, if not set by fetched data
    const areaDropdown = document.getElementById("areaDropdown");
    if (areaDropdown && !areaDropdown.textContent.includes(currentAreaId) && currentAreaId !== null) {
         // A simple mapping, you might want a more robust way to get area name from ID
        const areaNames = {1: "Central", 2: "Norte", 3: "Sul", 4: "Leste", 5: "Oeste"};
        areaDropdown.textContent = `Área: ${areaNames[currentAreaId] || currentAreaId}`;
    } else if (areaDropdown && currentAreaId === null && !areaDropdown.textContent.includes("Área:")) {
        // Default if no area in URL and not set by data yet
        areaDropdown.textContent = `Área: Todas`;
    }
});
// Inicializar com a área atual
const currentAreaId = getCurrentAreaId();
setInterval(() => fetchLatestData(currentAreaId), 2000);
