from datetime import datetime
from flask import render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from . import timetable_bp
from .algorithm import TimetableGenerator
from ..models import Task, TimetableSlot
from .. import db


@timetable_bp.route('/')
@login_required
def view():
    week_number = datetime.utcnow().isocalendar()[1]
    slots = TimetableSlot.query.filter_by(
        user_id=current_user.id, week_number=week_number
    ).all()
    return render_template('timetable/view.html', slots=slots)


@timetable_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.status != 'completed'
    ).all()
    if not tasks:
        flash('No pending tasks to schedule.', 'warning')
        return redirect(url_for('timetable.view'))

    week_number = datetime.utcnow().isocalendar()[1]
    TimetableSlot.query.filter_by(
        user_id=current_user.id, week_number=week_number
    ).delete()

    generator = TimetableGenerator(user_id=current_user.id)
    slots = generator.generate(tasks)
    for slot in slots:
        db.session.add(slot)
    db.session.commit()
    flash(f'Timetable generated with {len(slots)} slots.', 'success')
    return redirect(url_for('timetable.view'))


@timetable_bp.route('/api/slots')
@login_required
def api_slots():
    week_number = datetime.utcnow().isocalendar()[1]
    slots = TimetableSlot.query.filter_by(
        user_id=current_user.id, week_number=week_number
    ).all()
    return jsonify([s.to_dict() for s in slots])


@timetable_bp.route('/clear', methods=['POST'])
@login_required
def clear():
    TimetableSlot.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('Timetable cleared.', 'info')
    return redirect(url_for('timetable.view'))
