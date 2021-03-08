from app.tasks import bp
from flask import render_template, url_for, redirect, request, current_app, flash, session
from flask_login import login_required, current_user
from app import db
from app.models import Task, User, Schedule, TaskWeek, Outlet
from app.enums import Role, TaskType
from app.schemas import TaskWeekCollectionSchema, TaskSchema
from app.utils.date_utils import isoparse, get_current_week, to_timezone
from app.tasks.forms import TaskForm, DeleteTaskForm

from datetime import datetime, timedelta
import json

@bp.route('/<username>', methods=["GET", "POST"])
@login_required
def user_tasks(username):
    if username != current_user.username and current_user.role != Role.SALES_REP_LEAD:
        return redirect(url_for('tasks.user_tasks', username=current_user.username))

    create_task_form = TaskForm()
    outlet_choices = [(outlet.id, outlet.name) for outlet in current_user.outlets]
    create_task_form.outlet.choices = outlet_choices
    if create_task_form.validate_on_submit():
        valid = True
        
        title = create_task_form.title.data
        description = create_task_form.description.data
        start = create_task_form.start.data
        end = create_task_form.end.data
        if start > end:
            flash("Invalid date")
            valid = False
            
        estimated_time = create_task_form.estimated_time.data.hour*60 + create_task_form.estimated_time.data.minute
        repeat_count = create_task_form.repeat_count.data
        outlet_id = create_task_form.outlet.data
        outlet = current_user.outlets.filter(Outlet.id == outlet_id).first()
        if not outlet:
            flash("Invalid outlet ID")
            valid = False

        if valid:
            task = Task(creator=current_user, type=TaskType.CUSTOM, title=title, description=description, start_date=start, end_date=end,
                        service_time=estimated_time, repeat_count=repeat_count, outlet=outlet, rep=current_user, assigner=current_user)
            weeks = TaskWeek.create_task_weeks(task, session['timezone'])
            db.session.add(task, weeks)
            db.session.commit()

    delete_task_form = DeleteTaskForm() 
    task_choices = [(task.id, f"(ID: {task.id}) {task.title}") for task in current_user.tasks if task.is_task_deletable(current_user)]
    delete_task_form.task_id.choices = task_choices
    if delete_task_form.validate_on_submit():
        valid = True
        task = current_user.tasks.filter(Task.id == delete_task_form.task_id.data).first()
        if not task:
            valid = False
            flash('Invalid Task')

        if not task.is_task_deletable(current_user):
            valid = False
            flash('Invalid Task')
        
        if valid:
            flash(f'Task {task.id} successfully deleted')
            db.session.delete(task)
            db.session.commit()
            task_choices = [(task.id, f"(ID: {task.id}) {task.title}") for task in current_user.tasks if task.is_task_deletable(current_user)]
            delete_task_form.task_id.choices = task_choices

    start = request.args.get('start')
    end = request.args.get('end')
    if start:
        start = isoparse(start)
    else:
        start = get_current_week(datetime.utcnow(), session['timezone'])[0]
    if end:
        end = isoparse(end)
    else:
        end = start + timedelta(days=current_app.config['DAYS_PER_WEEK'])

    current_task_week = TaskWeek.query.filter(TaskWeek.end_date >= start).filter(TaskWeek.start_date < end)
    mandatory_tasks = current_task_week.join(Task, Task.id == TaskWeek.task_id).filter(Task.type == TaskType.MANDATORY).join(User, User.id == Task.rep_id).filter(User.username == username).order_by(Task.id.desc()).all()
    custom_tasks = current_task_week.join(Task, Task.id == TaskWeek.task_id).filter(Task.type == TaskType.CUSTOM).join(User, User.id == Task.rep_id).filter(User.username == username).order_by(Task.id.desc()).all()
    schedules = Schedule.get_schedule(current_user, start_date=datetime.utcnow())
    return render_template('tasks/tasks.html', title='My Tasks', mandatory_tasks=mandatory_tasks, custom_tasks=custom_tasks, upcoming_schedules=schedules, start=start, end=end, create_task_form=create_task_form, delete_task_form=delete_task_form)    

@bp.route('/<username>/task', methods=["GET"])
@login_required
def task_data(username):
    if username != current_user.username and current_user.role != Role.SALES_REP_LEAD:
        return redirect(url_for('tasks.user_tasks', username=current_user.username))

    task_id = request.args.get('task_id')
    task = current_user.tasks.filter(Task.id == task_id).first()

    return {'task': TaskSchema().dump(task)}

@bp.route('/<username>/week/data', methods=["GET"])
@login_required
def taskweek_data(username):
    if username != current_user.username and current_user.role != Role.SALES_REP_LEAD:
        return redirect(url_for('tasks.user_tasks', username=current_user.username))
    query = TaskWeek.query
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    if start_date:
        start_date = isoparse(start_date)
        query = query.filter(TaskWeek.start_date >= start_date)
    if end_date:
        end_date = isoparse(end_date)
        query = query.filter(TaskWeek.end_date <= end_date)
   
    task_weeks = query.join(Task, Task.id == TaskWeek.task_id).join(User, User.id == Task.rep_id).filter(User.username == username).order_by(Task.id.desc()).all()
    return_obj = {"weeks": task_weeks}
    return TaskWeekCollectionSchema().dumps(return_obj)