from pydantic import BaseModel, EmailStr


class UserScheme(BaseModel):
    id: int
    username: str
    email: EmailStr
    phone: str | None
    first_name: str | None
    last_name: str | None
