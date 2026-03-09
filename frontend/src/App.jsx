/**
 * Medical MRI Diagnosis AI Agent - Main App Component
 *
 * This single-page app lets users upload an MRI image and view the analysis
 * from the Flask backend API (POST /api/v1/analyze).
 */
import { useState } from 'react'

// Backend API URL - uses proxy in dev (vite.config.js) or direct URL
const API_URL = '/api/v1/analyze'

function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setError(null)
    setResult(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setError('Please select an image first.')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('image', file)

      const response = await fetch(API_URL, {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        const msg = data?.error?.message || data?.error || `Request failed (${response.status})`
        throw new Error(msg)
      }

      setResult(data)
    } catch (err) {
      setError(err.message || 'Analysis failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header>
        <h1>Medical MRI Diagnosis AI Agent</h1>
      </header>

      <main>
        {/* Upload form */}
        <form onSubmit={handleSubmit} className="upload-form">
          <input
            type="file"
            accept=".png,.jpg,.jpeg"
            onChange={handleFileChange}
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </form>

        {/* Error state */}
        {error && (
          <div className="error-box">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="results">
            <h2>Analysis Result</h2>
            {result.request_id && (
              <p className="meta">Request ID: {result.request_id}</p>
            )}
            {result.latency_ms != null && (
              <p className="meta">Latency: {result.latency_ms} ms</p>
            )}

            {/* QA Result */}
            {result.qa && (
              <section className="result-section">
                <h3>QA Result</h3>
                <ul>
                  <li><strong>safe_to_infer:</strong> {String(result.qa.safe_to_infer)}</li>
                  <li><strong>quality_score:</strong> {result.qa.quality_score}</li>
                  <li>
                    <strong>warnings:</strong>{' '}
                    {result.qa.warnings?.length
                      ? result.qa.warnings.join(', ')
                      : 'None'}
                  </li>
                </ul>
              </section>
            )}

            {/* Vision Result */}
            {result.vision != null && (
              <section className="result-section">
                <h3>Vision Result</h3>
                <ul>
                  <li><strong>label:</strong> {result.vision.label}</li>
                  <li><strong>confidence:</strong> {result.vision.confidence}</li>
                  <li>
                    <strong>probs:</strong>
                    <pre>{JSON.stringify(result.vision.probs, null, 2)}</pre>
                  </li>
                </ul>
              </section>
            )}
            {result.vision === null && (
              <section className="result-section">
                <h3>Vision Result</h3>
                <p className="muted">Inference skipped (QA blocked)</p>
              </section>
            )}

            {/* Report */}
            {result.report && (
              <section className="result-section">
                <h3>Report</h3>
                <ul>
                  <li><strong>findings:</strong> {result.report.findings}</li>
                  <li><strong>impression:</strong> {result.report.impression}</li>
                  <li>
                    <strong>next_steps:</strong>
                    <ul>
                      {result.report.next_steps?.map((step, i) => (
                        <li key={i}>{step}</li>
                      ))}
                    </ul>
                  </li>
                  <li><strong>limitations:</strong> {result.report.limitations}</li>
                  <li><strong>urgency:</strong> {result.report.urgency}</li>
                </ul>
              </section>
            )}

            {/* Artifacts - uploaded image preview */}
            {result.artifacts?.uploaded_image_url && (
              <section className="result-section">
                <h3>Artifacts</h3>
                <p>Uploaded image preview:</p>
                <img
                  src={result.artifacts.uploaded_image_url}
                  alt="Uploaded MRI"
                  className="preview-img"
                />
              </section>
            )}
          </div>
        )}
      </main>
    </div>
  )
}

export default App
