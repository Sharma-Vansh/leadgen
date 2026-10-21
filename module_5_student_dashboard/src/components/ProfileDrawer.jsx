import React, { useState } from 'react';
import { 
  X, 
  User, 
  GraduationCap, 
  Award, 
  Code2, 
  Plus, 
  Trash2, 
  Save, 
  CheckCircle2, 
  Briefcase,
  MapPin,
  IndianRupee
} from 'lucide-react';

export default function ProfileDrawer({ 
  isOpen, 
  onClose, 
  profile, 
  onSaveProfile,
  onNotify 
}) {
  if (!isOpen) return null;

  const [formData, setFormData] = useState({ ...profile });
  const [newSkill, setNewSkill] = useState('');

  const handleAddSkill = (e) => {
    e?.preventDefault();
    if (newSkill.trim() && !formData.skills?.includes(newSkill.trim())) {
      setFormData({
        ...formData,
        skills: [...(formData.skills || []), newSkill.trim()]
      });
      setNewSkill('');
    }
  };

  const handleRemoveSkill = (skillToRemove) => {
    setFormData({
      ...formData,
      skills: formData.skills.filter(s => s !== skillToRemove)
    });
  };

  const handleSave = (e) => {
    e?.preventDefault();
    onSaveProfile(formData);
    onNotify?.("Candidate profile & preferences saved successfully!", "success");
    onClose();
  };

  return (
    <div className="drawer-overlay" onClick={onClose}>
      <div className="drawer-container glass-panel-elevated" onClick={e => e.stopPropagation()}>
        {/* Drawer Header */}
        <div className="drawer-header">
          <div className="drawer-title-row">
            <User size={20} className="text-cyan" />
            <h3>Candidate Profile & Preferences</h3>
          </div>
          <button className="btn-close-drawer" onClick={onClose} aria-label="Close profile drawer">
            <X size={20} />
          </button>
        </div>

        {/* Drawer Content */}
        <form className="drawer-body" onSubmit={handleSave}>
          {/* Personal Information */}
          <div className="drawer-section">
            <h4 className="drawer-section-title">Personal & Contact</h4>
            <div className="drawer-field">
              <label>Full Name</label>
              <input 
                type="text" 
                value={formData.name || ''} 
                onChange={e => setFormData({ ...formData, name: e.target.value })}
                required 
              />
            </div>
            <div className="drawer-field">
              <label>Email Address</label>
              <input 
                type="email" 
                value={formData.email || ''} 
                onChange={e => setFormData({ ...formData, email: e.target.value })}
                required 
              />
            </div>
          </div>

          {/* Academic Background */}
          <div className="drawer-section">
            <h4 className="drawer-section-title">Academic Background</h4>
            <div className="drawer-field">
              <label>Degree & Major</label>
              <input 
                type="text" 
                value={formData.degree || ''} 
                onChange={e => setFormData({ ...formData, degree: e.target.value })}
              />
            </div>
            <div className="drawer-field">
              <label>Institution / University</label>
              <input 
                type="text" 
                value={formData.institution || ''} 
                onChange={e => setFormData({ ...formData, institution: e.target.value })}
              />
            </div>
            <div className="drawer-row-2">
              <div className="drawer-field">
                <label>Batch Year</label>
                <input 
                  type="number" 
                  value={formData.batchYear || 2026} 
                  onChange={e => setFormData({ ...formData, batchYear: Number(e.target.value) })}
                />
              </div>
              <div className="drawer-field">
                <label>CGPA / Percentage</label>
                <input 
                  type="text" 
                  value={formData.cgpa || ''} 
                  onChange={e => setFormData({ ...formData, cgpa: e.target.value })}
                />
              </div>
            </div>
          </div>

          {/* Target Role & Preferences */}
          <div className="drawer-section">
            <h4 className="drawer-section-title">Career Preferences</h4>
            <div className="drawer-field">
              <label>Target Role Title</label>
              <input 
                type="text" 
                value={formData.targetRole || ''} 
                onChange={e => setFormData({ ...formData, targetRole: e.target.value })}
              />
            </div>

            <div className="drawer-field">
              <label>Minimum Expected Salary (LPA)</label>
              <input 
                type="number" 
                value={formData.preferences?.minSalaryLPA || 12} 
                onChange={e => setFormData({ 
                  ...formData, 
                  preferences: { 
                    ...formData.preferences, 
                    minSalaryLPA: Number(e.target.value) 
                  } 
                })}
              />
            </div>
          </div>

          {/* Verified Technical Skills */}
          <div className="drawer-section">
            <h4 className="drawer-section-title">Verified Technical Skills ({formData.skills?.length || 0})</h4>
            <div className="add-skill-row">
              <input 
                type="text" 
                placeholder="Add skill (e.g. Redis, Go, Kubernetes)..."
                value={newSkill}
                onChange={e => setNewSkill(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddSkill();
                  }
                }}
              />
              <button type="button" className="btn-secondary" onClick={handleAddSkill}>
                <Plus size={14} />
                <span>Add</span>
              </button>
            </div>

            <div className="profile-skills-chips">
              {formData.skills?.map((skill, idx) => (
                <span key={idx} className="profile-skill-chip">
                  <span>{skill}</span>
                  <button type="button" onClick={() => handleRemoveSkill(skill)}>×</button>
                </span>
              ))}
            </div>
          </div>

          {/* Drawer Actions */}
          <div className="drawer-footer">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              <Save size={16} />
              <span>Save & Re-Index Matches</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
