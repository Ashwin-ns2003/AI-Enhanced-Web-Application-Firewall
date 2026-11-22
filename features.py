import re
import urllib.parse

# Words that often appear in attacks
SUSPICIOUS_WORDS = ["select", "union", "drop", "insert", "script", "alert", "onerror", "onload",
                    "passwd", "cmd", "bash", "whoami", "sleep", "exec", "etc", "javascript"]


def extract_features(text):
    """Turn a request string into a few simple numbers for the ML model."""
    text = urllib.parse.unquote_plus(text or "")      # decode %27 -> ' etc.
    lower = text.lower()
    length = len(text)
    special = sum(1 for ch in text if ch in "'\"<>;|`$()%=/\\-")   # special characters
    digits = sum(ch.isdigit() for ch in text)
    keywords = sum(1 for w in SUSPICIOUS_WORDS if w in lower)
    special_ratio = special / length if length else 0
    return [length, special, special_ratio, digits, keywords]
