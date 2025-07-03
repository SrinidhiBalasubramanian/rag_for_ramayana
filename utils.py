import json

import logging

import traceback

from datetime import datetime
from functools import wraps
from typing import Callable, Any
from pymongo import MongoClient

from config import MONGO_DB, LogDetails

class Tools:

    @staticmethod
    def read_json(filepath: str) -> dict:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    
    @staticmethod
    def setup_logger(name: str = "rag_for_ramayana"):
        logger = logging.getLogger(name)
        if not logger.handlers:
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    @staticmethod
    def safe_run(default_return: Any = None):
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                logger = Tools.setup_logger()
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Exception in {func.__name__}: {e}")
                    logger.debug(traceback.format_exc())
                    return default_return
            return wrapper
        return decorator

    
class DB:
    def __init__(self):
        client = MongoClient(MONGO_DB.URL)
        db = client[MONGO_DB.DATABASE]
        self.collection = db[MONGO_DB.COLLECTION]

    def log_usage(self, log_details: LogDetails):
        log_entry = {
            "timeStamp": datetime.now(),
            "query": log_details.query,
            "embeddingResults": log_details.embedding_results,
            "output": log_details.answer,
            "tokenUsage": log_details.token_usage
        }
        self.collection.insert_one(log_entry)

