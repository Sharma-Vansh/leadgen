/**
 * LeadGen Field Mapper & Heuristics Engine
 * Accurately associates diverse ATS & Govt form inputs with candidate profile fields
 */

const FieldMapper = {
  // Regex pattern rules for field classification
  rules: [
    { field: 'firstName', regex: /first.*name|fname|given.*name|legal.*first/i },
    { field: 'lastName', regex: /last.*name|lname|family.*name|surname|legal.*last/i },
    { field: 'fullName', regex: /^name$|full.*name|candidate.*name|applicant.*name|your.*name/i },
    { field: 'email', regex: /email|e-mail|mail.*address/i },
    { field: 'phone', regex: /phone|mobile|contact.*no|telephone|cell/i },
    { field: 'linkedin', regex: /linkedin|linked.*in/i },
    { field: 'github', regex: /github|git.*profile/i },
    { field: 'portfolio', regex: /portfolio|website|personal.*site|web.*link/i },
    { field: 'university', regex: /college|university|school|institution|academic.*inst/i },
    { field: 'degree', regex: /degree|qualification|highest.*degree|program/i },
    { field: 'major', regex: /major|discipline|branch|field.*of.*study|department/i },
    { field: 'cgpa', regex: /cgpa|gpa|percentage|marks|grade/i },
    { field: 'graduationYear', regex: /grad.*year|pass.*year|year.*of.*passing|completion.*year/i },
    { field: 'address', regex: /address|street|line.*1/i },
    { field: 'city', regex: /city|town|district/i },
    { field: 'state', regex: /state|province|region/i },
    { field: 'postalCode', regex: /zip|postal|pincode|pin.*code/i },
    { field: 'country', regex: /country|nation/i },
    { field: 'summary', regex: /summary|bio|about.*you|brief.*intro/i },
    { field: 'coverLetter', regex: /cover.*letter|statement|pitch|why.*hire/i },
    { field: 'gender', regex: /gender|sex/i },
    { field: 'dob', regex: /dob|birth.*date|date.*of.*birth/i }
  ],

  getElementLabel(el) {
    // 1. Associated <label for="...">
    if (el.id) {
      const label = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
      if (label && label.innerText) return label.innerText.trim();
    }

    // 2. Parent label tag
    const parentLabel = el.closest('label');
    if (parentLabel && parentLabel.innerText) return parentLabel.innerText.trim();

    // 3. Preceding sibling label or span
    let prev = el.previousElementSibling;
    while (prev) {
      if (prev.tagName === 'LABEL' || prev.tagName === 'SPAN' || prev.tagName === 'DIV') {
        const text = prev.innerText.trim();
        if (text && text.length < 50) return text;
      }
      prev = prev.previousElementSibling;
    }

    return '';
  },

  classifyElement(el) {
    if (!el || el.type === 'hidden' || el.type === 'submit' || el.type === 'button') {
      return null;
    }

    const identifiers = [
      el.name || '',
      el.id || '',
      el.placeholder || '',
      el.getAttribute('aria-label') || '',
      el.getAttribute('data-automation-id') || '',
      el.autocomplete || '',
      this.getElementLabel(el)
    ].join(' ').toLowerCase();

    for (const rule of this.rules) {
      if (rule.regex.test(identifiers)) {
        return rule.field;
      }
    }

    return null;
  },

  getValueForField(field, profile) {
    if (!profile) return null;
    return profile[field] || null;
  },

  setElementValue(el, value) {
    if (!el || value === undefined || value === null) return false;

    // Handle standard inputs & textareas
    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
      el.focus();
      el.value = value;

      // Dispatch comprehensive synthetic events for React/Workday listeners
      el.dispatchEvent(new Event('input', { bubbles: true, cancelable: true }));
      el.dispatchEvent(new Event('change', { bubbles: true, cancelable: true }));
      el.dispatchEvent(new Event('blur', { bubbles: true, cancelable: true }));
      return true;
    }

    // Handle select elements
    if (el.tagName === 'SELECT') {
      const options = Array.from(el.options);
      const valLower = String(value).toLowerCase();

      // Find best matching option
      const match = options.find(opt => 
        opt.value.toLowerCase().includes(valLower) || 
        opt.text.toLowerCase().includes(valLower)
      );

      if (match) {
        el.value = match.value;
        el.dispatchEvent(new Event('change', { bubbles: true }));
        return true;
      }
    }

    return false;
  }
};

// Export for tests
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { FieldMapper };
}
