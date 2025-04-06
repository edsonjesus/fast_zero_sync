from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_read_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')  # Act (ação)
    assert response.status_code == HTTPStatus.OK  # Assert

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
    assert response.text == html


def test_create_user_deve_retornar_created_e_usuario_sem_senha(client):
    # Valida UserSchema
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@email.com',
            'password': '123456',
        },
    )

    # Valida retorno HTTPStatus
    assert response.status_code == HTTPStatus.CREATED

    # Valida UserPublic
    assert response.json() == {
        'username': 'alice',
        'email': 'alice@email.com',
        'id': 1,
    }


def test_create_user_deve_retornar_erro_usuario_ja_existe(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@email.com',
            'password': '123456',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Usuário já existe'}


def test_create_user_deve_retornar_erro_email_ja_existe(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'maria',
            'email': 'alice@email.com',
            'password': '123456',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email já existe'}


def test_read_users_deve_retornar_lista_vazia_de_usuarios(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_deve_retornar_lista_de_usuarios(client, user):
    # Valida se o objeto user do SQLAlchemy
    # pode ser convertido para o schema UserPublic
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_read_user_por_id_deve_retornar_usuario(client, user):
    # user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/1')
    assert response.status_code == HTTPStatus.OK
    # assert response.json() == user_schema
    assert response.json() == {
        'username': 'alice',
        'email': 'alice@email.com',
        'id': 1,
    }


def test_read_user_por_id_deve_retornar_erro_404_quando_usuario_nao_existe(
    client, user
):
    response = client.get('/users/0')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        'detail': 'Usuário não encontrado',
    }


def test_update_user_deve_atualizar_nome_e_email_do_usuario(client, user):
    response = client.put(
        '/users/1',
        json={
            'username': 'alice.maria',
            'email': 'alice@exemplo.com',
            'password': '12345',
            'id': 1,
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'alice.maria',
        'email': 'alice@exemplo.com',
        'id': 1,
    }


def test_update_user_deve_retornar_erro_404_quando_usuario_nao_existe(
    client, user
):
    response = client.put(
        '/users/0',
        json={
            'username': 'usuario.fantasma',
            'email': 'fantasma@exemplo.com',
            'password': '12345',
            'id': 0,
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        'detail': 'Usuário não encontrado',
    }


def test_delete_user_deve_excluir_usuario(client, user):
    response = client.delete('/users/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Usuário excluído com sucesso'}


def test_delete_user_deve_retornar_erro_404_quando_usuario_nao_existe(client):
    response = client.delete('/users/0')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        'detail': 'Usuário não encontrado',
    }
