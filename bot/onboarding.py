from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update, Poll
from telegram.ext import (ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler,
                          PollAnswerHandler, CallbackContext)
from utils.redis_cache import get_from_cache, set_in_cache
import json
import re
from utils.logger import setup_logger

logger = setup_logger(__name__, 'bot.log')
# Define states
(EMAIL, PHONE, PHOTO, COUNTRY, BIO, BIRTHDAY, CONFIRMATION, CHANGE_INFO, CHANGE_INFO_INPUT, 
WATCH_VIDEO, QUIZ, VIDEO, ONBOARDING_COMPLETE, ADMIN_APPROVAL) = range(14)


# Email validation regex
EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# Quiz questions and answers
# Quiz questions and answers
quiz_questions = [
    ("What is the capital of France?", ["London", "Paris", "Berlin", "Rome"], 1),
    ("Which planet is known as the Red Planet?", ["Earth", "Mars", "Jupiter", "Venus"], 1),
    ("Who wrote 'Hamlet'?", ["William Shakespeare", "Charles Dickens", "Leo Tolstoy", "Mark Twain"], 0),
    ("What is the largest ocean on Earth?", ["Atlantic Ocean", "Indian Ocean", "Pacific Ocean", "Arctic Ocean"], 2),
    ("In which year did the Titanic sink?", ["1912", "1910", "1914", "1908"], 0)
]


# Video links
video_links = [
    "https://drive.google.com/file/d/1zPbDa9B_WOHNW4xnEChcnaW9Ffl3TyQh/view?usp=sharing",
    "https://drive.google.com/file/d/1CaaYjirmCdosSQU6MDdFjMMLdbRrOGvf/view?usp=sharing",
    "https://drive.google.com/file/d/1ez_jCHtMTsIBwCYQ2dybSU21Wrv3X-yZ/view?usp=sharing",
    "https://drive.google.com/file/d/12rpnx-YsA-e2YKLwheqaUlahRXwKXBpd/view?usp=drive_link",
    "https://drive.google.com/file/d/1LXiN5r-LFBGalhaPYwW7lJSuxtkBz_Jx/view?usp=drive_link"
    
]

# Start function with modifications
def start(update: Update, context: CallbackContext) -> int:
    user_id = str(update.message.from_user.id)
    user_first_name = update.message.from_user.first_name
    user_data = get_from_cache(user_id)

    if user_data:
        user_data_json = json.loads(user_data)
        if user_data_json.get('status') == 'CONFIRMED':
            update.message.reply_text(f"Welcome back, {user_first_name}!")
        elif user_data_json.get('status') == 'PENDING':
            update.message.reply_text(f"Hi {user_first_name}, your registration is still pending.")
    else:
        update.message.reply_text(f'Welcome {user_first_name}! Please enter your email:')
        return EMAIL

# Email handler with validation
def collect_email(update: Update, context: CallbackContext) -> int:
    email = update.message.text
    if re.fullmatch(EMAIL_REGEX, email):
        context.user_data['email'] = email
        update.message.reply_text('Great! Now, please send me your phone number.')
        return PHONE
    else:
        update.message.reply_text('Invalid email. Please enter a valid email address:')
        return EMAIL

# Phone handler with basic validation
def collect_phone(update: Update, context: CallbackContext) -> int:
    phone = update.message.text
    if phone.isdigit() and 7 <= len(phone) <= 15:
        context.user_data['phone'] = phone
        update.message.reply_text('Thanks! Lastly, tell me a bit about yourself.')
        return BIO
    else:
        update.message.reply_text('Invalid phone number. Please enter a valid phone number:')
        return PHONE

# Bio handler
def collect_bio(update, context):
    context.user_data['bio'] = update.message.text
    update.message.reply_text("Please upload your headshot/photo:")
    return PHOTO

# Photo handler
def photo(update, context):
    if update.message.photo:
        photo_file = update.message.photo[-1]
        context.user_data['photo'] = photo_file.file_id  # Store the file ID
        update.message.reply_text("Please enter your country:")
        return COUNTRY
    else:
        update.message.reply_text("Please upload a valid headshot/photo.")
        return PHOTO

# Country handler
def country_handler(update, context):
    context.user_data['country'] = update.message.text
    update.message.reply_text("Please enter your birthday (DD-MM-YYYY):")
    return BIRTHDAY

# Birthday handler
def birthday_handler(update, context):
    context.user_data['birthday'] = update.message.text
    return confirmation(update, context)

# Confirmation handler
# Confirmation handler
def confirmation(update, context):
    try:
        details = "\n".join([f"{key}: {value}" for key, value in context.user_data.items() if key != 'photo'])
        
        photo_id = context.user_data.get('photo')
        # Check if update is a CallbackQuery and extract the message
        message = update.callback_query.message if update.callback_query else update.message
        if message:
            if photo_id:
                message.reply_photo(photo=photo_id)  # Send the photo by its file ID
            message.reply_text(f"Please confirm your details:\n{details}")
            keyboard = [[InlineKeyboardButton("Yes", callback_data='yes'),
                        InlineKeyboardButton("No", callback_data='no')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message.reply_text('Is this information correct?', reply_markup=reply_markup)
        else:
            # Log or handle the case where message is None
            print("Error: Message object is None in confirmation")
        return CONFIRMATION
    except AttributeError as e:
        print(f"AttributeError in confirmation: {e}")

# CallbackQuery handler for confirmation
def button(update, context):
    query = update.callback_query
    query.answer()

    if query.data == 'yes':
        query.edit_message_text(text="Registration complete. Starting onboarding...")
        return start_onboarding(update, context)
    elif query.data == 'no':
        keyboard = [
            [InlineKeyboardButton("Email", callback_data='change_email')],
            [InlineKeyboardButton("Phone", callback_data='change_phone')],
            [InlineKeyboardButton("Bio", callback_data='change_bio')],
            [InlineKeyboardButton("Country", callback_data='change_country')],
            [InlineKeyboardButton("Birthday", callback_data='change_birthday')],
            [InlineKeyboardButton("Photo", callback_data='change_photo')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text('Which information would you like to change?', reply_markup=reply_markup)
        return CHANGE_INFO
    else:
        # Handle unexpected callback data
        query.edit_message_text("Unexpected option. Please try again.")
        return CONFIRMATION

# Handler for changing information
def change_info(update, context):
    query = update.callback_query
    query.answer()
    field = query.data.split('_')[-1]

    # Ask the user for the new information
    context.user_data['update_field'] = field  # Store the field being updated
    query.edit_message_text(f"Please enter your new {field}:")
    return CHANGE_INFO_INPUT

# Handler for receiving the new information input
def change_info_input(update, context):
    user_input = update.message.text
    field = context.user_data.pop('update_field', None)

    if field:
        context.user_data[field] = user_input  # Update the field in context.user_data

    # Return to the confirmation step
    return confirmation(update, context)

# Onboarding start handler
def start_onboarding(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    context.user_data['video_index'] = 0
    return send_video_message(update, context)

# Send video message handler
def send_video_message(update: Update, context: CallbackContext) -> int:
    video_index = context.user_data.get('video_index', 0)
    if video_index < len(video_links):
        # Send the video link
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Please watch this video: {video_links[video_index]}")
        # After sending the video, add a button to proceed to the quiz
        keyboard = [[InlineKeyboardButton("I've watched the video, proceed to the quiz", callback_data='proceed_to_quiz')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Click the button when you're ready to proceed to the quiz.", reply_markup=reply_markup)
        return WATCH_VIDEO  # Define WATCH_VIDEO state if not already defined
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Congratulations, you've completed all the videos and quizzes!")
        return ONBOARDING_COMPLETE
def proceed_to_quiz_handler(update: Update, context: CallbackContext) -> int:
    return quiz_handler(update, context)


def quiz_handler(update, context):
    video_index = context.user_data.get('video_index', 0)
    question, options, correct_option_index = quiz_questions[video_index]
    keyboard = [[InlineKeyboardButton(option, callback_data=str(index == correct_option_index)) for index, option in enumerate(options)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text=question, reply_markup=reply_markup)
    return QUIZ


# Handler for quiz answer - Button based
def quiz(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    video_index = context.user_data.get('video_index', 0)

    if query.data == 'True':  # Correct answer
        context.user_data['video_index'] += 1
        return VIDEO if video_index + 1 < len(video_links) else ONBOARDING_COMPLETE
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Incorrect answer. Try again.")
        return quiz_handler(update, context)  # Re-send the same quiz question






# Admin approval handler
def admin_approval_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    
    # Parse the callback data to get the user_id and action
    user_id, action = query.data.split('_')
    
    if action == "approve":
        # Admin selects a planet, moon, and satellite for the user
        # This is a placeholder, you'll need to implement the actual logic
        #assign_planet_moon_satellite_to_user(user_id)
        
        # Make an API call to the verify user endpoint to approve the user
        #verify_user(user_id, True)  # Assuming this function takes user_id and a boolean for approval
        
        # Notify the user of their acceptance
        context.bot.send_message(chat_id=user_id, text="Congratulations, your registration has been approved!")
    elif action == "deny":
        # Make an API call to the verify user endpoint to deny the user
        #verify_user(user_id, False)  # Assuming this function takes user_id and a boolean for approval
        
        # Notify the user of their rejection
        context.bot.send_message(chat_id=user_id, text="Your registration has been denied.")
    
    return ConversationHandler.END

def onboarding_complete(update, context):
    update.message.reply_text("Onboarding complete! Welcome to the team!")
    return ConversationHandler.END

# Cancel handler
def cancel(update, context):
    update.message.reply_text('Operation cancelled.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Conversation handler
def conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            EMAIL: [MessageHandler(Filters.text & ~Filters.command, collect_email)],
            PHONE: [MessageHandler(Filters.text & ~Filters.command, collect_phone)],
            PHOTO: [MessageHandler(Filters.photo, photo)],
            COUNTRY: [MessageHandler(Filters.text & ~Filters.command, country_handler)],
            BIO: [MessageHandler(Filters.text & ~Filters.command, collect_bio)],
            BIRTHDAY: [MessageHandler(Filters.text & ~Filters.command, birthday_handler)],
            CONFIRMATION: [CallbackQueryHandler(button), MessageHandler(Filters.text & ~Filters.command, confirmation)],
            CHANGE_INFO: [CallbackQueryHandler(change_info)],
            CHANGE_INFO_INPUT: [MessageHandler(Filters.text & ~Filters.command, change_info_input)],
            WATCH_VIDEO: [CallbackQueryHandler(proceed_to_quiz_handler, pattern='proceed_to_quiz')],
            QUIZ: [CallbackQueryHandler(quiz)],
            VIDEO: [MessageHandler(Filters.text & ~Filters.command, send_video_message)],
            ONBOARDING_COMPLETE: [MessageHandler(Filters.text & ~Filters.command, onboarding_complete)],
            ADMIN_APPROVAL: [CallbackQueryHandler(admin_approval_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
