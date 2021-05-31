#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Point32

def callback(data):
    p=[]
    p.append(data)
    

rospy.init_node('listener', anonymous=True)
rospy.Subscriber("/points_pcl", Point32, callback)
rospy.spin()

