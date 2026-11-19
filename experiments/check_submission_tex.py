"""Structural checks for the 8-page submission source.

Checks: environments and braces balanced, every \\ref has a \\label, every
citation key exists in the bibliography and every bib entry is cited, and the
main-body word count (abstract through the end of the conclusion).

Usage:
  python -m experiments.check_submission_tex
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "paper" / "submission" / "main.tex"
BIB = ROOT / "paper" / "submission" / "custom.bib"


def main() -> int:
    tex = TEX.read_text(encoding="utf-8")
    bib = BIB.read_text(encoding="utf-8")

    labels = set(re.findall(r"\\label\{([^}]+)\}", tex))
    refs = set(re.findall(r"\\ref\{([^}]+)\}", tex))
    missing_labels = sorted(refs - labels)

    cites: set[str] = set()
    for group in re.findall(r"\\cite[tp]?\{([^}]+)\}", tex):
        cites |= {key.strip() for key in group.split(",")}
    bib_keys = set(re.findall(r"@\w+\{([^,]+),", bib))
    missing_bib = sorted(cites - bib_keys)
    uncited = sorted(bib_keys - cites)

    opens = Counter(re.findall(r"\\begin\{([^}]+)\}", tex))
    closes = Counter(re.findall(r"\\end\{([^}]+)\}", tex))
    unbalanced = {key: (opens[key], closes[key])
                  for key in set(opens) | set(closes) if opens[key] != closes[key]}
    braces = tex.count("{") - tex.count("}")

    start = tex.index(r"\begin{abstract}")
    end = tex.index(r"\section*{Limitations}")
    body = re.sub(r"(?m)%.*$", "", tex[start:end])
    body_words = len(re.findall(r"[A-Za-z0-9]+", body))
    body_tex_words = len(re.findall(r"[A-Za-z]+", re.sub(r"\\[A-Za-z]+", " ", body)))

    errors = []
    if missing_labels:
        errors.append(f"refs without labels: {missing_labels}")
    if missing_bib:
        errors.append(f"citations missing from bib: {missing_bib}")
    if uncited:
        errors.append(f"uncited bib entries: {uncited}")
    if unbalanced:
        errors.append(f"unbalanced environments: {unbalanced}")
    if braces:
        errors.append(f"unbalanced braces: {braces:+d}")

    print(f"labels={len(labels)} refs={len(refs)} cite_keys={len(cites)} "
          f"bib_keys={len(bib_keys)}")
    print(f"body_words_including_quoted_text={body_words} "
          f"body_words_including_commands={body_tex_words}")
    print(f"figures={tex.count(chr(92) + 'includegraphics')} "
          f"tables={opens['table'] + opens['table*']}")
    if errors:
        for error in errors:
            print("FAIL:", error)
        return 1
    print("OK: structure, references, and citations are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
