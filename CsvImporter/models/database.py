import os
from sqlalchemy import create_engine, MetaData, Column, Integer
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base, declared_attr


class BaseModel(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, autoincrement=False)


naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s",
    "pk": "pk_%(table_name)s"
}


engine = create_engine(
    'sqlite+pysqlite:///{0}/csvimporter.db'.format(os.path.dirname(os.path.abspath(__file__))), convert_unicode=True)
Session = scoped_session(sessionmaker(autocommit=True, autoflush=False, bind=engine))
Base = declarative_base(cls=BaseModel)
Base.metadata = MetaData(naming_convention=naming_convention)
Base.query = Session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from CsvImporter.models import models
    Base.metadata.create_all(bind=engine, checkfirst=True)