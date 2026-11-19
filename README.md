# 🚖 Cab Prediction System

An intelligent predictive analytics and machine learning system for modern ride-hailing networks (Uber, Ola, Lyft). It provides instant fare estimation, passenger cancellation risk assessment, demand hotspot clustering, and operational telematics intelligence.

---

## 🌟 Key Features

- **💵 Instant Fare Estimation**: Multilinear and polynomial regression models predicting accurate trip pricing dynamically calibrated against real-time distance, vehicle class, traffic density, and weather conditions.
- **⚠️ Ride Cancellation Risk Prediction**: Classification engine evaluating passenger and driver churn risks based on wait time, localized surge factors, and pickup sectors.
- **📍 Demand Hotspots & Spatial Segmentation**: Unsupervised density-based spatial clustering (DBSCAN) and partitional K-Means mapping high-demand zones across urban districts.
- **📊 Interactive Analytics Dashboard**: Modern, clean Streamlit application with live sliders, residual diagnostics, and correlation heatmaps.

---

## 🚀 Quick Start

### 1. Launch the Web Application (One-Click)
Double-click **`run_app.bat`** or run:
```cmd
run_app.bat
```
Then open your browser at:
👉 **http://localhost:8501**

### 2. Run the Full Model Pipeline
To retrain models and regenerate all performance visual analytics:
```bash
python main.py
```

---

## 📁 Repository Structure
```
cab_prediction_system/
├── app.py                                  # Streamlit web dashboard
├── run_app.bat                             # One-click Windows application launcher
├── main.py                                 # Pipeline orchestrator
├── generate_dataset.py                     # Realistic dataset generator
├── cab_rides_dataset.csv                   # Raw ride transactions
├── cleaned_cab_data.csv                    # Cleaned feature-engineered dataset
├── data_analysis_and_exploration.py             # Descriptive analytics & EDA
├── data_cleaning_and_price_prediction.py    # Preprocessing pipeline & fare regression
├── ride_cancellation_prediction.py   # Cancellation risk classifiers
├── ride_grouping_and_patterns.py   # Spatial clustering & PCA
├── models/                                 # Exported trained scikit-learn models
├── plots/                                  # Statistical visualizations and diagnostic charts
├── Dockerfile                              # Containerization specification
├── docker-compose.yml                      # Docker Compose orchestrator
├── requirements.txt                        # Project dependencies
└── DEPLOYMENT.md                           # Deployment guides (Local, Cloud, Docker)
```

---

## 🌐 Deployment
The project is container-ready and can be deployed anywhere:
- **Local machine**: via `run_app.bat`
- **Docker**: `docker compose up -d`
- **Cloud (Streamlit Cloud, Render, Railway)**: Connect the GitHub repository with entry point `app.py`.
