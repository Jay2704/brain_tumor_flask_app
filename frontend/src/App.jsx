/**
 * Medical MRI Diagnosis AI Agent - Interactive UI
 *
 * Features: drag-and-drop upload, loading state with progress steps,
 * results dashboard. Connects to POST /api/v1/analyze.
 */
import { useState, useRef } from 'react'

const API_URL = '/api/v1/analyze'

function formatLabel(label) {
  if (!label) return ''
  return label
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
}

function App() {
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const [loadingStep, setLoadingStep] = useState(0)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [view, setView] = useState('upload') // 'upload' | 'loading' | 'results' | 'tumor-types'
  const fileInputRef = useRef(null)

  const TUMOR_TYPES = [
    {
      name: 'Glioma',
      desc: 'Gliomas originate from glial cells—the supportive cells of the brain and spinal cord. They are the most common type of primary brain tumor, accounting for roughly one-third of all brain tumors.',
      details: [
        'Gliomas are graded I–IV based on growth rate and aggressiveness. Low-grade (I–II) tumors grow slowly; high-grade (III–IV) glioblastomas are aggressive and fast-growing.',
        'Common subtypes include astrocytomas, oligodendrogliomas, and glioblastomas. Glioblastoma multiforme (GBM) is the most aggressive and common malignant brain tumor in adults.',
        'Symptoms may include headaches, seizures, nausea, vision or speech changes, weakness, and cognitive decline. Location of the tumor affects which symptoms appear.',
        'Treatment typically involves surgery when possible, followed by radiation and chemotherapy. Prognosis varies widely by grade and subtype.',
      ],
    },
    {
      name: 'Meningioma',
      desc: 'Meningiomas arise from the meninges—the thin membranes (dura mater, arachnoid, pia mater) that surround the brain and spinal cord. They are usually benign and among the most common primary brain tumors.',
      details: [
        'About 90% of meningiomas are benign (grade I). They grow slowly and may not cause symptoms for years. Malignant meningiomas (grade III) are rare.',
        'They occur more often in women and in people over 60. Prior radiation to the head and certain genetic conditions can increase risk.',
        'Symptoms depend on size and location: headaches, seizures, vision changes, weakness, or personality changes. Some are discovered incidentally on imaging.',
        'Treatment options include observation for small, asymptomatic tumors; surgery for removal; and radiation when surgery is not feasible or for recurrence.',
      ],
    },
    {
      name: 'Pituitary',
      desc: 'Pituitary tumors develop in the pituitary gland, a small structure at the base of the brain that controls many hormones. Most pituitary tumors are benign adenomas and do not spread beyond the skull.',
      details: [
        'Pituitary adenomas can be functioning (produce excess hormones) or non-functioning. Functioning tumors may cause Cushing disease, acromegaly, or prolactin excess.',
        'The pituitary sits near the optic nerves, so tumors can cause vision loss, especially peripheral vision, and headaches. Hormone changes may cause fatigue, weight changes, or menstrual irregularities.',
        'Diagnosis often involves MRI, hormone blood tests, and visual field testing. Many small tumors are found incidentally.',
        'Treatment may include observation, medication (e.g., for prolactinomas), surgery (often transsphenoidal), and sometimes radiation.',
      ],
    },
    {
      name: 'No Tumor',
      desc: 'No abnormal mass or tumor is detected in the brain scan. The scan appears within normal limits for tumor screening purposes.',
      details: [
        'A "no tumor" result indicates that the AI did not identify signs of glioma, meningioma, or pituitary tumor in the analyzed image.',
        'This does not rule out all brain conditions. Other abnormalities (e.g., stroke, infection, cysts) may require different imaging or clinical evaluation.',
        'Always discuss results with a healthcare provider. AI analysis is for support only and should be reviewed by a qualified radiologist.',
      ],
    },
  ]

  const handleFileSelect = (selectedFile) => {
    if (!selectedFile) return
    if (!/\.(png|jpg|jpeg)$/i.test(selectedFile.name)) {
      setError('Please select a PNG, JPG, or JPEG image.')
      return
    }
    setError(null)
    setFile(selectedFile)
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setPreviewUrl(URL.createObjectURL(selectedFile))
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    const f = e.dataTransfer.files[0]
    if (f) handleFileSelect(f)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleAnalyze = async () => {
    if (!file) {
      setError('Please select an image first.')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)
    setView('loading')
    setLoadingStep(1)

    // Simulate step 1: Image validation (quick)
    await new Promise((r) => setTimeout(r, 400))
    setLoadingStep(2)

    try {
      const formData = new FormData()
      formData.append('image', file)

      const response = await fetch(API_URL, {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()
      setLoadingStep(3)

      if (!response.ok) {
        const msg = data?.error?.message || data?.error || `Request failed (${response.status})`
        throw new Error(msg)
      }

      setResult(data)
      await new Promise((r) => setTimeout(r, 400))
      setView('results')
    } catch (err) {
      setError(err.message || 'Analysis failed.')
      setView('upload')
    } finally {
      setLoading(false)
    }
  }

  const handleBack = () => {
    setView('upload')
    setResult(null)
    setFile(null)
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
      setPreviewUrl(null)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <button type="button" className="header-logo" onClick={() => setView('upload')}>
            <span className="logo-icon">🔬</span>
            <span>MRI Diagnosis AI</span>
          </button>
          <nav className="header-nav">
            <button type="button" className="nav-link" onClick={() => setView('tumor-types')}>
              Brain Tumor Types
            </button>
          </nav>
        </div>
        <div className="header-actions">
          <button type="button" className="btn-login">Login</button>
          <button type="button" className="btn-signup">Sign Up</button>
        </div>
      </header>

      <main className="main">
        {view === 'upload' && (
          <section className="upload-section">
            <h1>Medical MRI Diagnosis AI Agent</h1>
            <p className="subtitle">
              Upload your MRI scans for instant AI-powered clinical insights and preliminary analysis.
            </p>

            <div
              className={`dropzone ${file ? 'dropzone-has-file' : ''}`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".png,.jpg,.jpeg"
                onChange={(e) => handleFileSelect(e.target.files[0])}
                className="dropzone-input"
              />
              <span className="dropzone-icon">📤</span>
              <p className="dropzone-text">Drag and drop MRI files here</p>
              <p className="dropzone-hint">Supports JPEG and PNG. Max file size: 5MB</p>
              <button type="button" className="btn-upload" onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}>
                + Select Files to Upload
              </button>
              {file && (
                <p className="dropzone-filename">Selected: {file.name}</p>
              )}
            </div>

            <div className="feature-cards">
              <div className="feature-card">
                <span className="feature-icon">🛡️</span>
                <span>HIPAA Compliant</span>
              </div>
              <div className="feature-card">
                <span className="feature-icon">⏱</span>
                <span>{'<'} 30s Analysis</span>
              </div>
            </div>

            {error && (
              <div className="error-box">
                <strong>Error:</strong> {error}
              </div>
            )}

            <button
              type="button"
              className="btn-analyze"
              onClick={handleAnalyze}
              disabled={!file || loading}
            >
              Analyze Image
            </button>
          </section>
        )}

        {view === 'loading' && (
          <section className="loading-section">
            <div className="loading-badge">
              <span className="loading-dot" />
              AI ANALYSIS IN PROGRESS
            </div>
            <h2>Analyzing Image...</h2>
            <p className="loading-subtitle">Our neural network is processing the scan for anomalies.</p>

            <div className="loading-preview">
              {previewUrl && (
                <img src={previewUrl} alt="MRI scan" className="loading-img" />
              )}
              <div className="loading-border" />
            </div>

            <div className="progress-steps">
              <div className={`progress-step ${loadingStep >= 1 ? 'done' : ''}`}>
                <span className="step-icon">{loadingStep >= 1 ? '✓' : '○'}</span>
                <span>Image validation</span>
                {loadingStep >= 1 && <span className="step-status">SUCCESS</span>}
              </div>
              <div className={`progress-step ${loadingStep >= 2 ? 'active' : ''} ${loadingStep >= 3 ? 'done' : ''}`}>
                <span className="step-icon">
                  {loadingStep >= 3 ? '✓' : loadingStep >= 2 ? '●' : '○'}
                </span>
                <span>AI model inference{loadingStep === 2 && '...'}</span>
                {loadingStep >= 3 && <span className="step-status">SUCCESS</span>}
              </div>
              <div className={`progress-step ${loadingStep >= 3 ? 'done' : ''}`}>
                <span className="step-icon">{loadingStep >= 3 ? '✓' : '○'}</span>
                <span>Generating diagnostic report</span>
                {loadingStep >= 3 && <span className="step-status">SUCCESS</span>}
              </div>
            </div>

            <div className="loading-footer">
              <span>🛡️ HIPAA Compliant Processing</span>
            </div>
          </section>
        )}

        {view === 'results' && result && (
          <section className="results-section">
            <div className="results-header">
              <button type="button" className="btn-back" onClick={handleBack}>
                ← Back
              </button>
              <h2>MRI AI Diagnostic Dashboard</h2>
            </div>

            {(result.artifacts?.uploaded_image_url || previewUrl) && (
              <div className="card card-image">
                <h3>Scan Preview</h3>
                <img
                  src={result.artifacts?.uploaded_image_url || previewUrl}
                  alt="Uploaded MRI"
                  className="preview-img"
                />
              </div>
            )}

            {/* Primary Detection */}
            <div className="card card-prediction">
              <h3>Primary Detection</h3>
              {result.vision ? (
                <>
                  <p className="prediction-label">{formatLabel(result.vision.label)}</p>
                  <p className="prediction-confidence">
                    Confidence: {Math.round((result.vision.confidence || 0) * 100)}%
                  </p>
                </>
              ) : (
                <p className="prediction-inconclusive">Result: Inconclusive</p>
              )}
            </div>

            {/* QA */}
            {result.qa && (
              <div className="card">
                <h3>🛡️ Quality Assurance</h3>
                <div className="qa-grid">
                  <div className={`qa-block ${result.qa.safe_to_infer ? 'qa-yes' : 'qa-no'}`}>
                    <span className="qa-label">Safe to Infer</span>
                    <span className="qa-value">{result.qa.safe_to_infer ? 'Yes' : 'No'}</span>
                  </div>
                  <div className="qa-block">
                    <span className="qa-label">Quality Score</span>
                    <span className="qa-value">{Math.round((result.qa.quality_score || 0) * 100)}%</span>
                  </div>
                </div>
                <p className="qa-warnings">
                  <strong>Warnings:</strong>{' '}
                  {result.qa.warnings?.length ? result.qa.warnings.join(' • ') : 'No warnings'}
                </p>
              </div>
            )}

            {/* Probabilities */}
            {result.vision?.probs && Object.keys(result.vision.probs).length > 0 && (
              <div className="card">
                <h3>📊 Probability Breakdown</h3>
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

            {/* Report */}
            {result.report && (
              <div className="card">
                <h3>📄 AI Diagnostic Report</h3>
                {result.report.findings && (
                  <div className="report-section">
                    <h4>Findings</h4>
                    <p>{result.report.findings}</p>
                  </div>
                )}
                {result.report.impression && (
                  <div className="report-section">
                    <h4>Impression</h4>
                    <p>{result.report.impression}</p>
                  </div>
                )}
                {result.report.next_steps?.length > 0 && (
                  <div className="report-section">
                    <h4>Recommended Next Steps</h4>
                    <ul>
                      {result.report.next_steps.map((step, i) => (
                        <li key={i}>{step}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {result.report.limitations && (
                  <div className="report-section">
                    <h4>Limitations</h4>
                    <p>{result.report.limitations}</p>
                  </div>
                )}
                {result.report.urgency && (
                  <div className="report-section">
                    <h4>Urgency</h4>
                    <p>{formatLabel(result.report.urgency)}</p>
                  </div>
                )}
              </div>
            )}

            <button type="button" className="btn-new-scan" onClick={handleBack}>
              New Scan
            </button>
          </section>
        )}

        {view === 'tumor-types' && (
          <section className="tumor-types-page">
            <button type="button" className="btn-back" onClick={() => setView('upload')}>
              ← Back to Upload
            </button>
            <h1>Types of Brain Tumors</h1>
            <p className="tumor-types-intro">
              This AI model classifies MRI scans into the following categories. Understanding these types helps interpret analysis results.
            </p>
            <div className="tumor-types-grid">
              {TUMOR_TYPES.map((t) => (
                <article key={t.name} className="tumor-type-card">
                  <h2>{t.name}</h2>
                  <p className="tumor-type-desc">{t.desc}</p>
                  {t.details && (
                    <ul className="tumor-type-details">
                      {t.details.map((item, i) => (
                        <li key={i}>{item}</li>
                      ))}
                    </ul>
                  )}
                </article>
              ))}
            </div>
            <button type="button" className="btn-new-scan" onClick={() => setView('upload')}>
              Upload MRI Scan
            </button>
          </section>
        )}
      </main>

      <footer className="footer">
        <div className="footer-nav">
          <button type="button" className={`nav-item ${view === 'upload' ? 'active' : ''}`} onClick={() => setView('upload')}>
            Upload
          </button>
          <button type="button" className={`nav-item ${view === 'tumor-types' ? 'active' : ''}`} onClick={() => setView('tumor-types')}>
            Tumor Types
          </button>
          {view === 'results' && <span className="nav-item active">Results</span>}
        </div>
        <p className="disclaimer">
          ⚠️ For educational purposes only. Not a substitute for professional medical advice.
        </p>
      </footer>
    </div>
  )
}

export default App
