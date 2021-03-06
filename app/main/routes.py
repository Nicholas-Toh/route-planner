from app.main import bp
from flask import render_template, url_for
from flask_login import login_required, current_user
from app.models import User, Task, Schedule
from datetime import datetime

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    schedules = Schedule.get_schedule(current_user, start_date=datetime.utcnow())
    return render_template('index.html', title='Home', upcoming_schedules=schedules)