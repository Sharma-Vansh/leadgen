import React from 'react';
import { 
  Layers, 
  ArrowRight, 
  ArrowLeft, 
  Trash2, 
  Sparkles, 
  CheckCircle, 
  Clock, 
  FileCheck,
  ChevronRight
} from 'lucide-react';

const STAGES = [
  { id: 'discovered', label: 'Discovered', desc: 'AI Matched Ingestion', color: '#38bdf8' },
  { id: 'preparing', label: 'Preparing', desc: 'ATS Tailoring in Progress', color: '#a855f7' },
  { id: 'ready', label: 'Ready to Apply', desc: 'Verified & Formatted', color: '#10b981' },
  { id: 'applied', label: 'Submitted', desc: 'Applied & Tracking', color: '#f59e0b' },
];

export default function KanbanTracker({ 
  items, 
  onMoveStage, 
  onDeleteItem, 
  onTailorResume,
  allJobs 
}) {
  const getStageItems = (stageId) => items.filter(it => it.stage === stageId);

  return (
    <div className="kanban-tracker-view animate-fade-in">
      <div className="kanban-header">
        <div>
          <h2 className="kanban-title">Application Pipeline</h2>
          <p className="kanban-subtitle">
            Track your tailored applications from discovery to final submission across all archetypes.
          </p>
        </div>
        <div className="kanban-total-badge">
          <span>{items.length} Active Applications</span>
        </div>
      </div>

      <div className="kanban-board-grid">
        {STAGES.map((stage, colIdx) => {
          const colItems = getStageItems(stage.id);

          return (
            <div key={stage.id} className="kanban-column glass-panel">
              {/* Column Header */}
              <div className="kanban-col-header" style={{ borderTop: `3px solid ${stage.color}` }}>
                <div>
                  <h4 className="col-title">{stage.label}</h4>
                  <span className="col-desc">{stage.desc}</span>
                </div>
                <span className="col-count-pill" style={{ background: `${stage.color}20`, color: stage.color }}>
                  {colItems.length}
                </span>
              </div>

              {/* Items List */}
              <div className="kanban-col-items">
                {colItems.length > 0 ? (
                  colItems.map(item => {
                    const matchedJob = allJobs.find(j => j.id === item.jobId);

                    return (
                      <div key={item.id} className="kanban-card glass-panel-elevated">
                        <div className="card-top-row">
                          <span className="card-company">{item.company}</span>
                          <span className="card-score-badge">{item.matchScore}%</span>
                        </div>

                        <h5 className="card-job-title">{item.title}</h5>

                        {item.notes && (
                          <p className="card-notes-text">{item.notes}</p>
                        )}

                        <div className="card-timestamp">
                          <Clock size={11} />
                          <span>{item.updatedAt}</span>
                        </div>

                        {/* Card Action Bar */}
                        <div className="card-actions-row">
                          {colIdx > 0 && (
                            <button 
                              className="btn-card-nav"
                              onClick={() => onMoveStage(item.id, STAGES[colIdx - 1].id)}
                              title={`Move back to ${STAGES[colIdx - 1].label}`}
                            >
                              <ArrowLeft size={13} />
                            </button>
                          )}

                          {matchedJob && (
                            <button 
                              className="btn-card-tailor"
                              onClick={() => onTailorResume(matchedJob)}
                              title="Tailor Resume in Studio"
                            >
                              <Sparkles size={12} />
                              <span>Resume</span>
                            </button>
                          )}

                          <button 
                            className="btn-card-delete"
                            onClick={() => onDeleteItem(item.id)}
                            title="Remove from pipeline"
                          >
                            <Trash2 size={13} />
                          </button>

                          {colIdx < STAGES.length - 1 && (
                            <button 
                              className="btn-card-nav next"
                              onClick={() => onMoveStage(item.id, STAGES[colIdx + 1].id)}
                              title={`Move to ${STAGES[colIdx + 1].label}`}
                            >
                              <ArrowRight size={13} />
                            </button>
                          )}
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="kanban-empty-col">
                    <p>No applications in {stage.label.toLowerCase()}</p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
