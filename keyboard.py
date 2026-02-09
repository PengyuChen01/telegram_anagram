"""Inline Keyboard generation for the Anagram game.

Layout: all buttons in a single row
[letter1] [letter2] [letter3] [letter4] [letter5] [letter6] [backspace] [submit]
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Callback data prefixes
CB_LETTER = "letter:"
CB_BACKSPACE = "action:backspace"
CB_SUBMIT = "action:submit"


def build_game_keyboard(available_letters=None):
    """Build keyboard with all buttons in a single row."""
    if not available_letters:
        return InlineKeyboardMarkup([])

    letters = [l.upper() for l in available_letters]

    # All buttons in one row: 6 letters + backspace + submit
    row = []
    for letter in letters:
        row.append(
            InlineKeyboardButton(letter, callback_data="%s%s" % (CB_LETTER, letter))
        )
    row.append(InlineKeyboardButton("\u232b", callback_data=CB_BACKSPACE))
    row.append(InlineKeyboardButton("\u2713", callback_data=CB_SUBMIT))

    return InlineKeyboardMarkup([row])


def build_join_keyboard():
    """Build the keyboard for the multiplayer lobby."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Join Game", callback_data="action:join"),
            InlineKeyboardButton("Start!", callback_data="action:begin"),
        ]
    ])
