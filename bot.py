"""Telegram Anagram Bot."""

import logging
from typing import Dict

from telegram import Update, CallbackQuery
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from config import BOT_TOKEN, GAME_DURATION
from models import GameSession, GameMode, GameState
from game import (
    generate_letters,
    validate_submission,
    format_game_message,
    format_results_message,
    format_waiting_message,
)
from keyboard import (
    build_game_keyboard,
    build_join_keyboard,
    CB_LETTER,
    CB_BACKSPACE,
    CB_SUBMIT,
)
from dictionary import dictionary

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

active_games: Dict[int, GameSession] = {}


def get_display_name(user):
    if user.first_name and user.last_name:
        return "%s %s" % (user.first_name, user.last_name)
    return user.first_name or user.username or "User%d" % user.id


async def send_game_keyboard(context, chat_id, session, user_id):
    player = session.get_player(user_id)
    if not player:
        return 0
    text = format_game_message(session, player)
    keyboard = build_game_keyboard(session.letters)
    msg = await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)
    player.message_id = msg.message_id
    return msg.message_id


async def update_player_message(context, chat_id, session, user_id):
    player = session.get_player(user_id)
    if not player or not player.message_id:
        return
    text = format_game_message(session, player)
    keyboard = build_game_keyboard(session.letters)
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id, message_id=player.message_id,
            text=text, reply_markup=keyboard,
        )
    except Exception as e:
        if "Message is not modified" not in str(e):
            logger.warning("Failed to update message: %s", e)


async def end_game(context, chat_id):
    session = active_games.get(chat_id)
    if not session:
        return
    session.finish()
    for player in session.players.values():
        if player.message_id:
            try:
                player.last_action = "Time is up!"
                final_text = format_game_message(session, player)
                await context.bot.edit_message_text(
                    chat_id=chat_id, message_id=player.message_id,
                    text=final_text, reply_markup=None,
                )
            except Exception:
                pass
    results = format_results_message(session)
    await context.bot.send_message(chat_id=chat_id, text=results)
    del active_games[chat_id]


async def timer_callback(context):
    chat_id = context.job.data
    await end_game(context, chat_id)


async def start_game_session(context, session):
    session.letters = generate_letters()
    session.start()
    session.possible_words = dictionary.find_possible_words(session.letters)
    logger.info("Game started in chat %s: letters=%s, possible=%d",
                session.chat_id, session.letters, len(session.possible_words))
    for user_id in session.players:
        await send_game_keyboard(context, session.chat_id, session, user_id)
    context.job_queue.run_once(
        timer_callback, when=GAME_DURATION,
        data=session.chat_id, name="game_timer_%d" % session.chat_id,
    )


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = ("Welcome to the Anagram Game!\n\n"
           "Given 6 random letters, find as many words as you can in 60 seconds!\n\n"
           "Scoring:\n"
           "  3 letters = 300 pts\n"
           "  4 letters = 400 pts\n"
           "  5 letters = 500 pts\n"
           "  6 letters = 600 pts\n\n"
           "Letters can be reused!\n\n"
           "Commands:\n"
           "  /play  - Start a solo game\n"
           "  /multi - Create a multiplayer game\n"
           "  /help  - Show this message")
    await update.message.reply_text(msg)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cmd_start(update, context)


async def cmd_play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id in active_games:
        await update.message.reply_text("A game is already running!")
        return
    session = GameSession(chat_id=chat_id, mode=GameMode.SOLO, host_user_id=user.id)
    session.add_player(user.id, user.username or "", get_display_name(user))
    active_games[chat_id] = session
    await update.message.reply_text("Starting solo game...")
    await start_game_session(context, session)


async def cmd_multi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id in active_games:
        await update.message.reply_text("A game is already running!")
        return
    session = GameSession(chat_id=chat_id, mode=GameMode.MULTI, host_user_id=user.id)
    session.add_player(user.id, user.username or "", get_display_name(user))
    active_games[chat_id] = session
    text = format_waiting_message(session)
    keyboard = build_join_keyboard()
    await update.message.reply_text(text, reply_markup=keyboard)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    chat_id = update.effective_chat.id
    user = update.effective_user
    if data == "action:join":
        await handle_join(query, context, chat_id, user)
        return
    if data == "action:begin":
        await handle_begin(query, context, chat_id, user)
        return
    session = active_games.get(chat_id)
    if not session or not session.is_playing:
        await query.answer("No active game!")
        return
    player = session.get_player(user.id)
    if not player:
        await query.answer("You are not in this game!")
        return
    if data.startswith(CB_LETTER):
        letter = data[len(CB_LETTER):]
        await handle_letter_press(query, context, chat_id, session, player, letter)
    elif data == CB_BACKSPACE:
        await handle_backspace(query, context, chat_id, session, player)
    elif data == CB_SUBMIT:
        await handle_submit(query, context, chat_id, session, player)
    else:
        await query.answer("Unknown action")


async def handle_join(query, context, chat_id, user):
    session = active_games.get(chat_id)
    if not session or not session.is_waiting:
        await query.answer("No lobby to join!")
        return
    if user.id in session.players:
        await query.answer("You already joined!")
        return
    session.add_player(user.id, user.username or "", get_display_name(user))
    text = format_waiting_message(session)
    keyboard = build_join_keyboard()
    await query.answer("%s joined!" % get_display_name(user))
    try:
        await query.edit_message_text(text, reply_markup=keyboard)
    except Exception:
        pass


async def handle_begin(query, context, chat_id, user):
    session = active_games.get(chat_id)
    if not session or not session.is_waiting:
        await query.answer("No lobby to start!")
        return
    if user.id != session.host_user_id:
        await query.answer("Only the host can start!")
        return
    if len(session.players) < 2:
        await query.answer("Need at least 2 players!")
        return
    await query.answer("Game starting!")
    try:
        await query.edit_message_text("Game starting now!")
    except Exception:
        pass
    await start_game_session(context, session)


async def handle_letter_press(query, context, chat_id, session, player, letter):
    if session.time_remaining <= 0:
        await query.answer("Time is up!")
        return
    player.add_letter(letter)
    player.last_action = ""
    await query.answer()
    await update_player_message(context, chat_id, session, player.user_id)


async def handle_backspace(query, context, chat_id, session, player):
    if session.time_remaining <= 0:
        await query.answer("Time is up!")
        return
    player.backspace()
    player.last_action = ""
    await query.answer()
    await update_player_message(context, chat_id, session, player.user_id)


async def handle_submit(query, context, chat_id, session, player):
    if session.time_remaining <= 0:
        await query.answer("Time is up!")
        return
    word = player.current_input.strip()
    if not word:
        await query.answer("Type some letters first!")
        return
    success, message, points = validate_submission(player, word, session)
    player.last_action = message
    player.reset_input()
    await query.answer(message)
    await update_player_message(context, chat_id, session, player.user_id)


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("play", cmd_play))
    app.add_handler(CommandHandler("multi", cmd_multi))
    app.add_handler(CallbackQueryHandler(handle_callback))
    logger.info("Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
