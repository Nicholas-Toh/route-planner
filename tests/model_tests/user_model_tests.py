#!/usr/bin/env python
from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.models import User, Outlet, Task, AvailableTime, Schedule, Remark
from app.enums import Zone, Role, TaskType, TaskStatus
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class UserModelTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_UserModel_AssignOutlet_OutletWithSameZoneShouldBeAssigned(self):
        u1 = User(username='john')
        u1.assign_zone(Zone.A)
        o1 = Outlet()
        o2 = Outlet()
        o1.assign_zone(Zone.A)
        o2.assign_zone(Zone.B)
        u1.assign_outlet(o1)
        u1.assign_outlet(o2)

        db.session.add_all([u1, o1, o2])
        db.session.commit()

        self.assertEqual(u1.outlets.all(), [o1])

    def test_UserModel_IsAssignedOutlet_UserAndOutletRepIdIsEqual(self):
        u1 = User(username='john')
        u2 = User(username='mary')
        u1.assign_zone(Zone.A)
        u2.assign_zone(Zone.B)
        o1 = Outlet()
        o2 = Outlet()
        o1.assign_zone(Zone.A)
        o2.assign_zone(Zone.B)
        u1.assign_outlet(o1)
        u2.assign_outlet(o2)

        db.session.add_all([u1, u2, o1, o2])
        db.session.commit()

        result1 = u1.is_assigned_outlet(o1)
        result2 = u1.is_assigned_outlet(o2)
        result3 = u2.is_assigned_outlet(o1)
        result4 = u2.is_assigned_outlet(o2)

        self.assertEqual(result1, True)
        self.assertEqual(result2, False)
        self.assertEqual(result3, False)
        self.assertEqual(result4, True)
    
    def test_UserModel_IsSameZone_UserAndOutletZoneIsEqual(self):
        u1 = User(username='john')
        u2 = User(username='mary')
        u1.assign_zone(Zone.A)
        u2.assign_zone(Zone.B)
        o1 = Outlet()
        o2 = Outlet()
        o1.assign_zone(Zone.A)
        o2.assign_zone(Zone.B)
        result1 = u1.is_same_zone(o1)
        result2 = u1.is_same_zone(o2)
        result3 = u2.is_same_zone(o1)
        result4 = u2.is_same_zone(o2)

        self.assertEqual(result1, True)
        self.assertEqual(result2, False)
        self.assertEqual(result3, False)
        self.assertEqual(result4, True)

    def test_UserModel_IsTaskAssignable_SameOutletShouldBeAssignable(self):
        u1 = User(username='john')
        u2 = User(username='mary')
        u1.assign_zone(Zone.A)
        u2.assign_zone(Zone.A)
        u1.assign_role(Role.SALES_REP)
        u2.assign_role(Role.SALES_REP)
        o1 = Outlet()
        o2 = Outlet()
        o1.assign_zone(Zone.A)
        o2.assign_zone(Zone.A)
        u1.assign_outlet(o1)
        u2.assign_outlet(o2)
        t1 = Task(creator=u1, outlet=o1, type=TaskType.CUSTOM)
        t2 = Task(creator=u1, outlet=o2, type=TaskType.CUSTOM)

        db.session.add_all([u1, u2, o1, o2, t1, t2])
        db.session.commit() 

        result1 = u1.is_task_assignable(t1, u1)
        result2 = u1.is_task_assignable(t2, u1)
        result3 = u2.is_task_assignable(t1, u2)
        result4 = u2.is_task_assignable(t2, u2)

        self.assertEqual(result1, True)
        self.assertEqual(result2, False)
        self.assertEqual(result3, False)
        self.assertEqual(result4, True)

    def test_UserModel_IsTaskAssignable_SalesRepCanOnlySelfAssignCustomTask(self):
        u1 = User(username='john')
        u2 = User(username='susan')
        u1.assign_zone(Zone.A)
        u2.assign_zone(Zone.A)
        u1.assign_role(Role.SALES_REP)
        u2.assign_role(Role.SALES_REP)
        o1 = Outlet()
        o1.assign_zone(Zone.A)
        u1.assign_outlet(o1)
        t1 = Task(creator=u1, outlet=o1, type=TaskType.CUSTOM)

        db.session.add_all([u1, u2, o1, t1])
        db.session.commit() 

        result1 = u1.is_task_assignable(t1, u1)
        result2 = u1.is_task_assignable(t1, u2)
        result3 = u2.is_task_assignable(t1, u2)
        result4 = u2.is_task_assignable(t1, u1)

        self.assertEqual(result1, True)
        self.assertEqual(result2, False)
        self.assertEqual(result3, False)
        self.assertEqual(result4, False)

    def test_UserModel_AssignTask_SelfAssignsShouldWorkForValidTasks(self):
        u1 = User(username='john')
        u2 = User(username='mary')
        u1.assign_zone(Zone.A)
        u2.assign_zone(Zone.B)
        u1.assign_role(Role.SALES_REP)
        u2.assign_role(Role.SALES_REP_LEAD)
        db.session.add_all([u1, u2])

        o1 = Outlet(zone=Zone.A, rep=u1)
        o2 = Outlet(zone=Zone.A, rep=u2) #In reality an outlet can never be
        o3 = Outlet(zone=Zone.B, rep=u1) #assigned to another sales rep of a different zone
        o4 = Outlet(zone=Zone.B, rep=u2)
        
        db.session.add_all([o1, o2, o3, o4])

        t1 = Task(creator=u1, outlet=o1, type=TaskType.CUSTOM)
        t2 = Task(creator=u1, outlet=o2, type=TaskType.CUSTOM)
        t3 = Task(creator=u1, outlet=o3, type=TaskType.CUSTOM)
        t4 = Task(creator=u1, outlet=o4, type=TaskType.CUSTOM)
        t5 = Task(creator=u2, outlet=o1, type=TaskType.MANDATORY)
        t6 = Task(creator=u2, outlet=o2, type=TaskType.MANDATORY)
        t7 = Task(creator=u2, outlet=o3, type=TaskType.MANDATORY)
        t8 = Task(creator=u2, outlet=o4, type=TaskType.MANDATORY)
        db.session.add_all([t1, t2, t3, t4, t5, t6, t7, t8])
        db.session.commit() 

        u1.assign_task(t1, u1) #Should get assigned
        u1.assign_task(t2, u1) #Should not get assigned
        u1.assign_task(t3, u1) #Should not get assigned
        u1.assign_task(t4, u1) #Should not get assigned
        u1.assign_task(t5, u1) #Should not get assigned
        u1.assign_task(t6, u1) #Should not get assigned
        u1.assign_task(t7, u1) #Should not get assigned
        u1.assign_task(t8, u1) #Should not get assigned

        self.assertEqual(u1.tasks.all(), [t1])

        u2.assign_task(t1, u2) #Should not get assigned
        u2.assign_task(t2, u2) #Should not get assigned
        u2.assign_task(t3, u2) #Should not get assigned
        u2.assign_task(t4, u2) #Should get assigned
        u2.assign_task(t5, u2) #Should not get assigned
        u2.assign_task(t6, u2) #Should not get assigned
        u2.assign_task(t7, u2) #Should not get assigned
        u2.assign_task(t8, u2) #Should get assigned
        
        self.assertEqual(u2.tasks.all(), [t4, t8])

    def test_UserModel_AssignTask_CrossAssignsShouldOnlyWorkForLeads(self):
        u1 = User(username='john')
        u2 = User(username='mary')
        u1.assign_zone(Zone.A)
        u2.assign_zone(Zone.B)
        u1.assign_role(Role.SALES_REP)
        u2.assign_role(Role.SALES_REP_LEAD)
        db.session.add_all([u1, u2])

        o1 = Outlet(zone=Zone.A, rep=u1)
        o2 = Outlet(zone=Zone.A, rep=u2)
        o3 = Outlet(zone=Zone.B, rep=u1)
        o4 = Outlet(zone=Zone.B, rep=u2)

        db.session.add_all([o1, o2, o3, o4])

        t1 = Task(creator=u1, outlet=o1, type=TaskType.CUSTOM)
        t2 = Task(creator=u1, outlet=o2, type=TaskType.CUSTOM)
        t3 = Task(creator=u1, outlet=o3, type=TaskType.CUSTOM)
        t4 = Task(creator=u1, outlet=o4, type=TaskType.CUSTOM)
        t5 = Task(creator=u2, outlet=o1, type=TaskType.MANDATORY)
        t6 = Task(creator=u2, outlet=o2, type=TaskType.MANDATORY)
        t7 = Task(creator=u2, outlet=o3, type=TaskType.MANDATORY)
        t8 = Task(creator=u2, outlet=o4, type=TaskType.MANDATORY)
        db.session.add_all([t1, t2, t3, t4, t5, t6, t7, t8])
        db.session.commit() 

        u2.assign_task(t1, u1) #Should not get assigned
        u2.assign_task(t2, u1) #Should not get assigned
        u2.assign_task(t3, u1) #Should not get assigned
        u2.assign_task(t4, u1) #Should not get assigned
        u2.assign_task(t5, u1) #Should not get assigned
        u2.assign_task(t6, u1) #Should not get assigned
        u2.assign_task(t7, u1) #Should not get assigned
        u2.assign_task(t8, u1) #Should not get assigned

        self.assertEqual(u2.tasks.all(), [])

        u1.assign_task(t1, u2) #Should get assigned
        u1.assign_task(t2, u2) #Should not get assigned
        u1.assign_task(t3, u2) #Should not get assigned
        u1.assign_task(t4, u2) #Should not get assigned
        u1.assign_task(t5, u2) #Should get assigned
        u1.assign_task(t6, u2) #Should not get assigned
        u1.assign_task(t7, u2) #Should not get assigned
        u1.assign_task(t8, u2) #Should not get assigned
        
        self.assertEqual(u1.tasks.all(), [t1, t5])

    def test_UserModel_UnassignZoneOutletTasks_ZoneOutletAndTasksShouldBeRemoved(self):
        u1 = User(username='john')
        u1.assign_zone(Zone.A)
        u1.assign_role(Role.SALES_REP)
        o1 = Outlet(zone=Zone.A, rep=u1)
        o2 = Outlet(zone=Zone.A, rep=u1)
        t1 = Task(creator=u1, outlet=o1, type=TaskType.CUSTOM)
        t2 = Task(creator=u1, outlet=o2, type=TaskType.CUSTOM)
        u1.assign_task(t1, u1)
        u1.assign_task(t2, u1)

        db.session.add_all([u1, o1, o2, t1, t2])
        db.session.commit()

        self.assertEqual(u1.zone, Zone.A)
        self.assertEqual(u1.outlets.all(), [o1, o2])
        self.assertEqual(u1.tasks.all(), [t1, t2])

        u1.unassign_zone_outlets_tasks()

        self.assertEqual(u1.zone, None)
        self.assertEqual(u1.outlets.all(), [])
        self.assertEqual(u1.tasks.all(), [])
