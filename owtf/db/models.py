"""
owtf.db.models
~~~~~~~~~~~~~~

The SQLAlchemy models for every table in the OWTF DB.
"""
import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Table, Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

# This table actually allows us to make a many to many relationship
# between transactions table and grep_outputs table
transaction_association_table = Table(
    'transaction_grep_association',
    Base.metadata,
    Column('transaction_id', Integer, ForeignKey('transactions.id')),
    Column('grep_output_id', Integer, ForeignKey('grep_outputs.id'))
)

Index('transaction_id_idx', transaction_association_table.c.transaction_id, postgresql_using='btree')


class Transaction(Base):
    __tablename__ = "transactions"

    target_id = Column(Integer, ForeignKey("targets.id"))
    id = Column(Integer, primary_key=True)
    url = Column(String)
    scope = Column(Boolean, default=False)
    method = Column(String)
    data = Column(String, nullable=True)  # Post DATA
    time = Column(Float(precision=10))
    time_human = Column(String)
    local_timestamp = Column(DateTime)
    raw_request = Column(Text)
    response_status = Column(String)
    response_headers = Column(Text)
    response_size = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    binary_response = Column(Boolean, nullable=True)
    session_tokens = Column(String, nullable=True)
    login = Column(Boolean, nullable=True)
    logout = Column(Boolean, nullable=True)
    grep_outputs = relationship(
        "GrepOutput",
        secondary=transaction_association_table,
        cascade="delete",
        backref="transactions"
    )

    def __repr__(self):
        return "<HTTP Transaction (url='%s' method='%s' response_status='%s')>" % (self.url, self.method,
                                                                                   self.response_status)


class GrepOutput(Base):
    __tablename__ = "grep_outputs"

    target_id = Column(Integer, ForeignKey("targets.id"))
    id = Column(Integer, primary_key=True)
    name = Column(String)
    output = Column(Text)
    # Also has a column transactions, which is added by
    # using backref in transaction

    __table_args__ = (UniqueConstraint('name', 'output', target_id),)


class Url(Base):
    __tablename__ = "urls"

    target_id = Column(Integer, ForeignKey("targets.id"))
    url = Column(String, primary_key=True)
    visited = Column(Boolean, default=False)
    scope = Column(Boolean, default=True)

    def __repr__(self):
        return "<URL (url='%s')>" % (self.url)


class PluginOutput(Base):
    __tablename__ = "plugin_outputs"

    target_id = Column(Integer, ForeignKey("targets.id"))
    plugin_key = Column(String, ForeignKey("plugins.key"))
    # There is a column named plugin which is caused by backref from the plugin class
    id = Column(Integer, primary_key=True)
    plugin_code = Column(String)  # OWTF Code
    plugin_group = Column(String)
    plugin_type = Column(String)
    date_time = Column(DateTime, default=datetime.datetime.now())
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    output = Column(String, nullable=True)
    error = Column(String, nullable=True)
    status = Column(String, nullable=True)
    user_notes = Column(String, nullable=True)
    user_rank = Column(Integer, nullable=True, default=-1)
    owtf_rank = Column(Integer, nullable=True, default=-1)
    output_path = Column(String, nullable=True)

    @hybrid_property
    def run_time(self):
        return self.end_time - self.start_time

    __table_args__ = (UniqueConstraint('plugin_key', 'target_id'),)


class Command(Base):
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


class Error(Base):
    __tablename__ = "errors"

    id = Column(Integer, primary_key=True)
    owtf_message = Column(String)
    traceback = Column(String, nullable=True)
    user_message = Column(String, nullable=True)
    reported = Column(Boolean, default=False)
    github_issue_url = Column(String, nullable=True)

    def __repr__(self):
        return "<Error (traceback='%s')>" % (self.traceback)


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True)
    dirty = Column(Boolean, default=False)  # Dirty if user edited it. Useful while updating
    resource_name = Column(String)
    resource_type = Column(String)
    resource = Column(String)
    __table_args__ = (UniqueConstraint('resource', 'resource_type', 'resource_name'),)


class TestGroup(Base):
    __tablename__ = "test_groups"

    code = Column(String, primary_key=True)
    group = Column(String)  # web, network
    descrip = Column(String)
    hint = Column(String, nullable=True)
    url = Column(String)
    priority = Column(Integer)
    plugins = relationship("Plugin")


class Work(Base):
    __tablename__ = "worklist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    target_id = Column(Integer, ForeignKey("targets.id"))
    plugin_key = Column(String, ForeignKey("plugins.key"))
    active = Column(Boolean, default=True)
    # Columns plugin and target are created using backrefs

    __table_args__ = (UniqueConstraint('target_id', 'plugin_key'),)

    def __repr__(self):
        return "<Work (target='%s', plugin='%s')>" % (self.target_id, self.plugin_key)


class Mapping(Base):
    __tablename__ = 'mappings'

    owtf_code = Column(String, primary_key=True)
    mappings = Column(String)
    category = Column(String, nullable=True)
