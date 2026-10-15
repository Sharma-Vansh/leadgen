# Archetype B: Universal ATS Adapters (150+ Companies)

Rather than building 150+ custom website scrapers, Archetype B leverages the public REST API endpoints of the 4 dominant Applicant Tracking Systems (ATS) used by top tech companies and unicorns.

## Covered ATS Platforms
1. **Greenhouse**: `boards-api.greenhouse.io/v1/boards/{company}/jobs` (Swiggy, Razorpay, Zomato, Datadog, Figma)
2. **Lever**: `api.lever.co/v0/postings/{company}` (Postman, Netflix, Spotify, Canva)
3. **Ashby**: `jobs.ashbyhq.com/api/non-api/job-board/{company}` (OpenAI, Linear, Vercel, Ramp, Retool)
4. **Workday**: `{company}.wd3.myworkdayjobs.com/wday/cxs/...` (Adobe, Walmart, Salesforce)

## Company Mapping
Company to ATS mappings are defined in `registry.json`. To add a new company, simply append its slug to the appropriate ATS array in `registry.json`.
