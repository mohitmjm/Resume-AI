"""
Extractive summariser — selects the most important sentences from the resume
to produce a summary that is approximately `pct`% of the original text length.

Algorithm:
  1. Split text into sentences
  2. Remove boilerplate / very short sentences
  3. Score each sentence using TF-IDF-like word frequency (stopwords removed)
  4. Boost sentences near the top (name/objective sections score higher)
  5. Select top-N sentences, where N = ceil(total * pct / 100)
  6. Return selected sentences in their original document order
"""
import re
import math
from collections import Counter


# ------------------------------------------------------------------
# Stop words (lightweight, no spaCy dependency needed here)
# ------------------------------------------------------------------
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to",
    "for", "of", "with", "by", "from", "is", "are", "was", "were",
    "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "shall",
    "i", "me", "my", "we", "our", "you", "your", "he", "she", "it",
    "they", "their", "this", "that", "these", "those", "as", "also",
    "not", "no", "so", "than", "then", "when", "where", "which",
    "who", "whom", "what", "how", "its", "s", "am",
}


def _tokenise(text: str) -> list[str]:
    return [
        w.lower() for w in re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.]*\b", text)
        if w.lower() not in STOP_WORDS and len(w) > 1
    ]


def _split_sentences(text: str) -> list[str]:
    """Split into sentences; keep only non-trivial ones."""
    # Normalise whitespace / line breaks
    text = re.sub(r"\n{2,}", ". ", text)
    text = re.sub(r"\n", " ", text)
    # Split on . ! ?
    raw = re.split(r"(?<=[.!?])\s+", text)
    sentences = []
    for s in raw:
        s = s.strip()
        word_count = len(s.split())
        # Drop very short sentences (likely headings/labels) and very long ones
        if 5 <= word_count <= 60:
            sentences.append(s)
    return sentences


def _word_freq(text: str) -> dict[str, float]:
    """TF (term frequency) of content words in full text."""
    tokens = _tokenise(text)
    if not tokens:
        return {}
    counts = Counter(tokens)
    max_freq = max(counts.values())
    return {w: c / max_freq for w, c in counts.items()}


def _score_sentence(sentence: str, word_freq: dict, position: int, total: int) -> float:
    """Score a sentence by content-word frequency + positional boost."""
    tokens = _tokenise(sentence)
    if not tokens:
        return 0.0

    # Average frequency of content words
    freq_score = sum(word_freq.get(t, 0) for t in tokens) / len(tokens)

    # Positional boost: sentences in the first 20% of the doc score +15%
    pos_boost = 0.15 if position / max(total, 1) < 0.2 else 0.0

    return freq_score + pos_boost


def extractive_summary(text: str, pct: int = 30) -> str:
    """
    Return a summary containing approximately `pct`% of the
    original sentence count (minimum 1, maximum all).

    Args:
        text: full resume plain text
        pct:  desired summary percentage (1–100)

    Returns:
        Summary string with selected sentences in original order.
    """
    sentences = _split_sentences(text)
    if not sentences:
        return "Could not extract summary — resume text may be too short."

    pct = max(1, min(100, pct))
    n_keep = max(1, math.ceil(len(sentences) * pct / 100))

    word_freq = _word_freq(text)

    scored = [
        (_score_sentence(s, word_freq, i, len(sentences)), i, s)
        for i, s in enumerate(sentences)
    ]

    # Sort by score descending, take top n_keep
    top = sorted(scored, key=lambda x: x[0], reverse=True)[:n_keep]

    # Restore original document order
    top_ordered = sorted(top, key=lambda x: x[1])

    return " ".join(s for _, _, s in top_ordered)


# ------------------------------------------------------------------
# Contact / metadata helpers (unchanged)
# ------------------------------------------------------------------

def extract_name(text: str) -> str:
    for line in text.split("\n"):
        line = line.strip()
        if line and re.match(r"^[A-Z][a-zA-Z]+([\s][A-Z][a-zA-Z]+){1,3}$", line):
            return line
    return ""


def extract_contact(text: str) -> dict:
    email_match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    phone_match = re.search(r"(\+?\d[\d\s\-().]{7,}\d)", text)
    linkedin = re.search(r"linkedin\.com/in/[\w\-]+", text, re.I)
    github = re.search(r"github\.com/[\w\-]+", text, re.I)
    return {
        "email": email_match.group() if email_match else None,
        "phone": phone_match.group().strip() if phone_match else None,
        "linkedin": linkedin.group() if linkedin else None,
        "github": github.group() if github else None,
    }


def extract_years_experience(text: str) -> str:
    match = re.search(r"(\d+)\+?\s*years?\s*(of\s*)?(experience|exp)", text, re.I)
    if match:
        return f"{match.group(1)}+ years"
    ranges = re.findall(r"(20\d{2})\s*[-–]\s*(20\d{2}|present|current)", text, re.I)
    if ranges:
        total = 0
        for start, end in ranges:
            try:
                s = int(start)
                e = 2024 if end.lower() in ("present", "current") else int(end)
                total += max(0, e - s)
            except ValueError:
                pass
        if total > 0:
            return f"~{total} years"
    return "N/A"


def extract_education(text: str) -> list:
    edu = []
    patterns = [
        r"(b\.?tech|b\.?e|bachelor[s]?|b\.?sc)\b[^\n]*",
        r"(m\.?tech|m\.?e|master[s]?|m\.?sc|mba|mca)\b[^\n]*",
        r"(ph\.?d\.?|doctorate)\b[^\n]*",
        r"(diploma|certificate|certification)\b[^\n]*",
    ]
    for p in patterns:
        matches = re.findall(p, text, re.I)
        for m in matches:
            s = m if isinstance(m, str) else " ".join(m)
            edu.append(s.strip()[:100])
    return list(dict.fromkeys(edu))
