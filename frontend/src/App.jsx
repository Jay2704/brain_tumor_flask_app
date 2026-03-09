/**
 * Medical MRI Diagnosis AI Agent - Main App Component
 *
 * This single-page app lets users upload an MRI image and view the analysis
 * from the Flask backend API (POST /api/v1/analyze).
 */
import { useState } from 'react'

// Backend API URL - uses proxy in dev (vite.config.js)
const API_URL = '/api/v1/analyze'

/**
 * Convert backend labels (e.g. no_tumor, glioma) to display text (No Tumor, Glioma)
 */
function formatLabel(label) {
  if (!label) return ''
  return label
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
}

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

        {error && (
          <div className="error-box">
            <strong>Error:</strong> {error}
          </div>
        )}

        {result && (
          <div className="results">
            {/* Prediction Result - prominent summary card */}
            <div className="card card-prediction">
              <h2>Prediction Result</h2>
              {result.vision ? (
                <>
                  <p className="prediction-label">Detected Type: {formatLabel(result.vision.label)}</p>
                  <p className="prediction-confidence">
                    Confidence: {Math.round((result.vision.confidence || 0) * 100)}%
                  </p>
                </>
              ) : (
                <p className="prediction-inconclusive">Result: Inconclusive</p>
              )}
            </div>

            {/* QA Card */}
            {result.qa && (
              <div className="card">
                <h3>Image Quality</h3>
                <p><strong>Safe to Infer:</strong> {result.qa.safe_to_infer ? 'Yes' : 'No'}</p>
                <p><strong>Quality Score:</strong> {Math.round((result.qa.quality_score || 0) * 100)}%</p>
                <p><strong>Warnings:</strong></p>
                <ul>
                  {result.qa.warnings?.length
                    ? result.qa.warnings.map((w, i) => <li key={i}>{w}</li>)
                    : <li>No warnings</li>}
                </ul>
              </div>
            )}

            {/* Probabilities - with progress bars */}
            {result.vision?.probs && Object.keys(result.vision.probs).length > 0 && (
              <div className="card">
                <h3>Class Probabilities</h3>
                <div className="prob-list">
                  {Object.entries(result.vision.probs)
                    .sort((a, b) => b[1] - a[1])
                    .map(([label, prob]) => {
                      const pct = Math.round(prob * 100)
                      const isHighest = label === result.vision.label
                      return (
                        <div key={label} className={`prob-item ${isHighest ? 'prob-item-highlight' : ''}`}>
                          <div className="prob-header">
                            <span>{formatLabel(label)}</span>
                            <span>{pct}%</span>
                          </div>
                          <div className="prob-bar">
                            <div className="prob-fill" style={{ width: `${pct}%` }} />
                          </div>
                        </div>
                      )
                    })}
                </div>
              </div>
            )}

            {/* Report Card */}
            {result.report && (
              <div className="card">
                <h3>Report</h3>
                <div className="report-section">
                  <h4>Findings</h4>
                  <p>{result.report.findings}</p>
                </div>
                <div className="report-section">
                  <h4>Impression</h4>
                  <p>{result.report.impression}</p>
                </div>
                <div className="report-section">
                  <h4>Recommended Next Steps</h4>
                  <ul>
                    {result.report.next_steps?.map((step, i) => (
                      <li key={i}>{step}</li>
                    ))}
                  </ul>
                </div>
                <div className="report-section">
                  <h4>Limitations</h4>
                  <p>{result.report.limitations}</p>
                </div>
                <div className="report-section">
                  <h4>Urgency</h4>
                  <p>{formatLabel(result.report.urgency)}</p>
                </div>
              </div>
            )}

            {/* Image Preview */}
            {result.artifacts?.uploaded_image_url && (
              <div className="card">
                <h3>Uploaded Image</h3>
                <img
                  src={result.artifacts.uploaded_image_url}
                  alt="Uploaded MRI"
                  className="preview-img"
                />
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}

export default App
