from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta


ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 30
SECRET = "201d573bd7d1344d3a3bfce1550b69102fd11be3db6d379508b6cccc58ea230b"

router = APIRouter(prefix="/authdb", tags=["authdb"], responses={404: {"description": "Not found"}})

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])

class User(BaseModel):

    username: str
    fullname: str 
    cc: str
    role: str 
    disabled: bool
class UserDB(User):

    password: str

#DB MOMENTANEA
users_db = {
    'nfonseca': {"username": "nfonseca", "fullname": "Nicolás Fonseca", "cc": "1233696364", "role": "Usuario", "disabled": False, "password": "$2a$04$PWWgDGsBjxjCaXbxcNWr4e/.1FQrMm8h/U/ryDY8qOPAZgVXsqM9C"},
    'jandrade': {"username": "jandrade", "fullname": "Jaime Andrade", "cc": "123456789", "role": "Administrador", "disabled" : False, "password": "$2a$04$lO7ytQCwybsHsftsan.3V.1VTyvvSAsz9/SHeEvVsWZ7YWSiGJSg2"}
    }

def buscar_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])
    
def buscar_user(username: str):
    if username in users_db:
        return User(**users_db[username]) 

async def auth_user(token: str = Depends(oauth2)):

    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"})

    try:
        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub")
        if username is None:
            raise exception

    except JWTError:
        raise exception

    return buscar_user(username)


async def user_actual(user: User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo")

    return user

#REGISTRO DE USUARIOS
@router.post("/signin")
async def new_user(user: UserDB):
    
    if user.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya existe")
    
    user.password = crypt.hash(user.password)
    users_db.update({user.username: user.dict()})
    return {"message": "Usuario creado"}

#ACTUALIZACIÓN DE USUARIOS
@router.put("/update")
async def update(user: UserDB, user_actual: User = Depends(user_actual)):
    
    if user.username not in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no existe")
    
    user.password = crypt.hash(user.password)
    users_db.update({user.username: user.dict()})
    return {"message": "Usuario actualizado"}

"INICIO DE SESIÓN"
@router.post("/login")

async def login(form: OAuth2PasswordRequestForm = Depends()):

    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")

    user = buscar_user_db(form.username)

    if not crypt.verify(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña no es correcta")

    access_token = {"sub": user.username,
                    "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)}

    return {"access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}

#CONSULTA DE USUARIO ACTUAL
@router.get("/users/me")
async def me(user: User = Depends(user_actual)):
    return user

"CONSULTA DE USUARIOS"
@router.get("/users")
async def users():
    return users_db
