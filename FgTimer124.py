# Flash grow timer 7.0 # 
#import RPi.GPIO as GPIO

import json
#import requests  #For Ajax calls
import time
from FgDateMethods import *

total_num_ports = 24
data_pin=17
latch_pin=22
clock_pin=27
running=26 #set high on boot via config.txt, set low once running (Keep pumps off when app not running so they don't stay on when there is a power loss to the pi)

json_schedule = None  ##in memory JSON file for on/off times

binary_array = [0] * total_num_ports
schedule_file = "1sec1through24test.json"  #File name for main plant schedule
schedule_file = "FgSchedule.json"  #File name for main plant schedule
HIGH = True
LOW = False

def get_pretty_print(json_object):
    return json.dumps(json_object, sort_keys=True, indent=4, separators=(',', ': '))

#region Startup Functions

##READ JSON     READ JSON     READ JSON     READ JSON     READ JSON     READ JSON     READ JSON     READ JSON     READ JSON     READ JSON     
def read_json_file():
    try:
        with open(schedule_file, 'r') as json_data:
            json_data = json.load(json_data)
            
            return json_data
    except FileNotFoundError:
        print("File not found." + schedule_file)


##Bootstrap         Bootstrap          Bootstrap        Bootstrap       Bootstrap       Bootstrap       Bootstrap       Bootstrap       Bootstrap
def boostrap():    

    json_schedule = read_json_file()  #Get json data from file into memory
    
    json_schedule = init_schedule(json_schedule)  #Set next on/off times

    return(json_schedule)

##calculate_next_on_time        calculate_next_on_time          calculate_next_on_time          calculate_next_on_time
def calculate_next_on_time(piSchedules):    ##Currently running and just booted, figure out next on time


    #schedule_action_milliseconds(StartTime,Duration,OffTimeInterval,CurrentTime):

    next_time = schedule_action_milliseconds( toDateTime(piSchedules["scheduleStartDate"]), piSchedules["runEvery"], piSchedules["runLength"], current_dt()  )
    print(next_time)


#     ##Keeping very separate for debugging purposes for now
#     runFrequency = piSchedules["runEvery"]  + piSchedules["runLength"]  #on/off total time
 
#     currentDate = bring_date_current(toDateTime(piSchedules["scheduleStartDate"]), toDateTime(piSchedules["scheduleStopDate"]))

#     time_elapsed = current_dt() - currentDate

#     time_elapsed_ms = time_elapsed.total_seconds() * 1000

#     interval = time_elapsed_ms / runFrequency   #how many times have on/off elapsed since start date/time and now
    

#     total = math.floor(interval) * runFrequency #round down interval and get total time elapsed 
    
#     #round_down = math.floor(interval * runFrequency)
    

#     almost = addTime(currentDate, total)
    
#     ##diff = (current_dt() - toDateTime(almost))
    
#     ##start_time = addTime(almost, piSchedules["runEvery"],"milliseconds", 'dt')
    
#     ##currently time should be short time away and off
#     startTimeFound = True
#     while (startTimeFound):
#         currentStartTime = almost
#         if (currentStartTime < current_dt()):
#             newStartTime = addTime(almost, piSchedules["runEvery"],"milliseconds", 'dt')
#             if(newStartTime > current_dt()): #currently running
#                 #subract last for start time use new for end
#                 print( str(currentStartTime) + " - " + str(newStartTime))
#                 startTimeFound = False

#                 #If next start time 
                
# #Start time < now?  If there has been no end time since the start time
#   #loop find current time       
                
#     start_today = bring_date_current(toDateTime(piSchedules["scheduleStartDate"]), current_dt())
#     end_today = bring_date_current(toDateTime(piSchedules["scheduleEndDate"]), current_dt())  #not right, shouldn't change end year?
 


#     timeABeforeB()

    



# ##

# #now is off, should always be off and before now?!
                
# #If                 


#     print("Start Time: " + str(start_time) + " current dr: " + str(current_dt()))

#     if (start_time > current_dt()):    #Currently supposed to be running
#         piSchedules["nextOnTime"] = current_dt()      #start immediately
        
#         piSchedules["nextOffTime"] = addTime(start_time, piSchedules["runLength"])      #set off time based on when it should have started
        
#         print("Should be on now :" + str(piSchedules["nextOnTime"]) + " off - " + piSchedules["nextOffTime"])
#         #return datetime.now()
#     else:
#         print("nope")   #Not currently running
        
#         start_time = addTime(start_time, piSchedules["runLength"],"milliseconds", 'dt')  #Wrong
        
#         piSchedules["nextOnTime"] = start_time      #start time in future
#         piSchedules["nextOffTime"] = addTime(start_time, piSchedules["runLength"])      #set off time based on when it should have started
#         print("next on:" + str(start_time) + " off - " + str(piSchedules["nextOffTime"])) #THIS IS WRONG!!
#         #return start_time 
        
#     print('end calculate_next_on_time')
#     print(piSchedules)

##init_schedule         init_schedule           init_schedule           init_schedule           init_schedule  
def init_schedule(json_schedule):
    print('init_schedule \n')
    get_pretty_print(json_schedule)
    print('\n')

    portCount = -1 #keep track of array number in case entire row needs deleting because no schedule

    for ports in json_schedule[:]: #For each port (pump) see if a current or future schedule exists
        portCount += 1
        scheduleCount = -1
        ports.pop('plantType')    #Remove fields that are not needed
        ports.pop('substrate')
        ports.pop('plantedDate')
        ports.pop('notes')

        for piSchedules in ports["piSchedules"][:]:    #a loop over a copy of the list referred as [:] (Each Port/plant)
            scheduleCount += 1
            print('pi schedule - ' + str(piSchedules["scheduleId"]) + " - " )

            if (dateABeforeB(piSchedules["scheduleStopDate"], datetime.now())):  #endtime in the past erase
                    ports["piSchedules"].pop(scheduleCount)
                    scheduleCount -= 1  # 1 less schedule
            else: #currently running or future
                if (dateABeforeB(datetime.now(), piSchedules["scheduleStartDate"])):  #future start date
                    piSchedules["nextOnTime"] = piSchedules["scheduleStartDate"]
                    piSchedules["nextOffTime"] = addTime(piSchedules["nextOnTime"], piSchedules["runLength"])
                else: #Currently running
                    print('HAS SCHEDULE running' + str(piSchedules["scheduleId"]))

                    piSchedules["nextOnTime"] = calculate_next_on_time(piSchedules)
                    piSchedules["nextOffTime"] = addTime(piSchedules["nextOnTime"], piSchedules["runLength"])
    return ""


#endregion

##################################################################################################
##Program run
print('Start Timer')
json_schedule = boostrap()








