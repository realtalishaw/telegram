from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from utils.redis_cache import get_from_cache
import json

# Define states
EMAIL, PHONE, PHOTO, COUNTRY, BIO, BIRTHDAY, CONFIRMATION, CHANGE_INFO, CHANGE_INFO_INPUT = range(9)


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
        update.message.reply_text(f"Welcome {user_fName}! Let's get you registered.", reply_markup=reply_markup)

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
    details = "\n".join([f"{key}: {value}" for key, value in context.user_data.items() if key != 'photo'])
    
    photo_id = context.user_data.get('photo')
    if photo_id:
        update.message.reply_photo(photo=photo_id)  # Send the photo by its file ID

    update.message.reply_text(f"Please confirm your details:\n{details}")
    keyboard = [[InlineKeyboardButton("Yes", callback_data='yes'),
                 InlineKeyboardButton("No", callback_data='no')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Is this information correct?', reply_markup=reply_markup)
    return CONFIRMATION

# CallbackQuery handler for confirmation
def button(update, context):
    query = update.callback_query
    query.answer()

    if query.data == 'yes':
        query.edit_message_text(text="Registration complete. Starting onboarding...")
        return ConversationHandler.END
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


# Cancel handler
def cancel(update, context):
    update.message.reply_text('Registration cancelled.', reply_markup=ReplyMarkupRemove())
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
            CHANGE_INFO_INPUT: [MessageHandler(Filters.text & ~Filters.command, change_info_input)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
