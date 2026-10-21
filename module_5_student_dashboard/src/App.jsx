import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import JobFeed from './components/JobFeed';
import JobDetailModal from './components/JobDetailModal';
import KanbanTracker from './components/KanbanTracker';
import ResumeStudioView from './components/ResumeStudioView';
import GovtDocumentLabView from './components/GovtDocumentLabView';
import ProfileDrawer from './components/ProfileDrawer';
import { api } from './services/api';
import { MOCK_JOBS, INITIAL_STUDENT_PROFILE, INITIAL_KANBAN_ITEMS } from './data/mockJobs';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';
import './App.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('feed'); // 'feed' | 'kanban' | 'resume' | 'govt'
  const [backendOnline, setBackendOnline] = useState(false);
  const [jobs, setJobs] = useState(MOCK_JOBS);
  const [profile, setProfile] = useState(INITIAL_STUDENT_PROFILE);
  const [kanbanItems, setKanbanItems] = useState(() => {
    const saved = localStorage.getItem('leadgen_kanban_items');
    return saved ? JSON.parse(saved) : INITIAL_KANBAN_ITEMS;
  });

  const [selectedJobForResume, setSelectedJobForResume] = useState(MOCK_JOBS[0]);
  const [modalJob, setModalJob] = useState(null);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [toasts, setToasts] = useState([]);

  // Check backend health & load initial data
  useEffect(() => {
    checkHealth();
    loadProfile();
  }, []);

  // Sync Kanban items to localStorage
  useEffect(() => {
    localStorage.setItem('leadgen_kanban_items', JSON.stringify(kanbanItems));
  }, [kanbanItems]);

  const checkHealth = async () => {
    const online = await api.checkStatus();
    setBackendOnline(online);
    if (online) {
      addToast("Connected to LeadGen FastAPI Backend (Port 8000)", "success");
      const feed = await api.getMatchedFeed();
      if (feed && feed.length > 0) setJobs(feed);
    } else {
      addToast("Demo Mode Active: Pre-loaded with 388 verified autonomous scraper jobs", "info");
    }
  };

  const loadProfile = async () => {
    const p = await api.getStudentProfile();
    if (p) setProfile(p);
  };

  const addToast = (message, type = 'info') => {
    const id = Date.now() + Math.random();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4000);
  };

  const handleTailorResume = (job) => {
    setSelectedJobForResume(job);
    setActiveTab('resume');
    addToast(`Loaded ${job.company} — ${job.title} into AI Resume Studio`, 'info');
  };

  const handleAddToTracker = (job) => {
    const exists = kanbanItems.find(it => it.jobId === job.id);
    if (exists) {
      addToast(`${job.company} is already in your application pipeline!`, 'info');
      setActiveTab('kanban');
      return;
    }

    const newItem = {
      id: `kanban-${Date.now()}`,
      jobId: job.id,
      company: job.company,
      title: job.title,
      stage: 'discovered',
      matchScore: job.matchScore,
      notes: `Added from Autonomous Job Feed (${job.archetypeLabel}). Target compensation: ${job.salary}.`,
      updatedAt: 'Just now'
    };

    setKanbanItems(prev => [newItem, ...prev]);
    addToast(`Added ${job.company} to your Application Pipeline!`, 'success');
  };

  const handleMoveKanbanStage = (itemId, newStage) => {
    setKanbanItems(prev => prev.map(item => {
      if (item.id === itemId) {
        return { ...item, stage: newStage, updatedAt: 'Just now' };
      }
      return item;
    }));
  };

  const handleDeleteKanbanItem = (itemId) => {
    setKanbanItems(prev => prev.filter(it => it.id !== itemId));
    addToast("Removed application from pipeline", "info");
  };

  const handleSaveProfile = async (updated) => {
    setProfile(updated);
    await api.saveStudentProfile(updated);
    addToast("Profile saved & AI semantic match engine re-indexed!", "success");
  };

  return (
    <div className="app-container">
      {/* Top Universal Navigation Bar */}
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab}
        backendOnline={backendOnline}
        onRefreshBackend={checkHealth}
        onOpenProfile={() => setIsProfileOpen(true)}
        profile={profile}
        kanbanCount={kanbanItems.length}
      />

      {/* Main View Area */}
      <main className="main-content">
        {activeTab === 'feed' && (
          <JobFeed 
            jobs={jobs}
            onViewDetails={(job) => setModalJob(job)}
            onTailorResume={handleTailorResume}
            onAddToTracker={handleAddToTracker}
            trackerJobIds={kanbanItems.map(it => it.jobId)}
          />
        )}

        {activeTab === 'kanban' && (
          <KanbanTracker 
            items={kanbanItems}
            onMoveStage={handleMoveKanbanStage}
            onDeleteItem={handleDeleteKanbanItem}
            onTailorResume={handleTailorResume}
            allJobs={jobs}
          />
        )}

        {activeTab === 'resume' && (
          <ResumeStudioView 
            jobs={jobs}
            selectedJob={selectedJobForResume}
            onSelectJob={(j) => setSelectedJobForResume(j)}
            profile={profile}
            onNotify={addToast}
          />
        )}

        {activeTab === 'govt' && (
          <GovtDocumentLabView 
            onNotify={addToast}
          />
        )}
      </main>

      {/* Job Detail Modal */}
      {modalJob && (
        <JobDetailModal 
          job={modalJob}
          onClose={() => setModalJob(null)}
          onTailorResume={handleTailorResume}
          onAddToTracker={handleAddToTracker}
          isInTracker={kanbanItems.some(it => it.jobId === modalJob.id)}
        />
      )}

      {/* Candidate Profile Drawer */}
      <ProfileDrawer 
        isOpen={isProfileOpen}
        onClose={() => setIsProfileOpen(false)}
        profile={profile}
        onSaveProfile={handleSaveProfile}
        onNotify={addToast}
      />

      {/* Toast Notification Container */}
      <div className="toast-container">
        {toasts.map(toast => (
          <div key={toast.id} className={`toast toast-${toast.type}`}>
            {toast.type === 'success' && <CheckCircle2 size={16} className="text-emerald" />}
            {toast.type === 'info' && <Info size={16} className="text-cyan" />}
            {toast.type === 'warn' && <AlertCircle size={16} className="text-amber" />}
            <span>{toast.message}</span>
            <button 
              className="toast-close-btn"
              onClick={() => setToasts(prev => prev.filter(t => t.id !== toast.id))}
            >
              <X size={12} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
