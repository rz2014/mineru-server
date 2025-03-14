from flask import Blueprint
from utils.external_api import ExternalApi
from utils.threadpool import BoundedThreadPoolExecutor

bp = Blueprint('web', __name__, url_prefix="/api/v1/pdf")
api = ExternalApi(bp)
threadpool = BoundedThreadPoolExecutor()

from . import pdf
