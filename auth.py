import os
from datetime import datetime, timedelta #expiration time on the wristband
from passlib.context import CryptContext #password-scrambling machine
from jose import jwt #wristband stamper/checker

'''
generates a hash password
lets people login and logs out after 24 hrs
'''


# In production this MUST be set as an environment variable (see DEPLOY.md).
# The fallback is only for local development.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

#checks whether the password is correct
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# takes in a login info
'''
data is a dictionary carrying the login info
the token carries the login info (email) inside it, tied to that specific user.
'''
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    # token expires after 24 hours
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# checks whether the user is valid and gives access to valid user without a login
# avoids repeated logins
def decode_access_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])