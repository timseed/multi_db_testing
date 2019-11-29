"""
Db Tests.
Main purpose to see if we can test 3 physical implementation of
the same schema, using the same code-base.
And we can ...
"""
# pylint:disable=unused-wildcard-import,broad-except, wildcard-import
import logging
from unittest import TestCase
import pymysql
from sqlalchemy.orm import Session

from hData.orm import *


class test_memory_db(TestCase):
    """
    Db Tests using the Inmemory Sqlite3 system initially.
    """

    logger = logging.getLogger(__name__)
    engine = create_engine("sqlite:///:memory:", echo=False)

    def get_session(self) -> Session:
        """
        Can we get a Session
        """
        smsession = sessionmaker(bind=self.engine)
        smsession.configure(bind=self.engine)
        session = smsession()
        self.assertIsInstance(session, Session)
        return session

    def test_1_create(self):
        """
        Create all the Db tables defined in the ORM module
        """
        Base.metadata.create_all(self.engine)

    def test_2_orm_insert(self):
        """
        Check we can insert using ORM syntax
        """
        session = self.get_session()
        user_one = User(name="Bob")
        user_two = User(name="Fred")
        ch1 = Channel(name="BBC")
        ch2 = Channel(name="CNN")
        ch3 = Channel(name="HKTV")
        user_one.channels.append(ch1)
        user_one.channels.append(ch2)
        user_two.channels.append(ch3)
        session.add_all([user_one, user_two, ch1, ch2, ch3])
        session.commit()

    def test_3_queries(self):
        """
        Query db.
        Check we get the expected results
        """
        session = self.get_session()
        user_test = session.query(User).first()
        self.assertEqual(user_test.name, "Bob")
        all_rec = [rec for rec in session.query(Channel).all()]
        self.assertEqual(len(all_rec), 3)
        #
        # Check the Join table is there
        #
        all_user = [rec for rec in session.query(UserChannel).all()]
        self.assertEqual(len(all_user), 3)

        # Query with no Join ... Bad result
        query_result = Query([User, Channel, UserChannel], session=session)
        self.assertEqual(query_result.count(), 18)

        query_result = (
            Query([User, Channel, UserChannel], session=session)
            .filter(User.user_id == UserChannel.user_id)
            .filter(Channel.channel_id == UserChannel.channel_id)
        )
        self.assertEqual(query_result.count(), 3)
        print("Tests Done")


class test_physical_sqlite_db(test_memory_db):
    """
    Now use a physical sqlite Db
    """

    logger = logging.getLogger(__name__)
    import os

    try:
        os.unlink("/tmp/userchannel.db")
    except Exception:
        pass
    logger = logging.getLogger(__name__)
    engine = create_engine("sqlite:////tmp/userchannel.db", echo=False)


class test_physical_mysql_db(test_memory_db):
    """
    Now use a physical mysql local database
    """

    logger = logging.getLogger(__name__)
    user = "root"
    password = "ducati"
    host = "localhost"
    db = "userchannel"
    # We need to drop the Database via the Service - not Attach to the Database
    connection = pymysql.connect(
        host=host, user=user, password=password, charset="utf8"
    )
    try:
        # Create a cursor object
        dbCursor = connection.cursor()
        sql = "DROP DATABASE " + db
        # Execute the create database SQL statment through the cursor instance
        try:
            dbCursor.execute(sql)
        except Exception:
            pass
        sql = "CREATE DATABASE " + db
        # Execute the create database SQL statment through the cursor instance
        dbCursor.execute(sql)
    except Exception as e:
        print("Exeception occured:{}".format(e))
    finally:
        connection.close()

    engine = create_engine(
        "mysql+mysqldb://root:ducati@localhost/userchannel", pool_recycle=3600
    )
    for t in engine.table_names():
        print(f"We have Table {t} and we SHOULD NOT HAVE THIS")
