from app import create_app, db
from app.models import User, Outlet, AvailableTime, Task, Remark, Schedule, TaskWeek

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 'User': User, 'Outlet': Outlet, 
        'AvailableTime': AvailableTime, 'Task': Task, 'Remark': Remark,
        'Schedule': Schedule, 'TaskWeek': TaskWeek}