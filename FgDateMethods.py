from datetime import date, datetime, timedelta

##Convert possible string TO DATE TIME     TO DATE TIME     TO DATE TIME     TO DATE TIME     TO DATE TIME     TO DATE TIME  
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
        return True
    else:
        return False

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
    diff = toDateTime(date2)-toDateTime(date1).microsecond 
    diff *= 1000  ## x1000 because PY dosn't have MS built in? (:~<
    return diff
    
##Take Y-M-d & time convert to todays y-m-d date & existing time
##Not truly accurate, could be up to 59 minutes off in case of power failure? Or startup?
def bring_date_current(dt):
    dt = toDateTime(dt)
    dt = dt.time()
    cd = str(date.today()) + ' ' + str(dt)

    return cd



#!!Asuming nothing is more than 1 day apart!!!
##Take Y-M-d & time convert to yesterdays or todays y-m-d date. Depends if 
def datetime_to_almost_current(dt):
    now = datetime.now()
    dt = toDateTime(dt)
    time = dt.time()

    new_datetime = toDateTime(str(date.today()) + ' ' + str(time))

    if(now > new_datetime):        #if date is past now, use yesterdays date time, start has passed already, but may still be running.
        new_datetime = addTime(new_datetime, -1, 'days', '')

    return new_datetime


    
def bring_schedule_current(almost_current_date, runEvery, runLength):

    


    #current_dt = dt.time()



    
    return ""