from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from typing import Optional, List
import os
import uuid
import shutil

import models
import schemas
import auth
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
app = FastAPI(title="KittenConnect API")

# Allow the frontend to call this API from the browser.
# Local dev origins are always allowed; the deployed frontend URL is added
# via the FRONTEND_URL environment variable on Render (see DEPLOY.md).
allowed_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
frontend_url = os.environ.get("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Folder where uploaded kitten photos are stored, served back at /uploads/<file>.
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Only accept real image types.
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
EXT_BY_TYPE = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

'''
if a user wants to create something, assign name, email, password and location to usercreate

if someone logs in, take email and passeord

if someone wants to go back in, check if they have already logged in and ignore them
'''

# sign up
@app.post("/signup", response_model=schemas.UserOut)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = auth.hash_password(user.password)
    new_user = models.User(
        # the things we create
        name=user.name,
        email=user.email,
        hashed_password=hashed_pw,
        location=user.location,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# login
@app.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()

    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # give her a wristband if she is in the database
    token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

'''
That token: str = Depends(oauth2_scheme) is the key. 
oauth2_scheme is a FastAPI security dependency — its 
whole job is to look at the incoming request, 
specifically the Authorization header, and extract 
whatever comes after the word Bearer

FastAPI sees create_kitten needs current_user, which needs get_current_user.
To run get_current_user, FastAPI first has to resolve its dependency: token: 
str = Depends(oauth2_scheme).

oauth2_scheme looks for an Authorization: Bearer <token> header. 

If it finds nothing, it doesn't hand back an empty string and let 
your code deal with it — it immediately raises an HTTP 401 itself, 
with that exact "Not authenticated" message, and stops everything right there.

Because of that, your get_current_user function body (the try/except 
with auth.decode_access_token) never even runs. Neither does create_kitten.
'''
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # accessing the function decode_access_token from auth.py
        payload = auth.decode_access_token(token) 
        # pulling out email from the payload dictionary
        email = payload.get("sub") 
        # 1. search through user's table, filter one that is equal, return the first occurrence
        user = db.query(models.User).filter(models.User.email == email).first()
    except:
        # we don't mention details of why it wouldn't work so that a fake user doesn't take advantage
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    return user

@app.get("/me", response_model=schemas.UserOut)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.post("/upload")
def upload_photo(
    request: Request,
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
):
    # reject anything that isn't an allowed image type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG, WEBP, or GIF images are allowed",
        )

    # unique filename so uploads never clobber each other
    ext = EXT_BY_TYPE[file.content_type]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as out:
        shutil.copyfileobj(file.file, out)

    # absolute URL the browser can load directly as an <img src>
    url = str(request.base_url) + f"uploads/{filename}"
    return {"url": url}


@app.post("/kittens", response_model=schemas.KittenOut)
def create_kitten(kitten: schemas.KittenCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    # what we create
    new_kitten = models.Kitten(
        name = kitten.name,
        age = kitten.age,
        location = kitten.location,
        photo = kitten.photo,
        notes = kitten.notes,
        owner_id = current_user.id,
        status = "available"
    ) 
    # saving new_kitten to the database
    db.add(new_kitten)
    db.commit()
    db.refresh(new_kitten)
    return new_kitten

@app.get("/kitten_list", response_model = List[schemas.KittenOut])
# what does it depend on? nothing.
def get_kitten(db: Session = Depends(get_db)):
    kitten = db.query(models.Kitten).all()
    return kitten


@app.get("/kittens/{kitten_id}", response_model=schemas.KittenOut)
def get_one_kitten(kitten_id: int, db: Session = Depends(get_db)):
    kitten = db.query(models.Kitten).filter(models.Kitten.id == kitten_id).first()
    if not kitten:
        raise HTTPException(status_code=404, detail="Kitten not found")
    return kitten


# helper: fetch a kitten and make sure current_user owns it before editing/deleting
def get_owned_kitten(kitten_id: int, db: Session, current_user: models.User) -> models.Kitten:
    kitten = db.query(models.Kitten).filter(models.Kitten.id == kitten_id).first()
    # 404 if it doesn't exist at all
    if not kitten:
        raise HTTPException(status_code=404, detail="Kitten not found")
    # 403 if it exists but belongs to someone else
    if kitten.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to modify this listing")
    return kitten


@app.put("/kittens/{kitten_id}", response_model=schemas.KittenOut)
def update_kitten(
    kitten_id: int,
    updates: schemas.KittenUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    kitten = get_owned_kitten(kitten_id, db, current_user)
    # only overwrite the fields the user actually sent
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(kitten, field, value)
    db.commit()
    db.refresh(kitten)
    return kitten


@app.delete("/kittens/{kitten_id}")
def delete_kitten(
    kitten_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    kitten = get_owned_kitten(kitten_id, db, current_user)
    db.delete(kitten)
    db.commit()
    return {"detail": "Kitten listing deleted"}
# updating a kitten returns one kitten only
@app.put("/kittens/{kitten_id}", response_model = schemas.KittenOut)
def edit_kitten(kitten_id: int, kitten: schemas.KittenCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
        existing_user = db.query(models.User).filter(models.User.email == user.email).first()