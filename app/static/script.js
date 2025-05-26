function updateCardColors(value, elementId, thresholds, descriptionElementId) {
    const card = document.getElementById(elementId);
    const description = document.getElementById(descriptionElementId);

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
            // Verificar se há dados para esta área
            if (Object.keys(data).length === 0) {
                console.log(`Sem dados para a área ${areaId}`);
                return;
            }

            updateCardColors(data.current_mA || 0, "card-campo-eletrico", {
                low: 10, medium: 20,
            }, "campo-eletrico-texto");
            updateCardColors(data.temperatura || 0, "card-temperatura", {low: 20, medium: 30}, "temperatura-texto");
            updateCardColors(data.humidade || 0, "card-humidade", {low: 50, medium: 70}, "humidade-texto");

            if (data.probabilidade) {
                const probValue = parseInt(data.probabilidade);
                updateCardColors(probValue, "card-probabilidade", {low: 50, medium: 75}, "probabilidade-texto");

                if (probValue > 75) {
                    if (typeof updateAlert === "function") {
                        updateAlert(data.probabilidade || "--", data.humidade || "--", data.current_mA || "--");
                    }
                }
            }

            if (Array.isArray(data.razoes)) {
                const lista = document.getElementById("razoes-lista");
                lista.innerHTML = ""; // Limpa uma vez só

                data.razoes.forEach((razao) => {
                    const li = document.createElement("li");
                    li.classList.add("list-group-item");
                    li.textContent = razao;
                    lista.appendChild(li);
                });
            }

            const areaIndicator = document.getElementById("area-indicator");
            if (areaIndicator) {
                areaIndicator.textContent = `Área: ${data.area || "Desconhecida"}`;
            }
        })
        .catch((error) => console.error("Error fetching data:", error));
}

// Obter o ID da área da URL atual (se existir)
function getCurrentAreaId() {
    const path = window.location.pathname;
    const match = path.match(/\/(\d+)$/);
    return match ? parseInt(match[1]) : null;
}

// Inicializar com a área atual
const currentAreaId = getCurrentAreaId();
setInterval(() => fetchLatestData(currentAreaId), 2000);
