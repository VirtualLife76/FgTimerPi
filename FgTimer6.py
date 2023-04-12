# Flash grow timer 6.0 # 
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

#GPIO.setmode(GPIO.BCM) ## Use board pin numbering
#GPIO.setwarnings(False)

##READ JSON     READ JSON     READ JSON     READ JSON     READ JSON     READ JSON     READ JSON     READ JSON     READ JSON     READ JSON     
def read_json_file():
    try:
        with open(schedule_file, 'r') as json_data:
            json_data = json.load(json_data)
            return json_data
    except FileNotFoundError:
        print("File not found." + schedule_file)

#SHIFTER     SHIFTER     SHIFTER     SHIFTER     SHIFTER     SHIFTER     SHIFTER     SHIFTER     SHIFTER
#Main function to set shift registers/RELAYS
class Shifter(object):
    def __init__(self):
        print('init shifter!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        #GPIO.setup(data_pin, GPIO.OUT) 
        #GPIO.setup(latch_pin, GPIO.OUT) 
        #GPIO.setup(clock_pin, GPIO.OUT, initial=GPIO.LOW) ## Setup GPIO Pin to OUT
        #GPIO.setup(running, GPIO.OUT, initial=GPIO.LOW)  ## switch to turn on shift registers. Default high set in config.txt
        tmpAry = binary_array

        self.binary_array_last = [] #tmpAry.copy()
        self.shift_output()
        print(tmpAry)
    def shift_output(self):
        
        #print(self.binary_array_last)
        if (binary_array != self.binary_array_last):
            print('shift_Output')
            print(binary_array)
            bits = {0: False, 1: True}
            
            #GPIO.output(latch_pin, LOW)
            for p in reversed(binary_array):
                #GPIO.output(clock_pin, LOW)
                #GPIO.output(data_pin, bits[p])
                #GPIO.output(clock_pin, HIGH)
                print("blah")
            #GPIO.output(latch_pin, HIGH)

            self.binary_array_last = binary_array.copy()

##Bootstrap         Bootstrap          Bootstrap        Bootstrap       Bootstrap       Bootstrap       Bootstrap       Bootstrap       Bootstrap
shift = Shifter()
def boostrap():    
    #GPIO.setup(running, GPIO.OUT, initial=GPIO.HIGH)  #Turn off all pumps by setting all OE 

    shift.shift_output()  #Set each shift register to low (binary_array set to all 0's on create)
        
    json_schedule = read_json_file()  #Get json data from file into memory

    time.sleep(3.09)  ##give a little time to click stop before pumps start

    json_schedule = init_schedule(json_schedule)  #Set next on/off times

    return(json_schedule)


def update_start_date(scheduleStartDate, scheduleEndDate):
    currentDate = bring_date_current(scheduleStartDate)
    endDate =bring_date_current(scheduleEndDate)
    #if start-currentDatye is past and end time today is past add day
    if(dateABeforeB(currentDate, datetime.now()) and dateABeforeB(endDate, datetime.now())): #add a day if this schedule is already past
        currentDate = addTime(currentDate, 1, 'days')
    c = currentDate
    return currentDate

##init_schedule         init_schedule           init_schedule           init_schedule           init_schedule           init_schedule           init_schedule
def init_schedule(json_schedule):
    print('init_schedule')
    print(json_schedule)
    portCount = -1 #keep track of array number in case entire row needs deleting because no schedule

    for ports in json_schedule[:]: #For each port (punp) see if a current or future schedule exists
        portCount += 1
        scheduleCount = -1
        ports.pop('plantType')    #Remove fields that are not needed
        ports.pop('substrate')
        ports.pop('plantedDate')
        ports.pop('notes')
        ports.pop('plantStatus')

        for piSchedules in ports["piSchedules"][:]:    #a loop over a copy of the list referred as [:] 
            scheduleCount += 1
            print('pi schedule')
            piSchedules.pop('plantId')  #Remove fields that are not needed
            piSchedules.pop('scheduleOrder')

            if (dateABeforeB(datetime.now(), piSchedules["scheduleStartDate"])):  #if startime future
                print('future start datte')
                piSchedules["nextOnTime"] = piSchedules["scheduleStartDate"]
                piSchedules["nextOffTime"] = addTime(piSchedules["nextOnTime"], piSchedules["runLength"])
            else:  #started and ended or currently running
                if (dateABeforeB(piSchedules["scheduleStopDate"], datetime.now())):  #endtime in the past erase
                    ports["piSchedules"].pop(scheduleCount)
                    scheduleCount -= 1  # 1 less schedule
                else: #already running
                    print('HAS SCHEDULE sechedule')
                    ##set to current start date of today or tomorrow and time
                    scheduleStartDate = update_start_date(piSchedules["scheduleStartDate"], piSchedules["scheduleStopDate"])

                    #Check if currently between hours to run
                    print(timeABeforeB(toTime(scheduleStartDate), toTime(datetime.now()) ) )
                    print(timeABeforeB(toTime(datetime.now()), toTime(piSchedules["scheduleStopDate"])))

                    if(timeABeforeB(toTime(scheduleStartDate), toTime(datetime.now()))) and \
                        timeABeforeB(toTime(datetime.now()), toTime(piSchedules["scheduleStopDate"]) ):

                        print('currently running!!!!!')
                        timeMultiplier = (piSchedules["runEvery"] + piSchedules["runLength"]) / 1000    #calculate largest multiplier to get to next time
                        secsDiff = (datetime.now() - toDateTime(scheduleStartDate)).total_seconds()
                        diffCount = int(secsDiff/(timeMultiplier)) #Number of timeMultipliers to add, int to round down
                        nextOnTime = addTime(scheduleStartDate, diffCount * (timeMultiplier), 'seconds')
                        nextOnTime = addTime(nextOnTime, timeMultiplier, 'seconds') #add once more so past now

                        nextOffTime = addTime(nextOnTime, piSchedules["runLength"])
                        piSchedules["nextOnTime"] = nextOnTime
                        piSchedules["nextOffTime"] = nextOffTime
                    else:   #running, just notcurrently. Set to future start date
                        print('Restart at a later date')
                        nextOnTime = scheduleStartDate
                        nextOffTime = addTime(nextOnTime, piSchedules["runLength"])
                        print(nextOnTime)

                        piSchedules["nextOnTime"] = nextOnTime
                        piSchedules["nextOffTime"] = nextOffTime

                    print('schedule-' + str(piSchedules["scheduleId"]) + '  nexton-' + nextOnTime + ' nextoff-' + nextOffTime)

        if (scheduleCount == -1):  #delete port completely, no schedules left to run
            json_schedule.pop(portCount)
            portCount -= 1

    print("=====init done====" + str(datetime.now()))

    print(len(json_schedule[0]['piSchedules']   ))

    print(json_schedule)
    return json_schedule

##UPDATE JSON SCHEDULE AND BINARY ARRAY SCHEDULE
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
                print('Turn OFF-> ' + str(currentPort) + ' @' + str(datetime.now()) + ' on==> ' + str(piSchedules["nextOnTime"]) + ' off==>' + str(piSchedules["nextOffTime"]))
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
            
            ##turn on
            if(binary_array[currentPort] != 1 and dateABeforeB(piSchedules["nextOnTime"], datetime.now()) ):  
                print(binary_array)
                print('Turn ON -> ' + str(currentPort) + ' -- ' + str(datetime.now()) + ' on==> ' + str(piSchedules["nextOnTime"]) + ' off==>' + str(piSchedules["nextOffTime"]))
                binary_array[currentPort] = 1
                nextOffTime = addTime(piSchedules["nextOnTime"], piSchedules["runLength"])
                if (dateABeforeB(piSchedules["scheduleStopDate"],nextOffTime )):
                    piSchedules["nextOffTime"] = piSchedules["scheduleStopDate"]
    if(len(deletePorts) > 0):
        for p in deletePorts:
            json_schedule.pop(p)
            print(json_schedule)


##################################################################################################
#Program run
print('Start Timer')
json_schedule = boostrap()

#PIO.setup(running, GPIO.OUT, initial=GPIO.LOW)     #set running pin low (enabled) so shift registers will work


while True:
#startShiftTime = datetime.now()
    update_schedule(json_schedule)
    shift.shift_output()
#     ##time.sleep(1)
#     endShitTime = datetime.now()
#     #print(ms_diff(startShiftTime, endShitTime))
#     #print(json_schedule)
# def end():
#     print('end')