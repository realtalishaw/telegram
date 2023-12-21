# api/projects.py

from utils.api_call import api_call
from utils.redis_cache import get_from_cache, set_in_cache, delete_from_cache
from utils.logger import setup_logger
logger = setup_logger(__name__, 'bot.log')



def get_all_projects():
    logger.info("API Request, get_all_projects")
    projects = api_call("projects", method='GET')
    
          

def create_project(project_data):
    logger.info("API Request, create_project")
    response = api_call("projects", method='POST', data=project_data)
    return response

def get_project(project_id):
    logger.info("API Request, get_project")
    project_data = api_call(f"projects/{project_id}", method='GET')
    return project_data

def update_project(project_id, project_data):
    logger.info("API Request, update_project")
    response = api_call(f"projects/{project_id}", method='PUT', data=project_data)
    return response

def delete_project(project_id):
    logger.info("API Request, delete_project")
    response = api_call(f"projects/{project_id}", method='DELETE')
    return response

def get_projects_by_moon(moon_id):
    logger.info("API Request, get_projects_by_moon")
    projects = api_call(f"projects/byMoon/{moon_id}", method='GET')
    return projects
