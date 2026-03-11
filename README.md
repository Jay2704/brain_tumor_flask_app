# Brain Tumor Detection Flask Application

A full-stack web application for brain MRI tumor classification. Upload an MRI scan and receive an AI-powered prediction (glioma, meningioma, pituitary, or no tumor) using a VGG-based CNN. Built with a **React frontend** and **Flask backend** using a 3-agent pipeline (QA → Vision → Report → Safety Gate).

**What it does (at a glance):**
- **Frontend:** Interactive React UI with drag-and-drop upload, loading states, results dashboard, and brain tumor info
- **Backend:** Flask REST API with 3-agent pipeline (QA, Vision, Report)
- Accepts MRI images (PNG/JPG/JPEG, max 5 MB)
- Preprocesses to 224×224 RGB, runs VGG-based CNN inference
- Returns prediction with confidence, QA metrics, diagnostic report, and model info

**Note:** This app is intended for educational and research demonstration only and is not a medical device.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     React Frontend (Vite)                        │
│  • Drag-and-drop upload  • Loading progress  • Results dashboard │
│  • Brain Tumor Types     • Model info        • Full-width navbar  │
└──────────────────────────────┬──────────────────────────────────┘
                               │ POST /api/v1/analyze
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Flask Backend (port 5001)                    │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐            │
│  │ QA Agent    │ → │ Vision Agent│ → │ Report Agent│            │
│  │ (quality)   │   │ (CNN infer) │   │ (findings)  │            │
│  └─────────────┘   └─────────────┘   └──────┬──────┘            │
│                                              │                    │
│  ┌──────────────────────────────────────────▼──────┐             │
│  │ Safety Gate (overrides when QA fails / low conf)│             │
│  └─────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

- **Python 3.7+** and `pip`
- **Node.js 18+** and `npm`

---

## Local Development

### 1. Clone the Repository

```bash
git clone https://github.com/Jay2704/brain_tumor_flask_app.git
cd brain_tumor_flask_app
```

### 2. Backend Setup

```bash
pip install -r requirements.txt
```

**Download the model:**  
https://drive.google.com/drive/folders/12cdcVJYoenwH2WIF_IuYXjKRrFiedDnn

Place the file in `models/`:
```
models/Brain_Tumors_vgg_final.h5
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
```

Set `VITE_API_BASE_URL` in `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:5001
```

### 4. Run the Application

**Terminal 1 – Backend:**
```bash
python app.py
```
Backend runs at `http://127.0.0.1:5001`

For production, use Gunicorn instead of the Flask development server:

```bash
gunicorn app:app
```

**Terminal 2 – Frontend:**
```bash
cd frontend
npm run dev
```
Frontend runs at `http://127.0.0.1:5173`

### 5. Access

Open **http://127.0.0.1:5173** in your browser. The React app proxies `/api`, `/healthz`, and `/static` to the Flask backend.

---

## Environment Variables Configuration

### Frontend (`frontend/.env`)

```env
VITE_API_BASE_URL=http://127.0.0.1:5001
```

- Used by the React app for API calls (for example: `${VITE_API_BASE_URL}/api/v1/analyze`).
- For production, set this to your deployed backend URL.

### GitHub Actions (for Pages build)

Set a repository variable named `VITE_API_BASE_URL` in GitHub:

- Repository Settings → Secrets and variables → Actions → Variables
- Name: `VITE_API_BASE_URL`
- Value: your backend base URL (for example `https://your-api.example.com`)

---

## Backend Deployment Instructions

### Deploy Flask Backend to Render (Beginner-Friendly)

1. Push your project to GitHub.
2. In Render, click **New +** → **Web Service** and connect your repository.
3. Configure the service:
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn wsgi:app`
4. Deploy the service and wait for the build to finish.

### Important Notes

- **Model file location:** Make sure the model exists at `models/Brain_Tumors_vgg_final.h5` on the deployed server.
- **Python version on Render:** Use Python `3.10.13` for TensorFlow compatibility.
- **Preferred Render config:** Set environment variable `PYTHON_VERSION=3.10.13`.
- **Free plan behavior:** Render free web services can sleep after inactivity, so the first request after idle time may be slow.
- **Memory note:** Free-tier instances can still run out of memory during TensorFlow inference on some requests.
- **Frontend API URL:** Set `VITE_API_BASE_URL` to your deployed Render backend URL so the frontend calls the correct API in production.

### Local Production-Style Run (Optional)

```bash
pip install -r requirements.txt
gunicorn wsgi:app
```

---

## Frontend Deployment via GitHub Actions

The project includes a GitHub Pages workflow at:

`/.github/workflows/deploy-frontend.yml`

What it does:
- Triggers on push to `main`
- Uses Node.js 20
- Installs dependencies in `frontend/`
- Builds the frontend with `npm run build`
- Uploads `frontend/dist` as the Pages artifact
- Deploys to GitHub Pages

Before deploying, set the GitHub Actions variable `VITE_API_BASE_URL` to your backend URL.

---

## Project Structure

```
brain_tumor_flask_app/
├── app.py                    # Flask app, routes, model loading
├── agent/                    # 3-agent pipeline
│   ├── qa_agent.py           # Image quality checks (PIL + numpy)
│   ├── vision_agent_tf.py    # TensorFlow CNN inference
│   ├── report_agent_stub.py  # Report generation
│   ├── safety_gate.py       # Overrides when QA fails / low confidence
│   ├── orchestrator.py      # Runs agents in sequence
│   └── schemas.py
├── ml/
│   └── preprocess.py        # 224×224 RGB preprocessing
├── frontend/                 # React + Vite
│   ├── src/
│   │   ├── App.jsx          # Main app (upload, loading, results, tumor types)
│   │   └── App.css
│   ├── index.html
│   ├── vite.config.js       # Proxies /api, /healthz, /static to backend
│   └── package.json
├── models/
│   └── Brain_Tumors_vgg_final.h5   # Download separately
├── static/
│   └── uploads/             # Uploaded images
├── templates/                # Flask HTML (legacy routes)
│   ├── index.html
│   ├── brain_tumor.html
│   └── contact.html
├── image_data/               # Sample MRI images (glioma, meningioma, etc.)
├── tests/
├── requirements.txt
└── README.md
```

---

## Frontend Features

- **Upload:** Drag-and-drop or click to select MRI files (PNG/JPG/JPEG, max 5 MB)
- **Loading:** Progress steps (Image validation → AI inference → Report generation)
- **Results Dashboard:**
  - Primary detection with confidence
  - Quality Assurance (Safe to Infer, Quality Score)
  - Probability breakdown with progress bars
  - AI Diagnostic Report (Findings, Impression, Next Steps, Limitations, Urgency)
  - Model info (VGG-based CNN, 224×224 input, ~94% validation accuracy, inference time)
- **Brain Tumor Types:** Info page for Glioma, Meningioma, Pituitary, No Tumor
- **Navbar:** Logo (→ home), Brain Tumor Types, Login, Sign Up (placeholders)

---

## API Documentation for /api/v1/analyze

### POST /api/v1/analyze

**Request:** Multipart form with file field `image` (PNG/JPG/JPEG, max 5 MB)

**Success (200):**
```json
{
  "request_id": "...",
  "qa": {"safe_to_infer": true, "quality_score": 0.25, "warnings": []},
  "vision": {"label": "no_tumor", "confidence": 0.85, "probs": {...}},
  "report": {"findings": "...", "impression": "...", "next_steps": [...], "limitations": "...", "urgency": "low"},
  "artifacts": {"uploaded_image_url": "/static/uploads/..."},
  "latency_ms": 123.45
}
```

When QA blocks inference, `vision` is `null` but the response is still 200 with a valid `report`.

**Error (4xx/5xx):**
```json
{
  "error": {"code": "ERROR_CODE", "message": "Human readable message"}
}
```

### GET /healthz

Returns `{ok, model_loaded, service}`. 200 when healthy, 500 when model unavailable.

---

## Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home (Flask template; React dev uses Vite) |
| `/upload` | POST | Form upload, returns HTML with prediction |
| `/about` | GET | Brain tumors info page |
| `/contact` | GET | Contact page |
| `/healthz` | GET | Health check (JSON) |
| `/api/v1/analyze` | POST | Analyze image (JSON) |
| `/api/analyze` | POST | Legacy alias for `/api/v1/analyze` |

---

## How It Works

1. User uploads an MRI image via the React UI (drag-and-drop or file picker).
2. Frontend sends `POST /api/v1/analyze` with multipart `image`.
3. Backend saves the image to `static/uploads/` (UUID-prefixed).
4. **QA agent** checks resolution (min 150px), brightness, contrast. Sets `safe_to_infer`.
5. **Vision agent** preprocesses (224×224 RGB, normalize [0,1]), runs the VGG-based CNN.
6. **Report agent** generates findings, impression, next steps.
7. **Safety gate** overrides report when QA fails or confidence < 0.60.
8. Response returned to frontend; results dashboard displays prediction, QA, probabilities, report, and model info.

**Model:** VGG-based CNN, input `(1, 224, 224, 3)`, classes: `glioma`, `meningioma`, `no_tumor`, `pituitary`.

---

## Running Tests

```bash
pip install -r requirements.txt
pytest
```

Tests mock the model and do not require the `.h5` file.

---

## Build for Production

```bash
cd frontend
npm run build
```

Output in `frontend/dist/`. Serve the backend and configure it to serve the built React app from `dist/` for production deployment.

To run the backend in production:

```bash
gunicorn app:app
```

---

## Troubleshooting

- **Model loading error:** Ensure `Brain_Tumors_vgg_final.h5` is in the `models/` folder. The app starts even if the model fails; `/healthz` returns 500 and the API returns a friendly error.
- **Port in use:** Change `app.run(port=5001)` in `app.py` and update the proxy in `frontend/vite.config.js` if needed.
- **CORS:** Backend CORS is enabled for `/api/*`. Vite dev server proxy can still be used for local development.

---

## License

This project is for educational purposes only. For any other usage, please contact the author.

---

## Credits

- Flask, TensorFlow/Keras, React, Vite  
- Jay and Team
