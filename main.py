import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import random

from plot_result import plot_queues
from random_times import *


random.seed(30)
np.random.seed(30)


# main fuction which fully runs the simulation whenever called
def run_simulation(warmup_time = 60, operation_time = 540):

    # events: 
    #         incoming_part_1       -> code: 0
    #         incoming_part_2       -> code: 1
    #         machineA_down         -> code: 2
    #         machineB_down         -> code: 3
    #         machineA_repair       -> code: 4
    #         machineB_repair       -> code: 5
    #         machineA_finish       -> code: 6
    #         machineB_finish_part1 -> code: 7
    #         machineB_finish_part2 -> code: 8
    #         machineC_finish_part1 -> code: 9
    #         machineC_finish_part2 -> code: 10

    time_now  = 0               # current time of simulation
    num_part1 = 0               # total number of part 1s entered
    num_part2 = 0               # total number of part 2s entered
    time_part1_in_system = 0    # total time that part 1s has been in the system (cumulative)
    time_part2_in_system = 0    # total time that part 2s has been in the system (cumulative)

    FEL = []
    machines_status = {'m1':[], # machine A status (list contains the id of the part that is being processed)
                       'm2':[], # machine B status
                       'm3':[]} # machine C status

    machines_isdown = {'m1':False, # whether machine A is down or not
                       'm2':False} # whether machine B is down or not
   
    machines_worktime = {'m1':0, # total runtime of mchine A
                         'm2':0, # total runtime of mchine B
                         'm3':0} # total runtime of mchine C
   
    total_downtime =    {'m1':0, # total downtime of mchine A
                         'm2':0, # total downtime of mchine B
                         'm3':0} # total downtime of mchine C

    machines_queue= {'m1':[],            # queue of machine A
                     'm2':{'p1':[],      # queue of machine B for part 1s
                           'p2':[]},     # queue of machine B for part 2s
                     'm3':{'p1':[],      # queue of machine C for part 1s
                           'p2':[]}}     # queue of machine C for part 2s

    machines_queue_time = {'m1':[],            # list containing times in which parts has been queued in machine A 
                           'm2':{'p1':[],      # ... machine B 
                                 'p2':[]},     # ... machine B 
                           'm3':{'p1':[],      # ... machine C
                                 'p2':[]}}     # ... machine C

    machines_num_parts= {'m1':0,            # number of parts processed by machine A
                         'm2':{'p1':0,      # number of part 1s processed by machine B
                               'p2':0},     # number of part 2s processed by machine B
                         'm3':{'p1':0,      # number of part 1s processed by machine C
                               'p2':0}}     # number of part 2s processed by machine C

    queue_log = {'m1':[],            
                    'm2':{'p1':[],      
                          'p2':[]},    
                    'm3':{'p1':[],      
                          'p2':[]}}
    time_log = []
    id_counter = 0
    parts_log = dict()

    # START
    FEL.append((0,0)) # first part 1 enters at time 0
    FEL.append((1,0)) # first part 2 enters at time 0
    FEL.append((2,machine_A_next_downtime())) # first down of machine A
    FEL.append((3,machine_B_next_downtime())) # first down of machine B

    # WARM-UP
    print('Warming up system ...',end=' ')
    # warming up the system without recording statistics
    while time_now < warmup_time:
        # taking the nearest event from FEL
        min_time = float('inf')
        min_code = None
        for code , t in FEL:
            if t < min_time:
                min_time = t
                min_code = code

        time_now = min_time
        FEL.remove((min_code,min_time))

        # checking the code of the nearest event:
        ########################### EVENT 0 ##############################
        
        if  min_code == 0: 

            # adding next enter time to FEL
            id_counter += 1
            parts_log[f'{id_counter}']={
                'type':1,
                'arrival_time':time_now}

            next_arrival = time_now + part_1_arrival_time()
            FEL.append((0,next_arrival))

            if not machines_isdown['m1']: # if machine A is not down
                if machines_status['m1'] == []: # if machine A is idle
                    machines_status['m1'].append(str(id_counter))
                    parts_log[str(id_counter)]['entered_machine_A_time'] = time_now
                    finish_time = time_now + machine_A_worktime()
                    FEL.append((6,finish_time))
                else: 
                    machines_queue['m1'].append(str(id_counter))
                    machines_queue_time['m1'].append(time_now)
                    parts_log[str(id_counter)]['entered_queue_B_time'] = time_now

            else: # if machine A is down
                if (machines_status['m2'] == []) and (not machines_isdown['m2']):
                    machines_status['m2'].append(str(id_counter))
                    parts_log[str(id_counter)]['entered_machine_B_time'] = time_now
                    finish_time = time_now + machine_B_worktime_for_part1()
                    FEL.append((7,finish_time))
                else:
                    machines_queue['m2']['p1'].append(str(id_counter))
                    machines_queue_time['m2']['p1'].append(time_now)
                    parts_log[str(id_counter)]['entered_queue_B_time'] = time_now

        ########################### EVENT 1 ##############################
        elif min_code == 1:

            id_counter += 1
            parts_log[f'{id_counter}']={
                'type':2,
                'arrival_time':time_now}

           # adding next enter time to FEL
            next_arrival = time_now + part_2_arrival_time()
            FEL.append((1,next_arrival))
            
            if not machines_isdown['m2']:
                if machines_status['m2'] == []:
                    machines_status['m2'].append(str(id_counter))
                    parts_log[str(id_counter)]['entered_machine_B_time'] = time_now
                    finish_time = time_now + machine_B_worktime()
                    FEL.append((8,finish_time))
                else:
                    machines_queue['m2']['p2'].append(str(id_counter))
                    machines_queue_time['m2']['p2'].append(time_now)
                    parts_log[str(id_counter)]['entered_queue_B_time'] = time_now

            else: 
                machines_queue['m2']['p2'].append(str(id_counter))
                machines_queue_time['m2']['p2'].append(time_now)
                parts_log[str(id_counter)]['entered_queue_B_time'] = time_now

        ########################### EVENT 2 ##############################
        elif min_code == 2: 

            machines_isdown['m1'] = True
            for p in machines_queue['m1']:
                parts_log[p]['moved_from_queue_AtoB_time'] = time_now
            machines_queue['m2']['p1'] += machines_queue['m1']
            machines_queue_time['m2']['p1'] += machines_queue_time['m1']
            machines_queue['m1'] = []
            machines_queue_time['m1'] = []
            repair_time = time_now + machine_A_downtime()
            FEL.append((4,repair_time))

        ########################### EVENT 3 ##############################
        elif min_code == 3: 

            machines_isdown['m2'] = True
            repair_time = time_now + machine_B_downtime()
            FEL.append((5,repair_time))

        ########################### EVENT 4 ##############################
        elif min_code == 4:

            machines_isdown['m1'] = False
            for p in machines_queue['m2']['p1']:
                parts_log[p]['moved_from_queue_BtoA_time'] = time_now
            machines_queue['m1'] += machines_queue['m2']['p1']
            machines_queue_time['m1'] += machines_queue_time['m2']['p1']
            machines_queue['m2']['p1'] = []
            machines_queue_time['m2']['p1'] = []
            next_down_time = time_now + machine_A_next_downtime()
            FEL.append((2,next_down_time))

        ########################### EVENT 5 ##############################
        elif min_code == 5: 
            
            machines_isdown['m2'] = False
            next_down_time = time_now + machine_B_next_downtime()
            FEL.append((3,next_down_time))

        ########################### EVENT 6 ##############################
        elif min_code == 6:

            leaving_part = machines_status['m1'][0]
            parts_log[leaving_part]['left_machine_A_time'] = time_now

            if len(machines_queue['m1']) == 0:
                machines_status['m1'] = []
                
            else:

                incoming_part = machines_queue['m1'].pop(0)
                machines_status['m1'] = [incoming_part]
                parts_log[incoming_part]['entered_machine_A_time'] = time_now
                out_time = machines_queue_time['m1'].pop(0)
                # parts_log[leaving_part]['working_time_in_machine_A'] = time_now - out_time
                finish_time = time_now + machine_A_worktime()
                FEL.append((6,finish_time))

            if machines_status['m3'] == []:
                
                machines_status['m3'].append(leaving_part)
                parts_log[leaving_part]['entered_machine_C_time'] = time_now
                finish_time = time_now + machine_C_worktime()
                FEL.append((9,finish_time))
            else:

                machines_queue['m3']['p1'].append(leaving_part)
                parts_log[leaving_part]['entered_queue_C_time'] = time_now
                machines_queue_time['m3']['p1'].append(time_now)

        ########################### EVENT 7 ##############################
        elif min_code == 7:

            leaving_part = machines_status['m2'][0]
            parts_log[leaving_part]['left_machine_B_time'] = time_now

            if (len(machines_queue['m2']['p1']) == 0) and (len(machines_queue['m2']['p2']) == 0): # در صورت خالی بودن صف های ماشین ب
                machines_status['m2'] = []

            elif len(machines_queue['m2']['p1']) != 0:
                incoming_part = machines_queue['m2']['p1'].pop(0)
                machines_status['m2'] = [incoming_part]
                parts_log[incoming_part]['entered_machine_B_time'] = time_now
                out_time = machines_queue_time['m2']['p1'].pop(0)
                # parts_log[leaving_part]['working_time_in_machine_B'] = time_now - out_time
                finish_time = time_now + machine_B_worktime_for_part1()
                FEL.append((7,finish_time))

            elif len(machines_queue['m2']['p2']) != 0:
                machines_status['m2'] = [incoming_part]
                parts_log[incoming_part]['entered_machine_B_time'] = time_now
                out_time = machines_queue_time['m2']['p2'].pop(0)
                # parts_log[leaving_part]['working_time_in_machine_B'] = time_now - out_time
                finish_time = time_now + machine_B_worktime()
                FEL.append((8,finish_time))
            
            if machines_status['m3'] == []: 

                machines_status['m3'].append(leaving_part)
                parts_log[leaving_part]['entered_machine_C_time'] = time_now
                finish_time = time_now + machine_C_worktime()
                FEL.append((9,finish_time))

            else:

                machines_queue['m3']['p1'].append(leaving_part)
                parts_log[leaving_part]['entered_queue_C_time'] = time_now
                machines_queue_time['m3']['p1'].append(time_now)

        ########################### EVENT 8 ##############################
        elif min_code == 8:
            
            leaving_part = machines_status['m2'][0]
            parts_log[leaving_part]['left_machine_B_time'] = time_now

            if (len(machines_queue['m2']['p1']) == 0) and (len(machines_queue['m2']['p2']) == 0): # در صورت خالی بودن صف های ماشین ب
                machines_status['m2'] = []

            elif len(machines_queue['m2']['p1']) != 0: 

                incoming_part = machines_queue['m2']['p1'].pop(0)
                machines_status['m2'] = [incoming_part]
                parts_log[incoming_part]['entered_machine_B_time'] = time_now
                out_time = machines_queue_time['m2']['p1'].pop(0)
                # parts_log[leaving_part]['working_time_in_machine_B'] = time_now - out_time
                finish_time = time_now + machine_B_worktime_for_part1()
                FEL.append((7,finish_time))

            elif len(machines_queue['m2']['p2']) != 0: 

                incoming_part = machines_queue['m2']['p2'].pop(0)
                machines_status['m2'] = [incoming_part]
                parts_log[incoming_part]['entered_machine_B_time'] = time_now
                out_time = machines_queue_time['m2']['p2'].pop(0)
                # parts_log[leaving_part]['working_time_in_machine_B'] = time_now - out_time
                finish_time = time_now + machine_B_worktime()
                FEL.append((8,finish_time))
            
            if machines_status['m3'] == []: 

                machines_status['m3'].append(leaving_part)
                parts_log[leaving_part]['entered_machine_C_time'] = time_now
                finish_time = time_now + machine_C_worktime()
                FEL.append((10,finish_time))
            else:

                machines_queue['m3']['p2'].append(leaving_part)
                parts_log[leaving_part]['entered_queue_C_time'] = time_now
                machines_queue_time['m3']['p2'].append(time_now)

        ########################### EVENT 9 ##############################
        elif min_code == 9:

            leaving_part = machines_status['m3'][0]
            parts_log[leaving_part]['left_machine_C_time'] = time_now

            if (len(machines_queue['m3']['p1']) == 0) and (len(machines_queue['m3']['p2']) == 0): 
                machines_status['m3'] = []

            elif len(machines_queue['m3']['p1']) != 0: 

                incoming_part = machines_queue['m3']['p1'].pop(0)
                machines_status['m3'] = [incoming_part]
                parts_log[incoming_part]['entered_machine_C_time'] = time_now
                out_time = machines_queue_time['m3']['p1'].pop(0)
                # parts_log[leaving_part]['working_time_in_machine_C'] = time_now - out_time
                finish_time = time_now + machine_C_worktime()
                FEL.append((9,finish_time))

            elif len(machines_queue['m3']['p2']) != 0:

                incoming_part = machines_queue['m3']['p2'].pop(0)
                machines_status['m3'] = [incoming_part]
                parts_log[incoming_part]['entered_machine_C_time'] = time_now
                out_time = machines_queue_time['m3']['p2'].pop(0)
                # parts_log[leaving_part]['working_time_in_machine_C'] = time_now - out_time
                finish_time = time_now + machine_C_worktime()
                FEL.append((10,finish_time))

        ########################### EVENT 10 ##############################
        elif min_code == 10:

            leaving_part = machines_status['m3'][0]
            parts_log[leaving_part]['left_machine_C_time'] = time_now

            if (len(machines_queue['m3']['p1']) == 0) and (len(machines_queue['m3']['p2']) == 0): 
                machines_status['m3'] = []
            elif len(machines_queue['m3']['p1']) != 0:

                incoming_part = machines_queue['m3']['p1'].pop(0)
                machines_status['m3'] = [incoming_part]
                parts_log[incoming_part]['entered_machine_C_time'] = time_now
                out_time = machines_queue_time['m3']['p1'].pop(0)
                # parts_log[leaving_part]['working_time_in_machine_C'] = time_now - out_time
                finish_time = time_now + machine_C_worktime()
                FEL.append((9,finish_time))

            elif len(machines_queue['m3']['p2']) != 0: 

                incoming_part = machines_queue['m3']['p2'].pop(0)
                machines_status['m3'] = [incoming_part]
                parts_log[incoming_part]['entered_machine_C_time'] = time_now
                out_time = machines_queue_time['m3']['p2'].pop(0)
                # parts_log[leaving_part]['working_time_in_machine_C'] = time_now - out_time
                finish_time = time_now + machine_C_worktime()
                FEL.append((10,finish_time))


    print('Warm-up finished! | Starting main operation ...',end=' ')

    # main loop with recording the stats
    # OPERATION
    while time_now < (warmup_time + operation_time):

        queue_log['m1'].append(len(machines_queue['m1']))
        queue_log['m2']['p1'].append(len(machines_queue['m2']['p1']))
        queue_log['m2']['p2'].append(len(machines_queue['m2']['p2']))
        queue_log['m3']['p1'].append(len(machines_queue['m3']['p1']))
        queue_log['m3']['p2'].append(len(machines_queue['m3']['p2']))
        time_log.append(time_now - warmup_time)

        min_time = float('inf')
        min_code = None
        for code , t in FEL:
            if t < min_time:
                min_time = t
                min_code = code
        
        time_now = min_time
        FEL.remove((min_code,min_time))

        ########################### EVENT 0 ##############################
    
        if  min_code == 0: 
            id_counter += 1
            parts_log[f'{id_counter}']={
                'type':1,
                'arrival_time':time_now}

            num_part1 += 1
            next_arrival = time_now + part_1_arrival_time()
            FEL.append((0,next_arrival))

            if not machines_isdown['m1']:
                if machines_status['m1'] == []:

                    machines_num_parts['m1'] += 1
                    machines_status['m1'].append(str(id_counter))
                    parts_log[str(id_counter)]['entered_machine_A_time'] = time_now
                    wt = machine_A_worktime()
                    time_part1_in_system += wt
                    machines_worktime['m1'] += wt
                    finish_time = time_now + wt
                    FEL.append((6,finish_time))
                else:
                    machines_queue['m1'].append(str(id_counter))
                    machines_queue_time['m1'].append(time_now)
                    parts_log[str(id_counter)]['entered_queue_B_time'] = time_now

            else: 
                if (machines_status['m2'] == []) and (not machines_isdown['m2']):
                    machines_num_parts['m2']['p1'] += 1
                    machines_status['m2'].append(str(id_counter))
                    parts_log[str(id_counter)]['entered_machine_B_time'] = time_now
                    wt = machine_B_worktime()
                    time_part1_in_system += wt
                    machines_worktime['m2'] += wt
                    finish_time = time_now + wt
                    FEL.append((7,finish_time))
                else:

                    machines_queue['m2']['p1'].append(str(id_counter))
                    machines_queue_time['m2']['p1'].append(time_now)
                    parts_log[str(id_counter)]['entered_queue_B_time'] = time_now

        ########################### EVENT 1 ##############################

        elif min_code == 1:

            id_counter += 1
            parts_log[f'{id_counter}']={
                'type':2,
                'arrival_time':time_now}

            num_part2 += 1
            next_arrival = time_now + part_2_arrival_time()
            FEL.append((1,next_arrival))
            
            if not machines_isdown['m2']:
                if machines_status['m2'] == []: 

                    machines_num_parts['m2']['p2'] += 1

                    machines_status['m2'].append(str(id_counter))
                    parts_log[str(id_counter)]['entered_machine_B_time'] = time_now

                    wt = machine_B_worktime()
                    time_part2_in_system += wt
                    machines_worktime['m2'] += wt
                    finish_time = time_now + wt
                    FEL.append((8,finish_time))
                else:
                    
                    machines_queue['m2']['p2'].append(str(id_counter))
                    machines_queue_time['m2']['p2'].append(time_now)
                    parts_log[str(id_counter)]['entered_queue_B_time'] = time_now
            else:
               
                machines_queue['m2']['p2'].append(str(id_counter))
                machines_queue_time['m2']['p2'].append(time_now)
                parts_log[str(id_counter)]['entered_queue_B_time'] = time_now

        ########################### EVENT 2 ##############################

        elif min_code == 2:

            machines_isdown['m1'] = True
            for p in machines_queue['m1']:
                parts_log[p]['moved_from_queue_AtoB_time'] = time_now
            machines_queue['m2']['p1'] += machines_queue['m1']
            machines_queue_time['m2']['p1'] += machines_queue_time['m1']
            machines_queue['m1'] = []
            machines_queue_time['m1'] = []
            dt = machine_A_downtime()
            total_downtime['m1'] += dt
            repair_time = time_now + dt
            FEL.append((4,repair_time))

        ########################### EVENT 3 ##############################

        elif min_code == 3: 

            machines_isdown['m2'] = True
            dt = machine_B_downtime()
            total_downtime['m2'] += dt
            repair_time = time_now + dt
            FEL.append((5,repair_time))

        ########################### EVENT 4 ##############################

        elif min_code == 4:

            machines_isdown['m1'] = False
            for p in machines_queue['m2']['p1']:
                parts_log[p]['moved_from_queue_BtoA_time'] = time_now
            machines_queue['m1'] += machines_queue['m2']['p1']
            machines_queue_time['m1'] += machines_queue_time['m2']['p1']
            machines_queue['m2']['p1'] = []
            machines_queue_time['m2']['p1'] = []
            next_down_time = time_now + machine_A_next_downtime()
            FEL.append((2,next_down_time))

        ########################### EVENT 5 ##############################
        
        elif min_code == 5:

            machines_isdown['m2'] = False
            next_down_time = time_now + machine_B_next_downtime()
            FEL.append((3,next_down_time))

        ########################### EVENT 6 ##############################

        elif min_code == 6:

            leaving_part = machines_status['m1'][0]
            parts_log[leaving_part]['left_machine_A_time'] = time_now
            
            if len(machines_queue['m1']) == 0:
                machines_status['m1'] = [] 

            else:

                machines_num_parts['m1'] += 1
                incoming_part = machines_queue['m1'].pop(0)
                machines_status['m1'] = [incoming_part]
                parts_log[incoming_part]['entered_machine_A_time'] = time_now
                out_time = machines_queue_time['m1'].pop(0)
                # parts_log[leaving_part]['working_time_in_machine_A'] = time_now - out_time
                q_time = time_now - out_time
                time_part1_in_system += q_time
                wt = machine_A_worktime()
                time_part1_in_system += wt
                machines_worktime['m1'] += wt
                finish_time = time_now + wt
                FEL.append((6,finish_time))

            if machines_status['m3'] == []: 

                machines_num_parts['m3']['p1'] += 1

                machines_status['m3'].append(leaving_part)
                parts_log[leaving_part]['entered_machine_C_time'] = time_now

                wt = machine_C_worktime()
                time_part1_in_system += wt
                machines_worktime['m3'] += wt
                finish_time = time_now + wt
                FEL.append((9,finish_time))
            else: 

                machines_queue['m3']['p1'].append(leaving_part)
                parts_log[leaving_part]['entered_queue_C_time'] = time_now
                machines_queue_time['m3']['p1'].append(time_now)

        ########################### EVENT 7 ##############################

        elif min_code == 7:

            leaving_part = machines_status['m2'][0]
            parts_log[leaving_part]['left_machine_B_time'] = time_now

            if (len(machines_queue['m2']['p1']) == 0) and (len(machines_queue['m2']['p2']) == 0): 
                machines_status['m2'] = []

            elif len(machines_queue['m2']['p1']) != 0: 

                machines_num_parts['m2']['p1'] += 1
                incoming_part = machines_queue['m2']['p1'].pop(0)
                machines_status['m2'] = [incoming_part]
                parts_log[incoming_part]['entered_machine_B_time'] = time_now
                out_time = machines_queue_time['m2']['p1'].pop(0)
                # parts_log[leaving_part]['working_time_in_machine_B'] = time_now - out_time
                finish_time = time_now + machine_B_worktime_for_part1()
                q_time = time_now - out_time
                time_part1_in_system += q_time
                wt = machine_B_worktime()
                time_part1_in_system += wt
                machines_worktime['m2'] += wt
                finish_time = time_now + wt
                FEL.append((7,finish_time))

            elif len(machines_queue['m2']['p2']) != 0: 

                machines_num_parts['m2']['p1'] += 1 
                incoming_part = machines_queue['m2']['p2'].pop(0)
                machines_status['m2'] = [incoming_part]
                parts_log[incoming_part]['entered_machine_B_time'] = time_now
                out_time = machines_queue_time['m2']['p2'].pop(0)
                # parts_log[leaving_part]['working_time_in_machine_B'] = time_now - out_time
                finish_time = time_now + machine_B_worktime_for_part1()
                q_time = time_now - out_time
                time_part2_in_system += q_time
                wt = machine_B_worktime()
                time_part2_in_system += wt
                machines_worktime['m2'] += wt
                finish_time = time_now + wt
                FEL.append((8,finish_time))
            
            if machines_status['m3'] == []: 

                machines_num_parts['m3']['p1'] += 1
                machines_status['m3'].append(leaving_part)
                parts_log[leaving_part]['entered_machine_C_time'] = time_now
                wt = machine_C_worktime()
                time_part1_in_system += wt
                machines_worktime['m3'] += wt
                finish_time = time_now + wt
                FEL.append((9,finish_time))
            else:
                
                machines_queue['m3']['p1'].append(leaving_part)
                parts_log[leaving_part]['entered_queue_C_time'] = time_now
                machines_queue_time['m3']['p1'].append(time_now)

        ########################### EVENT 8 ##############################

        elif min_code == 8:

            leaving_part = machines_status['m2'][0]
            parts_log[leaving_part]['left_machine_B_time'] = time_now

            if (len(machines_queue['m2']['p1']) == 0) and (len(machines_queue['m2']['p2']) == 0):
                machines_status['m2'] = []

            elif len(machines_queue['m2']['p1']) != 0: 

                machines_num_parts['m2']['p1'] += 1
                incoming_part = machines_queue['m2']['p1'].pop(0)
                machines_status['m2'] = [incoming_part]
                parts_log[incoming_part]['entered_machine_B_time'] = time_now
                out_time = machines_queue_time['m2']['p1'].pop(0)
                # parts_log[leaving_part]['working_time_in_machine_B'] = time_now - out_time
                q_time = time_now - out_time
                time_part1_in_system += q_time
                wt = machine_B_worktime()
                time_part1_in_system += wt
                machines_worktime['m2'] += wt
                finish_time = time_now + wt
                FEL.append((7,finish_time))

            elif len(machines_queue['m2']['p2']) != 0: 

                machines_num_parts['m2']['p2'] += 1
                incoming_part = machines_queue['m2']['p2'].pop(0)
                machines_status['m2'] = [incoming_part]
                parts_log[incoming_part]['entered_machine_B_time'] = time_now
                out_time = machines_queue_time['m2']['p2'].pop(0)
                # parts_log[leaving_part]['working_time_in_machine_B'] = time_now - out_time
                q_time = time_now - out_time
                time_part2_in_system += q_time
                wt = machine_B_worktime()
                time_part2_in_system += wt
                machines_worktime['m2'] += wt
                finish_time = time_now + wt
                FEL.append((8,finish_time))
            
            if machines_status['m3'] == []:

                machines_num_parts['m3']['p2'] += 1
                machines_status['m3'].append(leaving_part)
                parts_log[leaving_part]['entered_machine_C_time'] = time_now
                wt = machine_C_worktime()
                time_part2_in_system += wt
                machines_worktime['m3'] += wt
                finish_time = time_now + wt
                FEL.append((10,finish_time))

            else:
                
                machines_queue['m3']['p2'].append(leaving_part)
                parts_log[leaving_part]['entered_queue_C_time'] = time_now
                machines_queue_time['m3']['p2'].append(time_now)

        ########################### EVENT 9 ##############################

        elif min_code == 9:

            leaving_part = machines_status['m3'][0]
            parts_log[leaving_part]['left_machine_C_time'] = time_now

            if (len(machines_queue['m3']['p1']) == 0) and (len(machines_queue['m3']['p2']) == 0): # در صورت خالی بودن صف های ماشین ج
                machines_status['m3'] = []

            elif len(machines_queue['m3']['p1']) != 0:

                machines_num_parts['m3']['p1'] += 1
                incoming_part = machines_queue['m3']['p1'].pop(0)
                machines_status['m3'] = [incoming_part]
                parts_log[incoming_part]['entered_machine_C_time'] = time_now
                out_time = machines_queue_time['m3']['p1'].pop(0)
                q_time = time_now - out_time
                time_part1_in_system += q_time
                wt = machine_C_worktime()
                time_part1_in_system += wt
                machines_worktime['m3'] += wt
                finish_time = time_now + wt
                FEL.append((9,finish_time))

            elif len(machines_queue['m3']['p2']) != 0: 

                machines_num_parts['m3']['p2'] += 1
                incoming_part = machines_queue['m3']['p2'].pop(0)
                machines_status['m3'] = [incoming_part]
                parts_log[incoming_part]['entered_machine_C_time'] = time_now
                out_time = machines_queue_time['m3']['p2'].pop(0)
                q_time = time_now - out_time
                time_part2_in_system += q_time
                wt = machine_C_worktime()
                time_part2_in_system += wt
                machines_worktime['m3'] += wt
                finish_time = time_now + wt
                FEL.append((10,finish_time))

        ########################### EVENT 10 ##############################

        elif min_code == 10: 

            leaving_part = machines_status['m3'][0]
            parts_log[leaving_part]['left_machine_C_time'] = time_now

            if (len(machines_queue['m3']['p1']) == 0) and (len(machines_queue['m3']['p2']) == 0):
                machines_status['m3'] = []

            elif len(machines_queue['m3']['p1']) != 0: 

                machines_num_parts['m3']['p1'] += 1
                incoming_part = machines_queue['m3']['p1'].pop(0)
                machines_status['m3'] = [incoming_part]
                parts_log[incoming_part]['entered_machine_C_time'] = time_now
                out_time = machines_queue_time['m3']['p1'].pop(0)
                q_time = time_now - out_time
                time_part1_in_system += q_time
                wt = machine_C_worktime()
                time_part1_in_system += wt
                machines_worktime['m3'] += wt
                finish_time = time_now + wt
                FEL.append((9,finish_time))

            elif len(machines_queue['m3']['p2']) != 0: 

                machines_num_parts['m3']['p2'] += 1
                incoming_part = machines_queue['m3']['p2'].pop(0)
                machines_status['m3'] = [incoming_part]
                parts_log[incoming_part]['entered_machine_C_time'] = time_now
                out_time = machines_queue_time['m3']['p2'].pop(0)
                q_time = time_now - out_time
                time_part2_in_system += q_time
                wt = machine_C_worktime()
                time_part2_in_system += wt
                machines_worktime['m3'] += wt
                finish_time = time_now + wt
                FEL.append((10,finish_time))
        # print(FEL)

    print('Done!')

    # retuening results
    stats = (num_part1,
             num_part2,
             time_part1_in_system,
             time_part2_in_system,
             machines_worktime,
             total_downtime,
             machines_num_parts,
             queue_log,
             time_log,
             parts_log,
             FEL)
    return(stats)



def calculate_point_estimation(observations):
    return(sum(observations)/len(observations))

def calculate_interval_estimation(observations,t_stat=2.26216,rounding=3):
    n = len(observations)
    point_est = calculate_point_estimation(observations)
    sigma = (sum([(obs - (sum(observations)/n))**2 for obs in observations])/(n*(n-1)))**0.5
    if rounding==0:
        lower_bound = math.floor(point_est - (t_stat*sigma))
        lower_bound = max(0,lower_bound)
        upper_bound = math.ceil(point_est + (t_stat*sigma))
    else:
        lower_bound = round(point_est - (t_stat*sigma),rounding)
        lower_bound = max(0,lower_bound)
        upper_bound = round(point_est + (t_stat*sigma),rounding)
    return((lower_bound,upper_bound))


if __name__ == "__main__":
    ITERATIONS = 10 # number of times simulation is done

    # stat lists
    num_part1_list = []
    num_part2_list = []
    time_part1_list = []
    time_part2_list = []
    machine1_worktime = []
    machine2_worktime = []
    machine3_worktime = []
    machine1_downtime = []
    machine2_downtime = []
    machine3_downtime = []
    machine1_num_parts = []
    machine2_num_parts1 = []
    machine2_num_parts2 = []
    machine3_num_parts1 = []
    machine3_num_parts2 = []
    parts_log_list = []
    fel_list = []


    for iter in range(ITERATIONS):

        print('iter',iter,end=': ')
        stats = run_simulation(warmup_time=60, operation_time=540)

        # ثبت نتایج
        num_part1_list.append(stats[0])
        num_part2_list.append(stats[1])
        time_part1_list.append(stats[2])
        time_part2_list.append(stats[3])
        machine1_worktime.append(stats[4]['m1'])
        machine2_worktime.append(stats[4]['m2'])
        machine3_worktime.append(stats[4]['m3'])
        machine1_downtime.append(stats[5]['m1'])
        machine2_downtime.append(stats[5]['m2'])
        machine3_downtime.append(stats[5]['m3'])
        machine1_num_parts.append(stats[6]['m1'])
        machine2_num_parts1.append(stats[6]['m2']['p1'])
        machine2_num_parts2.append(stats[6]['m2']['p2'])
        machine3_num_parts1.append(stats[6]['m3']['p1'])
        machine3_num_parts2.append(stats[6]['m3']['p2'])

        queue_status = stats[7]
        time_log = stats[8]
        parts_log_list.append(stats[9])
        fel_list.append(stats[10])

    # calculating response time for rach type of parts
    response_time_part1 = [time_part1_list[i]/num_part1_list[i] for i in range(10)]
    response_time_part2 = [time_part2_list[i]/num_part2_list[i] for i in range(10)]


    print('**********************************\n')
    print('Simulation Result:\n\n')

    # calulating estimations
    result={'Number of parts #1':[round(calculate_point_estimation(num_part1_list)) , calculate_interval_estimation(num_part1_list,t_stat=2.26216,rounding=0)],
        'Number of parts #2':[round(calculate_point_estimation(num_part2_list)) , calculate_interval_estimation(num_part2_list,t_stat=2.26216,rounding=0)],
        'total process time of parts #1':[round(calculate_point_estimation(time_part1_list),2) , calculate_interval_estimation(time_part1_list)],
        'total process time of parts #2':[round(calculate_point_estimation(time_part2_list),2) , calculate_interval_estimation(time_part2_list)],
        'Response time of part #1':[round(calculate_point_estimation(response_time_part1),2) , calculate_interval_estimation(response_time_part1)],
        'Response time of part #2':[round(calculate_point_estimation(response_time_part2),2) , calculate_interval_estimation(response_time_part2)],
        'Total work time of machine A':[round(calculate_point_estimation(machine1_worktime),2) , calculate_interval_estimation(machine1_worktime)],
        'Total work time of machine B':[round(calculate_point_estimation(machine2_worktime),2) , calculate_interval_estimation(machine2_worktime)],
        'Total work time of machine C':[round(calculate_point_estimation(machine3_worktime),2) , calculate_interval_estimation(machine3_worktime)],
        'Total down time of machine A':[round(calculate_point_estimation(machine1_downtime),2) , calculate_interval_estimation(machine1_downtime)],
        'Total down time of machine B':[round(calculate_point_estimation(machine2_downtime),2) , calculate_interval_estimation(machine2_downtime)],
        'Total down time of machine C':[round(calculate_point_estimation(machine3_downtime),2) , calculate_interval_estimation(machine3_downtime)],
        'Number of parts #1 processed by machine A':[round(calculate_point_estimation(machine1_num_parts)) , calculate_interval_estimation(machine1_num_parts,t_stat=2.26216,rounding=0)],
        'Number of parts #1 processed by machine B':[round(calculate_point_estimation(machine2_num_parts1)) , calculate_interval_estimation(machine2_num_parts1,t_stat=2.26216,rounding=0)],
        'Number of parts #2 processed by machine B':[round(calculate_point_estimation(machine2_num_parts2)) , calculate_interval_estimation(machine2_num_parts2,t_stat=2.26216,rounding=0)],
        'Number of parts #1 processed by machine C':[round(calculate_point_estimation(machine3_num_parts1)) , calculate_interval_estimation(machine3_num_parts1,t_stat=2.26216,rounding=0)],
        'Number of parts #2 processed by machine C':[round(calculate_point_estimation(machine3_num_parts2)) , calculate_interval_estimation(machine3_num_parts2,t_stat=2.26216,rounding=0)],
        }


    result = pd.DataFrame(result,index=['point_estimation','interval_estimation(%95 conf)'])
    print(result.T)

    part_log = parts_log_list[-1]
    with open('trace_parts.txt','w') as f:
        for part_id in part_log.keys():
            log = part_log[part_id]
            f.write(f'>>> Part {part_id}: ')
            for key, val in log.items():
                f.write(f'{key}:{round(val,2)} | ')
            f.write('\n----------------------------------------------------\n')

    # plotting
    plot_queues(queue_status, time_log)