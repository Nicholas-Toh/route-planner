from datetime import date, timedelta, datetime, timezone, time
import dateutil.parser
from backports.zoneinfo import ZoneInfo
from functools import lru_cache

def isoparse(str):
    if not str:
        return None

    return dateutil.parser.isoparse(str)

def all_mondays(year):
    d = datetime(year, 1, 1)                                                       
    d += timedelta(days = 7 - d.weekday())  # First Monday                                                         
    while d.year == year:
        yield d
        d += timedelta(days = 7)

@lru_cache(maxsize=32)
def get_all_weeks(year):
    dict = {}
    for wn,d in enumerate(all_mondays(year)):
        dict[wn+1] = [(d + timedelta(days=k))for k in range(0,7)]
    return dict

def to_timezone(date, from_timezone='UTC', to_timezone='UTC'):
    date = date.replace(tzinfo=ZoneInfo(from_timezone)).astimezone(tz=ZoneInfo(to_timezone)).replace(tzinfo=None)
    return date

def get_current_week(date, user_timezone='UTC'):
    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    new_date = to_timezone(date, from_timezone=user_timezone)
    first_day = new_date - timedelta(days=date.isocalendar()[2] - 1)
    week = [first_day + timedelta(days=i) for i in range(0, 7)]
    return week

def get_week_range(start_date, end_date):
    if end_date < start_date:
        raise ValueError("End date exceeds start date")
    print(start_date)
    _, start_week, _ = start_date.isocalendar()
    _, end_week, _ = end_date.isocalendar()
    if end_week >= start_week:
        return [get_current_week(start_date + timedelta(days=7*i)) for i in range(0, end_week-start_week+1)]
   
    #weeks = [get_all_weeks(start_date.year + i) for i in range(0, end_date.year-start_date.year)]
    #weeks += [get_current_week()]

def to_datetime(date):
    return datetime(date.year, date.month, date.day)

def time_to_datetime(time):
    return datetime.utcnow().replace(hour=time.hour, minute=time.minute, second=time.second)

def time_to_minutes(time):
    return time.hour * 60 + time.minute