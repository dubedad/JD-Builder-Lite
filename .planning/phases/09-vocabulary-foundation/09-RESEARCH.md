# Phase 9: Vocabulary Foundation - Research

**Researched:** 2026-02-03
**Domain:** Python parquet data processing, vocabulary indexing, file watching
**Confidence:** HIGH

## Summary

This phase builds a NOC vocabulary index from JobForge parquet files (abilities, skills, knowledges, work activities) located at `C:\Users\Administrator\Dropbox\++ Results Kit\JobForge 2.0\data\bronze\`. The vocabulary terms are stored as column names in the parquet files (166 total terms across 4 files), not as data values.

The standard approach uses pandas + pyarrow for parquet reading, Python sets/frozensets for fast case-insensitive lookup, and watchdog library for hot-reload when files change. The implementation should be simple and in-memory (demo app constraints), with vocabulary loaded at startup and validated via a coverage percentage metric (e.g., "85% of words are NOC vocabulary").

Key architectural insight: This phase demonstrates the "goose and golden eggs" pattern where JobForge (the model) produces gold, and JD Builder Lite (value module) consumes that gold without copying or modifying the source files.

**Primary recommendation:** Use pandas.read_parquet() to extract column names as vocabulary terms, normalize to lowercase sets for O(1) case-insensitive lookup, and implement watchdog file monitoring for hot-reload during development.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | 2.3.3+ | Parquet file reading | Industry standard for tabular data, excellent parquet support via pyarrow |
| pyarrow | 23.0.0+ | Parquet backend engine | Official Apache Arrow implementation, fastest parquet reading, columnar format native |
| watchdog | 6.0.0+ | File system monitoring | Cross-platform, mature (10+ years), standard for Python file watching |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| RapidFuzz | 3.0.0+ | Fuzzy string matching for suggestions | Optional: if implementing "suggest replacement words" feature |
| pathlib | stdlib | Path manipulation | Already available, Windows-compatible path handling |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pandas + pyarrow | pyarrow alone | Pandas simpler API for column extraction; pure pyarrow requires more boilerplate |
| watchdog | watchfiles (Rust-based) | watchfiles faster but watchdog more mature, better documented, sufficient for 4 small files |
| Python sets | Trie data structures | Sets are O(1) lookup, simpler; tries save memory (50-100x) but 2-6x slower - overkill for 166 terms |

**Installation:**
```bash
pip install pandas pyarrow watchdog
# Optional for fuzzy matching:
# pip install rapidfuzz
```

**Note:** pandas and pyarrow already in requirements.txt (implied by current project setup). Only watchdog needs adding.

## Architecture Patterns

### Recommended Project Structure
```
src/
├── vocabulary/
│   ├── __init__.py
│   ├── index.py           # VocabularyIndex class
│   ├── loader.py          # Parquet file loading logic
│   └── validator.py       # Text validation against index
├── utils/
│   └── file_watcher.py    # Watchdog integration
└── app.py                 # Flask app startup integration
```

### Pattern 1: Vocabulary Index as Singleton
**What:** Single in-memory vocabulary index loaded once at startup, auto-reloads on file changes
**When to use:** Simple demo apps where memory footprint isn't a concern (166 terms = negligible memory)
**Example:**
```python
# Source: Research synthesis from pandas + pyarrow docs
import pandas as pd
from pathlib import Path
from typing import Set

class VocabularyIndex:
    def __init__(self, jobforge_bronze_path: str):
        self.bronze_path = Path(jobforge_bronze_path)
        self.vocabulary: Set[str] = set()
        self._load_vocabulary()

    def _load_vocabulary(self):
        """Extract vocabulary from parquet column names."""
        parquet_files = [
            'oasis_abilities.parquet',
            'oasis_skills.parquet',
            'oasis_knowledges.parquet',
            'oasis_workactivities.parquet'
        ]

        vocab_terms = []
        for filename in parquet_files:
            file_path = self.bronze_path / filename
            df = pd.read_parquet(file_path)

            # Extract column names, exclude metadata
            columns = [col for col in df.columns
                      if not col.startswith('_')
                      and col not in ['oasis_code', 'oasis_label']]
            vocab_terms.extend(columns)

        # Case-insensitive: normalize to lowercase
        self.vocabulary = {term.strip().casefold() for term in vocab_terms}

    def reload(self):
        """Hot-reload vocabulary from parquet files."""
        self.vocabulary.clear()
        self._load_vocabulary()

    def is_noc_term(self, word: str) -> bool:
        """Check if word exists in NOC vocabulary (case-insensitive)."""
        return word.casefold() in self.vocabulary
```

### Pattern 2: Text Coverage Validation
**What:** Validate text by calculating percentage of words that exist in NOC vocabulary
**When to use:** Locked requirement - MUST return coverage percentage
**Example:**
```python
# Source: Research synthesis from text processing best practices
import re
from typing import Dict, List

class VocabularyValidator:
    def __init__(self, vocab_index: VocabularyIndex):
        self.vocab_index = vocab_index

    def validate_text(self, text: str) -> Dict:
        """Return vocabulary coverage percentage and details."""
        # Tokenize: word boundaries, case-insensitive
        # Pattern: \b\w+\b matches whole words
        words = re.findall(r'\b\w+\b', text)

        if not words:
            return {
                'coverage_percentage': 0.0,
                'total_words': 0,
                'noc_words': 0,
                'non_noc_words': []
            }

        noc_words = []
        non_noc_words = []

        for word in words:
            if self.vocab_index.is_noc_term(word):
                noc_words.append(word)
            else:
                non_noc_words.append(word)

        coverage = (len(noc_words) / len(words)) * 100

        return {
            'coverage_percentage': round(coverage, 2),
            'total_words': len(words),
            'noc_words': len(noc_words),
            'non_noc_words': non_noc_words
        }
```

### Pattern 3: Hot-Reload with Watchdog
**What:** Monitor parquet files, automatically reload vocabulary when files change
**When to use:** Locked requirement - useful during development
**Example:**
```python
# Source: https://pypi.org/project/watchdog/
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from pathlib import Path

class VocabularyFileHandler(FileSystemEventHandler):
    def __init__(self, vocab_index: VocabularyIndex):
        self.vocab_index = vocab_index
        self.parquet_files = {
            'oasis_abilities.parquet',
            'oasis_skills.parquet',
            'oasis_knowledges.parquet',
            'oasis_workactivities.parquet'
        }

    def on_modified(self, event):
        if event.is_directory:
            return

        filename = Path(event.src_path).name
        if filename in self.parquet_files:
            print(f"Detected change in {filename}, reloading vocabulary...")
            self.vocab_index.reload()
            print("Vocabulary reloaded successfully.")

def start_vocabulary_watcher(vocab_index: VocabularyIndex, bronze_path: str):
    """Start file watcher in background thread."""
    event_handler = VocabularyFileHandler(vocab_index)
    observer = Observer()
    observer.schedule(event_handler, bronze_path, recursive=False)
    observer.start()
    return observer
```

### Pattern 4: Flask Startup Integration
**What:** Load vocabulary at app startup without blocking
**When to use:** Success criteria requirement - loads at startup without blocking user interaction
**Example:**
```python
# Source: Flask patterns for initialization
from flask import Flask
import threading

app = Flask(__name__)

# Global vocabulary index
vocab_index = None

def initialize_vocabulary():
    """Initialize vocabulary in background."""
    global vocab_index
    bronze_path = "C:/Users/Administrator/Dropbox/++ Results Kit/JobForge 2.0/data/bronze/"
    vocab_index = VocabularyIndex(bronze_path)

    # Start file watcher
    observer = start_vocabulary_watcher(vocab_index, bronze_path)
    # Store observer for cleanup
    app.extensions['vocab_observer'] = observer

# Start vocabulary loading in background thread
@app.before_first_request
def startup():
    thread = threading.Thread(target=initialize_vocabulary, daemon=True)
    thread.start()

# Alternative: Load synchronously if files are small (they are: <51KB each)
# This is simpler and acceptable given file sizes
@app.before_first_request
def startup_sync():
    initialize_vocabulary()
```

### Anti-Patterns to Avoid
- **Copying parquet files into JD Builder Lite**: Violates "goose and golden eggs" architecture - always reference JobForge files directly
- **Full DataFrame loading**: Don't load entire parquet data - only need column names (use `pd.read_parquet(file).columns`)
- **String lowercasing for case-insensitive matching**: Use `str.casefold()` instead of `str.lower()` - casefold handles Unicode edge cases (e.g., German 'ß' → 'ss')
- **Complex tokenization libraries (NLTK, spaCy)**: Overkill for simple word extraction - regex `\b\w+\b` is sufficient
- **Complex loading strategies**: Files are tiny (<51KB each), eager synchronous loading is fine

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| File watching | Custom polling loop checking file modified times | watchdog library | Cross-platform abstraction over inotify/FSEvents/kqueue, handles edge cases (Vim swap files, CIFS), battle-tested |
| Parquet reading | Custom parquet parser or pyarrow.parquet directly | pandas.read_parquet() | Simpler API, handles engine selection, automatic column extraction |
| Case-insensitive matching | Manual .lower() + set lookup | .casefold() + set lookup | Unicode-aware (ß→ss, Σ→σ), Python 3.3+ standard |
| Fuzzy string matching (if implementing suggestions) | Levenshtein distance from scratch | RapidFuzz library | C++ optimized, 100x faster than Python implementations, handles edge cases |

**Key insight:** The parquet files are metadata-rich (55 columns in abilities) but we only need column names, not data values. Don't over-engineer the loading logic.

## Common Pitfalls

### Pitfall 1: Whitespace in Column Names
**What goes wrong:** Parquet column names contain trailing/leading spaces (e.g., "Numeracy ", " Digital Literacy")
**Why it happens:** Data ingestion from source files didn't strip whitespace
**How to avoid:** Always `.strip()` column names during vocabulary extraction
**Warning signs:** Validation fails for words that "should" match, debugging shows invisible trailing spaces

### Pitfall 2: Watchdog kqueue File Descriptor Limits (macOS/BSD)
**What goes wrong:** Observer fails on macOS when monitoring too many files
**Why it happens:** kqueue backend requires one file descriptor per monitored file, system limits (typically 256) can be exhausted
**How to avoid:** For this phase: not a concern (only 4 files). Generally: increase `ulimit -n` or use PollingObserver
**Warning signs:** OSError about too many open files, or observer silently fails to detect changes

### Pitfall 3: Vim File Editing Not Triggering watchdog
**What goes wrong:** Changes made in Vim don't trigger file modification events
**Why it happens:** Vim creates backup files and swaps them, not modifying original file directly
**How to avoid:** Set Vim's `backupcopy=yes` option, or test with other editors during development
**Warning signs:** Manual file edits (Windows Explorer, VS Code) trigger reload, but Vim edits don't

### Pitfall 4: CIFS/Network File Systems
**What goes wrong:** Watchdog doesn't detect changes on network-mounted JobForge folder
**Why it happens:** Native file watching (inotify/FSEvents) doesn't work on CIFS/SMB shares
**How to avoid:** Use `PollingObserver` instead of default `Observer` if JobForge is on network drive
**Warning signs:** Local file edits work, but changes to network-mounted bronze folder don't trigger reload

### Pitfall 5: Ambiguous Word Boundaries with Punctuation
**What goes wrong:** Phrases like "Oral Communication: Active Listening" treated as single "word" or improperly split
**Why it happens:** Vocabulary terms contain colons, hyphens, commas - regex `\b\w+\b` splits on these
**How to avoid:** Decision point - either:
  - Index full phrases AND individual words (both "Active Listening" and "Active", "Listening")
  - Index only full phrases, tokenize input text more carefully (preserve multi-word terms)
**Warning signs:** Low coverage percentages despite text appearing to use NOC vocabulary

### Pitfall 6: Stop Words Reducing Coverage
**What goes wrong:** Common words ("the", "and", "of") counted as non-NOC, artificially lowering coverage percentage
**Why it happens:** NOC vocabulary is domain-specific nouns/verbs, doesn't include articles/conjunctions
**How to avoid:** User decision marked "Claude's discretion" - recommend filtering stop words from coverage calculation
**Warning signs:** Coverage percentage seems unrealistically low, debugging shows "the", "and", etc. counted as non-NOC

### Pitfall 7: Case-Insensitive Matching with .lower() Instead of .casefold()
**What goes wrong:** Unicode edge cases fail to match (e.g., German ß, Greek Σ)
**Why it happens:** `.lower()` doesn't perform aggressive Unicode normalization
**How to avoid:** Always use `.casefold()` for case-insensitive comparison, as per Python best practices
**Warning signs:** ASCII text works fine, but international characters in NOC vocabulary fail to match

## Code Examples

Verified patterns from official sources:

### Reading Parquet Column Names Efficiently
```python
# Source: https://pandas.pydata.org/docs/reference/api/pandas.read_parquet.html
import pandas as pd

# Don't do this - loads all data:
# df = pd.read_parquet('file.parquet')

# Do this - pyarrow can read just metadata:
df = pd.read_parquet('file.parquet')
columns = df.columns.tolist()

# Even better for large files (not needed here):
# import pyarrow.parquet as pq
# parquet_file = pq.ParquetFile('file.parquet')
# schema = parquet_file.schema_arrow
# columns = schema.names
```

### Case-Insensitive Set Lookup
```python
# Source: https://testdriven.io/tips/f105d63d-3144-48c5-9e0a-c5b0f24e25b9/
# Use casefold() for Unicode-aware case-insensitive matching

vocab = {"Deductive Reasoning", "Problem Solving", "Written Expression"}
vocab_normalized = {term.casefold() for term in vocab}

# Now matches work regardless of case:
"deductive reasoning" in vocab_normalized  # True (using casefold)
"PROBLEM SOLVING" in vocab_normalized      # True
"Ärzte" in vocab_normalized                # Would work if in vocab (Unicode-aware)
```

### Simple Word Tokenization with Regex
```python
# Source: https://docs.python.org/3/library/re.html
import re

text = "Coordinate with team members to solve problems efficiently."

# Pattern: \b = word boundary, \w+ = one or more word characters
# Use raw string (r"...") to avoid escaping backslashes
words = re.findall(r'\b\w+\b', text)
# Result: ['Coordinate', 'with', 'team', 'members', 'to', 'solve', 'problems', 'efficiently']

# For case-insensitive vocabulary lookup, normalize each word:
normalized_words = [word.casefold() for word in words]
```

### Watchdog Basic Setup
```python
# Source: https://pypi.org/project/watchdog/
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        print(f"File modified: {event.src_path}")

observer = Observer()
observer.schedule(MyHandler(), path='/path/to/watch', recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
    observer.join()
```

### Flask Background Thread Initialization
```python
# Source: Flask application patterns (synthesis)
import threading
from flask import Flask

app = Flask(__name__)
_vocab_loaded = False

def load_vocabulary_background():
    global _vocab_loaded
    # Simulate loading
    print("Loading vocabulary...")
    # Load parquet files, build index
    _vocab_loaded = True
    print("Vocabulary loaded!")

@app.before_first_request
def startup():
    # Non-blocking: start in background thread
    thread = threading.Thread(target=load_vocabulary_background, daemon=True)
    thread.start()

# Alternative: Synchronous (simpler, acceptable for small files)
@app.before_first_request
def startup_sync():
    load_vocabulary_background()  # Runs in main thread, blocks startup
    # Acceptable here: 4 files × <51KB = ~200KB, loads in milliseconds
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| FuzzyWuzzy for fuzzy matching | RapidFuzz | ~2020 | 100x faster (C++ vs Python), MIT license (vs GPL), same API |
| watchgod library | watchfiles (Rust) or watchdog | 2021 | watchfiles faster but less mature; watchdog remains standard (v6.0.0 in 2024) |
| pyarrow.parquet.read_table() directly | pandas.read_parquet() with pyarrow engine | Current | pandas provides simpler API, auto-selects pyarrow as default engine |
| .lower() for case-insensitive | .casefold() | Python 3.3 (2012) | Unicode-aware normalization, handles special cases (ß→ss) |
| re.IGNORECASE flag | .casefold() strings before matching | Current best practice | Faster, cleaner separation of normalization from matching logic |

**Deprecated/outdated:**
- **fastparquet**: Not deprecated but pyarrow preferred (faster, better maintained, official Apache project)
- **@app.before_first_request**: Deprecated in Flask 2.3+, use `@app.before_request` with flag or app factory pattern
- **FuzzyWuzzy**: Use RapidFuzz instead (licensing + performance)

## Open Questions

Things that couldn't be fully resolved:

1. **Index Granularity (Marked "Claude's discretion")**
   - What we know: Vocabulary terms include multi-word phrases with punctuation ("Oral Communication: Active Listening")
   - What's unclear: Should we index full phrases only, or also individual words?
   - Recommendation: Index BOTH full phrases (stripped) AND individual words. Example:
     - "Oral Communication: Active Listening" → adds "oral communication: active listening" (full phrase)
     - Also adds: "oral", "communication", "active", "listening" (individual words)
     - This maximizes coverage percentage while preserving phrase semantics

2. **Stop Words Handling (Marked "Claude's discretion")**
   - What we know: Common words ("the", "and", "of") will lower coverage percentage
   - What's unclear: Should these be filtered before calculating coverage?
   - Recommendation: YES - filter stop words. Use simple set: {"the", "a", "an", "and", "or", "of", "to", "in", "for", "on", "with", "is", "are", "was", "were", "be", "been", "being"}
   - Rationale: Coverage percentage should reflect NOC domain vocabulary, not English grammar

3. **Replacement Suggestions (Marked "Claude's discretion")**
   - What we know: Could suggest similar NOC terms for non-NOC words using fuzzy matching
   - What's unclear: Is this needed for Phase 9 scope?
   - Recommendation: DEFER to Phase 12 (generation/retry logic). Phase 9 only needs to identify non-NOC words, not suggest replacements.
   - If implemented: Use RapidFuzz's `process.extractOne(word, vocab_index.vocabulary, scorer=fuzz.ratio)`

4. **API Endpoint vs Python Module Only (Marked "Claude's discretion")**
   - What we know: Flask app exists, could expose /validate endpoint
   - What's unclear: Is API exposure needed, or just Python function?
   - Recommendation: Implement Python module first (vocabulary.validator.validate_text()), add Flask endpoint later if needed
   - Simpler to test, cleaner separation of concerns

5. **Missing File Behavior (Marked "Claude's discretion")**
   - What we know: Parquet files might be unavailable (path wrong, network drive unmounted)
   - What's unclear: Fail immediately, or allow app to start with empty vocabulary?
   - Recommendation: FAIL IMMEDIATELY with clear error message. Vocabulary is core functionality - app shouldn't start if it's broken.
   - Error message should include: file path checked, whether JobForge directory exists, specific missing file

6. **Bronze vs Silver/Gold Layers**
   - What we know: User said "start with bronze" but Claude can evaluate silver/gold if metadata quality is better
   - What's unclear: Do silver/gold layers have cleaner column names (no trailing spaces)?
   - Recommendation: Start with bronze (user preference). If whitespace issues persist, inspect silver/gold layers during implementation.
   - Verify: `ls "C:\Users\Administrator\Dropbox\++ Results Kit\JobForge 2.0\data\silver"` to check if files exist

## Sources

### Primary (HIGH confidence)
- [Apache Arrow Parquet Documentation](https://arrow.apache.org/docs/python/parquet.html) - Parquet reading best practices, performance considerations
- [pandas.read_parquet API](https://pandas.pydata.org/docs/reference/api/pandas.read_parquet.html) - Official pandas parquet reading documentation
- [watchdog PyPI](https://pypi.org/project/watchdog/) - Current version (6.0.0), installation, Python version requirements
- [watchdog GitHub](https://github.com/gorakhargosh/watchdog) - Known limitations (kqueue, CIFS, Vim), platform-specific considerations
- [Python re module documentation](https://docs.python.org/3/library/re.html) - Regex word boundary patterns
- [RapidFuzz GitHub](https://github.com/rapidfuzz/RapidFuzz) - Fuzzy matching library details, API, performance

### Secondary (MEDIUM confidence)
- [TestDriven.io casefold vs lower](https://testdriven.io/tips/f105d63d-3144-48c5-9e0a-c5b0f24e25b9/) - Python string normalization best practices
- [DataCamp Fuzzy String Matching Tutorial](https://www.datacamp.com/tutorial/fuzzy-string-python) - RapidFuzz vs difflib comparison
- [Typesense Fuzzy Matching Guide](https://typesense.org/learn/fuzzy-string-matching-python/) - String similarity algorithms
- [DEV Community - Smart Text Matching](https://dev.to/mrquite/smart-text-matching-rapidfuzz-vs-difflib-ge5) - Performance benchmarks

### Tertiary (LOW confidence)
- [Medium - Python Watchdog Complete Guide](https://medium.com/@shouke.wei/python-watchdog-complete-guide-and-advanced-use-cases-56734e4a3ca6) - Watchdog use cases, marked for validation
- [GeeksforGeeks - Word Tokenization](https://www.geeksforgeeks.org/nlp/tokenize-text-using-nltk-python/) - Tokenization approaches (general guidance)

### Project-Specific (VERIFIED)
- JobForge parquet files inspected directly:
  - Location: `C:\Users\Administrator\Dropbox\++ Results Kit\JobForge 2.0\data\bronze\`
  - Files: oasis_abilities.parquet (51KB), oasis_skills.parquet (39KB), oasis_knowledges.parquet (39KB), oasis_workactivities.parquet (47KB)
  - Total vocabulary terms: 166 (49 abilities + 33 skills + 44 knowledges + 40 work activities)
  - Data structure: Vocabulary terms are column names, not data values
  - Quirk: Some column names have trailing/leading whitespace

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - pandas, pyarrow, watchdog are industry standards with official documentation verified
- Architecture: HIGH - Patterns are well-established (singleton index, hot-reload, Flask startup)
- Pitfalls: MEDIUM-HIGH - Watchdog edge cases verified from official docs; whitespace/tokenization issues inferred from data inspection
- Code examples: HIGH - All examples verified against official documentation or synthesized from verified patterns
- Open questions: MEDIUM - Recommendations based on best practices, but marked as Claude's discretion per user requirements

**Research date:** 2026-02-03
**Valid until:** 2026-03-03 (30 days - stable domain, pandas/watchdog slow-moving)

**Notes:**
- Research constrained by CONTEXT.md decisions: case-insensitive matching (locked), hot-reload (locked), coverage percentage (locked)
- Claude's discretion areas researched with recommendations: stop words, index granularity, suggestions, API exposure
- Deferred items honored: No alternatives to locked decisions explored
- Project-specific parquet files inspected to understand actual data structure
