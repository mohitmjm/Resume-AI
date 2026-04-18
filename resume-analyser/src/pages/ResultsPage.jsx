import { useLocation, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Download } from 'lucide-react';
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts';
import ScoreGauge from '../components/results/ScoreGauge';
import './ResultsPage.css';

const SCORE_COLOR = (score) => {
  if (score >= 85) return '#22d3a9';
  if (score >= 70) return '#38bdf8';
  if (score >= 55) return '#fbbf24';
  if (score >= 40) return '#fb923c';
  return '#f87171';
};

const SCORE_COLOR_MAP = {
  excellent: '#22d3a9', good: '#38bdf8',
  moderate: '#fbbf24', weak: '#fb923c', poor: '#f87171',
};

const getScoreColor = (score) => {
  if (score >= 85) return 'excellent';
  if (score >= 70) return 'good';
  if (score >= 55) return 'moderate';
  if (score >= 40) return 'weak';
  return 'poor';
};

const getScoreLabel = (score) => {
  if (score >= 85) return 'Excellent';
  if (score >= 70) return 'Good';
  if (score >= 55) return 'Average';
  if (score >= 40) return 'Below Average';
  return 'Poor';
};

/* ── Custom tooltip ── */
const FactorTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="custom-tooltip">
      <p className="tt-title">{d.name}</p>
      <p className="tt-score">{d.score} / {d.max} pts</p>
      <p className="tt-note">{d.note}</p>
    </div>
  );
};

export default function ResultsPage() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const result = state?.result;
  const fileName = state?.fileName || 'resume';

  if (!result) {
    return (
      <div className="results-empty section container">
        <div className="glass-card" style={{ padding: '3rem', textAlign: 'center' }}>
          <p style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</p>
          <h2>No Results Found</h2>
          <p style={{ margin: '1rem 0 2rem' }}>Go back and upload your resume to get an analysis.</p>
          <Link to="/" className="btn btn-primary">← Back to Home</Link>
        </div>
      </div>
    );
  }

  const { ats, skills, job_roles, summary, name, contact, years_experience, education } = result;
  const colorKey = getScoreColor(ats.total);
  const scoreLabel = getScoreLabel(ats.total);
  const scoreHex = SCORE_COLOR_MAP[colorKey];

  /* ATS breakdown → bar chart data */
  const atsChartData = Object.entries(ats.breakdown).map(([key, val]) => ({
    name: key,
    score: val.score,
    max: val.max,
    note: val.note,
    fill: val.score >= val.max * 0.75 ? '#22d3a9' : val.score >= val.max * 0.4 ? '#fbbf24' : '#f87171',
  }));

  /* Skills by category → radar data */
  const radarData = Object.entries(skills.by_category || {}).map(([cat, arr]) => ({
    subject: cat.replace(' & ', ' &\n'),
    count: arr.length,
  }));

  /* Export JSON */
  const handleExport = () => {
    const blob = new Blob([JSON.stringify({ fileName, ...result }, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `resume-analysis-${Date.now()}.json`; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <main className="results-page section">
      <div className="container">
        {/* Header */}
        <div className="results-header animate-fade-up">
          <button className="btn btn-ghost" onClick={() => navigate('/')}>
            <ArrowLeft size={15} /> New Analysis
          </button>
          <div className="results-meta">
            <p className="results-filename">📄 {fileName}</p>
            {name && <p className="results-name">{name}</p>}
          </div>
          <button className="btn btn-ghost" onClick={handleExport}>
            <Download size={15} /> Export
          </button>
        </div>

        {/* ── Row 1: ATS Score + Summary ── */}
        <div className="row-two animate-fade-up">
          {/* ATS Gauge */}
          <div className="glass-card card-pad gauge-card">
            <h2 className="section-label">ATS Score</h2>
            <ScoreGauge score={ats.total} label={scoreLabel} color={colorKey} />
            <div className="ats-meta">
              <div className="meta-item">
                <span className="meta-k">Grade</span>
                <span className="meta-v" style={{ color: scoreHex }}>{ats.grade}</span>
              </div>
              {years_experience && years_experience !== 'N/A' && (
                <div className="meta-item">
                  <span className="meta-k">Experience</span>
                  <span className="meta-v">{years_experience}</span>
                </div>
              )}
              {contact?.email && (
                <div className="meta-item">
                  <span className="meta-k">Email</span>
                  <span className="meta-v ellipsis">{contact.email}</span>
                </div>
              )}
            </div>
          </div>

          {/* Summary */}
          <div className="glass-card card-pad summary-card">
            <h2 className="section-label">AI Summary</h2>
            <p className="summary-text">{summary}</p>

            {education?.length > 0 && (
              <div className="edu-block">
                <p className="edu-label">🎓 Education</p>
                {education.slice(0, 2).map((e, i) => (
                  <p key={i} className="edu-item">{e}</p>
                ))}
              </div>
            )}

            {contact && (
              <div className="contact-pills">
                {contact.email && <span className="cpill">✉ {contact.email}</span>}
                {contact.phone && <span className="cpill">📞 {contact.phone}</span>}
                {contact.linkedin && <span className="cpill">🔗 LinkedIn</span>}
                {contact.github && <span className="cpill">⌥ GitHub</span>}
              </div>
            )}
          </div>
        </div>

        {/* ── ATS Breakdown Bar Chart ── */}
        <div className="glass-card card-pad animate-fade-up">
          <h2 className="section-label">ATS Score Breakdown</h2>
          <p className="section-sub">How your resume performs across 8 ATS factors</p>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={atsChartData} margin={{ top: 10, right: 20, left: 0, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis
                dataKey="name"
                tick={{ fill: '#64748b', fontSize: 12 }}
                angle={-25}
                textAnchor="end"
                interval={0}
              />
              <YAxis tick={{ fill: '#64748b', fontSize: 12 }} />
              <Tooltip content={<FactorTooltip />} />
              <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                {atsChartData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>

          {/* Factor breakdown table */}
          <div className="factor-list">
            {atsChartData.map((f) => (
              <div key={f.name} className="factor-row">
                <span className="factor-name">{f.name}</span>
                <div className="factor-bar-wrap">
                  <div
                    className="factor-bar-fill"
                    style={{ width: `${(f.score / f.max) * 100}%`, background: f.fill }}
                  />
                </div>
                <span className="factor-score" style={{ color: f.fill }}>{f.score}/{f.max}</span>
                <span className="factor-note">{f.note}</span>
              </div>
            ))}
          </div>
        </div>

        {/* ── Row 3: Job Roles + Skills Radar ── */}
        <div className="row-two animate-fade-up">
          {/* Job role predictions */}
          <div className="glass-card card-pad">
            <h2 className="section-label">Suitable Job Roles</h2>
            <p className="section-sub">
              {job_roles?.[0]?.source === 'ml'
                ? 'Predicted by ML model (Kaggle dataset)'
                : 'Based on keyword analysis'}
            </p>
            <div className="job-role-list">
              {(job_roles || []).map((role, i) => {
                const conf = role.confidence;
                const color = conf >= 70 ? '#22d3a9' : conf >= 45 ? '#38bdf8' : '#fbbf24';
                return (
                  <div key={i} className="job-role-card">
                    <div className="job-role-top">
                      <span className="job-rank">#{i + 1}</span>
                      <span className="job-title">{role.role}</span>
                      <span className="job-conf" style={{ color }}>{conf.toFixed(0)}%</span>
                    </div>
                    <div className="job-bar-bg">
                      <div
                        className="job-bar-fill"
                        style={{ width: `${conf}%`, background: color }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Radar chart */}
          <div className="glass-card card-pad">
            <h2 className="section-label">Skills by Category</h2>
            <p className="section-sub">{skills.all?.length || 0} total skills detected</p>
            {radarData.length > 0 ? (
              <ResponsiveContainer width="100%" height={260}>
                <RadarChart data={radarData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
                  <PolarGrid stroke="rgba(255,255,255,0.08)" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 11 }} />
                  <Radar
                    name="Skills"
                    dataKey="count"
                    stroke="#3b82f6"
                    fill="#3b82f6"
                    fillOpacity={0.25}
                  />
                </RadarChart>
              </ResponsiveContainer>
            ) : (
              <p style={{ color: 'var(--clr-text-3)', textAlign: 'center', padding: '2rem' }}>
                No skills detected — try a more detailed resume.
              </p>
            )}
          </div>
        </div>

        {/* ── Skills by category (tags) ── */}
        {Object.keys(skills.by_category || {}).length > 0 && (
          <div className="glass-card card-pad animate-fade-up">
            <h2 className="section-label">Detected Skills</h2>
            <div className="skill-cat-grid">
              {Object.entries(skills.by_category).map(([cat, items]) => (
                <div key={cat} className="skill-cat-group">
                  <p className="skill-cat-name">{cat}</p>
                  <div className="skill-pill-row">
                    {items.map((s) => (
                      <span key={s} className="skill-pill">{s}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
