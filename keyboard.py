"""Inline Keyboard generation for the Anagram game.

Layout: only the game letters + backspace + submit
Row 1: [letter1] [letter2] [letter3]
Row 2: [letter4] [letter5] [letter6]
Row 3: [backspace] [submit]
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Callback data prefixes
CB_LETTER = "letter:"
CB_BACKSPACE = "action:backspace"
CB_SUBMIT = "action:submit"


def build_game_keyboard(available_letters=None):
    """Build keyboard with only the game letters + backspace + submit."""
    if not available_letters:
        return InlineKeyboardMarkup([])

    letters = [l.upper() for l in available_letters]

    # Split letters into rows of 3
    keyboard = []
    row = []
    for letter in letters:
        row.append(
            InlineKeyboardButton(letter, callback_data="%s%s" % (CB_LETTER, letter))
        )
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    # Add backspace and submit row
    keyboard.append([
        InlineKeyboardButton("\u232b", callback_data=CB_BACKSPACE),
        InlineKeyboardButton("\u2713", callback_data=CB_SUBMIT),
    ])

    return InlineKeyboardMarkup(keyboard)


def build_join_keyboard():
    """Build the keyboard for the multiplayer lobby."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Join Game", callback_data="action:join"),
            InlineKeyboardButton("Start!", callback_data="action:begin"),
        ]
    ])
