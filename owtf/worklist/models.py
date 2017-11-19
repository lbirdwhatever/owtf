from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Table, Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from owtf.api.factory import db


class Work(db.Model):
    __tablename__ = "worklist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    target_id = Column(Integer, ForeignKey("targets.id"))
    plugin_key = Column(String, ForeignKey("plugins.key"))
    active = Column(Boolean, default=True)
    # Columns plugin and target are created using backrefs

    __table_args__ = (UniqueConstraint('target_id', 'plugin_key'),)

    def __repr__(self):
        return "<Work (target='%s', plugin='%s')>" % (self.target_id, self.plugin_key)
