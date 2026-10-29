# 🎓 EduPredict AI — Advanced Student Score & Performance Intelligence Suite

[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Flask-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn%201.6+-orange.svg)](https://scikit-learn.org/)
[![Model Accuracy](https://img.shields.io/badge/Ensemble%20R%C2%B2-0.998-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

> A state-of-the-art academic performance intelligence platform featuring multi-algorithm machine learning consensus, real-time interactive score simulation, explainable AI (XAI) feature attribution, target grade inverse optimization, batch CSV roster evaluation, and printable diagnostic report cards.

---

## 🌟 Key Features

### 1. 🧠 Multi-Model Machine Learning Consensus
- **Parallel Algorithms**: Simultaneously trains and evaluates:
  - **Consensus Ensemble (Weighted)**: $R^2 \approx 0.998$
  - **Gradient Boosting Regressor (GBR)**: Non-linear gradient boosted decision trees
  - **Random Forest (100 Trees)**: Ensemble bagging with variance estimation
  - **Ridge Regression (L2)**: Regularized linear model preventing overfitting
  - **Linear Regression**: Direct, explainable marginal baseline
- **5-Fold Cross Validation**: Cross-validated with $R^2$, MAE, and RMSE metrics.
- **Uncertainty & 95% Confidence Intervals**: Dynamically models prediction margin of error (e.g., $84.5 \pm 1.8$ points).
- **Academic Grading Scale**: Maps numerical outputs to letter grades (`A+`, `A`, `B`, `C`, `D`, `F`) and risk classifications (*Low Risk*, *Moderate Risk*, *High Academic Risk*).

### 2. ⚡ Real-Time Score Studio (Interactive Dashboard)
- **Synchronized Controls**: Real-time sliders and numeric inputs for Study Hours, Sleep Duration, Class Attendance, and Completed Assignments.
- **Instant Live Calculation**: Asynchronous debounced AJAX updates—no page reloads required.
- **Animated SVG Radial Gauge**: Fluid progress ring with neon gradient color transitions based on score tiers.
- **Behavioral Archetype Presets**: One-click quick presets (*Top Achiever*, *Balanced Routine*, *At-Risk Profile*, *Cohort Median*).

### 3. 🔍 Explainable AI (XAI) & Actionable Guidance
- **Feature Impact Waterfall**: Displays exact point attribution added or subtracted relative to cohort baselines.
- **Smart Advisory Engine**: Detects sleep deficits (< 6h), warns when attendance is below the 75% threshold, and calculates the exact hours needed to achieve the next letter grade.

### 4. 📈 Visual Analytics & Radar Profile (Chart.js)
- **4-Pillar Performance Radar Chart**: Multi-axis balance across study intensity, sleep adequacy, attendance rate, and coursework completion against class averages.
- **Marginal Sensitivity Curve**: Plots projected score trajectory from 1 to 14 study hours holding other factors constant.
- **Multi-Model Consensus Comparison**: Bar chart comparing predictions across all 4 machine learning algorithms.

### 5. 🎯 Goal & Target Optimizer (Inverse Solver)
- Input your desired score (e.g., 85% or 92%).
- Computes the necessary study hours and produces a balanced habit roadmap leveraging attendance and assignments.

### 6. 📂 Batch CSV / Excel Evaluation
- Upload student rosters via drag-and-drop (`.csv` or `.xlsx`).
- Scores entire classes simultaneously with grades, percentile standings, and risk alerts.
- Downloadable sample CSV template provided.

### 7. 🖨️ Printable Diagnostic Student Report Card
- Generates a polished diagnostic report with student metrics, standing, and recommendations, formatted for printing or PDF export.

### 8. 🎨 Modern Glassmorphic Design System
- Sleek dark theme with glowing accents, backdrop blur, and micro-animations.
- Built-in Dark / Light mode toggle with local storage persistence.

---

## 📁 Project Structure

```
student_score_app/
│
├── student_score_app/
│   ├── app.py                     # Flask web server and REST API endpoints
│   ├── ml_engine.py               # Multi-model ML pipeline, benchmarks, and XAI
│   ├── model.pkl                  # Serialized machine learning model
│   ├── requirements.txt           # Project dependencies
│   ├── student_performance.xlsx   # Academic training dataset (Excel)
│   ├── student_performance.csv    # Academic training dataset (CSV)
│   │
│   ├── static/
│   │   ├── style.css              # Glassmorphic CSS design system & themes
│   │   └── app.js                 # Frontend interactive controller & charts
│   │
│   └── templates/
│       ├── index.html             # Main analytics dashboard & simulator
│       └── result.html            # Diagnostic evaluation result page
│
├── .gitignore                     # Git ignore rules
└── README.md                      # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/Asvitha-chitteti/Student-Score-App.git
cd Student-Score-App
```

### 2. Install Dependencies
```bash
pip install -r student_score_app/requirements.txt
```

### 3. Run the Application
```bash
python student_score_app/app.py
```

### 4. Open in Your Browser
Navigate to **`http://127.0.0.1:7860`**

---

## 📡 REST API Reference

| Endpoint | Method | Payload / Parameters | Description |
|---|---|---|---|
| `/` | `GET` | None | Renders the full interactive platform |
| `/predict` | `POST` | Form or JSON (`hours`, `sleep`, `attendance`, `assignments`, `model`) | Score prediction endpoint |
| `/api/predict` | `POST` | JSON: `{ hours, sleep, attendance, assignments, model }` | Real-time prediction with XAI breakdown |
| `/api/optimize` | `POST` | JSON: `{ target_score, sleep, attendance, assignments }` | Inverse target score solver |
| `/api/batch-predict` | `POST` | `multipart/form-data` with `file` | Evaluates student roster (CSV/Excel) |
| `/api/download-template` | `GET` | None | Downloads sample CSV roster template |
| `/api/metrics` | `GET` | None | Returns model benchmark comparison table |
| `/data` | `GET` | `?format=json` or HTML | Dataset explorer |

---

## 📄 License
This project is licensed under the MIT License.
