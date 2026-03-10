# Brain Tumor MRI Diagnosis AI — Complete Workflow

## End-to-End User Journey

```
1. User opens app (http://127.0.0.1:5173)
2. Lands on Home screen
3. Clicks "Upload MRI Image" or navigates to Diagnosis AI
4. Selects/drops MRI file (PNG/JPG/JPEG, max 5 MB)
5. Clicks "Analyze Image"
6. Sees loading state (Image validation → AI inference → Report)
7. Views results: prediction, QA, probabilities, report, model info
8. Optional: Download PDF report
```

---

## Detailed Workflow

### Phase 1: Upload

| Step | Actor | Action |
|------|-------|--------|
| 1.1 | User | Drags file or clicks "Select Files to Upload" |
| 1.2 | Frontend | Validates: PNG/JPG/JPEG, displays filename |
| 1.3 | User | Clicks "Analyze Image" |
| 1.4 | Frontend | Sets `view = 'loading'`, `loadingStep = 1` |
| 1.5 | Frontend | Builds `FormData`, appends `image` file |
| 1.6 | Frontend | Sends `POST /api/v1/analyze` to backend |

### Phase 2: Backend Processing

| Step | Component | Action |
|------|------------|--------|
| 2.1 | Flask | Receives multipart request |
| 2.2 | Flask | Validates: `image` present, allowed extension, filename |
| 2.3 | Flask | Saves to `static/uploads/{uuid}_{filename}` |
| 2.4 | Flask | Calls `orchestrate(image_path, model, CLASS_LABELS, uploaded_image_url)` |
| 2.5 | Orchestrator | Generates `request_id`, starts timer |
| 2.6 | **QA Agent** | Opens image with PIL, checks: |
| | | • min(w,h) >= 150 |
| | | • mean brightness not too dark/bright |
| | | • std (contrast) not too low |
| | | Returns `{safe_to_infer, quality_score, warnings}` |
| 2.7 | Orchestrator | If `safe_to_infer` is False → skip Vision, run Report with empty vision |
| 2.8 | **Vision Agent** | If safe: preprocess (224×224 RGB, /255), `model.predict()` |
| | | Returns `{label, confidence, probs}` |
| 2.9 | **Report Agent** | Generates `{findings, impression, next_steps, limitations, urgency}` |
| | | Based on QA + vision; handles low confidence, QA failure |
| 2.10 | **Safety Gate** | Overrides report if QA failed or confidence < 0.60 |
| | | Always adds disclaimer to limitations |
| 2.11 | Orchestrator | Builds `{request_id, qa, vision, report, artifacts, latency_ms}` |
| 2.12 | Flask | Returns JSON 200 |

### Phase 3: Results Display

| Step | Component | Action |
|------|------------|--------|
| 3.1 | Frontend | Receives JSON response |
| 3.2 | Frontend | Sets `loadingStep = 3`, waits 400ms |
| 3.3 | Frontend | Sets `view = 'results'`, `result = data` |
| 3.4 | Frontend | Renders: |
| | | • Scan preview (from artifacts.uploaded_image_url) |
| | | • Primary Detection card (label, confidence with color band) |
| | | • QA card (Safe to Infer, Quality Score, warnings) |
| | | • Probability breakdown (bars + percentages) |
| | | • AI Diagnostic Report (findings, impression, next_steps, etc.) |
| | | • Model info (VGG CNN, inference time) |
| | | • Download PDF button |

### Phase 4: Optional Actions

| Action | Flow |
|--------|------|
| **Download PDF** | jsPDF builds report from result, `doc.save(filename)` |
| **New Scan** | `handleBack()` → clear file, result, set view = 'upload' |
| **Navigate** | Home, Diagnosis AI, Tumor Types, Login, Sign Up |

---

## Agent Pipeline (Backend)

```
                    ┌──────────────────┐
                    │   QA Agent       │
                    │   run(image_path)│
                    └────────┬─────────┘
                             │
                    {safe_to_infer, quality_score, warnings}
                             │
              ┌──────────────┴──────────────┐
              │ safe_to_infer?              │
              └──────────────┬──────────────┘
                    │                    │
                   YES                   NO
                    │                    │
                    ▼                    │
         ┌──────────────────┐           │
         │  Vision Agent    │           │
         │  run(image_path, │           │
         │  model, labels)  │           │
         └────────┬─────────┘           │
                  │                     │
         {label, confidence, probs}     │
                  │                     │
                  └──────────┬──────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Report Agent    │
                    │  run(qa, vision) │
                    └────────┬─────────┘
                             │
                    {findings, impression, next_steps, ...}
                             │
                             ▼
                    ┌──────────────────┐
                    │  Safety Gate     │
                    │  apply(qa, vision,│
                    │  report)         │
                    └────────┬─────────┘
                             │
                    Final report (with overrides if needed)
```

---

## Error Handling

| Scenario | Backend | Frontend |
|----------|---------|----------|
| No file | 400 MISSING_FILE | — |
| Invalid extension | 400 UNSUPPORTED_EXTENSION | Client also validates |
| File too large | 413 FILE_TOO_LARGE | — |
| Model not loaded | 503 MODEL_UNAVAILABLE | — |
| Processing exception | 500 INTERNAL_SERVER_ERROR | Shows error message, view = 'upload' |
| QA blocks inference | 200, vision=null | Shows "Inconclusive", report still displayed |

---

## Key Data Structures

### QA Output
```python
{"safe_to_infer": bool, "quality_score": float, "warnings": [str]}
```

### Vision Output
```python
{"label": str, "confidence": float, "probs": {str: float}}
```

### Report Output
```python
{"findings": str, "impression": str, "next_steps": [str], "limitations": str, "urgency": str}
```

### Full API Response
```python
{
  "request_id": str,
  "qa": {...},
  "vision": {...} or None,
  "report": {...},
  "artifacts": {"uploaded_image_url": str},
  "latency_ms": float
}
```
