# Git Rescue & Collaboration Instructions

## Context

Rob pushed 35 commits directly to `origin/master`. Those commits contain the DND Careers Site
work and a merge of Vic's JD Builder. Vic's local `master` is his JD Builder codebase — a
completely separate git history (no shared ancestor).

The goals:
1. Save Rob's work permanently on a branch (`rob/careers-site`)
2. Restore `origin/master` to Vic's JD Builder state
3. Make `master` the default branch on GitHub and delete the empty `main` branch
4. Establish a clean collaboration workflow going forward

---

## Step 1 — Rob saves his work (Rob does this first)

Run these commands **on Rob's machine** from the project root:

```bash
# Create a branch to save all of Rob's current work
git checkout -b rob/careers-site

# Push that branch to GitHub — Rob's work is now permanently saved
git push origin rob/careers-site

# Confirm the branch is on GitHub
git branch -r | grep rob
```

You should see `origin/rob/careers-site` in the output.

**Rob's work is now safe. Tell Vic when this is done before proceeding.**

---

## Step 2 — Vic restores master and fixes the default branch (Vic does this after Step 1)

Run these commands **on Vic's machine** from the project root:

```bash
# Force push Vic's local master to origin/master
# This replaces Rob's history with Vic's JD Builder (v5.1, Phase 31 complete)
git push origin master --force

# Confirm origin/master now shows Vic's last commit
git log origin/master --oneline | head -3
```

The top commit should be Vic's JD Builder work, not Rob's careers site commits.

Then, change the default branch from `main` to `master` and delete `main`:

```bash
# Set master as the default branch on GitHub
gh repo edit --default-branch master

# Delete the empty main branch (was default but contained almost nothing)
git push origin --delete main

# Confirm main is gone
git branch -r
```

You should see `origin/master` but no `origin/main`.

---

## After Both Steps Are Done

The repo will be in this clean state:

| Branch | Contains |
|--------|----------|
| `origin/master` | Vic's JD Builder (v5.1, Phase 31 complete) — **default branch** |
| `origin/rob/careers-site` | Rob's DND Careers Site + merge attempt (all 35 commits, safe archive) |
| `origin/vic/jd-builder-lite-work` | Vic's working branch (identical to master) |

---

## Step 3 — Rob sets up his local environment for collaboration

**Important:** `rob/careers-site` and `master` have completely separate git histories. GitHub
will block a pull request between them ("unrelated histories"). Rob cannot simply PR
`rob/careers-site` into `master`.

To work together properly going forward, Rob needs to start from Vic's master:

```bash
# Pull down the updated master (Vic's JD Builder)
git fetch origin

# Create a fresh integration branch from Vic's master
git checkout -b rob/careers-integration origin/master

# Confirm the branch is based on Vic's master
git log --oneline | head -3
```

Rob then ports his careers site code into this new branch by copying files
(not merging git history).

### Files to copy wholesale from `rob/careers-site`

These are entirely new files that don't exist in Vic's master — just copy them in:

| File/Folder | What it is |
|-------------|------------|
| `src/routes/careers.py` | Flask Blueprint for all `/careers/*` routes |
| `src/services/careers_parquet_reader.py` | Reads `job_architecture.parquet` + `bridge_caf_ja.parquet` |
| `templates/careers/` | All 4 careers templates (base, careers, family, career_detail) |
| `templates/landing.html` | The `/` routing gate between JD Builder and Careers Site |
| `static/images/careers/` | All career site images (webp, png, jpg) |
| `ps_careers_site/` | Original standalone FastAPI version — reference only, keep for context |

### Changes to make manually in `src/app.py`

**Do NOT copy Rob's entire `app.py` over Vic's.** Instead make these 4 targeted edits to
Vic's `src/app.py`:

**1. Add the careers Blueprint import** (after the existing api_bp import):
```python
from src.routes.careers import careers_bp
```

**2. Wrap `initialize_vocabulary()` in a try/except** so the app still starts even if
parquet files are unavailable:
```python
def initialize_vocabulary():
    global vocab_index, vocab_observer, generation_service
    try:
        vocab_index = VocabularyIndex(JOBFORGE_BRONZE_PATH)
        vocab_observer = start_vocabulary_watcher(vocab_index, JOBFORGE_BRONZE_PATH)
        print(f"[Vocabulary] Loaded: {vocab_index.get_term_count()} terms")
        generation_service = get_generation_service(vocab_index)
        print("[Generation] Service initialized (lazy loading enabled)")
    except FileNotFoundError as e:
        print(f"[Vocabulary] WARNING: {e}")
        print("[Vocabulary] JD Builder search features unavailable — careers site will still work.")
```

**3. Register the careers Blueprint** (after `app.register_blueprint(api_bp)`):
```python
app.register_blueprint(careers_bp)
```

**4. Change the `/` route to serve the landing page, and move JD Builder to `/builder/`**:
```python
# Replace this:
@app.route('/')
def index():
    return render_template('index.html')

# With this:
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/builder/')
def index():
    return render_template('index.html')
```

### Fix the `/careers/` 500 error

Rob left a known bug: the `/careers/` route returns a 500 error with no visible traceback.
This must be fixed in `rob/careers-integration` before submitting a PR.

To debug it, run the app in debug mode and visit `/careers/`:
```bash
python -m flask --app src/app.py run --debug
```

The Werkzeug debugger should show the full traceback in the browser. The most likely cause
is a `pandas` or `pyarrow` error when loading `job_architecture.parquet` at render time.
Check `src/services/careers_parquet_reader.py` and verify `JOBFORGE_GOLD_PATH` is set
correctly in `.env`.

### Commit and push

Once files are copied, app.py is updated, and the 500 bug is fixed:

```bash
git add src/routes/careers.py src/services/careers_parquet_reader.py
git add templates/careers/ templates/landing.html
git add static/images/careers/
git add ps_careers_site/
git add src/app.py
git commit -m "feat(careers): integrate DND Careers Site as Flask Blueprint"
git push origin rob/careers-integration
```

Then open a pull request from `rob/careers-integration` → `master` on GitHub.
This will work as a normal PR because both branches now share the same base history.

---

## Going Forward — Collaboration Rules

| Rule | Detail |
|------|--------|
| Never push to `master` directly | All changes via pull request |
| Rob's working branch | `rob/careers-integration` (based on Vic's master) |
| Vic's working branch | local `master`, pushed to `vic/jd-builder-lite-work` |
| `rob/careers-site` | Archive only — do not develop on it |
| PRs reviewed before merge | Vic reviews Rob's PRs; Rob reviews Vic's if needed |

---

## If Something Goes Wrong

Rob's work is safe on `rob/careers-site` as long as Step 1 completed successfully.
To verify Rob's branch is intact at any time:

```bash
git log origin/rob/careers-site --oneline | head -5
```

The most recent commit should be `8037c28 docs: update handoff with full session state and unresolved bug`.

To restore `origin/master` back to Rob's state (full rollback):

```bash
git push origin rob/careers-site:master --force
```
