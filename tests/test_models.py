from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session):
    user = User(
        username='usuario.teste', password='secret', email='usuario@test.com'
    )

    session.add(user)
    session.commit()

    result = session.scalar(
        select(User).where(User.email == 'usuario@test.com')
    )

    assert result.username == 'usuario.teste'
    assert result.email == 'usuario@test.com'
    assert result.password == 'secret'
