// Mapeamento de IDs de área para nomes
const AREA_NAMES = {
  1: "Central",
  2: "Norte",
  3: "Sul",
  4: "Leste",
  5: "Oeste",
};

// Helper function for authenticated fetch requests
async function authenticatedFetch(url, options = {}) {
  try {
    const response = await fetch(url, options);

    if (!response.ok) {
      if (response.status === 401) {
        console.log("Usuário não autenticado - redirecionando para login");
        window.location.href = "/login";
        return null;
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response;
  } catch (error) {
    console.error("Erro na requisição:", error);
    throw error;
  }
}

// -----------------------------------------------------------------
// NOVA FUNÇÃO CORRIGIDA - A SOLUÇÃO!
// Use esta no lugar da antiga.
// -----------------------------------------------------------------
function updateCardColors(value, elementId, thresholds, descriptionElementId) {
  const card = document.getElementById(elementId);
  const description = document.getElementById(descriptionElementId);

  // Se o card não for encontrado, não fazemos nada.
  if (!card || !description) {
    console.warn(
      `Elemento não encontrado: ${elementId} ou ${descriptionElementId}`,
    );
    return;
  }

  // 1. GARANTIMOS QUE AS CLASSES BASE ESTEJAM SEMPRE LÁ
  // O ideal é que elas já estejam no HTML, mas esta é uma segurança extra.
  card.classList.add("card", "card-tematico", "text-center");

  // 2. LIMPAMOS APENAS AS CLASSES DE DESTAQUE ANTIGAS
  // Isso evita que o card fique com múltiplas cores.
  card.classList.remove(
    "card-highlight-ok",
    "card-highlight-mid",
    "card-highlight-crit",
  );

  // 3. ADICIONAMOS A NOVA CLASSE DE DESTAQUE CORRETA
  if (value <= thresholds.low) {
    card.classList.add("card-highlight-ok");
    description.textContent = `${value} - Normal`;
  } else if (value <= thresholds.medium) {
    card.classList.add("card-highlight-mid");
    description.textContent = `${value} - Moderado`;
  } else {
    card.classList.add("card-highlight-crit");
    description.textContent = `${value} - Crítico`;
  }
}

function fetchLatestData(areaId = null) {
  let url = "/latest-data";
  if (areaId !== null && areaId !== undefined) {
    url += `/${areaId}`;
  }

  authenticatedFetch(url)
    .then((response) => {
      if (!response) return; // Authentication failed, redirect handled
      return response.json();
    })
    .then((data) => {
      const globalAlertBanner = document.getElementById(
        "global-multiple-alerts-banner",
      );
      const headerAlertStatus = document.getElementById("header-alert-status");

      // Função auxiliar para mostrar alerta global se não houver local
      function showGlobalAlertFallback() {
        authenticatedFetch("/latest-data")
          .then((resp) => {
            if (!resp) return; // Authentication failed, redirect handled
            return resp.json();
          })
          .then((globalData) => {
            updateCustomAlert(globalData, true);
          });
      }

      if (areaId !== null && areaId !== undefined) {
        // Vista específica de área
        if (
          Object.keys(data).length === 0 ||
          data.probabilidade === undefined ||
          data.probabilidade <= 75
        ) {
          // Não há alerta crítico local, buscar global
          showGlobalAlertFallback();
          // Limpar placeholders dos cards
          document.getElementById("precipitacao-texto").textContent = "-- mm";
          document.getElementById("temperatura-texto").textContent =
            "--°C - Indefinido";
          document.getElementById("humidade-texto").textContent =
            "--% - Indefinido";
          document.getElementById("campo-eletrico-texto").textContent =
            "-- mA - Indefinido";
          const listaRazoes = document.getElementById("razoes-lista");
          if (listaRazoes)
            listaRazoes.innerHTML =
              "<li class='list-group-item'>Sem dados de razões.</li>";
        }

        // Se tem alerta crítico local, buscar global para saber se há outros
        authenticatedFetch("/latest-data")
          .then((resp) => {
            if (!resp) return; // Authentication failed, redirect handled
            return resp.json();
          })
          .then((globalData) => {
            // Filtrar alertas críticos diferentes da área atual
            const otherCritical = Array.isArray(globalData)
              ? globalData.filter(
                  (a) => a.probabilidade > 75 && a.area !== areaId,
                )
              : [];
            updateCustomAlert(data, false, otherCritical.length);
          });

        updateCardColors(
          data.current_mA || 0,
          "card-campo-eletrico",
          {
            low: 10,
            medium: 20,
          },
          "campo-eletrico-texto",
        );
        updateCardColors(
          data.temperatura || 0,
          "card-temperatura",
          { low: 20, medium: 30 },
          "temperatura-texto",
        );
        updateCardColors(
          data.humidade || 0,
          "card-humidade",
          { low: 50, medium: 70 },
          "humidade-texto",
        );
        updateCardColors(
          data.predicted_precipitation_mm || 0,
          "card-precipitacao",
          {
            low: 5,
            medium: 15,
          },
          "precipitacao-texto",
        );

        // Atualizar lista de razões
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
            listaRazoes.innerHTML =
              "<li class='list-group-item'>Nenhuma razão específica no momento.</li>";
          }
        }
      } else {
        // Vista global
        if (Array.isArray(data) && data.length > 0) {
          updateCustomAlert(data, true);
          if (globalAlertBanner) globalAlertBanner.classList.remove("d-none");
          if (headerAlertStatus) {
            headerAlertStatus.textContent = "Alerta(s) Ativo(s)!";
            headerAlertStatus.classList.remove("alert-inactive");
            headerAlertStatus.classList.add("alert-active");
          }

          if (
            window.location.pathname === "/" ||
            window.location.pathname === "/index.html"
          ) {
            const firstAlert = data[0];
            updateCardColors(
              firstAlert.current_mA || 0,
              "card-campo-eletrico",
              {
                low: 10,
                medium: 20,
              },
              "campo-eletrico-texto",
            );
            updateCardColors(
              firstAlert.temperatura || 0,
              "card-temperatura",
              {
                low: 20,
                medium: 30,
              },
              "temperatura-texto",
            );
            updateCardColors(
              firstAlert.humidade || 0,
              "card-humidade",
              {
                low: 50,
                medium: 70,
              },
              "humidade-texto",
            );
            updateCardColors(
              firstAlert.probabilidade || 0,
              "card-precipitacao",
              {
                low: 10,
                medium: 25,
              },
              "precipitacao-texto",
            );
            const listaRazoes = document.getElementById("razoes-lista");
            if (listaRazoes) {
              if (
                Array.isArray(firstAlert.razoes) &&
                firstAlert.razoes.length > 0
              ) {
                listaRazoes.innerHTML = "";
                firstAlert.razoes.forEach((razao) => {
                  const li = document.createElement("li");
                  li.classList.add("list-group-item");
                  li.textContent = razao;
                  listaRazoes.appendChild(li);
                });
              } else {
                listaRazoes.innerHTML =
                  "<li class='list-group-item'>Nenhuma razão específica no momento.</li>";
              }
            }
            const areaDropdown = document.getElementById("areaDropdown");
            if (areaDropdown && firstAlert.area !== undefined) {
              areaDropdown.textContent = `Área: ${firstAlert.area} (Primeiro Alerta)`;
            }
          }
        } else {
          updateCustomAlert(null);
          if (globalAlertBanner) globalAlertBanner.classList.add("d-none");
          if (headerAlertStatus) {
            headerAlertStatus.textContent = "Sem Alertas";
            headerAlertStatus.classList.remove("alert-active");
            headerAlertStatus.classList.add("alert-inactive");
          }
          if (
            window.location.pathname === "/" ||
            window.location.pathname === "/index.html"
          ) {
            document.getElementById("precipitacao-texto").textContent = "-- mm";
            document.getElementById("temperatura-texto").textContent =
              "--°C - Indefinido";
            document.getElementById("humidade-texto").textContent =
              "--% - Indefinido";
            document.getElementById("campo-eletrico-texto").textContent =
              "-- mA - Indefinido";
            const listaRazoes = document.getElementById("razoes-lista");
            if (listaRazoes)
              listaRazoes.innerHTML =
                "<li class='list-group-item'>Sem dados de razões.</li>";
            const areaDropdown = document.getElementById("areaDropdown");
            if (areaDropdown) {
              areaDropdown.textContent = `Área: Todas`;
            }
          }
        }
      }

      // Atualizar dropdown de área
      const areaDropdown = document.getElementById("areaDropdown");
      if (areaDropdown) {
        const currentPathAreaId = getCurrentAreaId();
        let displayAreaName = "Todas";
        if (currentPathAreaId !== null) {
          displayAreaName =
            AREA_NAMES[currentPathAreaId] || `Área ${currentPathAreaId}`;
        }
        areaDropdown.textContent = `Área: ${displayAreaName}`;
      }
    })
    .catch((error) => {
      console.error("Error fetching data:", error);
      updateCustomAlert(null);
      if (globalAlertBanner) globalAlertBanner.classList.add("d-none");
      if (headerAlertStatus) {
        headerAlertStatus.textContent = "Erro Conexão";
        headerAlertStatus.classList.remove("alert-inactive");
        headerAlertStatus.classList.add("alert-active");
      }
    });
}

// Keep updateInmetCards and fetchLatestInmetData
function updateInmetCards(data) {
  document.getElementById("inmet-chuva").textContent =
    data["Chuva (mm)"] ?? "--";
  document.getElementById("inmet-vento").textContent =
    data["Vel. Vento (m/s)"] ?? "--";
  document.getElementById("inmet-pressao").textContent =
    data["Pressao Ins. (hPa)"] ?? "--";
  document.getElementById("inmet-radiacao").textContent =
    data["Radiacao (KJ/m²)"] ?? "--";
  let dataStr = data["Data"] || "--";
  let horaStr = data["Hora (UTC)"] ? `${data["Hora (UTC)"]}` : "-- UTC"; // Corrected to show unit even if time is missing

  // Ensure 'Hora (UTC)' is treated as a string and formatted correctly
  let displayHora = "--";
  if (data["Hora (UTC)"]) {
    let rawHora = String(data["Hora (UTC)"]);
    if (rawHora.length === 3) rawHora = "0" + rawHora; // Pad 3-digit times like "100" to "0100"
    if (rawHora.length === 4) {
      // Expected format e.g. "0100"
      displayHora = `${rawHora.substring(0, 2)}:${rawHora.substring(2, 4)} UTC`;
    } else {
      displayHora = `${rawHora} UTC`; // Fallback for unexpected format
    }
  }

  const horaElements = document.getElementsByClassName("inmet-data-hora");
  for (let i = 0; i < horaElements.length; i++) {
    horaElements[i].textContent = `Data: ${dataStr} | Hora: ${displayHora}`;
  }
}

function fetchLatestInmetData() {
  authenticatedFetch("/latest-inmet")
    .then((response) => {
      if (!response) return; // Authentication failed, redirect handled
      return response.json();
    })
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

document.addEventListener("DOMContentLoaded", function () {
  const currentAreaId = getCurrentAreaId();

  // Fetch data for the specific area if URL indicates, or global alerts if not.
  fetchLatestData(currentAreaId);
  setInterval(() => fetchLatestData(currentAreaId), 5000);

  // If on the alertas.html page, fetch and display all alerts
  if (window.location.pathname.includes("/painel_alertas")) {
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

  authenticatedFetch("/latest-data") // Fetches the list of active alerts
    .then((response) => {
      if (!response) return; // Authentication failed, redirect handled
      return response.json();
    })
    .then((activeAlerts) => {
      panelContainer.innerHTML = ""; // Clear previous alerts

      if (Array.isArray(activeAlerts) && activeAlerts.length > 0) {
        if (noAlertsMessage) noAlertsMessage.classList.add("d-none");
        activeAlerts.forEach((alertData) => {
          const alertBox = createAlertBox(alertData);
          panelContainer.appendChild(alertBox);
        });
      } else {
        if (noAlertsMessage) noAlertsMessage.classList.remove("d-none");
      }
    })
    .catch((error) => {
      console.error("Error fetching all alerts for panel:", error);
      if (panelContainer)
        panelContainer.innerHTML =
          "<p class='text-danger'>Erro ao carregar alertas.</p>";
      if (noAlertsMessage) noAlertsMessage.classList.add("d-none");
    });
}

function createAlertBox(data) {
  // Reuse styling from alert.html's .custom-heavy-rain-alert or define new ones
  // This function creates a DOM element for a single alert.
  // For simplicity, using a structure similar to the global alert but with details.
  const areaNames = {
    1: "Central",
    2: "Norte",
    3: "Sul",
    4: "Leste",
    5: "Oeste",
  };
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
    reasonsHtml = data.razoes
      .map((r) => `<li class="list-group-item small">${r}</li>`)
      .join("");
  } else {
    reasonsHtml =
      "<li class='list-group-item small'>Nenhuma razão específica.</li>";
  }

  cardDiv.innerHTML = `
        <div class="card-header bg-transparent fw-bold">
            <i class="fas fa-cloud-showers-heavy"></i> Alerta: ${areaName}
        </div>
        <div class="card-body">
            <p class="card-text mb-1"><strong>Probabilidade:</strong> <span class="badge bg-danger">${data.probabilidade || "--"}%</span></p>
            <p class="card-text mb-1"><strong>Temperatura:</strong> ${data.temperatura || "--"}°C</p>
            <p class="card-text mb-1"><strong>Umidade:</strong> ${data.humidade || "--"}%</p>
            <p class="card-text mb-1"><strong>Campo Elétrico:</strong> ${data.current_mA || "--"} mA</p>
            <p class="card-text mb-1 mt-2"><strong>Razões:</strong></p>
            <ul class="list-group list-group-flush small">${reasonsHtml}</ul>
        </div>
        <div class="card-footer bg-transparent text-muted small d-flex justify-content-between align-items-center">
            <span>Última atualização: ${new Date().toLocaleTimeString()}</span>
            <button class="protocol-button ms-2" type="button">
                <i class="fas fa-play me-1"></i>Iniciar Protocolo
            </button>
        </div>
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

function updateCustomAlert(data, showAll = false, otherCriticalCount = 0) {
  const customHeavyRainAlert = document.getElementById(
    "custom-heavy-rain-alert",
  );
  const verMaisButton = document.getElementById("ver-mais-alertas");

  if (!customHeavyRainAlert) return;

  // Se não houver dados ou não for um array quando showAll=true
  if (
    !data ||
    (showAll && !Array.isArray(data)) ||
    (!showAll && !data.probabilidade)
  ) {
    customHeavyRainAlert.classList.add("d-none");
    if (verMaisButton) verMaisButton.classList.add("d-none");
    return;
  }

  // Processar dados baseado no modo (único alerta ou múltiplos)
  if (showAll) {
    // Filtrar alertas críticos
    const criticalAlerts = data.filter((alert) => alert.probabilidade > 75);

    if (criticalAlerts.length > 0) {
      const firstAlert = criticalAlerts[0];
      customHeavyRainAlert.classList.remove("d-none");

      // Atualizar informações do primeiro alerta
      document.getElementById("alert-area").textContent =
        `${firstAlert.area} (${AREA_NAMES[firstAlert.area] || ""})`;
      document.getElementById("alert-probabilidade").textContent =
        `${firstAlert.probabilidade}%`;
      document.getElementById("alert-umidade").textContent =
        `${firstAlert.humidade}%`;
      document.getElementById("alert-campo-eletrico").textContent =
        `${firstAlert.current_mA || "--"} mA`;

      // Mostrar botão ver mais se houver mais alertas
      if (criticalAlerts.length > 1 && verMaisButton) {
        verMaisButton.classList.remove("d-none");
        document.getElementById("num-alertas").textContent =
          criticalAlerts.length - 1;
      } else if (verMaisButton) {
        verMaisButton.classList.add("d-none");
      }
    } else {
      customHeavyRainAlert.classList.add("d-none");
      if (verMaisButton) verMaisButton.classList.add("d-none");
    }
  } else {
    // Modo alerta único
    if (data.probabilidade > 75) {
      customHeavyRainAlert.classList.remove("d-none");
      document.getElementById("alert-area").textContent =
        `${data.area} (${AREA_NAMES[data.area] || ""})`;
      document.getElementById("alert-probabilidade").textContent =
        `${data.probabilidade}%`;
      document.getElementById("alert-umidade").textContent =
        `${data.humidade}%`;
      document.getElementById("alert-campo-eletrico").textContent =
        `${data.current_mA || "--"} mA`;

      // Mostrar botão ver mais se houver outros alertas críticos
      if (otherCriticalCount > 0 && verMaisButton) {
        verMaisButton.classList.remove("d-none");
        document.getElementById("num-alertas").textContent = otherCriticalCount;
      } else if (verMaisButton) {
        verMaisButton.classList.add("d-none");
      }
    } else {
      customHeavyRainAlert.classList.add("d-none");
      if (verMaisButton) verMaisButton.classList.add("d-none");
    }
  }
}

import * as THREE from "https://unpkg.com/three@0.165.0/build/three.module.js";

const container = document.getElementById("glass-container");

if (container) {
  const width = container.clientWidth;
  const height = container.clientHeight;

  const scene = new THREE.Scene();

  // --- MUDANÇA 1: Usar Câmera Ortográfica para UI ---
  // Este tipo de câmera não tem perspectiva, o que é ideal para um efeito de fundo plano.
  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 10);

  const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
  renderer.setSize(width, height);
  container.appendChild(renderer.domElement);

  // --- MUDANÇA 2: Usar um Plano (PlaneGeometry) em vez de uma esfera ---
  // Isso criará uma "folha de vidro" que cobre toda a navbar.
  const geometry = new THREE.PlaneGeometry(2, 2); // O tamanho (2,2) preenche a câmera ortográfica

  const material = new THREE.MeshPhysicalMaterial({
    // Você pode diminuir os valores para um efeito mais sutil
    roughness: 0.2,
    transmission: 1.0,
    thickness: 1.0, // Uma espessura menor pode ficar melhor em uma navbar
    ior: 1.2, // Um IOR menor causa menos distorção
  });

  const glassPlane = new THREE.Mesh(geometry, material);
  scene.add(glassPlane);

  // --- Lidando com redimensionamento (essencial para a navbar responsiva do Bootstrap) ---
  const resizeObserver = new ResizeObserver((entries) => {
    const entry = entries[0];
    const newWidth = entry.contentRect.width;
    const newHeight = entry.contentRect.height;

    renderer.setSize(newWidth, newHeight);

    // Para a câmera ortográfica, não mexemos no 'aspect'.
    // Podemos ajustar a escala do plano se quisermos, mas geralmente não é necessário.
  });
  resizeObserver.observe(container);

  // Loop de renderização (pode ser mais simples, sem rotação)
  function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
  }

  animate();
}

// Função para buscar e atualizar a previsão de precipitação
async function updatePrecipitationPrediction(areaId = null) {
  try {
    const url = areaId
      ? `/predict_precipitation/${areaId}`
      : "/predict_precipitation/";

    const response = await authenticatedFetch(url);

    if (!response) return; // Authentication failed, redirect handled

    const data = await response.json();

    if (data.status === "success") {
      const precipText = document.getElementById("precipitacao-texto");
      if (precipText) {
        precipText.textContent = data.predicted_precipitation;
      }

      // Update card colors based on precipitation amount
      const card = document.getElementById("card-precipitacao");
      if (card) {
        updateCardColors(
          data.raw_value,
          "card-precipitacao",
          {
            low: 5, // 0-5mm: Normal
            medium: 15, // 5-15mm: Moderado, >15mm: Crítico
          },
          "precipitacao-texto",
        );
      }
    } else if (
      data.status === "error" &&
      data.message === "Usuário não autenticado"
    ) {
      console.log("Usuário não autenticado - redirecionando para login");
      window.location.href = "/login";
      return;
    } else {
      const precipText = document.getElementById("precipitacao-texto");
      if (precipText) {
        precipText.textContent = "-- mm";
      }
    }
  } catch (error) {
    console.error("Erro ao buscar previsão:", error);
    const precipText = document.getElementById("precipitacao-texto");
    if (precipText) {
      precipText.textContent = "-- mm";
    }
  }
}

// Add precipitation update to the data fetch cycle
const originalFetchLatestData = fetchLatestData;
fetchLatestData = async function (areaId = null) {
  await Promise.all([
    originalFetchLatestData(areaId),
    updatePrecipitationPrediction(areaId),
  ]);
};
