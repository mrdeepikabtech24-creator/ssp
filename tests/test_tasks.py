import pytest
from app import create_app, db
from app.models import User, Task


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
def auth_client(app, client):
    with app.app_context():
        user = User(username='taskuser', email='task@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
    client.post('/auth/login', data={'email': 'task@example.com', 'password': 'password123'})
    return client


def test_create_task(app, auth_client):
    response = auth_client.post('/tasks/create', data={
        'title': 'Math Assignment',
        'subject': 'Mathematics',
        'difficulty': 3,
        'priority': 'high',
        'estimated_hours': 2.0,
    }, follow_redirects=False)
    assert response.status_code == 302
    with app.app_context():
        task = Task.query.filter_by(title='Math Assignment').first()
        assert task is not None


def test_list_tasks(auth_client):
    response = auth_client.get('/tasks/')
    assert response.status_code == 200


def test_edit_task(app, auth_client):
    with app.app_context():
        user = User.query.filter_by(email='task@example.com').first()
        task = Task(user_id=user.id, title='Old Title', subject='Science', difficulty=2, priority='low')
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    response = auth_client.post(f'/tasks/{task_id}/edit', data={
        'title': 'New Title',
        'subject': 'Science',
        'difficulty': 4,
        'priority': 'high',
    }, follow_redirects=False)
    assert response.status_code == 302
    with app.app_context():
        updated = Task.query.get(task_id)
        assert updated.title == 'New Title'


def test_delete_task(app, auth_client):
    with app.app_context():
        user = User.query.filter_by(email='task@example.com').first()
        task = Task(user_id=user.id, title='To Delete', subject='History', difficulty=1, priority='low')
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    auth_client.post(f'/tasks/{task_id}/delete')
    with app.app_context():
        assert Task.query.get(task_id) is None


def test_complete_task(app, auth_client):
    with app.app_context():
        user = User.query.filter_by(email='task@example.com').first()
        task = Task(user_id=user.id, title='To Complete', subject='Physics', difficulty=3, priority='medium')
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    response = auth_client.post(f'/tasks/{task_id}/complete')
    assert response.status_code == 200
    with app.app_context():
        task = Task.query.get(task_id)
        assert task.status == 'completed'


def test_unauthenticated_redirect(client):
    response = client.get('/tasks/', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']
