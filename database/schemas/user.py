def user_schema(user) -> dict:
    
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "fullname": user["fullname"],
        "cc": user["cc"],
        "role": user["role"],
        "disabled": user["disabled"],
        "password": user["password"] #encriptada
    }