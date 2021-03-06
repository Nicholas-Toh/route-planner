#!/usr/bin/env python
from datetime import datetime, timedelta, time
import unittest
from app import create_app, db
from app.models import User, Outlet, Task, AvailableTime, Schedule, Remark, TaskWeek
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

    def test_TaskWeekModel_CreateTaskWeeks_ShouldCreateTaskWeeksWithinTaskDateRange(self):
        u1 = User(zone=Zone.A, role=Role.SALES_REP)
        o1 = Outlet(zone=Zone.A, rep=u1)
        now = datetime(2021, 2, 15)
        _, current_week, _ = now.isocalendar()
        t1 = Task(outlet=o1, rep=u1, creator=u1, type=TaskType.CUSTOM, assigner=u1,\
                  start_date=now+timedelta(days=7), end_date=now+timedelta(days=13))
        t2 = Task(outlet=o1, rep=u1, creator=u1, type=TaskType.CUSTOM, assigner=u1,\
                  start_date=now+timedelta(days=6), end_date=now+timedelta(days=13))
        t3 = Task(outlet=o1, rep=u1, creator=u1, type=TaskType.CUSTOM, assigner=u1,\
                  start_date=now+timedelta(days=7), end_date=now+timedelta(days=14))
        t4 = Task(outlet=o1, rep=u1, creator=u1, type=TaskType.CUSTOM, assigner=u1,\
                  start_date=now+timedelta(days=6), end_date=now+timedelta(days=14))
                
        db.session.add_all([u1, o1, t1, t2, t3, t4])
        db.session.commit()

        result1 = TaskWeek.create_task_weeks(t1)
        result2 = TaskWeek.create_task_weeks(t2)
        result3 = TaskWeek.create_task_weeks(t3)
        result4 = TaskWeek.create_task_weeks(t4)
        
        db.session.add_all(result1+result2+result3+result4)
        db.session.commit()

        self.assertEqual(len(result1), 1)
        self.assertEqual(result1[0].start_date, datetime(2021, 2, 22))
        self.assertEqual(result1[0].end_date, datetime(2021, 2, 28))

        self.assertEqual(len(result2), 2)
        self.assertEqual(result2[0].start_date, datetime(2021, 2, 15))
        self.assertEqual(result2[0].end_date, datetime(2021, 2, 21))
        self.assertEqual(result2[1].start_date, datetime(2021, 2, 22))
        self.assertEqual(result2[1].end_date, datetime(2021, 2, 28))

        self.assertEqual(len(result3), 2)
        self.assertEqual(result3[0].start_date, datetime(2021, 2, 22))
        self.assertEqual(result3[0].end_date, datetime(2021, 2, 28))
        self.assertEqual(result3[1].start_date, datetime(2021, 3, 1))
        self.assertEqual(result3[1].end_date, datetime(2021, 3, 7))

        self.assertEqual(len(result4), 3)
        self.assertEqual(result4[0].start_date, datetime(2021, 2, 15))
        self.assertEqual(result4[0].end_date, datetime(2021, 2, 21))
        self.assertEqual(result4[1].start_date, datetime(2021, 2, 22))
        self.assertEqual(result4[1].end_date, datetime(2021, 2, 28))
        self.assertEqual(result4[2].start_date, datetime(2021, 3, 1))
        self.assertEqual(result4[2].end_date, datetime(2021, 3, 7))

    def test_TaskWeekModel_IsTaskExpired_ShouldReturnTrueForExpiredTasks(self):
        u1 = User(zone=Zone.A, role=Role.SALES_REP)
        o1 = Outlet(zone=Zone.A, rep=u1)
        now = datetime(2021, 2, 17)
        _, current_week, _ = now.isocalendar()
        t1 = Task(outlet=o1, rep=u1, creator=u1, type=TaskType.CUSTOM, assigner=u1,\
                  start_date=now, end_date=now+timedelta(days=14))

        db.session.add_all([u1, o1, t1])
        db.session.commit()

        task_week = TaskWeek.create_task_weeks(t1)

        week1 = task_week[0]
        week2 = task_week[1]
        week3 = task_week[2]

        result1 = week1.is_task_expired(datetime(2021, 2, 15))
        result2 = week1.is_task_expired(datetime(2021, 2, 17))
        result3 = week1.is_task_expired(datetime(2021, 2, 18))
        result4 = week1.is_task_expired(datetime(2021, 2, 21))

        result5 = week2.is_task_expired(datetime(2021, 2, 22))
        result6 = week2.is_task_expired(datetime(2021, 2, 23))
        result7 = week2.is_task_expired(datetime(2021, 2, 28))

        result8 = week3.is_task_expired(datetime(2021, 3, 1))
        result9 = week3.is_task_expired(datetime(2021, 3, 2))
        result10 = week3.is_task_expired(datetime(2021, 3, 3))
        result11 = week3.is_task_expired(datetime(2021, 3, 4))
        result12 = week3.is_task_expired(datetime(2021, 3, 7))

        self.assertEqual(result1, False)
        self.assertEqual(result2, False)
        self.assertEqual(result3, False)
        self.assertEqual(result4, False)
        self.assertEqual(result5, False)
        self.assertEqual(result6, False)
        self.assertEqual(result7, False)
        self.assertEqual(result8, False)
        self.assertEqual(result9, False)
        self.assertEqual(result10, False)
        self.assertEqual(result11, True)
        self.assertEqual(result12, True)
