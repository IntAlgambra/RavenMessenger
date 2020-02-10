'''
структура базы данных клиентов сервера:
-Клиенты:
    -Id уникальный
    -Логин уникальный
    -Пароль (сначала открытый потом кэш)
'''

import hashlib
import os.path

from sqlalchemy import Column, Integer, String, Boolean, Binary, create_engine
from sqlalchemy.orm import sessionmaker, relationship, scoped_session

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.exc import IntegrityError, OperationalError

from sqlalchemy.orm.exc import UnmappedInstanceError

from sqlalchemy.engine import Engine

#имя файла с базой sqlite
DATABASE_FILENAME = 'clients_1.db'

#Создаем родительский класс для всех таблиц в базе данных
DB = declarative_base()

#Таблица с данными о клиентах
class Clients(DB):

    __tablename__ = 'clients'

    client_id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String, unique=True)
    password = Column(String)
    is_online = Column(Boolean)
    public_key = Column(Binary)

    def __repr__(self):
        return('client №{} with login {}'.format(self.client_id, self.client_login))

#Класс для работы с базой данных
class Database():
    def __init__(self, filename=DATABASE_FILENAME):
        self.database = DB
        self.filename = filename
        database_exist = os.path.isfile(self.filename)
        self.engine = create_engine('sqlite:///{}'.format(self.filename))
        if not database_exist:
            self.create_all()
        self.session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(self.session_factory)

    def create_all(self):
        self.database.metadata.create_all(self.engine)

    def update_all(self):
        self.database.metadata.drop_all(self.engine)
        self.database.metadata.create_all(self.engine)

    def add_client(self, login, password):
        session = self.session()
        try:
            client = Clients(login = login, password = password, is_online = False, public_key=b'')
            session.add(client)
            session.commit()
        except IntegrityError:
            session.rollback()
            print('This client is already in database')
        finally:
            self.session.remove()

    def auth_client(self, login, password, public_key):
        session = self.session()
        try:
            client = session.query(Clients).filter(Clients.login == login).first()
            if not client:
                return False
            else:
                if client.password == password:
                    client.public_key = public_key
                    session.commit()
                    return True
            return False
        except OperationalError:
            session.rollback()
            return None
        finally:
            self.session.remove()

    def reg_client(self, login, temp_password, password):
        session = self.session()
        try:
            client = session.query(Clients).filter(Clients.login == login).first()
            if client:
                if client.password != temp_password:
                    return False
                else:
                    client.password = password
                    session.commit()
                    return True
            else:
                return False
        except OperationalError:
            session.rollback()
            return None
        finally:
            self.session.remove()

    def get_public_key(self, login):
        session = self.session()
        try:
            client = session.query(Clients).filter(Clients.login == login).first()
            if client:
                public_key = client.public_key
                return public_key
            else:
                return None
        except OperationalError:
            session.rollback()
            return None
        finally:
            self.session.remove()

    def make_online(self, login):
        session = self.session()
        try:
            client = session.query(Clients).filter(Clients.login == login).first()
            client.is_online = True
            session.commit()
        except Exception as e:
            prrint(e)
            return None
        finally:
            self.session.remove()

    def make_offline(self, login):
        session = self.session()
        try:
            client = session.query(Clients).filter(Clients.login == login).first()
            client.is_online = False
            session.commit()
        except Exception as e:
            prrint(e)
            return None
        finally:
            self.session.remove()

    def delete_client(self, login):
        session = self.session()
        try:
            client = session.query(Clients).filter(Clients.login == login).first()
            session.delete(client)
            session.commit()
            return True
        except UnmappedInstanceError:
            session.rollback()
            return False
        finally:
            self.session.remove()

    def check_client(self, login):
        session = self.session()
        try:
            clients_query = session.query(Clients.login).all()
            if login in [data[0] for data in clients_query]:
                return True
            else:
                return False
        except OperationalError:
            session.rollback()
            return None
        finally:
            self.session.remove()

if __name__ == '__main__':
    db = Database()
    db.update_all()
    clients = [
        ['John', '12345'],
        ['James', 'qwerty'],
        ['Luke', 'starwars']
    ]
    for record in clients:
        db.add_client(record[0], hashlib.md5(record[1].encode()).hexdigest())

    # print(db.auth_client('John', '12345'))
    # print(db.auth_client('James', 'enkfclkn'))
    # print(db.auth_client('cnslnf', 'vknsknv'))
    # print('----------------')
    # print(db.reg_client('John', '12345', '124124dscm'))
    # print(db.reg_client('Luke', 'kkcsvdsv', 'y9hwec'))
    # print(db.reg_client('kmsmckmd', 'dscdc', 'escsc'))

