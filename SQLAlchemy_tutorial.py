from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import Session


# base クラスでデータベースのフィールドを定義
Base = declarative_base()
class User(Base):
    __tablename__="user"
    user_id = Column(Integer, primary_key=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    age = Column(Integer)

    def full_name(self):
        return f"{self.first_name} {self.last_name}" 

# sqlite のデータベースを tutorial.db のファイル名で作成 or アクセス
engine = create_engine("sqlite:///tutorial.db", echo=True)
Base.metadata.create_all(engine)

# session を介してデータを追加
with Session(engine) as session:
    new_user = User(first_name="Taro", last_name="Tanaka", age=25)
    session.add(new_user)
    session.commit()

