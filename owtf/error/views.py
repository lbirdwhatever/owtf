from flask import Flask, Blueprint
from flask_restful import Resource

from owtf.lib import exceptions
from owtf.api.factory import app, api

error = Blueprint('error', __name__, url_prefix='/errors/')
api.init_app(error)


class ErrorDataHandler(Resource):
    def get(self, error_id=None):
        if error_id is None:
            filter_data = dict(self.request.arguments)
            self.write(self.get_component("db_error").get_all(filter_data))
        else:
            try:
                self.write(self.get_component("db_error").get(error_id))
            except exceptions.InvalidErrorReference:
                raise tornado.web.HTTPError(400)

    def post(self, error_id=None):
        if error_id is None:
            try:
                filter_data = dict(self.request.arguments)
                username = filter_data['username'][0]
                title = filter_data['title'][0]
                body = filter_data['body'][0]
                id = int(filter_data['id'][0])
                self.write(self.get_component("error_handler").add_github_issue(
                    username, title, body, id))
            except:
                raise tornado.web.HTTPError(400)
        else:
            raise tornado.web.HTTPError(400)

    def patch(self, error_id=None):
        if error_id is None:
            raise tornado.web.HTTPError(400)
        if self.request.arguments.get_argument("user_message", default=None):
            raise tornado.web.HTTPError(400)
        self.get_component("db_error").update(
            error_id, self.request.arguments.get_argument("user_message"))

    def delete(self, error_id=None):
        if error_id is None:
            raise tornado.web.HTTPError(400)
        try:
            self.get_component("db_error").delete(error_id)
        except exceptions.InvalidErrorReference:
            raise tornado.web.HTTPError(400)


api.add_resource(ErrorDataHandler, '/')
