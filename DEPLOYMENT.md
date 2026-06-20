# Deployment Guide

This guide details how to deploy the Citizen Cyber Shield FastAPI Backend, Frontend static files, and Streamlit application to cloud platforms (specifically GitHub, Netlify, and Render).

---

## 1. Preparing for Production (CRITICAL)

Before deploying, you **MUST** update the API endpoint URL in the frontend JavaScript files:
* Open `frontend/js/app.js`.
* Locate `const API_BASE_URL = "http://localhost:8000";` (Line 7).
* Replace `"http://localhost:8000"` with your deployed backend URL (e.g. `"https://api.citizencybershield.com"` or `"https://citizen-cyber-shield-backend.onrender.com"`).

---

## 2. Deploying the Backend (FastAPI) on Render

[Render](https://render.com/) is a great cloud platform for hosting Python web servers.

### Step-by-Step Backend Deploy:
1. Log in to Render and create a new **Web Service**.
2. Connect your Git repository.
3. Configure the following service settings:
   * **Environment**: `Python 3`
   * **Region**: Choose the closest region.
   * **Branch**: `main`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `python -m uvicorn backend.server:app --host 0.0.0.0 --port 10000`
4. Add the following **Environment Variables** in the Render Dashboard:
   * `PYTHON_VERSION`: `3.10.0` (or higher)
   * `OPENBLAS_NUM_THREADS`: `1` (prevents threading overhead errors)
   * `OMP_NUM_THREADS`: `1`
5. Click **Create Web Service**. Render will build and expose a public URL (e.g. `https://your-app.onrender.com`). Use this URL to update `API_BASE_URL` in `frontend/js/app.js`.

---

## 3. Deploying the Frontend Static Site on Netlify

[Netlify](https://www.netlify.com/) is ideal for hosting HTML/JS static files.

### Step-by-Step Frontend Deploy:
1. Log in to Netlify.
2. Select **Add new site** -> **Import an existing project** from GitHub.
3. Choose your repository.
4. Configure build settings:
   * **Base directory**: `frontend`
   * **Build command**: Leave blank (no build step needed for plain HTML/JS).
   * **Publish directory**: `.` (which points to the `frontend` folder since it's the base directory).
5. Click **Deploy site**.
6. Once deployed, Netlify will give you a public URL (e.g., `https://your-site.netlify.app`).

---

## 4. Deploying the Streamlit Interface (Alternative) on Streamlit Community Cloud

If you wish to deploy the Streamlit app (`app.py`):
1. Sign up on [Streamlit Community Cloud](https://share.streamlit.io/).
2. Click **New app**.
3. Choose your repository, branch, and set the main file path to `app.py`.
4. Click **Deploy**.

---

## 5. Deployment Checklist
* [ ] Changed `API_BASE_URL` in `frontend/js/app.js` to the live backend URL.
* [ ] Ensured that models `.pkl` are committed or uploaded.
* [ ] Checked that datasets directories are ignored in `.gitignore`.
* [ ] Added standard thread safety environment variables to backend service.
