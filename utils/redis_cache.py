# utils/cache.py

import redis

# Initialize Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Function to get data from cache
def get_from_cache(key):
    try:
        return redis_client.get(key)
    except redis.RedisError as e:
        print(f"Redis error: {e}")
        return None  # In case of error, return None

# Function to set data in cache
def set_in_cache(key, value, timeout=3600):  # Default timeout of 1 hour
    try:
        redis_client.set(key, value, ex=timeout)
    except redis.RedisError as e:
        print(f"Redis error: {e}")

# Function to delete data from cache
def delete_from_cache(key):
    try:
        redis_client.delete(key)
    except redis.RedisError as e:
        print(f"Redis error: {e}")

# Additional functions to handle specific cache operations can be added here
