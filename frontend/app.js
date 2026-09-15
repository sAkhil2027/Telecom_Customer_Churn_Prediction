// Global Chart Instance
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
  document.getElementById('tenure-val').textContent = `${val} mo`;
  updateEstimatedTotal();
}

// Update Monthly Charges Slider
function updateMonthly(val) {
  const num = parseFloat(val).toFixed(2);
  document.getElementById('monthly-val').textContent = `$${num}`;
  updateEstimatedTotal();
}

// Calculate Estimated Total Charges
function updateEstimatedTotal() {
  const tenure = parseInt(document.getElementById('tenure').value, 10);
  const monthly = parseFloat(document.getElementById('MonthlyCharges').value);
  const total = (tenure * monthly).toFixed(2);
  document.getElementById('estimated-total').textContent = `$${Number(total).toLocaleString()}`;
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
  for (const [field, value] of Object.entries(preset)) {
    const el = form.elements[field];
    if (el) {
      el.value = value;
    }
  }

  updateTenure(preset.tenure);
  updateMonthly(preset.MonthlyCharges);

  // Automatically trigger prediction on preset load for smooth user experience
  setTimeout(() => {
    document.getElementById('churn-form').dispatchEvent(new Event('submit'));
  }, 100);
}

// Reset Form to Default
function resetForm() {
  const form = document.getElementById('churn-form');
  form.reset();
  updateTenure(12);
  updateMonthly(75);
  document.getElementById('results-placeholder').style.display = 'block';
  document.getElementById('results-active').style.display = 'none';
}

// Tab Switching
function switchTab(tab) {
  document.getElementById('single-view').classList.toggle('active', tab === 'single');
  document.getElementById('batch-view').classList.toggle('active', tab === 'batch');
  document.getElementById('tab-single-btn').classList.toggle('active', tab === 'single');
  document.getElementById('tab-batch-btn').classList.toggle('active', tab === 'batch');
}

// Initialize Gauge Chart
function initOrUpdateGauge(churnPct, riskColor) {
  const canvas = document.getElementById('probabilityGauge');
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
          'rgba(255, 255, 255, 0.08)'
        ],
        borderWidth: 0,
        circumference: 240,
        rotation: 240
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '78%',
      animation: {
        animateRotate: true,
        duration: 900
      },
      plugins: {
        tooltip: { enabled: false }
      }
    }
  });

  // Update center number
  const pctEl = document.getElementById('gauge-pct');
  pctEl.textContent = `${churnPct}%`;
  pctEl.style.color = riskColor;
}

// Handle Single Customer Prediction
async function handleSinglePrediction(event) {
  event.preventDefault();
  const form = document.getElementById('churn-form');
  const btn = document.getElementById('predict-btn');
  const btnText = btn.querySelector('.btn-text');
  const spinner = document.getElementById('btn-spinner');

  // Prepare Payload
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

  // Loading State
  btn.disabled = true;
  btnText.textContent = 'Analyzing Churn Probability...';
  spinner.style.display = 'block';

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
    alert(`Prediction Error: ${error.message}`);
  } finally {
    btn.disabled = false;
    btnText.textContent = 'Run Churn Prediction';
    spinner.style.display = 'none';
  }
}

// Render Prediction Result
function renderPredictionResult(data) {
  document.getElementById('results-placeholder').style.display = 'none';
  const activeCard = document.getElementById('results-active');
  activeCard.style.display = 'block';

  // Badge
  const badge = document.getElementById('risk-badge');
  badge.textContent = data.risk_level;
  badge.style.color = data.risk_color;
  badge.style.backgroundColor = `${data.risk_color}22`;
  badge.style.border = `1px solid ${data.risk_color}66`;

  // Timestamp
  document.getElementById('result-time').textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  // Gauge & Bars
  initOrUpdateGauge(data.churn_probability, data.risk_color);

  document.getElementById('stat-churn-num').textContent = `${data.churn_probability}%`;
  document.getElementById('stat-retention-num').textContent = `${data.retention_probability}%`;

  document.getElementById('bar-churn').style.width = `${data.churn_probability}%`;
  document.getElementById('bar-retention').style.width = `${data.retention_probability}%`;

  // Risk Factors
  const factorsList = document.getElementById('factors-list');
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

  // Retention Strategies
  const stratList = document.getElementById('strategies-list');
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

  // Smooth scroll into results on mobile
  if (window.innerWidth < 1024) {
    activeCard.scrollIntoView({ behavior: 'smooth' });
  }
}

// BATCH FILE HANDLING
function handleFileSelected(event) {
  const file = event.target.files[0];
  if (file) {
    selectedBatchFile = file;
    document.getElementById('file-name-text').textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    document.getElementById('file-selected-badge').style.display = 'flex';
  }
}

// Upload & Score Batch CSV
async function uploadAndScoreBatch() {
  if (!selectedBatchFile) return;

  const btn = document.getElementById('run-batch-btn');
  btn.disabled = true;
  btn.textContent = 'Scoring CSV...';

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
    btn.disabled = false;
    btn.textContent = 'Run Bulk Prediction';
  }
}

// Render Batch Results
function renderBatchResults(data) {
  document.getElementById('batch-results-wrap').style.display = 'block';
  document.getElementById('batch-total').textContent = data.total_processed;
  document.getElementById('batch-high-risk').textContent = data.high_risk_count;
  document.getElementById('batch-rate').textContent = `${data.churn_rate_predicted}%`;

  const tbody = document.getElementById('batch-table-body');
  tbody.innerHTML = '';

  data.predictions.forEach(p => {
    const tr = document.createElement('tr');
    const color = p.risk_level === 'High Risk' ? 'var(--risk-high)' : (p.risk_level === 'Moderate Risk' ? 'var(--risk-mod)' : 'var(--risk-low)');
    tr.innerHTML = `
      <td>#${p.row_id}</td>
      <td><strong>${p.churn_prediction}</strong></td>
      <td>${p.churn_probability}%</td>
      <td><span style="color: ${color}; font-weight: 600;">${p.risk_level}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

// Initial setup on window load
window.addEventListener('DOMContentLoaded', () => {
  updateTenure(12);
  updateMonthly(75);
});
