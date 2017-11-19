"""
owtf.api.factory
~~~~~~~~~~~~~~~~~~~~~

"""

import logging

from flask import Flask, Blueprint
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

from owtf.config.views import config
from owtf.error.views import error
from owtf.plugin.views import plugin
from owtf.session.views import session
from owtf.targets.views import target
from owtf.transactions.views import transactions
from owtf.worklist.views import work



app = Flask(__name__)
api = Api(app, url_prefix="/api")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/owtf.db'
db = SQLAlchemy(app)


app.register_blueprint(config)
app.register_blueprint(error)
app.register_blueprint(plugin)
app.register_blueprint(session)
app.register_blueprint(target)
app.register_blueprint(transactions)
app.register_blueprint(work)


if __name__ == "__main__":
    app.run()
