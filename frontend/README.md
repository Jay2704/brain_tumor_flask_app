# Medical MRI Diagnosis AI Agent - React Frontend

Minimal React frontend for the Brain Tumor Detection Flask API.

## Prerequisites

- Node.js 18+
- Flask backend running at `http://127.0.0.1:5001`

## Run the Frontend

```bash
# Install dependencies
npm install

# Create local environment file
cp .env.example .env

# Start the dev server (runs on http://localhost:5173)
npm run dev
```

## Environment Variables

Create a `.env` file in `frontend/` (you can copy from `.env.example`):

```bash
cp .env.example .env
```

Set:

```env
VITE_API_BASE_URL=http://127.0.0.1:5001
```

For local development, keep this pointed to your Flask backend.

The Vite dev server proxies `/api`, `/healthz`, and `/static` to the Flask backend, so API calls and image previews work without CORS issues.

## Start the Backend First

From the project root:

```bash
python app.py
```

Then run `npm run dev` in the `frontend/` folder.

## Build for Production

```bash
npm run build
```

Output is in `dist/`. Serve it with any static file server, or point the Flask app to serve the built files.
