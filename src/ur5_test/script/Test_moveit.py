#!/usr/bin/env python
import sys
import moveit_commander
import rospy
from UR5 import UR5_ARM

	
moveit_commander.roscpp_initialize(sys.argv)
rospy.init_node('UR5_ControlNode',anonymous=True)
ARM=UR5_ARM("arm")
ARM.GoHome()
rospy.Rate(0.5)
ARM.ARMInfo()
plan,fraction,waypoints=ARM.CartesianPath()
ARM.DisplayPath(waypoints)
if fraction>=99 :
	ARM.execute_plan(plan)
else :
	print("Cannot execute 100 % of the trajectory !!! Only {} can be executed  ".format(fraction))
ARM.GoHome()
ARM.GetTCPPos()
moveit_commander.os._exit(0)
