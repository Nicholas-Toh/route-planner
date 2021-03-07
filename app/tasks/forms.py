from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, SelectField, TimeField, TextAreaField, HiddenField
from wtforms.fields.html5 import IntegerField, DateField, DateTimeLocalField
from wtforms.validators import DataRequired, Length
from datetime import datetime

class TaskForm(FlaskForm):
    id = "create-task-form"
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Length(max=300)])
    outlet = SelectField('Outlet')
    user_start = DateField('Start', format='%Y-%m-%d', validators=[DataRequired()])
    user_end = DateField('End', format='%Y-%m-%d', validators=[DataRequired()])
    estimated_time = TimeField('Estimated Time', render_kw={"placeholder":"HH:MM"}, validators=[DataRequired()])
    repeat_count = IntegerField('How many times?', render_kw={"min":"1"}, default=1, validators=[DataRequired()])
    start = DateTimeLocalField(label='', format='%Y-%m-%dT%H:%M')
    end = DateTimeLocalField(label='', format='%Y-%m-%dT%H:%M')

class DeleteTaskForm(FlaskForm):
    id = 'delete-task-form'
    task_id = SelectField('Task ID', id="task-id", validators=[DataRequired()])