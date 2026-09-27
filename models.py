from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base
'''
what comes in, what goes out and whats stored is different

terms you are learning:
    nullable: it can be left empty
    id means row number in this context
'''
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    location = Column(String, nullable=True)

class Kitten(Base):
    __tablename__ = "kittens"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    location = Column(String, nullable = False)
    photo = Column(String, nullable = True)
    notes = Column(String, nullable=True)
    # user.id connected to owner_id
    owner_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, nullable=False, default="available")