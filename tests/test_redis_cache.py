from utils.redis_cache import set_in_cache, get_from_cache, delete_from_cache

def test_redis_operations():
    # Test setting a value in cache
    key = "userName"
    value = "realtalishawhite"
    set_in_cache(key, value)
    print(f"Set {key} in cache with value: {value}")

    # Test getting the value from cache
    cached_value = get_from_cache(key)
    if cached_value:
        print(f"Retrieved {key} from cache with value: {cached_value.decode('utf-8')}")
    else:
        print(f"Failed to retrieve {key} from cache.")

    # Test deleting the value from cache
    delete_from_cache(key)
    print(f"Deleted {key} from cache")

    # Verify deletion
    if not get_from_cache(key):
        print(f"Successfully verified deletion of {key} from cache.")
    else:
        print(f"Failed to delete {key} from cache.")

if __name__ == "__main__":
    test_redis_operations()
