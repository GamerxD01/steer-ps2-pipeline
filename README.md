# PS2 · steerpipe: research paper → doctor-approved Instagram posts

© 2026 Chandra Prakash · evaluation prototype · see `LICENSE.txt`

You give it a DOI or a PDF. It pulls out the findings **word for word** and checks every quote and number against the paper using code. It then writes a carousel, a static or a reel in English and Hinglish. A doctor approves each post, seeing every line next to the exact sentence it came from. Only approved posts are exported.

**▶ Review board (live):** https://gamerxd01.github.io/steer-ps2-pipeline/review-board.html. Type a reviewer name, mark claims ✓/✗, then approve or reject each post.

## Finished posts (`posts/`)
| Format | Paper | Message | Files |
|---|---|---|---|
| **Carousel** | ICMR-INDIAB-23, Indian national survey (IJMR 2025) | 43.3% of Indian adults have a normal BMI but are metabolically unhealthy, so check waist, BP and sugar, not just the scale | `posts/indiab-mono/carousel/` (8 slides, EN + HI) |
| **Static** | Wyatt et al., glucose dips (Nature Metabolism 2021) | The 4 pm hunger can be a sugar dip, not a willpower problem | `posts/wyatt-dips/static/` (feed, square and story, EN + HI) |
| **Reel** | STEP 1 extension, weight after stopping (Diabetes Obes Metab 2022) | Regain is biology, not failure, so plan the exit with a doctor | `posts/step1-ext/reel/reel_hi.mp4` (37 s, Hinglish voiceover and captions) + silent English cut + SRT |
| Bonus carousel (**made from a PDF**) | Misra et al., revised Indian obesity definition (2025) | Look beyond the scale: BMI above 23, waist, and daily-life impact | `posts/misra-definition/carousel/` |

Each post folder has captions in English and Hinglish, hashtags, alt text, and `message.txt` (the message and why it matters to this audience).

## Research / source sheet
- `SOURCES.md` (and `SOURCES.csv`): **every line in every post** mapped to its claim, the verbatim quote, and the location in the paper (paragraph or `page N ¶k`), with the DOI. Every quote was verified by code to exist in the paper.
- `run-log/<paper>/claims.json`: all extracted claims, with population, caveats, limitations and a "do not say" list.

## Workflow / automation (`architecture.png`)
1. **Ingest:** a DOI goes through Europe PMC to structured full text; a PDF goes through a layout-aware reader. Every paragraph gets a location ID.
2. **Extract (AI):** 8–15 claims, each with a verbatim quote, location, population and caveat.
3. **Verify (code):**
   - The quote must exist word for word, and its real location overwrites whatever the AI reported.
   - Every number in a claim must appear in its quote.
   - Failing claims are auto-rejected.
4. **Create (AI):** one message per post, written in English and Hinglish, plus a claim map linking every line to its claims.
5. **Check (code):**
   - Every line cites a verified claim, and no number in the post is missing from the paper.
   - No drug or brand names, promises or shaming language.
   - The source and steerclub.com sign-off are present.
   - A failed check triggers **one automatic repair round**, with the exact errors sent back.
6. **Render:** our own HTML templates. The reel's chart uses the paper's real numbers, and the voiceover is time-synced.
7. **Doctor gate:** the review board. Then **export** of approved posts only, plus a weekly `schedule.csv`.

Batch run: one line per paper (`run-log/demo-batch.txt`). Logs, timings, the repair-round example and test results are all in `run-log/`. Prompt summary: `PROMPTS.md`.

## Estimated human time per paper
**About 10 minutes, all of it doctor review.** That covers skimming about 10 claims beside their quotes and approving the post. There's no writing or design time. Machine time for the 4-paper batch was about 3 minutes, mostly rendering the reel.

## Honest notes
In this sandbox, Gemini, the ElevenLabs API and Europe PMC were blocked by the network. Paper text was fetched through a browser and from the supplied PDFs, and the two AI steps were answered through the pipeline's built-in fallback mode. Everything else ran unchanged: verification, checks, repair loop, rendering, review and export. More detail is in `SUBMISSION.md`.

## Files
`SUBMISSION.md` (full write-up) · `README.md` · `SOURCES.md/.csv` · `architecture.png` · `PROMPTS.md` · `review-board.html` · `posts/` · `run-log/` · `LICENSE.txt`
