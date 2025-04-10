from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, Token, UserList, UserPublic, UserSchema
from fast_zero.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)

app = FastAPI()
database = []


@app.get('/', response_class=HTMLResponse)
def read_root():
    html = """
    <html>
        <head>
            <title>Olá, mundo!</title>
        </head>
        <body>
            <h1>Olá, mundo!</h1>
        </body>
    </html>
    """
    return html


@app.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session=Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Usuário ou senha inválidos',
            # headers={'WWW-Authenticate': 'Bearer'},
        )

    access_token = create_access_token(data_payload={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'Bearer'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session=Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Usuário já existe',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email já existe',
            )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users/', response_model=UserList)
def read_users(skip: int = 0, limit: int = 10, session=Depends(get_session)):
    users = session.scalars(select(User).offset(skip).limit(limit))
    return {'users': users}


@app.get('/users/{user_id}', response_model=UserPublic)
def read_user(user_id: int, session=Depends(get_session)):
    # db_user = session.get(User, user_id)
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Usuário não encontrado',
        )

    return db_user


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(user_id: int, user: UserSchema, session=Depends(get_session)):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Usuário não encontrado',
        )

    # usuário já existe se houver outro user_id com mesmo username
    outro_usuario_com_mesmo_username = session.scalar(
        select(User)
        .where(User.username == user.username)
        .where(User.id != user_id)
    )
    if outro_usuario_com_mesmo_username:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Usuário já existe',
        )

    # email já existe se houver outro user_id com mesmo email
    outro_usuario_com_mesmo_email = session.scalar(
        select(User).where(User.email == user.email).where(User.id != user_id)
    )
    if outro_usuario_com_mesmo_email:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Email já existe',
        )

    db_user.username = user.username
    db_user.email = user.email
    db_user.password = get_password_hash(user.password)

    session.commit()
    session.refresh(db_user)

    return db_user


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(user_id: int, session=Depends(get_session)):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Usuário não encontrado',
        )

    session.delete(db_user)
    session.commit()

    return {'message': 'Usuário excluído com sucesso'}
