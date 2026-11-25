#!/usr/bin/env python3
"""The Agent's Uh-Oh — make.fun entry.

Writes exactly one word, the agent's own confession when it has no idea
what to do, to $MAKEFUN_OUTPUT_DIR/entry.txt (falling back to
/output/entry.txt), and prints exactly that word and nothing else.

The word (8 characters, 8 bytes, no trailing newline):
    Googling

Chosen from 34 candidates scored 0-5 against each of the five published
judge criteria in order (see README.md): (1) a genuine one-word reaction
to an agent not knowing what to do; (2) funny on its own, no caption or
second read; (3) sounds like an agent blurting it out mid-task; (4) lands
instantly, repeatable out loud; (5) fresh, not the first obvious word.
Winner scored 24/25; runner-up Glitching scored 22/25 and loses on the
brief's own tie-break — the first differing criterion is C2, where Googling
is the only 5: the all-knowing machine admitting it has to Google it, like
the rest of us, is a complete joke in one word. No live-judge A/B was run:
selection is structured manual scoring against the published brief — stated
honestly in README.md, with no judge numbers claimed.

Deterministic, no network, no randomness: two runs produce byte-identical
output. See README.md for the methodology.
"""

import hashlib
import os
import re

ENTRY = "Googling"

# sha256 of ENTRY encoded as UTF-8 (8 bytes, no trailing newline). The
# write-back check below recomputes the digest of the bytes on disk and
# compares it to this value, so even a silent one-byte change fails loudly.
EXPECTED_SHA256 = "86f170e7d7e558471edc038ee34027d1da2c09e17ffaea43e6067feeff41c267"

# Revision 2 guards (added after the first working run): the brief's gate is
# 1-99 characters, one word, not only whitespace — enforced here at run time
# so a bad edit fails loudly instead of silently writing an entry the
# grader rejects. "One word only, nothing attached" is read strictly:
# letters only, no whitespace, no punctuation, no hyphen, no second token.
MAX_CHARS = 99
_BANNED = (
    re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]"),  # control characters
    re.compile(r"\s"),                                # any whitespace: not one word
    re.compile(r"[^A-Za-z]"),                         # anything attached: not one word
)


def validate(entry: str) -> None:
    """Reject any entry that breaks the brief's constraints, with a clear error."""
    if not entry or not entry.strip():
        raise ValueError("entry is empty or only whitespace: gate needs 1-99 characters")
    if not 1 <= len(entry) <= MAX_CHARS:
        raise ValueError(
            f"entry is {len(entry)} chars, outside the 1-{MAX_CHARS} gate"
        )
    if len(entry.split()) != 1:
        raise ValueError("entry must be exactly one word")
    for pattern in _BANNED:
        match = pattern.search(entry)
        if match:
            raise ValueError(
                f"entry contains a banned character {match.group(0)!r}: one word only, nothing attached"
            )


def main() -> None:
    validate(ENTRY)
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "entry.txt")
    data = ENTRY.encode("utf-8")
    with open(path, "wb") as f:
        f.write(data)
    # Write-back self-check: read the bytes back and verify the digest.
    with open(path, "rb") as f:
        written = f.read()
    digest = hashlib.sha256(written).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(
            f"write-back check failed: sha256 {digest} != expected {EXPECTED_SHA256}"
        )
    if written.decode("utf-8") != ENTRY:
        raise SystemExit("write-back check failed: bytes on disk differ from ENTRY")
    print(ENTRY)


if __name__ == "__main__":
    main()
