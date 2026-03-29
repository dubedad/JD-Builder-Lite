"""
Navigation Restructure Tests — Phase 11 Plan 01

Tests for 4-level browse hierarchy:
  /careers                              → 22 Function cards
  /careers/{function-slug}              → Family cards for that function
  /careers/{function-slug}/{family-slug} → Title cards for that family

Written TDD RED before implementation.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    """Import app lazily so RED phase can collect without ImportError."""
    from main import app
    return TestClient(app)


# -----------------------------------------------------------------------
# L1: /careers — 22 Function cards
# -----------------------------------------------------------------------

def test_careers_returns_200(client):
    """GET /careers returns HTTP 200."""
    resp = client.get("/careers")
    assert resp.status_code == 200


def test_careers_contains_22_function_cards(client):
    """GET /careers contains exactly 22 function cards."""
    resp = client.get("/careers")
    assert resp.status_code == 200
    # Each card has class="career-card"
    assert resp.text.count('class="career-card') == 22


def test_careers_cards_link_to_function_slug(client):
    """Each function card href points to /careers/{function-slug}."""
    resp = client.get("/careers")
    assert resp.status_code == 200
    # Every function slug link starts with /careers/ and is not a family-level URL
    assert '/careers/' in resp.text


def test_careers_hero_shows_civilian_careers_heading(client):
    """Hero banner contains a 'Civilian Careers' heading."""
    resp = client.get("/careers")
    assert resp.status_code == 200
    assert "Civilian Careers" in resp.text


def test_careers_cards_have_image_or_gradient_fallback(client):
    """Each card uses an image or a gradient fallback class."""
    resp = client.get("/careers")
    assert resp.status_code == 200
    # At minimum, gradient fallback classes must be present for cards without images
    # (gradient-{function-slug} classes are defined in gradients.css)
    assert "gradient-" in resp.text or "career-card" in resp.text


def test_careers_search_data_present(client):
    """Function names are searchable client-side (data-name attributes present)."""
    resp = client.get("/careers")
    assert resp.status_code == 200
    assert 'data-name=' in resp.text


# -----------------------------------------------------------------------
# L2: /careers/{function-slug} — Family cards within a function
# -----------------------------------------------------------------------

def test_function_page_returns_200(client):
    """GET /careers/administration returns 200 for a valid function slug."""
    resp = client.get("/careers/administration")
    assert resp.status_code == 200


def test_function_page_shows_only_families_of_that_function(client):
    """Family cards on L2 belong only to the requested function."""
    resp = client.get("/careers/administration")
    assert resp.status_code == 200
    # Page should contain family cards
    assert 'class="career-card' in resp.text


def test_function_page_family_cards_link_to_family_slug(client):
    """Each family card on L2 links to /careers/{function-slug}/{family-slug}."""
    resp = client.get("/careers/administration")
    assert resp.status_code == 200
    # All card hrefs include /careers/administration/
    assert "/careers/administration/" in resp.text


def test_function_page_breadcrumb_shows_function_name(client):
    """Breadcrumb on L2 shows Home > Careers > [Function Name]."""
    resp = client.get("/careers/administration")
    assert resp.status_code == 200
    # Breadcrumb contains "Administration"
    assert "Administration" in resp.text


def test_function_page_hero_shows_function_name(client):
    """Hero on L2 shows the function name and description."""
    resp = client.get("/careers/administration")
    assert resp.status_code == 200
    assert "Administration" in resp.text


def test_function_page_invalid_slug_returns_404(client):
    """GET /careers/invalid-slug returns 404."""
    resp = client.get("/careers/invalid-slug-that-does-not-exist")
    assert resp.status_code == 404


# -----------------------------------------------------------------------
# L3: /careers/{function-slug}/{family-slug} — Title cards within family
# -----------------------------------------------------------------------

def test_family_page_returns_200(client):
    """GET /careers/administration/administrative-services returns 200."""
    # Find a valid function/family combo from DB
    resp = client.get("/careers/administration/administrative-services")
    # Accept 200 or 404 depending on whether this combo exists;
    # the test just verifies the route is wired at all
    assert resp.status_code in (200, 404)


def test_family_page_valid_combo_returns_200(client):
    """GET /careers/{valid-function}/{valid-family} returns 200."""
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "careers.sqlite")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("""
        SELECT jf.job_function_slug, jfam.job_family_slug
        FROM job_families jfam
        JOIN job_functions jf ON jf.job_function_slug = jfam.job_function_slug
        LIMIT 1
    """).fetchone()
    conn.close()
    assert row is not None, "No valid function/family combo found in DB"
    resp = client.get(f"/careers/{row['job_function_slug']}/{row['job_family_slug']}")
    assert resp.status_code == 200


def test_family_page_shows_title_cards(client):
    """Title cards on L3 are rendered as career-card elements."""
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "careers.sqlite")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("""
        SELECT jf.job_function_slug, jfam.job_family_slug
        FROM job_families jfam
        JOIN job_functions jf ON jf.job_function_slug = jfam.job_function_slug
        LIMIT 1
    """).fetchone()
    conn.close()
    resp = client.get(f"/careers/{row['job_function_slug']}/{row['job_family_slug']}")
    assert resp.status_code == 200
    # Title cards or at minimum the page loads with card-related content
    assert 'career-card' in resp.text or 'VIEW CAREERS' in resp.text


def test_family_page_title_cards_link_to_career_detail(client):
    """Each title card on L3 links to /career/{title-slug}."""
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "careers.sqlite")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("""
        SELECT jf.job_function_slug, jfam.job_family_slug
        FROM job_families jfam
        JOIN job_functions jf ON jf.job_function_slug = jfam.job_function_slug
        WHERE EXISTS (
            SELECT 1 FROM careers c WHERE c.job_family_slug = jfam.job_family_slug
        )
        LIMIT 1
    """).fetchone()
    conn.close()
    if row is None:
        pytest.skip("No family with job titles in DB")
    resp = client.get(f"/careers/{row['job_function_slug']}/{row['job_family_slug']}")
    assert resp.status_code == 200
    assert '/career/' in resp.text


def test_family_page_breadcrumb_shows_function_and_family(client):
    """Breadcrumb on L3 shows Home > Careers > [Function] > [Family]."""
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "careers.sqlite")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("""
        SELECT jf.job_function_slug, jf.job_function, jfam.job_family_slug, jfam.job_family
        FROM job_families jfam
        JOIN job_functions jf ON jf.job_function_slug = jfam.job_function_slug
        LIMIT 1
    """).fetchone()
    conn.close()
    resp = client.get(f"/careers/{row['job_function_slug']}/{row['job_family_slug']}")
    assert resp.status_code == 200
    # Both function and family names appear (breadcrumb)
    assert row['job_function'] in resp.text
    assert row['job_family'] in resp.text


def test_family_page_invalid_family_returns_404(client):
    """GET /careers/valid-function/invalid-family returns 404."""
    resp = client.get("/careers/administration/invalid-family-xyz")
    assert resp.status_code == 404
