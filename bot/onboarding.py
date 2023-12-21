from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, PollAnswerHandler
from telegram import Poll
from utils.redis_cache import get_from_cache, set_in_cache
import json

# Define states
EMAIL, PHONE, PHOTO, COUNTRY, BIO, BIRTHDAY, CONFIRMATION, CHANGE_INFO, CHANGE_INFO_INPUT, \
VIDEO_1, QUIZ_1, VIDEO_2, QUIZ_2, VIDEO_3, QUIZ_3, VIDEO_4, QUIZ_4, VIDEO_5, QUIZ_5, ONBOARDING_COMPLETE, RECEIVE_POLL_ANSWER = range(21)


# Start registration
def start(update, context):
    user_id = str(update.effective_user.id)
    cache_key = f"user:{user_id}"
    cached_user_data = get_from_cache(cache_key)
    user_fName = update.message.from_user.first_name

    if cached_user_data:
        user_data = json.loads(cached_user_data)
        if user_data.get('status') == 'CONFIRMED':
            update.message.reply_text(f"Welcome back, {user_fName}!")
        elif user_data.get('status') == 'PENDING':
            update.message.reply_text(f"Hi {user_fName}, your registration is still pending.")
    else:
        keyboard = [[InlineKeyboardButton("Register", callback_data='register')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(f"Welcome {user_fName}!I'm Theo bot! Let's get you registered.", reply_markup=reply_markup)

def start_registration(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Please enter your email address:")
    return EMAIL

# Email handler
def email(update, context):
    context.user_data['email'] = update.message.text
    update.message.reply_text("Please enter your phone number:")
    return PHONE

# Phone handler
def phone(update, context):
    context.user_data['phone'] = update.message.text
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
def country(update, context):
    context.user_data['country'] = update.message.text
    update.message.reply_text("Please tell us about yourself (your bio):")
    return BIO

# Bio handler
def bio(update, context):
    context.user_data['bio'] = update.message.text
    update.message.reply_text("Please enter your birthday (DD-MM-YYYY):")
    return BIRTHDAY

# Birthday handler
def birthday(update, context):
    context.user_data['birthday'] = update.message.text
    return confirmation(update, context)

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
            # Add buttons for other fields as needed
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text('Which information would you like to change?', reply_markup=reply_markup)
        return CHANGE_INFO

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

def start_onboarding(update, context):
    try:
        # Check if update is a CallbackQuery and extract the message
        message = update.callback_query.message if update.callback_query else update.message
        if message:
            print(f"Onboarding Message: {message}")
            message.reply_text("Welcome to the onboarding process!")
            # return video_1(update, context)
        else:
            # Log or handle the case where message is None
            print("Error: Message object is None in start_onboarding")
        return quiz_1(update, context)
    except AttributeError as e:
        print(f"AttributeError in start_onboarding: {e}")


def video_1(update, context):
    message = update.callback_query.message if update.callback_query else update.message
    video_url = "https://drive.google.com/file/d/1zPbDa9B_WOHNW4xnEChcnaW9Ffl3TyQh/view?usp=sharing"
    message.reply_text(f"Please watch this video:\n{video_url}")
    return quiz_1(update, context)

def quiz_1(update, context):
    message = update.callback_query.message if update.callback_query else update.message
    video_url = "https://drive.google.com/file/d/1zPbDa9B_WOHNW4xnEChcnaW9Ffl3TyQh/view?usp=sharing"
    message.reply_text(f"Please watch this video:\n{video_url}")
    print("quiz1 being initialized...")
    print(f"update {update} context {context}")
    # context.bot.send_poll(chat_id=update.effective_chat.id, question="Dummy question for Video 1?",
    #                       options=["Option 1", "Option 2", "Option 3", "Option 4"],
    #                       type='quiz', correct_option_id=0)
    q = 'What is the capital of Italy?'
    answers = ['Rome', 'London', 'Amsterdam']
    print(f"update.effective_chat.id: {update.effective_chat.id}")
    message = context.bot.send_poll(chat_id=update.effective_chat.id, question=q, options=answers, type=Poll.QUIZ, correct_option_id=0)
    print(f"messsage: {message}")
    payload = {
        message.poll.id: {
            "questions": q,
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "answers": 0,
        }
    }
    context.bot_data.update(payload)
    print(f"User answer: {update.poll_answer}")
    return receive_poll_answer(update, context)

async def receive_poll_answer(update, context):
    answer = update.poll_answer
    print(f"answer: {answer}")
    answered_poll = context.bot_data[answer.poll_id]
    print(f"answered_poll {answered_poll}")
    if update.poll_answer == 0:
        return quiz_2(update, context)
    else:
        return quiz_1(update, context)

def video_2(update, context):
    message = update.callback_query.message if update.callback_query else update.message
    video_url = "https://drive.google.com/file/d/1CaaYjirmCdosSQU6MDdFjMMLdbRrOGvf/view?usp=sharing"
    message.reply_text(f"Please watch this video:\n{video_url}")
    return QUIZ_2

def quiz_2(update, context):
    message = update.callback_query.message if update.callback_query else update.message
    video_url = "https://drive.google.com/file/d/1CaaYjirmCdosSQU6MDdFjMMLdbRrOGvf/view?usp=sharing"
    message.reply_text(f"Please watch this video:\n{video_url}")

    context.bot.send_poll(chat_id=update.effective_chat.id, question="Dummy question for Video 2?",
                          options=["Option 1", "Option 2", "Option 3", "Option 4"],
                          type='quiz', correct_option_id=1)
    payload = {
        message.poll.id: {
            "questions": q,
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "answers": 0,
        }
    }
    context.bot_data.update(payload)
    return VIDEO_3

def video_3(update, context):
    message = update.callback_query.message if update.callback_query else update.message
    video_url = "https://drive.google.com/file/d/1ez_jCHtMTsIBwCYQ2dybSU21Wrv3X-yZ/view?usp=sharing"
    message.reply_text(f"Please watch this video:\n{video_url}")
    return QUIZ_3

def quiz_3(update, context):
    context.bot.send_poll(chat_id=update.effective_chat.id, question="Dummy question for Video 3?",
                          options=["Option 1", "Option 2", "Option 3", "Option 4"],
                          type='quiz', correct_option_id=2)
    return VIDEO_4

def video_4(update, context):
    message = update.callback_query.message if update.callback_query else update.message
    video_url = "https://drive.google.com/file/d/12rpnx-YsA-e2YKLwheqaUlahRXwKXBpd/view?usp=drive_link"
    message.reply_text(f"Please watch this video:\n{video_url}")
    return QUIZ_4

def quiz_4(update, context):
    context.bot.send_poll(chat_id=update.effective_chat.id, question="Dummy question for Video 4?",
                          options=["Option 1", "Option 2", "Option 3", "Option 4"],
                          type='quiz', correct_option_id=3)
    return VIDEO_5

def video_5(update, context):
    message = update.callback_query.message if update.callback_query else update.message
    video_url = "https://drive.google.com/file/d/1LXiN5r-LFBGalhaPYwW7lJSuxtkBz_Jx/view?usp=drive_link"
    message.reply_text(f"Please watch this video:\n{video_url}")
    return QUIZ_5

def quiz_5(update, context):
    context.bot.send_poll(chat_id=update.effective_chat.id, question="Dummy question for Video 5?",
                          options=["Option 1", "Option 2", "Option 3", "Option 4"],
                          type='quiz', correct_option_id=0)
    return ONBOARDING_COMPLETE

def onboarding_complete(update, context):
    message = update.callback_query.message if update.callback_query else update.message
    message.reply_text("Onboarding complete! Welcome to the team!")
    return ConversationHandler.END



# Cancel handler
def cancel(update, context):
    message = update.callback_query.message if update.callback_query else update.message
    message.reply_text('Registration cancelled.', reply_markup=ReplyMarkupRemove())
    return ConversationHandler.END

# Create conversation handler
def conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      CallbackQueryHandler(start_registration, pattern='^register$')],
        states={
            EMAIL: [MessageHandler(Filters.text & ~Filters.command, email)],
            PHONE: [MessageHandler(Filters.text & ~Filters.command, phone)],
            PHOTO: [MessageHandler(Filters.photo, photo)],
            COUNTRY: [MessageHandler(Filters.text & ~Filters.command, country)],
            BIO: [MessageHandler(Filters.text & ~Filters.command, bio)],
            BIRTHDAY: [MessageHandler(Filters.text & ~Filters.command, birthday)],
            CONFIRMATION: [CallbackQueryHandler(button)],
            CHANGE_INFO: [CallbackQueryHandler(change_info)],
            CHANGE_INFO_INPUT: [MessageHandler(Filters.text & ~Filters.command, change_info_input)],
            VIDEO_1: [CommandHandler('video_1', video_1)],
            QUIZ_1: [MessageHandler(Filters.text & ~Filters.command, quiz_1)],
            VIDEO_2: [MessageHandler(Filters.text & ~Filters.command, video_2)],
            QUIZ_2: [PollAnswerHandler(quiz_2)],
            VIDEO_3: [MessageHandler(Filters.text & ~Filters.command, video_3)],
            QUIZ_3: [PollAnswerHandler(quiz_3)],
            VIDEO_4: [MessageHandler(Filters.text & ~Filters.command, video_4)],
            QUIZ_4: [PollAnswerHandler(quiz_4)],
            VIDEO_5: [MessageHandler(Filters.text & ~Filters.command, video_5)],
            QUIZ_5: [PollAnswerHandler(quiz_5)],
            ONBOARDING_COMPLETE: [MessageHandler(Filters.text & ~Filters.command, onboarding_complete)],
            # RECEIVE_POLL_ANSWER: [MessageHandler(Filters.poll, receive_poll_answer, run_async=True)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
