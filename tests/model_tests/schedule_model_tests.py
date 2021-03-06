#!/usr/bin/env python
from datetime import datetime, timedelta, date, time
import unittest
from app import create_app, db
from app.models import User, Outlet, Task, AvailableTime, Schedule, Remark
from app.enums import Zone, Role, TaskType, TaskStatus
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class ScheduleModelTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_ScheduleModel_GetSchedule_ShouldReturnTasksWithinDateRange(self):
        u1 = User(zone=Zone.A, role=Role.SALES_REP)
        u2 = User(zone=Zone.B, role=Role.SALES_REP)
        o1 = Outlet(zone=Zone.A, rep=u1)
        o2 = Outlet(zone=Zone.B, rep=u2)
        t1 = Task(outlet=o1, rep=u1, creator=u1, type=TaskType.CUSTOM, assigner=u1)
        t2 = Task(outlet=o2, rep=u2, creator=u2, type=TaskType.CUSTOM, assigner=u2)
        s1 = Schedule(start=date(2020, 1, 27), end=date(2020, 1, 27), rep=u1, task=t1)
        s2 = Schedule(start=date(2020, 1, 28), end=date(2020, 1, 28), rep=u1, task=t1)
        s3 = Schedule(start=date(2020, 1, 29), end=date(2020, 1, 29), rep=u1, task=t1)
        s4 = Schedule(start=date(2020, 1, 30), end=date(2020, 1, 30), rep=u1, task=t1)
        s5 = Schedule(start=date(2020, 1, 31), end=date(2020, 1, 31), rep=u1, task=t1)

        s6 = Schedule(start=date(2020, 1, 27), end=date(2020, 1, 27), rep=u2, task=t2)
        s7 = Schedule(start=date(2020, 1, 28), end=date(2020, 1, 28), rep=u2, task=t2)
        s8 = Schedule(start=date(2020, 1, 29), end=date(2020, 1, 29), rep=u2, task=t2)
        s9 = Schedule(start=date(2020, 1, 30), end=date(2020, 1, 30), rep=u2, task=t2)
        s10 = Schedule(start=date(2020, 1, 31), end=date(2020, 1, 31), rep=u2, task=t2)

        db.session.add_all([u1, u2, o1, o2, t1, t2, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10])
        db.session.commit()

        result1 = Schedule.get_schedule(u1, start_date=datetime(2020, 1, 29), end_date=datetime(2020, 1, 29))
        result2 = Schedule.get_schedule(u1, start_date=datetime(2020, 1, 28), end_date=datetime(2020, 1, 29))
        result3 = Schedule.get_schedule(u1, start_date=datetime(2020, 1, 27), end_date=datetime(2020, 1, 29))
        result4 = Schedule.get_schedule(u1, start_date=datetime(2020, 1, 29), end_date=datetime(2020, 1, 30))
        result5 = Schedule.get_schedule(u1, start_date=datetime(2020, 1, 29), end_date=datetime(2020, 1, 31))
        result6 = Schedule.get_schedule(u1, start_date=datetime(2020, 1, 27), end_date=datetime(2020, 1, 31))
        result7 = Schedule.get_schedule(u1, start_date=datetime(2020, 1, 26), end_date=datetime(2020, 1, 26))
        result8 = Schedule.get_schedule(u1, start_date=datetime(2020, 2, 1), end_date=datetime(2020, 2, 1))
        result9 = Schedule.get_schedule(u1, start_date=datetime(2020, 1, 29))
        result10 = Schedule.get_schedule(u1, end_date=datetime(2020, 1, 29)) #Doing this will get all schedules that have ever been 
                                                                         #created, DO NOT DO THIS

        self.assertEqual(result1, [s3])
        self.assertEqual(result2, [s2, s3])
        self.assertEqual(result3, [s1, s2, s3])
        self.assertEqual(result4, [s3, s4])
        self.assertEqual(result5, [s3, s4, s5])
        self.assertEqual(result6, [s1, s2, s3, s4, s5])
        self.assertEqual(result7, [])
        self.assertEqual(result8, [])
        self.assertEqual(result9, [s3, s4, s5])
        self.assertEqual(result10, [s1, s2, s3])