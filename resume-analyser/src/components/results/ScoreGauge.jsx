import { useEffect, useRef } from 'react';
import './ScoreGauge.css';

const COLOR_MAP = {
  excellent: '#22d3a9',
  good:      '#38bdf8',
  moderate:  '#fbbf24',
  weak:      '#fb923c',
  poor:      '#f87171',
};

export default function ScoreGauge({ score, label, color }) {
  const circleRef = useRef(null);

  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const strokeColor = COLOR_MAP[color] || '#38bdf8';

  useEffect(() => {
    if (!circleRef.current) return;
    const offset = circumference - (score / 100) * circumference;
    circleRef.current.style.setProperty('--dash-offset', offset);
  }, [score, circumference]);

  return (
    <div className="gauge-wrapper">
      <div className="gauge-svg-wrap">
        <svg
          className="gauge-svg"
          viewBox="0 0 200 200"
          aria-label={`Match score: ${score}%`}
          role="img"
        >
          {/* Track */}
          <circle
            cx="100" cy="100" r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.06)"
            strokeWidth="14"
          />
          {/* Progress arc */}
          <circle
            ref={circleRef}
            cx="100" cy="100" r={radius}
            fill="none"
            stroke={strokeColor}
            strokeWidth="14"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={circumference} // start at 0, animate via CSS
            transform="rotate(-90 100 100)"
            className="gauge-arc"
            style={{
              '--dash-offset': circumference - (score / 100) * circumference,
              filter: `drop-shadow(0 0 8px ${strokeColor}80)`,
            }}
          />
        </svg>

        {/* Score text overlay */}
        <div className="gauge-center">
          <span className="gauge-score" style={{ color: strokeColor }}>
            {score}
          </span>
          <span className="gauge-pct">%</span>
          <span className="gauge-sub">Match</span>
        </div>
      </div>

      {/* Label badge */}
      <div className="gauge-label" style={{ color: strokeColor, borderColor: `${strokeColor}30`, background: `${strokeColor}12` }}>
        {label}
      </div>

      {/* Score breakdown hint */}
      <p className="gauge-hint">
        Semantic similarity + keyword coverage
      </p>
    </div>
  );
}
