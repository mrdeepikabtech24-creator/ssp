import pytest
from app import create_app, db
from app.models import User


@pytest.fixture
def app():
    application = create_app('testing')
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def registered_user(app):
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
    return {'email': 'test@example.com', 'password': 'password123'}


def test_register_success(client):
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123',
        'confirm_password': 'password123',
    }, follow_redirects=False)
    assert response.status_code == 302


def test_register_duplicate_email(client, registered_user):
    response = client.post('/auth/register', data={
        'username': 'anotheruser',
        'email': registered_user['email'],
        'password': 'password123',
        'confirm_password': 'password123',
    })
    assert b'already registered' in response.data or response.status_code == 200


def test_login_success(client, registered_user):
    response = client.post('/auth/login', data={
        'email': registered_user['email'],
        'password': registered_user['password'],
    }, follow_redirects=False)
    assert response.status_code == 302


def test_login_wrong_password(client, registered_user):
    response = client.post('/auth/login', data={
        'email': registered_user['email'],
        'password': 'wrongpassword',
    })
    assert b'Invalid' in response.data or response.status_code in (200, 401)


def test_logout(client, registered_user):
    client.post('/auth/login', data={
        'email': registered_user['email'],
        'password': registered_user['password'],
    })
    response = client.get('/auth/logout', follow_redirects=False)
    assert response.status_code == 302
