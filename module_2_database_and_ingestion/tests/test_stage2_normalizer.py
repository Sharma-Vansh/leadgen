"""
Unit Tests for Stage 2: Normalization Engine
Tests SalaryConverter, LocationCleaner, DateParser, and TypeClassifier.
"""
from datetime import datetime, timezone
import pytest

from module_2_database_and_ingestion.ingestion.stage2_normalizer import (
    SalaryConverter,
    LocationCleaner,
    DateParser,
    TypeClassifier
)


# --- SalaryConverter Tests ---

def test_lpa_salary_conversion():
    s_min, s_max, curr = SalaryConverter.convert("6.5 - 12.0 LPA")
    assert s_min == 650000.0
    assert s_max == 1200000.0
    assert curr == "INR"


def test_monthly_stipend_conversion():
    s_min, s_max, curr = SalaryConverter.convert("₹35,000 per month")
    assert s_min == 420000.0
    assert s_max == 420000.0
    assert curr == "INR"


def test_foreign_currency_conversion():
    # $80k to $120k with USD=83.5
    s_min, s_max, curr = SalaryConverter.convert("$80k - $120k")
    assert s_min == round(80 * 1000 * 83.5, 2)
    assert s_max == round(120 * 1000 * 83.5, 2)
    assert curr == "INR"


def test_unknown_salary_returns_none():
    s_min, s_max, curr = SalaryConverter.convert("Not Disclosed / Best in Industry")
    assert s_min is None
    assert s_max is None
    assert curr == "INR"


# --- LocationCleaner Tests ---

def test_city_alias_normalization():
    loc, is_rem, cntry, city = LocationCleaner.clean("Bengaluru, Karnataka")
    assert city == "Bangalore"
    assert is_rem is False
    assert cntry == "India"


def test_gurgaon_mumbai_normalization():
    loc1, _, _, city1 = LocationCleaner.clean("Gurugram Office")
    assert city1 == "Gurgaon"

    loc2, _, _, city2 = LocationCleaner.clean("Bombay / Navi Mumbai")
    assert city2 == "Navi Mumbai" or city2 == "Mumbai"


def test_explicit_remote_detection():
    loc, is_rem, cntry, city = LocationCleaner.clean("Remote / Work from home")
    assert is_rem is True
    assert "Remote" in loc


# --- DateParser Tests ---

def test_iso_date_parsing():
    dt = DateParser.parse("2026-10-15")
    assert dt is not None
    assert dt.year == 2026
    assert dt.month == 10
    assert dt.day == 15
    assert dt.tzinfo == timezone.utc


def test_relative_date_with_injected_clock():
    ref = datetime(2026, 10, 15, 12, 0, 0, tzinfo=timezone.utc)
    dt = DateParser.parse("2 days ago", reference_time=ref)
    assert dt is not None
    assert dt.day == 13


def test_unknown_date_returns_none():
    dt = DateParser.parse("Invalid date string or missing")
    assert dt is None


# --- TypeClassifier Tests ---

def test_internship_classification():
    t_type, conf = TypeClassifier.classify("Summer Analyst", title="Software Engineering Intern")
    assert t_type == "internship"
    assert conf == "high"


def test_gig_classification():
    t_type, conf = TypeClassifier.classify("Field Partner", title="Delivery Rider & Driver")
    assert t_type == "gig"
    assert conf == "high"


def test_contract_classification():
    t_type, conf = TypeClassifier.classify("Contractual (6 Months)", title="DevOps Consultant")
    assert t_type == "contract"
    assert conf == "high"
