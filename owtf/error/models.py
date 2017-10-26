"""
owtf.error.models
~~~~~~~~~~~~~~
"""
import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Table, Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from owtf.database import db


class Error(db.Model):
    __tablename__ = "errors"

    id = Column(Integer, primary_key=True)
    owtf_message = Column(String)
    traceback = Column(String, nullable=True)
    user_message = Column(String, nullable=True)
    reported = Column(Boolean, default=False)
    github_issue_url = Column(String, nullable=True)

    def __repr__(self):
        return "<Error (traceback='%s')>" % (self.traceback)
