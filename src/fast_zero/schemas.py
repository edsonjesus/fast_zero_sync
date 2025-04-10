from pydantic import BaseModel, ConfigDict, EmailStr


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserDB(UserSchema):
    id: int


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    # Quando carregar objetos, validar pelos atributos
    # (importante para os testes)
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str  # O token que vamos gerar
    token_type: str  # O modelo que o cliente deve usar para Autorização
