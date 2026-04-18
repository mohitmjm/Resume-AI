import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, FileText, X, Sparkles, Zap, Shield, Brain } from 'lucide-react';
import './HomePage.css';

const FEATURES = [
  { icon: <Brain size={22} />, title: 'ATS Score', desc: 'Get your resume\'s ATS compatibility score across 8 key factors.' },
  { icon: <Zap size={22} />, title: 'Job Role Prediction', desc: 'ML model trained on 2400+ Kaggle resumes predicts your best-fit roles.' },
  { icon: <Sparkles size={22} />, title: 'Skill Analysis', desc: 'Visual breakdown of your skills across 9 technology categories.' },
  { icon: <Shield size={22} />, title: 'AI Summary', desc: 'Auto-generated professional summary based on your resume content.' },
];

export default function HomePage() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const onDrop = useCallback((accepted, rejected) => {
    setError('');
    if (rejected.length > 0) {
      const code = rejected[0].errors[0]?.code;
      if (code === 'file-too-large') setError('File too large — max 10 MB.');
      else setError('Invalid file type. Upload PDF or DOCX only.');
      return;
    }
    if (accepted.length > 0) setFile(accepted[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 10 * 1024 * 1024,
    multiple: false,
  });

  const handleAnalyse = async () => {
    if (!file) { setError('Please upload your resume first.'); return; }
    setError('');
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const API_URL = import.meta.env.VITE_API_URL || '';
      const res = await fetch(`${API_URL}/api/analyse`, {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) { setError(data.error || 'Analysis failed.'); return; }

      navigate('/results', { state: { result: data, fileName: file.name } });
    } catch (err) {
      setError('Cannot reach backend server. Make sure the Python backend is running (python app.py in resume-analyser-backend).');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="home-page">
      {/* Hero */}
      <section className="hero section">
        <div className="container">
          <div className="hero-content animate-fade-up">
            <div className="badge badge-primary hero-badge">
              <Sparkles size={13} />
              NLP-Powered · Kaggle Dataset · ATS Optimiser
            </div>
            <h1 className="hero-title">
              Know exactly how your<br />
              <span className="gradient-text">resume performs</span>
            </h1>
            <p className="hero-sub">
              Upload your resume and get your ATS score, skill breakdown,
              job role predictions, and an AI-generated summary — instantly.
            </p>
          </div>

          {/* Upload card */}
          <div className="upload-card glass-card animate-fade-up">
            {!file ? (
              <div
                {...getRootProps()}
                className={`dropzone ${isDragActive ? 'drag-active' : ''}`}
              >
                <input {...getInputProps()} />
                <div className="dz-icon-wrap">
                  <UploadCloud size={44} strokeWidth={1.5} />
                </div>
                <p className="dz-main">{isDragActive ? 'Drop it here!' : 'Drag & drop your resume'}</p>
                <p className="dz-sub">PDF or DOCX · up to 10 MB</p>
                <span className="btn btn-ghost" style={{ pointerEvents: 'none' }}>Browse Files</span>
              </div>
            ) : (
              <div className="file-preview">
                <div className="file-icon"><FileText size={30} /></div>
                <div className="file-info">
                  <p className="file-name">{file.name}</p>
                  <p className="file-meta">{(file.size / 1024).toFixed(0)} KB · Ready to analyse</p>
                </div>
                <button className="remove-btn" onClick={() => setFile(null)} title="Remove">
                  <X size={16} />
                </button>
              </div>
            )}

            {error && <div className="upload-error" role="alert">⚠️ {error}</div>}

            <button
              className="btn btn-primary btn-lg analyse-btn"
              onClick={handleAnalyse}
              disabled={loading || !file}
              id="analyse-btn"
            >
              {loading ? (
                <><span className="spinner" /> Analysing...</>
              ) : (
                <><Brain size={18} /> Analyse Resume</>
              )}
            </button>
          </div>

          {/* Feature grid */}
          <div className="features-grid">
            {FEATURES.map((f, i) => (
              <div key={i} className="feature-card glass-card animate-fade-up">
                <div className="feature-icon">{f.icon}</div>
                <h3 className="feature-title">{f.title}</h3>
                <p className="feature-desc">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
