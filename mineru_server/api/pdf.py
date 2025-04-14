import subprocess
import uuid
from flask import app
from flask_restful import Resource, reqparse

import config
from utils.response import BaseResponse

from utils.threadpool import BoundedThreadPoolExecutor
from . import api
import logging
from models.db import db
from models.task import Task, task_fields
import json
import json
from flask import Flask, current_app

# from concurrent.futures import ThreadPoolExecutor
from flask_restful import Resource, marshal, marshal_with

threadpool = BoundedThreadPoolExecutor()




class LocalPdfApi(Resource):

    def get(self, task_id):
        task = db.session.query(Task).filter_by(id=task_id).first()
        if not task:
            return BaseResponse(code=404, message='task not found').json
        return BaseResponse(
            code=200,
            message='success',
            data=marshal(task, task_fields),
        ).json

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'file_path', type=str, required=True, nullable=False, location='json'
        )
        parser.add_argument(
            'output_dir', type=str, required=True, nullable=False, location='json'
        )
        parser.add_argument(
            'type', type=str, required=False, nullable=False, location='json'
        )
        args = parser.parse_args()
        parse_type = args['type'] if args['type'] is not None else 'auto'
        try:
            exec = config.get_env('PDF_CMD')
            command = (
                f"{exec} -p {args['file_path']} -m {parse_type} -o {args['output_dir']}"
            )
            logging.info("execute command: " + command)
            task_id = str(uuid.uuid4())
            threadpool.submit(
                60, run_convert, current_app._get_current_object(), task_id, command
            )
            return BaseResponse(
                data={'task_id': task_id, 'output_dir': args['output_dir']}
            ).json
        except Exception as e:
            return BaseResponse(code=500, message=str(e)).json


def run_convert(flask_app, task_id, command):
    try:
        with flask_app.app_context():
            try:
                db.session.add(Task(id=task_id, command=command, status='running'))
                db.session.commit()
                result = subprocess.run(
                    command,
                    shell=True,
                    text=True,
                )
                return_code = result.returncode
                err: str = None
                status: str
                if result.returncode == 0:
                    status = "success"
                else:
                    status = "failed"
                    err = f"Command failed with error: {result}"
            except Exception as e:
                return_code = -1
                status = "failed"
                err = f"Execution failed with exception: {str(e)}"
                raise e
            finally:
                update_dic = {"status": status, "return_code": return_code}
                if err:
                    logging.error(err)
                    update_dic['error'] = err
                db.session.query(Task).filter(Task.id == task_id).update(update_dic)
                db.session.commit()
    except Exception as e:
        logging.error(e)
        raise e


api.add_resource(LocalPdfApi, '/local', '/local/<string:task_id>')
