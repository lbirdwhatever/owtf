"""
owtf.api.handlers.work
~~~~~~~~~~~~~

"""
from flask import Flask, Blueprint
from flask_restful import Resource

from owtf.lib import exceptions
from owtf.utils.strings import cprint
from owtf.api.factory import app, api


worklist = Blueprint('worklist', __name__, url_prefix='/worklist/')
api.init_app(worklist)


class WorklistHandler(Resource):
    def get(self, work_id=None, action=None):
        try:
            if work_id is None:
                criteria = dict(self.request.arguments)
                self.write(self.get_component("worklist_manager").get_all(criteria))
            else:
                self.write(self.get_component("worklist_manager").get(int(work_id)))
        except exceptions.InvalidParameterType:
            raise tornado.web.HTTPError(400)
        except exceptions.InvalidWorkReference:
            raise tornado.web.HTTPError(400)

    def post(self, work_id=None, action=None):
        if work_id is not None or action is not None:
            tornado.web.HTTPError(400)
        try:
            filter_data = dict(self.request.arguments)
            if not filter_data:
                raise tornado.web.HTTPError(400)
            plugin_list = self.get_component("db_plugin").get_all(filter_data)
            target_list = self.get_component("target").get_target_config_dicts(filter_data)
            if (not plugin_list) or (not target_list):
                raise tornado.web.HTTPError(400)
            force_overwrite = self.get_component("config").str2bool(self.get_argument("force_overwrite",
                                                                                              "False"))
            self.get_component("worklist_manager").add_work(target_list, plugin_list, force_overwrite=force_overwrite)
            self.set_status(201)
        except exceptions.InvalidTargetReference:
            raise tornado.web.HTTPError(400)
        except exceptions.InvalidParameterType:
            raise tornado.web.HTTPError(400)

    def delete(self, work_id=None, action=None):
        if work_id is None or action is not None:
            tornado.web.HTTPError(400)
        try:
            work_id = int(work_id)
            if work_id != 0:
                self.get_component("worklist_manager").remove_work(work_id)
                self.set_status(200)
            else:
                if action == 'delete':
                    self.get_component("worklist_manager").delete_all()
        except exceptions.InvalidTargetReference:
            raise tornado.web.HTTPError(400)
        except exceptions.InvalidParameterType:
            raise tornado.web.HTTPError(400)
        except exceptions.InvalidWorkReference:
            raise tornado.web.HTTPError(400)

    def patch(self, work_id=None, action=None):
        if work_id is None or action is None:
            tornado.web.HTTPError(400)
        try:
            work_id = int(work_id)
            if work_id != 0:  # 0 is like broadcast address
                if action == 'resume':
                    self.get_component("db").Worklist.patch_work(work_id, active=True)
                elif action == 'pause':
                    self.get_component("db").Worklist.patch_work(work_id, active=False)
            else:
                if action == 'pause':
                    self.get_component("worklist_manager").pause_all()
                elif action == 'resume':
                    self.get_component("worklist_manager").resume_all()
        except exceptions.InvalidWorkReference:
            raise tornado.web.HTTPError(400)


class WorklistSearchHandler(Resource):
    def get(self):
        try:
            criteria = dict(self.request.arguments)
            criteria["search"] = True
            self.write(self.get_component("worklist_manager").search_all(criteria))
        except exceptions.InvalidParameterType:
            raise tornado.web.HTTPError(400)


api.add_resource(WorklistHandler, '/')
api.add_resource(WorklistSearchHandler, '/search')
