#!/usr/bin/env python

import traceback
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
import tf2_ros
import geometry_msgs.msg

from gazebo_msgs.srv import GetLinkState 


def cmdVelCB(data):
    return 

def process():
    global model_info, chassis_info
    loop_rate = rospy.Rate(10)

    br = tf2_ros.TransformBroadcaster()
    t = geometry_msgs.msg.TransformStamped()

    mouse_sub = rospy.Subscriber('/cmd_vel', Twist, cmdVelCB, queue_size=10)
    while not rospy.is_shutdown():
        chassis_info = model_info("robot::base_link","world")

        t.header.stamp = rospy.Time.now()
        t.header.frame_id = "map"
        t.child_frame_id = "base_link"
        t.transform.translation.x = chassis_info.link_state.pose.position.x
        t.transform.translation.y = chassis_info.link_state.pose.position.y
        t.transform.translation.z = chassis_info.link_state.pose.position.z
        t.transform.rotation.x = chassis_info.link_state.pose.orientation.x
        t.transform.rotation.y = chassis_info.link_state.pose.orientation.y
        t.transform.rotation.z = chassis_info.link_state.pose.orientation.z
        t.transform.rotation.w = chassis_info.link_state.pose.orientation.w

        br.sendTransform(t)
        loop_rate.sleep()

if __name__ == '__main__':
  rospy.init_node('pub_robot_TF', anonymous=False)
  model_info= rospy.ServiceProxy('/gazebo/get_link_state', GetLinkState)  
  try:
    process()
  except Exception as ex:
    print(traceback.print_exc())