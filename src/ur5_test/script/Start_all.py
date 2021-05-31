#!/usr/bin/env python
import roslaunch
import rospy
import subprocess
roscore = subprocess.Popen('roscore') #start the master 
rospy.sleep(1)  # wait a bit to be sure the roscore is really launched
rospy.init_node('Start_painting_process', anonymous=True)#initialise the node 
uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)#generate or get a unique id 
roslaunch.configure_logging(uuid)# Acquisition of logging set
launch = roslaunch.parent.ROSLaunchParent(uuid, ["/home/sabrine/Bureau/pfe_ws/src/ur_gazebo/launch/ur5.launch"])
launch.start()# Launch of Roslaunch
rospy.loginfo("gazebo started !!")
rospy.sleep(10)#wait 10s before launching the planning
launch = roslaunch.parent.ROSLaunchParent(uuid, ["/home/sabrine/Bureau/pfe_ws/src/ur5_moveit_config/launch/ur5_moveit_planning_execution.launch"])
launch.start()

#shutdown master after half hour
rospy.sleep(1800)
launch.shutdown()
