"""PDF route: two-column journal PDFs must come in as clean, quotable, located text.
© 2026 Chandra Prakash · prototype built for steer."""
import os, sys, json
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import pytest
from steerpipe import ingest, verify

PDF = os.path.join(HERE, "papers", "paper-step1ext2022-weight-regain.pdf")
pytestmark = pytest.mark.skipif(not os.path.exists(PDF), reason="sample PDF not present")


@pytest.fixture(scope="module")
def doc():
    return ingest.from_pdf(PDF)


def test_metadata_from_page_one(doc):
    m = doc["meta"]
    assert m["doi"] == "10.1111/dom.14725" and m["year"] == "2022" and m["journal"] == "Diabetes Obes Metab"
    assert m["authors"][0] == "John P. H. Wilding"          # degrees and affiliation digits stripped


def test_sections_found_and_references_skipped(doc):
    secs = {b["section"] for b in doc["blocks"]}
    assert {"Introduction", "Results", "Discussion", "References"} <= secs
    assert "[page" in ingest.to_prompt_text(doc) and "(References)" not in ingest.to_prompt_text(doc)


def test_quote_spanning_lines_and_hyphenation_verifies(doc):
    # in the PDF this sentence is broken over 4 lines with 'treat-/ment'-style hyphenation
    q = "Following treatment withdrawal, semaglutide and placebo participants regained 11.6 (SD: 7.7) and 1.9 (SD: 4.8) percentage points of lost weight, respectively, by week 120"
    loc = verify.find_location(q, doc)
    assert loc and loc.startswith("page 2")


def test_web_and_pdf_routes_agree():
    ext = json.load(open(os.path.join(HERE, "outputs", "step1-ext", "prompts", "extract.json")))
    ok, dropped = verify.verify_claims(ext, ingest.from_pdf(PDF))
    assert len(ok) >= 12        # remaining 2 differ only in how citation markers are typeset (web " 8 , 9 ;" vs PDF "8,9;")
