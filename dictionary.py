"""Dictionary loading and word validation for the Anagram game."""

from collections import Counter
from typing import Set, List
from config import DICTIONARY_PATH, MIN_WORD_LENGTH, NUM_LETTERS


class Dictionary:
    """Loads SOWPODS dictionary and provides word validation."""

    def __init__(self):
        self._words: Set[str] = set()
        self._words_by_length: dict[int, Set[str]] = {}
        self._load()

    def _load(self):
        """Load dictionary file and index words by length."""
        with open(DICTIONARY_PATH, "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip().upper()
                if len(word) < MIN_WORD_LENGTH or len(word) > NUM_LETTERS:
                    continue
                self._words.add(word)
                length = len(word)
                if length not in self._words_by_length:
                    self._words_by_length[length] = set()
                self._words_by_length[length].add(word)

        total = len(self._words)
        print(f"Dictionary loaded: {total} words (length {MIN_WORD_LENGTH}-{NUM_LETTERS})")
        for length in sorted(self._words_by_length.keys()):
            count = len(self._words_by_length[length])
            print(f"  {length}-letter words: {count}")

    def is_valid_word(self, word: str) -> bool:
        """Check if a word exists in the dictionary."""
        return word.upper() in self._words

    def can_form_word(self, word: str, available_letters: List[str]) -> bool:
        """Check if a word can be formed using the available letters (each letter used once)."""
        available_count = Counter(l.upper() for l in available_letters)
        word_count = Counter(word.upper())
        return all(word_count[c] <= available_count.get(c, 0) for c in word_count)

    def find_possible_words(self, letters: List[str]) -> List[str]:
        """Find all valid words that can be formed from the given letters.

        Each letter can only be used once per word.
        """
        available_count = Counter(l.upper() for l in letters)
        possible = []
        for word in self._words:
            word_count = Counter(word)
            if all(word_count[c] <= available_count.get(c, 0) for c in word_count):
                possible.append(word)
        return sorted(possible, key=lambda w: (len(w), w))

    def count_possible_words(self, letters: List[str]) -> int:
        """Count how many valid words can be formed from the given letters."""
        available_count = Counter(l.upper() for l in letters)
        count = 0
        for word in self._words:
            word_count = Counter(word)
            if all(word_count[c] <= available_count.get(c, 0) for c in word_count):
                count += 1
        return count


# Singleton instance
dictionary = Dictionary()
