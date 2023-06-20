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

    #time.sleep(3.09)  ##give a little time to click stop before pumps start

    json_schedule = init_schedule(json_schedule)  #Set next on/off times

    return(json_schedule)


## Schedule is running, will next on time be today or tomorrow, set accordingly
def update_start_date(scheduleStartDate, scheduleEndDate, runEvery, runLength):

    ##End date should never be past
    if (dateABeforeB(scheduleEndDate, datetime.now())):
        raise Exception("Date provided can't be in the past")

    #Get seconds difference -> divide by on/off times to get current date almost time. Remainder time - on time to see if currently running


    ##timeDiff = ms_diff(scheduleStartDate, datetime.now())      ##difference in MS and now

    tempStartDate = datetime_to_current(scheduleStartDate)


    TIME_ELAPSED = datetime.now() - toDateTime(scheduleStartDate)
    seconds_elapsed = TIME_ELAPSED.total_seconds() 


    runFrequency = runEvery + runLength

    msToCurrentTime = seconds_elapsed/runFrequency

    newStartDateTime = addTime(scheduleStartDate, msToCurrentTime, "seconds")

    print(newStartDateTime)




    ##what time does it end on todays date, if later, then currently running
    ##endDate = bring_date_current(scheduleEndDate)
    ##if(dateABeforeB(endDate, currentDate))  ##ended today will start later. Eneded today could be at 8am or midnight so may start again the same day
        ##Get next start time

    ##else    ##base next start time before end time





    currentDate = bring_date_current(scheduleStartDate)
    
    


    #if start-currentDatye is past and end time today is past add day
    if(dateABeforeB(currentDate, datetime.now()) and dateABeforeB(endDate, datetime.now())): #add a day if this schedule is already past
        currentDate = addTime(currentDate, 1, 'days')
        c = currentDate
    return currentDate



def calculate_next_on_time(piSchedules):
    print('calculate_next_on_time \n' + str(piSchedules) + '\n')

    ##set to current start date of today or tomorrow and time
    scheduleStartDate = update_start_date(piSchedules["scheduleStartDate"], piSchedules["scheduleStopDate"], piSchedules["runEvery"], piSchedules["runLength"])

    timeMultiplier = (piSchedules["runEvery"] + piSchedules["runLength"]) / 1000       #calculate largest multiplier to get to next time convert to Seconds from MS
    
    secsDiff = (datetime.now() - toDateTime(scheduleStartDate)).total_seconds()



    diffCount = int(secsDiff/(timeMultiplier)) #Number of timeMultipliers to add, int to round down
    nextOnTime = addTime(scheduleStartDate, diffCount * (timeMultiplier), 'seconds')
    nextOnTime = addTime(nextOnTime, timeMultiplier, 'seconds') #add once more so past now

    nextOffTime = addTime(nextOnTime, piSchedules["runLength"])
    piSchedules["nextOnTime"] = nextOnTime
    piSchedules["nextOffTime"] = nextOffTime
    
    return "";


##init_schedule         init_schedule           init_schedule           init_schedule           init_schedule           init_schedule           init_schedule
def init_schedule(json_schedule):
    print('init_schedule \n')
    get_pretty_print(json_schedule)
    print('\n')
    print( type(json_schedule)  )

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

                    calculate_next_on_time(piSchedules)
                    ##set to current start date of today or tomorrow and time
                    ##scheduleStartDate = update_start_date(piSchedules["scheduleStartDate"], piSchedules["scheduleStopDate"])






                  

                    print('schedule-' + str(piSchedules["scheduleId"]) + '  nexton-' + nextOnTime + ' nextoff-' + nextOffTime)






        if (scheduleCount == -1):  #delete port completely, no schedules left to run
            json_schedule.pop(portCount)
            portCount -= 1

    get_pretty_print(json_schedule)

    return json_schedule

##UPDATE JSON SCHEDULE AND BINARY ARRAY SCHEDULE
def update_schedule(schedule):
    print("UpdateSchefule");

##################################################################################################
#Program run
print('Start Timer')
json_schedule = boostrap()
