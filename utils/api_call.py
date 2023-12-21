# utils/api_call.py

import requests
from utils.logger import setup_logger
logger = setup_logger(__name__, 'bot.log')

API_BASE_URL = "https://dqpllfj7tb.execute-api.us-east-1.amazonaws.com/dev"

def api_call(endpoint, method='GET', data=None, params=None):
    url = f"{API_BASE_URL}/{endpoint}"
    print(f"API call: {url}")
    headers = {'Content-Type': 'application/json'}

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, json=data)

        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        # Log error and handle it as necessary
        print(f"API Request failed: {e}")
        logger.info(f"API {method} request for {endpoint} failed with error {e}")
        return None
