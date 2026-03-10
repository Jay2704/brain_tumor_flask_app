# Brain Tumor MRI Diagnosis AI — Tech Stack

## Summary

| Layer | Technology | Version / Notes |
|-------|------------|-----------------|
| **Frontend** | React | 18.2 |
| **Build** | Vite | 5.x |
| **Backend** | Flask | 3.1 |
| **ML** | TensorFlow / Keras | 2.18 |
| **Image** | Pillow, NumPy | 11.0, 2.0 |
| **PDF** | jsPDF | 4.2 |
| **Testing** | pytest, pytest-flask | 8.3, 1.3 |

---

## Frontend

| Package | Purpose |
|---------|---------|
| **React** | UI components, state management (useState, useEffect) |
| **React DOM** | React rendering for the browser |
| **Vite** | Dev server, HMR, production build, proxy to backend |
| **jsPDF** | Client-side PDF generation for report export |

**Key features:**
- Single-page application (SPA)
- No routing library (view state in React state)
- Proxy: `/api`, `/healthz`, `/static` → Flask (port 5001)
- Dark mode (localStorage persistence)
- Responsive layout

---

## Backend

| Package | Purpose |
|---------|---------|
| **Flask** | Web framework, routing, request handling |
| **Werkzeug** | WSGI, secure_filename, request parsing |
| **TensorFlow** | Load and run Keras model (.h5) |
| **Pillow (PIL)** | Image loading, resize, RGB conversion |
| **NumPy** | Array operations, preprocessing |

**Key features:**
- REST API: `POST /api/v1/analyze`, `GET /healthz`
- CORS enabled for API routes
- Multipart file upload (max 5 MB)
- Standardized error format: `{error: {code, message}}`

---

## ML / Model

| Component | Details |
|-----------|---------|
| **Model** | VGG-based CNN (Keras .h5) |
| **Input** | 224×224 RGB, normalized [0, 1] |
| **Output** | 4 classes: glioma, meningioma, no_tumor, pituitary |
| **Preprocessing** | `ml/preprocess.py`: resize, convert RGB, normalize |

**Model file:** `models/Brain_Tumors_vgg_final.h5` (download separately, in .gitignore)

---

## Project Structure

```
brain_tumor_flask_app/
├── app.py                 # Flask app, routes, model loading
├── agent/
│   ├── qa_agent.py        # Image quality checks
│   ├── vision_agent_tf.py # TensorFlow inference
│   ├── report_agent_stub.py # Report generation
│   ├── safety_gate.py     # Report overrides
│   ├── orchestrator.py   # Pipeline coordination
│   └── schemas.py
├── ml/
│   └── preprocess.py      # 224×224 RGB preprocessing
├── frontend/
│   ├── src/App.jsx       # Main React app
│   ├── src/App.css       # Styles
│   ├── vite.config.js    # Proxy config
│   └── package.json
├── models/                # .h5 model (gitignored)
├── static/uploads/       # Uploaded images
├── templates/            # Flask HTML (legacy)
├── tests/                # pytest
├── docs/                 # Documentation
├── requirements.txt
└── README.md
```

---

## Development Environment

| Tool | Purpose |
|------|---------|
| **Python 3.7+** | Backend runtime |
| **Node.js 18+** | Frontend build & dev server |
| **pip** | Python dependencies |
| **npm** | Frontend dependencies |

**Ports:**
- Frontend (Vite): `http://127.0.0.1:5173`
- Backend (Flask): `http://127.0.0.1:5001`

---

## Testing

| Tool | Purpose |
|------|---------|
| **pytest** | Test runner |
| **pytest-flask** | Flask test client |
| **BeautifulSoup** | HTML parsing in template tests |

Tests mock the model; no `.h5` file required.
