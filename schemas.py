'''
we are defining classes necassary for registration
'''
from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

'''
this is what the user creates, 
so id and hashed password is not necessary since we 
are the ones creating it for the user
'''
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    location: Optional[str] = None

class KittenCreate(BaseModel):
    name: str
    age: Optional[int] = None
    location: str
    photo: Optional[str] = None
    notes: Optional[str] = None
    # status: str

'''
fields the owner can edit; all optional so they can update just one thing
'''
class KittenUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    location: Optional[str] = None
    photo: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None

'''

'''
class UserOut(BaseModel):
    id: int
    name: str
    email: str
    location: Optional[str] = None
'''
output: what the user and other people see
'''
class KittenOut(BaseModel):
    id: int
    name: str
    age: Optional[int] = None
    location: str
    photo: Optional[str] = None
    notes: Optional[str] = None
    owner_id: int
    status: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

