from datetime import date, time, datetime, timedelta, timezone

# 1. date: Calendar date only
birthday = date(1998, 5, 14)
print(birthday.year, birthday.month, birthday.day)  # 1998 5 14

# 2. time: Wall-clock time of day only
alarm = time(hour=7, minute=30, second=0)
print(alarm.isoformat())  # "07:30:00"

# 3. datetime: Combines date and time
meeting = datetime(2026, 11, 5, 14, 0, 0)
print(meeting.year,meeting.month)  # 2026-11-05 14:00:00

# 4. timedelta: Duration arithmetic
two_weeks = timedelta(days=14)
follow_up = meeting + two_weeks
#print(follow_up)  # 2026-11-19 14:00:00

# Calculate difference between two timestamps
diff = follow_up - meeting
#print(diff.days, diff.total_seconds())  # 14 1209600.0

# 5. timezone: Fixed-offset UTC representation
ist_offset = timezone(timedelta(hours=5, minutes=30))  # UTC+05:30
local_now = datetime.now(ist_offset)
#print(local_now.tzname())  # "UTC+05:30"

