"""
owtf.api.handlers.config
~~~~~~~~~~~~~~~~~~~~~

"""
from werkzeug.exceptions import BadRequest
from flask import Flask, Blueprint, request, jsonify
from flask_restful import Resource

from owtf.lib import exceptions
from owtf.api.factory import app, api
from owtf.config.service import update

config = Blueprint('config', __name__, url_prefix='/api/configuration')
api.init_app(config)


class ConfigurationHandler(Resource):
    def get(self):
        filter_data = dict(request.arguments)
        return jsonify(get_all(filter_data))

    def patch(self):
        for key, value_list in list(request.args.items()):
            try:
                update(key, value_list[0])
            except exceptions.InvalidConfigurationReference:
                raise BadRequest(400)


api.add_resource(ConfigurationHandler, '/')
