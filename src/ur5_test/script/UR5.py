#!/usr/bin/env python
import sys
import copy
import rospy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
from math import pi
from std_msgs.msg import String
#from moveit_commander.conversions import pose_to_list
from tf.transformations import *
import csv 
import roslib; roslib.load_manifest('visualization_marker_tutorials')
from visualization_msgs.msg import Marker
from visualization_msgs.msg import MarkerArray
from geometry_msgs.msg import Point
from std_msgs.msg import Duration

class UR5_ARM():
	
	robot = moveit_commander.RobotCommander()
	scene = moveit_commander.PlanningSceneInterface()

	def __init__(self,group_name):
		self.group = moveit_commander.MoveGroupCommander(group_name)
		self.JointPositions = self.group.get_current_joint_values()
		self.group.set_planning_time(15)
		self.group.set_num_planning_attempts(10)
		self.group.allow_replanning(True)
		self.eef_link=self.group.get_end_effector_link()
                
	def MoveJoints(self,JointPositions=[]):  
		self.group.set_start_state(self.robot.get_current_state())
		if len(JointPositions)==0:
			return False
		else:
			self.group.go(JointPositions, wait=True)
			self.group.stop()
			return True
	
	def ARMInfo(self):
		planning_frame = self.group.get_planning_frame()
		print ("============ Reference frame: %s" % planning_frame)

		#Print the name of the end-effector link for this group:
		eef = self.group.get_end_effector_link()
		print ("============ End effector: %s" % eef,"*************")
		print ("============RPY : {} " .format(self.group.get_current_rpy(eef)),"**************")

		# Get a list of all the groups in the robot:
		group_names = self.robot.get_group_names()
		print ("============ Robot Groups:",self.robot.get_group_names(),"*****************")

		# Sometimes for debugging it is useful to print the entire state of the
		# robot:
		print ("**************Robot state***************")
		print (self.robot.get_current_state())
		print ("")
	
	def GetTCPPos(self):
		print ("============ Printing End Effector POS :")
		print (self.group.get_current_pose().pose)
	
	def go_to_pose_goal(self,Pos=[]):
		self.group.set_start_state(self.robot.get_current_state())
		a=self.group.get_current_rpy(self.eef_link)
		if len(Pos)== 0:
			return 0
		else:
			pose_goal = geometry_msgs.msg.Pose()

		q_orig = quaternion_from_euler(a[0],a[1],a[2])
		q_rot = quaternion_from_euler(Pos[3],Pos[4],Pos[5])
		q_new = quaternion_multiply(q_rot, q_orig)
		pose_goal.orientation.x = q_new[0]
		pose_goal.orientation.y = q_new[1]
		pose_goal.orientation.z = q_new[2]
		pose_goal.orientation.w = q_new[3]

		pose_goal.position.x = Pos[0]
		pose_goal.position.y = Pos[1]
		pose_goal.position.z = Pos[2]
		self.group.set_pose_target(pose_goal)

		## Now, we call the planner to compute the plan and execute it.
		plan = self.group.go(wait=True)
		# Calling `stop()` ensures that there is no residual movement
		self.group.stop()
		self.group.clear_pose_targets()


	def CartesianPath(self):
		pose_goal= geometry_msgs.msg.PoseStamped().pose
		a = self.group.get_current_rpy(self.eef_link)

		with open('WayPoints.csv') as csv_file:
			next(csv_file)
			csv_reader = csv.reader(csv_file, delimiter=',')
			waypoints = []
			line_count = 0
			for row in csv_reader:
				q_orig = quaternion_from_euler(a[0],a[1],a[2])
				q_rot = quaternion_from_euler(float(row[3]),float(row[4]),float(row[5]))
				q_new = quaternion_multiply(q_rot, q_orig)

			pose_goal.orientation.x = q_new[0]
			pose_goal.orientation.y = q_new[1]
			pose_goal.orientation.z = q_new[2]
			pose_goal.orientation.w = q_new[3]
			pose_goal.position.x = float(row[0])
			pose_goal.position.y = float(row[1])
			pose_goal.position.z = float(row[2])
			waypoints.append(copy.deepcopy(pose_goal))
			line_count+=1
			csv_file.close()

			#Compute a Cartesian path that follows specified waypoints with a step size of at most eef_step meters 
			#between end effector configurations of consecutive points in the result trajectory. 
			#Return a value that is between 0.0 and 1.0 indicating the fraction of the path achieved
			#as described by the waypoints. Return -1.0 in case of error.
			(plan, fraction) = self.group.compute_cartesian_path(
                                      waypoints,   # waypoints to follow
                                       0.05,        # eef_step
                                       50.0)
			print("Plannig Path")
			return plan,fraction*100,waypoints
		
		
	def GoHome(self,HomePos=[1.5,-0.8,0.8,0,1.6,0]):
		self.MoveJoints(HomePos)
		print("The robot arm is in home position")
		

	
	def DisplayPath(self,waypoints,topic='visualization_marker_array'):
		publisher = rospy.Publisher(topic, MarkerArray, queue_size=100)
		markerArray = MarkerArray()
		count = 0
		MARKERS_MAX = 100
		marker = Marker()
		marker.points = []
		marker.header.frame_id = "/world"
		marker.type = marker.LINE_STRIP
		marker.action = marker.ADD
		marker.lifetime = rospy.Duration(50)
		marker.scale.x = 0.01
		marker.color.a = 1.0
		marker.color.r = 0.0
		marker.color.g = 1.0
		marker.color.b = 0.0
		for points in waypoints:
		   marker.pose.orientation.x = 0
		   marker.pose.orientation.y = 0
		   marker.pose.orientation.z = 0
		   marker.pose.orientation.w = 0
		   line_point = Point()
		   line_point.x =points.position.x
		   line_point.y = points.position.y
		   line_point.z = points.position.z
		   marker.points.append(line_point)

		   # We add the new marker to the MarkerArray, removing the oldest
		   # marker from it when necessary
		   if(count > MARKERS_MAX):
		       markerArray.markers.pop(0)

		   markerArray.markers.append(marker)

		   # Renumber the marker IDs
		   id = 0
		   for m in markerArray.markers:
		       m.id = id
		       id += 1
		   count += 1
		   publisher.publish(markerArray)
		   rospy.sleep(0.3)

	
	def execute_plan(self, plan):
		print("Execution")
		self.group.execute(plan,wait=True)