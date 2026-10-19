"""
Unit Tests for Stage 1: Validation Gate
"""
import pytest
from module_2_database_and_ingestion.ingestion.stage1_validator import Stage1Validator, ValidationResult
from module_1_scraping_engine.core.schema import StandardJobListing


def test_valid_standard_listing():
    data = {
        "source_id": "SRC-0001",
        "source_name": "Naukri",
        "title": "Senior Python Backend Engineer",
        "company": "Swiggy",
        "apply_url": "https://www.naukri.com/job/senior-python-swiggy-001"
    }
    validated, reason = Stage1Validator.validate_single(data)
    assert reason is None
    assert validated is not None
    assert validated["title"] == "Senior Python Backend Engineer"
    assert validated["company"] == "Swiggy"


def test_missing_title_rejected():
    data = {
        "source_id": "SRC-0001",
        "source_name": "Naukri",
        "title": "  ",
        "company": "Swiggy",
        "apply_url": "https://www.naukri.com/job/001"
    }
    validated, reason = Stage1Validator.validate_single(data)
    assert validated is None
    assert "Title is missing" in reason


def test_missing_company_private_rejected():
    data = {
        "source_id": "SRC-0001",
        "source_name": "Naukri",
        "title": "Java Developer",
        "company": "",
        "apply_url": "https://www.naukri.com/job/001"
    }
    validated, reason = Stage1Validator.validate_single(data)
    assert validated is None
    assert "Company name is missing" in reason


def test_missing_company_govt_default_assigned():
    data = {
        "source_id": "SRC-0257",  # Archetype C govt discovery
        "source_name": "SarkariResult",
        "title": "SSC CGL 2026 Notification",
        "company": "",
        "apply_url": "https://ssc.gov.in/cgl-2026"
    }
    validated, reason = Stage1Validator.validate_single(data)
    assert reason is None
    assert validated is not None
    assert validated["company"] == "Central / State Government Recruitment"


def test_invalid_url_protocol_rejected():
    data = {
        "source_id": "SRC-0001",
        "source_name": "Naukri",
        "title": "Python Dev",
        "company": "Infosys",
        "apply_url": "ftp://files.example.com/job"
    }
    validated, reason = Stage1Validator.validate_single(data)
    assert validated is None
    assert "invalid protocol" in reason


def test_blocklisted_domain_rejected():
    data = {
        "source_id": "SRC-0001",
        "source_name": "Naukri",
        "title": "Earn $5000 a day",
        "company": "Crypto Scheme",
        "apply_url": "https://free-crypto-giveaway.xyz/apply"
    }
    validated, reason = Stage1Validator.validate_single(data)
    assert validated is None
    assert "security blocklist" in reason


def test_batch_validation_reporting():
    batch = [
        {"source_id": "SRC-01", "source_name": "Portal", "title": "Job 1", "company": "Comp", "apply_url": "https://comp.com/1"},
        {"source_id": "SRC-01", "source_name": "Portal", "title": "", "company": "Comp", "apply_url": "https://comp.com/2"},
        {"source_id": "SRC-01", "source_name": "Portal", "title": "Job 3", "company": "Comp", "apply_url": "invalid-url"},
    ]
    res: ValidationResult = Stage1Validator.validate_batch(batch)
    assert res.total_count == 3
    assert res.valid_count == 1
    assert res.rejected_count == 2
    assert len(res.rejected_records) == 2
