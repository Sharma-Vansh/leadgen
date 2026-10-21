import React from 'react';
import { 
  Briefcase, 
  Layers, 
  FileText, 
  ShieldCheck, 
  User, 
  Bell, 
  Wifi, 
  WifiOff, 
  RefreshCw 
} from 'lucide-react';

export default function Navbar({ 
  activeTab, 
  setActiveTab, 
  backendOnline, 
  onRefreshBackend, 
  onOpenProfile, 
  profile,
  kanbanCount
}) {
  const completeness = 88; // Profile readiness %

  return (
    <header className="navbar-wrapper">
      <div className="navbar-inner">
        {/* Brand Logo & Name */}
        <div className="navbar-brand">
          <div className="brand-logo-glow">
            <Briefcase size={22} className="brand-icon" />
          </div>
          <div className="brand-text">
            <div className="brand-title">
              LeadGen <span className="brand-badge-ai">AI OS</span>
            </div>
            <div className="brand-subtitle">Autonomous Career & Exam Intelligence</div>
          </div>
        </div>

        {/* Center Navigation Tabs */}
        <nav className="nav-tabs">
          <button 
            className={`nav-tab-btn ${activeTab === 'feed' ? 'active' : ''}`}
            onClick={() => setActiveTab('feed')}
          >
            <Briefcase size={16} />
            <span>Job Feed</span>
            <span className="nav-tab-counter">388+</span>
          </button>

          <button 
            className={`nav-tab-btn ${activeTab === 'kanban' ? 'active' : ''}`}
            onClick={() => setActiveTab('kanban')}
          >
            <Layers size={16} />
            <span>Pipeline</span>
            {kanbanCount > 0 && <span className="nav-tab-counter">{kanbanCount}</span>}
          </button>

          <button 
            className={`nav-tab-btn ${activeTab === 'resume' ? 'active' : ''}`}
            onClick={() => setActiveTab('resume')}
          >
            <FileText size={16} />
            <span>Resume Studio</span>
            <span className="nav-tab-pill">ATS 94%</span>
          </button>

          <button 
            className={`nav-tab-btn ${activeTab === 'govt' ? 'active' : ''}`}
            onClick={() => setActiveTab('govt')}
          >
            <ShieldCheck size={16} />
            <span>Govt Document Lab</span>
            <span className="nav-tab-pill pulse">SSC / UPSC</span>
          </button>
        </nav>

        {/* Right Section: Backend Status & Profile Pill */}
        <div className="navbar-actions">
          {/* Backend Health Badge */}
          <button 
            className={`backend-status-pill ${backendOnline ? 'online' : 'demo'}`}
            onClick={onRefreshBackend}
            title={backendOnline ? "Connected to FastAPI Backend (Port 8000)" : "Running in Resilient Demo Mode (Click to re-check backend)"}
          >
            {backendOnline ? (
              <>
                <span className="status-dot green"></span>
                <Wifi size={13} />
                <span>API Live</span>
              </>
            ) : (
              <>
                <span className="status-dot purple"></span>
                <WifiOff size={13} />
                <span>Demo Mode</span>
                <RefreshCw size={11} className="refresh-icon" />
              </>
            )}
          </button>

          {/* Profile Completeness Pill */}
          <button className="profile-pill-btn" onClick={onOpenProfile}>
            <div className="profile-avatar">
              <User size={15} />
            </div>
            <div className="profile-info-compact">
              <span className="profile-name">{profile?.name?.split(' ')[0] || 'Candidate'}</span>
              <div className="completeness-bar-container">
                <div className="completeness-bar" style={{ width: `${completeness}%` }}></div>
              </div>
            </div>
            <span className="completeness-text">{completeness}%</span>
          </button>
        </div>
      </div>
    </header>
  );
}
