# Flash grow timer 7.0 # 
#import RPi.GPIO as GPIO

#On 45 15 seconds, off 45 seconds already running issue

#.from audioop import add
from asyncio.windows_events import NULL
import json
#import requests  #For Ajax calls
import time
import datetime
import keyboard
import math
import datetime
from FgDateMethods import *
from FgScheduleAction_v2 import *

total_num_ports = 24
data_pin=17
latch_pin=22
clock_pin=27
running=26 #set high on boot via config.txt, set low once running (Keep pumps off when app not running so they don't stay on when there is a power loss to the pi)

json_schedule = None  ##in memory JSON file for on/off times
#base_start_time = NULL  ##Json sced gets set with current start time which will be different if already running
use_base_start_time = True    

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
    print(next_time )
    print("End Calc next on time")
    global base_start_time
    base_start_time = next_time[1]

    return next_time


##init_schedule         init_schedule           init_schedule           init_schedule           init_schedule  
def init_schedule(json_schedule):
    print('init_schedule \n')
    print(json_schedule)
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
            #print('pi schedule - ' + str(piSchedules["scheduleId"]) + " - " )

            if (dateABeforeB(piSchedules["scheduleStopDate"], datetime.now())):  #endtime in the past erase
                    ports["piSchedules"].pop(scheduleCount)
                    scheduleCount -= 1  # 1 less schedule
            else: #currently running or future
                if (dateABeforeB(datetime.now(), piSchedules["scheduleStartDate"])):  #future start date
                    print("Future Start Date")
                    piSchedules["nextOnTime"] = piSchedules["scheduleStartDate"]
                    piSchedules["nextOffTime"] = addTime(piSchedules["nextOnTime"], piSchedules["runLength"])
                else: #Currently running
                    print('HAS SCHEDULE running' + str(piSchedules["scheduleId"]))
                    nextOnOff = calculate_next_on_time(piSchedules)     #Start start and end times
                    if(nextOnOff[0] == "On"):
                        piSchedules["nextOnTime"] = nextOnOff[1]
                        piSchedules["nextOffTime"] = addTime(piSchedules["nextOnTime"], piSchedules["runLength"])
                    else:
                        piSchedules["nextOnTime"] = current_dt()
                        piSchedules["nextOffTime"] = nextOnOff[1]
                       

    print('end init_schedule')
    print(json_schedule)
    print('/n')
    
    return json_schedule


#endregion

##Main loop. 
def update_schedule(schedule):
    deletePorts = []
    
    portCount = -1 
    scheduleCount = -1

    for ports in schedule[:]:
        portCount += 1
        scheduleCount = -1
        currentPort = ports["portNumber"]
        deleteSchedules = []
        
        for piSchedules in ports["piSchedules"][:]:    #a loop over a copy of the list referred as [:] 
            scheduleCount += 1

            ##turn off
            if(binary_array[currentPort] != 0 and dateABeforeB(piSchedules["nextOffTime"], datetime.now())):  
                #print(binary_array)
                
                binary_array[currentPort] = 0
                
                nextOnTime = addTime(piSchedules["nextOffTime"], piSchedules["runEvery"])
                if (dateABeforeB(nextOnTime, piSchedules["scheduleStopDate"])):
                    piSchedules["nextOnTime"] = nextOnTime  #off time set when turned on
                else: #last run for this schedule delete it
                    if(len(json_schedule[portCount]['piSchedules']) > 1):
                        #ports.pop('piSchedules')  #remove this schedule
                        ports["piSchedules"].pop(scheduleCount)
                    else: #remove port, no schedules left.
                        deletePorts.append(portCount)

                print(str(datetime.now()) + ' Next on==> ' + str(piSchedules["nextOnTime"]) + ' Next off==>' + str(piSchedules["nextOffTime"]))
                print('')

            ##turn on
            if(binary_array[currentPort] != 1 and dateABeforeB(piSchedules["nextOnTime"], datetime.now()) ):  
                binary_array[currentPort] = 1   ##set port on

                
    #base_start_time = current_dt()  ##Json sced gets set with current start time which will be different if already running
#use_base_start_time = True;   
                global use_base_start_time
                global base_start_time
                if(use_base_start_time):
                    #piSchedules["nextOffTime"] = addTime(base_start_time, piSchedules["runLength"])      ##/Can't ' add to NextOnTime
                    use_base_start_time = False
                else:
                    piSchedules["nextOffTime"] = addTime(piSchedules["nextOnTime"], piSchedules["runLength"])      ##/Can't ' add to NextOnTime

                    #evens on


                if (dateABeforeB(piSchedules["scheduleStopDate"],piSchedules["nextOffTime"] )):  ##If the entire schedule end time is before next off time, set to end 
                    print("End next off time!!!!!!!!!!!!!! SHPOULDN'T BE HERE NOW")
                    piSchedules["nextOffTime"] = piSchedules["scheduleStopDate"]

                print(str(datetime.now()) + 'Turn ONN -> ' + str(piSchedules["nextOnTime"]) + ' Next off==>' + str(piSchedules["nextOffTime"]) )
    if(len(deletePorts) > 0):
        for p in deletePorts:
            json_schedule.pop(p)
            print("main loop delete ports ->" + json_schedule)


##################################################################################################
##Program run
print('Start Timer' + str(datetime.now()))
json_schedule = boostrap()

is_running = True

while True:
    if keyboard.is_pressed("q"):
        if(is_running):
            print("q pressed, pausing loop")
        
        is_running = False
    else:
        is_running = True    
        update_schedule(json_schedule)
        



