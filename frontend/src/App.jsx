/**
 * Brain Tumor Detection Using AI - Interactive UI
 *
 * Features: drag-and-drop upload, loading state with progress steps,
 * results dashboard, dark mode, PDF export. Connects to POST /api/v1/analyze.
 */
import { useState, useRef, useEffect } from 'react'
import { jsPDF } from 'jspdf'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

function formatLabel(label) {
  if (!label) return ''
  return label
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
}

function getConfidenceBand(confidence) {
  if (confidence >= 0.8) return 'high'
  if (confidence >= 0.6) return 'medium'
  return 'low'
}

function exportReportToPdf(result, previewUrl) {
  const doc = new jsPDF()
  const margin = 20
  let y = 20
  const lineHeight = 7
  const sectionGap = 10

  const addText = (text, size = 10) => {
    doc.setFontSize(size)
    const lines = doc.splitTextToSize(text, 170)
    lines.forEach((line) => {
      if (y > 270) {
        doc.addPage()
        y = 20
      }
      doc.text(line, margin, y)
      y += lineHeight
    })
  }

  const addSection = (title, content) => {
    if (y > 250) {
      doc.addPage()
      y = 20
    }
    doc.setFontSize(12)
    doc.setFont(undefined, 'bold')
    doc.text(title, margin, y)
    y += lineHeight
    doc.setFont(undefined, 'normal')
    doc.setFontSize(10)
    if (content && String(content).trim()) addText(String(content))
    y += sectionGap
  }

  doc.setFontSize(18)
  doc.setFont(undefined, 'bold')
  doc.text('MRI AI Diagnostic Report', margin, y)
  y += lineHeight + 2

  doc.setFontSize(10)
  doc.setFont(undefined, 'normal')
  doc.text(`Report ID: ${result.request_id || 'N/A'}`, margin, y)
  y += lineHeight
  doc.text(`Generated: ${new Date().toLocaleString()}`, margin, y)
  y += sectionGap + 5

  if (result.vision) {
    addSection('Primary Detection', `${formatLabel(result.vision.label)} (Confidence: ${Math.round((result.vision.confidence || 0) * 100)}%)`)
  } else {
    addSection('Primary Detection', 'Inconclusive')
  }

  if (result.qa) {
    addSection('Quality Assurance', `Safe to Infer: ${result.qa.safe_to_infer ? 'Yes' : 'No'} | Quality Score: ${Math.round((result.qa.quality_score || 0) * 100)}%`)
    if (result.qa.warnings?.length) {
      addText(`Warnings: ${result.qa.warnings.join('; ')}`)
      y += sectionGap
    }
  }

  if (result.vision?.probs && Object.keys(result.vision.probs).length > 0) {
    const probs = Object.entries(result.vision.probs)
      .sort((a, b) => b[1] - a[1])
      .map(([label, p]) => `${formatLabel(label)}: ${Math.round(p * 100)}%`)
      .join(', ')
    addSection('Probability Breakdown', probs)
  }

  if (result.report) {
    if (result.report.findings) addSection('Findings', result.report.findings)
    if (result.report.impression) addSection('Impression', result.report.impression)
    if (result.report.next_steps?.length) {
      addSection('Recommended Next Steps', result.report.next_steps.join('\n• '))
    }
    if (result.report.limitations) addSection('Limitations', result.report.limitations)
    if (result.report.urgency) addSection('Urgency', formatLabel(result.report.urgency))
  }

  addSection('Disclaimer', 'For educational purposes only. Not a substitute for professional medical advice. Results should be reviewed by a qualified radiologist.')

  const filename = `MRI_Report_${result.request_id || Date.now()}.pdf`
  doc.save(filename)
}

function App() {
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const [loadingStep, setLoadingStep] = useState(0)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [view, setView] = useState('home') // 'home' | 'upload' | 'loading' | 'results' | 'tumor-types' | 'future-work' | 'login' | 'signup'
  const [darkMode, setDarkMode] = useState(() => {
    try {
      return localStorage.getItem('darkMode') === 'true'
    } catch {
      return false
    }
  })
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const fileInputRef = useRef(null)

  const handleNavClick = (viewName) => {
    setView(viewName)
    setSidebarOpen(false)
  }

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light')
    try {
      localStorage.setItem('darkMode', darkMode)
    } catch {}
  }, [darkMode])


  // Auth form state (placeholder - no backend)
  const [loginEmail, setLoginEmail] = useState('')
  const [loginPassword, setLoginPassword] = useState('')
  const [signupName, setSignupName] = useState('')
  const [signupEmail, setSignupEmail] = useState('')
  const [signupPassword, setSignupPassword] = useState('')
  const [signupConfirm, setSignupConfirm] = useState('')
  const [authMessage, setAuthMessage] = useState(null)
  const [showLoginPassword, setShowLoginPassword] = useState(false)
  const [showSignupPassword, setShowSignupPassword] = useState(false)
  const [showSignupConfirm, setShowSignupConfirm] = useState(false)

  const TUMOR_TYPES = [
    {
      name: 'Glioma',
      desc: 'Gliomas originate from glial cells—the supportive cells of the brain and spinal cord. They are the most common type of primary brain tumor, accounting for roughly one third of all brain tumors.',
      details: [
        'Gliomas are graded I–IV based on growth rate and aggressiveness. Low grade (I–II) tumors grow slowly; high grade (III–IV) glioblastomas are aggressive and fast growing.',
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
        'Pituitary adenomas can be functioning (produce excess hormones) or nonfunctioning. Functioning tumors may cause Cushing disease, acromegaly, or prolactin excess.',
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
    let timeoutId

    // Simulate step 1: Image validation (quick)
    await new Promise((r) => setTimeout(r, 400))
    setLoadingStep(2)

    try {
      const formData = new FormData()
      formData.append('image', file)
      const controller = new AbortController()
      timeoutId = setTimeout(() => controller.abort(), 20000)

      const response = await fetch(
        `${API_BASE_URL}/api/v1/analyze`,
        {
          method: 'POST',
          body: formData,
          signal: controller.signal,
        }
      )

      const text = await response.text()
      setLoadingStep(3)

      let data
      try {
        data = text && text.trim() ? JSON.parse(text) : {}
      } catch {
        const hint = !text || !text.trim()
          ? 'Server returned empty response. Ensure the Flask backend is running on port 5001 and the model file exists.'
          : 'Server returned invalid response. Check that the backend is running and the model is loaded.'
        throw new Error(hint)
      }

      if (!response.ok) {
        const err = data?.error
        const msg =
          (typeof err === 'string' ? err : err?.message) ||
          data?.message ||
          `Request failed (${response.status})`
        throw new Error(msg)
      }

      setResult(data)
      await new Promise((r) => setTimeout(r, 400))
      setView('results')
    } catch (err) {
      if (err?.name === 'AbortError') {
        setError('Request timed out after 20 seconds. Please try again.')
        setView('upload')
        return
      }
      const msg = err.message || 'Analysis failed.'
      const isConnectionError = /failed to fetch|networkerror|ECONNREFUSED|connection refused/i.test(msg) ||
        (msg.includes('Request failed') && (msg.includes('500') || msg.includes('502') || msg.includes('503')))
      setError(
        isConnectionError
          ? 'Backend unavailable. Start the Flask server: run `python app.py` from the project root (port 5001).'
          : msg
      )
      setView('upload')
    } finally {
      clearTimeout(timeoutId)
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
    <div className={`app ${view === 'home' ? 'app-home' : ''} ${darkMode ? 'dark' : ''}`}>
      <div className={`sidebar-overlay ${sidebarOpen ? 'open' : ''}`} onClick={() => setSidebarOpen(false)} aria-hidden="true" />
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <button type="button" className="sidebar-logo" onClick={() => handleNavClick('home')}>
          <span className="logo-icon">🔬</span>
          <span>MRI Diagnosis AI</span>
        </button>
        <nav className="sidebar-nav">
          <button type="button" className={`sidebar-link ${view === 'home' ? 'active' : ''}`} onClick={() => handleNavClick('home')}>
            <span className="sidebar-link-icon">🏠</span>
            Home
          </button>
          <button type="button" className={`sidebar-link ${view === 'upload' || view === 'loading' || view === 'results' ? 'active' : ''}`} onClick={() => handleNavClick('upload')}>
            <span className="sidebar-link-icon">🔬</span>
            Diagnosis AI
          </button>
          <button type="button" className={`sidebar-link ${view === 'tumor-types' ? 'active' : ''}`} onClick={() => handleNavClick('tumor-types')}>
            <span className="sidebar-link-icon">📋</span>
            Brain Tumor Types
          </button>
          <button type="button" className={`sidebar-link ${view === 'future-work' ? 'active' : ''}`} onClick={() => handleNavClick('future-work')}>
            <span className="sidebar-link-icon">🚀</span>
            Future Work
          </button>
        </nav>
        <div className="sidebar-actions">
          <button
            type="button"
            className="btn-theme-toggle"
            onClick={() => setDarkMode((d) => !d)}
            title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
          <button type="button" className="btn-login" onClick={() => { handleNavClick('login'); setAuthMessage(null); }}>
            Login
          </button>
          <button type="button" className="btn-signup" onClick={() => { handleNavClick('signup'); setAuthMessage(null); }}>
            Sign Up
          </button>
        </div>
      </aside>

      <div className="app-content">
        <button
          type="button"
          className={`btn-hamburger ${sidebarOpen ? 'open' : ''}`}
          onClick={() => setSidebarOpen((o) => !o)}
          aria-label={sidebarOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={sidebarOpen}
        >
          <span className="hamburger-line" />
          <span className="hamburger-line" />
          <span className="hamburger-line" />
        </button>
      <main className={`main ${view === 'home' ? 'main-home' : ''}`}>
        {view === 'home' && (
          <section className="home-section">
            <div className="home-hero">
              <span className="home-badge">AI-Powered MRI Classification</span>
              <h1 className="home-title">
                <span className="home-title-gradient">Brain Tumor</span>
                <br />Detection AI
              </h1>
              <div className="home-subtitle-block">
                <p className="home-subtitle">
                  Upload an MRI scan and get an AI-based tumor classification with confidence scores and structured insights.
                </p>
                <p className="hero-disclaimer">
                  This is an educational AI demo and not a medical diagnosis tool.
                </p>
              </div>
              <button type="button" className="btn-cta" onClick={() => setView('upload')}>
                Upload MRI Image →
              </button>
            </div>

            <div className="home-stats">
              <div className="home-stat">
                <span className="home-stat-value">4</span>
                <span className="home-stat-label">Tumor Types</span>
              </div>
              <div className="home-stat">
                <span className="home-stat-value">{'<'}30s</span>
                <span className="home-stat-label">Analysis Time</span>
              </div>
            </div>

            <div className="home-cards">
              <div className="home-card">
                <h3>How It Works</h3>
                <ol>
                  <li>Upload your MRI scan (PNG/JPG)</li>
                  <li>AI validates quality and analyzes your scan</li>
                  <li>Get findings, impression & next steps</li>
                </ol>
              </div>
              <div className="home-card">
                <h3>What We Detect</h3>
                <ul>
                  <li><strong>Glioma</strong> — glial cell tumors</li>
                  <li><strong>Meningioma</strong> — meninges tumors</li>
                  <li><strong>Pituitary</strong> — pituitary adenomas</li>
                  <li><strong>No Tumor</strong> — within normal limits</li>
                </ul>
              </div>
            </div>

            <div className="home-features">
              <div className="home-feature">
                <span className="home-feature-icon">🛡️</span>
                <span>Privacy First</span>
              </div>
              <div className="home-feature">
                <span className="home-feature-icon">⏱</span>
                <span>{'<'} 30s Analysis</span>
              </div>
            </div>
          </section>
        )}

        {view === 'upload' && (
          <section className="upload-section">
            <h1>Brain Tumor Detection AI</h1>
            <p className="subtitle">
              Upload an MRI image to run AI-based tumor classification and receive a confidence-driven result.
            </p>
            <p className="upload-disclaimer">
              This is an educational AI demo and not a medical diagnosis tool.
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

            {previewUrl && (
              <div className="upload-preview-card">
                <h3>Uploaded MRI Preview</h3>
                <img src={previewUrl} alt="Uploaded MRI preview" className="upload-preview-img" />
              </div>
            )}

            <div className="feature-cards">
              <div className="feature-card">
                <span className="feature-icon">🛡️</span>
                <span>Privacy First</span>
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
            <p className="loading-subtitle">Processing your scan for anomalies.</p>

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
                <span>AI analysis{loadingStep === 2 && '...'}</span>
                {loadingStep >= 3 && <span className="step-status">SUCCESS</span>}
              </div>
              <div className={`progress-step ${loadingStep >= 3 ? 'done' : ''}`}>
                <span className="step-icon">{loadingStep >= 3 ? '✓' : '○'}</span>
                <span>Generating diagnostic report</span>
                {loadingStep >= 3 && <span className="step-status">SUCCESS</span>}
              </div>
            </div>

            <div className="loading-footer">
              <span>🛡️ Privacy-First Processing</span>
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
              <button
                type="button"
                className="btn-download-pdf"
                onClick={() => exportReportToPdf(result, previewUrl)}
              >
                Download PDF
              </button>
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
            <div className={`card card-prediction conf-${result.vision ? getConfidenceBand(result.vision.confidence || 0) : 'low'}`}>
              <h3>Primary Detection</h3>
              {result.vision ? (
                <>
                  <p className="prediction-label">{formatLabel(result.vision.label)}</p>
                  <p className="prediction-confidence">
                    Confidence: <span className={`conf-badge conf-${getConfidenceBand(result.vision.confidence || 0)}`}>{Math.round((result.vision.confidence || 0) * 100)}%</span>
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
                      const band = getConfidenceBand(prob)
                      return (
                        <div key={label} className={`prob-item ${isHighest ? 'prob-item-highlight' : ''}`}>
                          <div className="prob-header">
                            <span>{formatLabel(label)}</span>
                            <span className={`conf-badge conf-${band}`}>{pct}%</span>
                          </div>
                          <div className="prob-bar">
                            <div className={`prob-fill conf-${band}`} style={{ width: `${pct}%` }} />
                          </div>
                        </div>
                      )
                    })}
                </div>
              </div>
            )}

            <div className="card card-heatmap-placeholder">
              <h3>🧠 Tumor Attention Heatmap</h3>
              <p className="heatmap-placeholder-text">
                Explainability visualization coming soon.
              </p>
            </div>

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
            <button type="button" className="btn-back" onClick={() => setView('home')}>
              ← Back
            </button>
            <h1>Types of Brain Tumors</h1>
            <p className="tumor-types-intro">
              Our AI classifies MRI scans into the following categories. Understanding these types helps interpret analysis results.
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

        {view === 'future-work' && (
          <section className="future-work-page">
            <button type="button" className="btn-back" onClick={() => setView('home')}>
              ← Back
            </button>
            <h1>Future Work & Roadmap</h1>
            <p className="future-work-intro">
              We are expanding our AI diagnostic capabilities to support more imaging modalities and clinical use cases. Here is what we plan to bring next.
            </p>

            <div className="future-work-grid">
              <article className="future-work-card">
                <span className="future-work-icon">🫁</span>
                <h2>Lung Disease Detection</h2>
                <p className="future-work-desc">
                  AI-powered analysis of chest X-rays and CT scans for pulmonary conditions including pneumonia, lung nodules, tuberculosis, and other respiratory abnormalities.
                </p>
                <ul className="future-work-details">
                  <li>Chest X-ray screening for pneumonia and COVID-19 related findings</li>
                  <li>CT lung nodule detection and size estimation</li>
                  <li>Support for tuberculosis screening in high burden regions</li>
                  <li>Integration with existing radiology workflows</li>
                </ul>
              </article>

              <article className="future-work-card">
                <span className="future-work-icon">❤️</span>
                <h2>Heart Disease Detection</h2>
                <p className="future-work-desc">
                  Cardiac imaging analysis for echocardiograms, chest X-rays, and cardiac MRI to support detection of heart failure, arrhythmias, and structural abnormalities.
                </p>
                <ul className="future-work-details">
                  <li>Echocardiogram analysis for ejection fraction and wall motion</li>
                  <li>ECG interpretation for arrhythmia screening</li>
                  <li>Cardiac MRI for structural and functional assessment</li>
                  <li>Cardiomegaly detection from chest X-rays</li>
                </ul>
              </article>

              <article className="future-work-card">
                <span className="future-work-icon">📋</span>
                <h2>Additional Features</h2>
                <p className="future-work-desc">
                  Platform improvements and new capabilities to enhance usability, accuracy, and integration for healthcare providers.
                </p>
                <ul className="future-work-details">
                  <li><strong>Batch processing</strong> — Analyze multiple scans in one session</li>
                  <li><strong>DICOM support</strong> — Native support for standard medical imaging format</li>
                  <li><strong>API access</strong> — REST API for third-party EHR and PACS integration</li>
                  <li><strong>Mobile app</strong> — iOS and Android apps for on the go review</li>
                  <li><strong>Multilanguage reports</strong> — Localized findings and impressions</li>
                  <li><strong>Comparison tracking</strong> — Compare scans over time for follow up</li>
                </ul>
              </article>
            </div>

            <div className="future-work-cta">
              <p>Have feedback or feature requests? Reach out to help shape our roadmap.</p>
            </div>
          </section>
        )}

        {view === 'login' && (
          <section className="auth-page">
            <div className="auth-card">
              <button type="button" className="btn-back" onClick={() => setView('home')}>
                ← Back
              </button>
              <h1>Login</h1>
              <p className="auth-subtitle">Sign in to access the Physician Portal</p>
              <form
                className="auth-form"
                onSubmit={(e) => {
                  e.preventDefault()
                  setAuthMessage('Login is not yet connected to a backend. This is a placeholder.')
                }}
              >
                <label>
                  <span>Email</span>
                  <input
                    type="email"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    placeholder="you@example.com"
                    required
                  />
                </label>
                <label>
                  <span>Password</span>
                  <div className="password-input-wrap">
                    <input
                      type={showLoginPassword ? 'text' : 'password'}
                      value={loginPassword}
                      onChange={(e) => setLoginPassword(e.target.value)}
                      placeholder="••••••••"
                      required
                    />
                    <button
                      type="button"
                      className="btn-toggle-password"
                      onClick={() => setShowLoginPassword((s) => !s)}
                      title={showLoginPassword ? 'Hide password' : 'Show password'}
                      aria-label={showLoginPassword ? 'Hide password' : 'Show password'}
                    >
                      {showLoginPassword ? '🙈' : '👁️'}
                    </button>
                  </div>
                </label>
                <button type="button" className="auth-forgot">Forgot password?</button>
                {authMessage && <p className="auth-message">{authMessage}</p>}
                <button type="submit" className="btn-submit">Sign In</button>
              </form>
              <p className="auth-switch">
                Don&apos;t have an account?{' '}
                <button type="button" className="auth-link" onClick={() => { setView('signup'); setAuthMessage(null); }}>
                  Sign Up
                </button>
              </p>
            </div>
          </section>
        )}

        {view === 'signup' && (
          <section className="auth-page">
            <div className="auth-card">
              <button type="button" className="btn-back" onClick={() => setView('home')}>
                ← Back
              </button>
              <h1>Sign Up</h1>
              <p className="auth-subtitle">Create an account for the Physician Portal</p>
              <form
                className="auth-form"
                onSubmit={(e) => {
                  e.preventDefault()
                  if (signupPassword !== signupConfirm) {
                    setAuthMessage('Passwords do not match.')
                    return
                  }
                  setAuthMessage('Sign up is not yet connected to a backend. This is a placeholder.')
                }}
              >
                <label>
                  <span>Full Name</span>
                  <input
                    type="text"
                    value={signupName}
                    onChange={(e) => setSignupName(e.target.value)}
                    placeholder="Dr. Jane Smith"
                    required
                  />
                </label>
                <label>
                  <span>Email</span>
                  <input
                    type="email"
                    value={signupEmail}
                    onChange={(e) => setSignupEmail(e.target.value)}
                    placeholder="you@example.com"
                    required
                  />
                </label>
                <label>
                  <span>Password</span>
                  <div className="password-input-wrap">
                    <input
                      type={showSignupPassword ? 'text' : 'password'}
                      value={signupPassword}
                      onChange={(e) => setSignupPassword(e.target.value)}
                      placeholder="••••••••"
                      required
                      minLength={8}
                    />
                    <button
                      type="button"
                      className="btn-toggle-password"
                      onClick={() => setShowSignupPassword((s) => !s)}
                      title={showSignupPassword ? 'Hide password' : 'Show password'}
                      aria-label={showSignupPassword ? 'Hide password' : 'Show password'}
                    >
                      {showSignupPassword ? '🙈' : '👁️'}
                    </button>
                  </div>
                </label>
                <label>
                  <span>Confirm Password</span>
                  <div className="password-input-wrap">
                    <input
                      type={showSignupConfirm ? 'text' : 'password'}
                      value={signupConfirm}
                      onChange={(e) => setSignupConfirm(e.target.value)}
                      placeholder="••••••••"
                      required
                    />
                    <button
                      type="button"
                      className="btn-toggle-password"
                      onClick={() => setShowSignupConfirm((s) => !s)}
                      title={showSignupConfirm ? 'Hide password' : 'Show password'}
                      aria-label={showSignupConfirm ? 'Hide password' : 'Show password'}
                    >
                      {showSignupConfirm ? '🙈' : '👁️'}
                    </button>
                  </div>
                </label>
                {authMessage && <p className="auth-message">{authMessage}</p>}
                <button type="submit" className="btn-submit">Create Account</button>
              </form>
              <p className="auth-switch">
                Already have an account?{' '}
                <button type="button" className="auth-link" onClick={() => { setView('login'); setAuthMessage(null); }}>
                  Login
                </button>
              </p>
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <div className="footer-nav">
          <button type="button" className={`nav-item ${view === 'home' ? 'active' : ''}`} onClick={() => setView('home')}>
            Home
          </button>
          <button type="button" className={`nav-item ${view === 'upload' || view === 'loading' || view === 'results' ? 'active' : ''}`} onClick={() => setView('upload')}>
            Diagnosis AI
          </button>
          <button type="button" className={`nav-item ${view === 'tumor-types' ? 'active' : ''}`} onClick={() => setView('tumor-types')}>
            Tumor Types
          </button>
          <button type="button" className={`nav-item ${view === 'future-work' ? 'active' : ''}`} onClick={() => setView('future-work')}>
            Future Work
          </button>
          <button type="button" className={`nav-item ${view === 'login' ? 'active' : ''}`} onClick={() => setView('login')}>
            Login
          </button>
        </div>
        <p className="disclaimer">
          ⚠️ For educational purposes only. Not a substitute for professional medical advice.
        </p>
      </footer>
      </div>
    </div>
  )
}

export default App
