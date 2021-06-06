#!/usr/bin/env python

import sys
import copy
import rospy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
from math import pi
from std_msgs.msg import String
from moveit_commander.conversions import pose_to_list
from tf.transformations import *
import csv 
import roslib; roslib.load_manifest('visualization_marker_tutorials')
from visualization_msgs.msg import Marker
from visualization_msgs.msg import MarkerArray
from geometry_msgs.msg import Point
from std_msgs.msg import Duration

def DisplayPath(waypoints,frame_id,topic='visualization_marker_array'):
		publisher = rospy.Publisher(topic, MarkerArray, queue_size=100)
		markerArray = MarkerArray()
		count = 0
		MARKERS_MAX = 100
		marker = Marker()
		marker.points = []
		marker.header.frame_id = frame_id
		marker.type = marker.LINE_STRIP
		marker.action = marker.ADD
		marker.lifetime = rospy.Duration(50)
		marker.scale.x = 0.02
		marker.color.a = 1.0
		marker.color.r = 1.0
		marker.color.g = 0.0
		marker.color.b = 1.0
		for points in waypoints :
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

rospy.init_node('etstt',anonymous=True)
pose_goal= geometry_msgs.msg.PoseStamped().pose
with open('src/ur5_test/script/WayPoints.csv') as csv_file:
	next(csv_file)
	csv_reader = csv.reader(csv_file, delimiter=',')
	waypoints = []
	line_count = 0
	for row in csv_reader:
		q_rot = quaternion_from_euler(float(row[3]),float(row[4]),float(row[5]))

	pose_goal.orientation.x = q_rot[0]
	pose_goal.orientation.y = q_rot[1]
	pose_goal.orientation.z = q_rot[2]
	pose_goal.orientation.w = q_rot[3]
	pose_goal.position.x = float(row[0])-0.223
	pose_goal.position.y =-0.2
	pose_goal.position.z = float(row[2])
	waypoints.append(copy.deepcopy(pose_goal))
	line_count+=1
                    
csv_file.close()
DisplayPath(waypoints,"/world")
print("done")

