from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from utils.logger import setup_logger
from bot.onboarding import conversation_handler  
from bot.commands import help, project, assignrole, createtask, assigntask, status, calendar, addevent, rsvp, settings, feedback
from bot.admin_approval import admin_approval_conversation_handler

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
    dp.add_handler(conversation_handler())
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("project", project))
    dp.add_handler(CommandHandler("assignrole", assignrole))
    dp.add_handler(CommandHandler("createtask", createtask))
    dp.add_handler(CommandHandler("assigntask", assigntask))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("calendar", calendar))
    dp.add_handler(CommandHandler("addevent", addevent))
    dp.add_handler(CommandHandler("rsvp", rsvp))
    dp.add_handler(CommandHandler("settings", settings))
    dp.add_handler(CommandHandler("feedback", feedback))
    dp.add_handler(admin_approval_conversation_handler())


    # Log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
