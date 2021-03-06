#!/usr/bin/env python
from datetime import datetime, timedelta, date
import unittest
from app import create_app, db
from app.models import User, Outlet, Task, AvailableTime, Schedule, Remark, TaskWeek
from app.enums import Zone, Role, TaskType, TaskStatus
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class TaskModelTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_TaskModel_TaskConstructor_InvalidDateShouldThrow(self):
        u1 = User(username='john')
        start = datetime(2021, 2, 22)
        t1 = Task(creator=u1, type=TaskType.CUSTOM, start_date=start, end_date=start)
        t2 = Task(creator=u1, type=TaskType.CUSTOM, start_date=start, end_date=start + timedelta(days=1))
        t3 = Task(creator=u1, type=TaskType.CUSTOM, start_date=start + timedelta(days=-1), end_date=start)

        with self.assertRaises(ValueError):
            t4 = Task(creator=u1, type=TaskType.CUSTOM, start_date=start, end_date=start + timedelta(days=-1))

        with self.assertRaises(ValueError):
            t5 = Task(creator=u1, type=TaskType.CUSTOM, start_date=start + timedelta(days=1), end_date=start)

    def TaskModel_TaskConstructor_OpenTasksShouldExpireWhenCurrentDateExceedsEndDate(self):
        u1 = User(username='john')
        start = datetime(2021, 2, 22)
        t1 = Task(creator=u1, type=TaskType.CUSTOM, start_date=start + timedelta(days=0), end_date=start + timedelta(days=0))
        t2 = Task(creator=u1, type=TaskType.CUSTOM, start_date=start + timedelta(days=0), end_date=start + timedelta(days=1))
        t3 = Task(creator=u1, type=TaskType.CUSTOM, start_date=start + timedelta(days=-1), end_date=start + timedelta(days=-1))

        self.assertEqual(t1.status, TaskStatus.OPEN)
        self.assertEqual(t2.status, TaskStatus.OPEN)
        self.assertEqual(t3.status, TaskStatus.EXPIRED)

    def TaskModel_AssignRep_AssignAndUnassignShouldSetStatusCorrectly(self):
        u1 = User(username='john')
        u2 = User(username='susan')
        start = datetime.utcnow()
        u1.assign_zone(Zone.A)
        u2.assign_zone(Zone.B)
        u1.assign_role(Role.SALES_REP)
        u2.assign_role(Role.SALES_REP)
        o1 = Outlet()
        o2 = Outlet()
        o1.assign_zone(Zone.A)
        o2.assign_zone(Zone.B)
        u1.assign_outlet(o1)
        u2.assign_outlet(o2)
        t1 = Task(creator=u1, outlet=o1, type=TaskType.CUSTOM)
        t2 = Task(creator=u1, outlet=o2, type=TaskType.CUSTOM)
        t3 = Task(creator=u1, outlet=o1, type=TaskType.CUSTOM)
        t4 = Task(creator=u1, outlet=o2, type=TaskType.CUSTOM)
        t5 = Task(creator=u1, outlet=o1, type=TaskType.CUSTOM, start_date=start + timedelta(days=-1), end_date=start + timedelta(days=-1))

        db.session.add_all([u1, u2, o1, o2, t1, t2, t3, t4, t5])
        db.session.commit()

        t1.assign_rep(u1, u1)
        self.assertEqual(t1.rep.id, u1.id)
        self.assertEqual(t1.status, TaskStatus.ASSIGNED)
        t1.unassign_rep()
        self.assertEqual(t1.status, TaskStatus.OPEN)
        t1.assign_rep(u2, u2)
        self.assertEqual(t1.rep, None)
        self.assertEqual(t1.status, TaskStatus.OPEN)
        t1.unassign_rep()
        self.assertEqual(t1.status, TaskStatus.OPEN)

        t2.assign_rep(u1, u1)
        self.assertEqual(t2.rep, None)
        self.assertEqual(t2.status, TaskStatus.OPEN)
        t2.unassign_rep()
        self.assertEqual(t2.status, TaskStatus.OPEN)
        t2.assign_rep(u2, u2)
        self.assertEqual(t2.rep.id, u2.id)
        self.assertEqual(t2.status, TaskStatus.ASSIGNED)
        t2.unassign_rep()
        self.assertEqual(t2.status, TaskStatus.OPEN)

        t3.assign_rep(u1, u1)
        self.assertEqual(t3.rep.id, u1.id)
        self.assertEqual(t3.status, TaskStatus.ASSIGNED)
        t3.set_status(TaskStatus.COMPLETED) #Rep completes the task but the task is reassigned
        t3.unassign_rep()
        self.assertEqual(t3.status, TaskStatus.COMPLETED)
        t3.assign_rep(u2, u2)
        self.assertEqual(t3.rep, None)
        self.assertEqual(t3.status, TaskStatus.COMPLETED)
        t3.unassign_rep()
        self.assertEqual(t3.status, TaskStatus.COMPLETED)

        t4.assign_rep(u1, u1)
        self.assertEqual(t4.rep, None)
        self.assertEqual(t4.status, TaskStatus.OPEN)
        t4.set_status(TaskStatus.COMPLETED) #Rep completes the task but the task is reassigned
        t4.unassign_rep()
        self.assertEqual(t4.status, TaskStatus.COMPLETED)
        t4.assign_rep(u2, u2)
        self.assertEqual(t4.rep.id, u2.id)
        self.assertEqual(t4.status, TaskStatus.ASSIGNED)
        t4.unassign_rep()
        self.assertEqual(t4.status, TaskStatus.OPEN)

        t5.assign_rep(u1, u1)
        self.assertEqual(t5.status, TaskStatus.ASSIGNED)
        t5.unassign_rep()
        self.assertEqual(t5.status, TaskStatus.EXPIRED)

    def test_TaskModel_GetUnscheduledTasks_ShouldGetUnscheduledTasksWithinDateRange(self):
        u1 = User(zone=Zone.A, role=Role.SALES_REP)
        u2 = User(zone=Zone.B, role=Role.SALES_REP)
        o1 = Outlet(zone=Zone.A, rep=u1)
        o2 = Outlet(zone=Zone.B, rep=u2)
        t1 = Task(outlet=o1, rep=u1, start_date=datetime(2020, 1, 27), end_date=datetime(2020, 1, 30), creator=u1, type=TaskType.CUSTOM, assigner=u1)
        t2 = Task(outlet=o1, rep=u1, start_date=datetime(2020, 1, 27), end_date=datetime(2020, 1, 30), creator=u1, type=TaskType.CUSTOM, assigner=u1)
        t3 = Task(outlet=o2, rep=u2, start_date=datetime(2020, 1, 27), end_date=datetime(2020, 1, 30), creator=u2, type=TaskType.CUSTOM, assigner=u2)
        t4 = Task(outlet=o2, rep=u2, start_date=datetime(2020, 1, 27), end_date=datetime(2020, 1, 30), creator=u2, type=TaskType.CUSTOM, assigner=u2)
        s1 = Schedule(start=datetime(2020, 1, 27, 14, 30), end=datetime(2020, 1, 27, 16), rep=u1, task=t1)
        s2 = Schedule(start=datetime(2020, 1, 27, 16, 30), end=datetime(2020, 1, 27, 18), rep=u2, task=t3)

        db.session.add_all([u1, u2, o1, o2, t1, t2, t3, t4, s1, s2])
        db.session.commit()

        result1 = Task.get_unscheduled_tasks(u1, datetime(2020, 1, 26), datetime(2020, 1, 29))
        result2 = Task.get_unscheduled_tasks(u1, datetime(2020, 1, 27), datetime(2020, 1, 29))
        result3 = Task.get_unscheduled_tasks(u1, datetime(2020, 1, 28), datetime(2020, 1, 29))
        result4 = Task.get_unscheduled_tasks(u1, datetime(2020, 1, 29), datetime(2020, 1, 29))
        result5 = Task.get_unscheduled_tasks(u1, datetime(2020, 1, 26), datetime(2020, 1, 28))
        result6 = Task.get_unscheduled_tasks(u1, datetime(2020, 1, 26), datetime(2020, 1, 27))
        result7 = Task.get_unscheduled_tasks(u1, datetime(2020, 1, 26), datetime(2020, 1, 26))
        result8 = Task.get_unscheduled_tasks(u1, datetime(2020, 1, 31), datetime(2020, 1, 31))
        self.assertRaises(ValueError, Task.get_unscheduled_tasks, u1, datetime(2020, 1, 26), datetime(2020, 1, 25))

        self.assertEqual(result1, [t2])
        self.assertEqual(result2, [t2])
        self.assertEqual(result3, [t1, t2])
        self.assertEqual(result4, [t1, t2])
        self.assertEqual(result5, [t2])
        self.assertEqual(result6, [t1, t2])
        self.assertEqual(result7, [])
        self.assertEqual(result8, [])

    def test_TaskScheduleTaskWeekMode_ScheduleAndTaskWeekShouldBeDeletedOnTaskDelete(self):
        u1 = User(zone=Zone.A, role=Role.SALES_REP)
        o1 = Outlet(zone=Zone.A, rep=u1)
        t1 = Task(outlet=o1, rep=u1, start_date=datetime(2020, 1, 27), end_date=datetime(2020, 1, 30), creator=u1, type=TaskType.CUSTOM, assigner=u1)
        t2 = Task(outlet=o1, rep=u1, start_date=datetime(2020, 1, 27), end_date=datetime(2020, 1, 30), creator=u1, type=TaskType.CUSTOM, assigner=u1)
        w1 = TaskWeek.create_task_weeks(t1)
        w2 = TaskWeek.create_task_weeks(t2)
        s1 = Schedule(rep=u1, task=t1)
        s2 = Schedule(rep=u1, task=t1)
        s3 = Schedule(rep=u1, task=t2)
        s4 = Schedule(rep=u1, task=t2)

        db.session.add_all([u1, o1, t1, t2, s1, s2, s3, s4] + w1 + w2)
        db.session.commit()

        db.session.delete(t1)
        db.session.commit()

        result1 = TaskWeek.query.all()
        result2 = Schedule.query.all()
        result3 = Outlet.query.all()
        result4 = u1.tasks.all()

        self.assertEqual(result1, w2)
        self.assertEqual(result2, [s3, s4])
        self.assertEqual(result3, [o1])
        self.assertEqual(result4, [t2])
        
if __name__ == '__main__':
    unittest.main(verbosity=2)