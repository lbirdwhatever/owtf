from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Table, Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from owtf.database import db


# This table actually allows us to make a many to many relationship
# between transactions table and grep_outputs table
transaction_association_table = Table(
    'transaction_grep_association',
    Base.metadata,
    Column('transaction_id', Integer, ForeignKey('transactions.id')),
    Column('grep_output_id', Integer, ForeignKey('grep_outputs.id'))
)

Index('transaction_id_idx',
      transaction_association_table.c.transaction_id, postgresql_using='btree'
)

class Transaction(db.Model):
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
