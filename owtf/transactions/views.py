"""
owtf.api.handlers.transactions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from flask import Flask, Blueprint
from flask_restful import Resource

from owtf import exceptions
from owtf.utils.strings import cprint
from owtf.exceptions import InvalidTargetReference
from owtf.api.factory import app, api


transactions = Blueprint('transactions', __name__, url_prefix='/transactions/')
api.init_app(transactions)


class TransactionDataHandler(Resource):
    def get(self, target_id=None, transaction_id=None):
        try:
            if transaction_id:
                self.write(self.get_component("transaction").get_by_id_as_dict(
                    int(transaction_id), target_id=int(target_id)))
            else:
                # Empty criteria ensure all transactions
                filter_data = dict(self.request.arguments)
                self.write(self.get_component("transaction").get_all_as_dicts(filter_data, target_id=int(target_id)))
        except exceptions.InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)
        except exceptions.InvalidTransactionReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)
        except exceptions.InvalidParameterType as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)

    def post(self, target_url):
        raise tornado.web.HTTPError(405)

    def put(self):
        raise tornado.web.HTTPError(405)

    def patch(self):
        raise tornado.web.HTTPError(405)

    def delete(self, target_id=None, transaction_id=None):
        try:
            if transaction_id:
                self.get_component("transaction").delete_transaction(int(transaction_id), int(target_id))
            else:
                raise tornado.web.HTTPError(400)
        except exceptions.InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)


class TransactionHrtHandler(Resource):
    def post(self, target_id=None, transaction_id=None):
        try:
            if transaction_id:
                filter_data = dict(self.request.arguments)
                self.write(self.get_component("transaction").get_hrt_response(filter_data, int(transaction_id), target_id=int(target_id)))
            else:
                raise tornado.web.HTTPError(400)
        except (InvalidTargetReference, InvalidTransactionReference, InvalidParameterType) as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)


class TransactionSearchHandler(Resource):
    def get(self, target_id=None):
        if not target_id:  # Must be a integer target id
            raise tornado.web.HTTPError(400)
        try:
            # Empty criteria ensure all transactions
            filter_data = dict(self.request.arguments)
            filter_data["search"] = True
            self.write(self.get_component("transaction").search_all(filter_data, target_id=int(target_id)))
        except exceptions.InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)
        except exceptions.InvalidTransactionReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)
        except exceptions.InvalidParameterType as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)


class URLDataHandler(Resource):
    def get(self, target_id=None):
        try:
            # Empty criteria ensure all transactions
            filter_data = dict(self.request.arguments)
            self.write(self.get_component("url_manager").get_all(filter_data, target_id=int(target_id)))
        except exceptions.InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)

    @tornado.web.asynchronous
    def post(self, target_url):
        raise tornado.web.HTTPError(405)

    @tornado.web.asynchronous
    def put(self):
        raise tornado.web.HTTPError(405)

    @tornado.web.asynchronous
    def patch(self):
        # TODO: allow modification of urls from the ui, may be adjusting scope etc.. but i don't understand
        # it's use yet ;)
        raise tornado.web.HTTPError(405)  # @UndefinedVariable

    @tornado.web.asynchronous
    def delete(self, target_id=None):
        # TODO: allow deleting of urls from the ui
        raise tornado.web.HTTPError(405)  # @UndefinedVariable


class URLSearchHandler(Resource):
    def get(self, target_id=None):
        if not target_id:  # Must be a integer target id
            raise tornado.web.HTTPError(400)
        try:
            # Empty criteria ensure all transactions
            filter_data = dict(self.request.arguments)
            filter_data["search"] = True
            self.write(self.get_component("url_manager").search_all(filter_data, target_id=int(target_id)))
        except exceptions.InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)
        except exceptions.InvalidParameterType as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)
