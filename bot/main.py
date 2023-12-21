# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, PollAnswerHandler
# from utils.logger import setup_logger
# from bot.onboarding import conversation_handler, receive_poll_answer
# from bot.commands import help, project, assignrole, createtask, assigntask, status, calendar, addevent, rsvp, settings, feedback

# logger = setup_logger(__name__, 'bot.log')
# logger.info("Bot started!")

# def error(update, context):
#     logger.warning('Update "%s" caused error "%s"', update, context.error)  

# def main():
#     """Start the bot."""
#     # Create the Updater and pass it your bot's token.
#     updater = Updater("6887127186:AAG525kpcNRTizg2LKM7BNfljDUT_k5tQ9M")

#     # Get the dispatcher to register handlers
#     dp = updater.dispatcher
#     dp.add_handler(CommandHandler("help", help))
#     dp.add_handler(CommandHandler("project", project))
#     dp.add_handler(CommandHandler("assignrole", assignrole))
#     dp.add_handler(CommandHandler("createtask", createtask))
#     dp.add_handler(CommandHandler("assigntask", assigntask))
#     dp.add_handler(CommandHandler("status", status))
#     dp.add_handler(CommandHandler("calendar", calendar))
#     dp.add_handler(CommandHandler("addevent", addevent))
#     dp.add_handler(CommandHandler("rsvp", rsvp))
#     dp.add_handler(CommandHandler("settings", settings))
#     dp.add_handler(CommandHandler("feedback", feedback))
#     # dp.add_handler(PollAnswerHandler("receive_poll_answer", receive_poll_answer))
#     dp.add_handler(MessageHandler(Filters.poll, receive_poll_answer, run_async=True))

#     # Register the conversation handler for the /start command
#     dp.add_handler(conversation_handler())

#     # Log all errors
#     dp.add_error_handler(error)

#     # Start the Bot
#     updater.start_polling()

#     # Run the bot until you press Ctrl-C
#     updater.idle()

# if __name__ == '__main__':
#     main()

import logging

from telegram import (
    KeyboardButton,
    KeyboardButtonPollType,
    Poll,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
# from telegram.constants import ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PollAnswerHandler,
    PollHandler,
    Filters,
)
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


TOTAL_VOTER_COUNT = 3


async def start(update, context):
    """Inform user about what this bot can do"""
    print(f"start initialized...")
    await update.message.reply_text(
        "Please select /poll to get a Poll, /quiz to get a Quiz or /preview"
        " to generate a preview for your poll"
    )


async def poll(update, context):
    """Sends a predefined poll"""
    questions = ["Good", "Really good", "Fantastic", "Great"]
    message = await context.bot.send_poll(
        update.effective_chat.id,
        "How are you?",
        questions,
        is_anonymous=False,
        allows_multiple_answers=True,
    )
    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {
        message.poll.id: {
            "questions": questions,
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "answers": 0,
        }
    }
    context.bot_data.update(payload)


async def receive_poll_answer(update, context):
    """Summarize a users poll vote"""
    answer = update.poll_answer
    answered_poll = context.bot_data[answer.poll_id]
    try:
        questions = answered_poll["questions"]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        return
    selected_options = answer.option_ids
    answer_string = ""
    for question_id in selected_options:
        if question_id != selected_options[-1]:
            answer_string += questions[question_id] + " and "
        else:
            answer_string += questions[question_id]
    await context.bot.send_message(
        answered_poll["chat_id"],
        f"{update.effective_user.mention_html()} feels {answer_string}!",
        # parse_mode=ParseMode.HTML,
    )
    answered_poll["answers"] += 1
    # Close poll after three participants voted
    if answered_poll["answers"] == TOTAL_VOTER_COUNT:
        await context.bot.stop_poll(answered_poll["chat_id"], answered_poll["message_id"])


async def quiz(update, context):
    """Send a predefined poll"""
    questions = ["1", "2", "4", "20"]
    message = await update.effective_message.reply_poll(
        "How many eggs do you need for a cake?", questions, type=Poll.QUIZ, correct_option_id=2
    )
    # Save some info about the poll the bot_data for later use in receive_quiz_answer
    payload = {
        message.poll.id: {"chat_id": update.effective_chat.id, "message_id": message.message_id}
    }
    context.bot_data.update(payload)


async def receive_quiz_answer(update, context):
    """Close quiz after three participants took it"""
    # the bot can receive closed poll updates we don't care about
    if update.poll.is_closed:
        return
    if update.poll.total_voter_count == TOTAL_VOTER_COUNT:
        try:
            quiz_data = context.bot_data[update.poll.id]
        # this means this poll answer update is from an old poll, we can't stop it then
        except KeyError:
            return
        await context.bot.stop_poll(quiz_data["chat_id"], quiz_data["message_id"])


async def preview(update, context):
    """Ask user to create a poll and display a preview of it"""
    # using this without a type lets the user chooses what he wants (quiz or poll)
    button = [[KeyboardButton("Press me!", request_poll=KeyboardButtonPollType())]]
    message = "Press the button to let the bot generate a preview for your poll"
    # using one_time_keyboard to hide the keyboard
    await update.effective_message.reply_text(
        message, reply_markup=ReplyKeyboardMarkup(button, one_time_keyboard=True)
    )


async def receive_poll(update, context):
    """On receiving polls, reply to it by a closed poll copying the received poll"""
    actual_poll = update.effective_message.poll
    # Only need to set the question and options, since all other parameters don't matter for
    # a closed poll
    await update.effective_message.reply_poll(
        question=actual_poll.question,
        options=[o.text for o in actual_poll.options],
        # with is_closed true, the poll/quiz is immediately closed
        is_closed=True,
        reply_markup=ReplyKeyboardRemove(),
    )


async def help_handler(update, context):
    """Display a help message"""
    await update.message.reply_text("Use /quiz, /poll or /preview to test this bot.")


def main():
    """Run bot."""
    # Create the Application and pass it your bot's token.
    updater =Updater("6887127186:AAG525kpcNRTizg2LKM7BNfljDUT_k5tQ9M")

    # Get the dispatcher to register handlers
    application = updater.dispatcher
    application.add_handler(CommandHandler("start", start, run_async=True))
    application.add_handler(CommandHandler("poll", poll))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("preview", preview))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(MessageHandler(Filters.poll, receive_poll))
    application.add_handler(PollAnswerHandler(receive_poll_answer))
    application.add_handler(PollHandler(receive_quiz_answer))

    # Run the bot until the user presses Ctrl-C
    # application.run_polling(allowed_updates=Update.ALL_TYPES)
    # Log all errors
    # application.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == "__main__":
    main()