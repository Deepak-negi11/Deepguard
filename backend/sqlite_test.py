from sqlalchemy import Column, Integer, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Test(Base):
    __tablename__ = 'test'
    id = Column(Integer, primary_key=True)

try:
    path = "/tmp/does_not_exist/test.db"
    url = f"sqlite:///{path}"
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    print("create_all succeeded!")
except Exception as e:
    print(f"create_all failed: {e}")
