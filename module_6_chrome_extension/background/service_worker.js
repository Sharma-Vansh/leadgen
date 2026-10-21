/**
 * LeadGen Chrome Extension — Manifest V3 Background Service Worker
 * Handles lifecycle, storage synchronization, and tab communication
 */

const DEFAULT_PROFILE = {
  fullName: "Arjun Sharma",
  firstName: "Arjun",
  lastName: "Sharma",
  email: "arjun.sharma@example.com",
  phone: "+91 98765 43210",
  rawPhone: "9876543210",
  gender: "Male",
  dob: "2004-05-14",
  nationality: "Indian",
  category: "General",
  address: "Flat 402, Green Glen Layout, Bellandur",
  city: "Bengaluru",
  state: "Karnataka",
  postalCode: "560103",
  country: "India",
  linkedin: "https://linkedin.com/in/arjun-sharma-dev",
  github: "https://github.com/Sharma-Vansh",
  portfolio: "https://arjunsharma.dev",
  institution: "National Institute of Technology",
  university: "National Institute of Technology",
  degree: "Bachelor of Technology",
  fieldOfStudy: "Computer Science and Engineering",
  major: "Computer Science",
  cgpa: "8.75",
  graduationYear: "2026",
  batchYear: "2026",
  headline: "Software Engineer | Python, FastAPI, React & Distributed Ingestion",
  summary: "Proactive Software Engineer specializing in Python, FastAPI, React, and scalable backend database architectures.",
  coverLetter: "Dear Hiring Team,\n\nI am writing to express my strong enthusiasm for this engineering opportunity. With a rigorous background in Computer Science and hands-on experience designing high-concurrency ingestion pipelines, relational databases (PostgreSQL), and modular full-stack interfaces, I am eager to contribute immediately to your engineering organization.\n\nThank you for your consideration.\n\nSincerely,\nArjun Sharma"
};

// Extension installation initialization
chrome.runtime.onInstalled.addListener(() => {
  console.log('[LeadGen AI] Extension installed successfully.');
  chrome.storage.local.get(['leadgen_student_profile'], (result) => {
    if (!result.leadgen_student_profile) {
      chrome.storage.local.set({ leadgen_student_profile: DEFAULT_PROFILE }, () => {
        console.log('[LeadGen AI] Default student profile initialized in storage.');
      });
    }
  });
});

// Periodic backend sync attempt
async function trySyncBackendProfile() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);
    const res = await fetch('http://localhost:8000/api/profile/me', {
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    if (res.ok) {
      const data = await res.json();
      if (data) {
        chrome.storage.local.set({ leadgen_student_profile: data });
        console.log('[LeadGen AI] Synced latest candidate profile from FastAPI backend.');
      }
    }
  } catch {
    // Offline mode: keep local storage
  }
}

chrome.runtime.onStartup.addListener(() => {
  trySyncBackendProfile();
});
