class Cache:

    def __init__(self, path: str, *, expiry: str = '1w'):
        self.cacheStorage = {}

    def cache(self, func):
        def wrapper(*args, **kwargs):
            key = func.__name__ + str(args) + str(kwargs)
            if self.isInCache(key):
                return self.retrieveFromCache(key)
            else:
                value = func(*args, **kwargs)
                self.storeInCache(key, value)
                return value
        return wrapper
    
    def isInCache(self, key):
        return (key in self.cacheStorage)
    
    def retrieveFromCache(self, key):
        if key in self.cacheStorage:
            return self.cacheStorage[key]
        else:
            return None
        
    def storeInCache(self, key, value):
        self.cacheStorage[key] = value
    
    def parseTimeString(timeStr: str):
        unitMap = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400,
            'w': 604800
        }

        try:
            value = int(timeStr[:-1])
            unit = timeStr[-1]
            if unit not in unitMap:
                raise ValueError("Invalid time unit")
            return value * unitMap[unit]
        except (ValueError, KeyError):
            raise ValueError("Invalid time string format")