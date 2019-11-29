import logging
from unittest import TestCase
from hData.orm import *
import pymysql

class test_memory_db(TestCase):
    logger = logging.getLogger(__name__)
    engine = create_engine("sqlite:///:memory:", echo=False)


    def get_session(self):
        smsession = sessionmaker(bind=self.engine)
        smsession.configure(bind=self.engine)
        session = smsession()
        return session

    def test_1_create(self):
        Base.metadata.create_all(self.engine)

    def test_2_orm_insert(self):
        session = self.get_session()
        u1 = User(name="Bob")
        u2 = User(name="Fred")
        ch1 = Channel(name="BBC")
        ch2 = Channel(name="CNN")
        ch3 = Channel(name="HKTV")
        u1.channels.append(ch1)
        u1.channels.append(ch2)
        u2.channels.append(ch3)
        session.add_all([u1, u2, ch1, ch2, ch3])
        session.commit()

    def test_3_queries(self):
        session = self.get_session()
        p = session.query(User).first()
        print(f"{p.name}")
        all_rec = [rec for rec in session.query(Channel).all()]
        self.assertEqual(len(all_rec), 3)
        #
        # Check the Join table is there
        #
        all_user = [rec for rec in session.query(UserChannel).all()]
        self.assertEqual(len(all_user), 3)

        # Query with no Join ... Bad result
        q = Query([User, Channel, UserChannel], session=session)
        self.assertEqual(q.count(), 18)

        q = Query([User, Channel, UserChannel], session=session). \
            filter(User.user_id == UserChannel.user_id). \
            filter(Channel.channel_id == UserChannel.channel_id)
        self.assertEqual(q.count(), 3)
        print("Test Done")


class test_physical_sqlite_db(test_memory_db):
    logger = logging.getLogger(__name__)
    import os
    try:
        os.unlink('/tmp/userchannel.db')
    except Exception:
        pass
    logger = logging.getLogger(__name__)
    engine = create_engine("sqlite:////tmp/userchannel.db", echo=False)


    # We need to drop all the tables first

    print("Testing sqlite PhysicalDb")

class test_physical_mysql_db(test_memory_db):
    logger = logging.getLogger(__name__)
    user='root'
    password='ducati'
    host='localhost'
    db='userchannel'
    # We need to drop the Database via the Service - not Attach to the Database
    connection = pymysql.connect(host=host, user=user, password=password, charset="utf8")
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

    engine = create_engine('mysql+mysqldb://root:ducati@localhost/userchannel', pool_recycle=3600)
    for t in engine.table_names():
        print(f"We have Table {t}")

