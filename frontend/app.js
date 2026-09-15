// Global Chart & File State
let gaugeChart = null;
let selectedBatchFile = null;

// Presets Dictionary
const PRESETS = {
  high_risk: {
    gender: 'Female',
    SeniorCitizen: 'No',
    Partner: 'No',
    Dependents: 'No',
    tenure: 2,
    PhoneService: 'Yes',
    MultipleLines: 'No',
    InternetService: 'Fiber optic',
    OnlineSecurity: 'No',
    OnlineBackup: 'No',
    DeviceProtection: 'No',
    TechSupport: 'No',
    StreamingTV: 'Yes',
    StreamingMovies: 'Yes',
    Contract: 'Month-to-month',
    PaperlessBilling: 'Yes',
    PaymentMethod: 'Electronic check',
    MonthlyCharges: 94.5
  },
  moderate_risk: {
    gender: 'Male',
    SeniorCitizen: 'No',
    Partner: 'Yes',
    Dependents: 'No',
    tenure: 15,
    PhoneService: 'Yes',
    MultipleLines: 'Yes',
    InternetService: 'Fiber optic',
    OnlineSecurity: 'Yes',
    OnlineBackup: 'No',
    DeviceProtection: 'Yes',
    TechSupport: 'No',
    StreamingTV: 'No',
    StreamingMovies: 'Yes',
    Contract: 'Month-to-month',
    PaperlessBilling: 'Yes',
    PaymentMethod: 'Credit card (automatic)',
    MonthlyCharges: 74.0
  },
  loyal: {
    gender: 'Male',
    SeniorCitizen: 'No',
    Partner: 'Yes',
    Dependents: 'Yes',
    tenure: 62,
    PhoneService: 'Yes',
    MultipleLines: 'Yes',
    InternetService: 'DSL',
    OnlineSecurity: 'Yes',
    OnlineBackup: 'Yes',
    DeviceProtection: 'Yes',
    TechSupport: 'Yes',
    StreamingTV: 'No',
    StreamingMovies: 'No',
    Contract: 'Two year',
    PaperlessBilling: 'No',
    PaymentMethod: 'Bank transfer (automatic)',
    MonthlyCharges: 42.5
  }
};

// Update Tenure Slider
function updateTenure(val) {
  const el = document.getElementById('tenure-val');
  if (el) el.textContent = `${val} mo`;
  updateEstimatedTotal();
}

// Update Monthly Charges Slider
function updateMonthly(val) {
  const num = parseFloat(val).toFixed(2);
  const el = document.getElementById('monthly-val');
  if (el) el.textContent = `$${num}`;
  updateEstimatedTotal();
}

// Calculate Estimated Total Charges
function updateEstimatedTotal() {
  const tenureEl = document.getElementById('tenure');
  const monthlyEl = document.getElementById('MonthlyCharges');
  const totalEl = document.getElementById('estimated-total');

  if (tenureEl && monthlyEl && totalEl) {
    const tenure = parseInt(tenureEl.value, 10) || 1;
    const monthly = parseFloat(monthlyEl.value) || 0.0;
    const total = (tenure * monthly).toFixed(2);
    totalEl.textContent = `$${Number(total).toLocaleString()}`;
  }
}

// Handle Internet Service Dropdown Change
function handleInternetChange(val) {
  const internetDependentFields = [
    'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies'
  ];
  if (val === 'No') {
    internetDependentFields.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = 'No internet service';
    });
  } else {
    internetDependentFields.forEach(id => {
      const el = document.getElementById(id);
      if (el && el.value === 'No internet service') el.value = 'No';
    });
  }
}

// Load Presets
function loadPreset(key) {
  const preset = PRESETS[key];
  if (!preset) return;

  const form = document.getElementById('churn-form');
  if (!form) return;

  for (const [field, value] of Object.entries(preset)) {
    const el = form.elements[field];
    if (el) el.value = value;
  }

  updateTenure(preset.tenure);
  updateMonthly(preset.MonthlyCharges);

  // Trigger evaluation
  setTimeout(() => {
    form.dispatchEvent(new Event('submit'));
  }, 50);
}

// Reset Form to Default
function resetForm() {
  const form = document.getElementById('churn-form');
  if (form) form.reset();
  
  updateTenure(12);
  updateMonthly(75);

  const placeholder = document.getElementById('results-placeholder');
  const activeCard = document.getElementById('results-active');
  if (placeholder) placeholder.style.display = 'block';
  if (activeCard) activeCard.style.display = 'none';
}

// Tab Switching
function switchTab(tab) {
  const singleView = document.getElementById('single-view');
  const batchView = document.getElementById('batch-view');
  const tabSingleBtn = document.getElementById('tab-single-btn');
  const tabBatchBtn = document.getElementById('tab-batch-btn');

  if (singleView) singleView.classList.toggle('active', tab === 'single');
  if (batchView) batchView.classList.toggle('active', tab === 'batch');
  if (tabSingleBtn) tabSingleBtn.classList.toggle('active', tab === 'single');
  if (tabBatchBtn) tabBatchBtn.classList.toggle('active', tab === 'batch');
}

// Initialize Gauge Chart
function initOrUpdateGauge(churnPct, riskColor) {
  const canvas = document.getElementById('probabilityGauge');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const safePct = Math.max(0, 100 - churnPct);

  if (gaugeChart) {
    gaugeChart.destroy();
  }

  gaugeChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [churnPct, safePct],
        backgroundColor: [
          riskColor,
          'rgba(255, 255, 255, 0.06)'
        ],
        borderWidth: 0,
        circumference: 240,
        rotation: 240
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '76%',
      animation: {
        animateRotate: true,
        duration: 750
      },
      plugins: {
        tooltip: { enabled: false }
      }
    }
  });

  const pctEl = document.getElementById('gauge-pct');
  if (pctEl) {
    pctEl.textContent = `${churnPct}%`;
    pctEl.style.color = riskColor;
  }
}

// Handle Single Customer Prediction
async function handleSinglePrediction(event) {
  event.preventDefault();
  const form = document.getElementById('churn-form');
  const btn = document.getElementById('predict-btn');
  const btnText = btn ? btn.querySelector('.btn-text') : null;
  const spinner = document.getElementById('btn-spinner');

  const formData = new FormData(form);
  const payload = {};
  formData.forEach((value, key) => {
    if (key === 'tenure') {
      payload[key] = parseInt(value, 10);
    } else if (key === 'MonthlyCharges') {
      payload[key] = parseFloat(value);
    } else {
      payload[key] = value;
    }
  });
  payload['TotalCharges'] = payload['tenure'] * payload['MonthlyCharges'];

  if (btn) btn.disabled = true;
  if (btnText) btnText.textContent = 'Analyzing Subscriber Risk...';
  if (spinner) spinner.style.display = 'block';

  try {
    const response = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'Prediction failed');
    }

    const data = await response.json();
    renderPredictionResult(data);
  } catch (error) {
    alert(`Assessment Error: ${error.message}`);
  } finally {
    if (btn) btn.disabled = false;
    if (btnText) btnText.textContent = 'Evaluate Subscriber Retention Risk';
    if (spinner) spinner.style.display = 'none';
  }
}

// Render Prediction Result
function renderPredictionResult(data) {
  const placeholder = document.getElementById('results-placeholder');
  const activeCard = document.getElementById('results-active');
  if (placeholder) placeholder.style.display = 'none';
  if (activeCard) activeCard.style.display = 'block';

  // Badge
  const badge = document.getElementById('risk-badge');
  if (badge) {
    badge.textContent = data.risk_level;
    badge.style.color = data.risk_color;
    badge.style.backgroundColor = `${data.risk_color}1a`;
    badge.style.border = `1px solid ${data.risk_color}4d`;
  }

  // Timestamp
  const timeEl = document.getElementById('result-time');
  if (timeEl) {
    timeEl.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  // Gauge & Bars
  initOrUpdateGauge(data.churn_probability, data.risk_color);

  const churnStat = document.getElementById('stat-churn-num');
  const retStat = document.getElementById('stat-retention-num');
  const churnBar = document.getElementById('bar-churn');
  const retBar = document.getElementById('bar-retention');

  if (churnStat) churnStat.textContent = `${data.churn_probability}%`;
  if (retStat) retStat.textContent = `${data.retention_probability}%`;
  if (churnBar) churnBar.style.width = `${data.churn_probability}%`;
  if (retBar) retBar.style.width = `${data.retention_probability}%`;

  // Risk Factors
  const factorsList = document.getElementById('factors-list');
  if (factorsList) {
    factorsList.innerHTML = '';
    if (data.risk_factors && data.risk_factors.length > 0) {
      data.risk_factors.forEach(rf => {
        const isSafe = rf.impact.includes('Loyalty') || rf.impact.includes('Retention');
        const item = document.createElement('div');
        item.className = 'factor-item';
        item.innerHTML = `
          <div class="factor-top">
            <span class="factor-title">${rf.factor}</span>
            <span class="impact-tag ${isSafe ? 'safe' : ''}">${rf.impact}</span>
          </div>
          <p class="factor-desc">${rf.detail}</p>
        `;
        factorsList.appendChild(item);
      });
    } else {
      factorsList.innerHTML = '<div class="factor-item"><p class="factor-desc">No dominant risk factors identified.</p></div>';
    }
  }

  // Retention Strategies
  const stratList = document.getElementById('strategies-list');
  if (stratList) {
    stratList.innerHTML = '';
    if (data.retention_strategies && data.retention_strategies.length > 0) {
      data.retention_strategies.forEach(st => {
        const item = document.createElement('div');
        item.className = 'strategy-item';
        item.innerHTML = `
          <div class="strategy-top">
            <span class="strategy-title">${st.title}</span>
            <span class="priority-tag">${st.priority}</span>
          </div>
          <p class="strategy-action">${st.action}</p>
        `;
        stratList.appendChild(item);
      });
    }
  }

  if (window.innerWidth < 1024 && activeCard) {
    activeCard.scrollIntoView({ behavior: 'smooth' });
  }
}

// BATCH FILE HANDLING
function handleFileSelected(event) {
  const file = event.target.files[0];
  if (file) {
    selectedBatchFile = file;
    const nameEl = document.getElementById('file-name-text');
    const badgeEl = document.getElementById('file-selected-badge');
    if (nameEl) nameEl.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    if (badgeEl) badgeEl.style.display = 'flex';
  }
}

// Upload & Score Batch CSV
async function uploadAndScoreBatch() {
  if (!selectedBatchFile) return;

  const btn = document.getElementById('run-batch-btn');
  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Processing Cohort...';
  }

  const formData = new FormData();
  formData.append('file', selectedBatchFile);

  try {
    const response = await fetch('/api/predict-batch', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'Batch processing failed');
    }

    const data = await response.json();
    renderBatchResults(data);
  } catch (err) {
    alert(`Batch Scoring Error: ${err.message}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = 'Run Bulk Prediction';
    }
  }
}

// Render Batch Results
function renderBatchResults(data) {
  const wrap = document.getElementById('batch-results-wrap');
  const totalEl = document.getElementById('batch-total');
  const highRiskEl = document.getElementById('batch-high-risk');
  const rateEl = document.getElementById('batch-rate');
  const tbody = document.getElementById('batch-table-body');

  if (wrap) wrap.style.display = 'block';
  if (totalEl) totalEl.textContent = data.total_processed;
  if (highRiskEl) highRiskEl.textContent = data.high_risk_count;
  if (rateEl) rateEl.textContent = `${data.churn_rate_predicted}%`;

  if (tbody) {
    tbody.innerHTML = '';
    data.predictions.forEach(p => {
      const tr = document.createElement('tr');
      const isHigh = p.risk_level === 'High Risk';
      const isMod = p.risk_level === 'Moderate Risk';
      const color = isHigh ? 'var(--risk-high)' : (isMod ? 'var(--risk-warning)' : 'var(--risk-low)');
      const bg = isHigh ? 'var(--risk-high-bg)' : (isMod ? 'var(--risk-warning-bg)' : 'var(--risk-low-bg)');
      
      tr.innerHTML = `
        <td style="font-family: 'JetBrains Mono', monospace; color: var(--text-secondary);">#${p.row_id}</td>
        <td><strong>${p.churn_prediction}</strong></td>
        <td style="font-family: 'JetBrains Mono', monospace;">${p.churn_probability}%</td>
        <td><span style="color: ${color}; background: ${bg}; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 0.75rem;">${p.risk_level}</span></td>
      `;
      tbody.appendChild(tr);
    });
  }
}

// Drag and drop listeners
function setupDragAndDrop() {
  const dropzone = document.getElementById('csv-dropzone');
  if (!dropzone) return;

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.style.borderColor = 'var(--telecom-blue)';
      dropzone.style.backgroundColor = 'var(--telecom-blue-subtle)';
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.style.borderColor = '';
      dropzone.style.backgroundColor = '';
    }, false);
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length) {
      handleFileSelected({ target: { files: files } });
    }
  }, false);
}

// Initial setup on window load
window.addEventListener('DOMContentLoaded', () => {
  updateTenure(12);
  updateMonthly(75);
  setupDragAndDrop();
});
