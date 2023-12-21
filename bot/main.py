from telegram.ext import Updater
from utils.logger import setup_logger
from bot.onboarding import conversation_handler  # Import the conversation handler

logger = setup_logger(__name__, 'bot.log')
logger.info("Bot started!")

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)  

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("6887127186:AAG525kpcNRTizg2LKM7BNfljDUT_k5tQ9M")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register the conversation handler for the /start command
    dp.add_handler(conversation_handler())

    # Log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
