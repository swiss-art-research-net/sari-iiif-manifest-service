class Cache:

    def __init__(self, path: str):
        self.cacheStorage = {}

    def cache(self, func):
        def wrapper(*args, **kwargs):
            key = func.__name__ + str(args) + str(kwargs)
            if key in self.cacheStorage:
                return self.cacheStorage[key]
            else:
                value = func(*args, **kwargs)
                self.cacheStorage[key] = value
                return value
        return wrapper