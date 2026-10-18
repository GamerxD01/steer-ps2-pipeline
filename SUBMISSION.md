# steerpipe — research paper → doctor-approved Instagram posts

**Problem Statement 2 · Steer Hackathon · Chandra Prakash**
© 2026 Chandra Prakash · prototype built for steer · evaluation only (see LICENSE.txt)

> **One line:** drop in a DOI, a PDF or a list of them. steerpipe pulls out the findings *word for word*, proves every number against the paper, writes a carousel, static or reel in English and Hinglish, and puts each post in front of a doctor. The doctor sees every line next to the exact sentence it came from. Nothing is exported until the doctor approves it.

---

## What's in this folder

| File | What it is |
|---|---|
| `review-board.html` | **Start here.** The doctor review gate for the demo batch (4 papers → 4 posts). Open it in Chrome, type a reviewer name, then tick claims ✓/✗, approve or request changes, and download `approvals.json`. |
| `posts/` | Rendered outputs for each paper: PNG slides, statics in 3 sizes, reel MP4 + SRT + cover, captions EN/HI, hashtags, alt text. All watermarked. |
| `architecture.png` | The pipeline on one page. |
| `run-log/` | Proof of the run: per-paper `claims.json` (verified and dropped claims with locations), `post_*.json` (content plus check results), `timing.json`, `llm_log.jsonl`, the batch file, the test results and `schedule.csv`. |
| `PROMPTS.md` | What the two LLM steps are told to do (summary). |
| `LICENSE.txt` | Evaluation-only licence. |

## The demo batch

| Paper | Why this paper | Format | Message |
|---|---|---|---|
| **ICMR-INDIAB-23** — Deepa et al., *Indian J Med Res* 2025 (national survey, 31 States/UTs) | India-specific. Answers "I'm not fat, so this isn't for me." | **Carousel** (8 slides incl. auto source slide) | A normal BMI doesn't mean metabolically healthy. Check your waist, BP and sugar, not just the scale. |
| **STEP 1 extension** — Wilding et al., *Diabetes Obes Metab* 2022 (RCT off-treatment follow-up) | Regain is the #1 GLP-1 fear in our PS1 research. | **Reel** 9:16, 37 s (Hinglish voiceover + captions; silent English cut) | Weight coming back after stopping is biology, not failure, so plan the exit with a doctor. |
| **PREDICT 1 glucose dips** — Wyatt et al., *Nature Metabolism* 2021 (1,070 adults with CGMs) | Explains the "4 pm hunger" (also our PS1 hook). | **Static** (feed 4:5, square, story 9:16) | That hunger 2–3 h after a meal can be a sugar dip, not a willpower problem. |
| **Revised definition of obesity in Asian Indians** — Misra et al., *Diabetes Metab Syndr* 2025 (expert consensus) — **ingested from the PDF** | India's own cut-offs answer "is this even for me?" | **Carousel** (8 slides) | Look beyond the scale: BMI above 23, your waist, and whether daily life or health is affected. |

Three are open access and came in via DOI-style full text; the Misra paper is not open access and went through the **PDF route** end to end. Each post states the study's own limits on the post itself: 97% white sample, cross-sectional design, industry-employed authors, and "lifestyle support was stopped too".

## How it works (see architecture.png)

1. **Ingest.** A DOI is resolved through Europe PMC to structured full text; a PDF goes through PyMuPDF. Every paragraph, table and page gets a **location id** (`p24`, `t2`, `page 3`).
2. **Extract (LLM).** The model returns 8–15 claims. Each claim has a plain-language finding, a **verbatim quote**, the location, the population, a caveat and a steer theme, plus the authors' limitations and a *do-not-say* list.
3. **Verify (code, not AI).**
   - Each quote must exist verbatim in the source after unicode, dash and whitespace normalisation, and the real location *overwrites* the model's.
   - Every number in a finding must be in its quote.
   - Failing claims are dropped and listed on the board.
4. **Create (LLM, per format).** The model picks one message and states why it matters to this audience. It writes EN plus natural Hinglish, captions, hashtags and alt text, and a **claim_map** that ties every line to claim ids.
5. **Check (code).**
   - Every factual line cites a verified claim.
   - Every number is in a cited claim, and no number appears anywhere in the post (captions and alt text included) that isn't in the paper.
   - The post contains no drug or brand names, weight-loss promises, shame words or before/after.
   - The source line and the steerclub.com sign-off are present.
   - **On failure, there is one automatic repair round.** The exact errors go back to the model with its previous answer. If the post still fails, it is blocked from export.
6. **Render (own templates).**
   - HTML templates are shot with headless Chromium.
   - Carousel: 1080×1350 slides with an automatic "every claim, traceable" source slide.
   - Static: auto-resized to feed, square and story with a **shrink-to-fit** pass, because Hinglish runs longer.
   - Reel: 1080×1920 30 fps MP4. The chart is drawn from the paper's real numbers. It has burned Hinglish subtitles in short chunks, an SRT file, and an optional voiceover that the scenes **time-sync to** (silence detection, then pause-tightening, then -14 LUFS).
7. **Doctor review gate.** Covered below.
8. **Export plus calendar.** `run.py --export approvals.json` copies **only approved posts** into dated folders, with captions, alt text and an approval record (who, when, note). `schedule.csv` spreads the posts across the week.

## The doctor's 10 minutes

The review board shows each post with its visuals (EN/Hinglish toggle), message and reasoning, the automatic check results, and a table: **line in the post → claim → verbatim quote → location → "open paper"**.

- The doctor marks each claim ✓ accurate or ✗ not accurate.
- **Approve is disabled** if any claim is ✗, if the automatic checks failed, or if no reviewer name is entered.
- "Request changes" carries a note to the content team.
- Decisions persist and download as `approvals.json`.

**Human time per paper: about 10 minutes of doctor review.** That covers skimming roughly 10 claims next to their quotes and approving 1 post. There is no writing or design time. Machine time for the 4-paper batch was about 3 minutes end to end, mostly reel rendering.

## Guardrails we tested (run-log/tests.txt — 11/11 pass)

The verifier and checker are unit-tested. They catch each of these:

- a paraphrased "quote";
- a finding that says 18.3% when the paper says 17.3%;
- a post line with a number its claim doesn't contain;
- a post citing a claim id that was never verified;
- a number in the caption that isn't in any verified claim;
- "Wegovy";
- "lose 10 kg in 30 days";
- a missing sign-off.

The PDF tests check page-1 metadata, section detection with References skipped, a quote that runs across four PDF lines with hyphenation, and that the web and PDF routes agree.

The checks earned their keep during the demo itself. They flagged that the first reel caption said **"327 adults"**. That number is in the paper but not in any *verified claim*. The repair round removed it; both answers and the exact failure list are in `run-log/step1-ext/`. While tuning, we also fixed three verifier false positives (`GLP-1` read as a stat, `49` vs `49.0`, `type 2 diabetes`) so the gate stays strict without crying wolf.

## PDF route (tested on the author's PDFs)

Most papers arrive as PDFs, so the PDF reader is built for real journal layouts:

- Two-column pages where every line is its own block are re-joined into running text, and line-break hyphenation is undone.
- Running headers and footers are dropped by position and repetition, footnotes by font size and position, and licence or "author manuscript" notices by pattern.
- Section headings are detected, including numbered ones like "5.2. Waist circumference", so References, acknowledgements and similar sections are skipped.
- Authors, journal, year and DOI are read from page 1, with degrees and affiliation markers stripped.
- Text is cut at sentence ends into located chunks (`page 7 ¶4`). Verification also searches whole pages and page boundaries, so a quote that crosses a column or page still matches.

**Cross-check.** The claims verified against the web full text were re-verified against the authors' PDFs (STEP 1 and Wyatt): **23 of 25 matched word for word.** The two misses are honest refusals: in the web version citation markers read "8 , 9 ;" and in the PDF "8,9;", so the quote is not verbatim in that source. In a PDF run the model quotes the PDF itself.

**The gate caught a real slip.** In the Misra extraction, one claim said "this 2025 consensus" but its quote never mentions 2025. The verifier auto-rejected it, and it is listed on the review board.

## Compliance by design

- **CDSCO advisory (10 March 2026):** no drug, brand or dose names and no "ask your doctor for X". Medicine is only ever "one part of doctor-led care", and the CTA is a doctor conversation, not a product.
- **ASCI/Meta health ads:** no promises, timelines or before/after, and no body shaming. Sources and limitations are shown on the post.
- A **source slide** is added to every carousel automatically, and every caption ends with the citation and DOI.

## Smart tech

| Piece | Choice |
|---|---|
| LLM | Gemini 2.5 Flash in JSON mode, temperature 0.2, with retries. The provider is swappable (`--llm gemini|session`). |
| Grounding | Verbatim-quote verification against located source blocks, plus number-level coverage checks. |
| Rendering | Playwright with HTML/CSS templates and ffmpeg. No paid design API, so it is fully brand-controllable. |
| Voice | ElevenLabs (warm Indian female voice), with scene timing driven by the audio. |
| Self-repair | Checker errors are fed back to the model once, automatically. |

**Cost per paper:** two LLM calls of about 15k tokens on Gemini Flash, which is a rupee or two at list price, plus about 45 s of TTS per reel.

## Honest notes

- **How this demo run was produced.** The cloud sandbox I built in could not reach Gemini, ElevenLabs's API or Europe PMC, because of network allow-listing.
  - The three papers' full texts were fetched through a browser and saved in the pipeline's input format.
  - The two LLM steps were answered by Claude through the pipeline's `session` provider, which writes each exact prompt to `prompts/<step>.prompt.md` and reads the JSON answer back.
  - Everything after that ran unchanged: verification, the checker, the repair loop, rendering, the board and export.
  - Switching to Gemini needs only `GEMINI_API_KEY` in `.env` and `--llm gemini`.
- **Reel voiceover.** The Hinglish voiceover was generated with ElevenLabs (Akshara voice, eleven_v4, one take picked from four). The pipeline split it into the 7 scenes by detecting the silences between them, shortened the pauses inside each scene, applied a light pitch-preserving 8% tempo lift for Reels pacing, and normalised it to -14 LUFS. The scenes are timed **to the voice**: every visual change and subtitle chunk lands on its spoken line, and the chart labels appear as the numbers are said. The reel runs 37 s (43 s raw). `reel_en.mp4` is the silent English cut for muted autoplay.
- The ICMR paper is CC BY-NC-SA, so its use here is non-commercial and with attribution.

## Run it (author's machine)

```
python run.py --batch papers/batch.txt --schedule 2026-10-20     # DOI / PDF / doc.json per line
# open outputs/review/index.html → doctor approves → Download approvals.json
python run.py --export approvals.json
```

*Pipeline source is retained by the author. This folder contains watermarked outputs and logs for evaluation only.*
