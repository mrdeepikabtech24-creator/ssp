from datetime import datetime, timedelta
from flask import render_template, jsonify
from flask_login import login_required, current_user
from . import analytics_bp
from ..models import Task, StudySession
from .. import db
from sqlalchemy import func


@analytics_bp.route('/')
@login_required
def dashboard():
    return render_template('analytics/dashboard.html')


@analytics_bp.route('/api/summary')
@login_required
def summary():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    total = len(tasks)
    completed = sum(1 for t in tasks if t.status == 'completed')
    pending = sum(1 for t in tasks if t.status == 'pending')
    in_progress = sum(1 for t in tasks if t.status == 'in_progress')
    completion_rate = round((completed / total * 100), 1) if total else 0
    avg_difficulty = round(sum(t.difficulty for t in tasks) / total, 1) if total else 0
    return jsonify({
        'total': total,
        'completed': completed,
        'pending': pending,
        'in_progress': in_progress,
        'completion_rate': completion_rate,
        'avg_difficulty': avg_difficulty,
    })


@analytics_bp.route('/api/weekly_progress')
@login_required
def weekly_progress():
    today = datetime.utcnow().date()
    result = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = day_start + timedelta(days=1)
        count = Task.query.filter(
            Task.user_id == current_user.id,
            Task.status == 'completed',
            Task.created_at >= day_start,
            Task.created_at < day_end,
        ).count()
        result.append({'date': day.isoformat(), 'completed': count})
    return jsonify(result)


@analytics_bp.route('/api/subject_breakdown')
@login_required
def subject_breakdown():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    breakdown = {}
    for task in tasks:
        subject = task.subject or 'Unassigned'
        hours = task.estimated_hours or 0
        breakdown[subject] = breakdown.get(subject, 0) + hours
    return jsonify([{'subject': k, 'hours': round(v, 1)} for k, v in breakdown.items()])


@analytics_bp.route('/api/streak')
@login_required
def streak():
    today = datetime.utcnow().date()
    streak_count = 0
    current_day = today
    while True:
        day_start = datetime.combine(current_day, datetime.min.time())
        day_end = day_start + timedelta(days=1)
        session_exists = StudySession.query.filter(
            StudySession.user_id == current_user.id,
            StudySession.start_time >= day_start,
            StudySession.start_time < day_end,
        ).first()
        if session_exists:
            streak_count += 1
            current_day -= timedelta(days=1)
        else:
            break
    return jsonify({'streak': streak_count})
