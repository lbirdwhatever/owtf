"""
owtf.config.models
~~~~~~~~~~~~~~~~~~
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Table, Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from owtf.api.factory import db


class Configuration(Base):
    __tablename__ = "configuration"

    key = Column(String, primary_key=True)
    value = Column(String)
    section = Column(String)
    descrip = Column(String, nullable=True)
    dirty = Column(Boolean, default=False)

    def __repr__(self):
        return "<ConfigSetting (key='%s', value='%s', dirty='%r')>" % (self.key, self.value, self.dirty)
