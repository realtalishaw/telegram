#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that works with polls. Only 3 people are allowed to interact with each
poll/quiz the bot generates. The preview command generates a closed poll/quiz, exactly like the
one the user sends the bot
"""
import logging

from telegram import (
    KeyboardButton,
    KeyboardButtonPollType,
    Poll,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PollAnswerHandler,
    PollHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


TOTAL_VOTER_COUNT = 3000000

original_poll_id = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inform user about what this bot can do"""
    await update.message.reply_text(
        "Please select /poll to get a Poll, /quiz to get a Quiz or /preview"
        " to generate a preview for your poll"
    )


async def poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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


async def receive_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        parse_mode=ParseMode.HTML,
    )
    answered_poll["answers"] += 1
    # Close poll after three participants voted
    if answered_poll["answers"] == TOTAL_VOTER_COUNT:
        await context.bot.stop_poll(answered_poll["chat_id"], answered_poll["message_id"])


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a predefined poll"""
    questions = ["1", "2", "4", "20"]
    message = await update.effective_message.reply_poll(
        "How many eggs do you need for a cake?", questions, type=Poll.QUIZ, correct_option_id=2
    )
    # Save some info about the poll the bot_data for later use in receive_quiz_answer
    payload = {
        message.poll.id: {"chat_id": update.effective_chat.id, "message_id": message.message_id}
    }
    global original_poll_id
    original_poll_id = message.poll.id
    
    context.bot_data.update(payload)


async def receive_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Close quiz after three participants took it"""
    # the bot can receive closed poll updates we don't care about
    print("Someone took a quiz!")
    print(f"update poll answer: {update.poll_answer}")
    if update.poll_answer:
        # Access the correct option ID
        correct_option_id = update.poll.correct_option_id

        # Print the correct option ID
        print(f"The correct option ID is: {correct_option_id}")
    answer = update.poll
    print(f"poll answer: {answer}")

    user_choice = 0
    for option in answer.options:
        if option.voter_count == 1:
            print(f"Option: {option.text}, Voter Count: {option.voter_count}")
            user_choice = option.text
    
    print(f"user choice: {user_choice}")
    if user_choice == "4":
        print("Correct answer moving on to another function...")
    else:
        print("Incorrect choice, rerun /quiz")
    # user_choice = update.poll.chosen_option
    # print(f"user choice: {user_choice}")
    # poll_id = update.poll_answer.poll_id
    # print(f"poll_id: {poll_id}")

    # original_poll = original_poll_id #retrieve_poll(poll_id)  # Function to retrieve the original poll
    # print(f"original_poll: {original_poll}")

    # correct_choice = original_poll.correct_option_id
    # print(f"correct_choice: {correct_choice}")

    # if user_choice == 2:
    #     print("Correct answer!")
    # else:
    #     print("Wrong answer, try again!")
    # print(f"context: {context}")
    # # Access the selected options
    # if update.poll_answer:
    #     # Access the selected options
    #     selected_options = update.poll_answer.option_ids

    #     # Print the selected options
    #     print(f"User {update.effective_user.id} chose options: {selected_options}")

    # await context.bot.stop_poll(quiz_data["chat_id"], quiz_data["message_id"])
    # # if answer != 4:
    # #     return quiz(update, context)

    # # if update.poll.is_closed:
    # #     return
    # # if update.poll.total_voter_count == TOTAL_VOTER_COUNT:
    # #     try:
    # #         quiz_data = context.bot_data[update.poll.id]
    # #     # this means this poll answer update is from an old poll, we can't stop it then
    # #     except KeyError:
    # #         return
    # #     await context.bot.stop_poll(quiz_data["chat_id"], quiz_data["message_id"])
    if update.poll.is_closed:
        return
    if update.poll.total_voter_count == TOTAL_VOTER_COUNT:
        try:
            quiz_data = context.bot_data[update.poll.id]
        # this means this poll answer update is from an old poll, we can't stop it then
        except KeyError:
            return

        # Check if the user submitted an answer
        if update.poll_answer:
            # Access the selected options
            selected_options = update.poll_answer.option_ids

            # Print the selected options
            print(f"User {update.effective_user.id} chose options: {selected_options}")

        # Continue with stopping the poll as needed
        await context.bot.stop_poll(quiz_data["chat_id"], quiz_data["message_id"])


async def preview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ask user to create a poll and display a preview of it"""
    # using this without a type lets the user chooses what he wants (quiz or poll)
    button = [[KeyboardButton("Press me!", request_poll=KeyboardButtonPollType())]]
    message = "Press the button to let the bot generate a preview for your poll"
    # using one_time_keyboard to hide the keyboard
    await update.effective_message.reply_text(
        message, reply_markup=ReplyKeyboardMarkup(button, one_time_keyboard=True)
    )


async def receive_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display a help message"""
    await update.message.reply_text("Use /quiz, /poll or /preview to test this bot.")


def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6887127186:AAG525kpcNRTizg2LKM7BNfljDUT_k5tQ9M").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("poll", poll))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("preview", preview))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(MessageHandler(filters.POLL, receive_poll))
    application.add_handler(PollAnswerHandler(receive_poll_answer))
    application.add_handler(PollHandler(receive_quiz_answer))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()