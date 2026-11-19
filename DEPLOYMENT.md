# 🚀 Deployment Guide - Cab Prediction System

This project is packaged with multiple deployment options depending on whether you want to deploy locally, in a container, or to the public cloud.

---

## Option 1: Instant Local Deployment (One-Click)

The repository includes a ready-to-use Windows batch launcher [`run_app.bat`](file:///c:/Users/madha/OneDrive/Desktop/cab_prediction_system/run_app.bat).

1. Simply double-click **`run_app.bat`** inside the `cab_prediction_system` folder.
2. It automatically starts Streamlit and opens your default browser at:
   ```
   http://localhost:8501
   ```
3. Or from PowerShell / Command Prompt:
   ```cmd
   cd c:\Users\madha\OneDrive\Desktop\cab_prediction_system
   run_app.bat
   ```

---

## Option 2: Deploy to Streamlit Community Cloud (Free Public URL)

**Streamlit Community Cloud** provides free 24/7 cloud hosting directly connected to GitHub:

1. **Push your code to GitHub**:
   - Create a new GitHub repository named `cab-prediction-system`.
   - Upload/push this folder contents (`app.py`, `requirements.txt`, `cleaned_cab_data.csv`, `plots/`, etc.).
2. **Deploy on Streamlit Cloud**:
   - Visit [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
   - Click **"New app"**.
   - Select your repository: `username/cab-prediction-system`.
   - Set **Main file path**: `app.py`.
   - Click **Deploy!**
3. Your app will receive a permanent public URL (e.g. `https://cab-prediction-system.streamlit.app`).

---

## Option 3: Deploy with Docker / Docker Compose

A production-grade [`Dockerfile`](file:///c:/Users/madha/OneDrive/Desktop/cab_prediction_system/Dockerfile) and [`docker-compose.yml`](file:///c:/Users/madha/OneDrive/Desktop/cab_prediction_system/docker-compose.yml) are pre-configured in this repository.

### Build and Run with Docker:
```bash
# Build Docker image
docker build -t cab-prediction-system .

# Run Docker container exposing port 8501
docker run -d -p 8501:8501 --name cab_app cab-prediction-system
```

### Build and Run with Docker Compose:
```bash
docker compose up -d
```
Access the application at `http://localhost:8501`.

---

## Option 4: Deploy to Cloud PaaS (Render, Railway, or Heroku)

The repository includes a [`Procfile`](file:///c:/Users/madha/OneDrive/Desktop/cab_prediction_system/Procfile):
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### Deploying to Render.com:
1. Push your repository to GitHub.
2. Sign in to [render.com](https://render.com) and click **"New Web Service"**.
3. Connect your GitHub repository.
4. Set:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
5. Click **Deploy Web Service**.
