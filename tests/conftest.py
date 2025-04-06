import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry


@pytest.fixture
def client(session):
    """Fixture para criar um cliente de teste FastAPI
    com uma sessão de banco de dados em memória."""

    def get_test_session():
        return session

    with TestClient(app) as client:
        # Sobrescreve a dependência get_session de produção
        # pela sessão de teste (sqlite em memória)
        app.dependency_overrides[get_session] = get_test_session

        yield client

    # Limpa as dependências sobrescritas após o teste
    app.dependency_overrides.clear()


@pytest.fixture
def session():
    """Fixture para criar uma sessão de banco de dados em memória."""
    engine = create_engine(
        'sqlite:///:memory:',
        # Para evitar o erro "SQLite objects created in a thread
        # can only be used in that same thread"
        connect_args={'check_same_thread': False},
        # Usa o mesmo recurso e não verifica se está na mesma thread
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@pytest.fixture
def user(session):
    """Fixture para criar um usuário de teste no banco de dados."""
    user = User(username='alice', email='alice@email.com', password='123456')
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
