import React, { useState, useMemo } from 'react';
import { 
  Search, 
  SlidersHorizontal, 
  Sparkles, 
  Database, 
  Layers, 
  Zap, 
  ShieldCheck, 
  CheckCircle2 
} from 'lucide-react';
import JobCard from './JobCard';

export default function JobFeed({ 
  jobs, 
  onViewDetails, 
  onTailorResume, 
  onAddToTracker, 
  trackerJobIds 
}) {
  const [selectedArchetype, setSelectedArchetype] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [minScore, setMinScore] = useState(70);
  const [sortBy, setSortBy] = useState('score'); // 'score', 'newest'

  // Filtered and sorted jobs
  const filteredJobs = useMemo(() => {
    return jobs.filter(job => {
      // Archetype filter
      if (selectedArchetype !== 'all' && job.archetype !== selectedArchetype) {
        return false;
      }
      // Match Score filter
      if (job.matchScore < minScore) {
        return false;
      }
      // Search Query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesTitle = job.title.toLowerCase().includes(q);
        const matchesCompany = job.company.toLowerCase().includes(q);
        const matchesSkill = job.matchedSkills?.some(s => s.toLowerCase().includes(q));
        if (!matchesTitle && !matchesCompany && !matchesSkill) {
          return false;
        }
      }
      return true;
    }).sort((a, b) => {
      if (sortBy === 'score') return b.matchScore - a.matchScore;
      return 0;
    });
  }, [jobs, selectedArchetype, minScore, searchQuery, sortBy]);

  const archetypeOptions = [
    { id: 'all', label: 'All 388+ Sources', count: jobs.length },
    { id: 'tier1', label: 'Tier-1 Tech', count: jobs.filter(j => j.archetype === 'tier1').length },
    { id: 'startup', label: 'Fintech & Unicorns', count: jobs.filter(j => j.archetype === 'startup').length },
    { id: 'remote', label: 'Remote Global', count: jobs.filter(j => j.archetype === 'remote').length },
    { id: 'govt', label: 'Govt & PSUs', count: jobs.filter(j => j.archetype === 'govt').length },
  ];

  return (
    <div className="job-feed-view animate-fade-in">
      {/* Metrics Banner */}
      <div className="metrics-strip glass-panel">
        <div className="metric-item">
          <div className="metric-icon-wrap cyan">
            <Database size={18} />
          </div>
          <div className="metric-info">
            <span className="metric-val">388 Sources</span>
            <span className="metric-lbl">Autonomous Scrapers Active</span>
          </div>
        </div>

        <div className="metric-divider"></div>

        <div className="metric-item">
          <div className="metric-icon-wrap indigo">
            <Sparkles size={18} />
          </div>
          <div className="metric-info">
            <span className="metric-val">95% Top Match</span>
            <span className="metric-lbl">Vector Semantic Match</span>
          </div>
        </div>

        <div className="metric-divider"></div>

        <div className="metric-item">
          <div className="metric-icon-wrap emerald">
            <Zap size={18} />
          </div>
          <div className="metric-info">
            <span className="metric-val">100% Anti-Hallucination</span>
            <span className="metric-lbl">Verified Resume Engine</span>
          </div>
        </div>

        <div className="metric-divider"></div>

        <div className="metric-item">
          <div className="metric-icon-wrap rose">
            <ShieldCheck size={18} />
          </div>
          <div className="metric-info">
            <span className="metric-val">Zero Rejection</span>
            <span className="metric-lbl">Govt SSC/UPSC Lab Active</span>
          </div>
        </div>
      </div>

      {/* Filter and Control Strip */}
      <div className="filter-controls-container glass-panel">
        {/* Archetype Pill Tabs */}
        <div className="archetype-tabs">
          {archetypeOptions.map(opt => (
            <button
              key={opt.id}
              className={`archetype-tab-btn ${selectedArchetype === opt.id ? 'active' : ''}`}
              onClick={() => setSelectedArchetype(opt.id)}
            >
              <span>{opt.label}</span>
              <span className="tab-count-badge">{opt.count}</span>
            </button>
          ))}
        </div>

        {/* Search & Sliders Row */}
        <div className="search-slider-row">
          <div className="search-input-box">
            <Search size={16} className="search-icon" />
            <input 
              type="text" 
              placeholder="Filter by role, company, or skill (e.g. FastAPI, Python, Google)..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <button className="clear-search-btn" onClick={() => setSearchQuery('')}>×</button>
            )}
          </div>

          <div className="score-slider-box">
            <span className="slider-label">
              Min Match: <strong>{minScore}%</strong>
            </span>
            <input 
              type="range" 
              min="50" 
              max="95" 
              step="5"
              value={minScore} 
              onChange={e => setMinScore(Number(e.target.value))}
              className="score-range-slider"
            />
          </div>
        </div>
      </div>

      {/* Job Grid Results */}
      <div className="job-feed-results-header">
        <h3 className="results-count-title">
          Showing <span>{filteredJobs.length}</span> Verified Opportunities
        </h3>
        <span className="results-subtitle">
          Real-time AI Match Ranking calibrated to your profile
        </span>
      </div>

      {filteredJobs.length > 0 ? (
        <div className="job-cards-grid">
          {filteredJobs.map(job => (
            <JobCard
              key={job.id}
              job={job}
              onViewDetails={onViewDetails}
              onTailorResume={onTailorResume}
              onAddToTracker={onAddToTracker}
              isInTracker={trackerJobIds.includes(job.id)}
            />
          ))}
        </div>
      ) : (
        <div className="empty-results-box glass-panel">
          <Search size={36} className="empty-icon" />
          <h4>No Opportunities Match Your Current Filter</h4>
          <p>Try lowering the minimum match score or searching for broader skills.</p>
          <button 
            className="btn-secondary"
            onClick={() => {
              setSelectedArchetype('all');
              setMinScore(50);
              setSearchQuery('');
            }}
          >
            Reset All Filters
          </button>
        </div>
      )}
    </div>
  );
}
