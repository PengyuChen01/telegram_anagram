import os

# Telegram Bot Token - set via environment variable or replace here
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Game settings
GAME_DURATION = 60  # seconds
NUM_LETTERS = 6
MIN_VOWELS = 2
MAX_VOWELS = 3

# Scoring: word length -> points
SCORE_MAP = {
    3: 300,
    4: 400,
    5: 500,
    6: 600,
}

# Minimum word length
MIN_WORD_LENGTH = 3

# Dictionary file path
DICTIONARY_PATH = os.path.join(os.path.dirname(__file__), "data", "csw.txt")

# Vowels and consonants
VOWELS = list("AEIOU")
CONSONANTS = list("BCDFGHJKLMNPQRSTVWXYZ")
