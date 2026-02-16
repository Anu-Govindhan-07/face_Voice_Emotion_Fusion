from __future__ import annotations

import re

from .language_detect import detect_language

TITLE_CASE_RE = re.compile(r"^[A-ZÅÄÖ][a-zåäöA-ZÅÄÖ'-]{1,29}$")


SELF_PATTERNS = {
    "en": [r"\b(?:i am|i'm|my name is)\s+(.+)$"],
    "sv": [r"\b(?:jag heter|mitt namn är)\s+(.+)$"],
}

MENTION_PATTERNS = {
    "en": [r"\b(?:this is|meet)\s+(.+)$"],
    "sv": [r"\b(?:det här är|han heter|hon heter)\s+(.+)$"],
}


def _normalize_candidates(fragment: str) -> list[str]:
    fragment = fragment.strip(" .,!?:;")
    tokens = re.split(r"\s+(?:and|och|,)\s+|,\s*", fragment)
    names = []
    for token in tokens:
        token = token.strip(" .,!?:;")
        if not token:
            continue
        words = token.split()
        if all(TITLE_CASE_RE.match(w) for w in words):
            names.append(" ".join(words))
    return names


def _extract_with_patterns(text: str, patterns: list[str], signal_type: str, language: str) -> list[dict]:
    signals = []
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if not m:
            continue
        for name in _normalize_candidates(m.group(1)):
            confidence = 0.9 if signal_type == "self" else 0.75
            signals.append({"name": name, "type": signal_type, "confidence": confidence, "method": "pattern", "language": language})
    return signals


def extract_name_signals(segments: list[dict]) -> list[dict]:
    output = []
    for seg in segments:
        text = seg.get("text", "")
        language = detect_language(text)

        # Primary would be multilingual NER; lightweight fallback uses robust patterning with title-case guard.
        signals = []
        signals.extend(_extract_with_patterns(text, SELF_PATTERNS.get(language, []) + SELF_PATTERNS["en"], "self", language))
        signals.extend(_extract_with_patterns(text, MENTION_PATTERNS.get(language, []) + MENTION_PATTERNS["en"], "mentioned", language))

        # Deduplicate by (name, type)
        seen = set()
        deduped = []
        for s in signals:
            key = (s["name"], s["type"])
            if key in seen:
                continue
            seen.add(key)
            deduped.append({k: v for k, v in s.items() if k != "language"})

        output.append(
            {
                "start": seg.get("start"),
                "end": seg.get("end"),
                "speaker_id": seg.get("speaker_id"),
                "language": language,
                "signals": deduped,
            }
        )
    return output
