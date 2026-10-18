# What the two AI steps are told (summary)

© 2026 Chandra Prakash · prototype built for steer · full prompt text retained by the author

The model is used in exactly two places. Everything else is deterministic code that checks the model's output.

## 1 · `extract` — "careful medical science editor"

**Input:** the full paper. Each block is prefixed with its location id, e.g. `[p24] (Results) …`. Contributions, peer-review history, acknowledgements and references are stripped out.

**Non-negotiable rules**
1. Every claim is backed by a **verbatim quote**, copied character for character. The quote is 1–3 consecutive sentences and is never stitched together from different places.
2. `location` is the bracketed id the quote came from.
3. Every number in the plain-language `finding` must appear in the quote.
4. State the population studied and don't generalise beyond it. Any gap goes in `caveat`.
5. Prefer primary results, and mark background statements as `background`.
6. Never recommend a drug, dose or brand, and never promise weight loss. Record funding and conflicts of interest.
7. Include the limitations the authors state.

**Output (JSON):**
- `paper`: design, population, funding/COI.
- 8–15 `claims`: finding, quote, location, numbers, type, population, caveat, relevance 1–5, and a steer theme (regain, muscle, hunger, india-risk, safety, habits, eligibility).
- `limitations`.
- `do_not_say`: things a careless writer might wrongly conclude from this paper.

Claims are ranked for steer's audience: Indian adults who have tried diets, are curious but sceptical about GLP-1 medicines, and worry about safety, muscle loss, regain and whether it's "for them".

## 2 · `create` — "Instagram writer for steer", one call per format

**Input:** only the *verified* claims, plus paper metadata.

**Steer voice:**
- Doctor-led and credible; every factual line cites claim ids.
- Warm and community-first ("aap", never "tum"). Never shames.
- Made for India: rotis, chai, weddings, desk jobs, the 4 pm biscuit.
- About habits, not quick fixes. Sentence case, short lines.

**Hard bans:**
- drug or brand names;
- weight-loss promises, kilos or timelines;
- miracle/melt/guaranteed language;
- before/after;
- shame words;
- numbers that aren't in the claims;
- creating demand for drug therapy.

**Task:** pick ONE message and give the REASONING for this audience. Then write the format in **English and natural Hinglish**, with captions in both, hashtags and alt text, plus a `claim_map` that links every line to its claim ids. Each format has an exact schema:

- **Carousel:** 5–7 slides from cover / stat / explain / myth-vs-science / habit / cta. A source slide is added automatically.
- **Static:** kicker, big stat, headline, support line and a handwritten note. It is auto-resized to feed, square and story.
- **Reel:** 5–7 scenes, each with on-screen text, a spoken Hinglish line and a visual (kinetic text, big number, chart from claim numbers, habit list or CTA). Total length 20–35 s.

## Repair round

If the automatic checker finds problems, the model gets back its own answer and the exact list of failures, for example `number(s) ['327'] in post but in no verified claim`. It must fix every one and return the full JSON again. If the post still fails, it is blocked from export and shown in red on the review board.
