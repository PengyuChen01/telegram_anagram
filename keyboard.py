"""Inline Keyboard generation for the Anagram game.

Layout: all buttons in a single row
[letter1] [letter2] ... [letter6] [backspace] [submit]

When a letter is used, it shows as X. Pressing X restores that letter.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Callback data prefixes
CB_LETTER = "letter:"    # letter:<position>:<letter>
CB_RESTORE = "restore:"  # restore:<position>:<letter>
CB_BACKSPACE = "action:backspace"
CB_SUBMIT = "action:submit"


def build_game_keyboard(available_letters=None, used_positions=None):
    """Build keyboard with all buttons in a single row.

    Args:
        available_letters: list of 6 letters
        used_positions: set of positions (0-5) that have been used
    """
    if not available_letters:
        return InlineKeyboardMarkup([])

    if used_positions is None:
        used_positions = set()

    letters = [l.upper() for l in available_letters]

    # All buttons in one row: 6 letters + backspace + submit
    row = []
    for i, letter in enumerate(letters):
        if i in used_positions:
            # Show X, pressing it restores this letter
            row.append(
                InlineKeyboardButton(
                    "\u2716", callback_data="%s%d:%s" % (CB_RESTORE, i, letter)
                )
            )
        else:
            # Show the letter, pressing it uses this position
            row.append(
                InlineKeyboardButton(
                    letter, callback_data="%s%d:%s" % (CB_LETTER, i, letter)
                )
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
