# api/files.py

from utils.api_call import api_call
from utils.logger import setup_logger
logger = setup_logger(__name__, 'bot.log')

def get_all_files():
    logger.info("API Request, get_all_files")
    files = api_call("files", method='GET')
    return files

def create_file(file_data):
    logger.info("API Request, create_file")
    response = api_call("files", method='POST', data=file_data)
    return response

def get_file(file_id):
    logger.info("API Request, get_file")
    file_data = api_call(f"files/{file_id}", method='GET')
    return file_data

def update_file(file_id, file_data):
    logger.info("API Request, update_file")
    response = api_call(f"files/{file_id}", method='PUT', data=file_data)
    return response

def delete_file(file_id):
    logger.info("API Request, delete_file")
    response = api_call(f"files/{file_id}", method='DELETE')
    return response

def get_files_by_moon(moon_id):
    logger.info("API Request, get_files_by_moon")
    files = api_call(f"files/moon/{moon_id}", method='GET')
    return files

def get_files_by_task(task_id):
    logger.info("API Request, get_files_by_task")
    files = api_call(f"files/task/{task_id}", method='GET')
    return files

def get_files_by_project(project_id):
    logger.info("API Request, get_files_by_project")
    files = api_call(f"files/project/{project_id}", method='GET')
    return files
