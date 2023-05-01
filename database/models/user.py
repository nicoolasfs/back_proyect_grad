from pydantic import BaseModel

class User(BaseModel):
    id: str | None
    username: str
    fullname: str 
    cc: str
    role: str 
    disabled: bool | None
    
class UserDB(User):
    password: str