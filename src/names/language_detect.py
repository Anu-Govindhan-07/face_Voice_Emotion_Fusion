from __future__ import annotations


def detect_language(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ["jag heter", "mitt namn", "det här är", "han heter", "hon heter"]):
        return "sv"
    return "en"
