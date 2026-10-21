/**
 * LeadGen Autonomous Job Form & ATS Detector
 * Detects Workday, Greenhouse, Lever, Ashby, SmartRecruiters, SSC, UPSC, and Generic application forms
 */

const FormDetector = {
  detectPlatform() {
    const url = window.location.href.toLowerCase();
    const html = document.body ? document.body.innerHTML.toLowerCase() : '';

    if (url.includes('myworkdayjobs.com') || document.querySelector('[data-automation-id]')) {
      return { platform: 'Workday', type: 'ats' };
    }
    if (url.includes('greenhouse.io') || document.querySelector('#job_application, form[action*="greenhouse"]')) {
      return { platform: 'Greenhouse', type: 'ats' };
    }
    if (url.includes('jobs.lever.co') || document.querySelector('.application-form, form[action*="lever"]')) {
      return { platform: 'Lever', type: 'ats' };
    }
    if (url.includes('ashbyhq.com') || document.querySelector('[class*="ashby"]')) {
      return { platform: 'Ashby', type: 'ats' };
    }
    if (url.includes('smartrecruiters.com') || document.querySelector('form[action*="smartrecruiters"]')) {
      return { platform: 'SmartRecruiters', type: 'ats' };
    }
    if (url.includes('ssc.gov.in') || url.includes('ssc.nic.in') || html.includes('staff selection commission')) {
      return { platform: 'SSC Govt Portal', type: 'govt' };
    }
    if (url.includes('upsc.gov.in') || url.includes('upsconline') || html.includes('union public service commission')) {
      return { platform: 'UPSC Govt Portal', type: 'govt' };
    }

    // Generic form detection based on key input keywords
    const inputElements = document.querySelectorAll('input:not([type="hidden"]), select, textarea');
    let jobSignals = 0;
    inputElements.forEach(el => {
      const name = (el.name || el.id || el.placeholder || '').toLowerCase();
      if (name.includes('resume') || name.includes('cv') || name.includes('education') || 
          name.includes('experience') || name.includes('linkedin') || name.includes('phone')) {
        jobSignals++;
      }
    });

    if (jobSignals >= 2) {
      return { platform: 'Generic Job Application', type: 'generic' };
    }

    return { platform: 'Unknown', type: 'none' };
  },

  extractJobContext() {
    let jobTitle = '';
    let company = '';

    // Common Heading Selectors
    const titleCandidates = [
      'h1.app-title', '.job-title', 'h1[data-automation-id="jobPostingHeader"]', 
      '.posting-headline h2', 'h1', '.header-title'
    ];
    for (const sel of titleCandidates) {
      const el = document.querySelector(sel);
      if (el && el.innerText.trim().length > 3) {
        jobTitle = el.innerText.trim().split('\n')[0];
        break;
      }
    }

    // Company Candidates
    const compCandidates = [
      '.company-name', '[data-automation-id="companyName"]', 
      'meta[property="og:site_name"]', '.org-name'
    ];
    for (const sel of compCandidates) {
      const el = document.querySelector(sel);
      if (el) {
        company = (el.content || el.innerText || '').trim();
        if (company) break;
      }
    }

    if (!company) {
      const hostname = window.location.hostname.replace('www.', '').split('.')[0];
      company = hostname.charAt(0).toUpperCase() + hostname.slice(1);
    }

    return { jobTitle: jobTitle || document.title, company };
  },

  scanPage() {
    const { platform, type } = this.detectPlatform();
    const context = this.extractJobContext();

    const inputs = document.querySelectorAll('input:not([type="hidden"]), select, textarea');
    let hasResumeUpload = false;
    let hasPhotoUpload = false;
    let hasSignatureUpload = false;

    inputs.forEach(el => {
      const idStr = ((el.id || '') + ' ' + (el.name || '') + ' ' + (el.getAttribute('aria-label') || '')).toLowerCase();
      if (el.type === 'file') {
        if (idStr.includes('resume') || idStr.includes('cv')) hasResumeUpload = true;
        if (idStr.includes('photo') || idStr.includes('pic') || idStr.includes('image')) hasPhotoUpload = true;
        if (idStr.includes('sign') || idStr.includes('signature')) hasSignatureUpload = true;
      }
    });

    return {
      isApplicationPage: type !== 'none',
      platform,
      type,
      jobTitle: context.jobTitle,
      company: context.company,
      url: window.location.href,
      inputCount: inputs.length,
      hasResumeUpload,
      hasPhotoUpload,
      hasSignatureUpload
    };
  }
};

// Export for environments
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { FormDetector };
}
