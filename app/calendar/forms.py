from flask_wtf import FlaskForm
from wtforms import SelectField, BooleanField, SubmitField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, InputRequired

class ScheduleTaskForm(FlaskForm):
    id = "sch-task-form"
    task_id = SelectField('Task ID', id="task-id", validators=[DataRequired()])
    start = DateTimeLocalField('Start Period', id="start", format='%Y-%m-%dT%H:%M', validators=[InputRequired()])
    end = DateTimeLocalField('End Period', id="end", format='%Y-%m-%dT%H:%M', validators=[InputRequired()])
