import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Trash2, Clock } from 'lucide-react';
import './HistoryPage.css';

const SCORE_COLOR = (score) => {
  if (score >= 85) return '#22d3a9';
  if (score >= 70) return '#38bdf8';
  if (score >= 55) return '#fbbf24';
  if (score >= 40) return '#fb923c';
  return '#f87171';
};

export default function HistoryPage() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    try {
      const stored = JSON.parse(localStorage.getItem('ra_history') || '[]');
      setHistory(stored);
    } catch { setHistory([]); }
  }, []);

  const clearAll = () => { localStorage.removeItem('ra_history'); setHistory([]); };
  const remove = (id) => {
    const updated = history.filter((h) => h.id !== id);
    localStorage.setItem('ra_history', JSON.stringify(updated));
    setHistory(updated);
  };

  return (
    <main className="history-page section">
      <div className="container">
        <div className="history-header animate-fade-up">
          <div>
            <h1 className="history-title">Analysis History</h1>
            <p className="history-sub">Stored locally in your browser — up to 20 analyses.</p>
          </div>
          {history.length > 0 && (
            <button className="btn btn-ghost" onClick={clearAll}>
              <Trash2 size={14} /> Clear All
            </button>
          )}
        </div>

        {history.length === 0 ? (
          <div className="history-empty glass-card animate-fade-up">
            <p style={{ fontSize: '3.5rem' }}>📭</p>
            <h3>No analyses yet</h3>
            <p>Upload a resume on the home page to get started.</p>
            <Link to="/" className="btn btn-primary" style={{ marginTop: '1.5rem' }}>
              Start Analysing
            </Link>
          </div>
        ) : (
          <div className="history-list">
            {history.map((item) => {
              const color = SCORE_COLOR(item.ats_total || 0);
              return (
                <div key={item.id} className="history-card glass-card animate-fade-up">
                  <div className="h-score-circle" style={{ color, borderColor: `${color}40`, background: `${color}10` }}>
                    <span className="h-score-num">{item.ats_total || '–'}</span>
                    {item.ats_total && <span className="h-score-pct">%</span>}
                  </div>
                  <div className="h-info">
                    <p className="h-filename">📄 {item.fileName}</p>
                    {item.top_role && <p className="h-role" style={{ color }}>{item.top_role}</p>}
                    <div className="h-date">
                      <Clock size={12} /> {new Date(item.timestamp).toLocaleString()}
                    </div>
                  </div>
                  <div className="h-actions">
                    <Link
                      to="/results"
                      state={{ result: item.result, fileName: item.fileName }}
                      className="btn btn-ghost"
                    >
                      View →
                    </Link>
                    <button className="h-delete-btn" onClick={() => remove(item.id)}>
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </main>
  );
}
