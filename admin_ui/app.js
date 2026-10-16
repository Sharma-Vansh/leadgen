// LeadGen Admin UI Logic
let allCompanies = [];
let currentFilter = 'all';

// DOM Elements
const companiesTbody = document.getElementById('companiesTbody');
const searchInput = document.getElementById('searchInput');
const btnClearSearch = document.getElementById('btnClearSearch');
const filterPills = document.querySelectorAll('.pill');
const showingCount = document.getElementById('showingCount');
const btnRefresh = document.getElementById('btnRefresh');

// Modal Elements
const addModal = document.getElementById('addModal');
const btnOpenAddModal = document.getElementById('btnOpenAddModal');
const btnCloseAddModal = document.getElementById('btnCloseAddModal');
const btnCancelModal = document.getElementById('btnCancelModal');
const addCompanyForm = document.getElementById('addCompanyForm');

const inputUrl = document.getElementById('inputUrl');
const btnAutoDetect = document.getElementById('btnAutoDetect');
const inputName = document.getElementById('inputName');
const selectAts = document.getElementById('selectAts');
const inputSlug = document.getElementById('inputSlug');
const inputCountry = document.getElementById('inputCountry');
const workdayFields = document.getElementById('workdayFields');
const inputWdBoard = document.getElementById('inputWdBoard');
const inputWdInstance = document.getElementById('inputWdInstance');

const btnTestConnection = document.getElementById('btnTestConnection');
const testResultBox = document.getElementById('testResultBox');

// Runner Panel Elements
const btnRunScraper = document.getElementById('btnRunScraper');
const runnerSection = document.getElementById('runnerSection');
const btnCloseRunner = document.getElementById('btnCloseRunner');
const runnerLogs = document.getElementById('runnerLogs');

// Toast
const toast = document.getElementById('toast');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  loadData();
  setupEventListeners();
});

function setupEventListeners() {
  // Search
  searchInput.addEventListener('input', (e) => {
    btnClearSearch.style.display = e.target.value ? 'block' : 'none';
    renderTable();
  });

  btnClearSearch.addEventListener('click', () => {
    searchInput.value = '';
    btnClearSearch.style.display = 'none';
    renderTable();
  });

  // Filter Pills
  filterPills.forEach(pill => {
    pill.addEventListener('click', () => {
      filterPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      currentFilter = pill.getAttribute('data-filter');
      renderTable();
    });
  });

  // Refresh
  btnRefresh.addEventListener('click', loadData);

  // Modal Open / Close
  btnOpenAddModal.addEventListener('click', () => {
    resetModalForm();
    addModal.classList.remove('hidden');
  });

  btnCloseAddModal.addEventListener('click', () => addModal.classList.add('hidden'));
  btnCancelModal.addEventListener('click', () => addModal.classList.add('hidden'));

  // ATS Dropdown change -> toggle Workday fields
  selectAts.addEventListener('change', () => {
    if (selectAts.value === 'workday') {
      workdayFields.classList.remove('hidden');
    } else {
      workdayFields.classList.add('hidden');
    }
  });

  // Auto-Detect URL
  btnAutoDetect.addEventListener('click', handleAutoDetect);

  // Live Test Connection
  btnTestConnection.addEventListener('click', handleTestConnection);

  // Form Submit
  addCompanyForm.addEventListener('submit', handleAddCompanySubmit);

  // Runner Toggle
  btnRunScraper.addEventListener('click', handleRunScraper);
  btnCloseRunner.addEventListener('click', () => runnerSection.classList.add('hidden'));
}

async function loadData() {
  try {
    const res = await fetch('/api/companies');
    const data = await res.json();
    
    // Flatten grouped data into single array
    allCompanies = [];
    for (const [ats, list] of Object.entries(data)) {
      list.forEach(c => {
        allCompanies.push({
          ...c,
          ats: ats
        });
      });
    }

    updateStats(data);
    renderTable();
  } catch (err) {
    showToast('Failed to load companies data: ' + err.message, 'error');
  }
}

function updateStats(data) {
  const ghCount = (data.greenhouse || []).length;
  const ashCount = (data.ashby || []).length;
  const srCount = (data.smartrecruiters || []).length;
  const levCount = (data.lever || []).length;
  const wdCount = (data.workday || []).length;
  const total = ghCount + ashCount + srCount + levCount + wdCount;

  document.getElementById('statTotal').textContent = total;
  document.getElementById('statGh').textContent = ghCount;
  document.getElementById('statAshby').textContent = ashCount;
  document.getElementById('statSr').textContent = srCount;
  document.getElementById('statLever').textContent = levCount;
  document.getElementById('statWd').textContent = wdCount;

  document.getElementById('pillAll').textContent = total;
  document.getElementById('pillGh').textContent = ghCount;
  document.getElementById('pillAshby').textContent = ashCount;
  document.getElementById('pillSr').textContent = srCount;
  document.getElementById('pillLever').textContent = levCount;
  document.getElementById('pillWd').textContent = wdCount;
}

function renderTable() {
  const query = searchInput.value.toLowerCase().trim();

  const filtered = allCompanies.filter(comp => {
    // Filter by ATS pill
    if (currentFilter !== 'all' && comp.ats !== currentFilter) {
      return false;
    }
    // Search query match
    if (query) {
      const matchName = (comp.name || '').toLowerCase().includes(query);
      const matchSlug = (comp.slug || '').toLowerCase().includes(query);
      const matchId = (comp.source_id || '').toLowerCase().includes(query);
      const matchCountry = (comp.country || '').toLowerCase().includes(query);
      return matchName || matchSlug || matchId || matchCountry;
    }
    return true;
  });

  showingCount.textContent = `Showing ${filtered.length} of ${allCompanies.length} companies`;

  if (filtered.length === 0) {
    companiesTbody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align:center; padding: 40px; color: var(--text-muted)">
          No companies found matching your query or filter.
        </td>
      </tr>
    `;
    return;
  }

  companiesTbody.innerHTML = filtered.map(comp => `
    <tr>
      <td>
        <div class="company-name-cell">
          <div class="company-avatar">${(comp.name || '?').charAt(0).toUpperCase()}</div>
          <span>${comp.name}</span>
        </div>
      </td>
      <td>
        <span class="ats-tag ${comp.ats}">${formatAtsLabel(comp.ats)}</span>
      </td>
      <td>
        <code class="slug-code">${comp.slug}</code>
      </td>
      <td>
        <span class="source-id-code">${comp.source_id || '-'}</span>
      </td>
      <td>${comp.country || 'Global'}</td>
      <td>
        <div class="action-btns">
          <button class="btn-table-action" onclick="testRowConnection('${comp.ats}', '${comp.slug}')">⚡ Test</button>
          <button class="btn-table-action delete" onclick="deleteCompany('${comp.ats}', '${comp.slug}', '${comp.name}')">🗑</button>
        </div>
      </td>
    </tr>
  `).join('');
}

function formatAtsLabel(ats) {
  const map = {
    greenhouse: 'Greenhouse',
    ashby: 'Ashby',
    smartrecruiters: 'SmartRecruiters',
    lever: 'Lever',
    workday: 'Workday'
  };
  return map[ats] || ats;
}

function handleAutoDetect() {
  const url = inputUrl.value.trim().toLowerCase();
  if (!url) {
    showToast('Please enter a URL first', 'error');
    return;
  }

  try {
    const parsed = new URL(url);
    const pathParts = parsed.pathname.split('/').filter(Boolean);

    if (url.includes('greenhouse.io')) {
      selectAts.value = 'greenhouse';
      inputSlug.value = pathParts[0] || '';
    } else if (url.includes('ashbyhq.com')) {
      selectAts.value = 'ashby';
      inputSlug.value = pathParts[0] || '';
    } else if (url.includes('lever.co')) {
      selectAts.value = 'lever';
      inputSlug.value = pathParts[0] || '';
    } else if (url.includes('smartrecruiters.com')) {
      selectAts.value = 'smartrecruiters';
      inputSlug.value = pathParts[0] || '';
    } else if (url.includes('myworkdayjobs.com')) {
      selectAts.value = 'workday';
      inputSlug.value = parsed.hostname.split('.')[0] || '';
    } else {
      showToast('Could not auto-detect known ATS from URL. Please pick ATS manually.', 'error');
      return;
    }

    if (!inputName.value && inputSlug.value) {
      inputName.value = inputSlug.value.charAt(0).toUpperCase() + inputSlug.value.slice(1);
    }

    selectAts.dispatchEvent(new Event('change'));
    showToast(`Detected: ${formatAtsLabel(selectAts.value)} (Slug: ${inputSlug.value})`, 'success');
  } catch (e) {
    showToast('Invalid URL format', 'error');
  }
}

async function handleTestConnection() {
  const ats = selectAts.value;
  const slug = inputSlug.value.trim();

  if (!slug) {
    testResultBox.innerHTML = '<span class="status-error">Please specify a company slug first.</span>';
    return;
  }

  testResultBox.innerHTML = '<span class="status-loading">⏳ Querying live ATS API endpoint...</span>';

  try {
    const res = await fetch('/api/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ats: ats,
        slug: slug,
        board: inputWdBoard.value.trim() || 'external',
        instance: inputWdInstance.value.trim() || 'wd5'
      })
    });
    const result = await res.json();

    if (result.valid) {
      testResultBox.innerHTML = `
        <span class="status-success">
          ✅ Verified Active! Found <strong>${result.jobs_count} live jobs</strong> on ${formatAtsLabel(ats)}.
        </span>
      `;
    } else {
      testResultBox.innerHTML = `
        <span class="status-error">
          ❌ Failed to connect: ${result.error || 'Endpoint returned 404/Empty'}.
        </span>
      `;
    }
  } catch (err) {
    testResultBox.innerHTML = `<span class="status-error">Error: ${err.message}</span>`;
  }
}

async function testRowConnection(ats, slug) {
  showToast(`Testing live connection for ${slug}...`, 'success');
  try {
    const res = await fetch('/api/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ats, slug })
    });
    const result = await res.json();
    if (result.valid) {
      showToast(`[${formatAtsLabel(ats)}] ${slug}: ${result.jobs_count} live jobs active!`, 'success');
    } else {
      showToast(`[${formatAtsLabel(ats)}] ${slug}: Connection warning (${result.error || '404'})`, 'error');
    }
  } catch (e) {
    showToast(`Test failed: ${e.message}`, 'error');
  }
}

async function handleAddCompanySubmit(e) {
  e.preventDefault();

  const payload = {
    name: inputName.value.trim(),
    ats: selectAts.value,
    slug: inputSlug.value.trim(),
    country: inputCountry.value.trim() || 'Global',
    board: inputWdBoard.value.trim() || 'external',
    instance: inputWdInstance.value.trim() || 'wd5'
  };

  try {
    const res = await fetch('/api/add-company', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await res.json();

    if (result.success) {
      showToast(`Successfully added ${payload.name} to ${formatAtsLabel(payload.ats)}!`, 'success');
      addModal.classList.add('hidden');
      loadData();
    } else {
      showToast(`Error: ${result.message}`, 'error');
    }
  } catch (err) {
    showToast(`Network error: ${err.message}`, 'error');
  }
}

async function deleteCompany(ats, slug, name) {
  if (!confirm(`Are you sure you want to remove ${name} (${slug}) from ${formatAtsLabel(ats)}?`)) {
    return;
  }

  try {
    const res = await fetch('/api/delete-company', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ats, slug })
    });
    const result = await res.json();

    if (result.success) {
      showToast(`Removed ${name} from registry.`, 'success');
      loadData();
    } else {
      showToast(`Failed to remove: ${result.message}`, 'error');
    }
  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  }
}

async function handleRunScraper() {
  runnerSection.classList.remove('hidden');
  runnerLogs.textContent = 'Starting test scraping runner for Archetype B...\n';

  try {
    const res = await fetch('/api/run-scraper', { method: 'POST' });
    const data = await res.json();
    runnerLogs.textContent = data.output || 'Scraper execution finished.';
    showToast(`Scraper finished! Extracted ${data.jobs_count || 0} jobs.`, 'success');
  } catch (err) {
    runnerLogs.textContent += '\nError executing scraper: ' + err.message;
    showToast('Failed to run scraper: ' + err.message, 'error');
  }
}

function resetModalForm() {
  addCompanyForm.reset();
  selectAts.value = 'greenhouse';
  inputCountry.value = 'Global';
  workdayFields.classList.add('hidden');
  testResultBox.innerHTML = '<span class="status-idle">Click "Test Live API Connection" to verify active jobs before saving.</span>';
}

function showToast(message, type = 'success') {
  toast.textContent = message;
  toast.className = `toast ${type}`;
  toast.classList.remove('hidden');

  setTimeout(() => {
    toast.classList.add('hidden');
  }, 4000);
}
