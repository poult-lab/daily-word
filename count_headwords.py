"""
Count headwords in a vocabulary journal file.

The file contains dated vocabulary entries in this format:
    01.arsenal  [ˈɑː(r)sənl]
    02.missile [ˈmɪsl]
    ...
Each headword line starts with a two-digit number and a period.

This script:
  1. Extracts every headword (removing phonetics, quoted glosses,
     {brace} annotations, and Chinese characters).
  2. Counts total entries and unique headwords.
  3. Separates single words from multi-word phrases.
  4. Lists which headwords were recorded more than once.
"""

import re
from collections import Counter

FILE_PATH = "/mnt/user-data/uploads/words_counting"


def extract_headwords(path):
    """Read the file and return a list of cleaned headwords."""
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            # Keep only lines that start with a two-digit number + period,
            # e.g. "01.arsenal  [ˈɑː(r)sənl]"
            m = re.match(r"^\d{2}\.(.*)$", line.strip())
            if not m:
                continue

            w = m.group(1)

            # Cut the string at the first phonetic bracket: [ / ( or （
            w = re.split(r"[\[/(（]", w)[0]

            # Remove quoted definitions, e.g. "a collection of weapons"
            w = re.sub(r'"[^"]*"', "", w)

            # Remove annotations in braces, e.g. {de:向下+posit:位置}
            w = re.sub(r"\{[^}]*\}", "", w)

            # Remove Chinese characters and full-width punctuation
            w = re.sub(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]", "", w)

            # Remove stray nested numbering, e.g. "1.capitalism" -> "capitalism"
            w = re.sub(r"^\d+\.", "", w)

            # Normalize: lowercase, strip whitespace and stray punctuation
            w = w.strip().lower().strip(".,;:'\" ")

            if w:
                entries.append(w)
    return entries


def main():
    entries = extract_headwords(FILE_PATH)

    print(f"Total headword entries: {len(entries)}")

    unique = sorted(set(entries))
    print(f"Unique headwords:       {len(unique)}")

    # Separate single words from phrases/other forms.
    # A "single word" = letters, apostrophes, or hyphens only.
    single_words = [w for w in unique if re.fullmatch(r"[a-z][a-z'-]*", w)]
    phrases = [w for w in unique if w not in set(single_words)]
    print(f"  - single words:       {len(single_words)}")
    print(f"  - phrases / other:    {len(phrases)}")

    # Find duplicated headwords
    counts = Counter(entries)
    dups = {w: n for w, n in counts.items() if n > 1}
    print(f"\nHeadwords recorded more than once: {len(dups)}")

    for times in sorted(set(dups.values()), reverse=True):
        words = sorted(w for w, n in dups.items() if n == times)
        print(f"\nRecorded {times} times ({len(words)} words):")
        print(", ".join(words))


if __name__ == "__main__":
    main()
