/**
 * LeadGen Autonomous Autofill — Default Candidate Profile
 * Synchronized with Module 5 Student Dashboard & Module 3 Backend
 */

const DEFAULT_LEADGEN_PROFILE = {
  // Personal & Contact
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

  // Location / Address
  address: "Flat 402, Green Glen Layout, Bellandur",
  city: "Bengaluru",
  state: "Karnataka",
  postalCode: "560103",
  country: "India",

  // Online Handles & Profiles
  linkedin: "https://linkedin.com/in/arjun-sharma-dev",
  github: "https://github.com/Sharma-Vansh",
  portfolio: "https://arjunsharma.dev",

  // Academic Credentials
  institution: "National Institute of Technology",
  university: "National Institute of Technology",
  degree: "Bachelor of Technology",
  fieldOfStudy: "Computer Science and Engineering",
  major: "Computer Science",
  cgpa: "8.75",
  cgpaMax: "10.0",
  percentage: "87.5",
  startYear: "2022",
  graduationYear: "2026",
  batchYear: "2026",

  // Professional Summary & Experience
  headline: "Software Engineer | Python, FastAPI, React & Distributed Ingestion Architectures",
  summary: "Proactive Software Engineer specializing in Python, FastAPI, React, and scalable backend database architectures. Experienced in building high-throughput APIs, containerized microservices, and reliable cloud deployments.",
  coverLetter: "Dear Hiring Team,\n\nI am writing to express my strong enthusiasm for this engineering opportunity. With a rigorous background in Computer Science and hands-on experience designing high-concurrency ingestion pipelines, relational databases (PostgreSQL), and modular full-stack interfaces, I am eager to contribute immediately to your engineering organization.\n\nThank you for your consideration.\n\nSincerely,\nArjun Sharma",

  // Top Verified Skills
  skills: [
    "Python",
    "FastAPI",
    "React",
    "JavaScript",
    "PostgreSQL",
    "SQLAlchemy",
    "Docker",
    "Git",
    "RESTful APIs",
    "Data Structures & Algorithms",
    "HTML5/CSS3",
    "Linux"
  ],

  // Govt Exam Ready Indicators
  govtDocuments: {
    photoReady: true,
    photoGuideline: "3.5x4.5cm, 20-50 KB",
    signatureReady: true,
    signatureGuideline: "140x60px, 10-20 KB, Pure White Background"
  }
};

// Export for ES modules and standard browser script scopes
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { DEFAULT_LEADGEN_PROFILE };
}
