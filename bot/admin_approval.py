from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CallbackQueryHandler, CallbackContext
from api.user import update_user, verify_user

# Define states for the conversation
(ADMIN_APPROVAL, ASSIGN_ROLE, ASSIGN_PLANET, ASSIGN_MOON, ASSIGN_SATELLITE, FINAL_CONFIRMATION) = range(6)

# Sample data (Replace with your actual data source)
planets = ["Earth", "Mars", "Jupiter"]
moons = ["Moon", "Europa", "Titan"]
satellites = ["ISS", "Hubble", "Voyager"]

# Function to send user data to the admin for approval
def send_data_to_admin(context, user_data):
    print("++++++++++++++++SENT TO ADMIN++++++++++++++++++++++++")
    admin_id = '5915765775'  # Replace with your admin's Telegram ID
    details = "\n".join([f"{key}: {value}" for key, value in user_data.items() if key != 'photo'])
    
    keyboard = [
        [InlineKeyboardButton("Approve", callback_data=f"approve_{user_data['id']}")],
        [InlineKeyboardButton("Deny", callback_data=f"deny_{user_data['id']}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=admin_id, text=f"New user registration:\n{details}", reply_markup=reply_markup)

# Handler for admin approval
def admin_approval_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    
    user_id, action = query.data.split('_')
    
    if action == "approve":
        context.user_data['approved_user_id'] = user_id
        return assign_role(update, context)
    elif action == "deny":
        context.bot.send_message(chat_id=user_id, text="Your registration has been denied.")
        return ConversationHandler.END

    return ADMIN_APPROVAL

# Function to assign role
def assign_role(update, context):
    query = update.callback_query
    query.answer()

    keyboard = [
        [InlineKeyboardButton("Member", callback_data="role_member")],
        [InlineKeyboardButton("Moderator", callback_data="role_moderator")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Select a role for the user:", reply_markup=reply_markup)
    
    return ASSIGN_PLANET

# Function to assign planet
def assign_planet(update, context):
    query = update.callback_query
    query.answer()

    keyboard = [[InlineKeyboardButton(planet, callback_data=f"planet_{planet}") for planet in planets]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Select a planet to assign:", reply_markup=reply_markup)

    return ASSIGN_MOON

# Function to assign moon
def assign_moon(update, context):
    query = update.callback_query
    query.answer()

    keyboard = [[InlineKeyboardButton(moon, callback_data=f"moon_{moon}") for moon in moons]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Select a moon to assign:", reply_markup=reply_markup)

    return ASSIGN_SATELLITE

# Function to assign satellite
def assign_satellite(update, context):
    query = update.callback_query
    query.answer()

    keyboard = [[InlineKeyboardButton(satellite, callback_data=f"satellite_{satellite}") for satellite in satellites]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Select a satellite to assign:", reply_markup=reply_markup)

    return FINAL_CONFIRMATION

# Function for final confirmation
def final_confirmation(update, context):
    query = update.callback_query
    query.answer()

    # Compile all selected options for final confirmation
    selections = context.user_data.get('selections', {})
    summary = "\n".join([f"{key}: {value}" for key, value in selections.items()])

    # Buttons for confirmation and editing
    keyboard = [
        [InlineKeyboardButton("Confirm", callback_data="confirm_final")],
        [InlineKeyboardButton("Edit Role", callback_data="edit_role")],
        [InlineKeyboardButton("Edit Planet", callback_data="edit_planet")],
        [InlineKeyboardButton("Edit Moon", callback_data="edit_moon")],
        [InlineKeyboardButton("Edit Satellite", callback_data="edit_satellite")],
        [InlineKeyboardButton("Cancel", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=f"Confirm selections:\n{summary}", reply_markup=reply_markup)

    return FINAL_CONFIRMATION

def edit_role(update, context):
    return assign_role(update, context)

def edit_planet(update, context):
    return assign_planet(update, context)

def edit_moon(update, context):
    return assign_moon(update, context)

def edit_satellite(update, context):
    return assign_satellite(update, context)

def confirm_final(update, context):
    query = update.callback_query
    query.answer()

    # Implement the API calls to update and verify the user here
    # update_user(context.user_data['approved_user_id'], context.user_data['selections'])
    # verify_user(context.user_data['approved_user_id'])

    query.edit_message_text(text="User has been updated and verified successfully.")
    return ConversationHandler.END

# Cancel handler
def cancel(update, context):
    update.message.reply_text('Operation cancelled.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Conversation handler for the admin approval process
def admin_approval_conversation_handler():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_approval_handler, pattern='^approve_|^deny_')],
        states={
            ASSIGN_ROLE: [CallbackQueryHandler(assign_planet, pattern='^role_'),
                          CallbackQueryHandler(edit_role, pattern='^edit_role')],
            ASSIGN_PLANET: [CallbackQueryHandler(assign_moon, pattern='^planet_'),
                            CallbackQueryHandler(edit_planet, pattern='^edit_planet')],
            ASSIGN_MOON: [CallbackQueryHandler(assign_satellite, pattern='^moon_'),
                          CallbackQueryHandler(edit_moon, pattern='^edit_moon')],
            ASSIGN_SATELLITE: [CallbackQueryHandler(final_confirmation, pattern='^satellite_'),
                               CallbackQueryHandler(edit_satellite, pattern='^edit_satellite')],
            FINAL_CONFIRMATION: [CallbackQueryHandler(confirm_final, pattern='^confirm_final'),
                                 CallbackQueryHandler(edit_role, pattern='^edit_role'),
                                 CallbackQueryHandler(edit_planet, pattern='^edit_planet'),
                                 CallbackQueryHandler(edit_moon, pattern='^edit_moon'),
                                 CallbackQueryHandler(edit_satellite, pattern='^edit_satellite')]
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern='^cancel')]
    )