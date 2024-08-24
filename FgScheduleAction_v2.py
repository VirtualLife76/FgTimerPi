# #notes from email
# My basic challenge is, take a start time with an on/off frequency and pick a random time, should it be on or off and for how long?

# So if the timer starts at 3pm on 1/1/24, turning on for 1 minute and off for 1 minute (variable), what is the status at any given time and how much time is left at that status. 

# Eg. 1 minute on, 1 minute off starting at 3pm on 1/1/24. 
# Now is 8/18/24 at 3:00pm, it should turn on now and turn off at 3:01
# Now is 8/18/24 at 3:00.15, it should turn on now for 45 seconds and turn off at 3:01
# Now is 8/18/24 at 3:01, it should stay off for 1 minute and turn on at 3:02
# Now is 8/18/24 at 3:01.15, it should stay off for 45 seconds and turn on at 3:02

# Output: 2 fields. On/off, next time. Constant loop, so it all gets updated every ms or so.

# FgDateMethods and FgTimer124 are the latest. I think my code may make it more confusing  outside of the date methods.

# Number of little gotcha's, like you mentioned, UTC. This shouldn't be nearly as hard as its been for me. It's still the main project I keep coming back to tho. 

#----------------------------------------------------

# RS Notes : 
# assumption that time is in UTC.  We can add timezones to the function.
# Test run is in minutes.  We will extend the functionality to milliseconds in a seperate function
# inputs
    # StartTime
    # Duration
    # OffTimeInterval
    # CurrentTime
# Outputs
    # Action for the given time
    # Time for next action (the action is the opposite)


import json
#import requests  #For Ajax calls
import time
from datetime import datetime,timedelta,timezone
import math
import logging
from FgDateMethods import *

# Optional logging
#logging.basicConfig(level=logging.ERROR)
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)



#function 
def schedule_action_minutes(StartTime,Duration,OffTimeInterval,CurrentTime):
 # Duration,OffTimeInterval are in minutes
 # StartTime,CurrentTime times are in UTC

    logging.debug("schedule_action_minutes start")
    
    totalinterval = Duration+OffTimeInterval
    logging.debug(totalinterval) 
    # calculate number of seconds between current time and start time
    diff = CurrentTime - StartTime
    #print (timedelta.total_seconds(diff)) 
    totaltimeunits = diff /timedelta(minutes=1)
    logging.debug(totaltimeunits) 
    time_remainder = totaltimeunits % totalinterval
    logging.debug(time_remainder) 

    # if the remainder is less than the duration, switch it on else switch it off
    # Time remainder is a little interesting. We need to finish up the interval
    # if < duration, take the current time, subtract the time_remainder and add the duration        
    # else  take the current time, subtract the time_remainder and add the interval
    # 

    #         
    if time_remainder < Duration :
        FgAction = "On"
        # if < duration, take the current time, subtract the time_remainder and add the duration        
        TimeToNextAction =  CurrentTime - timedelta(minutes = time_remainder) + timedelta(minutes = Duration)
    else : 
        FgAction = "Off"
        # else  take the current time, subtract the time_remainder and add the totalinterval
        TimeToNextAction =  CurrentTime - timedelta(minutes = time_remainder) + timedelta(minutes = totalinterval)
    
    return (FgAction,TimeToNextAction) 



def schedule_action_milliseconds(StartTime,Duration,OffTimeInterval,CurrentTime):
 # Duration,OffTimeInterval are in milliseconds
 # StartTime,CurrentTime times are in UTC

    logging.debug("schedule_action_milliseconds start")
    
    totalinterval = Duration+OffTimeInterval
    logging.debug(totalinterval) 
    # calculate number of seconds between current time and start time
    diff = CurrentTime - StartTime
    #print (timedelta.total_seconds(diff)) 
    totaltimeunits = diff /timedelta(milliseconds=1)
    logging.debug(totaltimeunits) 
    time_remainder = totaltimeunits % totalinterval
    logging.debug(time_remainder) 

    # if the remainder is less than the duration, switch it on else switch it off
    # Time remainder is a little interesting. We need to finish up the interval
    # if < duration, take the current time, subtract the time_remainder and add the duration        
    # else  take the current time, subtract the time_remainder and add the interval
    # 

    #         
    if time_remainder < Duration :
        FgAction = "On"
        # if < duration, take the current time, subtract the time_remainder and add the duration        
        TimeToNextAction =  CurrentTime - timedelta(milliseconds = time_remainder) + timedelta(milliseconds = Duration)
    else : 
        FgAction = "Off"
        # else  take the current time, subtract the time_remainder and add the totalinterval
        TimeToNextAction =  CurrentTime - timedelta(milliseconds = time_remainder) + timedelta(milliseconds = totalinterval)
    
    return (FgAction,TimeToNextAction) 


# run tests

# minutes
# Test 1 
""" TEST_StartTime  = datetime.strptime("2024-01-01 15:00:00", "%Y-%m-%d %H:%M:%S")
TEST_Duration = 1
TEST_OffTimeInterval = 1
TEST_CurrentTime  = datetime.strptime("2024-08-18 15:00:00", "%Y-%m-%d %H:%M:%S")

logging.info("TEST 1")
result = schedule_action_minutes(TEST_StartTime,TEST_Duration,TEST_OffTimeInterval,TEST_CurrentTime)
#logging.info(TEST_StartTime,str(TEST_Duration),str(TEST_OffTimeInterval),TEST_CurrentTime)
logging.info(result)

# Test 2 
TEST_StartTime  = datetime.strptime("2024-01-01 15:00:00", "%Y-%m-%d %H:%M:%S")
TEST_Duration = 1
TEST_OffTimeInterval = 1
TEST_CurrentTime  = datetime.strptime("2024-08-18 15:00:15", "%Y-%m-%d %H:%M:%S")

logging.info("TEST 2")
result = schedule_action_minutes(TEST_StartTime,TEST_Duration,TEST_OffTimeInterval,TEST_CurrentTime)
#logging.info(TEST_StartTime,str(TEST_Duration),str(TEST_OffTimeInterval),TEST_CurrentTime)
logging.info(result)

# Test 3 
TEST_StartTime  = datetime.strptime("2024-01-01 15:00:00", "%Y-%m-%d %H:%M:%S")
TEST_Duration = 1
TEST_OffTimeInterval = 1
TEST_CurrentTime  = datetime.strptime("2024-08-18 15:01:00", "%Y-%m-%d %H:%M:%S")

logging.info("TEST 3")
result = schedule_action_minutes(TEST_StartTime,TEST_Duration,TEST_OffTimeInterval,TEST_CurrentTime)
#logging.info(TEST_StartTime,str(TEST_Duration),str(TEST_OffTimeInterval),TEST_CurrentTime)
logging.info(result)

# Test 4 
TEST_StartTime  = datetime.strptime("2024-01-01 15:00:00", "%Y-%m-%d %H:%M:%S")
TEST_Duration = 1
TEST_OffTimeInterval = 1
TEST_CurrentTime  = datetime.strptime("2024-08-18 15:01:15", "%Y-%m-%d %H:%M:%S")

logging.info("TEST 4")
result = schedule_action_minutes(TEST_StartTime,TEST_Duration,TEST_OffTimeInterval,TEST_CurrentTime)
#logging.info(TEST_StartTime,str(TEST_Duration),str(TEST_OffTimeInterval),TEST_CurrentTime)
logging.info(result)



# milliseconds
# Test 1 
TEST_StartTime  = datetime.strptime("2024-01-01 15:00:00", "%Y-%m-%d %H:%M:%S")
TEST_Duration = 60000
TEST_OffTimeInterval = 60000
TEST_CurrentTime  = datetime.strptime("2024-08-18 15:00:00", "%Y-%m-%d %H:%M:%S")

logging.info("TEST 1 ms")
result = schedule_action_milliseconds(TEST_StartTime,TEST_Duration,TEST_OffTimeInterval,TEST_CurrentTime)
#logging.info(TEST_StartTime,str(TEST_Duration),str(TEST_OffTimeInterval),TEST_CurrentTime)
logging.info(result)

# Test 2 
TEST_StartTime  = datetime.strptime("2024-01-01 15:00:00", "%Y-%m-%d %H:%M:%S")
TEST_Duration = 60000
TEST_OffTimeInterval = 60000
TEST_CurrentTime  = datetime.strptime("2024-08-18 15:00:15", "%Y-%m-%d %H:%M:%S")

logging.info("TEST 2 ms")
result = schedule_action_milliseconds(TEST_StartTime,TEST_Duration,TEST_OffTimeInterval,TEST_CurrentTime)
#logging.info(TEST_StartTime,str(TEST_Duration),str(TEST_OffTimeInterval),TEST_CurrentTime)
logging.info(result)

# Test 3 
TEST_StartTime  = datetime.strptime("2024-01-01 15:00:00", "%Y-%m-%d %H:%M:%S")
TEST_Duration = 60000
TEST_OffTimeInterval = 60000
TEST_CurrentTime  = datetime.strptime("2024-08-18 15:01:00", "%Y-%m-%d %H:%M:%S")

logging.info("TEST 3 ms")
result = schedule_action_milliseconds(TEST_StartTime,TEST_Duration,TEST_OffTimeInterval,TEST_CurrentTime)
#logging.info(TEST_StartTime,str(TEST_Duration),str(TEST_OffTimeInterval),TEST_CurrentTime)
logging.info(result)

# Test 4 
TEST_StartTime  = datetime.strptime("2024-01-01 15:00:00", "%Y-%m-%d %H:%M:%S")
TEST_Duration = 60000
TEST_OffTimeInterval = 60000
TEST_CurrentTime  = datetime.strptime("2034-08-18 15:01:15", "%Y-%m-%d %H:%M:%S")

logging.info("TEST 4 ms")
result = schedule_action_milliseconds(TEST_StartTime,TEST_Duration,TEST_OffTimeInterval,TEST_CurrentTime)
#logging.info(TEST_StartTime,str(TEST_Duration),str(TEST_OffTimeInterval),TEST_CurrentTime)
logging.info(result)
 """




