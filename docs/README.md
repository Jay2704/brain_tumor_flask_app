# Brain Tumor MRI Diagnosis AI — Documentation

Documentation for interview preparation and project overview.

---

## Documents

| Document | Description |
|----------|-------------|
| **[ARCHITECTURE.md](./ARCHITECTURE.md)** | System architecture, component diagram, data flow, API contract |
| **[TECH_STACK.md](./TECH_STACK.md)** | Technologies used (React, Flask, TensorFlow, etc.), project structure |
| **[WORKFLOW.md](./WORKFLOW.md)** | End-to-end workflow, agent pipeline, error handling, data structures |
| **[INTERVIEW_QA.md](./INTERVIEW_QA.md)** | Interview Q&A for SDE 1 & SDE 2 — architecture, backend, frontend, ML, system design, security, testing |

---

## Quick Reference

**What it does:** Classifies brain MRI scans into 4 categories (glioma, meningioma, pituitary, no tumor) using a VGG-based CNN.

**Stack:** React + Vite (frontend) | Flask + TensorFlow (backend) | 3-agent pipeline (QA → Vision → Report) + Safety Gate

**Key endpoints:** `POST /api/v1/analyze`, `GET /healthz`

**Model:** VGG CNN, 224×224 RGB input, 4 classes, ~94% validation accuracy
