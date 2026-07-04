from pydantic import BaseModel

class AdminLoginReq(BaseModel):
    username: str
    password: str