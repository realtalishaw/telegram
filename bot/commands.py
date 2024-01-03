from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, CallbackContext
from utils.redis_cache import get_from_cache, set_in_cache
from utils.helper_functions import is_user_allowed
import re
from api.user import create_user
from api.task import create_task
from api.project import create_project
import json
import re


def help(update, context):
    #if not is_user_allowed(update, context):
        #return
    help_text = ("List of commands:\n"
                 "/start - Initiate interaction with TheoBot\n"
                 "/help - Get a list of available commands\n"
                 "/project - Add new project to Jira\n"
                 "/assignrole - Assign roles to users\n"
                 "/createtask - Create a new task within a project\n"
                 "/calendar - View the Theometrics Calendar\n"
                 "/addevent - Add Event to the Theometrics Calendar\n"
                 "/rsvp - RSVP for calendar event\n"
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
    if not is_user_allowed(update, context):
        return
    update.message.reply_text('User role assignment is not yet implemented.')

def project(update, context):
    # if not is_user_allowed(update, context):
    #     return
    update.message.reply_text('Example: /project "name example" "description example" "moonID"')
    # get params
    params = update.message.text
    # remove the /createtask command
    modified_text = params.replace('/project', '')
    # Split the input string into individual components
    components = re.findall(r'"(.*?)"', modified_text)
    # Check if there are enough components
    if len(components) >= 3:
      # Create a dictionary with the desired keys and values
      payload = {
        "name": components[0],
        "description": components[1],
        "projectLead": "627afe2219b1290068294114",
        "status": "ACTIVE",
        "moonID": components[2],
      }

      # Convert the dictionary to a JSON string
      json_payload = json.dumps(payload, indent=2)

      # Now, you can parse the decoded JSON string
      parsed_body = json.loads(json_payload) if isinstance(json_payload, str) else json_payload
    
      # Print the JSON payload
      print(parsed_body)
      try:
        response = create_project(parsed_body)
        print(response)
        if response == None:
          update.message.reply_text("An error occurred while creating the Jira project. Check moonID.")
        else:
           update.message.reply_text("New project added to Jira!")
      except:
        update.message.reply_text("An error occurred while creating the Jira project. Check moonID.")
    else:
      update.message.reply_text("You didn't supply enough parameters in the /project command. Try again.")

def createtask(update, context):
    # if not is_user_allowed(update, context):
    #     return
    update.message.reply_text('Example: /createtask "title example" "description example" "projectID" "notes example"')
    # get params
    params = update.message.text
    # remove the /createtask command
    modified_text = params.replace('/createtask', '')
    # Split the input string into individual components
    components = re.findall(r'"(.*?)"', modified_text)
    # Check if there are enough components
    if len(components) >= 4:
      # Create a dictionary with the desired keys and values
      payload = {
          "title": components[0],
          "description": components[1],
          "projectID": components[2],
          "taskType": "10008",
          "notes": components[3],
          "status": "TO_DO"
      }

      # Convert the dictionary to a JSON string
      json_payload = json.dumps(payload, indent=2)
      # Assuming 'body' is your input variable
      # decoded_body = json.loads(body.encode().decode('unicode_escape'))

      # Now, you can parse the decoded JSON string
      parsed_body = json.loads(json_payload) if isinstance(json_payload, str) else json_payload
    
      # Print the JSON payload
      print(parsed_body)
      try:
        response = create_task(parsed_body)
        print(response)
        if response == None:
          update.message.reply_text("An error occurred adding the Jira task. Check projectID.")
        else:
           update.message.reply_text("New task added to Jira!")
      except:
        update.message.reply_text("An error occurred adding the Jira task. Check projectID.")
    else:
      update.message.reply_text("You didn't supply enough parameters in the /createtask command. Try again.")

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