# Brain Tumor Detection Flask Application

This web application lets you upload a brain MRI image and receive an instant prediction of the tumor type using a pre-trained deep learning model built with TensorFlow/Keras. It uses a 3-agent architecture (QA, Vision, Report) and provides both a web UI and a REST API.

**What it does (at a glance):**
- Accepts an MRI image upload (PNG/JPG/JPEG, max 5 MB)
- Runs QA checks (resolution, brightness, contrast)
- Preprocesses the image to 224×224 RGB and normalizes pixel values
- Runs inference with a CNN model (`.h5`)
- Returns one of four classes: `glioma`, `meningioma`, `no_tumor`, `pituitary`

**Use cases:**
- Quick local demos of medical imaging classification workflows
- Baseline for students learning Flask + TensorFlow deployment
- REST API for React or other frontends (CORS enabled)
- Starting point for customizing with your own models/datasets

**Note:** This app is intended for educational and research demonstration only and is not a medical device.

---

## Prerequisites

- Python 3.7 or higher
- `pip` (Python package installer)

---

## Instructions to Set Up and Run the Project

### 1. Clone the Repository
```bash
git clone https://github.com/Jay2704/brain_tumor_flask_app.git
cd brain_tumor_flask_app
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Download the Model File
Download the `.h5` model from this Google Drive folder:  
https://drive.google.com/drive/folders/12cdcVJYoenwH2WIF_IuYXjKRrFiedDnn

Create a `models/` directory (if it does not exist) and place the file there:
```
models/Brain_Tumors_vgg_final.h5
```

The model file is in `.gitignore` (not committed to the repo) because it is large.

### 4. Run the Flask Application
```bash
python app.py
```

### 5. Access the Application
Open your browser and navigate to:
```
http://127.0.0.1:5001/
```

---

## Project Structure

```
brain_tumor_flask_app/
├── app.py                 # Flask app, routes, model loading
├── agent/                 # 3-agent pipeline
│   ├── qa_agent.py        # Image quality checks (PIL + numpy)
│   ├── vision_agent_tf.py # TensorFlow inference
│   ├── report_agent_stub.py
│   ├── safety_gate.py
│   ├── orchestrator.py
│   └── schemas.py
├── ml/
│   └── preprocess.py      # Image preprocessing
├── models/
│   └── Brain_Tumors_vgg_final.h5   # Download separately
├── static/
│   ├── uploads/
│   └── style.css
├── templates/
│   ├── index.html
│   ├── brain_tumor.html
│   └── contact.html
├── tests/
│   ├── test_app.py
│   ├── test_api.py
│   └── test_template_content.py
├── requirements.txt
└── README.md
```

---

## Features

- **Web UI:** Upload MRI images via form, view prediction with confidence and quality score
- **REST API:** `POST /api/v1/analyze` for programmatic access (multipart form field `image`)
- **Health check:** `GET /healthz` returns `{ok, model_loaded, model_path}` (200 when healthy, 500 when model unavailable)
- **CORS:** Enabled for `/api/v1/analyze`, `/api/analyze`, `/healthz` (React dev server)
- **Validation:** PNG/JPG/JPEG only, 5 MB max, secure filenames
- **Standardized errors:** JSON `{error: {code, message}}` for API failures

---

## Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home page and upload form |
| `/upload` | POST | Form upload, returns HTML with prediction |
| `/about` | GET | Brain tumors info page |
| `/contact` | GET | Contact page |
| `/healthz` | GET | Health check (JSON) |
| `/api/v1/analyze` | POST | Analyze image (JSON) |
| `/api/analyze` | POST | Legacy alias for `/api/v1/analyze` |

---

## API: POST /api/v1/analyze

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

---

## How It Works

1. Upload an MRI image via the homepage form or API.
2. The server saves the image to `static/uploads/` (UUID-prefixed filename).
3. **QA agent** checks resolution (min 150px), brightness, contrast.
4. **Vision agent** preprocesses (224×224 RGB, normalize [0,1]), runs the TensorFlow model.
5. **Report agent** generates findings, impression, next steps; **safety gate** applies overrides when QA fails or confidence < 0.60.
6. The result is displayed (web) or returned as JSON (API).

**Model input shape:** `(1, 224, 224, 3)`  
**Predicted classes:** `glioma`, `meningioma`, `no_tumor`, `pituitary`

---

## React Frontend (Optional)

A minimal React frontend is in `frontend/`. To run it:

```bash
cd frontend
npm install
npm run dev
```

Ensure the Flask backend is running first (`python app.py`). The frontend proxies API calls to `http://127.0.0.1:5001`.

---

## Running Tests

```bash
pip install -r requirements.txt
pytest
```

Tests mock the model and do not require the `.h5` file.

---

## Troubleshooting

- **Model loading error:** Ensure `Brain_Tumors_vgg_final.h5` is in the `models/` folder (relative to `app.py`). The app will start even if the model fails to load; `/healthz` returns 500 and the upload/API return a friendly error.
- **Port in use:** Edit `app.run(port=5001, debug=True)` in `app.py` to use another port.
- **Apple Silicon:** Ensure a compatible TensorFlow build per the official docs if you encounter binary compatibility errors.

---

## License

This project is for educational purposes only. For any other usage, please contact the author.

---

## Credits

- Flask Framework
- TensorFlow/Keras
- Jay and Team
