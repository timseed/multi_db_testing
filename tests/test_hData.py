from unittest import TestCase
import logging
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Query
from hData.orm import *

logger = logging.getLogger(__name__)
engine = create_engine("sqlite:///:memory:", echo=False)


class test_memory_db(TestCase):

    def get_session(self):
        smsession = sessionmaker(bind=engine)
        smsession.configure(bind=engine)
        session = smsession()
        return session


    def test_1_create(self):
        Base.metadata.create_all(engine)


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
        all_rec=[rec for rec in session.query(Channel).all()]
        self.assertEqual(len(all_rec), 3)
        #
        # Check the Join table is there
        #
        all_user = [rec for rec in session.query(UserChannel).all()]
        self.assertEqual(len(all_user),3)

        # Query with no Join ... Bad result
        q = Query([User, Channel, UserChannel], session=session)
        self.assertEqual(q.count(), 18)

        q = Query([User, Channel, UserChannel], session=session). \
            filter(User.user_id == UserChannel.user_id). \
            filter(Channel.channel_id == UserChannel.channel_id)
        self.assertEqual(q.count(), 3)
