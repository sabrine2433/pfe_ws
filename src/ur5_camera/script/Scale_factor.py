#!/usr/bin/env python
# -*-coding:Latin-1 -*
from sensor_msgs.msg import CameraInfo, Image
from PIL import ImageChops
from PIL import Image as IMAGE
from cv_bridge import CvBridge, CvBridgeError
import numpy as np
import cv2
import rospy
import imutils

def start_node():
    rospy.init_node('image_pub')
    rospy.loginfo('image_pub node started')
    rospy.Subscriber("/3Dcamera/color/image_raw", Image, process_image)
    rospy.spin()

def process_image(msg):
         b=0
	 bridge = CvBridge()
	 try:
		
        	 cv_image = bridge.imgmsg_to_cv2(msg, "bgr8")
         except CvBridgeError, e:
         	 rospy.logerr("CvBridge Error: {0}".format(e))

         cv2.imwrite("actual_image.jpg",cv_image)
         showImage('Camera_frame',cv_image)
         image1=IMAGE.open("actual_image.jpg")
	 image2=IMAGE.open("ref.jpg")
         ap=cv2.imread("actual_image.jpg")
	 FindContours(image1,image2,ap)

def showImage(frame_name,img):
    
    cv2.imshow(frame_name, img)
    cv2.waitKey(1)
def Key_func(a):
        xa,ya=a
	return xa
def tri(t,Max):
          sub_t=[]
          for i in range(len(t)):
	  	cx,cy=t[i][0][0],t[i][0][1]
                if cy in range(Max,3*Max):	
			sub_t.append((cx,cy))
          print(sub_t)
          sub_t=sorted(sub_t,key=Key_func)              
	  return sub_t[0],sub_t[-1]
def FindContours(img,img1,res):
        img=img.convert('L')
	diff=ImageChops.difference(img,img1)#diff est le résultat de soustraction de l'image original et le modele    
	diff=diff.convert('L')                  # convertir diff en image en niveau de gris(gray scale)
	
	new_img=np.array(diff)   
	              
	retval, bw = cv2.threshold(new_img,2,255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) #bw est le resultat du seuillage pour determiner les zones pulvériser
	bw= cv2.GaussianBlur(bw, (7, 7), 0)   #appliquer un filtre pour éliminer le bruit (un filtre gaussien)
	imgEdge,contours1,hierarchy = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)# determiner les contours des zones d'interet 
        cnt = max(contours1, key=cv2.contourArea)
        leftmost = tuple(cnt[cnt[:,:,0].argmin()][0])
	rightmost = tuple(cnt[cnt[:,:,0].argmax()][0])
	topmost = tuple(cnt[cnt[:,:,1].argmin()][0])
	bottommost = tuple(cnt[cnt[:,:,1].argmax()][0])
   	peri = cv2.arcLength(cnt, True)
	approx = cv2.approxPolyDP(cnt, 0.001 * peri, True)
        cv2.circle(res,leftmost, 8, (0, 0, 255), -1)
	pt1,pt2=tri(approx,topmost[1])
        print(pt2)
        cv2.circle(res,pt1, 8, (0, 0, 255), -1)
        cv2.circle(res,pt2, 8, (0, 0, 255), -1)
        cv2.circle(res,leftmost, 8, (0, 0, 255), -1)
	cv2.circle(res,rightmost, 8, (0, 0, 255), -1)               
        showImage("rr",res)
      
        return contours1,bw
	

if __name__ == '__main__':
        ap=cv2.imread("actual_image.jpg")
        start_node()

