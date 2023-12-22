# api/user.py
import json
from utils.api_call import api_call
from utils.redis_cache import set_in_cache, delete_from_cache
from utils.logger import setup_logger
logger = setup_logger(__name__, 'bot.log')


def get_user(user_id):
    logger.info("API Request, get_user")
    user_data = api_call(f"users/{user_id}", method='GET')
    return user_data

def create_user(user_data):
    logger.info("API Request, create_user")
    response = api_call("users", method='POST', data=user_data)

    # Check if the response contains 'createUser' key and 'id' field
    if response and 'createUser' in response and 'id' in response['createUser']:
        user_info = response['createUser']
        user_id = user_info['id']
        cache_key = f"user:{user_id}"

        # Serialize and cache the user data
        set_in_cache(cache_key, json.dumps(user_info))

    return response


def update_user(user_id, user_data):
    logger.info("API Request, update_user")
    cache_key = f"user:{user_id}"
    response = api_call(f"users/{user_id}", method='PUT', data=user_data)
    if response:
        set_in_cache(cache_key, response)
    return response

def verify_user(user_id, user_data):
    logger.info("API Request, verify_user")
    cache_key = f"user:{user_id}"
    response = api_call(f"users/verify/{user_id}", method='POST', data=user_data)
    if response:
        set_in_cache(cache_key, response)
    return response


def delete_user(user_id):
    logger.info("API Request, delete_user")
    cache_key = f"user:{user_id}"
    response = api_call(f"users/{user_id}", method='DELETE')
    if response:
        delete_from_cache(cache_key)
    return response

def get_all_users():
    logger.info("API Request, get_all_users")
    users = api_call("users", method='GET')
    return users
