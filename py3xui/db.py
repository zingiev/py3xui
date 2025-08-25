import sqlalchemy as sql
from sqlalchemy.orm import declarative_base, sessionmaker


engine = sql.create_engine("sqlite:///py3xui.session")
Base = declarative_base()


class Cookies(Base):
    __tablename__ = "cookies"

    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String, nullable=False)
    value = sql.Column(sql.String, nullable=False)
    domain = sql.Column(sql.String, nullable=False)
    path = sql.Column(sql.String, nullable=False)
    secure = sql.Column(sql.String, nullable=False)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db = Session()
