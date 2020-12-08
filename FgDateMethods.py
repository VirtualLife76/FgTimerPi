from datetime import date, datetime, timedelta

##TO DATE TIME     TO DATE TIME     TO DATE TIME     TO DATE TIME     TO DATE TIME     TO DATE TIME  
def toDateTime(time):
    time = str(time)
    if (time != ""):
        try:
            return datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
        except:
            return datetime.strptime(time, '%Y-%m-%d %H:%M:%S')

#To date only
def toDateOnly(dt):
    dt = str(toDateTime(dt))
    dt = dt.split(" ")[0]
    return dt

##To Time       To Time     To Time     To Time     To Time     To Time     To Time     To Time
def toTime(dt):
    dt = toDateTime(dt)
    dt = dt.time()
    return dt

        
##dateABeforeB     dateABeforeB     dateABeforeB     dateABeforeB     dateABeforeB     dateABeforeB 
def dateABeforeB(dtA, dtB):
    if (toDateTime(dtA) <= toDateTime(dtB)):
        return 1
    else:
        return 0

##Time
def timeABeforeB(tA, tB):
    if(tA <= tB):
        return True
    else:
        return False

##addTime    addTime    addTime    addTime    addTime    addTime    addTime    addTime    addTime
def addTime(date_time, add_time, time_type = 'milliseconds', return_type = 'str'):
    if (time_type == 'milliseconds'):
        results = toDateTime(date_time) + timedelta(milliseconds=add_time)
    if (time_type == 'seconds'):
        results = toDateTime(date_time) + timedelta(seconds=add_time)
    if (time_type == 'hours'):
        results = toDateTime(date_time) + timedelta(hours=add_time)
    if (time_type == 'days'):
        results = toDateTime(date_time) + timedelta(days=add_time)
        
    if (return_type == 'str'):
        return str(results)
    else:
        return results
    
def days_diff(date1, date2):
    return abs(toDateTime(date2)-toDateTime(date1)).days
    
def hours_diff(date1, date2):
    diff = toDateTime(date2)-toDateTime(date1)
    #print('hours')
    #print(diff.seconds)
    d = divmod(diff.seconds, 6000)
    return d
    
def ms_diff(date1, date2):
    diff = toDateTime(date2)-toDateTime(date1)
    return diff
    
##Take Y-M-d & time convert to todays y-m-d date & existing time
def bring_date_current(dt):
    dt = toDateTime(dt)
    dt = dt.time()
    cd = str(date.today()) + ' ' + str(dt)

    return cd
    
    
    
    