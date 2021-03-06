from app.calendar import bp
from app import db
from flask import render_template, url_for, redirect, current_app, flash, request, session
from flask_login import login_required, current_user
from app.calendar.forms import ScheduleTaskForm
from app.models import Task, User, Schedule
from app.enums import Role, TaskType
from app.utils.serializers import is_true, serialize_collection
from app.utils.date_utils import get_current_week, isoparse, to_timezone
from app.utils.adapters import schedule_to_fullcalendar, task_to_customer
from app.utils.math import euclidean_distance
from app.optimizer.interface import Config, solve, depot
from app.schemas import ScheduleSchema, TaskSchema
from datetime import datetime, time, timedelta
import json
import math

@bp.route('/<username>', methods=['GET','POST'])
@login_required
def planner(username):
    if username != current_user.username and current_user.role != Role.SALES_REP_LEAD:
        return redirect(url_for('calendar.planner', username=current_user.username))

    start_date = isoparse(request.args.get('start')) or get_current_week(datetime.utcnow(), session['timezone'])[0]
    schedule_task_form = ScheduleTaskForm() 
    task_choices = [(task.id, f"(ID: {task.id}) {task.title}") for task in current_user.tasks]
    schedule_task_form.task_id.choices = task_choices
    if schedule_task_form.validate_on_submit():
        valid = True

        task = Task.query.filter(Task.id == schedule_task_form.task_id.data).first()
        if task.rep.id != current_user.id:
            flash('Invalid task')
            valid = False

        start = schedule_task_form.start.data #In UTC time, it is the forms job of converting from local to UTC
        end = schedule_task_form.end.data
        if start > end:
            flash('Invalid date')
            valid = False

        if end - start >= timedelta(days=current_app.config['TASK_SCHEDULE_LIMIT']):
            flash(f'Tasks can only be scheduled for {current_app.config["TASK_SCHEDULE_LIMIT"]} days')
            valid = False

        week = get_current_week(start)
        if not Schedule.is_task_scheduled(task, week[0], week[-1]):
            flash(f'Task {schedule_task_form.task_id.data} has already been scheduled for this week')
            valid = False
        
        elif not Schedule.is_schedule_available(current_user, start, end):
            flash('A task has already been scheduled at that time')
            valid = False
        
        if valid:
            if to_timezone(start, to_timezone=session['timezone']).time() < time(8, 0, 0) or to_timezone(end, to_timezone=session['timezone']).time() > time(20, 0, 0): #TODO: working hours
                flash('You have scheduled a task outside of your working hours')

            schedule = Schedule(start=start, end=end, rep=current_user, task=task)
            db.session.add(schedule)
            db.session.commit()

            start_date = get_current_week(start, session['timezone'])[0]
    
    unscheduled_tasks = Task.get_unscheduled_tasks(current_user, start_date=start_date, end_date=start_date+timedelta(days=6))
    return render_template('calendar/calendar.html', title='Calendar', all_tasks=unscheduled_tasks, schedule_task_form=schedule_task_form, start_date=start_date)

@bp.route('/<username>/schedule/data', methods=["GET", "POST", "DELETE"])
@login_required
def schedule_data(username):
    if username != current_user.username and current_user.role != Role.SALES_REP_LEAD:
        return redirect(url_for('tasks.user_tasks', username=current_user.username))
    
    start_date = isoparse(request.args.get('start'))
    end_date = isoparse(request.args.get('end'))
    data = request.get_json()
    if data:
        if request.method == 'DELETE':
            print('delete')
            valid = True
            
            schedule_id = data['task']['id']
            schedule = Schedule.query.filter(Schedule.id == schedule_id).first()

            if not schedule:
                valid = False
                
            current_week = get_current_week(isoparse(data['task']['start']))
            if not start_date and not end_date:
                start_date = current_week[0]
                end_date = current_week[-1]

            if valid:    
                db.session.delete(schedule)
                db.session.commit()

        elif request.method == 'POST':
            valid = True

            schedules = []
            for schedule in data['tasks']:
                rep = User.query.filter(User.id == schedule['rep_id']).first()
                if not rep:
                    valid = False
                    break
                task = rep.tasks.filter(Task.id == schedule['task_id']).first()
                schedules.append(Schedule(start=isoparse(schedule['start']), end=isoparse(schedule['end']), rep=rep, task=task))
            
            current_week = get_current_week(isoparse(schedule['start']))
            if not start_date and not end_date:
                start_date = current_week[0]
                end_date = current_week[-1]
                
            if valid:
                db.session.add_all(schedules)
                db.session.commit()
    
    unscheduled = is_true(request.args.get('unscheduled'))
    result = {}
    if unscheduled:
        unscheduled_tasks = Task.get_unscheduled_tasks(current_user, start_date=start_date, end_date=end_date)
        result['tasks'] = TaskSchema().dump(unscheduled_tasks, many=True)
    
    else:
        schedules = Schedule.get_schedule(current_user, start_date=start_date, end_date=end_date)
        result['tasks'] = [schedule_to_fullcalendar(schedule, session['timezone']) for schedule in schedules]
        result['stats'] = calculate_stats(schedules, start_date, depot)

    return result

@bp.route('/<username>/optimize', methods=["GET"])
@login_required
def optimize_schedule(username):
    if username != current_user.username and current_user.role != Role.SALES_REP_LEAD:
        return redirect(url_for('tasks.user_tasks', username=current_user.username))
 
    start = isoparse(request.args.get('start'))
    end = isoparse(request.args.get('end'))

    if not start:
        return {"tasks": {} }
 
    if not end:
        end = get_current_week(start)[-3] #friday

    #unscheduled_tasks = Task.get_unscheduled_tasks(current_user, start, end)
    #optimized_schedule = optimize(unscheduled_tasks, start)
    result = \
    {
        "tasks": [],
        "stats": {}
    }

    tasks = current_user.tasks.filter(Task.start_date <= end).filter(Task.end_date >= start).all()

    if len(tasks) < 1:
        return result

    optimized_schedule = optimize(current_user, tasks, start)
    result["tasks"] = [schedule_to_fullcalendar(schedule, session['timezone']) for schedule in optimized_schedule['schedule']]
    result["stats"] = optimized_schedule['stats']

    return result


def optimize(user, tasks, start):
    config = Config()
    config.set_optional_customers(tasks)
    solution = solve(config)

    output = {}
    output['schedule'] = []
    outlets = set()
    output['stats'] = \
    {
        "total_distance": 0.0,
        "total_value": 0.0,
        "num_tasks": 0,
        "num_outlets": 0,
    }
    for day, tasks in solution.items():
        for task in tasks:
            start_date = start + timedelta(days=day, minutes=task.get('start_time'))
            end_date = start + timedelta(days=day, minutes=task.get('end_time'))
            user_task = user.tasks.filter(Task.id == task.get('task_id')).first() #task ID 
            output['schedule'].append(Schedule(start=start_date, end=end_date, rep=user, task=user_task)) 
            output['stats']['total_distance'] += task.get('travel_time')
            output['stats']['total_value'] += task.get('value')
            output['stats']['num_tasks'] += 1
            outlets.add(task.get('id'))
    
    output['stats']['num_outlets'] = len(outlets)

    db.session.flush()
 
    print(output['schedule'])

    return output

#schedules must be sorted according to date
#start date must already be adjusted to user timezone
def calculate_stats(schedules, start, depot): 
    stats = \
    {
        "total_distance": 0.0,
        "total_value": 0.0,
        "num_tasks": 0,
        "num_outlets": 0,
    }

    outlets = set()
    day = -1
    schedule_by_day = {}

    if len(schedules) < 1:
        return stats

    for schedule in schedules:
        while schedule.start - start > timedelta(days=day):
            day += 1
            schedule_by_day[day] = [depot, depot]

        schedule_by_day[day].insert(-1, task_to_customer(schedule.task))

    for day, customers in schedule_by_day.items():
        for i in range(1, len(customers)):
            customer = customers[i]
            prev_customer = customers[i-1]
            stats['total_distance'] += round(euclidean_distance(prev_customer.info.x, prev_customer.info.y, customer.info.x, customer.info.y), 4)
            if customer.info.id != depot.info.id:
                stats['total_value'] += round(customer.info.value, 4)
                stats['num_tasks'] += 1
                outlets.add(customer.info.taskID)
    stats['num_outlets'] = len(outlets)

    return stats