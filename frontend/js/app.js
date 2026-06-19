/*
================================================================
   CITIZEN CYBER SHIELD - JS APP INTERACTION CONTROLLER
================================================================
*/

const API_BASE_URL = "http://localhost:8000";

// --- Shared Utility: Terminal Logger ---
function initTerminal(elementId) {
  const term = document.getElementById(elementId);
  if (!term) return null;
  term.innerHTML = `<div class="terminal-line success">SOC console ready for inputs...</div>`;
  
  return {
    log: (msg, type = '') => {
      const line = document.createElement('div');
      line.className = `terminal-line ${type}`;
      line.textContent = msg;
      term.appendChild(line);
      term.scrollTop = term.scrollHeight;
    },
    clear: () => {
      term.innerHTML = '';
    }
  };
}

// --- SMS Scam Detection ---
async function runSMSAnalysis() {
  const text = document.getElementById('sms-input').value.trim();
  const resultsDiv = document.getElementById('sms-results');
  
  if (!text) {
    alert("Please input a message first.");
    return;
  }
  
  const logger = initTerminal('sms-terminal');
  resultsDiv.style.display = 'none';
  
  logger.log("Establishing secure connection to AI inference server...");
  logger.log("Tokenizing text payload...");
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/scan-sms`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message: text })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP Error status: ${response.status}`);
    }
    
    const data = await response.json();
    
    logger.log("Inference complete. Parsing classifications...", "success");
    logger.log(`Target class resolved: ${data.category}`, data.is_scam ? 'error' : 'success');
    logger.log(`Probability confidence parameter: ${data.confidence}`, 'success');
    
    // Render Results
    document.getElementById('sms-score').textContent = data.risk_score;
    document.getElementById('sms-severity').textContent = data.category.toUpperCase();
    
    let severityColor = 'var(--neon-green)';
    if (data.severity === 'CRITICAL') {
      severityColor = 'var(--neon-red)';
    } else if (data.severity === 'MEDIUM') {
      severityColor = 'var(--neon-purple-bright)';
    }
    
    document.getElementById('sms-severity').style.color = severityColor;
    document.getElementById('sms-severity').style.textShadow = `0 0 10px ${severityColor}`;
    
    const findingsList = document.getElementById('sms-findings');
    findingsList.innerHTML = `<li>📈 Model Classifier Confidence: ${data.confidence}</li>` + 
      (data.explainability && data.explainability.length > 0
        ? data.explainability.map(r => `<li>⚠️ ${r}</li>`).join('')
        : `<li>✅ No critical threat indicators found in standard database logs.</li>`);
    
    resultsDiv.style.display = 'block';
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
    
  } catch (error) {
    logger.log(`CRITICAL: Model server lookup failed: ${error.message}`, 'error');
    alert("Threat Server connection refused. Verify backend server.py is running!");
  }
}

// --- URL Phishing Analyzer ---
async function runURLAnalysis() {
  const url = document.getElementById('url-input').value.trim();
  const resultsDiv = document.getElementById('url-results');
  
  if (!url) {
    alert("Please input a valid URL.");
    return;
  }
  
  const logger = initTerminal('url-terminal');
  resultsDiv.style.display = 'none';
  
  logger.log(`Registering lookup target: ${url}`);
  logger.log("Extracting domain lexical metrics...");
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/scan-url`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ url: url })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP Error status: ${response.status}`);
    }
    
    const data = await response.json();
    
    logger.log("DNS & redirect mappings processed successfully.", "success");
    logger.log("Evaluating features against Random Forest threat dataset...", "success");
    logger.log(`Risk classification: ${data.severity}`, data.severity === 'SAFE' ? 'success' : 'error');
    
    // Render Results
    document.getElementById('url-score').textContent = data.risk_score;
    document.getElementById('url-severity').textContent = data.severity;
    
    let severityColor = 'var(--neon-green)';
    if (data.severity === 'PHISHING HAZARD') {
      severityColor = 'var(--neon-red)';
    } else if (data.severity === 'SUSPICIOUS') {
      severityColor = 'var(--neon-purple-bright)';
    }
    
    document.getElementById('url-severity').style.color = severityColor;
    document.getElementById('url-severity').style.textShadow = `0 0 10px ${severityColor}`;
    
    // SSL & Age features
    const feats = data.features;
    document.getElementById('url-ssl').textContent = feats.IsHTTPS === 1 ? "SECURE (HTTPS)" : "UNSECURE (HTTP)";
    document.getElementById('url-ssl').style.color = feats.IsHTTPS === 1 ? "var(--neon-green)" : "var(--neon-red)";
    document.getElementById('url-age').textContent = `Entropy: ${feats.Entropy.toFixed(2)} | Subdomains: ${feats.NoOfSubDomain}`;
    
    const findingsList = document.getElementById('url-findings');
    if (data.findings && data.findings.length > 0) {
      findingsList.innerHTML = data.findings.map(f => `<li>⚠️ ${f}</li>`).join('');
    } else {
      findingsList.innerHTML = `<li>✅ Domain parameters match trusted SSL credentials.</li>`;
    }
    
    resultsDiv.style.display = 'block';
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
    
  } catch (error) {
    logger.log(`CRITICAL: Feature extraction server failed: ${error.message}`, 'error');
    alert("Connection to backend server.py refused!");
  }
}

// --- OCR Screenshot Scanner ---
async function triggerOCRScan() {
  const fileInput = document.getElementById('screenshot-upload');
  const resultsDiv = document.getElementById('screenshot-results');
  
  if (!fileInput.files || fileInput.files.length === 0) {
    alert("Please upload a file first.");
    return;
  }
  
  const logger = initTerminal('ocr-terminal');
  resultsDiv.style.display = 'none';
  
  const file = fileInput.files[0];
  logger.log(`Mounting screenshot asset: ${file.name}`);
  logger.log("Uploading file to OCR preprocessing engine...");
  
  const formData = new FormData();
  formData.append("file", file);
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/scan-screenshot`, {
      method: "POST",
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`HTTP Error status: ${response.status}`);
    }
    
    const data = await response.json();
    
    logger.log("OpenCV preprocessing contrast & deskew filters applied.", "success");
    logger.log("EasyOCR text segment lines extracted.", "success");
    
    const sms = data.sms_report;
    logger.log(`AI categorization completed: ${sms.category}`, sms.is_scam ? 'error' : 'success');
    
    // Render Results
    document.getElementById('ocr-text-preview').textContent = data.extracted_text || "(No text found)";
    
    document.getElementById('ocr-score').textContent = sms.risk_score;
    document.getElementById('ocr-severity').textContent = sms.category.toUpperCase();
    
    let severityColor = 'var(--neon-green)';
    if (sms.severity === 'CRITICAL') {
      severityColor = 'var(--neon-red)';
    } else if (sms.severity === 'MEDIUM') {
      severityColor = 'var(--neon-purple-bright)';
    }
    
    document.getElementById('ocr-severity').style.color = severityColor;
    document.getElementById('ocr-severity').style.textShadow = `0 0 10px ${severityColor}`;
    
    const findingsList = document.getElementById('ocr-findings');
    findingsList.innerHTML = `<li>📈 Model Classifier Confidence: ${sms.confidence}</li>` + 
      (sms.explainability && sms.explainability.length > 0
        ? sms.explainability.map(e => `<li>⚠️ ${e}</li>`).join('')
        : `<li>✅ Extracted content is free of verified threat structures.</li>`);
    
    resultsDiv.style.display = 'block';
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
    
  } catch (error) {
    logger.log(`CRITICAL: OCR pipeline invocation failed: ${error.message}`, 'error');
    alert("Connection to backend server.py refused!");
  }
}

// --- Complaint Template Generator ---
async function generateComplaintText(event) {
  if (event) event.preventDefault();
  
  const name = document.getElementById('victim-name').value;
  const scamType = document.getElementById('scam-type').value;
  const date = document.getElementById('scam-date').value;
  const platform = document.getElementById('scam-platform').value;
  const targetInfo = document.getElementById('scam-target-info').value;
  const amount = document.getElementById('scam-amount').value || '0.00';
  const desc = document.getElementById('scam-description').value;

  const formData = new FormData();
  formData.append("name", name);
  formData.append("scam_type", scamType);
  formData.append("date", date);
  formData.append("platform", platform);
  formData.append("target_info", targetInfo);
  formData.append("amount", amount);
  formData.append("description", desc);
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/generate-complaint`, {
      method: "POST",
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`HTTP Error status: ${response.status}`);
    }
    
    const data = await response.json();
    
    document.getElementById('complaint-output').value = data.complaint_text;
    document.getElementById('complaint-results').style.display = 'block';
    document.getElementById('complaint-results').scrollIntoView({ behavior: 'smooth' });
    
  } catch (error) {
    alert("Complaint generator failed: " + error.message);
  }
}

function copyComplaint() {
  const txtarea = document.getElementById('complaint-output');
  txtarea.select();
  document.execCommand('copy');
  
  const copyBtn = document.getElementById('btn-copy');
  const oldText = copyBtn.textContent;
  copyBtn.textContent = "COPIED TO CLIPBOARD!";
  copyBtn.style.color = "var(--neon-green)";
  copyBtn.style.borderColor = "var(--neon-green)";
  
  setTimeout(() => {
    copyBtn.textContent = oldText;
    copyBtn.style.color = "";
    copyBtn.style.borderColor = "";
  }, 2000);
}

function printComplaint() {
  const content = document.getElementById('complaint-output').value;
  const printWindow = window.open('', '_blank');
  printWindow.document.write(`<pre style="font-family: monospace; padding: 40px; background: white; color: black; font-size: 14px; line-height: 1.5; white-space: pre-wrap;">${content}</pre>`);
  printWindow.document.close();
  printWindow.print();
}

// --- Dynamic Recovery Plan Loader ---
async function loadRecoveryPlan() {
  const threatType = document.getElementById('recovery-threat-type').value;
  const bankName = document.getElementById('recovery-bank').value;
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/recovery-plan`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ threat_type: threatType, bank_name: bankName })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP Error status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Render header
    document.getElementById('recovery-steps-title').textContent = `${threatType.toUpperCase()} MITIGATION PLAN`;
    
    // Render checklists
    const listContainer = document.getElementById('recovery-steps-list');
    if (data.steps && data.steps.length > 0) {
      listContainer.innerHTML = data.steps.map((step, idx) => `
        <li>
          <label class="checkbox-container" style="padding-top: 2px;">
            <input type="checkbox" id="rec-chk-${idx}" onchange="updateRecoveryProgress()">
            <span class="custom-checkbox"></span>
          </label>
          <div>${step}</div>
        </li>
      `).join('');
    } else {
      listContainer.innerHTML = '<li>No actions registered.</li>';
    }
    
    // Render Bank helplines & web
    document.getElementById('recovery-bank-helpline').textContent = data.bank.helpline || "1930 / Contact Branch";
    document.getElementById('recovery-bank-website').textContent = `${bankName} Website Portal`;
    document.getElementById('recovery-bank-website').href = data.bank.website || "https://cybercrime.gov.in";
    
    // Trigger reset check states
    updateRecoveryProgress();
    
  } catch (error) {
    alert("Failed to load recovery plan: " + error.message);
  }
}

// --- Recovery Checklist Progress Logic ---
function updateRecoveryProgress() {
  const checkboxes = document.querySelectorAll('.checklist-group input[type="checkbox"]');
  const pctText = document.getElementById('recovery-pct-text');
  const bar = document.getElementById('recovery-progress-bar');
  
  if (checkboxes.length === 0) {
    if (bar) bar.style.width = '0%';
    if (pctText) pctText.textContent = "0% Actions Secured";
    return;
  }
  
  const checked = document.querySelectorAll('.checklist-group input[type="checkbox"]:checked');
  const pct = Math.round((checked.length / checkboxes.length) * 100);
  
  if (bar) bar.style.width = `${pct}%`;
  if (pctText) pctText.textContent = `${pct}% Actions Secured`;
  
  checkboxes.forEach(chk => {
    const parentLi = chk.closest('li');
    if (chk.checked) {
      parentLi.style.opacity = '0.5';
      parentLi.style.textDecoration = 'line-through';
    } else {
      parentLi.style.opacity = '1';
      parentLi.style.textDecoration = 'none';
    }
  });
}
