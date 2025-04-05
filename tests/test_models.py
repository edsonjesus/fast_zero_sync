from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session):
    user = User(username='test', password='secret', email='test@test.com')
    assert user.username == 'test'
    assert user.password == 'secret'
    session.add(user)
    session.commit()
    result = session.scalar(select(User).where(User.email == 'test@test.com'))
    assert result.username == 'test'
