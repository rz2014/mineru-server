import subprocess
import uuid
import os
from pathlib import Path
import shutil
from flask import request, send_file
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
from flask_restful import Resource, marshal
from utils.tar import compress_folder_to_tar_gz
from flask import send_file

threadpool = BoundedThreadPoolExecutor()


# threadpool = ThreadPoolExecutor(max_workers=2)


ALLOWED_EXTENSIONS = ["pdf"]  # TODO image, docx


class RemotePdfApi(Resource):

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
        files = request.files
        if not files:
            raise ValueError("No files provided for upload")
        if len(files) > 1:
            raise ValueError("Only one file can be uploaded at a time")

        file_names = list(files.keys())
        file = files[file_names[0]]

        extension = file.filename.split(".")[-1]
        if extension.lower() not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Invalid file type: {extension}. Allowed types are: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        file_content = file.read()

        # TODO get file path
        task_id = str(uuid.uuid4())
        input_sub_path = f"upload_files/{task_id}.{extension}"

        output_sub_path = f"parsed_results/{task_id}"
        base_path = current_app.config.get('STORAGE_LOCAL_PATH')
        if not base_path or base_path.endswith("/"):
            output_path = base_path + output_sub_path
            input_path = base_path + input_sub_path
        else:
            output_path = base_path + "/" + output_sub_path
            input_path = base_path + "/" + input_sub_path

        folder = os.path.dirname(input_path)
        os.makedirs(folder, exist_ok=True)

        with open(os.path.join(input_path), "wb") as f:
            f.write(file_content)

        try:
            exec = config.get_env('PDF_CMD')
            backend = config.get_env('MINERU_BACKEND')
            command = f"{exec} -p {input_path} -o {output_path} -m auto -b {backend}"
            logging.info("execute command: " + command)
            threadpool.submit(
                60,
                run_convert,
                current_app._get_current_object(),
                task_id,
                command,
                True,
            )
            return BaseResponse(data={'task_id': task_id}).json
        except Exception as e:
            return BaseResponse(code=500, message=str(e)).json


class DownloadApi(Resource):

    def get(self, task_id):
        task = db.session.query(Task).filter_by(id=task_id).first()
        if not task:
            return BaseResponse(code=404, message='task not found').json

        if task.status != 'success':
            return BaseResponse(code=500, message='task is not completed yet').json

        output = json.loads(task.output) if task.output else None
        if not output:
            return BaseResponse(code=404, message='task output not found').json

        if 'output_tar_path' not in output:
            return BaseResponse(code=404, message='task output tar path not found').json

        output_tar_path = output['output_tar_path']

        if not os.path.exists(output_tar_path):
            return BaseResponse(code=404, message='tar file not found').json

        return send_file(
            output_tar_path,
            mimetype='application/gzip',
            as_attachment=True,
            download_name=f"{task_id}.tar.gz",
        )


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
            backend = config.get_env('MINERU_BACKEND')
            command = (
                f"{exec} -p {args['file_path']} -o {args['output_dir']} -m {parse_type} -b {backend}"
            )
            logging.info("execute command: " + command)
            task_id = str(uuid.uuid4())
            threadpool.submit(
                60,
                run_convert,
                current_app._get_current_object(),
                task_id,
                command,
                False,
            )
            return BaseResponse(
                data={'task_id': task_id, 'output_dir': args['output_dir']}
            ).json
        except Exception as e:
            return BaseResponse(code=500, message=str(e)).json


def run_convert(flask_app, task_id, command, remote: bool):
    try:
        with flask_app.app_context():
            try:
                if remote:
                    output_sub_path = f"parsed_results/{task_id}"
                    base_path = current_app.config.get('STORAGE_LOCAL_PATH')
                    if not base_path or base_path.endswith("/"):
                        output_path = base_path + output_sub_path
                    else:
                        output_path = base_path + "/" + output_sub_path
                    directory = Path(output_path)
                    if directory.exists():
                        shutil.rmtree(directory)
                    directory.mkdir(parents=True, exist_ok=True)

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
                output: str = None

                if remote:
                    output_tar_path = compress_folder_to_tar_gz(
                        output_path + f"/{task_id}"
                    )
                    output = json.dumps(
                        {
                            "output_tar_path": output_tar_path,
                            "output_dir": output_path,
                            "command": command,
                        },
                        ensure_ascii=True,
                    )

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
                update_dic = {
                    "status": status,
                    "return_code": return_code,
                    "output": output,
                }
                if err:
                    logging.error(err)
                    update_dic['error'] = err
                db.session.query(Task).filter(Task.id == task_id).update(update_dic)
                db.session.commit()
    except Exception as e:
        logging.error(e)
        raise e


api.add_resource(RemotePdfApi, '/remote', '/remote/<string:task_id>')
api.add_resource(LocalPdfApi, '/local', '/local/<string:task_id>')
api.add_resource(DownloadApi, '/download/<string:task_id>')
