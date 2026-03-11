import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // GitHub Pages repository base path.
  base: '/brain_tumor_detection/',
  server: {
    port: 5173,
    proxy: {
      // Optional: proxy API calls to avoid CORS during dev (backend has CORS enabled anyway)
      '/api': 'http://127.0.0.1:5001',
      '/healthz': 'http://127.0.0.1:5001',
      '/static': 'http://127.0.0.1:5001',
    },
  },
})
