import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Task, TimetableSlot
from app.timetable.algorithm import TimetableGenerator


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
        user = User(username='ttuser', email='tt@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
    client.post('/auth/login', data={'email': 'tt@example.com', 'password': 'password123'})
    return client


@pytest.fixture
def sample_tasks(app):
    with app.app_context():
        user = User.query.filter_by(email='tt@example.com').first()
        tasks = [
            Task(user_id=user.id, title='Task A', subject='Maths', difficulty=4,
                 priority='high', estimated_hours=3,
                 deadline=datetime.utcnow() + timedelta(days=2)),
            Task(user_id=user.id, title='Task B', subject='Science', difficulty=2,
                 priority='medium', estimated_hours=2,
                 deadline=datetime.utcnow() + timedelta(days=7)),
            Task(user_id=user.id, title='Task C', subject='History', difficulty=3,
                 priority='low', estimated_hours=1.5,
                 deadline=datetime.utcnow() + timedelta(days=14)),
        ]
        for t in tasks:
            db.session.add(t)
        db.session.commit()


def test_generate_timetable(app, auth_client, sample_tasks):
    response = auth_client.post('/timetable/generate', follow_redirects=False)
    assert response.status_code == 302
    with app.app_context():
        user = User.query.filter_by(email='tt@example.com').first()
        slots = TimetableSlot.query.filter_by(user_id=user.id).all()
        assert len(slots) > 0


def test_slots_api(app, auth_client, sample_tasks):
    auth_client.post('/timetable/generate')
    response = auth_client.get('/timetable/api/slots')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_algorithm_urgency():
    gen = TimetableGenerator(user_id=1)
    urgent = gen._calculate_urgency(datetime.utcnow() + timedelta(days=1))
    not_urgent = gen._calculate_urgency(datetime.utcnow() + timedelta(days=30))
    assert urgent > not_urgent


def test_algorithm_balance(app):
    with app.app_context():
        user = User(username='baluser', email='bal@example.com')
        user.set_password('pass')
        db.session.add(user)
        db.session.commit()

        tasks = [
            Task(user_id=user.id, title=f'Task {i}', subject=f'Sub{i}',
                 difficulty=3, priority='medium', estimated_hours=2,
                 deadline=datetime.utcnow() + timedelta(days=5 + i))
            for i in range(3)
        ]
        for t in tasks:
            db.session.add(t)
        db.session.commit()

        gen = TimetableGenerator(user_id=user.id)
        slots = gen.generate(tasks)
        days_used = {s.day_of_week for s in slots if s.slot_type == 'study'}
        assert len(days_used) >= 2


def test_clear_timetable(app, auth_client, sample_tasks):
    auth_client.post('/timetable/generate')
    auth_client.post('/timetable/clear')
    with app.app_context():
        user = User.query.filter_by(email='tt@example.com').first()
        slots = TimetableSlot.query.filter_by(user_id=user.id).all()
        assert len(slots) == 0
