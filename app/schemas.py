from app import marshmallow as ma
from app.models import TaskWeek, Task, Outlet, Schedule
class OutletSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Outlet
    
    value = ma.auto_field(as_string=True)

class TaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Task
    outlet = ma.Nested(OutletSchema)

class TaskWeekSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TaskWeek

    task = ma.Nested(TaskSchema)

class TaskWeekCollectionSchema(ma.Schema):
    weeks = ma.List(ma.Nested(TaskWeekSchema))

class ScheduleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Schedule

    rep_id = ma.auto_field()
    task_id = ma.auto_field()
