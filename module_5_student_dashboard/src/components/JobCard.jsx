import React from 'react';
import { 
  Building2, 
  MapPin, 
  Sparkles, 
  Plus, 
  Check, 
  ExternalLink, 
  ChevronRight,
  TrendingUp,
  Clock
} from 'lucide-react';

export default function JobCard({ 
  job, 
  onViewDetails, 
  onTailorResume, 
  onAddToTracker, 
  isInTracker 
}) {
  const getBadgeClass = (archetype) => {
    switch (archetype) {
      case 'tier1': return 'badge-tier1';
      case 'startup': return 'badge-startup';
      case 'remote': return 'badge-remote';
      case 'govt': return 'badge-govt';
      default: return 'badge-tech';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'score-high';
    if (score >= 80) return 'score-medium';
    return 'score-low';
  };

  return (
    <div className="job-card glass-panel-elevated">
      {/* Top Header: Company Info & Match Meter */}
      <div className="job-card-header">
        <div className="company-branding">
          <div 
            className="company-avatar" 
            style={{ background: job.companyGradient || 'linear-gradient(135deg, #38bdf8 0%, #6366f1 100%)' }}
          >
            {job.companyInitial || job.company?.charAt(0) || 'C'}
          </div>
          <div className="company-meta">
            <h4 className="company-name">{job.company}</h4>
            <div className="job-location">
              <MapPin size={13} />
              <span>{job.location}</span>
            </div>
          </div>
        </div>

        {/* Semantic Match Score Gauge */}
        <div className={`match-score-badge ${getScoreColor(job.matchScore)}`}>
          <div className="match-score-inner">
            <span className="score-num">{job.matchScore}%</span>
            <span className="score-label">MATCH</span>
          </div>
        </div>
      </div>

      {/* Role Title & Archetype Tag */}
      <div className="job-title-row">
        <h3 className="job-title" onClick={() => onViewDetails(job)}>
          {job.title}
        </h3>
        <div className="job-tags-row">
          <span className={`badge ${getBadgeClass(job.archetype)}`}>
            {job.archetypeLabel || job.archetype}
          </span>
          <span className="salary-tag">
            {job.salary}
          </span>
        </div>
      </div>

      {/* Experience & Posting Age */}
      <div className="job-secondary-meta">
        <span className="meta-item">
          <TrendingUp size={12} />
          {job.experienceLevel}
        </span>
        <span className="meta-item">
          <Clock size={12} />
          {job.postedDate}
        </span>
      </div>

      {/* Matched vs Skill Gaps Preview */}
      <div className="skills-preview-section">
        <div className="skill-pills-wrap">
          {job.matchedSkills?.slice(0, 3).map((skill, idx) => (
            <span key={idx} className="skill-pill skill-matched" title="Verified Skill">
              ✓ {skill}
            </span>
          ))}
          {job.skillGaps?.slice(0, 2).map((gap, idx) => (
            <span key={idx} className="skill-pill skill-gap" title="Recommended to Learn">
              + {gap}
            </span>
          ))}
        </div>
      </div>

      {/* Card Action Controls */}
      <div className="job-card-actions">
        <button 
          className="btn-tailor-quick" 
          onClick={() => onTailorResume(job)}
          title="Tailor resume specifically for this job description"
        >
          <Sparkles size={14} />
          <span>Tailor Resume</span>
        </button>

        <button 
          className={`btn-tracker-toggle ${isInTracker ? 'tracked' : ''}`}
          onClick={() => onAddToTracker(job)}
          title={isInTracker ? "Already added to your Pipeline" : "Add to Kanban Application Pipeline"}
        >
          {isInTracker ? (
            <>
              <Check size={14} />
              <span>Tracked</span>
            </>
          ) : (
            <>
              <Plus size={14} />
              <span>Track</span>
            </>
          )}
        </button>

        <button 
          className="btn-view-details" 
          onClick={() => onViewDetails(job)}
          title="View full job requirements & eligibility"
        >
          <span>Details</span>
          <ChevronRight size={14} />
        </button>
      </div>
    </div>
  );
}
