"""Semantic similarity matcher.

PRIMARY IMPLEMENTATION: sentence-transformers (all-MiniLM-L6-v2)
FALLBACK IMPLEMENTATION: Stemmed TF-IDF cosine similarity (numpy only)

The primary implementation uses a 384-dimensional neural embedding model and
computes cosine similarity in embedding space — capturing semantic meaning even
when vocabulary differs (e.g. "software engineer" matches "IT systems developer").

The TF-IDF fallback is a pure bag-of-words approach with prefix stemming. It
works only on lexical overlap after reducing words to their first 5 characters.
It does NOT capture synonyms, paraphrasing, or cross-vocabulary similarity.

--- ACCURACY IMPACT OF TF-IDF FALLBACK ---

Why this fallback was introduced (2025-03-05):
  PyTorch has no binary wheels for Python 3.14+ as of this date. sentence-transformers
  requires torch, so it cannot be installed on Python 3.14. The fallback keeps the
  classification pipeline functional but with reduced shortlisting quality.

Known accuracy risks with TF-IDF fallback:
  1. VOCABULARY MISMATCH: JD language ("manages staff") may not overlap with
     TBS definition language ("involves the supervision of employees"). These are
     semantically equivalent but lexically distinct — neural embeddings handle this;
     TF-IDF does NOT.

  2. SHORTLISTING GAPS: Groups that rely on semantic understanding to be selected
     as candidates may be missed entirely, meaning the LLM never considers them.
     Missed candidates cannot be recovered downstream.

  3. COMPENSATING MECHANISMS (partially mitigate the above):
     a. `keyword_boost` in shortlisting/__init__.py adds 0.15 to groups whose
        TITLE_KEYWORD_GROUPS keywords appear in the JD text, allowing obvious
        title-based matches to pass the similarity threshold even when TF-IDF is 0.
     b. `labels_boost` adds 0.0–0.1 for groups whose labels.csv entries match
        words in the JD, providing a secondary lexical signal.
     c. `keyword_boost > 0` was added as an ADDITIONAL filter condition so that
        keyword-matched groups are never blocked from the shortlist even with
        TF-IDF score of 0. (See shortlisting/__init__.py, change 2025-03-05.)

  4. SCORE SCALE DIFFERENCE: TF-IDF cosine scores are typically LOWER than neural
     similarity scores for the same text pairs. The `min_similarity` thresholds
     (0.2 in allocator.py, 0.3 in shortlist_by_definition) were calibrated for
     neural embeddings and may be too aggressive when TF-IDF is in use.

  5. 5-CHAR PREFIX STEMMING COLLISIONS: "devel*" merges "develop/developer/
     development/developing" — good. But it also merges unrelated words that share
     a prefix (e.g. "polic*" for both "policy" and "police"). Impact is small at
     the corpus level but possible.

How to re-enable neural embeddings when PyTorch supports Python 3.14+:
  pip install sentence-transformers
  (No code changes needed — the try/except auto-selects the better implementation.)

How to assess accuracy impact:
  See .planning/accuracy-notes/tfidf-fallback-2025-03-05.md for a structured
  evaluation checklist and test cases to run once PyTorch 3.14 support arrives.

Per RESEARCH.md: all-MiniLM-L6-v2 selected for balanced speed/quality.
"""

from typing import List, Dict
import re
import math

try:
    from sentence_transformers import SentenceTransformer
    from sentence_transformers.util import cos_sim
    HAS_SENTENCE_TRANSFORMERS = True
except (ImportError, RuntimeError):
    HAS_SENTENCE_TRANSFORMERS = False
    SentenceTransformer = None
    cos_sim = None


_STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'of', 'in', 'to', 'for', 'is', 'are',
    'that', 'this', 'with', 'on', 'at', 'by', 'from', 'as', 'be', 'it',
    'its', 'not', 'but', 'can', 'may', 'will', 'has', 'have', 'had',
    'their', 'they', 'such', 'other', 'which', 'who', 'these', 'those',
}


def _stem(word: str) -> str:
    """Lightweight prefix stem: truncate to first 5 chars for words >= 5 chars.

    Merges common morphological variants that share a root:
      'development', 'developer', 'developing', 'develops' → 'devel'
      'management', 'manages', 'manager'                   → 'manag'
      'analysis', 'analyst', 'analyze'                     → 'analy'
      'administrative', 'administration'                   → 'admin'

    Known limitation: merges unrelated words with the same 5-char prefix.
    Example: 'polic*' captures both 'policy' and 'police'. This is rare in
    the occupational group domain but not impossible.
    """
    return word[:5] if len(word) >= 5 else word


def _tokenize(text: str) -> List[str]:
    """Extract alpha tokens of length >= 3, remove stopwords, apply prefix stem.

    The minimum length of 3 filters out articles, pronouns, and noise words
    that are not in the stopwords set. Stopwords are removed before stemming
    to avoid wasting vocabulary slots on common function words.
    """
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    return [_stem(w) for w in words if w not in _STOPWORDS]


def _tfidf_cosine(text_a: str, text_b: str) -> float:
    """Cosine similarity over stemmed log-TF bag-of-words vectors.

    Formula:
      TF(t, d) = 1 + log(count(t, d))  if count > 0, else 0
      similarity = dot(va, vb) / (||va|| * ||vb||)

    No IDF term is used because the corpus is small (one pair at a time) and
    IDF would require pre-computing across all group definitions. Log-TF alone
    provides reasonable term weighting without IDF.

    Score interpretation (approximate, not calibrated):
      > 0.20 : good lexical overlap — likely related domain
      0.10-0.20 : moderate overlap — possibly related
      0.05-0.10 : sparse overlap — weak signal
      < 0.05 : near-zero overlap — probably unrelated or vocabulary mismatch

    IMPORTANT: These thresholds are LOWER than typical neural cosine scores
    for equivalent text pairs. The `min_similarity` parameters in the pipeline
    were calibrated for neural embeddings (typically 0.2–0.4 meaningful range).
    Under TF-IDF, the effective meaningful range shifts to roughly 0.05–0.20.
    This means some genuinely relevant groups may fall below the threshold and
    be missed from the shortlist. The keyword_boost safety net partially
    compensates for the most common cases. See module docstring for full analysis.
    """
    tokens_a = _tokenize(text_a)
    tokens_b = _tokenize(text_b)

    if not tokens_a or not tokens_b:
        return 0.0

    # Build shared vocabulary from both texts
    vocab = list(set(tokens_a) | set(tokens_b))
    vocab_index = {w: i for i, w in enumerate(vocab)}

    def tf_vec(tokens):
        vec = [0.0] * len(vocab)
        count = {}
        for t in tokens:
            count[t] = count.get(t, 0) + 1
        for word, freq in count.items():
            if word in vocab_index:
                vec[vocab_index[word]] = 1 + math.log(freq)
        return vec

    va = tf_vec(tokens_a)
    vb = tf_vec(tokens_b)

    dot = sum(a * b for a, b in zip(va, vb))
    norm_a = math.sqrt(sum(x * x for x in va))
    norm_b = math.sqrt(sum(x * x for x in vb))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


class SemanticMatcher:
    """Calculate semantic similarity between JD text and occupational group definitions.

    Selects the best available implementation at construction time:
      - If sentence-transformers + torch are available: uses all-MiniLM-L6-v2
        (neural, 384-dim, captures semantic meaning across vocabulary)
      - Otherwise: uses _tfidf_cosine() fallback (lexical, stems only)

    Callers can check `matcher._use_neural` to know which backend is active.
    The API (compute_similarity, shortlist_by_definition) is identical either way.
    """

    def __init__(self):
        """Initialize with sentence-transformers if available, otherwise TF-IDF fallback."""
        self._model = None
        self._use_neural = False
        self._definition_cache = {}

        if HAS_SENTENCE_TRANSFORMERS:
            try:
                self._model = SentenceTransformer('all-MiniLM-L6-v2')
                self._use_neural = True
            except Exception:
                pass  # Model download failed or other init error — fall through to TF-IDF

        if not self._use_neural:
            import sys
            print(
                "[SemanticMatcher] ACCURACY WARNING: sentence-transformers unavailable "
                "(torch not supported on Python 3.14+). "
                "Using TF-IDF cosine similarity fallback. "
                "Shortlisting accuracy is reduced — some occupational groups may be "
                "incorrectly excluded as candidates before LLM classification. "
                "See src/matching/shortlisting/semantic_matcher.py module docstring "
                "and .planning/accuracy-notes/tfidf-fallback-2025-03-05.md for details.",
                file=sys.stderr
            )

    def compute_similarity(self, jd_text: str, definition: str) -> float:
        """Calculate similarity between JD text and a group definition.

        Returns a score in [0.0, 1.0]. Score meaning differs by backend:
          Neural:  cosine similarity of 384-dim sentence embeddings
                   (captures semantic meaning; 0.3+ is a meaningful match)
          TF-IDF:  cosine similarity of stemmed log-TF vectors
                   (captures lexical overlap only; 0.1+ may be meaningful;
                    see _tfidf_cosine docstring for score interpretation)

        Args:
            jd_text: Combined Client-Service Results + Key Activities text
            definition: Occupational group definition text from TBS

        Returns:
            Cosine similarity score between 0.0 and 1.0
        """
        if not jd_text or not definition:
            return 0.0

        if self._use_neural:
            jd_embedding = self._model.encode(jd_text, convert_to_tensor=True)
            if definition not in self._definition_cache:
                self._definition_cache[definition] = self._model.encode(
                    definition, convert_to_tensor=True
                )
            definition_embedding = self._definition_cache[definition]
            similarity = cos_sim(jd_embedding, definition_embedding)
            return float(similarity.item())
        else:
            return _tfidf_cosine(jd_text, definition)

    def shortlist_by_definition(
        self,
        jd_text: str,
        groups: List[Dict],
        min_similarity: float = 0.3
    ) -> List[Dict]:
        """Return groups with semantic similarity >= threshold, sorted descending.

        NOTE ON THRESHOLD CALIBRATION:
          The default min_similarity=0.3 was calibrated for neural embeddings.
          Under TF-IDF fallback, meaningful similarity scores are typically in
          the 0.05–0.20 range, so a threshold of 0.3 would exclude most groups.
          In practice, shortlist_with_all_signals (in __init__.py) calls this
          with min_similarity=0.2 and adds a keyword_boost safety net to ensure
          groups are not wrongly excluded. This method's direct callers should
          be aware that threshold calibration is backend-dependent.

        Args:
            jd_text: Combined Client-Service Results + Key Activities text
            groups: List of group dicts with 'definition' key
            min_similarity: Threshold — calibrated for neural backend (0.3 default)

        Returns:
            List of dicts: {'group': ..., 'semantic_similarity': float}
            Sorted by semantic_similarity descending
        """
        candidates = []

        for group in groups:
            definition = group.get('definition', '')
            if not definition:
                continue

            similarity = self.compute_similarity(jd_text, definition)

            if similarity >= min_similarity:
                candidates.append({
                    'group': group,
                    'semantic_similarity': similarity
                })

        candidates.sort(key=lambda x: x['semantic_similarity'], reverse=True)
        return candidates


def shortlist_candidates(
    jd_text: str,
    groups: List[Dict],
    min_similarity: float = 0.3,
    max_candidates: int = 10
) -> List[Dict]:
    """Convenience wrapper: shortlist top candidates by semantic similarity.

    Args:
        jd_text: Combined Client-Service Results + Key Activities text
        groups: List of group dicts with 'definition' key
        min_similarity: Threshold (default 0.3 — calibrated for neural backend)
        max_candidates: Max candidates to return (default 10)

    Returns:
        List of dicts: {'group': ..., 'semantic_similarity': float}
        Sorted by semantic_similarity desc, limited to max_candidates
    """
    matcher = SemanticMatcher()
    candidates = matcher.shortlist_by_definition(jd_text, groups, min_similarity)
    return candidates[:max_candidates]


__all__ = ['SemanticMatcher', 'shortlist_candidates']
