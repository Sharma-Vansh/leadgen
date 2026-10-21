/**
 * LeadGen Chrome Extension — Popup Controller
 */

document.addEventListener('DOMContentLoaded', async () => {
  const statusDot = document.getElementById('status-dot');
  const statusHeadline = document.getElementById('status-headline');
  const platformName = document.getElementById('platform-name');
  const jobTitleText = document.getElementById('job-title-text');
  const btnAutofill = document.getElementById('btn-autofill');
  const autofillResult = document.getElementById('autofill-result');
  const candidateName = document.getElementById('candidate-name');

  // Load candidate profile from storage or default
  let profile = typeof DEFAULT_LEADGEN_PROFILE !== 'undefined' ? DEFAULT_LEADGEN_PROFILE : null;
  if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
    chrome.storage.local.get(['leadgen_student_profile'], (res) => {
      if (res && res.leadgen_student_profile) {
        profile = { ...profile, ...res.leadgen_student_profile };
      }
      if (candidateName && profile?.firstName) {
        candidateName.textContent = `${profile.firstName} ${profile.lastName ? profile.lastName.charAt(0) + '.' : ''}`;
      }
    });
  }

  // Get active tab and query status
  if (typeof chrome !== 'undefined' && chrome.tabs && chrome.tabs.query) {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const activeTab = tabs[0];
      if (!activeTab || !activeTab.id) {
        setIdleStatus();
        return;
      }

      chrome.tabs.sendMessage(activeTab.id, { action: 'GET_PAGE_STATUS' }, (res) => {
        if (chrome.runtime.lastError || !res || !res.data) {
          setIdleStatus();
          return;
        }

        const data = res.data;
        if (data.isApplicationPage) {
          statusDot.className = 'status-indicator-dot active';
          statusHeadline.textContent = 'Application Form Detected';
          platformName.textContent = data.platform;
          jobTitleText.textContent = data.company ? `${data.company} — ${data.jobTitle || 'Role'}` : (data.jobTitle || 'Job Form');
          btnAutofill.disabled = false;
        } else {
          setIdleStatus();
        }
      });
    });
  } else {
    setIdleStatus();
  }

  function setIdleStatus() {
    statusDot.className = 'status-indicator-dot idle';
    statusHeadline.textContent = 'Ready on Standby';
    platformName.textContent = 'Browse Job / Exam Form';
    jobTitleText.textContent = 'Navigate to Workday, Greenhouse, or SSC';
  }

  // Autofill button click
  btnAutofill.addEventListener('click', () => {
    btnAutofill.disabled = true;
    btnAutofill.textContent = 'Filling Application...';

    if (typeof chrome !== 'undefined' && chrome.tabs && chrome.tabs.query) {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const activeTab = tabs[0];
        if (!activeTab || !activeTab.id) return;

        chrome.tabs.sendMessage(activeTab.id, { action: 'PERFORM_AUTOFILL' }, (response) => {
          btnAutofill.disabled = false;
          btnAutofill.innerHTML = '<span>⚡ Autofill Application (1-Click)</span>';

          if (response && response.result) {
            autofillResult.style.display = 'block';
            autofillResult.textContent = `✓ Successfully filled ${response.result.filledCount} fields!`;
          } else {
            autofillResult.style.display = 'block';
            autofillResult.textContent = 'Autofill initiated on active page!';
          }

          setTimeout(() => {
            autofillResult.style.display = 'none';
          }, 4000);
        });
      });
    }
  });

  // Copy Cover Letter
  document.getElementById('btn-copy-cover-letter')?.addEventListener('click', () => {
    const text = profile?.coverLetter || "Dear Hiring Team,\n\nI am eager to apply for this engineering role.\n\nSincerely,\nArjun Sharma";
    navigator.clipboard.writeText(text).then(() => {
      const el = document.getElementById('btn-copy-cover-letter');
      const original = el.innerHTML;
      el.innerHTML = '<span class="tool-icon">✓</span><span class="tool-name">Copied!</span>';
      setTimeout(() => { el.innerHTML = original; }, 2000);
    });
  });

  // Open Web Dashboard
  document.getElementById('btn-open-dashboard')?.addEventListener('click', () => {
    if (typeof chrome !== 'undefined' && chrome.tabs && chrome.tabs.create) {
      chrome.tabs.create({ url: 'http://localhost:5173' });
    } else {
      window.open('http://localhost:5173', '_blank');
    }
  });
});
