from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from database.models.user import User, UserDB
from database.client import db_client
from database.schemas.user import user_schema


ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 30
SECRET = "201d573bd7d1344d3a3bfce1550b69102fd11be3db6d379508b6cccc58ea230b"

router = APIRouter(prefix="/auth", tags=["auth"], responses={404: {"description": "Not found"}})

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])

#DB MOMENTANEA

users_db = {}

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
@router.post("/signin", response_model=UserDB, status_code=status.HTTP_201_CREATED)
async def new_user(user: UserDB):
    
    userdict = dict(user)
    userdict["disabled"] = False
    del userdict["id"]
    
    if userdict["username"] in db_client.local.users.distinct("username"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya existe")
    
    #MongoDB asigna un id automáticamente
    id = db_client.local.users.insert_one(userdict).inserted_id

    new_user = user_schema(db_client.local.users.find_one({"_id": id}))
    
    #encriptamos la contraseña
    new_user["password"] = crypt.hash(new_user["password"])
    
    return UserDB(**new_user)
    
    
#ACTUALIZACIÓN DE USUARIOS
@router.put("/update", response_model=UserDB, status_code=status.HTTP_200_OK)
async def update(user: UserDB):#= Depends(user_actual)

    userdict = dict(user)
    
    if userdict["username"] not in db_client.local.users.distinct("username"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no existe")
    
    #Actualiza el usuario
    db_client.local.users.update_one({"username": userdict["username"]}, {"$set": userdict})
    
    return UserDB(**userdict)
    
    return {"message": "Usuario actualizado"}

"INICIO DE SESIÓN"
@router.post("/login", response_model=UserDB, status_code=status.HTTP_200_OK)

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
@router.get("/users/me", response_model=UserDB, status_code=status.HTTP_200_OK)
async def me(user: User = Depends(user_actual)):
    return user

"CONSULTA DE USUARIOS"
@router.get("/users", response_model=UserDB, status_code=status.HTTP_200_OK)
async def users():
    return users_db

# #ELIMINACIÓN DE USUARIOS
# @router.delete("/delete", response_model=UserDB, status_code=status.HTTP_200_OK)
# async def delete(user: UserDB = Depends(user_actual)):
        
#         userdict = dict(user)
#         # if user.username not in users_db:
#         #     raise HTTPException(
#         #         status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no existe")
        
#         id = db_client.local.users.delete_one(userdict).deleted_id
        
#         return {"message": "Usuario eliminado"}
