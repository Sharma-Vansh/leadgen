import React from 'react';
import { 
  X, 
  Building2, 
  MapPin, 
  Calendar, 
  Users, 
  ExternalLink, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle, 
  Lightbulb, 
  Plus, 
  Check 
} from 'lucide-react';

export default function JobDetailModal({ 
  job, 
  onClose, 
  onTailorResume, 
  onAddToTracker, 
  isInTracker 
}) {
  if (!job) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-container glass-panel-elevated" onClick={e => e.stopPropagation()}>
        {/* Modal Top Bar */}
        <div className="modal-header">
          <div className="modal-company-info">
            <div 
              className="company-avatar-large"
              style={{ background: job.companyGradient || 'linear-gradient(135deg, #38bdf8 0%, #6366f1 100%)' }}
            >
              {job.companyInitial || job.company?.charAt(0)}
            </div>
            <div>
              <div className="modal-company-name-row">
                <span className="modal-company-name">{job.company}</span>
                <span className="badge badge-tech">{job.archetypeLabel || job.archetype}</span>
              </div>
              <h2 className="modal-job-title">{job.title}</h2>
              <div className="modal-quick-meta">
                <span><MapPin size={13} /> {job.location}</span>
                <span>•</span>
                <span><Calendar size={13} /> Deadline: {job.deadline}</span>
                <span>•</span>
                <span><Users size={13} /> {job.applicantCount || 45} Applicants</span>
              </div>
            </div>
          </div>

          <button className="btn-close-modal" onClick={onClose} aria-label="Close modal">
            <X size={20} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body">
          {/* Match Score & Compensation Banner */}
          <div className="modal-score-banner">
            <div className="modal-score-gauge">
              <span className="modal-score-val">{job.matchScore}%</span>
              <span className="modal-score-sub">Semantic Match</span>
            </div>
            <div className="modal-salary-info">
              <span className="modal-salary-label">Compensation Package</span>
              <span className="modal-salary-val">{job.salary}</span>
            </div>
          </div>

          {/* Eligibility Criteria */}
          {job.eligibility && (
            <div className="modal-section">
              <h4 className="modal-section-title">Eligibility & Academic Requirements</h4>
              <div className="modal-eligibility-box">
                <CheckCircle2 size={16} className="text-emerald" />
                <p>{job.eligibility}</p>
              </div>
            </div>
          )}

          {/* Job Overview / Description */}
          <div className="modal-section">
            <h4 className="modal-section-title">Role Overview</h4>
            <p className="modal-description-text">{job.description}</p>
          </div>

          {/* Skills Breakdown Grid */}
          <div className="modal-section">
            <h4 className="modal-section-title">AI Skill Alignment Matrix</h4>
            <div className="skills-matrix-grid">
              {/* Verified Matched Skills */}
              <div className="skills-matrix-column verified">
                <div className="matrix-col-header">
                  <CheckCircle2 size={16} />
                  <span>Verified Candidate Skills ({job.matchedSkills?.length || 0})</span>
                </div>
                <div className="skill-pills-wrap">
                  {job.matchedSkills?.map((skill, i) => (
                    <span key={i} className="skill-pill skill-matched">
                      ✓ {skill}
                    </span>
                  ))}
                </div>
              </div>

              {/* Recommended Skill Gaps */}
              <div className="skills-matrix-column gaps">
                <div className="matrix-col-header">
                  <AlertCircle size={16} />
                  <span>Targeted Skill Gaps ({job.skillGaps?.length || 0})</span>
                </div>
                <div className="skill-pills-wrap">
                  {job.skillGaps?.map((gap, i) => (
                    <span key={i} className="skill-pill skill-gap">
                      + {gap}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* AI Learning Recommendation Box */}
          {job.learningTip && (
            <div className="learning-recommendation-box">
              <Lightbulb size={20} className="lightbulb-icon" />
              <div>
                <span className="rec-title">AI Match Accelerator Tip</span>
                <p className="rec-text">{job.learningTip}</p>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer Actions */}
        <div className="modal-footer">
          <button 
            className="btn-secondary" 
            onClick={() => onAddToTracker(job)}
          >
            {isInTracker ? <Check size={16} /> : <Plus size={16} />}
            <span>{isInTracker ? 'In Your Pipeline' : 'Add to Pipeline'}</span>
          </button>

          <div className="modal-footer-right">
            {job.applyUrl && (
              <a 
                href={job.applyUrl} 
                target="_blank" 
                rel="noreferrer" 
                className="btn-secondary"
              >
                <span>Official Portal</span>
                <ExternalLink size={15} />
              </a>
            )}

            <button 
              className="btn-primary" 
              onClick={() => {
                onClose();
                onTailorResume(job);
              }}
            >
              <Sparkles size={16} />
              <span>Tailor ATS Resume</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
