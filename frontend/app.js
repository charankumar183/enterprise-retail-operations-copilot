// Enterprise AI Retail Operations Assistant - Frontend Controller
const API_BASE = "/api/v1";

let currentUser = {
  username: "manager",
  role: "Store Manager",
  fullName: "Marcus Vance"
};

let authToken = "";

async function authenticateUser(username = "manager", password = "admin123") {
  try {
    const res = await fetch(`${API_BASE}/auth/json-login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    if (res.ok) {
      const data = await res.json();
      authToken = data.access_token;
      return true;
    }
  } catch (err) {
    console.error("Authentication error:", err);
  }
  return false;
}

let currentSessionId = "session_" + Math.random().toString(36).substring(2, 9);
let inventoryChartInstance = null;
let stockoutChartInstance = null;
let recentCitations = [];

// Initialize on document load
document.addEventListener("DOMContentLoaded", async () => {
  await authenticateUser("manager", "admin123");
  loadInventoryDashboard();
  loadProductsList();
  loadDocumentsList();
  loadAuditLogs();
});

// Tab Switcher
function switchTab(tabId) {
  document.querySelectorAll(".nav-item").forEach(item => item.classList.remove("active"));
  document.querySelectorAll(".content-panel").forEach(panel => panel.classList.remove("active"));

  const targetPanel = document.getElementById(`tab-${tabId}`);
  if (targetPanel) {
    targetPanel.classList.add("active");
  }

  // Highlight nav item
  const navItems = document.querySelectorAll(".nav-item");
  const tabMap = { chat: 0, inventory: 1, products: 2, documents: 3, citations: 4, reports: 5, admin: 6 };
  if (tabMap[tabId] !== undefined && navItems[tabMap[tabId]]) {
    navItems[tabMap[tabId]].classList.add("active");
  }

  const titles = {
    chat: "AI Retail Operations Assistant",
    inventory: "Live Inventory & Supply Chain Overview",
    products: "Enterprise Product Master Catalog",
    documents: "Retail Knowledge Ingestion & Document Management",
    citations: "Audit-Grade Source Provenance & Citations",
    reports: "Operations Report Generation Center",
    admin: "System Administration & Benchmark Evaluation"
  };
  document.getElementById("pageTitle").textContent = titles[tabId] || "AI Retail Assistant";

  if (tabId === "inventory") {
    loadInventoryDashboard();
  } else if (tabId === "documents") {
    loadDocumentsList();
  } else if (tabId === "admin") {
    loadAuditLogs();
  }
}

async function changeRolePersona(newRole) {
  const roleUsers = {
    "Store Manager": { username: "manager", fullName: "Marcus Vance" },
    "Supply Chain Analyst": { username: "analyst", fullName: "Elena Rostova" },
    "Inventory Planner": { username: "planner", fullName: "David Chen" },
    "Category Manager": { username: "category", fullName: "Sarah Jenkins" },
    "Procurement Manager": { username: "procurement", fullName: "Robert Martinez" },
    "Administrator": { username: "admin", fullName: "Chief Operations Officer" }
  };

  const userMeta = roleUsers[newRole] || { username: "manager", fullName: "Marcus Vance" };
  currentUser.role = newRole;
  currentUser.fullName = userMeta.fullName;
  currentUser.username = userMeta.username;

  await authenticateUser(userMeta.username, "admin123");

  document.getElementById("currentUserLabel").textContent = currentUser.fullName;
  document.getElementById("currentRoleBadge").textContent = newRole;
  document.getElementById("roleSelector").value = newRole;

  appendChatMessage("assistant", `Authenticated and switched active persona to **${newRole}** (${currentUser.fullName}). Signed JWT token acquired for backend API authorization.`);
}

// Quick Sample Query
function applySampleQuery(text) {
  document.getElementById("chatQueryInput").value = text;
  sendChatMessage();
}

// Clear Chat
function clearChat() {
  currentSessionId = "session_" + Math.random().toString(36).substring(2, 9);
  document.getElementById("chatMessages").innerHTML = `
    <div class="msg-wrapper msg-assistant">
      <div class="msg-bubble">
        Session history cleared. Ready for your next retail operations or supply chain query.
      </div>
      <div class="msg-meta">Enterprise Retail Copilot • Fresh Session</div>
    </div>
  `;
  document.getElementById("activeIntentBadge").textContent = "Intent: Auto-Routing";
}

// Chat Send & Render
async function sendChatMessage() {
  const inputEl = document.getElementById("chatQueryInput");
  const query = inputEl.value.trim();
  if (!query) return;

  // Render user message
  appendChatMessage("user", query);
  inputEl.value = "";

  const sendBtn = document.getElementById("btnSendChat");
  sendBtn.disabled = true;
  sendBtn.innerHTML = "Processing...";

  // Prepare metadata filters
  const filterCat = document.getElementById("filterCategory").value;
  const filterStore = document.getElementById("filterStore").value;
  const filterWh = document.getElementById("filterWarehouse").value;
  const filterDoc = document.getElementById("filterDocType").value;

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(authToken ? { "Authorization": `Bearer ${authToken}` } : {})
      },
      body: JSON.stringify({
        query: query,
        conversation_id: currentSessionId,
        filter_category: filterCat || null,
        filter_store: filterStore || null,
        filter_warehouse: filterWh || null,
        filter_doc_type: filterDoc || null
      })
    });

    if (!res.ok) {
      throw new Error(`Server returned ${res.status}`);
    }

    const data = await res.json();
    document.getElementById("activeIntentBadge").textContent = `Route: ${data.route_taken}`;

    // Store citations
    if (data.citations && data.citations.length > 0) {
      recentCitations.push(...data.citations);
      renderRecentCitations();
    }

    // Render assistant response
    appendChatMessage("assistant", data.response, data);

  } catch (err) {
    appendChatMessage("assistant", `⚠️ **Error communicating with AI Copilot:** ${err.message}. Please check if the FastAPI backend is running.`);
  } finally {
    sendBtn.disabled = false;
    sendBtn.innerHTML = "Send ➔";
  }
}

function appendChatMessage(role, text, metaData = null) {
  const container = document.getElementById("chatMessages");
  const wrapper = document.createElement("div");
  wrapper.className = `msg-wrapper msg-${role}`;

  let formattedText = text
    .replace(/\n\n/g, "<br><br>")
    .replace(/\n/g, "<br>")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/### (.*?)(<br>|$)/g, "<h3 style='font-size:15px;margin:6px 0;'>$1</h3>")
    .replace(/#### (.*?)(<br>|$)/g, "<h4 style='font-size:13.5px;margin:4px 0;'>$1</h4>")
    .replace(/`([^`]+)`/g, "<code style='background:#e2e8f0;padding:2px 4px;border-radius:4px;'>$1</code>");

  let citationsHtml = "";
  if (metaData && metaData.citations && metaData.citations.length > 0) {
    citationsHtml = `
      <div class="citations-box">
        <strong>Verified Source Citations (${metaData.citations.length}):</strong>
        ${metaData.citations.map(c => `
          <div class="citation-item">
            <span>📄 <strong>${c.document_name}</strong> — ${c.section_reference} (Page ${c.page_number})</span>
            <span class="badge badge-success">Confidence: ${(c.confidence_score * 100).toFixed(0)}%</span>
          </div>
        `).join("")}
      </div>
    `;
  }

  let sqlHtml = "";
  if (metaData && metaData.sql_query) {
    sqlHtml = `
      <div style="margin-top:8px;font-size:11px;color:#475569;background:#e2e8f0;padding:6px 8px;border-radius:4px;font-family:monospace;">
        🗄️ <strong>Executed SQL Query:</strong> ${metaData.sql_query}
      </div>
    `;
  }

  let latencyText = metaData ? `• Latency: ${metaData.response_latency_ms}ms • Intent: ${metaData.detected_intent}` : "";

  wrapper.innerHTML = `
    <div class="msg-bubble">
      ${formattedText}
      ${citationsHtml}
      ${sqlHtml}
    </div>
    <div class="msg-meta">
      <span>${role === "user" ? currentUser.fullName : "Enterprise AI Copilot"}</span>
      <span>${latencyText}</span>
    </div>
  `;

  container.appendChild(wrapper);
  container.scrollTop = container.scrollHeight;
}

// Render Recent Citations
function renderRecentCitations() {
  const container = document.getElementById("citationsFullList");
  if (!recentCitations || recentCitations.length === 0) return;

  container.innerHTML = recentCitations.map((c, idx) => `
    <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px;margin-bottom:10px;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <span style="font-weight:700;font-size:14px;color:#1e3a8a;">#${idx+1} — ${c.document_name}</span>
        <span class="badge badge-success">Confidence Score: ${(c.confidence_score*100).toFixed(0)}%</span>
      </div>
      <div style="font-size:12.5px;color:#334155;margin:4px 0;"><strong>Section:</strong> ${c.section_reference} | <strong>Page:</strong> ${c.page_number}</div>
      ${c.snippet ? `<div style="font-size:12px;color:#64748b;background:#fff;padding:8px;border-radius:4px;border:1px solid #cbd5e1;margin-top:6px;">"${c.snippet}"</div>` : ""}
    </div>
  `).join("");
}

// Load Inventory Overview & Charts
async function loadInventoryDashboard() {
  try {
    const res = await fetch(`${API_BASE}/inventory/overview`);
    const data = await res.json();

    document.getElementById("invTotalSkus").textContent = data.total_products;
    document.getElementById("invLowStock").textContent = data.low_stock_count;
    document.getElementById("invOutOfStock").textContent = data.out_of_stock_count;
    document.getElementById("invActiveHubs").textContent = data.warehouses_active;

    const tbody = document.getElementById("inventoryTableBody");
    tbody.innerHTML = data.inventory_items.map(i => {
      let badgeClass = i.status === "In Stock" ? "badge-success" : (i.status === "Low Stock" ? "badge-warning" : "badge-danger");
      return `
        <tr>
          <td><strong>${i.product_id}</strong></td>
          <td>${i.product_name}</td>
          <td>${i.location_type.toUpperCase()}</td>
          <td><code>${i.location_id}</code></td>
          <td><strong>${i.quantity_on_hand}</strong></td>
          <td>${i.quantity_reserved}</td>
          <td>${i.reorder_threshold}</td>
          <td><span class="badge ${badgeClass}">${i.status}</span></td>
        </tr>
      `;
    }).join("");

    renderInventoryCharts(data.inventory_items);

  } catch (err) {
    console.error("Error loading inventory:", err);
  }
}

function renderInventoryCharts(items) {
  // Chart 1: Warehouse Stock Distribution
  const whItems = items.filter(i => i.location_type === "warehouse");
  const whLabels = [...new Set(whItems.map(i => i.location_id))];
  const whStockSums = whLabels.map(loc => {
    return whItems.filter(i => i.location_id === loc).reduce((sum, item) => sum + item.quantity_on_hand, 0);
  });

  const ctx1 = document.getElementById("inventoryStockChart").getContext("2d");
  if (inventoryChartInstance) inventoryChartInstance.destroy();
  inventoryChartInstance = new Chart(ctx1, {
    type: "bar",
    data: {
      labels: whLabels,
      datasets: [{
        label: "Available Warehouse Units",
        data: whStockSums,
        backgroundColor: ["#3b82f6", "#0ea5e9", "#6366f1", "#14b8a6"]
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } }
    }
  });

  // Chart 2: Status Donut
  const inStock = items.filter(i => i.status === "In Stock").length;
  const lowStock = items.filter(i => i.status === "Low Stock").length;
  const outStock = items.filter(i => i.status === "Out of Stock").length;

  const ctx2 = document.getElementById("stockoutDonutChart").getContext("2d");
  if (stockoutChartInstance) stockoutChartInstance.destroy();
  stockoutChartInstance = new Chart(ctx2, {
    type: "doughnut",
    data: {
      labels: ["In Stock", "Low Stock", "Out of Stock"],
      datasets: [{
        data: [inStock, lowStock, outStock],
        backgroundColor: ["#10b981", "#f59e0b", "#ef4444"]
      }]
    },
    options: { responsive: true }
  });
}

// Product Search
async function loadProductsList(searchQuery = "", category = "") {
  try {
    let url = `${API_BASE}/products`;
    const params = [];
    if (searchQuery) params.push(`search=${encodeURIComponent(searchQuery)}`);
    if (category) params.push(`category=${encodeURIComponent(category)}`);
    if (params.length > 0) url += `?${params.join("&")}`;

    const res = await fetch(url);
    const data = await res.json();

    const tbody = document.getElementById("productTableBody");
    tbody.innerHTML = data.map(p => `
      <tr>
        <td><strong>${p.product_id}</strong></td>
        <td>${p.name}</td>
        <td>${p.category}</td>
        <td>${p.department}</td>
        <td>${p.brand}</td>
        <td>$${p.unit_price.toFixed(2)}</td>
        <td><code>${p.supplier_id}</code></td>
        <td>${p.lead_time_days} days</td>
        <td>${p.min_reorder_level} units</td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Error loading products:", err);
  }
}

function searchProducts() {
  const query = document.getElementById("productSearchInput").value.trim();
  const cat = document.getElementById("productCategoryFilter").value;
  loadProductsList(query, cat);
}

// Document Management
async function loadDocumentsList() {
  try {
    const res = await fetch(`${API_BASE}/documents`);
    const data = await res.json();

    const tbody = document.getElementById("documentTableBody");
    tbody.innerHTML = data.map(d => `
      <tr>
        <td>${d.id}</td>
        <td><strong>${d.filename}</strong></td>
        <td><span class="badge badge-info">${d.file_type.toUpperCase()}</span></td>
        <td>${d.doc_type}</td>
        <td>${d.version}</td>
        <td><strong>${d.total_chunks}</strong></td>
        <td>${(d.file_size_bytes / 1024).toFixed(1)} KB</td>
        <td><span class="badge badge-success">${d.status}</span></td>
        <td>
          <button class="btn btn-secondary" style="padding:2px 8px;font-size:11px;" onclick="deleteDocumentRecord(${d.id})">Delete</button>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Error loading documents:", err);
  }
}

async function handleDocumentUpload(e) {
  e.preventDefault();
  const fileInput = document.getElementById("uploadFile");
  if (!fileInput.files || fileInput.files.length === 0) return;

  const btn = document.getElementById("btnUploadSubmit");
  const feedback = document.getElementById("uploadFeedback");
  btn.disabled = true;
  btn.textContent = "Parsing & Indexing...";
  feedback.style.display = "block";
  feedback.textContent = "Uploading, executing chunking, embeddings and ChromaDB indexation...";
  feedback.style.color = "#3b82f6";

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  formData.append("doc_type", document.getElementById("uploadDocType").value);
  formData.append("department", document.getElementById("uploadDepartment").value);
  formData.append("version", document.getElementById("uploadVersion").value);

  try {
    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: "POST",
      headers: {
        ...(authToken ? { "Authorization": `Bearer ${authToken}` } : {})
      },
      body: formData
    });
    const result = await res.json();

    if (!res.ok) throw new Error(result.detail || "Upload failed");

    feedback.textContent = `✅ ${result.message}`;
    feedback.style.color = "#10b981";
    fileInput.value = "";
    loadDocumentsList();
  } catch (err) {
    feedback.textContent = `❌ Upload Error: ${err.message}`;
    feedback.style.color = "#ef4444";
  } finally {
    btn.disabled = false;
    btn.textContent = "Upload & Index";
  }
}

async function deleteDocumentRecord(docId) {
  if (!confirm(`Are you sure you want to delete Document ID ${docId}? This will remove its chunks from ChromaDB.`)) return;
  try {
    const res = await fetch(`${API_BASE}/documents/${docId}`, {
      method: "DELETE",
      headers: {
        ...(authToken ? { "Authorization": `Bearer ${authToken}` } : {})
      }
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      alert(`Delete Failed (${res.status}): ${err.detail || "Access Denied. Only Administrator can delete documents."}`);
      return;
    }
    loadDocumentsList();
  } catch (err) {
    alert("Delete failed: " + err.message);
  }
}

// Report Generator
async function generateReport() {
  const repType = document.getElementById("reportTypeSelect").value;
  const targetId = document.getElementById("reportTargetId").value.trim() || "STORE-105";

  try {
    const res = await fetch(`${API_BASE}/reports/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(authToken ? { "Authorization": `Bearer ${authToken}` } : {})
      },
      body: JSON.stringify({ report_type: repType, target_id: targetId })
    });
    const data = await res.json();

    const card = document.getElementById("generatedReportCard");
    card.style.display = "block";

    document.getElementById("reportTitle").textContent = data.title;
    document.getElementById("reportTimestamp").textContent = `Generated: ${new Date(data.generated_at).toLocaleString()}`;
    document.getElementById("reportSummaryText").textContent = data.summary;

    const metricsGrid = document.getElementById("reportKeyMetricsGrid");
    metricsGrid.innerHTML = Object.entries(data.key_metrics).map(([k, v]) => `
      <div class="card" style="padding:12px;">
        <div class="stat-label">${k.replace(/_/g, " ")}</div>
        <div style="font-size:18px;font-weight:700;color:#1e3a8a;">${typeof v === "number" ? v.toLocaleString() : v}</div>
      </div>
    `).join("");

    const recsList = document.getElementById("reportRecommendationsList");
    recsList.innerHTML = data.recommendations.map(r => `<li>${r}</li>`).join("");

    const dlBtn = document.getElementById("btnDownloadReport");
    dlBtn.href = data.download_url;
    dlBtn.textContent = `Download ${data.report_id}.json`;

  } catch (err) {
    alert("Report generation error: " + err.message);
  }
}

// Admin Audit Logs
async function loadAuditLogs() {
  try {
    const res = await fetch(`${API_BASE}/feedback/audit-logs?limit=25`);
    const logs = await res.json();

    const tbody = document.getElementById("auditTableBody");
    tbody.innerHTML = logs.map(l => `
      <tr>
        <td>${l.id}</td>
        <td><strong>${l.username}</strong> (${l.user_role})</td>
        <td>${l.query_text.substring(0, 45)}...</td>
        <td><span class="route-pill">${l.route_taken}</span></td>
        <td>${l.response_latency_ms} ms</td>
        <td><code>${l.sql_query ? l.sql_query.substring(0, 30) + "..." : "N/A"}</code></td>
        <td>${new Date(l.created_at).toLocaleTimeString()}</td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Error loading audit logs:", err);
  }
}

// Run Benchmark Evaluation
async function runEvaluationBenchmark() {
  try {
    const res = await fetch(`${API_BASE}/evaluation/benchmark`);
    const data = await res.json();

    const tbody = document.getElementById("evaluationTableBody");
    tbody.innerHTML = data.models.map(m => `
      <tr>
        <td><strong>${m.model_name}</strong></td>
        <td><span class="badge badge-success">${(m.retrieval_precision * 100).toFixed(1)}%</span></td>
        <td><span class="badge badge-success">${(m.retrieval_recall * 100).toFixed(1)}%</span></td>
        <td>${(m.response_accuracy * 100).toFixed(1)}%</td>
        <td>${m.avg_latency_ms.toFixed(1)} ms</td>
        <td><span class="badge badge-info">${(m.hallucination_rate * 100).toFixed(1)}%</span></td>
        <td>${m.mrr.toFixed(3)}</td>
      </tr>
    `).join("");

    alert(`Benchmark Complete!\nWinner: ${data.winner_model}\n${data.summary_findings}`);
  } catch (err) {
    alert("Benchmark failed: " + err.message);
  }
}
