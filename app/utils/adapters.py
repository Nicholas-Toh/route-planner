from app.models import Schedule, Task, Outlet, AvailableTime
from app.optimizer.Tricoire_MuPOTW.Data.Problem import Customer, Info
from app.utils.date_utils import time_to_minutes, to_timezone, to_datetime
from app.schemas import ScheduleSchema

import json    
from datetime import timezone

def schedule_to_fullcalendar(obj, timezone):
    #TODO: IMPLEMENT MULTIPLE AVAILABLE TIMES
    local_start_time = obj.task.outlet.available_times.first().start_time
    available_start_time = to_timezone(obj.start.replace(hour=local_start_time.hour, minute=local_start_time.minute), from_timezone=timezone)
    local_end_time = obj.task.outlet.available_times.first().end_time
    available_end_time = to_timezone(obj.end.replace(hour=local_end_time.hour, minute=local_end_time.minute), from_timezone=timezone)
    is_out_of_range = True if obj.end > available_end_time or obj.end < available_start_time else False
    
    dict = \
    {
        "id": obj.id,
        "title": obj.task.title,
        "description": obj.task.description,
        "start": obj.start.replace(microsecond=0).isoformat()+'Z',
        "end": obj.end.replace(microsecond=0).isoformat()+'Z',
        "schedule_obj": ScheduleSchema().dump(obj),
        "is_out_of_range": is_out_of_range
    }
    return dict

def fullcalendar_to_schedule(obj):
    return None

def task_to_customer(task):
    info = Info()
    info.id = task.outlet.id
    info.x = int(task.outlet.x)
    info.y = int(task.outlet.y)
    info.value = float(task.outlet.value)
    info.startTime = time_to_minutes(task.outlet.available_times.first().start_time)
    info.serviceTime = task.service_time
    info.endTime = time_to_minutes(task.outlet.available_times.first().end_time)
    info.taskID = task.id

    customer = Customer(info)
    return customer