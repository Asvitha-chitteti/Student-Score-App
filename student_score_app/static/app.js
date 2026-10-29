/* ==========================================================================
   EduPredict AI — Frontend Interactive Engine & Charting Controller
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // State
  let currentPrediction = null;
  let radarChart = null;
  let sensitivityChart = null;
  let modelsChart = null;
  let debounceTimer = null;

  // DOM Elements
  const inputs = {
    hours: document.getElementById('input-hours'),
    hoursSlider: document.getElementById('slider-hours'),
    sleep: document.getElementById('input-sleep'),
    sleepSlider: document.getElementById('slider-sleep'),
    attendance: document.getElementById('input-attendance'),
    attendanceSlider: document.getElementById('slider-attendance'),
    assignments: document.getElementById('input-assignments'),
    assignmentsSlider: document.getElementById('slider-assignments'),
    model: document.getElementById('model-select')
  };

  const displays = {
    score: document.getElementById('display-score'),
    gradePill: document.getElementById('display-grade-pill'),
    gradeDesc: document.getElementById('display-grade-desc'),
    gaugeCircle: document.getElementById('gauge-progress-circle'),
    ciLower: document.getElementById('display-ci-lower'),
    ciUpper: document.getElementById('display-ci-upper'),
    percentile: document.getElementById('display-percentile'),
    riskBadge: document.getElementById('display-risk-badge'),
    impactList: document.getElementById('impact-list'),
    recList: document.getElementById('recommendations-list')
  };

  // Tabs
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab');
      tabButtons.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add('active');

      // Refresh charts if entering analytics tab
      if (targetId === 'tab-analytics') {
        setTimeout(initOrUpdateCharts, 100);
      }
    });
  });

  // Dark/Light Theme Switcher
  const themeToggle = document.getElementById('theme-toggle');
  const savedTheme = localStorage.getItem('edupredict-theme') || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('edupredict-theme', next);
      updateThemeIcon(next);
      if (radarChart) {
        initOrUpdateCharts();
      }
    });
  }

  function updateThemeIcon(theme) {
    if (!themeToggle) return;
    themeToggle.innerHTML = theme === 'dark' 
      ? '<span>☀️ Light Mode</span>' 
      : '<span>🌙 Dark Mode</span>';
  }

  // Synchronize Slider <-> Number Inputs
  function bindSync(slider, input) {
    if (!slider || !input) return;
    slider.addEventListener('input', (e) => {
      input.value = e.target.value;
      triggerPrediction();
    });
    input.addEventListener('input', (e) => {
      slider.value = e.target.value;
      triggerPrediction();
    });
  }

  bindSync(inputs.hoursSlider, inputs.hours);
  bindSync(inputs.sleepSlider, inputs.sleep);
  bindSync(inputs.attendanceSlider, inputs.attendance);
  bindSync(inputs.assignmentsSlider, inputs.assignments);

  if (inputs.model) {
    inputs.model.addEventListener('change', triggerPrediction);
  }

  // Preset Buttons
  const presets = {
    top: { hours: 9.5, sleep: 7.5, attendance: 96, assignments: 9 },
    balanced: { hours: 6.0, sleep: 7.0, attendance: 85, assignments: 6 },
    atrisk: { hours: 2.5, sleep: 5.0, attendance: 65, assignments: 3 },
    reset: { hours: 6.5, sleep: 6.0, attendance: 85, assignments: 6 }
  };

  document.querySelectorAll('[data-preset]').forEach(btn => {
    btn.addEventListener('click', () => {
      const p = presets[btn.getAttribute('data-preset')];
      if (!p) return;
      inputs.hours.value = inputs.hoursSlider.value = p.hours;
      inputs.sleep.value = inputs.sleepSlider.value = p.sleep;
      inputs.attendance.value = inputs.attendanceSlider.value = p.attendance;
      inputs.assignments.value = inputs.assignmentsSlider.value = p.assignments;
      triggerPrediction();
    });
  });

  // Debounced Predict API Call
  function triggerPrediction() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(fetchPrediction, 80);
  }

  async function fetchPrediction() {
    const payload = {
      hours: parseFloat(inputs.hours.value) || 0,
      sleep: parseFloat(inputs.sleep.value) || 0,
      attendance: parseFloat(inputs.attendance.value) || 0,
      assignments: parseFloat(inputs.assignments.value) || 0,
      model: inputs.model ? inputs.model.value : 'ensemble'
    };

    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!response.ok) throw new Error('Prediction API failed');
      const data = await response.json();
      currentPrediction = data;
      renderPrediction(data);
      if (document.getElementById('tab-analytics').classList.contains('active')) {
        updateChartsData(data);
      }
    } catch (err) {
      console.error('Prediction error:', err);
    }
  }

  // Render Prediction to UI
  function renderPrediction(data) {
    if (!data) return;

    // Animate Score Counter
    if (displays.score) {
      animateValue(displays.score, parseFloat(displays.score.innerText) || 0, data.score, 350);
    }

    // Radial Gauge Calculation
    // Circumference = 2 * PI * 90 = ~565.48
    if (displays.gaugeCircle) {
      const circumference = 565.48;
      const progress = Math.max(0, Math.min(100, data.score));
      const offset = circumference - (progress / 100) * circumference;
      displays.gaugeCircle.style.strokeDashoffset = offset;
    }

    // Grade Pill
    if (displays.gradePill) {
      displays.gradePill.innerText = `Grade ${data.letter_grade}`;
      displays.gradePill.className = `grade-pill pill-${data.grade_color}`;
    }

    if (displays.gradeDesc) {
      displays.gradeDesc.innerText = data.grade_desc;
    }

    // KPIs
    if (displays.ciLower && displays.ciUpper) {
      displays.ciLower.innerText = data.ci.lower;
      displays.ciUpper.innerText = data.ci.upper;
    }

    if (displays.percentile) {
      displays.percentile.innerText = `Top ${Math.round(100 - data.percentile)}%`;
    }

    if (displays.riskBadge) {
      displays.riskBadge.innerText = data.risk_level;
      displays.riskBadge.className = `kpi-badge badge-${data.risk_badge}`;
    }

    // Waterfall Feature Impacts
    if (displays.impactList && data.impacts) {
      displays.impactList.innerHTML = data.impacts.map(item => `
        <div class="impact-item">
          <div class="impact-info">
            <span class="impact-name">${item.feature} (${item.value})</span>
            <span class="impact-meta">vs ${item.baseline}</span>
          </div>
          <span class="impact-badge ${item.positive ? 'impact-pos' : 'impact-neg'}">
            ${item.positive ? '+' : ''}${item.points} pts
          </span>
        </div>
      `).join('');
    }

    // AI Smart Recommendations
    if (displays.recList && data.recommendations) {
      displays.recList.innerHTML = data.recommendations.map(rec => `
        <div class="rec-card rec-${rec.type}">
          <div class="rec-title">${rec.title}</div>
          <div class="rec-text">${rec.text}</div>
        </div>
      `).join('');
    }
  }

  function animateValue(elem, start, end, duration) {
    if (start === end) return;
    const range = end - start;
    let startTime = null;

    function step(timestamp) {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const current = start + range * progress;
      elem.innerText = current.toFixed(1);
      if (progress < 1) {
        window.requestAnimationFrame(step);
      } else {
        elem.innerText = end.toFixed(1);
      }
    }
    window.requestAnimationFrame(step);
  }

  // Chart.js Visualizations
  function initOrUpdateCharts() {
    if (!currentPrediction) return;

    const isDark = (document.documentElement.getAttribute('data-theme') || 'dark') === 'dark';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)';
    const textColor = isDark ? '#94a3b8' : '#475569';

    // 1. Radar Chart (Student Profile vs Class Benchmark)
    const radarCtx = document.getElementById('radarChart');
    if (radarCtx) {
      if (radarChart) radarChart.destroy();
      radarChart = new Chart(radarCtx, {
        type: 'radar',
        data: {
          labels: currentPrediction.radar.labels,
          datasets: [
            {
              label: 'Current Student',
              data: currentPrediction.radar.student,
              backgroundColor: 'rgba(99, 102, 241, 0.25)',
              borderColor: '#6366f1',
              borderWidth: 2.5,
              pointBackgroundColor: '#6366f1'
            },
            {
              label: 'Cohort Average',
              data: currentPrediction.radar.benchmark,
              backgroundColor: 'rgba(6, 182, 212, 0.15)',
              borderColor: '#06b6d4',
              borderWidth: 2,
              borderDash: [4, 4],
              pointBackgroundColor: '#06b6d4'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            r: {
              angleLines: { color: gridColor },
              grid: { color: gridColor },
              pointLabels: { color: textColor, font: { family: 'Plus Jakarta Sans', size: 12, weight: 600 } },
              ticks: { display: false, min: 0, max: 100 }
            }
          },
          plugins: {
            legend: { labels: { color: textColor, font: { family: 'Plus Jakarta Sans', weight: 600 } } }
          }
        }
      });
    }

    // 2. Sensitivity Curve (Score vs Study Hours)
    const sensCtx = document.getElementById('sensitivityChart');
    if (sensCtx) {
      if (sensitivityChart) sensitivityChart.destroy();
      const labels = currentPrediction.sensitivity.map(pt => `${pt.hours}h`);
      const dataPoints = currentPrediction.sensitivity.map(pt => pt.predicted_score);

      sensitivityChart = new Chart(sensCtx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Projected Score',
            data: dataPoints,
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            fill: true,
            tension: 0.35,
            pointRadius: 4,
            pointHoverRadius: 7
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              grid: { color: gridColor },
              ticks: { color: textColor, font: { family: 'Plus Jakarta Sans' } },
              title: { display: true, text: 'Daily Study Hours', color: textColor }
            },
            y: {
              min: 0,
              max: 100,
              grid: { color: gridColor },
              ticks: { color: textColor, font: { family: 'Plus Jakarta Sans' } },
              title: { display: true, text: 'Projected Final Score', color: textColor }
            }
          },
          plugins: {
            legend: { display: false }
          }
        }
      });
    }

    // 3. Models Comparison Chart
    const modelsCtx = document.getElementById('modelsComparisonChart');
    if (modelsCtx && currentPrediction.models_comparison) {
      if (modelsChart) modelsChart.destroy();
      const modelLabels = ['Linear', 'Ridge', 'Random Forest', 'Gradient Boosting'];
      const modelVals = [
        currentPrediction.models_comparison.linear,
        currentPrediction.models_comparison.ridge,
        currentPrediction.models_comparison.rf,
        currentPrediction.models_comparison.gbr
      ];

      modelsChart = new Chart(modelsCtx, {
        type: 'bar',
        data: {
          labels: modelLabels,
          datasets: [{
            label: 'Model Prediction',
            data: modelVals,
            backgroundColor: ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b'],
            borderRadius: 8
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              grid: { display: false },
              ticks: { color: textColor, font: { family: 'Plus Jakarta Sans', weight: 600 } }
            },
            y: {
              min: 0,
              max: 100,
              grid: { color: gridColor },
              ticks: { color: textColor }
            }
          },
          plugins: {
            legend: { display: false }
          }
        }
      });
    }
  }

  function updateChartsData(data) {
    if (radarChart && data.radar) {
      radarChart.data.datasets[0].data = data.radar.student;
      radarChart.update();
    }
    if (sensitivityChart && data.sensitivity) {
      sensitivityChart.data.datasets[0].data = data.sensitivity.map(pt => pt.predicted_score);
      sensitivityChart.update();
    }
    if (modelsChart && data.models_comparison) {
      modelsChart.data.datasets[0].data = [
        data.models_comparison.linear,
        data.models_comparison.ridge,
        data.models_comparison.rf,
        data.models_comparison.gbr
      ];
      modelsChart.update();
    }
  }

  // Goal Optimizer Logic
  const targetSlider = document.getElementById('target-score-slider');
  const targetInput = document.getElementById('target-score-input');
  const optimizeBtn = document.getElementById('run-optimizer-btn');

  if (targetSlider && targetInput) {
    targetSlider.addEventListener('input', (e) => targetInput.value = e.target.value);
    targetInput.addEventListener('input', (e) => targetSlider.value = e.target.value);
  }

  if (optimizeBtn) {
    optimizeBtn.addEventListener('click', async () => {
      const targetVal = parseFloat(targetInput ? targetInput.value : 85);
      const payload = {
        target_score: targetVal,
        sleep: parseFloat(inputs.sleep.value) || 7,
        attendance: parseFloat(inputs.attendance.value) || 85,
        assignments: parseFloat(inputs.assignments.value) || 7
      };

      try {
        const res = await fetch('/api/optimize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const plan = await res.json();
        const resCard = document.getElementById('optimizer-result-card');
        if (resCard) {
          resCard.style.display = 'block';
          document.getElementById('opt-target-display').innerText = `${plan.target_score} pts`;
          document.getElementById('opt-needed-hours').innerText = `${plan.recommended_hours} hrs/day`;
          document.getElementById('opt-plan-hours').innerText = `${plan.balanced_plan.hours} hrs`;
          document.getElementById('opt-plan-att').innerText = `${plan.balanced_plan.attendance}%`;
          document.getElementById('opt-plan-assign').innerText = `${plan.balanced_plan.assignments}`;
        }
      } catch (err) {
        console.error('Optimizer error:', err);
      }
    });
  }

  // Batch Predict File Upload
  const uploadZone = document.getElementById('batch-upload-zone');
  const fileInput = document.getElementById('batch-file-input');
  const batchResultsContainer = document.getElementById('batch-results-container');
  const batchTableBody = document.getElementById('batch-table-body');
  const batchTotal = document.getElementById('batch-total-count');
  const batchAvg = document.getElementById('batch-avg-score');
  const batchPass = document.getElementById('batch-pass-rate');

  if (uploadZone && fileInput) {
    uploadZone.addEventListener('click', () => fileInput.click());
    uploadZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      uploadZone.classList.add('dragover');
    });
    uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
    uploadZone.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadZone.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) {
        fileInput.files = e.dataTransfer.files;
        handleBatchUpload(fileInput.files[0]);
      }
    });
    fileInput.addEventListener('change', () => {
      if (fileInput.files.length > 0) {
        handleBatchUpload(fileInput.files[0]);
      }
    });
  }

  async function handleBatchUpload(file) {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    formData.append('model', inputs.model ? inputs.model.value : 'ensemble');

    try {
      uploadZone.innerHTML = '<div class="upload-icon">⏳</div><h3>Processing student dataset...</h3>';
      const res = await fetch('/api/batch-predict', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Upload failed');

      // Populate batch results
      if (batchResultsContainer && batchTableBody) {
        batchResultsContainer.style.display = 'block';
        batchTotal.innerText = data.summary.total_students;
        batchAvg.innerText = data.summary.avg_score;
        batchPass.innerText = `${data.summary.pass_rate}%`;

        batchTableBody.innerHTML = data.records.map(r => `
          <tr>
            <td><strong>${r.Student_Name}</strong></td>
            <td>${r.Hours}</td>
            <td>${r.Sleep}</td>
            <td>${r.Attendance}%</td>
            <td>${r.Assignments}</td>
            <td><strong style="color: var(--primary); font-family: var(--font-mono);">${r.Predicted_Score}</strong></td>
            <td><span class="grade-pill pill-cyan" style="font-size: 11px; padding: 2px 8px;">${r.Grade}</span></td>
            <td><span class="kpi-badge badge-${r.Risk_Level.includes('Low') ? 'success' : r.Risk_Level.includes('Moderate') ? 'warning' : 'danger'}">${r.Risk_Level}</span></td>
          </tr>
        `).join('');
      }

      uploadZone.innerHTML = `
        <div class="upload-icon">✅</div>
        <h3>Successfully Scored ${data.records.length} Students</h3>
        <p style="font-size: 13px; color: var(--text-muted);">Click or drop another CSV/Excel file to run a new batch</p>
      `;
    } catch (err) {
      alert(`Batch processing error: ${err.message}`);
      uploadZone.innerHTML = `
        <div class="upload-icon">📁</div>
        <h3>Drop Student CSV or Excel file here</h3>
        <p style="font-size: 13px; color: var(--text-muted);">or click to browse from computer</p>
      `;
    }
  }

  // Diagnostic Report Modal & Print
  const printTrigger = document.getElementById('open-report-btn');
  const reportModal = document.getElementById('report-modal');
  const closeModal = document.getElementById('close-report-modal');
  const doPrintBtn = document.getElementById('do-print-btn');

  if (printTrigger && reportModal) {
    printTrigger.addEventListener('click', () => {
      populateReportCard();
      reportModal.classList.add('active');
    });
  }

  if (closeModal && reportModal) {
    closeModal.addEventListener('click', () => reportModal.classList.remove('active'));
    reportModal.addEventListener('click', (e) => {
      if (e.target === reportModal) reportModal.classList.remove('active');
    });
  }

  if (doPrintBtn) {
    doPrintBtn.addEventListener('click', () => window.print());
  }

  function populateReportCard() {
    if (!currentPrediction) return;
    document.getElementById('rep-score').innerText = `${currentPrediction.score} / 100`;
    document.getElementById('rep-grade').innerText = `Grade ${currentPrediction.letter_grade}`;
    document.getElementById('rep-status').innerText = currentPrediction.grade_desc;
    document.getElementById('rep-risk').innerText = currentPrediction.risk_level;
    document.getElementById('rep-percentile').innerText = `Top ${Math.round(100 - currentPrediction.percentile)}%`;
    document.getElementById('rep-ci').innerText = `${currentPrediction.ci.lower} - ${currentPrediction.ci.upper} (95% CI)`;

    document.getElementById('rep-hours').innerText = `${inputs.hours.value} hrs`;
    document.getElementById('rep-sleep').innerText = `${inputs.sleep.value} hrs`;
    document.getElementById('rep-att').innerText = `${inputs.attendance.value}%`;
    document.getElementById('rep-assign').innerText = `${inputs.assignments.value}`;
    document.getElementById('rep-date').innerText = new Date().toLocaleDateString('en-US', {
      year: 'numeric', month: 'long', day: 'numeric'
    });
  }

  // Initial trigger to load initial prediction
  fetchPrediction();
});
