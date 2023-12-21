# api/tasks.py

from utils.api_call import api_call
from utils.logger import setup_logger
logger = setup_logger(__name__, 'bot.log')

def get_all_tasks():
    logger.info("API Request, get_all_tasks")
    tasks = api_call("tasks", method='GET')
    return tasks

def create_task(task_data):
    logger.info("API Request, create_task")
    response = api_call("tasks", method='POST', data=task_data)
    return response

def get_task(task_id):
    logger.info("API Request, get_task")
    task_data = api_call(f"tasks/{task_id}", method='GET')
    return task_data

def update_task(task_id, task_data):
    logger.info("API Request, update_task")
    response = api_call(f"tasks/{task_id}", method='PUT', data=task_data)
    return response

def delete_task(task_id):
    logger.info("API Request, delete_task")
    response = api_call(f"tasks/{task_id}", method='DELETE')
    return response

def get_tasks_by_project(project_id):
    logger.info("API Request, get_tasks_by_project")
    tasks = api_call(f"tasks/byProject/{project_id}", method='GET')
    return tasks
