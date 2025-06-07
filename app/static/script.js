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
    if (areaId !== null && areaId !== undefined) { // Check for undefined too
        url += `/${areaId}`;
    }

    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            const globalAlertBanner = document.getElementById("global-multiple-alerts-banner");
            const headerAlertStatus = document.getElementById("header-alert-status");

            if (areaId !== null && areaId !== undefined) { // Specific area view (index.html with /<area_id>)
                if (Object.keys(data).length === 0 || data.probabilidade === undefined) {
                    console.log(`Sem dados para a área ${areaId}`);
                    // Clear or set placeholders for card data
                    document.getElementById("probabilidade-texto").textContent = "--% - Indefinido";
                    document.getElementById("temperatura-texto").textContent = "--°C - Indefinido";
                    document.getElementById("humidade-texto").textContent = "--% - Indefinido";
                    document.getElementById("campo-eletrico-texto").textContent = "-- mA - Indefinido";
                    const listaRazoes = document.getElementById("razoes-lista");
                    if (listaRazoes) listaRazoes.innerHTML = "<li class='list-group-item'>Sem dados de razões.</li>";
                    // If there's a specific single alert banner for area view (not the global one)
                    // you might hide it here. For now, we assume index.html only uses the global banner.

                    // Update header alert status if needed for single area view specifically
                    // This part might need more thought if the global banner is also on single area view.
                    // For simplicity, let's assume the header reflects global state.
                    // We'll handle global alert state below based on whether ANY alert is active.

                    return; // Exit if no specific area data.
                }

                // Update cards for the specific area
                updateCardColors(data.current_mA || 0, "card-campo-eletrico", { low: 10, medium: 20 }, "campo-eletrico-texto");
                updateCardColors(data.temperatura || 0, "card-temperatura", { low: 20, medium: 30 }, "temperatura-texto");
                updateCardColors(data.humidade || 0, "card-humidade", { low: 50, medium: 70 }, "humidade-texto");
                updateCardColors(data.probabilidade || 0, "card-probabilidade", { low: 50, medium: 75 }, "probabilidade-texto");


                const listaRazoes = document.getElementById("razoes-lista");
                if (listaRazoes) {
                    if (Array.isArray(data.razoes) && data.razoes.length > 0) {
                        listaRazoes.innerHTML = "";
                        data.razoes.forEach((razao) => {
                            const li = document.createElement("li");
                            li.classList.add("list-group-item");
                            li.textContent = razao;
                            listaRazoes.appendChild(li);
                        });
                    } else {
                        listaRazoes.innerHTML = "<li class='list-group-item'>Nenhuma razão específica no momento.</li>";
                    }
                }
                // The global alert banner logic is handled when areaId is null.
                // For single area view, the cards are updated, the global banner reflects overall state.

            } else { // Global view (index.html without /<area_id> or for header status)
                     // data here is expected to be an ARRAY of active alerts.
                if (Array.isArray(data) && data.length > 0) {
                    // One or more alerts are active
                    if (globalAlertBanner) globalAlertBanner.classList.remove("d-none");
                    if (headerAlertStatus) {
                        headerAlertStatus.textContent = "Alerta(s) Ativo(s)!";
                        headerAlertStatus.classList.remove("alert-inactive");
                        headerAlertStatus.classList.add("alert-active");
                    }
                    // If on main page (no areaId) and you still want to show *some* default cards:
                    // You could pick the first alert, or an average, or a summary.
                    // For simplicity, let's assume the cards on main page show "no specific area" or are less prominent
                    // when multiple alerts are active, encouraging user to go to the panel.
                    // Or, if you are on the main page (currentAreaId is null), you might want to update
                    // the cards with the data of the *first* active alert for display purposes, or a summary.
                    // Let's update with the first alert for now if no area is selected.
                    if (window.location.pathname === '/' || window.location.pathname === '/index.html') { // Only if truly on main page
                        const firstAlert = data[0];
                        updateCardColors(firstAlert.current_mA || 0, "card-campo-eletrico", { low: 10, medium: 20 }, "campo-eletrico-texto");
                        updateCardColors(firstAlert.temperatura || 0, "card-temperatura", { low: 20, medium: 30 }, "temperatura-texto");
                        updateCardColors(firstAlert.humidade || 0, "card-humidade", { low: 50, medium: 70 }, "humidade-texto");
                        updateCardColors(firstAlert.probabilidade || 0, "card-probabilidade", { low: 50, medium: 75 }, "probabilidade-texto");
                        const listaRazoes = document.getElementById("razoes-lista");
                         if (listaRazoes) {
                            if (Array.isArray(firstAlert.razoes) && firstAlert.razoes.length > 0) {
                                listaRazoes.innerHTML = "";
                                firstAlert.razoes.forEach((razao) => {
                                    const li = document.createElement("li");
                                    li.classList.add("list-group-item");
                                    li.textContent = razao;
                                    listaRazoes.appendChild(li);
                                });
                            } else {
                                listaRazoes.innerHTML = "<li class='list-group-item'>Nenhuma razão específica no momento.</li>";
                            }
                        }
                        const areaDropdown = document.getElementById("areaDropdown");
                        if (areaDropdown && firstAlert.area !== undefined) {
                             areaDropdown.textContent = `Área: ${firstAlert.area} (Primeiro Alerta)`;
                        }
                    }


                } else {
                    // No active alerts globally, or data is not an array (error or single area with no alert)
                    if (globalAlertBanner) globalAlertBanner.classList.add("d-none");
                    if (headerAlertStatus) {
                        headerAlertStatus.textContent = "Sem Alertas";
                        headerAlertStatus.classList.remove("alert-active");
                        headerAlertStatus.classList.add("alert-inactive");
                    }
                    // If on main page (no areaId), clear cards or show placeholders
                    if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
                        document.getElementById("probabilidade-texto").textContent = "--% - Indefinido";
                        document.getElementById("temperatura-texto").textContent = "--°C - Indefinido";
                        document.getElementById("humidade-texto").textContent = "--% - Indefinido";
                        document.getElementById("campo-eletrico-texto").textContent = "-- mA - Indefinido";
                        const listaRazoes = document.getElementById("razoes-lista");
                        if (listaRazoes) listaRazoes.innerHTML = "<li class='list-group-item'>Sem dados de razões.</li>";
                         const areaDropdown = document.getElementById("areaDropdown");
                        if (areaDropdown) {
                             areaDropdown.textContent = `Área: Todas`;
                        }
                    }
                }
            }

            // Update area dropdown text based on areaId (this should be more robust if area names are needed)
            const areaDropdown = document.getElementById("areaDropdown");
            if (areaDropdown) {
                const currentPathAreaId = getCurrentAreaId(); // Get area from URL
                const areaNames = {1: "Central", 2: "Norte", 3: "Sul", 4: "Leste", 5: "Oeste", null: "Todas"};
                let displayAreaName = "Todas";
                if (currentPathAreaId !== null) {
                    displayAreaName = areaNames[currentPathAreaId] || `Área ${currentPathAreaId}`;
                }
                areaDropdown.textContent = `Área: ${displayAreaName}`;
            }


        })
        .catch((error) => {
            console.error("Error fetching data:", error);
            const globalAlertBanner = document.getElementById("global-multiple-alerts-banner");
            const headerAlertStatus = document.getElementById("header-alert-status");
            if (globalAlertBanner) globalAlertBanner.classList.add("d-none"); // Hide on error too
            if (headerAlertStatus) {
                headerAlertStatus.textContent = "Erro Conexão";
                headerAlertStatus.classList.remove("alert-inactive");
                headerAlertStatus.classList.add("alert-active"); // Style as active to draw attention to error
            }
        });
}

// Keep updateInmetCards and fetchLatestInmetData
function updateInmetCards(data) {
    document.getElementById('inmet-chuva').textContent = data["Chuva (mm)"] ?? '--';
    document.getElementById('inmet-vento').textContent = data["Vel. Vento (m/s)"] ?? '--';
    document.getElementById('inmet-pressao').textContent = data["Pressao Ins. (hPa)"] ?? '--';
    document.getElementById('inmet-radiacao').textContent = data["Radiacao (KJ/m²)"] ?? '--';
    let dataStr = data["Data"] || '--';
    let horaStr = data["Hora (UTC)"] ? `${data["Hora (UTC)"]}` : '-- UTC'; // Corrected to show unit even if time is missing

    // Ensure 'Hora (UTC)' is treated as a string and formatted correctly
    let displayHora = '--';
    if (data["Hora (UTC)"]) {
        let rawHora = String(data["Hora (UTC)"]);
        if (rawHora.length === 3) rawHora = "0" + rawHora; // Pad 3-digit times like "100" to "0100"
        if (rawHora.length === 4) { // Expected format e.g. "0100"
            displayHora = `${rawHora.substring(0,2)}:${rawHora.substring(2,4)} UTC`;
        } else {
             displayHora = `${rawHora} UTC`; // Fallback for unexpected format
        }
    }


    const horaElements = document.getElementsByClassName('inmet-data-hora');
    for (let i = 0; i < horaElements.length; i++) {
        horaElements[i].textContent = `Data: ${dataStr} | Hora: ${displayHora}`;
    }
}


function fetchLatestInmetData() {
    fetch('/latest-inmet')
        .then((response) => response.json())
        .then((data) => {
            if (!data || Object.keys(data).length === 0) {
                updateInmetCards({}); // Clear cards if no data
                return;
            }
            updateInmetCards(data);
        })
        .catch((error) => {
            console.error("Error fetching INMET data:", error);
            updateInmetCards({}); // Clear cards on error
        });
}


function getCurrentAreaId() {
    const path = window.location.pathname;
    const match = path.match(/\/(\d+)(?:\/)?$/);
    return match ? parseInt(match[1]) : null;
}

document.addEventListener('DOMContentLoaded', function() {
    const currentAreaId = getCurrentAreaId();

    // Fetch data for the specific area if URL indicates, or global alerts if not.
    fetchLatestData(currentAreaId);
    setInterval(() => fetchLatestData(currentAreaId), 5000);

    // If on the alertas.html page, fetch and display all alerts
    if (window.location.pathname.includes('/painel_alertas')) {
        fetchAndDisplayAllAlerts();
        setInterval(fetchAndDisplayAllAlerts, 7000); // Refresh alert panel
    }

    fetchLatestInmetData();
    setInterval(fetchLatestInmetData, 10000); // Refresh INMET data
});

// Function specific to alertas.html to display all active alerts
function fetchAndDisplayAllAlerts() {
    const panelContainer = document.getElementById("alert-panel-container");
    const noAlertsMessage = document.getElementById("no-alerts-message");
    if (!panelContainer) return; // Only run on alertas.html

    fetch("/latest-data") // Fetches the list of active alerts
        .then(response => response.json())
        .then(activeAlerts => {
            panelContainer.innerHTML = ""; // Clear previous alerts

            if (Array.isArray(activeAlerts) && activeAlerts.length > 0) {
                if (noAlertsMessage) noAlertsMessage.classList.add("d-none");
                activeAlerts.forEach(alertData => {
                    const alertBox = createAlertBox(alertData);
                    panelContainer.appendChild(alertBox);
                });
            } else {
                if (noAlertsMessage) noAlertsMessage.classList.remove("d-none");
            }
        })
        .catch(error => {
            console.error("Error fetching all alerts for panel:", error);
            if (panelContainer) panelContainer.innerHTML = "<p class='text-danger'>Erro ao carregar alertas.</p>";
            if (noAlertsMessage) noAlertsMessage.classList.add("d-none");
        });
}

function createAlertBox(data) {
    // Reuse styling from alert.html's .custom-heavy-rain-alert or define new ones
    // This function creates a DOM element for a single alert.
    // For simplicity, using a structure similar to the global alert but with details.
    const areaNames = { 1: "Central", 2: "Norte", 3: "Sul", 4: "Leste", 5: "Oeste" };
    const areaName = areaNames[data.area] || `Área ${data.area}`;

    const colDiv = document.createElement("div");
    colDiv.className = "col-md-6 col-lg-4 mb-3"; // Bootstrap column for responsiveness

    const cardDiv = document.createElement("div");
    cardDiv.className = "card h-100 shadow-sm alert-card-dynamic"; // Added alert-card-dynamic for potential specific styling

    // Determine card color based on probability
    if (data.probabilidade > 75) {
        cardDiv.classList.add("border-danger"); // Example: red border for high probability
    } else if (data.probabilidade > 50) {
        cardDiv.classList.add("border-warning"); // Example: orange border for medium
    } else {
        cardDiv.classList.add("border-info"); // Example: blue for lower
    }

    let reasonsHtml = "";
    if (Array.isArray(data.razoes) && data.razoes.length > 0) {
        reasonsHtml = data.razoes.map(r => `<li class="list-group-item small">${r}</li>`).join('');
    } else {
        reasonsHtml = "<li class='list-group-item small'>Nenhuma razão específica.</li>";
    }

    cardDiv.innerHTML = `
        <div class="card-header bg-transparent fw-bold">
            <i class="fas fa-cloud-showers-heavy"></i> Alerta: ${areaName}
        </div>
        <div class="card-body">
            <p class="card-text mb-1"><strong>Probabilidade:</strong> <span class="badge bg-danger">${data.probabilidade || '--'}%</span></p>
            <p class="card-text mb-1"><strong>Temperatura:</strong> ${data.temperatura || '--'}°C</p>
            <p class="card-text mb-1"><strong>Umidade:</strong> ${data.humidade || '--'}%</p>
            <p class="card-text mb-1"><strong>Campo Elétrico:</strong> ${data.current_mA || '--'} mA</p>
            <p class="card-text mb-1 mt-2"><strong>Razões:</strong></p>
            <ul class="list-group list-group-flush small">${reasonsHtml}</ul>
        </div>
        <div class="card-footer bg-transparent text-muted small">
            Última atualização: ${new Date().toLocaleTimeString()} </div>
    `;
    // Potential styling for .alert-card-dynamic in style.css if needed
    // .alert-card-dynamic.border-danger { background-color: #ffebee; }
    // .alert-card-dynamic.border-warning { background-color: #fff3e0; }

    colDiv.appendChild(cardDiv);
    return colDiv;
}

// The old `updateAlert` function is not directly used for the global banner anymore.
// It could be repurposed or used if you have a view that shows a single, detailed alert.
/*
function updateAlert(prob, umid, campo, area) {
    // This function was for the old single alert banner.
    // Its logic might be integrated into createAlertBox or a similar function
    // if you have a page/modal for viewing one specific alert in detail.
    // For the global banner on index.html, it's now just a notification.
}
*/