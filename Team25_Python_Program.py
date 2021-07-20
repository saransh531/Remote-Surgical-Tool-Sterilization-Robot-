

import sys
sys.path.append('../')

from Common_Libraries.p2_lib import *

import os
from Common_Libraries.repeat_timer_lib import repeating_timer

def update_sim ():
    try:
        arm.ping()
    except Exception as error_update_sim:
        print (error_update_sim)

arm = q_arm()


update_thread = repeating_timer(2, update_sim)

import random

## These are a couple global variables that we defined to simplify the code.

container_one = [-0.5850, 0.2264, 0.4100]
container_two = [-0.0001,-0.6287,0.47]
container_three = [-0.0001,0.6227,0.490]
container_four = [-0.3786, 0.1378, 0.3498]
container_five = [0.007, -0.4051, 0.373]
container_six = [0.0021, 0.4039, 0.3066]
pickup_threshold = 0.95
threshold = 0
gripper_threshold = 0.4
bin_threshold = 0.6
drawer_threshold = 0.2

## The function below lists the xyz-coordinates of the bin locations for each
## of the containers.
## It accepts one argument that determines the ID of the container.
## Depending on the ID (colour, size), different coordinates will be given.
## It then returns these coordinates.
    
def bin_location(container_ID):  
    if container_ID == 1:
        bin_xyz = container_one
    elif container_ID == 2:
        bin_xyz = container_two
    elif container_ID == 3:
        bin_xyz = container_three
    elif container_ID == 4:
        bin_xyz = container_four
    elif container_ID == 5:
        bin_xyz = container_five
    elif container_ID == 6:
        bin_xyz = container_six
    return bin_xyz


## This function will move the q-arm to the Home location, the bin location,
## or the container pickup location depending on the readings from the
## muscle sensors.
## It accepts an argument from the previous function.
## When the left arm is greater than the pickup threshold (0.95) and the
## right arm equals the threshold variable (0.0), the q-arm moves to the
## pickup location.
## When the right arm is greater than the bin threshold (0.4) and the left
## arm equals the threshold variable, the q-arm moves to the bin location.
## When both the left and right muscle sensors are greater than the pickup
## threshold, the q-arm moves to the home location.

def move_arm(bin_xyz):
    location = 0
    while location == 0:
        time.sleep(0.25)
        arm.emg_left()
        arm.emg_right()
        if arm.emg_left() > pickup_threshold and arm.emg_right() == threshold:
            location = arm.move_arm(0.5055,0.0,0.0227)
        elif arm.emg_right() > bin_threshold and arm.emg_left() == threshold:
            location = arm.move_arm(bin_xyz[0],bin_xyz[1],bin_xyz[2])
        elif arm.emg_right() > pickup_threshold and arm.emg_left() > pickup_threshold:
            location = arm.move_arm(0.4064,0.0,0.4826)
    return location

        
## The function below accepts no argmuents. 
## When the right arm is greater than the gripper threshold (0.2) and the
## left arm equals the threshold variable, the gripper closes.
## When the left arm is greater than the gripper threshold and the right
## arm equals the threshold variable, the gripper opens.

def gripper():
    gripper = 0
    while gripper == 0:
        time.sleep(0.5)
        arm.emg_left()
        arm.emg_right()
        if arm.emg_right() > gripper_threshold and arm.emg_left() == threshold:
            gripper = arm.control_gripper(40)
        elif arm.emg_left() > gripper_threshold and arm.emg_right() == threshold:
            gripper = arm.control_gripper(-40)
    return gripper


## The below function accepts one argument from the first function.
## When the left arm is greater than the drawer threshold (0.6) and the
## right arm equals the threshold variable, the drawer will open according
## to its container ID which was given in the argument.
## When the right arm is greater than the drawer threshold and the left
## arm equals the threshold variable, the drawer will close according
## to its container ID.

def drawers(dropoff_xyz):
    drawer = 0
    while drawer == 0:
        time.sleep(0.25)
        arm.emg_left()
        arm.emg_right()
        if dropoff_xyz == container_four and arm.emg_left() > drawer_threshold and arm.emg_right() == threshold:
            drawer = arm.open_red_autoclave(True)  
        elif dropoff_xyz == container_five and arm.emg_left() > drawer_threshold and arm.emg_right() == threshold:
            drawer = arm.open_green_autoclave(True)  
        elif dropoff_xyz == container_six and arm.emg_left() > drawer_threshold and arm.emg_right() == threshold:
            drawer = arm.open_blue_autoclave(True)
        elif dropoff_xyz == container_four and arm.emg_right() > drawer_threshold and arm.emg_left() == threshold:
            drawer = arm.open_red_autoclave(False)   
        elif dropoff_xyz == container_five and arm.emg_right() > drawer_threshold and arm.emg_left() == threshold:
            drawer = arm.open_green_autoclave(False)   
        elif dropoff_xyz == container_six and arm.emg_right() > drawer_threshold and arm.emg_left() == threshold:
            drawer = arm.open_blue_autoclave(False)
    return drawer            


## This is the main function in which all the functions come together
## to run through the entire workflow.
## The process will repeat six times until all containers are in their
## respective postions. The spawning of the containers are randomized.
## The container ID and coordinates of the corresponding bin have are
## printed for user benefit and knowledge.

def main():
    arm.home()
    time.sleep(1)
    container_ID = []
    while len(container_ID) < 6:
        ID = random.randint(1,6)
        if ID not in container_ID:
            container_ID.append(ID)
            print(ID)
            time.sleep(1)
            arm.spawn_cages(ID)
            dropoff_xyz = bin_location(ID)
            print(dropoff_xyz)
            time.sleep(1)
            while True:
                if arm.emg_left() > pickup_threshold and arm.emg_right() == threshold:
                    move_arm(dropoff_xyz)
                    time.sleep(1)
                    break
            while True:
                if arm.emg_right() > gripper_threshold and arm.emg_left() == threshold:
                    gripper()
                    time.sleep(1)
                    break
            while True:
                if arm.emg_right() > bin_threshold and arm.emg_left() == threshold:
                    move_arm(dropoff_xyz)
                    time.sleep(1)
                    break
            if ID == 1 or ID == 2 or ID == 3:
                time.sleep(1)
                while True:
                    if arm.emg_left() > gripper_threshold and arm.emg_right() == threshold:
                        gripper()
                        time.sleep(1)
                        break                    
                while True:
                    if arm.emg_right() > pickup_threshold and arm.emg_left() > pickup_threshold:
                        move_arm(dropoff_xyz)
                        time.sleep(1)
                        break
            elif ID == 4 or ID == 5 or ID == 6:
                time.sleep(1)
                while True:
                    if arm.emg_left() > drawer_threshold and arm.emg_right() == threshold:
                        drawers(dropoff_xyz)
                        time.sleep(1.5)
                        break
                while True:
                    if arm.emg_left() > gripper_threshold and arm.emg_right() == threshold:
                        gripper()
                        time.sleep(1)
                        break
                while True:
                    if arm.emg_right() > drawer_threshold and arm.emg_left() == threshold:
                        drawers(dropoff_xyz)
                        time.sleep(1)
                        break
                while True:
                    if arm.emg_right() > pickup_threshold and arm.emg_left() > pickup_threshold:
                        move_arm(dropoff_xyz)
                        time.sleep(1)
                        break


