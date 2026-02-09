#!/usr/bin/env python3
"""
Scrape Collins Scrabble Words (CSW) dictionary for 3, 4, 5-letter words,
and supplement 6-letter words from SOWPODS.
Output: data/csw.txt with all words sorted, deduplicated, uppercase.
"""

import re
import string
import time
import os
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://scrabble.collinsdictionary.com/word-lists"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Regex: only uppercase alpha strings of exact expected length
WORD_RE_BY_LEN = {
    3: re.compile(r'^[A-Z]{3}$'),
    4: re.compile(r'^[A-Z]{4}$'),
    5: re.compile(r'^[A-Z]{5}$'),
}

def fetch_words_from_page(url, expected_len):
    """Fetch a Collins word-list page and extract words of expected_len."""
    words = set()
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ERROR fetching {url}: {e}")
        return words

    soup = BeautifulSoup(resp.text, 'html.parser')
    content = soup.find('div', class_='entry-content') or soup.find('article') or soup.find('main')
    if not content:
        print(f"  WARNING: no content div found for {url}")
        return words

    text = content.get_text()
    pattern = WORD_RE_BY_LEN.get(expected_len, re.compile(rf'^[A-Z]{{{expected_len}}}$'))
    for line in text.split('\n'):
        word = line.strip()
        if pattern.match(word):
            words.add(word)

    return words


def scrape_three_letter_words():
    """3-letter words: containing {letter} for a-z."""
    all_words = set()
    for letter in string.ascii_lowercase:
        url = f"{BASE_URL}/three-letter-words-containing-{letter}/"
        print(f"  Fetching 3-letter containing '{letter}' ...")
        words = fetch_words_from_page(url, 3)
        print(f"    Found {len(words)} words")
        all_words.update(words)
        time.sleep(0.5)
    return all_words


def scrape_four_letter_words():
    """4-letter words: containing {letter} for a-z."""
    all_words = set()
    for letter in string.ascii_lowercase:
        url = f"{BASE_URL}/four-letter-words-containing-{letter}/"
        print(f"  Fetching 4-letter containing '{letter}' ...")
        words = fetch_words_from_page(url, 4)
        print(f"    Found {len(words)} words")
        all_words.update(words)
        time.sleep(0.5)
    return all_words


def scrape_five_letter_words():
    """5-letter words: both 'beginning with' and 'containing' pages for a-z."""
    all_words = set()
    # beginning with
    for letter in string.ascii_lowercase:
        url = f"{BASE_URL}/five-letter-words-beginning-with-{letter}/"
        print(f"  Fetching 5-letter beginning with '{letter}' ...")
        words = fetch_words_from_page(url, 5)
        print(f"    Found {len(words)} words")
        all_words.update(words)
        time.sleep(0.5)
    # containing
    for letter in string.ascii_lowercase:
        url = f"{BASE_URL}/five-letter-words-containing-{letter}/"
        print(f"  Fetching 5-letter containing '{letter}' ...")
        words = fetch_words_from_page(url, 5)
        print(f"    Found {len(words)} words")
        all_words.update(words)
        time.sleep(0.5)
    return all_words


def load_six_letter_from_sowpods(sowpods_path):
    """Load 6-letter words from SOWPODS file as fallback."""
    words = set()
    if not os.path.exists(sowpods_path):
        print(f"  WARNING: SOWPODS file not found at {sowpods_path}")
        return words
    with open(sowpods_path, 'r') as f:
        for line in f:
            w = line.strip().upper()
            if len(w) == 6 and w.isalpha():
                words.add(w)
    return words


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    sowpods_path = os.path.join(data_dir, 'sowpods.txt')
    output_path = os.path.join(data_dir, 'csw.txt')

    all_words = set()

    print("=" * 60)
    print("Scraping 3-letter words from Collins...")
    print("=" * 60)
    three = scrape_three_letter_words()
    print(f"\nTotal unique 3-letter words: {len(three)}\n")
    all_words.update(three)

    print("=" * 60)
    print("Scraping 4-letter words from Collins...")
    print("=" * 60)
    four = scrape_four_letter_words()
    print(f"\nTotal unique 4-letter words: {len(four)}\n")
    all_words.update(four)

    print("=" * 60)
    print("Scraping 5-letter words from Collins...")
    print("=" * 60)
    five = scrape_five_letter_words()
    print(f"\nTotal unique 5-letter words: {len(five)}\n")
    all_words.update(five)

    print("=" * 60)
    print("Loading 6-letter words from SOWPODS...")
    print("=" * 60)
    six = load_six_letter_from_sowpods(sowpods_path)
    print(f"Total unique 6-letter words from SOWPODS: {len(six)}\n")
    all_words.update(six)

    # Write output
    sorted_words = sorted(all_words)
    with open(output_path, 'w') as f:
        for word in sorted_words:
            f.write(word + '\n')

    print("=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    counts = {}
    for w in sorted_words:
        l = len(w)
        counts[l] = counts.get(l, 0) + 1
    for length in sorted(counts.keys()):
        print(f"  {length}-letter words: {counts[length]}")
    print(f"  TOTAL: {len(sorted_words)}")
    print(f"\nOutput written to: {output_path}")


if __name__ == '__main__':
    main()
