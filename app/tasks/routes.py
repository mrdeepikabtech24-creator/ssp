from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from . import tasks_bp
from ..models import Task
from .. import db


@tasks_bp.route('/')
@login_required
def list_tasks():
    status_filter = request.args.get('status', 'all')
    query = Task.query.filter_by(user_id=current_user.id)
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    tasks = query.order_by(Task.deadline.asc()).all()
    return render_template('tasks/list.html', tasks=tasks, status_filter=status_filter)


@tasks_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_task():
    if request.method == 'POST':
        deadline_str = request.form.get('deadline')
        deadline = datetime.fromisoformat(deadline_str) if deadline_str else None
        task = Task(
            user_id=current_user.id,
            title=request.form['title'],
            description=request.form.get('description', ''),
            subject=request.form.get('subject', ''),
            difficulty=int(request.form.get('difficulty', 3)),
            deadline=deadline,
            priority=request.form.get('priority', 'medium'),
            estimated_hours=float(request.form.get('estimated_hours') or 0) or None,
        )
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully.', 'success')
        return redirect(url_for('tasks.list_tasks'))
    return render_template('tasks/create.html')


@tasks_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        deadline_str = request.form.get('deadline')
        task.title = request.form['title']
        task.description = request.form.get('description', '')
        task.subject = request.form.get('subject', '')
        task.difficulty = int(request.form.get('difficulty', 3))
        task.deadline = datetime.fromisoformat(deadline_str) if deadline_str else None
        task.priority = request.form.get('priority', 'medium')
        task.estimated_hours = float(request.form.get('estimated_hours') or 0) or None
        task.status = request.form.get('status', task.status)
        db.session.commit()
        flash('Task updated.', 'success')
        return redirect(url_for('tasks.list_tasks'))
    return render_template('tasks/create.html', task=task)


@tasks_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_task(id):
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted.', 'success')
    return redirect(url_for('tasks.list_tasks'))


@tasks_bp.route('/<int:id>/complete', methods=['POST'])
@login_required
def complete_task(id):
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    task.status = 'completed'
    db.session.commit()
    return jsonify({'status': 'completed'})


@tasks_bp.route('/api/list')
@login_required
def api_list():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify([t.to_dict() for t in tasks])
