import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Task, StudySession


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
        user = User(username='anuser', email='an@example.com')
        user.set_password('password123')
        db.session.add(user)

        tasks = [
            Task(user_id=1, title='T1', subject='Maths', difficulty=3,
                 priority='high', estimated_hours=2, status='completed'),
            Task(user_id=1, title='T2', subject='Science', difficulty=2,
                 priority='medium', estimated_hours=1.5, status='pending'),
            Task(user_id=1, title='T3', subject='Maths', difficulty=4,
                 priority='high', estimated_hours=3, status='in_progress'),
        ]
        for t in tasks:
            db.session.add(t)
        db.session.commit()

    client.post('/auth/login', data={'email': 'an@example.com', 'password': 'password123'})
    return client


def test_summary_api(auth_client):
    response = auth_client.get('/analytics/api/summary')
    assert response.status_code == 200
    data = response.get_json()
    for key in ('total', 'completed', 'pending', 'completion_rate', 'avg_difficulty'):
        assert key in data


def test_weekly_progress(auth_client):
    response = auth_client.get('/analytics/api/weekly_progress')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 7
    assert 'date' in data[0] and 'completed' in data[0]


def test_subject_breakdown(auth_client):
    response = auth_client.get('/analytics/api/subject_breakdown')
    assert response.status_code == 200
    data = response.get_json()
    subjects = [d['subject'] for d in data]
    assert 'Maths' in subjects


def test_streak_calculation(app, auth_client):
    with app.app_context():
        user = User.query.filter_by(email='an@example.com').first()
        task = Task.query.filter_by(user_id=user.id).first()
        for i in range(3):
            day = datetime.utcnow() - timedelta(days=i)
            session = StudySession(
                user_id=user.id,
                task_id=task.id,
                start_time=day,
                end_time=day + timedelta(hours=1),
                duration_minutes=60,
            )
            db.session.add(session)
        db.session.commit()

    response = auth_client.get('/analytics/api/streak')
    assert response.status_code == 200
    data = response.get_json()
    assert data['streak'] >= 3
