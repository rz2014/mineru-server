import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from flask import Flask

from config import Config
from api import bp
from models.db import init_db


class PieMinerUApp(Flask):
    pass


def register_blueprints(app: Flask):
    app.register_blueprint(bp)


def create_app() -> Flask:
    app = PieMinerUApp(__name__)
    app.config.from_object(Config())
    init_db(app)
    register_blueprints(app)

    return app


def init_logger(app: Flask):
    log_handlers = None
    log_file = app.config.get('LOG_FILE')
    if log_file:
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)
        log_handlers = [
            RotatingFileHandler(
                filename=log_file, maxBytes=1024 * 1024 * 1024, backupCount=5
            ),
            logging.StreamHandler(sys.stdout),
        ]

    try:
        logging.basicConfig(
            level=app.config.get('LOG_LEVEL'),
            format=app.config.get('LOG_FORMAT'),
            datefmt=app.config.get('LOG_DATEFORMAT'),
            handlers=log_handlers,
        )
    except Exception as e:
        print(e)
        raise


def main():
    app = create_app()
    init_logger(app)
    app.run(host="0.0.0.0", port=8300)


if __name__ == "__main__":
    main()
