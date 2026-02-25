# StateEye

Web applications are frequently updated with new designs, buttons and features. These updates can unintentionally break existing functions and manually checking everything each time is slow and error-prone.
This project introduces StateEye, an intelligent web-testing tool inspired by the FRAGGEN approach. StateEye automatically analyzes websites after updates to ensure everything still works properly. It explores the website like a real user, interacts with different sections and observes how each part responds. Instead of comparing entire pages, StateEye divides them into smaller sections and checks for meaningful changes more precisely.
A key advantage of StateEye is its ability to identify pages that look almost the same but differ slightly in data or structure. By recognizing these near-duplicate states, it avoids redundant testing and focuses only on meaningful differences, saving both time and effort.
StateEye also generates reusable test cases automatically from its exploration, allowing future updates to be verified quickly and consistently. It intelligently ignores minor layout or color changes while highlighting real functional issues.
To assist manual testers, StateEye includes a browser plugin that marks tested and untested areas and suggests the next steps, making testing faster, smarter and more reliable while helping developers maintain stable, high-quality websites with ease.

---

## Features

- **Fragment-based comparison** — compares states, not whole pages
- **Clone skipping** — identical fragments across pages are tested only once
- **Near-duplicate detection** — highlights data-fluid regions where content varies but structure stays the same
- **Automated mode** — crawls websites with a real browser , extracts states, classifies them, and generates tests
- **Manual mode** — tracks which elements a tester has clicked and shows untested/tested coverage live
- **Test generation** — Generate test cases
- **SQLite storage** — all crawl data persisted for re-analysis

---

## Installation

### Prerequisites
- Python 3.11+
- pip

### Steps

```bash
# 1. Clone the repository
git clone <repo-url>
cd StateEye

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install the Playwright browser binary (one-time)
python -m playwright install chromium
```

---

## How to Use — GUI

StateEye provides a desktop GUI for both automated and manual testing.

### Launch the GUI

```bash
python pythonCode/stateeye_gui.py
```

This opens the StateEye window with the following controls:

| Control | Description |
|---------|-------------|
| **Target** | Enter a website URL (e.g. `http://localhost:8080`) or a local HTML file/folder path |
| **Mode** | Choose **Automated** or **Manual** |
| **Runtime (min)** | Time limit for automated crawling (default: 1 minute) |
| **Max depth** | How many link levels deep to crawl (default: 5) |
| **Max states** | Maximum number of pages to visit (default: 50) |
| **Credentials file** | Optional — path to a credentials file for sites with login forms |
| **Start** | Begin crawling (automated) or launch browser (manual) |
| **Stop** | Abort the current session |
| **Generate Tests** | Generate test artifacts from the completed session |

---

## References

- FRAGGEN paper: https://dl.acm.org/doi/10.1145/3377811.3380416
- Extended version: https://arxiv.org/pdf/2110.14043

