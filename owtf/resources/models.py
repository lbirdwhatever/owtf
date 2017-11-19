from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Table, Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from owtf.api.factory import db


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True)
    # Dirty if user edited it. Useful while updating
    dirty = Column(Boolean, default=False)
    resource_name = Column(String)
    resource_type = Column(String)
    resource = Column(String)
    __table_args__ = (UniqueConstraint(
        'resource', 'resource_type', 'resource_name'),)
