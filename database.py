import sqlalchemy
import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker, declarative_base
from config import *

Base = declarative_base()


class Viewed(Base):
    __tablename__ = 'viewed'

    worksheet_id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    profile_id = sq.Column(sq.Integer, unique=True)


def create_tables(engine):
    Base.metadata.create_all(engine)


engine = sqlalchemy.create_engine(DSN)
create_tables(engine)

Session = sessionmaker(bind=engine)
session = Session()


def add_worksheet(profile_id):
    to_bd = Viewed(profile_id=profile_id)
    session.add(to_bd)
    session.commit()


def find_worksheets(profile_id):
    session.commit()
    from_bd = session.query(Viewed).filter(Viewed.profile_id==profile_id).all()
    if not from_bd:
        return 0
    else:
        return 1


session.close()
