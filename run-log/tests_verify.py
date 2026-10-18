"""Guardrail tests: the pipeline must never let a wrong number, a fake quote or a brand name through.
© 2026 Chandra Prakash · prototype built for steer.   Run:  python3 -m pytest -q tests
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from steerpipe import verify

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = json.load(open(os.path.join(HERE, "papers", "step1ext2022.json"), encoding="utf-8"))
REAL_Q = "From week 0 to week 68, mean weight loss was 17.3% (SD: 9.3%) with semaglutide and 2.0% (SD: 6.1%) with placebo."


def claim(**kw):
    c = {"id": "C1", "finding": "People lost 17.3% over 68 weeks.", "quote": REAL_Q, "location": "p99"}
    c.update(kw); return c


def test_real_quote_passes_and_location_is_corrected():
    ok, dropped = verify.verify_claims({"claims": [claim()]}, DOC)
    assert len(ok) == 1 and not dropped
    assert ok[0]["location"] == "p3" and ok[0]["location_model"] == "p99"   # model said p99; verifier found p3


def test_paraphrased_quote_is_dropped():
    ok, dropped = verify.verify_claims({"claims": [claim(quote="Mean weight loss was about 17% with semaglutide.")]}, DOC)
    assert not ok and "quote not found verbatim in source" in dropped[0]["problems"]


def test_invented_number_in_finding_is_dropped():
    ok, dropped = verify.verify_claims({"claims": [claim(finding="People lost 18.3% over 68 weeks.")]}, DOC)
    assert not ok and "18.3" in dropped[0]["problems"][0]


def test_unicode_and_spacing_differences_still_match():
    q = REAL_Q.replace(" ", "  ").replace("-", "‐")
    ok, _ = verify.verify_claims({"claims": [claim(quote=q)]}, DOC)
    assert ok


def test_number_parser_ignores_names_and_canonicalises():
    assert verify.numbers_in("GLP-1 and type 2 diabetes, phase III") == set()
    assert verify.numbers_in("49.0 years") == verify.numbers_in("age 49")
    assert verify.numbers_in("1,961 adults") == {"1961"}


def _post(text, ids, caption_extra=""):
    return {"en": {"headline": text}, "caption_en": "x " + caption_extra + "\nSource: y\nsteerclub.com", "caption_hi": "",
            "claim_map": [{"text": text, "claim_ids": ids}]}


def test_post_checks():
    ok, _ = verify.verify_claims({"claims": [claim()]}, DOC)
    by = {c["id"]: c for c in ok}
    assert verify.check_post(_post("People lost 17.3% in 68 weeks", ["C1"]), by) == []
    assert any("not in cited claims" in i for i in verify.check_post(_post("People lost 21% in 68 weeks", ["C1"]), by))
    assert any("unverified" in i for i in verify.check_post(_post("People lost 17.3%", ["C9"]), by))
    assert any("in no verified claim" in i for i in verify.check_post(_post("ok", ["C1"], caption_extra="327 adults"), by))
    assert any("drug/brand" in i for i in verify.check_post(_post("Wegovy works", ["C1"]), by))
    assert any("promise" in i for i in verify.check_post(_post("Lose 10 kg in 30 days", ["C1"]), by))
    p = _post("ok", ["C1"]); p["caption_en"] = "no sign-off"
    assert any("steerclub.com" in i for i in verify.check_post(p, by))


def test_doi_digits_are_not_treated_as_stats():
    ok, _ = verify.verify_claims({"claims": [claim()]}, DOC)
    by = {c["id"]: c for c in ok}
    assert verify.check_post(_post("ok", ["C1"], caption_extra="(doi:10.1111/dom.14725)"), by) == []
