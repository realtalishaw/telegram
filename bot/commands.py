from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, CallbackContext
from utils.redis_cache import get_from_cache, set_in_cache
from utils.helper_functions import is_user_allowed
import re
from api.user import create_user
from api.task import create_task
import json

def help(update, context):
    #if not is_user_allowed(update, context):
        #return
    help_text = ("List of commands:\n"
                 "/start - Initiate interaction with TheoBot\n"
                 "/help - Get a list of available commands\n"
                 "/project - Add new project to Jira\n"
                 "/assignrole - Assign roles to users\n"
                 "/createtask - Create a new task within a project\n"
                 "/assigntask - Assign a task to a team member\n"
                 "/status - Check the status of a task\n"
                 "/calendar - View the Theometrics Calendar\n"
                 "/addevent - Add Event to the Theometrics Calendar\n"
                 "/rsvp - RSVP for calendar event\n"
                 "/settings - View or Edit Account Settings\n"
                 "/feedback - Provide feedback about the bot\n"
                 "More features coming soon!")
    update.message.reply_text(help_text)



def button(update, context):
    query = update.callback_query
    query.answer()
    if query.data == 'show_bevis':
        query.edit_message_text(text="Selected option: Show me your Bevis")
    elif query.data == 'create_bevis':
        query.edit_message_text(text="Selected option: Create New Bevis")


def assignrole(update, context):
    
    #if not is_user_allowed(update, context):
        #return
    update.message.reply_text('User role assignment is not yet implemented.')

def project(update, context):
    # get params
    params = update.message.text
    # remove the /createtask command
    modified_text = params.replace('/project', '')
    # Split the input string into individual components
    components = modified_text.split()

    update.message.reply_text('Creating a new project is not yet implemented.')

def createtask(update, context):
    # get params
    params = update.message.text
    # remove the /createtask command
    modified_text = params.replace('/createtask', '')
    # Split the input string into individual components
    components = modified_text.split()

    # Create a dictionary with the desired keys and values
    payload = {
        "title": components[0],
        "description": components[1],
        "assignee": components[2],
        "projectID": components[3],
        "dueDate": "2023-12-25T01:14:59.142Z",  # You need to format the dueDate as needed
        "taskType": components[5],
        "notes": components[6],
        "status": components[7]
    }

    # Convert the dictionary to a JSON string
    json_payload = json.dumps(payload, indent=2)

    # Print the JSON payload
    print(json_payload)
    create_task(json_payload)
    update.message.reply_text('Creating a new task initialized...')

def assigntask(update, context):
    #if not is_user_allowed(update, context):
        #return
    update.message.reply_text('Assigning a task is not yet implemented.')

def status(update, context):
    #if not is_user_allowed(update, context):
        #return
    update.message.reply_text('Checking task status is not yet implemented.')

def feedback(update, context):
    #if not is_user_allowed(update, context):
        #return
    update.message.reply_text('Feedback mechanism is not yet implemented.')

def calendar(update, context):
    #if not is_user_allowed(update, context):
        #return
    update.message.reply_text('Viewing the calendar is not yet implemented.')

def addevent(update, context):
    #if not is_user_allowed(update, context):
        #return
    update.message.reply_text('Submitting an event is not yet implemented.')

def rsvp(update, context):
    #if not is_user_allowed(update, context):
        #return
    update.message.reply_text('RSVP to an event is not yet implemented.')


def settings(update, context):
    #if not is_user_allowed(update, context):
        #return
    update.message.reply_text('Settings are not yet implemented.')

def feedback(update, context):
    #if not is_user_allowed(update, context):
        #return
    update.message.reply_text('Feedback functionality will be implemented.')