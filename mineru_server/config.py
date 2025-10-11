import os

import dotenv

dotenv.load_dotenv()

DEFAULTS = {
    'WEB_URL': 'http://localhost:8300',
    'PDF_CMD': 'mineru',
    'MINERU_BACKEND': 'vlm-vllm-engine',
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///mineru-server.db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': "False",
    'STORAGE_LOCAL_PATH': 'storage',
    'MAX_WORKER': 1,
    'MAX_TASK_SIZE': 1,
}


def get_env(key):
    return os.environ.get(key, DEFAULTS.get(key))


def get_bool_env(key):
    value = get_env(key)
    return value.lower() == 'true' if value is not None else False


def get_cors_allow_origins(env, default):
    cors_allow_origins = []
    if get_env(env):
        for origin in get_env(env).split(','):
            cors_allow_origins.append(origin)
    else:
        cors_allow_origins = [default]

    return cors_allow_origins


class Config:
    """Application configuration class."""

    def __init__(self):
        self.TESTING = get_bool_env('TESTING')
        self.LOG_LEVEL = get_env('LOG_LEVEL')
        self.LOG_FILE = get_env('LOG_FILE')
        self.LOG_FORMAT = get_env('LOG_FORMAT')
        self.LOG_DATEFORMAT = get_env('LOG_DATEFORMAT')

        self.WEB_URL = get_env('WEB_URL')

        self.WEB_CORS_ALLOW_ORIGINS = get_cors_allow_origins(
            'WEB_CORS_ALLOW_ORIGINS', self.WEB_URL
        )

        self.PDF_CMD = get_env('PDF_CMD')

        self.SQLALCHEMY_DATABASE_URI = get_env('SQLALCHEMY_DATABASE_URI')
        self.SQLALCHEMY_TRACK_MODIFICATIONS = get_bool_env(
            'SQLALCHEMY_TRACK_MODIFICATIONS'
        )

        self.STORAGE_LOCAL_PATH = get_env("STORAGE_LOCAL_PATH")
