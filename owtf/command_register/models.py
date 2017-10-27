from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Table, Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from owtf.database import db


class Command(db.Model):
    __tablename__ = "command_register"

    start_time = Column(DateTime)
    end_time = Column(DateTime)
    success = Column(Boolean, default=False)
    target_id = Column(Integer, ForeignKey("targets.id"))
    plugin_key = Column(String, ForeignKey("plugins.key"))
    modified_command = Column(String)
    original_command = Column(String, primary_key=True)

    @hybrid_property
    def run_time(self):
        return self.end_time - self.start_time
