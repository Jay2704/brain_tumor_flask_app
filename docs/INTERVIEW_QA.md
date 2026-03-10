# Interview Questions & Answers — SDE 1 & SDE 2 Level

Interview preparation document for the Brain Tumor MRI Diagnosis AI project. Questions are categorized and tagged by level (SDE 1 / SDE 2).

---

## Table of Contents

1. [Project & Architecture](#1-project--architecture)
2. [Backend & API](#2-backend--api)
3. [Frontend & React](#3-frontend--react)
4. [ML & Deep Learning](#4-ml--deep-learning)
5. [System Design & Scalability](#5-system-design--scalability)
6. [Security & Best Practices](#6-security--best-practices)
7. [Testing & Debugging](#7-testing--debugging)
8. [Behavioral & Problem Solving](#8-behavioral--problem-solving)

---

## 1. Project & Architecture

### Q1.1: Walk me through the high-level architecture of this project. [SDE 1]

**Answer:**

The application is a full-stack medical imaging system with three main layers:

1. **Frontend (React + Vite):** Single-page application running on port 5173. Users upload MRI images via drag-and-drop, trigger analysis, and view results. The frontend communicates with the backend via REST API.

2. **Backend (Flask):** REST API on port 5001. Receives uploaded images, runs them through a 3-agent pipeline (QA → Vision → Report), and returns structured JSON. The pipeline includes:
   - **QA Agent:** Validates image quality (resolution, brightness, contrast)
   - **Vision Agent:** Runs CNN inference for tumor classification
   - **Report Agent:** Generates diagnostic report (findings, impression, next steps)
   - **Safety Gate:** Overrides report when QA fails or confidence is low

3. **Storage:** Uploaded images in `static/uploads/`, pre-trained VGG CNN model in `models/`.

Data flows: User → Frontend → POST /api/v1/analyze → Flask → Orchestrator → Agents → JSON response → Frontend renders results.

---

### Q1.2: Why did you choose a 3-agent pipeline instead of a single monolithic flow? [SDE 2]

**Answer:**

**Separation of concerns:** Each agent has a single responsibility. QA checks quality, Vision does inference, Report generates text. This makes the code easier to test, maintain, and extend.

**Fail-fast and short-circuit:** If QA determines the image is too small, dark, or low contrast (`safe_to_infer = false`), we skip the Vision agent entirely. This saves compute (no CNN inference on bad images) and avoids misleading predictions.

**Pluggability:** The Report agent can be swapped—e.g., replace the deterministic stub with an LLM-based report without changing QA or Vision. The Safety Gate ensures consistent behavior regardless of which report implementation is used.

**Observability:** Each agent produces structured output. We can log, monitor, or debug each stage independently.

---

### Q1.3: What is the Safety Gate and why is it important? [SDE 1]

**Answer:**

The Safety Gate is a post-processing step that overrides the report when certain conditions are met:

1. **QA fails:** If `safe_to_infer` is false (image too small, too dark, etc.), the report is overridden to "Inconclusive due to image quality" with appropriate next steps.

2. **Low confidence:** If the model's confidence is below 60%, the report is overridden to "Uncertain classification" with recommendations for repeat imaging or expert review.

3. **Disclaimer:** Always appends "Educational demo only. Not medical advice." to the limitations field.

**Why it matters:** In a medical context, we must avoid presenting high-confidence predictions when the input is poor or the model is uncertain. The Safety Gate ensures the output is never misleading.

---

## 2. Backend & API

### Q2.1: Explain the request flow for POST /api/v1/analyze. [SDE 1]

**Answer:**

1. **Validation:** Check that `image` is present in `request.files`, filename is non-empty, extension is PNG/JPG/JPEG, and file size is under 5 MB.

2. **Save file:** Generate a UUID-prefixed filename (e.g., `uuid_originalname.jpg`), save to `static/uploads/` to avoid collisions and path traversal.

3. **Model check:** If the model failed to load at startup, return 503 MODEL_UNAVAILABLE.

4. **Orchestration:** Call `orchestrate(image_path, model, CLASS_LABELS, uploaded_image_url)`:
   - QA Agent runs first
   - If `safe_to_infer`, Vision Agent runs; else vision is skipped
   - Report Agent runs with QA + vision (or empty vision)
   - Safety Gate applies overrides

5. **Response:** Return JSON with `request_id`, `qa`, `vision`, `report`, `artifacts`, `latency_ms`. If QA blocks inference, `vision` is null but the response is still 200.

6. **Error handling:** On exception, log and return 500 with a standardized error payload.

---

### Q2.2: How do you handle CORS and why is it needed? [SDE 1]

**Answer:**

**What:** CORS (Cross-Origin Resource Sharing) allows the React app (running on `http://localhost:5173`) to make requests to the Flask backend (running on `http://localhost:5001`). Without CORS, the browser blocks these cross-origin requests.

**How:** We use `@app.after_request` to add CORS headers for API routes:
- `Access-Control-Allow-Origin: *` (for dev; in production restrict to specific domains)
- `Access-Control-Allow-Headers: Content-Type`
- `Access-Control-Allow-Methods: GET, POST, OPTIONS`

We also handle OPTIONS preflight requests in `@app.before_request`—browsers send OPTIONS before POST for cross-origin requests, and we return 204 with the appropriate headers.

**Alternative:** In development, Vite proxies `/api` and `/healthz` to the backend, so the browser sees same-origin requests. CORS is still enabled for when the frontend is served from a different origin (e.g., production).

---

### Q2.3: Why use UUID-prefixed filenames for uploads? [SDE 1]

**Answer:**

1. **Uniqueness:** Prevents collisions when multiple users upload files with the same name (e.g., `mri.jpg`).

2. **Security:** `secure_filename` alone can still allow problematic names. UUID prefix adds an extra layer and makes it harder to guess or enumerate upload paths.

3. **Traceability:** The `request_id` in the orchestrator can be linked to the filename for debugging.

4. **Path traversal:** Prevents attacks like `../../../etc/passwd` by ensuring the stored filename always starts with a UUID.

---

### Q2.4: How would you add rate limiting to the API? [SDE 2]

**Answer:**

Use Flask-Limiter:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app=app, key_func=get_remote_address)

@app.route("/api/v1/analyze", methods=["POST"])
@limiter.limit("10 per minute")  # 10 requests per minute per IP
def api_v1_analyze():
    ...
```

**Considerations:**
- Key by IP: `get_remote_address` (or by API key if authenticated)
- Limits: e.g., 10/minute for analyze to prevent abuse
- Storage: Redis for distributed rate limiting in production
- Response: 429 Too Many Requests with `Retry-After` header

---

## 3. Frontend & React

### Q3.1: How do you manage state in this React app? [SDE 1]

**Answer:**

We use React's built-in `useState` for local component state:

- **View state:** `view` (home, upload, loading, results, tumor-types, login, signup) determines which section is rendered.
- **File state:** `file`, `previewUrl` for the selected image.
- **Analysis state:** `loading`, `loadingStep`, `error`, `result` for the API call and response.
- **Auth state:** `loginEmail`, `loginPassword`, etc., for form inputs.
- **UI state:** `darkMode`, `showLoginPassword`, etc.

No Redux or Context—the app is a single component tree, and state is lifted to `App.jsx`. For a larger app, we might use Context for theme or React Query for server state.

---

### Q3.2: How does the frontend handle the async API call and loading states? [SDE 1]

**Answer:**

1. **Before request:** Set `loading = true`, `view = 'loading'`, `loadingStep = 1`. Clear any previous error/result.

2. **Simulated steps:** We simulate "Image validation" (400ms) and "AI inference" (actual fetch) to show progress. `loadingStep` increments: 1 → 2 → 3.

3. **Fetch:** `fetch(API_URL, { method: 'POST', body: formData })`. On success, parse JSON, set `loadingStep = 3`, wait 400ms, then set `result` and `view = 'results'`.

4. **Error handling:** On `!response.ok` or catch, set `error` and `view = 'upload'`. User sees the error message and can retry.

5. **Finally:** `setLoading(false)` in a `finally` block so loading is always cleared.

---

### Q3.3: Why use Vite instead of Create React App? [SDE 2]

**Answer:**

- **Speed:** Vite uses native ES modules and esbuild for dev, so startup and HMR are much faster than CRA's Webpack-based setup.
- **Proxy:** Simple proxy config in `vite.config.js` for `/api`, `/healthz`, `/static`—no need for `http-proxy-middleware`.
- **Build:** Rollup-based production build with tree-shaking and code splitting.
- **Modern:** CRA is in maintenance mode; Vite is the recommended default for new React projects.

---

## 4. ML & Deep Learning

### Q4.1: Describe the CNN model and preprocessing pipeline. [SDE 1]

**Answer:**

**Model:** VGG-based CNN (Keras .h5), trained for 4-class brain tumor classification.

**Input:** `(1, 224, 224, 3)` — batch of 1, 224×224 pixels, RGB.

**Preprocessing (`ml/preprocess.py`):**
1. Open image with PIL, convert to RGB.

2. Resize to 224×224 (required by the model).

3. Normalize pixel values: `img_array / 255.0` → range [0, 1].

4. Add batch dimension: `expand_dims(..., axis=0)`.

**Output:** Softmax probabilities for each class. We take `argmax` for the label and the max value for confidence.

---

### Q4.2: What is the QA Agent checking and why? [SDE 1]

**Answer:**

The QA Agent performs image quality checks:

1. **Resolution:** `min(w, h) >= 150`. Smaller images may not have enough detail for reliable inference.

2. **Brightness:** Mean pixel value < 0.15 → "too dark"; > 0.90 → "too bright". Extreme values can affect model performance.

3. **Contrast:** Std dev < 0.05 → "low contrast". Flat images provide little discriminative information.

4. **Quality score:** `quality_score = clip(std_val, 0, 1)` — used in the report and as a proxy for image quality.

**Why:** Poor-quality images can lead to misleading predictions. QA acts as a gate before expensive inference.

---

### Q4.3: How would you improve model accuracy or add explainability? [SDE 2]

**Answer:**

**Accuracy:**
- Data augmentation (rotation, flip, brightness)
- Transfer learning (fine-tune a pre-trained ResNet, EfficientNet)
- Ensemble of multiple models
- More training data, especially for rare classes

**Explainability:**
- **Grad-CAM:** Generate heatmaps showing which regions the model focused on. Useful for radiologists to validate.
- **Saliency maps:** Similar idea, different visualization.
- **LIME/SHAP:** Model-agnostic explanations (slower, more complex).

Implementation: TensorFlow/Keras supports Grad-CAM via custom layers. We could add an endpoint that returns the heatmap overlay URL alongside the prediction.

---

## 5. System Design & Scalability

### Q5.1: How would you scale this system to handle 1000 concurrent users? [SDE 2]

**Answer:**

**Bottlenecks:** CPU-bound inference (TensorFlow), single Flask process, local file storage.

**Approaches:**

1. **Horizontal scaling:** Run multiple Flask workers (Gunicorn/uWSGI) behind a load balancer. Each worker loads its own model (memory-intensive) or we use a shared model server.

2. **Async inference:** Offload inference to a queue (Celery, Redis Queue). API returns immediately with a `request_id`; client polls or uses webhooks for results. This decouples upload from inference.

3. **Model serving:** Use TensorFlow Serving or a dedicated inference service. Flask workers become thin; they call the inference service via gRPC/HTTP.

4. **Storage:** Move uploads to S3 or similar. Use a CDN for serving images. Reduces disk I/O on app servers.

5. **Caching:** Cache results by image hash for identical uploads.

6. **Database:** Store analysis history in PostgreSQL for audit, history, and analytics.

---

### Q5.2: How would you add a history feature for past analyses? [SDE 2]

**Answer:**

**Backend:**
- Add a table: `analyses(id, request_id, user_id?, image_path, created_at, qa, vision, report)`.
- After orchestration, persist the result to the DB.
- Add `GET /api/v1/results/{request_id}` to fetch a past result.
- Add `GET /api/v1/history?limit=20` to list recent analyses (with optional user_id if we add auth).

**Frontend:**
- Add a "History" view that fetches `/api/v1/history` and displays thumbnails + predictions.
- Clicking an item fetches `/api/v1/results/{request_id}` and shows the full report.

**Storage:** Use SQLite for simplicity; PostgreSQL for production. Consider purging old uploads after N days to save disk.

---

## 6. Security & Best Practices

### Q6.1: What security measures are in place for file uploads? [SDE 1]

**Answer:**

1. **Extension whitelist:** Only PNG, JPG, JPEG allowed. Prevents executable uploads.

2. **File size limit:** `MAX_CONTENT_LENGTH = 5 MB` — Flask rejects larger requests before processing.

3. **Secure filenames:** `secure_filename()` from Werkzeug removes path components and dangerous characters.

4. **UUID prefix:** Prevents overwriting and guessing.

5. **Storage location:** Files saved to `static/uploads/` (not executable directory). In production, ensure uploads are not served as executable.

**Additional:** Could add magic-byte validation (verify file is actually an image), virus scanning, and rate limiting per IP.

---

### Q6.2: What if the model is used for malicious purposes (e.g., fake medical reports)? [SDE 2]

**Answer:**

**Mitigations:**
- **Disclaimer:** Every report includes "Educational demo only. Not medical advice." to set expectations.
- **No PHI:** We don't store patient names or IDs. Only image + result.
- **Audit logging:** Log request_id, IP, timestamp for audit trail.
- **Rate limiting:** Prevents bulk abuse.
- **Access control:** Add authentication (API key, OAuth) for production; restrict who can use the API.
- **Watermarking:** Optional: add a visible "AI-generated, for educational use" watermark on exported PDFs.

**Responsibility:** As developers, we ensure the system is clearly labeled and not misrepresented. Legal compliance (FDA, HIPAA) depends on deployment context.

---

## 7. Testing & Debugging

### Q7.1: How do you test the backend without the actual model file? [SDE 1]

**Answer:**

We use **mocking** with `unittest.mock.patch`:

```python
@patch('app.model', MagicMock(predict=lambda x: np.array([[0.1, 0.2, 0.6, 0.1]])))
def test_analyze_returns_success(client, sample_image):
    response = client.post("/api/v1/analyze", data={"image": sample_image})
    assert response.status_code == 200
```

The mock replaces `app.model` with a fake object whose `predict` returns a fixed array. We don't need the .h5 file, and tests run quickly.

**Benefits:** Tests are isolated, fast, and deterministic. We can test error paths (e.g., `model = None`) by patching with `None`.

---

### Q7.2: How would you debug a failing inference in production? [SDE 2]

**Answer:**

1. **Logging:** Add structured logs (request_id, stage, timing, error) at each step. Use a logging library like `structlog` for JSON logs.

2. **Request ID:** Pass `request_id` through the response and logs. When a user reports an issue, we can trace the full flow.

3. **Error capture:** On exception, log the full traceback, request_id, and image path. Consider Sentry or similar for aggregation.

4. **Reproducibility:** Save the failed image (with request_id) for offline debugging. Run the same image through the pipeline locally.

5. **Health checks:** `/healthz` confirms model is loaded. Add a readiness probe that runs a dummy inference to verify the model is responsive.

6. **Metrics:** Track latency percentiles, error rates, QA failure rate. Alert on anomalies.

---

## 8. Behavioral & Problem Solving

### Q8.1: Describe a challenging technical problem you solved in this project. [SDE 1]

**Answer:**

**Problem:** When QA fails, we shouldn't run the Vision agent. But the Report agent still needs to produce a useful output. The frontend also expected a consistent response shape.

**Solution:** 
- Orchestrator checks `safe_to_infer`.
- If false, set `vision = None` and call Report with `qa` and empty `{}`.
- Report agent has explicit logic for when vision is empty or missing—it returns "Inconclusive due to image quality" with appropriate next steps.
- Safety Gate reinforces this when QA fails.
- Frontend handles `vision === null` by showing "Inconclusive" in the Primary Detection card.

**Learning:** Designing for failure cases upfront (graceful degradation) prevents edge-case bugs and improves UX.

---

### Q8.2: How would you add an LLM-based report while keeping the system reliable? [SDE 2]

**Answer:**

1. **New Report Agent:** Create `report_agent_llm.py` that calls OpenAI/Anthropic with a structured prompt (QA + vision summary). Parse the response into JSON (findings, impression, next_steps, etc.).

2. **Fallback:** If the LLM call fails (timeout, rate limit, parse error), fall back to the deterministic stub. The orchestrator catches exceptions and calls the stub.

3. **Config:** Use an env var `USE_LLM_REPORT=true/false` to switch. Default to false for reliability.

4. **Validation:** Validate LLM output structure before returning. If it doesn't match the schema, use the stub.

5. **Cost/latency:** LLM adds 1–5s and cost per request. Consider caching for identical inputs.

6. **Safety:** Always run the Safety Gate after the report—it overrides when QA fails or confidence is low, regardless of report source.

---

### Q8.3: If you had more time, what would you improve? [SDE 1]

**Answer:**

- **Testing:** Add integration tests with a real model, add frontend E2E tests (Playwright/Cypress).
- **History:** Persist analyses to a database, add a History view.
- **LLM report:** Replace the stub with an LLM for richer, more natural reports.
- **DICOM support:** Accept DICOM files for real radiology workflows.
- **Explainability:** Add Grad-CAM heatmaps to show model attention.
- **Auth:** Implement Login/Sign Up with JWT for the Physician Portal.
- **Performance:** Add model caching, result caching, async inference.

---

## Quick Reference

| Topic | Key Points |
|-------|------------|
| **Architecture** | 3-agent pipeline (QA → Vision → Report) + Safety Gate |
| **Tech** | React, Vite, Flask, TensorFlow, Pillow, NumPy |
| **API** | POST /api/v1/analyze, GET /healthz |
| **Model** | VGG CNN, 224×224 RGB, 4 classes |
| **Security** | Extension whitelist, size limit, secure_filename, UUID prefix |
| **Testing** | pytest, mock model, no .h5 required |
