"""
ORM database Table, Indexes and Relationships.
"""
# pylint: disable=invalid-name, protected-access
from sqlalchemy import Table, select, Column, String, ForeignKey, Integer, create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref, Query

Base = declarative_base()

# pylint: disable=too-few-public-methods

"""
The database Definition is here.
It is quite straight forward or tables, indexes and constraints.
Views on the other hand are terrible (IMHO) in SqlAlchemy.
Once the REST API is better understood or defined.
We should add more Indexes to speed up these queries.
"""
class UserChannel(Base):
    __tablename__ = "userchannel"
    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True)
    channel_id = Column(Integer, ForeignKey("channel.channel_id"), primary_key=True)
    # Name                  Classname
    user    = relationship("User",     backref=backref("tv", cascade="all, delete-orphan"))
    channel = relationship("Channel",  backref=backref("tv", cascade="all, delete-orphan"))


class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(20))
    channels = relationship("Channel", secondary="userchannel")


class Channel(Base):
    __tablename__ = 'channel'
    channel_id = Column(Integer,
                        autoincrement=True,
                        primary_key=True)
    name = Column(String(20))
    users = relationship("User", secondary="userchannel")

