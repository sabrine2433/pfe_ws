#include <ros/ros.h>
#include <tf/transform_datatypes.h>
#include <tf/transform_listener.h>
#include <tf/transform_broadcaster.h>
#include <sensor_msgs/PointCloud2.h> //hydro
#include <typeinfo>
// PCL specific includes
#include <pcl_conversions/pcl_conversions.h> //hydro
#include "pcl_ros/transforms.h"
#include <sensor_msgs/PointCloud.h>
#include <sensor_msgs/PointCloud2.h>
#include <sensor_msgs/point_cloud_conversion.h>
#include <pcl/filters/voxel_grid.h>
#include <pcl/filters/passthrough.h>
#include <pcl/sample_consensus/method_types.h>
#include <pcl/sample_consensus/model_types.h>
#include <pcl/segmentation/sac_segmentation.h>
#include <pcl/filters/extract_indices.h>
#include <pcl/segmentation/extract_clusters.h>
#include <pcl/filters/crop_box.h>
#include <pcl/filters/statistical_outlier_removal.h>
#include <tf_conversions/tf_eigen.h>
#include <pcl/segmentation/extract_polygonal_prism_data.h>
/// PCL convex hull
#include <pcl/features/boundary.h>
#include <pcl/features/normal_3d.h>
std::vector<geometry_msgs::Point32> Point_cloud;


int main(int argc, char *argv[])
{
  /*
   * INITIALIZE ROS NODE
   */
  ros::init(argc, argv, "perception_node");
  ros::NodeHandle nh;
  ros::NodeHandle priv_nh_("~");

  /*
   * SET UP PARAMETERS (COULD BE INPUT FROM LAUNCH FILE/TERMINAL)
   */
  std::string cloud_topic, world_frame, camera_frame;
  world_frame="world";
  camera_frame="kinect_link";
  cloud_topic="/3Dcamera/depth/points";

  /*
   * SETUP PUBLISHERS
   */
  ros::Publisher object_pub, cluster_pub, pose_pub,points_pub;
  object_pub = nh.advertise<sensor_msgs::PointCloud2>("object_cluster", 1);
  cluster_pub = nh.advertise<sensor_msgs::PointCloud2>("primary_cluster", 1);
  points_pub =nh.advertise<sensor_msgs::PointCloud2>("points_pcl", 1);
 while (ros::ok())
 {
  /*
   * LISTEN FOR POINTCLOUD
   */
  std::string topic = nh.resolveName(cloud_topic);
  ROS_INFO_STREAM("Cloud service called; waiting for a PointCloud2 on topic "<< topic);
  sensor_msgs::PointCloud2::ConstPtr recent_cloud =
               ros::topic::waitForMessage<sensor_msgs::PointCloud2>(topic, nh);

  /*
   * TRANSFORM POINTCLOUD FROM CAMERA FRAME TO WORLD FRAME
   */
  tf::TransformListener listener;
  tf::StampedTransform stransform;
  try
  {
    listener.waitForTransform(world_frame, recent_cloud->header.frame_id,  ros::Time::now(), ros::Duration(6.0));
    listener.lookupTransform(world_frame, recent_cloud->header.frame_id,  ros::Time(0), stransform);
  }
  catch (tf::TransformException ex)
  {
    ROS_ERROR("%s",ex.what());
  }
  sensor_msgs::PointCloud2 transformed_cloud;
//  sensor_msgs::PointCloud2::ConstPtr recent_cloud =
//               ros::topic::waitForMessage<sensor_msgs::PointCloud2>(topic, nh);
  pcl_ros::transformPointCloud(world_frame, stransform, *recent_cloud, transformed_cloud);

  /*
   * CONVERT POINTCLOUD ROS->PCL
   */
  pcl::PointCloud<pcl::PointXYZ> cloud;
  pcl::fromROSMsg (transformed_cloud, cloud);

pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_ptr (new pcl::PointCloud<pcl::PointXYZ> (cloud));
/*pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_voxel_filtered (new pcl::PointCloud<pcl::PointXYZ> ());
pcl::VoxelGrid<pcl::PointXYZ> voxel_filter;
voxel_filter.setInputCloud (cloud_ptr);
voxel_filter.setLeafSize (float(0.05), float(0.05), float(0.05));
voxel_filter.filter (*cloud_voxel_filtered);
// filter x
pcl::PointCloud<pcl::PointXYZ> xf_cloud;
pcl::PassThrough<pcl::PointXYZ> pass_x;
pass_x.setInputCloud(cloud_voxel_filtered);
pass_x.setFilterFieldName("x");
pass_x.setFilterLimits(-0.3,0.3);
pass_x.filter(xf_cloud);
// filter y
pcl::PointCloud<pcl::PointXYZ>::Ptr xf_cloud_ptr(new pcl::PointCloud<pcl::PointXYZ>(xf_cloud));
pcl::PointCloud<pcl::PointXYZ> yf_cloud;
pcl::PassThrough<pcl::PointXYZ> pass_y;
pass_y.setInputCloud(xf_cloud_ptr);
pass_y.setFilterFieldName("y");
pass_y.setFilterLimits(0.5,1.5);
pass_y.filter(yf_cloud);
pcl::PointCloud<pcl::PointXYZ>::Ptr yf_cloud_ptr(new pcl::PointCloud<pcl::PointXYZ>(yf_cloud));
/*
   * CONVERT POINTCLOUD PCL->ROS
   * PUBLISH CLOUD
   * Fill Code: UPDATE AS NECESSARY
   * ========================================*/
/*pcl::PointCloud<pcl::Normal>::Ptr normals (new pcl::PointCloud<pcl::Normal>); 
pcl::NormalEstimation<pcl::PointXYZ, pcl::Normal> ne; 
ne.setInputCloud (yf_cloud_ptr); 
pcl::search::KdTree<pcl::PointXYZ>::Ptr tree (new pcl::search::KdTree<pcl::PointXYZ> ()); 
ne.setSearchMethod (tree); 
ne.setRadiusSearch (0.5); 
ne.compute (*normals); 
pcl::PointCloud<pcl::Boundary> boundaries; 
pcl::BoundaryEstimation<pcl::PointXYZ, pcl::Normal, pcl::Boundary> est; 
est.setInputCloud (yf_cloud_ptr); 
est.setInputNormals (normals);
est.setRadiusSearch (0.2); 
est.setSearchMethod (pcl::search::KdTree<pcl::PointXYZ>::Ptr (new pcl::search::KdTree<pcl::PointXYZ>)); 
est.compute (boundaries); 
ROS_INFO("Boundary Size: %d",yf_cloud.points.size()); */
  sensor_msgs::PointCloud2::Ptr pc2_cloud (new sensor_msgs::PointCloud2);
  pcl::toROSMsg(cloud, *pc2_cloud);
  pc2_cloud->header.frame_id=world_frame;
  pc2_cloud->header.stamp=ros::Time::now();
  object_pub.publish(pc2_cloud);
  std::cout<<cloud.at(394,35);
  }
   
  
  return 0;
}

