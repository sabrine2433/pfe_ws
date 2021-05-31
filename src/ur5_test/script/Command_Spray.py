#!/usr/bin/env python  
import rospy
import tf
import geometry_msgs.msg
import csv
from std_msgs.msg import Bool

if __name__ == '__main__':
        rospy.init_node('generate_Spray_gun_command',anonymous=True)  
        listener = tf.TransformListener()#help make the task of receiving transforms ( get access to frame transformations)
        #rospy.wait_for_service('spawn')
        rospy.spin()#keep the program running until killing manually
        i=0
        Gun=False
        waypoints=[]
        rate = rospy.Rate(100.0)
        now = rospy.Time.now()
        with open('WayPoints.csv') as csv_file:
                next(csv_file)
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                        x_g = float(row[0])
                        y_g = float(row[1])
                        z_g= float(row[2])
                        a=x_g,y_g,z_g
                        waypoints.append(a)
                        print(waypoints)



                 
        pub = rospy.Publisher('/Command_SPRAY',Bool, queue_size=10)
        while  i < len(waypoints):
                print("*************Transform***********")
                listener.waitForTransform('/world','/tool0',rospy.Time(), rospy.Duration(2.0))
                (trans, rot) = listener.lookupTransform('/world', '/tool0', rospy.Time(0))
                x,y,z=trans[0],trans[1],trans[2]
                xi,yi,zi=waypoints[i]
                if (abs(xi-x)<0.005)and (abs(yi-y)<0.005)and (abs(zi-z)<0.005):
                        if i%2==0 :
                                print("ON")
                                Gun=True
                        else :
                                print("OFF")
                                Gun=False
			
                        i+=1
                pub.publish(Gun)
                rate.sleep()






