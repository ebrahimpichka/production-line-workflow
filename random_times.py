import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import random

random.seed(30)
np.random.seed(30)

# functions to generate random time

def part_1_arrival_time(mu=20,std=3): # part 1 enter time
    return(abs(np.random.normal(loc=mu, scale=std)))

def part_2_arrival_time(mu=16,std=10): # part 2 enter time
    return(abs(np.random.normal(loc=mu, scale=std)))

def machine_A_worktime(mu=15,std=9): # worktime of machine A
    return(abs(np.random.normal(loc=mu, scale=std)))

def machine_B_worktime(mu=18,std=2): # worktime of machine B (on part 1)
    return(abs(np.random.normal(loc=mu, scale=std)))

def machine_B_worktime_for_part1(mu=40,std=9): # worktime of machine B (on part 2)
    return(abs(np.random.normal(loc=mu, scale=std)))

def machine_C_worktime(mu=10,std=4): # worktime of machine C
    return(abs(np.random.normal(loc=mu, scale=std)))

def machine_A_next_downtime(mu=450,std=50): # next downtime of machine A
    return(abs(np.random.normal(loc=mu, scale=std)))

def machine_B_next_downtime(mu=210,std=10): # next downtime of machine B
    return(abs(np.random.normal(loc=mu, scale=std)))

def machine_A_downtime(mu=25,std=4): # downtime of machine A
    return(abs(np.random.normal(loc=mu, scale=std)))

def machine_B_downtime(mu=20,std=4): # downtime of machine B
    return(abs(np.random.normal(loc=mu, scale=std)))