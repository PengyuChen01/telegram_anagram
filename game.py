"""Core game logic for the Anagram game."""

import random
from typing import List, Tuple

from config import VOWELS, CONSONANTS, NUM_LETTERS, MIN_VOWELS, MAX_VOWELS, SCORE_MAP
from dictionary import dictionary
from models import GameSession, Player


def generate_letters():
    min_words_required = 10
    max_attempts = 100
    for _ in range(max_attempts):
        num_vowels = random.randint(MIN_VOWELS, MAX_VOWELS)
        num_consonants = NUM_LETTERS - num_vowels
        vowels = random.sample(VOWELS, num_vowels)
        consonants = random.sample(CONSONANTS, num_consonants)
        letters = vowels + consonants
        random.shuffle(letters)
        letters = [l.upper() for l in letters]
        word_count = dictionary.count_possible_words(letters)
        if word_count >= min_words_required:
            return letters
    return list("MASTER")


def validate_submission(player, word, session):
    """Returns (success, message, points)."""
    word = word.upper()
    if len(word) < 3:
        return False, "Too short! Need 3+ letters.", 0
    if len(word) > NUM_LETTERS:
        return False, "Too long! Max %d letters." % NUM_LETTERS, 0
    if not dictionary.can_form_word(word, session.letters):
        bad = set(word) - set(l.upper() for l in session.letters)
        return False, "Letter(s) %s not in your letters!" % ",".join(bad), 0
    if player.has_found(word):
        return False, "Already found %s!" % word, 0
    if not dictionary.is_valid_word(word):
        return False, "%s is not a valid word!" % word, 0
    points = player.add_word(word)
    return True, "+%d pts for %s!" % (points, word), points


def format_game_message(session, player):
    lines = []
    lines.append("=== ANAGRAM GAME ===")
    lines.append("")
    lines.append("Letters:  [ %s ]" % session.letters_display)
    lines.append("")
    inp = player.current_input if player.current_input else "_ _ _"
    lines.append("Input:  %s" % inp)
    lines.append("")
    lines.append("Time: %ds  |  Score: %d" % (session.time_remaining, player.score))
    if player.last_action:
        lines.append("")
        lines.append(">> %s" % player.last_action)
    lines.append("")
    if player.found_words:
        ws = []
        for w in player.found_words:
            pts = SCORE_MAP.get(len(w), 0)
            ws.append("%s(+%d)" % (w, pts))
        lines.append("Found (%d): %s" % (len(player.found_words), ", ".join(ws)))
    else:
        lines.append("No words found yet!")
    return "\n".join(lines)


def format_results_message(session):
    lines = []
    lines.append("=== GAME OVER! ===")
    lines.append("")
    lines.append("Letters were:  [ %s ]" % session.letters_display)
    lines.append("")
    rankings = session.get_rankings()
    if len(rankings) == 1:
        p = rankings[0]
        lines.append("Final Score: %d" % p.score)
        if p.found_words:
            ws = ["%s(+%d)" % (w, SCORE_MAP.get(len(w), 0)) for w in p.found_words]
            lines.append("Words Found (%d): %s" % (len(p.found_words), ", ".join(ws)))
        else:
            lines.append("No words found!")
    else:
        lines.append("Rankings:")
        for i, p in enumerate(rankings, 1):
            medal = {1: "1st", 2: "2nd", 3: "3rd"}.get(i, "%dth" % i)
            lines.append("  %s  %s: %d pts (%d words)" % (medal, p.display_name, p.score, len(p.found_words)))
    lines.append("")
    all_found = set()
    for p in session.players.values():
        all_found.update(p.found_words)
    missed = [w for w in session.possible_words if w not in all_found]
    if missed:
        shown = missed[:20]
        extra = len(missed) - len(shown)
        lines.append("Missed words: %s" % ", ".join(shown))
        if extra > 0:
            lines.append("  ...and %d more!" % extra)
    lines.append("")
    lines.append("Total: %d/%d possible words found" % (len(all_found), len(session.possible_words)))
    return "\n".join(lines)


def format_waiting_message(session):
    lines = []
    lines.append("=== ANAGRAM GAME - Lobby ===")
    lines.append("")
    lines.append("Players:")
    for p in session.players.values():
        tag = " (host)" if p.user_id == session.host_user_id else ""
        lines.append("  - %s%s" % (p.display_name, tag))
    lines.append("")
    lines.append("Press Join Game to join. Host presses Start! to begin.")
    return "\n".join(lines)
