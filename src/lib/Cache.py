from os import remove as removeFile
from os.path import exists, getmtime, join

import pickle
import time
class Cache:

    def __init__(self, path: str, *, expiry: str = '1w'):
        self.cacheDirectory = path
        self.cacheExpiry = Cache._parseTimeString(expiry)

    def cache(self, func):
        def wrapper(*args, **kwargs):
            key = func.__name__ + str(args) + str(kwargs)
            if self._isInCache(key):
                return self._retrieveFromCache(key)
            else:
                value = func(*args, **kwargs)
                self._storeInCache(key, value)
                return value
        return wrapper

    def _deleteIfExpired(self, key):
        filepath = self._generateFilePath(key)
        if exists(filepath):
            lastModified = getmtime(filepath)
            if lastModified + self.cacheExpiry < time.time():
                removeFile(filepath)

    def _generateFilePath(self, key):
        return join(self.cacheDirectory, self._generateFilename(key))

    def _generateFilename(self, key):
        return str(hash(key)) + '.pickle'

    def _isInCache(self, key):
        self._deleteIfExpired(key)
        return exists(self._generateFilePath(key))
    
    def _retrieveFromCache(self, key):
        filepath = self._generateFilePath(key)
        if exists(filepath):
            with open(filepath, 'rb') as f:
                value = pickle.load(f)
                return value
        
    def _storeInCache(self, key, value):
        filepath = self._generateFilePath(key)
        with open(filepath, 'wb') as f:
            pickle.dump(value, f)
    
    def _parseTimeString(timeStr: str):
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