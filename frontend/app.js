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
  document.getElementById('tab-si