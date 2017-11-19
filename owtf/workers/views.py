"""
owtf.workers.views
~~~~~~~~~~~~~~~~~~~~~~
"""

from flask import Flask, Blueprint
from flask_restful import Resource

from owtf.exceptions import InvalidTargetReference
from owtf.api.factory import app, api


workers = Blueprint('workers', __name__, url_prefix='/workers/')
api.init_app(workers)


class WorkerHandler(Resource):
    def set_default_headers(self):
        self.add_header("Access-Control-Allow-Origin", "*")
        self.add_header("Access-Control-Allow-Methods", "GET, POST, DELETE")

    def get(self, worker_id=None, action=None):
        if not worker_id:
            self.write(self.get_component(
                "worker_manager").get_worker_details())
        try:
            if worker_id and (not action):
                self.write(self.get_component(
                    "worker_manager").get_worker_details(int(worker_id)))
            if worker_id and action:
                if int(worker_id) == 0:
                    getattr(self.get_component("worker_manager"),
                            '%s_all_workers' % action)()
                getattr(self.get_component("worker_manager"),
                        '%s_worker' % action)(int(worker_id))
        except exceptions.InvalidWorkerReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)

    def post(self, worker_id=None, action=None):
        if worker_id or action:
            raise tornado.web.HTTPError(400)
        self.get_component("worker_manager").create_worker()
        self.set_status(201)  # Stands for "201 Created"

    def options(self, worker_id=None, action=None):
        self.set_status(200)

    def delete(self, worker_id=None, action=None):
        if (not worker_id) or action:
            raise tornado.web.HTTPError(400)
        try:
            self.get_component("worker_manager").delete_worker(int(worker_id))
        except exceptions.InvalidWorkerReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)


api.add_resource(WorkerHandler, '/')
