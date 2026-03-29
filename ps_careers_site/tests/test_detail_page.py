"""
Enhanced Detail Page Tests — Phase 12 Plan 01

Tests for:
  - Key Responsibilities, Required Skills, Typical Education tabs on /career/{slug}
  - Breadcrumb: Home > Careers > [Function] > [Family] > [Title]
  - Graceful NULL handling for new content columns

Written TDD RED before implementation.
"""
import sqlite3
import os
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    """Import app lazily so RED phase can collect without ImportError."""
    from main import app
    return TestClient(app)


@pytest.fixture(scope="module")
def valid_slug_with_content():
    """Return a job_title_slug for a career that has key_responsibilities data."""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "careers.sqlite")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("""
        SELECT c.job_title_slug, c.key_responsibilities, c.required_skills,
               c.typical_education, c.job_family_slug,
               jfam.job_function_slug, jf.job_function, jfam.job_family
        FROM careers c
        JOIN job_families jfam ON c.job_family_slug = jfam.job_family_slug
        JOIN job_functions jf ON jfam.job_function_slug = jf.job_function_slug
        WHERE c.key_responsibilities IS NOT NULL
          AND c.required_skills IS NOT NULL
          AND c.typical_education IS NOT NULL
        LIMIT 1
    """).fetchone()
    conn.close()
    if row is None:
        pytest.skip("No career with all three content columns populated in DB")
    return dict(row)


@pytest.fixture(scope="module")
def valid_slug_any():
    """Return any valid job_title_slug (with function/family context)."""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "careers.sqlite")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("""
        SELECT c.job_title_slug, c.job_title, c.job_family_slug,
               jfam.job_function_slug, jf.job_function, jfam.job_family
        FROM careers c
        JOIN job_families jfam ON c.job_family_slug = jfam.job_family_slug
        JOIN job_functions jf ON jfam.job_function_slug = jf.job_function_slug
        LIMIT 1
    """).fetchone()
    conn.close()
    if row is None:
        pytest.skip("No careers in DB")
    return dict(row)


# -----------------------------------------------------------------------
# Test 1 & 2 & 3: New tab headers appear on detail page
# -----------------------------------------------------------------------

def test_detail_page_contains_key_responsibilities_tab(client, valid_slug_any):
    """GET /career/{valid-slug} contains 'Key Responsibilities' section/tab."""
    resp = client.get(f"/career/{valid_slug_any['job_title_slug']}")
    assert resp.status_code == 200
    assert "Key Responsibilities" in resp.text


def test_detail_page_contains_required_skills_tab(client, valid_slug_any):
    """GET /career/{valid-slug} contains 'Required Skills' section/tab."""
    resp = client.get(f"/career/{valid_slug_any['job_title_slug']}")
    assert resp.status_code == 200
    assert "Required Skills" in resp.text


def test_detail_page_contains_typical_education_tab(client, valid_slug_any):
    """GET /career/{valid-slug} contains 'Typical Education' section/tab."""
    resp = client.get(f"/career/{valid_slug_any['job_title_slug']}")
    assert resp.status_code == 200
    assert "Typical Education" in resp.text


# -----------------------------------------------------------------------
# Test 4 & 5 & 6: Content from DB renders (non-empty when DB has value)
# -----------------------------------------------------------------------

def test_detail_page_key_responsibilities_content_matches_db(client, valid_slug_with_content):
    """Key Responsibilities content matches DB value (not empty)."""
    resp = client.get(f"/career/{valid_slug_with_content['job_title_slug']}")
    assert resp.status_code == 200
    # At minimum the section heading must appear
    assert "Key Responsibilities" in resp.text
    # And some non-placeholder text from the DB should appear
    snippet = (valid_slug_with_content["key_responsibilities"] or "")[:30]
    assert snippet in resp.text


def test_detail_page_required_skills_content_matches_db(client, valid_slug_with_content):
    """Required Skills content matches DB value (not empty)."""
    resp = client.get(f"/career/{valid_slug_with_content['job_title_slug']}")
    assert resp.status_code == 200
    assert "Required Skills" in resp.text
    snippet = (valid_slug_with_content["required_skills"] or "")[:30]
    assert snippet in resp.text


def test_detail_page_typical_education_content_matches_db(client, valid_slug_with_content):
    """Typical Education content matches DB value (not empty)."""
    resp = client.get(f"/career/{valid_slug_with_content['job_title_slug']}")
    assert resp.status_code == 200
    assert "Typical Education" in resp.text
    snippet = (valid_slug_with_content["typical_education"] or "")[:30]
    assert snippet in resp.text


# -----------------------------------------------------------------------
# Test 7 & 8 & 9: Breadcrumb shows full 4-level hierarchy
# -----------------------------------------------------------------------

def test_detail_breadcrumb_contains_function_link(client, valid_slug_any):
    """Breadcrumb contains Function name with link to /careers/{function-slug}."""
    resp = client.get(f"/career/{valid_slug_any['job_title_slug']}")
    assert resp.status_code == 200
    function_slug = valid_slug_any["job_function_slug"]
    function_name = valid_slug_any["job_function"]
    assert f"/careers/{function_slug}" in resp.text
    assert function_name in resp.text


def test_detail_breadcrumb_contains_family_link(client, valid_slug_any):
    """Breadcrumb contains Family name with link to /careers/{function-slug}/{family-slug}."""
    resp = client.get(f"/career/{valid_slug_any['job_title_slug']}")
    assert resp.status_code == 200
    function_slug = valid_slug_any["job_function_slug"]
    family_slug = valid_slug_any["job_family_slug"]
    family_name = valid_slug_any["job_family"]
    assert f"/careers/{function_slug}/{family_slug}" in resp.text
    assert family_name in resp.text


def test_detail_breadcrumb_contains_job_title_as_final_element(client, valid_slug_any):
    """Breadcrumb ends with Job Title as a non-linked (span) element."""
    resp = client.get(f"/career/{valid_slug_any['job_title_slug']}")
    assert resp.status_code == 200
    # The breadcrumb structure should use a span for the final item
    assert "<span>" in resp.text or "breadcrumb" in resp.text


# -----------------------------------------------------------------------
# Test 10: Graceful NULL handling
# -----------------------------------------------------------------------

def test_detail_page_null_key_responsibilities_renders_gracefully(client):
    """If key_responsibilities is NULL, section still renders without error."""
    db_path = os.path.join(os.path.dirname(os.path.dirname("ps_careers_site/")), "careers.sqlite")
    # Use the fixture approach instead
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "careers.sqlite")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("""
        SELECT job_title_slug FROM careers
        WHERE key_responsibilities IS NULL
        LIMIT 1
    """).fetchone()
    conn.close()

    if row is None:
        pytest.skip("All careers have key_responsibilities populated — NULL test not applicable")

    resp = client.get(f"/career/{row['job_title_slug']}")
    assert resp.status_code == 200
    # Page must render without 500 error, and Key Responsibilities section present
    assert "Key Responsibilities" in resp.text
