# StateEye
StateEye, an intelligent web-testing tool inspired by the FRAGGEN approach.
# Project Description:
Web applications are frequently updated with new designs, buttons and features. These updates can unintentionally break existing functions and manually checking everything each time is slow and error-prone.<br>
This project introduces <b>StateEye</b>, an intelligent web-testing tool inspired by the <b>FRAGGEN</b> approach. StateEye automatically analyzes websites after updates to ensure everything still works properly. It explores the website like a real user, interacts with different sections and observes how each part responds. Instead of comparing entire pages, StateEye divides them into smaller sections and checks for meaningful changes more precisely.<br>
A key advantage of StateEye is its ability to identify pages that look almost the same but differ slightly in data or structure. By recognizing these <b>near-duplicate</b> states, it avoids redundant testing and focuses only on meaningful differences, saving both time and effort.<br>
StateEye also generates reusable test cases automatically from its exploration, allowing future updates to be verified quickly and consistently. It intelligently ignores minor layout or color changes while highlighting real functional issues.<br>
To assist manual testers, StateEye includes a browser plugin that marks <b>tested and untested</b> areas and suggests the next steps, making testing faster, smarter and more reliable while helping developers maintain stable, high-quality websites with ease.

## What's included now
- Playwright-based crawler that explores a site, captures DOM + screenshots, and extracts fragments for finer-grained analysis.
- Near-duplicate detection using DOM and perceptual image hashes with configurable thresholds.
- SQLite-backed storage of runs, states, fragments, and pairwise comparisons.
- HTML + JSON reporting per run.
- Auto-generated Playwright regression scripts for the unique states discovered.

## Quick start
1. Create/activate a Python 3 virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Install the Playwright browser binary once: `python -m playwright install chromium`
4. Crawl a site and generate a report:
   - `python -m stateeye.cli crawl --url http://localhost:3000/addressbook/ --max-depth 2 --headless`
   - For pages requiring login, supply pre-actions (fill + click) as JSON:
     ```json
     [
       {"selector": "input[name='user']", "action_type": "fill", "value": "admin"},
       {"selector": "input[name='pass']", "action_type": "fill", "value": "secret"},
       {"selector": "input[type='submit']", "action_type": "click"}
     ]
     ```
     Save as `preactions.json` then run:
     `python -m stateeye.cli crawl --url http://localhost:3000/addressbook/ --max-depth 3 --headless --preactions preactions.json`
     If auto-fill is too aggressive, add `--disable-autofill`.
5. Reports and artifacts are written under `stateeye_runs/<run-name>/`:
   - `report.html` / `report.json` – state classifications with screenshots/fragments.
   - `generated_tests.py` – replayable Playwright script for unique states.
   - `stateeye.db` – SQLite database with states/comparisons.

## Analyze an existing run
If you already have a run folder (for example from earlier Crawljax/FRAGGEN replication), you can regenerate the summary:
```
python -m stateeye.cli analyze --run-dir stateeye_runs/<run-name> --generate-tests
```

## Notes
- The crawler is depth/step bounded (see CLI flags) to keep explorations short. Increase `--max-depth`/`--max-states` for broader coverage.
- Fragment extraction focuses on semantic blocks (`section`, `article`, `form`, buttons, etc.) and crops element-level screenshots to pinpoint visual changes.
- Near-duplicate thresholds are defined in `stateeye/config.py` (`SimilarityConfig`) if you want to tune clone vs. near-duplicate sensitivity.
# Paper
- https://dl.acm.org/doi/10.1145/3377811.3380416
- https://arxiv.org/pdf/2110.14043

