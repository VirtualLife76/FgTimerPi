# Flash grow timer 7.0 # 
#import RPi.GPIO as GPIO

#.from audioop import add
import json
#import requests  #For Ajax calls
import time
import datetime
import keyboard
import math
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
    ##Keeping very separate for debugging purposes for now
    runFrequency = piSchedules["runEvery"]  + piSchedules["runLength"]  #on/off total time
    

    currentDate = bring_date_current(toDateTime(piSchedules["scheduleStartDate"]), toDateTime(piSchedules["scheduleStopDate"]))

    time_elapsed = datetime.now() - currentDate

    time_elapsed_ms = time_elapsed.total_seconds() * 1000

    interval = time_elapsed_ms / runFrequency   #how many times have on/off elapsed since start date/time and now
    
    total = math.floor(interval) * runFrequency #round down interval and get total time elapsed 
    
    almost = addTime(currentDate, total)
    
    is_on = addTime(almost, piSchedules["runEvery"],"milliseconds", 'dt')
    
    if (is_on > datetime.now()):    #Currently supposed to be running
        print("next time to turn on:" + str(datetime.now()))
        return datetime.now()
    else:
        print("nope")   #Not currently running
        is_on = addTime(is_on, piSchedules["runLength"],"milliseconds", 'dt')
        print("next time to turn on x:" + str(is_on))
        return is_on 
 

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
                    next_on_time = calculate_next_on_time(piSchedules)
                    piSchedules["nextOnTime"] = next_on_time
                    piSchedules["nextOffTime"] = addTime(next_on_time, piSchedules["runLength"])
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
            #print(str(schedules["nextOnTime"]) + ' -- ' + str(datetime.now()) + '---' + str(schedules["nextOffTime"]) + '---' + str(currentPort )) 
            #print(' -- ' + str(dateABeforeB(piSchedules["nextOffTime"],  datetime.now())) + ' --- ' + str(dateABeforeB(piSchedules["nextOnTime"], datetime.now())))
            scheduleCount += 1

            ##turn off
            if(binary_array[currentPort] != 0 and dateABeforeB(piSchedules["nextOffTime"], datetime.now())):  
                print(binary_array)
                
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

                print('Turn OFF-> ' + str(currentPort) + ' ' + str(datetime.now()) + ' on==> ' + str(piSchedules["nextOnTime"]) + ' off==>' + str(piSchedules["nextOffTime"]))
            
            ##turn on
            if(binary_array[currentPort] != 1 and dateABeforeB(piSchedules["nextOnTime"], datetime.now()) ):  
                print("On array" + str(binary_array))
                print('Turn ON --> ' + str(currentPort) + ' -- ' + str(datetime.now()) + ' current next off==>' + str(piSchedules["nextOffTime"]))

                binary_array[currentPort] = 1   ##set port on


                test = addTime(piSchedules["nextOnTime"], piSchedules["runLength"])
                piSchedules["nextOffTime"] = addTime(piSchedules["nextOnTime"], piSchedules["runLength"])

                print(piSchedules["nextOffTime"] + " \n" + addTime(piSchedules["nextOnTime"], piSchedules["runLength"]))



                if (dateABeforeB(piSchedules["scheduleStopDate"],piSchedules["nextOffTime"] )):  ##If the entire schedule end time is before next off time, set to end 
                    print("End next off time")
                    piSchedules["nextOffTime"] = piSchedules["scheduleStopDate"]

                print('Turn ONN -> ' + str(currentPort) + ' -- ' + str(datetime.now()) + ' on==> ' + str(piSchedules["nextOnTime"]) + ' Next off==>' + str(piSchedules["nextOffTime"]) + ' ' + test)
    if(len(deletePorts) > 0):
        for p in deletePorts:
            json_schedule.pop(p)
            print("main loop delete ports ->" + json_schedule)


##################################################################################################
##Program run
print('Start Timer')
json_schedule = boostrap()

is_running = True

while True:
    if keyboard.is_pressed("q"):
        print("q pressed, pausing loop")
        is_running = False
    else:
        is_running = True    
        update_schedule(json_schedule)
        



