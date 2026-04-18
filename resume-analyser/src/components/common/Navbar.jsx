import { Link, useLocation } from 'react-router-dom';
import { FileText, History, ExternalLink } from 'lucide-react';
import './Navbar.css';

export default function Navbar() {
  const { pathname } = useLocation();

  return (
    <header className="navbar">
      <div className="container navbar-inner">
        <Link to="/" className="navbar-brand">
          <span className="navbar-logo-icon">
            <FileText size={20} />
          </span>
          <span className="navbar-logo-text">
            Resume<span className="navbar-logo-accent">AI</span>
          </span>
        </Link>

        <nav className="navbar-nav">
          <Link
            to="/"
            className={`navbar-link ${pathname === '/' ? 'active' : ''}`}
          >
            Analyse
          </Link>
          <Link
            to="/history"
            className={`navbar-link ${pathname === '/history' ? 'active' : ''}`}
          >
            <History size={15} />
            History
          </Link>
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="navbar-link"
          >
            <ExternalLink size={15} />
            GitHub
          </a>
        </nav>
      </div>
    </header>
  );
}
