#!/usr/bin/env python
# -*-coding:Latin-1 -*
from PIL import Image,ImageChops
import numpy as np
import cv2
import math 
from numpy import asarray
import math
import csv 



def fonction(pt1,pt2,pt3,pt4,d):                       
	xa,ya=pt1
	xb,yb=pt2 
	xc,yc=pt3
	xd,yd=pt4
	key,i,n=0,0,0
	if xd!=xa:
		while(i<=n):		
			a=float(yd-ya)/(xd-xa)
			b=ya-(a*xa)
			if key==0:
				b1=d*math.sqrt((a**2)+1)+b
			else:
				b1=-d*math.sqrt((a**2)+1)+b

			a2=float(yb-ya)/(xb-xa)
			b2=ya-(a2*xa)
			a3=float(yc-yd)/(xc-xd)
			b3=yd-(a3*xd)
			xr=float(b2-b1)/(a-a2)
			yr=a2*xr+b2
			
			if xr<xa:
				key=1
				n=1
			else :
			   	key=0

			xr1=float(b3-b1)/(a-a3)
			yr1=a3*xr1+b3
			i=i+1
			return(int(xr),int(yr)),(int(xr1),int(yr1))
	else:
		return (int(xa+d),int(ya)),(int(xd+d),int(yd))



def FindContours(img,img1,res):
	diff=ImageChops.difference(img,img1)#diff est le résultat de soustraction de l'image original et le modele    
	print('diff=',diff)

	diff=diff.convert('L')                  # Convert the image to greyscale that we can applicate the edge and the other algorithms of the image pre-processing
	new_img=np.array(diff) 	              
	retval, bw = cv2.threshold(new_img,2,255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) #bw est le resultat du seuillage pour determiner les zones à pulvériser
	#threshold convert image from color to greyscale
	bw= cv2.GaussianBlur(bw, (7, 7), 0)   #appliquer un filtre pour éliminer le bruit (un filtre gaussien)
	contours1,hierarchy = cv2.findContours(bw, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)# determiner les contours des zones d'interet 
	cv2.drawContours(res,contours1,-1, (0,0,0),3)
	
	cv2.imshow('contour',res)
	cv2.imwrite("contour.jpg",res)
	
	return contours1,bw

def tri(c):
	(x,y), r = cv2.minEnclosingCircle(c)
	return(x)

def paint(contours,img,d):
	tab_res=[]

	mask=np.zeros(shape=[500,500], dtype=np.uint8)
	for j in range(len(contours)):
		rect = cv2.minAreaRect(contours[j]) #cv2.minAreaRect() for finding the minimum area rotated rectangle.
		#This takes as input a 2D point set and returns a Box2D structure which contains the following details – (center(x, y), (width, height), angle of rotation)
		box = cv2.boxPoints(rect)#limitation of the interest zone in a rectagle box
		box = np.int0(box)
		print("box=",box)

		cv2.drawContours(img,[box],-1,(60,255,128),2)
		print('box done')
		cv2.imshow('box',img)
		cv2.imwrite("box.jpg",img)
		
		for i in box:
			cv2.circle(img,(i[0],i[1]), 10, (128,255,0),2)
			print('circle done')
			cv2.imshow('circle',img)
			cv2.imwrite("circle.jpg",img)
		
		#box1=cv2.multiply(img, box)
		#cv2.imwrite("box",box1)

		bs= box[box[:,0].argsort()]#argshort returns the indices that would sort an array.
		if bs[0][1]>bs[1][1] :
			p3=bs[1]
			p1=bs[0]
		else :
			p3=bs[0]
			p1=bs[1]	
		if bs[2][1]>bs[3][1] :
			p4=bs[3]
			p2=bs[2]
		else:
			p4=bs[2]
			p2=bs[3]
		bs=np.array([p1,p2,p3,p4])
		pt1=(bs[0][0],bs[0][1])
		pt2=(bs[1][0],bs[1][1])
		pt3=(bs[2][0],bs[2][1])
		pt4=(bs[3][0],bs[3][1])
		wmax=math.sqrt((bs[0][0]-bs[1][0])**2+(bs[0][1]-bs[1][1])**2)#wmax est la largeur de rectangle englobant le contour
		nb=int(round(wmax/d,0))
		points=[]        
		for i in range(1,nb):
			p1,p2=fonction(pt3,pt4,pt2,pt1,d*i)		
			points.append(p1)
			points.append(p2)
			mask=cv2.line(img,p2,p1,(128,0,255),2)  
			#print(mask)
			cv2.imshow("mask",mask)
			cv2.imwrite("mask.jpg",mask)

		result=cv2.multiply(img, mask)
		cv2.imshow("multiply",result)
		cv2.imwrite("moltiply.jpg",result)

		
		cnt1,hierarchy = cv2.findContours(result, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
		cnt1=sorted(cnt1,key=tri)
		cv2.drawContours(img,cnt1,-1, (60,255,128),2)	
		cv2.imshow("multiply2",img)
		cv2.imwrite("multiply2.jpg",img)

		points=[]
		k=0
		for c in cnt1:
			c=sorted(c, key=lambda cont: cont[0][1])
			p1=c[len(c)-1][0][0],c[len(c)-1][0][1]
			p=c[0][0][0],c[0][0][1]
			if k%2==0:
				points.append(p)
				points.append(p1)
			else :
				points.append(p1)
				points.append(p)
			k+=1
	    
		tab_res=tab_res+points
	return tab_res
	
	
def init(im1,im2):	

	img1=cv2.imread(im2)
	img2=Image.open(im1)
	img3=Image.open(im2)
	return img1,img2,img3


def generate(v,path):
	with open(path, mode='w') as csv_file:
		fieldnames = ['x', 'y', 'z','rx','ry','rz']
		writer = csv.DictWriter(csv_file,fieldnames=fieldnames)
		writer.writeheader()
		for i in range(len(waypoints)):
			xi,yi=(waypoints[i])
			cx,cy=(0,0)        #(545,795) est l'origine du nouveau repere
			x1,y1=xi-cx,cy-yi
			Xr,Zr=x1*(2.54/96),y1*(2.54/96) # 2.54 cm = 1 inch et 96dpi (dots per inch) est la résolution de l'image actuelle
			X,Z=(0.06*Xr),(Zr*0.06)         # on a choisie une echelle de 6 /// X et Z sont en mètre
			X,Z=X+0.223,Z+0.26
			row={'x':X,'y':0.57,'z':Z,'rx':0,'ry':0,'rz':0}
			writer.writerow(row)



img_origin=cv2.imread("/home/sabrine/Bureau/pfe_ws/src/ur5_test/script/images/original.jpg")
gray = cv2.cvtColor(img_origin, cv2.COLOR_BGR2GRAY )
cv2.imshow("diff_img",gray)
cv2.imwrite("diff.jpg",gray)

print("*********************Done1-2*****************")
img_in,img,img1=init("/home/sabrine/Bureau/pfe_ws/src/ur5_test/script/images/original.jpg","/home/sabrine/Bureau/pfe_ws/src/ur5_test/script/images/modele.jpg")# init(image_originale(avant le modification ),image_modele)
difff=img-img_in
cv2.imshow("diff_img",difff)
cv2.imwrite("diff_img.jpg",difff)

contours,bw=FindContours(img1,img,img_in)
waypoints=paint(contours,bw,20) #paint(image_originale,Rayon_spay(dans ce cas = 20 px))
#cv2.imshow("result1",bw)
#cv2.imwrite("result1.png",bw)
print(waypoints)

cv2.drawContours(img_origin,contours,-1, (255,0,0),2)

cv2.imshow("pp",img_origin)
cv2.imwrite("pp.png",img_in)

print("done")
for i in range(len(waypoints)-1):
	img_in=cv2.line(img_origin,waypoints[i+1],waypoints[i],(0,0,0),1)

cv2.imshow("result2",img_origin)
cv2.imwrite("result2.png",img_in)


generate(waypoints,'WayPoints.csv')

cv2.waitKey(0)



