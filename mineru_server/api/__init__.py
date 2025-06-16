from flask import Blueprint
from utils.external_api import ExternalApi
from utils.threadpool import BoundedThreadPoolExecutor
import config

bp = Blueprint('web', __name__, url_prefix="/api/v1/pdf")
api = ExternalApi(bp)
threadpool = BoundedThreadPoolExecutor(int(config.get_env('MAX_WORKER')), int(config.get_env('MAX_TASK_SIZE')))

from . import pdf
