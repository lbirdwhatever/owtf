from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Table, Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from owtf.database import db


class Session(db.Model):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    active = Column(Boolean, default=False)
    targets = relationship("Target", secondary=target_association_table, backref="sessions")
