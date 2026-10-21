"""
LeadGen Module 6 — Chrome Extension & Autofill Assistant Test Suite
Validates Manifest V3 compliance, referenced asset integrity, and field mapping heuristics
"""

import os
import json
import re
import pytest

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_PATH = os.path.join(MODULE_DIR, "manifest.json")


def test_manifest_structure_and_v3_compliance():
    """Verify manifest.json is valid Manifest V3 with all mandatory properties."""
    assert os.path.exists(MANIFEST_PATH), "manifest.json does not exist"
    
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest.get("manifest_version") == 3, "Extension must use Manifest V3"
    assert manifest.get("name") == "LeadGen AI — Autonomous Job & Exam Autofill"
    assert manifest.get("version") == "1.0.0"
    
    # Required permissions
    perms = manifest.get("permissions", [])
    assert "storage" in perms, "Must have storage permission"
    assert "activeTab" in perms, "Must have activeTab permission"
    assert "scripting" in perms, "Must have scripting permission"


def test_manifest_referenced_files_exist():
    """Verify that every file referenced in manifest.json actually exists on disk."""
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Check background service worker
    sw_path = manifest.get("background", {}).get("service_worker")
    assert sw_path, "Background service worker must be declared"
    assert os.path.exists(os.path.join(MODULE_DIR, sw_path)), f"Missing service worker: {sw_path}"

    # Check content scripts and CSS
    content_scripts = manifest.get("content_scripts", [])
    assert len(content_scripts) > 0, "At least one content script bundle must be declared"
    for cs in content_scripts:
        for js_file in cs.get("js", []):
            assert os.path.exists(os.path.join(MODULE_DIR, js_file)), f"Missing content js: {js_file}"
        for css_file in cs.get("css", []):
            assert os.path.exists(os.path.join(MODULE_DIR, css_file)), f"Missing content css: {css_file}"

    # Check popup files
    popup_html = manifest.get("action", {}).get("default_popup")
    assert popup_html, "Default popup html must be defined"
    assert os.path.exists(os.path.join(MODULE_DIR, popup_html)), f"Missing popup html: {popup_html}"

    # Check icons
    icons = manifest.get("icons", {})
    for size, icon_file in icons.items():
        assert os.path.exists(os.path.join(MODULE_DIR, icon_file)), f"Missing icon ({size}): {icon_file}"


def test_field_mapper_regex_coverage():
    """Verify regex patterns in field_mapper.js against known ATS input signatures."""
    mapper_path = os.path.join(MODULE_DIR, "content", "field_mapper.js")
    with open(mapper_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Test cases: (input_string, expected_field)
    test_cases = [
        # Workday attributes
        ("first_name", "firstName"),
        ("legal_first_name", "firstName"),
        ("last_name", "lastName"),
        ("candidate_email_address", "email"),
        ("contact_phone_number", "phone"),
        ("linkedin_profile_url", "linkedin"),
        ("github_repository_link", "github"),
        ("personal_website_portfolio", "portfolio"),
        ("college_university_name", "university"),
        ("highest_degree_earned", "degree"),
        ("major_discipline", "major"),
        ("cumulative_cgpa_score", "cgpa"),
        ("year_of_passing_graduation", "graduationYear"),
        ("street_address_line1", "address"),
        ("city_locality", "city"),
        ("postal_pincode", "postalCode"),
        # Govt Exam attributes
        ("candidate_full_name", "fullName"),
        ("date_of_birth_dob", "dob"),
        ("gender_identity", "gender"),
    ]

    for identifier, expected_field in test_cases:
        # Check rule match
        rule_pattern = rf"field:\s*'{expected_field}',\s*regex:\s*/([^/]+)/i"
        match = re.search(rule_pattern, content)
        assert match, f"Missing rule definition for {expected_field}"
        regex_str = match.group(1)
        
        is_matched = bool(re.search(regex_str, identifier, re.IGNORECASE))
        assert is_matched, f"Regex for {expected_field} failed to match '{identifier}'"


def test_default_profile_schema_completeness():
    """Verify default_profile.js contains all core fields for zero-hallucination autofill."""
    profile_path = os.path.join(MODULE_DIR, "shared", "default_profile.js")
    with open(profile_path, "r", encoding="utf-8") as f:
        content = f.read()

    required_keys = [
        "fullName", "firstName", "lastName", "email", "phone",
        "linkedin", "github", "portfolio", "institution", "degree",
        "cgpa", "graduationYear", "summary", "coverLetter", "skills"
    ]

    for key in required_keys:
        assert f"{key}:" in content, f"default_profile.js missing key: {key}"
