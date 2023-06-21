from datetime import datetime
import pymysql

from database import USER, PASSWORD, HOST, PORT, DATABASE

from sqlalchemy import create_engine, Column, String, Date, Integer, and_, ForeignKey, func
from sqlalchemy.orm import sessionmaker, joinedload, relationship, declarative_base

# Создание соединения с базой данных
pymysql.install_as_MySQLdb()
engine = create_engine(f"mysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Определение модели данных
Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    birthday = Column(Date)
    email = Column(String)
    phone = Column(String)
    password = Column(String)


class Grant(Base):
    __tablename__ = "grants"

    id = Column(Integer, primary_key=True)
    directions_id = Column(Integer, ForeignKey("directions.id"))
    status_id = Column(Integer, ForeignKey("status.id"))
    foundations_id = Column(Integer, ForeignKey("foundations.id"))
    title = Column(String)
    image = Column(String)
    description = Column(String)
    apply_starrt_at = Column(String)
    apply_end_at = Column(String)

    direction = relationship("Direction")
    status = relationship("Status")
    foundation = relationship("Foundation")

class Foundation(Base):
    __tablename__ = "foundations"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    image = Column(String)
    description = Column(String)
    type = Column(String)


class Direction(Base):
    __tablename__ = "directions"
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Status(Base):
    __tablename__ = "status"
    id = Column(Integer, primary_key=True)
    name = Column(String)


# Создание таблицы (если она еще не существует)
Base.metadata.create_all(engine)


# Функция для создания нового пользователя
async def create_user(name, surname, birthday, email, phone, password):
    session = Session()
    user = User(
        name=name,
        surname=surname,
        birthday=datetime.strptime(birthday, '%Y-%m-%d').date(),
        email=email,
        phone=phone,
        password=password)
    session.add(user)
    session.commit()
    session.close()


def select_all_grants():
    session = Session()
    grants = session.query(Grant). \
        join(Direction, Grant.directions_id == Direction.id). \
        join(Status, Grant.status_id == Status.id). \
        join(Foundation, Grant.foundations_id == Foundation.id). \
        options(joinedload(Grant.direction), joinedload(Grant.status), joinedload(Grant.foundation)). \
        all()
    return grants


def select_all_fonds():
    session = Session()
    fonds = session.query(Foundation).all()
    for fond in fonds:
        count = session.query(func.count(Grant.id)).filter(Grant.foundations_id == fond.id).scalar()
        fond.grant_count = count
    return fonds


def search_fonds(title='', type=''):
    session = Session()
    if title and type:
        fonds = session.query(Foundation).filter(
            and_(Foundation.title.ilike(f"%{title}%"), Foundation.type.ilike(f"%{type}%"))
        ).all()
        for fond in fonds:
            count = session.query(func.count(Grant.id)).filter(Grant.foundations_id == fond.id).scalar()
            fond.grant_count = count
        return fonds

def get_fond_by_id(fond_id):
    session = Session()
    fond = session.query(Foundation).filter_by(id=fond_id).first()
    count = session.query(func.count(Grant.id)).filter(Grant.foundations_id == fond.id).scalar()
    fond.grant_count = count
    session.close()
    return fond


def get_grant_by_id(grant_id):
    session = Session()
    grant = session.query(Grant). \
        join(Direction, Grant.directions_id == Direction.id). \
        join(Status, Grant.status_id == Status.id). \
        join(Foundation, Grant.foundations_id == Foundation.id). \
        options(joinedload(Grant.direction), joinedload(Grant.status), joinedload(Grant.foundation)). \
        filter(Grant.id == grant_id).first()
    session.close()
    return grant



def search_grants(direction, status, foundation):
    session = Session()
    grants_query = session.query(Grant)

    if direction:
        grants_query = grants_query.filter(Grant.directions_id.ilike(f"%{direction}%"))
    if status:
        grants_query = grants_query.filter(Grant.status_id.ilike(f"%{status}%"))
    if foundation:
        grants_query = grants_query.filter(Grant.foundations_id.ilike(f"%{foundation}%"))

    grants = grants_query.all()
    return grants

