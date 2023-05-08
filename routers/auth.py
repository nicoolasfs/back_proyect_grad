from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from database.models.user import User, UserDB
from database.client import db_client
from database.schemas.user import user_schema, users_schema
from bson.objectid import ObjectId


ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 30
SECRET = "201d573bd7d1344d3a3bfce1550b69102fd11be3db6d379508b6cccc58ea230b"

router = APIRouter(prefix="/auth", tags=["auth"], responses={404: {"description": "Not found"}})

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])

def buscar_user(username: str):
    
    user = user_schema(db_client.local.users.find_one({"username": username}))
    if username in user:
        
        return User(**user_schema(user))
    
async def auth_user(token: str = Depends(oauth2)):
    
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"})

    try:
        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub")
        print (username)
        if username is None:
            raise exception

    except JWTError:
        
        return {"error": "error"}
        raise exception

    return buscar_user(username)


async def user_actual(user: User = Depends(auth_user)):
    
    userdict = dict(user)
    
    if userdict["disabled"] is True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo")
    
    return user

#REGISTRO DE USUARIOS
@router.post("/signin", response_model=UserDB, status_code=status.HTTP_201_CREATED)
async def new_user(user: UserDB):
    
    userdict = dict(user)
    userdict["disabled"] = True
    del userdict["id"]
    
    if userdict["username"] in db_client.local.users.distinct("username"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya existe")
    
    #MongoDB asigna un id automáticamente
    id = db_client.local.users.insert_one(userdict).inserted_id
    
    new_user = user_schema(db_client.local.users.find_one({"_id": id}))
    
    #encriptamos la contraseña
    new_user["password"] = crypt.hash(new_user["password"])
    
    #Insertamos la nueva contraseña encriptada en la base de datos
    #$set sirve para actualizar un campo específico, en este caso la contraseña
    db_client.local.users.update_one({"_id": id}, {"$set": new_user})
    
    return UserDB(**new_user)
    
    
#ACTUALIZACIÓN DE USUARIOS
@router.put("/update", response_model=UserDB, status_code=status.HTTP_200_OK)
async def update(user: UserDB ):#= Depends(user_actual)

    userdict = dict(user)
    userdict["disabled"] = False
    
    if userdict["username"] not in db_client.local.users.distinct("username"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no existe")
    
    #Actualiza el usuario
    db_client.local.users.update_one({"username": userdict["username"]}, {"$set": userdict})
    
    return UserDB(**userdict)

#"INICIO DE SESIÓN"
@router.post("/login", response_model=UserDB, status_code=status.HTTP_200_OK)
async def login(form: OAuth2PasswordRequestForm = Depends()):
   
    user_db = db_client.local.users.find_one({"username": form.username})
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")
    
    #Verificamos la contraseña
    if not crypt.verify(form.password, user_db["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña no es correcta")
        
    #Creamos el token
    token = jwt.encode(
        {"sub": user_db["username"], "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)},
        SECRET, algorithm=ALGORITHM)
    
    #Actualizamos el token en la base de datos
    db_client.local.users.update_one({"username": user_db["username"]}, {"$set": {"token": token}})
    
    #Retornamos el usuario
    return UserDB(**user_db)

#CONSULTA DEL USUARIO POR ID
@router.get("/users/{id}", response_model=UserDB, status_code=status.HTTP_200_OK)
async def user_by_id(id: str = Depends(user_actual)):

    return  db_client.local.users.find_one({"_id": ObjectId(id)})

#CONSULTA DEL USUARIO ACTUAL
@router.get("/me", response_model=UserDB, status_code=status.HTTP_200_OK)
async def me(user: User):#= Depends(user_actual)
    
    return user
    
#"CONSULTA DE USUARIOS"
@router.get("/users", response_model=list[UserDB], status_code=status.HTTP_200_OK)
async def users():
    return users_schema(db_client.local.users.find())

# #ELIMINACIÓN DE USUARIOS
@router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
async def delete(id: str = Depends(user_actual)):
        
        found = db_client.local.users.find_one_and_delete({"_id": ObjectId(id)})
        
        if not found:
            return {"message": "Usuario no encontrado"}
