from app import db, login
from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app.enums import Zone, TaskStatus, TaskType, Role, Day
from app.utils.date_utils import get_current_week, get_week_range, to_timezone

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), index=True, unique=True)
    email = db.Column(db.String(254), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    name = db.Column(db.String(64), index=True)
    contact_num = db.Column(db.String(30), index=True, unique=True)
    zone = db.Column(db.Enum(Zone))
    address = db.Column(db.String(200))
    role = db.Column(db.Enum(Role))
    outlets = db.relationship('Outlet', backref='rep', lazy="dynamic")
    tasks = db.relationship('Task', backref='rep', lazy="dynamic", foreign_keys="Task.rep_id")
    created_tasks = db.relationship('Task', backref='creator', lazy="dynamic", foreign_keys="Task.creator_id")
    remarks = db.relationship('Remark', backref='rep', lazy='dynamic')
    schedule = db.relationship('Schedule', backref='rep', lazy='dynamic')

    def __init__(self, username=None, password=None, email=None, name=None, contact_num=None, zone=None,
                 address=None, role=None, timezone=None):
        self.username = username
        self.set_password(password)
        self.email = email
        self.name = name
        self.contact_num = contact_num
        if zone:
            self.assign_zone(zone)

        if role:
            self.assign_role(role)

        self.timezone = timezone

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, 'sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    def assign_task(self, task, assigner):
        if self.is_task_assignable(task, assigner):
            self.tasks.append(task)
            #CHANGE TASK STATUS

    def is_task_assignable(self, task, assigner):
        if assigner.role == Role.SALES_REP: #Sales Rep can only assign custom tasks to themselves
            if task.type == TaskType.CUSTOM and self.is_same_zone(task.outlet) and self.is_assigned_outlet(task.outlet) and assigner.id == self.id:
                return True

        if assigner.role == Role.SALES_REP_LEAD: #Sales Rep Lead can assign any valid tasks to anyone
            if self.is_same_zone(task.outlet) and self.is_assigned_outlet(task.outlet): #NOT MY PART
                return True

        return False

    def unassign_task(self, task):
        self.tasks.remove(task)
        #CHANGE TASK STATUS

    def unassign_tasks(self):
        for task in self.tasks:
            self.unassign_task(task)

    def assign_outlet(self, outlet):
        if self.is_same_zone(outlet):
            self.outlets.append(outlet)
 
    def is_outlet_assignable(self, outlet):
        if self.is_same_zone(outlet):
            return True
        else:
            return False
    
    def is_assigned_outlet(self, outlet):
        if outlet.is_assigned_rep():
            return self.id == outlet.rep.id

        return False

    def unassign_outlet(self, outlet):
        self.outlets.remove(outlet)

    def unassign_outlets(self):
        for outlet in self.outlets:
            self.unassign_outlet(outlet)

    def unassign_zone_outlets_tasks(self):
        self.unassign_zone()
        self.unassign_outlets()
        self.unassign_tasks()

    def unassign_outlet_tasks(self, outlet):
        self.unassign_outlet(outlet)
        for task in outlet.tasks:
            self.unassign_task(task)

    def assign_zone(self, zone: Zone):
        if not isinstance(zone, Zone):
            raise ValueError("User - Invalid zone")
            
        self.zone = zone

    def unassign_zone(self):
        self.zone = None

    def is_same_zone(self, outlet):
        if self.zone == outlet.zone and self.zone is not None and outlet.zone is not None:
            return True
        else:
            return False

    def assign_role(self, role: Role):
        if not isinstance(role, Role):
            raise ValueError("User - Invalid zone")
            
        self.role = role

    def unassign_role(self):
        self.role = None

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Outlet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True)
    location = db.Column(db.String(200), index=True)
    zone = db.Column(db.Enum(Zone))
    value = db.Column(db.Numeric(precision=5))
    contact_num = db.Column(db.String(30))
    email = db.Column(db.String(254), index=True)
    rep_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    available_times = db.relationship('AvailableTime', backref='outlet', lazy='dynamic')
    tasks = db.relationship('Task', backref='outlet', lazy='dynamic')
    x = db.Column(db.String(20))
    y = db.Column(db.String(20))

    def __init__(self, name=None, location=None, zone=None, value=None, x=None, y=None, contact_num=None, email=None, rep=None):
        self.name = name
        self.location = location
        if zone:
            self.assign_zone(zone)
        
        self.x = x
        self.y = y
        self.value = value
        self.contact_num = contact_num
        self.email = email

        if rep:
            self.assign_rep(rep)
    
    def assign_rep(self, rep):
        rep.assign_outlet(self)

    def unassign_rep(self):
        self.rep.unassign_outlet(self)

    def assign_zone(self, zone: Zone):
        if isinstance(zone, Zone):
            self.zone = zone

    def get_available_time(self, day: int):
        times = self.available_times.filter(AvailableTime.day == day).all()
        return times

    def get_available_times(self):
        times = self.available_times.all()
        return times

    def is_assigned_rep(self):
        return self.rep is not None

# This special table is stored in local timezone, not UTC
# During optimization, optimization is performed in minutes, and hence 
# relative to local timezone simply because that there will be
# negative values if we did our calculations relative to UTC +0
# The starting date is already offset to UTC+0, so we will just add our optimized schedule
# that is in local to the starting date, effectively shifting the optimized schedule back from local to UTC
class AvailableTime(db.Model):
    __tablename__ = "available_time"
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    day = db.Column(db.Enum(Day))
    outlet_id = db.Column(db.Integer, db.ForeignKey('outlet.id'))

    def __init__(self, day=None, start_time=None, end_time=None, outlet=None):
        self.start_time = start_time
        self.end_time = end_time
        self.day = day
        self.outlet = outlet

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), index=True)
    description = db.Column(db.String(300))
    type = db.Column(db.Enum(TaskType))  #Mandatory or optional
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.Enum(TaskStatus))
    service_time = db.Column(db.Integer)
    repeat_count = db.Column(db.Integer)
    completion_count = db.Column(db.Integer)
    outlet_id = db.Column(db.Integer, db.ForeignKey('outlet.id'))
    rep_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    schedule = db.relationship('Schedule', backref='task', cascade="all", lazy='dynamic')
    weeks = db.relationship('TaskWeek', backref='task', cascade="all", lazy='dynamic')

    def __init__(self, creator, type, title=None, description=None, start_date=datetime.utcnow(), end_date=datetime.utcnow(),
                 service_time=0, repeat_count=0, completion_count=0,
                 outlet=None, rep=None, assigner=None):
        self.title = title
        self.description = description
        self.creator = creator
        self.type = type
        if end_date is not None and start_date is not None:
            if start_date > end_date:
                raise ValueError('Task - Start date exceeds end date')
                
        self.start_date = start_date
        self.end_date = end_date
        if repeat_count < 0:
            raise ValueError('Task - Repeat count less than 0')
        self.repeat_count = repeat_count

        if completion_count < 0:
            raise ValueError('Task - Completion count less than 0')
        self.completion_count = completion_count

        if service_time < 0:
            raise ValueError('Task - Service time less than 0')
        self.service_time = service_time
        self.status = TaskStatus.OPEN
        self.outlet = outlet

        self.update_expiration_status()
        
        if rep:
            self.assign_rep(rep, assigner)

    def update_expiration_status(self):
        if self.status == TaskStatus.OPEN:
            if self.is_task_expired():
                self.set_status(TaskStatus.EXPIRED)
    
    def set_status(self, task_status: TaskStatus):
        if not isinstance(task_status, TaskStatus):
            raise ValueError("Task - Invalid status")
            
        self.status = task_status

    def set_type(self, task_type: TaskType):
        if not isinstance(task_type, TaskStatus):
            raise ValueError("Task - Invalid type")
            
        self.type = task_type

    def assign_rep(self, rep, assigner):
        if rep.is_task_assignable(self, assigner):
            rep.assign_task(self, assigner)
            self.status = TaskStatus.ASSIGNED

    def unassign_rep(self):
        self.rep = None
        if self.status != TaskStatus.COMPLETED:
            if self.is_task_expired():
                self.status = TaskStatus.EXPIRED
            else:
                self.status = TaskStatus.OPEN

    def is_task_expired(self):
        if datetime.utcnow() > self.end_date:
            return True
        else:
            return False

    def is_task_deletable(self, user):
        if user.role == Role.SALES_REP:
            if user == self.creator and self.type == TaskType.CUSTOM:
                return True
        
        if user.role == Role.SALES_REP_LEAD:
            return True
        
        return False

    @staticmethod
    def get_unscheduled_tasks(user, start_date=None, end_date=None):
        if start_date is not None and end_date is not None:
            if start_date > end_date:
                raise ValueError("Schedule get_schedule - Start date exceeds end date")
        query = Task.query.filter(Task.rep_id == user.id).filter(Task.end_date >= start_date).filter(Task.start_date <= end_date)
        query = query.join(Schedule, (Task.id == Schedule.task_id)
                & (Schedule.end >= start_date if start_date else None)
                & (Schedule.start <= end_date if end_date else None),
                isouter=True)
        
        return query.filter(Schedule.task_id==None).order_by(Task.type.desc()).order_by(Task.end_date).all()

class TaskWeek(db.Model):
    __tablename__ = "task_week"
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.Enum(TaskStatus))
    remarks = db.relationship('Remark', backref='taskweek', lazy='dynamic')

    def __init__(self, task, start_date=None, end_date=None):
        if start_date is not None and end_date is not None:
            if start_date > end_date:
                raise ValueError("TaskWeek - Start date exceeds end date")
        
        self.task = task
        self.start_date = start_date
        self.end_date = end_date

        now = datetime.utcnow()
        if now < self.start_date or now > self.end_date:
            now = self.start_date

        if self.is_task_expired(now):
            self.set_status(TaskStatus.EXPIRED)
        else:
            self.set_status(TaskStatus.OPEN)

    def set_status(self, task_status: TaskStatus):
        if not isinstance(task_status, TaskStatus):
            raise ValueError("TaskWeek - Invalid status")
            
        self.status = task_status

    def is_task_expired(self, date): #Expiration depends on which day of the week it is being compared to
        if date < self.start_date or date > self.end_date:
            raise ValueError("TaskWeek - date exceeds week range")

        if date > self.task.end_date:
            return True
        else:
            return False

    @staticmethod
    def create_task_weeks(task, timezone='UTC'):
        start_date = to_timezone(task.start_date, to_timezone=timezone)
        end_date = to_timezone(task.end_date, to_timezone=timezone)
        weeks = get_week_range(start_date, end_date) 
        task_weeks = []
        for week in weeks:
            task_weeks.append(TaskWeek(task, to_timezone(week[0], from_timezone=timezone), to_timezone(week[-1], from_timezone=timezone)))

        return task_weeks

class Remark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500))
    rep_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    taskweek_id = db.Column(db.Integer, db.ForeignKey('task_week.id'))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)

    def __init__(self, description=None, rep=None, task=None):
        self.description = description
        self.rep = rep
        self.task = task

    @staticmethod
    def get_remarks(task):
        remarks = Remark.query.filter(task==task).all()
        return remarks

class Schedule(db.Model): #Some tasks can be scheduled more than once because they need to be repeated
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    rep_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id')) 

    def __init__(self, start=None, end=None, rep=None, task=None):
        self.start = start
        self.end = end
        self.rep = rep
        self.task = task

    @staticmethod
    def get_schedule(user, start_date=None, end_date=None):
        if start_date is not None and end_date is not None:
            if start_date > end_date:
                raise ValueError("Schedule get_schedule - Start date exceeds end date")

        query = Schedule.query.filter(Schedule.rep == user)
        if start_date is not None:
            query = query.filter(Schedule.end >= start_date)

        if end_date is not None:
            query = query.filter(Schedule.start <= end_date)

        schedules = query.order_by(Schedule.start).all()                   
        return schedules
            
    @staticmethod
    def is_schedule_available(user, start, end):
        print(start)
        print(end)
        sch = Schedule.query.filter(Schedule.rep == user).filter(Schedule.start >= start).filter(Schedule.end <= end).first()
        print("none" if not sch else sch.start)
        print("none" if not sch else sch.end)
        sch2 = Schedule.query.filter(Schedule.rep == user).filter(Schedule.end > start).filter(Schedule.start <= end).first()
        print("none" if not sch2 else sch.start)
        print("none" if not sch2 else sch.end)
        return \
            Schedule.query.filter(Schedule.rep == user).filter(Schedule.start >= start).filter(Schedule.end <= end).count() == 0 and \
            Schedule.query.filter(Schedule.rep == user).filter(Schedule.end > start).filter(Schedule.start <= end).count() == 0

    @staticmethod
    def is_task_scheduled(task, start, end):
        return Schedule.query.filter(Schedule.task == task).filter(Schedule.start >= start).filter(Schedule.end <= end).count() == 0

@login.user_loader
def load_user(id):
    return User.query.get(int(id))