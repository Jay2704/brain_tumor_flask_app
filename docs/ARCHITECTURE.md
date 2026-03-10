# Brain Tumor MRI Diagnosis AI — System Architecture

## Overview

A full-stack medical imaging application that classifies brain MRI scans into four categories (glioma, meningioma, pituitary, no tumor) using a VGG-based CNN. The system uses a **3-agent pipeline** with a **safety gate** to ensure quality and reliability.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                                     │
│  React + Vite SPA • Port 5173                                                │
│  • Home • Diagnosis AI • Brain Tumor Types • Login/Sign Up                   │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │ HTTP POST /api/v1/analyze (multipart)
                                     │ GET /healthz
                                     │ GET /static/uploads/*
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FLASK BACKEND (Port 5001)                             │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     ORCHESTRATOR                                       │   │
│  │  Coordinates agents in sequence, measures latency, returns combined   │   │
│  │  result {request_id, qa, vision, report, artifacts, latency_ms}       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                     │                                         │
│         ┌──────────────────────────┼──────────────────────────┐            │
│         ▼                          ▼                          ▼            │
│  ┌─────────────┐            ┌─────────────┐            ┌─────────────┐      │
│  │  QA AGENT   │───────────▶│VISION AGENT │───────────▶│REPORT AGENT │      │
│  │  (quality)  │            │ (CNN infer) │            │ (findings)   │      │
│  └─────────────┘            └─────────────┘            └──────┬───────┘      │
│         │                           │                        │              │
│         │  safe_to_infer=false       │  label, confidence     │              │
│         │  → skip vision             │  probs                 │              │
│         │                            │                        │              │
│         └───────────────────────────┴────────────────────────┴──────────────┤
│                                              │                              │
│                                              ▼                              │
│                                    ┌─────────────────┐                      │
│                                    │  SAFETY GATE    │                      │
│                                    │  Overrides when │                      │
│                                    │  QA fails or    │                      │
│                                    │  confidence<60% │                      │
│                                    └─────────────────┘                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STORAGE                                                                      │
│  • static/uploads/ — Uploaded MRI images (UUID-prefixed)                       │
│  • models/Brain_Tumors_vgg_final.h5 — Pre-trained VGG CNN                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Frontend (React + Vite)

| Component | Responsibility |
|-----------|----------------|
| **App.jsx** | Main SPA: view state (home, upload, loading, results, tumor-types, login, signup), file handling, API calls |
| **Upload flow** | Drag-and-drop, file validation (PNG/JPG/JPEG, 5MB), Analyze button |
| **Loading state** | Progress steps: Image validation → AI inference → Report generation |
| **Results dashboard** | Primary detection, QA, probability breakdown, report, model info, PDF export |
| **Vite proxy** | Proxies `/api`, `/healthz`, `/static` to Flask backend |

### 2. Backend (Flask)

| Component | Responsibility |
|-----------|----------------|
| **app.py** | Routes, CORS, file upload handling, model loading, orchestration call |
| **Orchestrator** | Runs QA → Vision → Report in sequence, applies Safety Gate |
| **QA Agent** | Image quality checks (resolution, brightness, contrast) |
| **Vision Agent** | Preprocess + CNN inference |
| **Report Agent** | Deterministic report generation (findings, impression, next_steps) |
| **Safety Gate** | Overrides report when QA fails or confidence < 0.60 |

### 3. ML Pipeline

| Component | Responsibility |
|-----------|----------------|
| **preprocess.py** | Resize to 224×224, convert to RGB, normalize [0,1] |
| **Vision Agent** | Loads model, runs `model.predict()`, returns label + probs |
| **Model** | VGG-based CNN, 4 classes: glioma, meningioma, no_tumor, pituitary |

---

## Data Flow

```
User uploads MRI
       │
       ▼
Flask receives multipart/form-data
       │
       ▼
Save to static/uploads/{uuid}_{filename}
       │
       ▼
Orchestrator.run(image_path, model, class_labels, uploaded_image_url)
       │
       ├──▶ QA Agent: {safe_to_infer, quality_score, warnings}
       │
       ├──▶ [if safe_to_infer] Vision Agent: {label, confidence, probs}
       │         │
       │         └── preprocess_image() → model.predict()
       │
       ├──▶ Report Agent: {findings, impression, next_steps, limitations, urgency}
       │
       ├──▶ Safety Gate: override report if needed, add disclaimer
       │
       ▼
Return JSON {request_id, qa, vision, report, artifacts, latency_ms}
       │
       ▼
React displays results dashboard
```

---

## API Contract

### POST /api/v1/analyze

**Request:** `multipart/form-data` with field `image` (PNG/JPG/JPEG, max 5 MB)

**Response (200):**
```json
{
  "request_id": "uuid",
  "qa": {"safe_to_infer": true, "quality_score": 0.25, "warnings": []},
  "vision": {"label": "no_tumor", "confidence": 0.85, "probs": {...}},
  "report": {"findings": "...", "impression": "...", "next_steps": [...], "limitations": "...", "urgency": "low"},
  "artifacts": {"uploaded_image_url": "/static/uploads/..."},
  "latency_ms": 123.45
}
```

When QA blocks inference, `vision` is `null` but response is still 200.

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| **3-agent pipeline** | Separation of concerns: quality check → inference → report. QA can short-circuit inference. |
| **Safety gate** | Ensures report is never misleading when QA fails or confidence is low. |
| **Deterministic report** | No LLM dependency; predictable, fast, no API costs. |
| **Vite proxy in dev** | Avoids CORS; frontend and backend run on different ports. |
| **UUID-prefixed filenames** | Prevents collisions, avoids path traversal. |

---

## Scalability Considerations

- **Stateless backend:** No session; each request is independent.
- **Model loaded once:** TensorFlow model loaded at startup, reused per request.
- **File storage:** Local disk; for scale, consider S3 or similar.
- **No queue:** Synchronous processing; for long inference, consider Celery/RQ.
