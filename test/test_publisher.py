#!/usr/bin/env python
import rospy

from std_msgs.msg import Float64

import sys, select, termios, tty
from geometry_msgs.msg import Twist


msg = """
Control Your Toy!
---------------------------
Moving around:
   u    i    o
   j    k    l
   m    ,    .
q/z : increase/decrease max speeds by 10%
w/x : increase/decrease only linear speed by 10%
e/c : increase/decrease only angular speed by 10%
space key, k : force stop
anything else : stop smoothly
CTRL-C to quit
"""

moveBindings = {
        'i':(1,0),
        'o':(1,-1),
        'j':(0,1),
        'l':(0,-1),
        'u':(1,1),
        ',':(-1,0),
        '.':(-1,1),
        'm':(-1,-1),
           }

speedBindings={
        'q':(1.1,1.1),
        'z':(.9,.9),
        'w':(1.1,1),
        'x':(.9,1),
        'e':(1,1.1),
        'c':(1,.9),
          }

def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

speed = 10
speedy = 10
turn = 10

def vels(speed,turn):
    return "currently:\tspeed %s\tturn %s " % (speed,turn)

if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin)
    
    rospy.init_node('car_teleop')
    
    velocity_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

    x = 0
    y = 0
    th = 0
    status = 0
    count = 0
    acc = 0.1
    target_speed = 0
    target_turn = 0
    control_speed = 0
    control_speedy = 0
    control_turn = 0
    rate = rospy.Rate(20) 
    try:
        print(msg)
        print(vels(speed,turn))
        vel_msg = Twist()
        while not rospy.is_shutdown():
            key = getKey()
            vel_msg.linear.x = 0
            vel_msg.linear.y = 0
            vel_msg.linear.z = 0
            vel_msg.angular.x = 0
            vel_msg.angular.y = 0
            vel_msg.angular.z = 0
            if key in moveBindings.keys():
                if(key == 'i' or key == ','):
                    x = moveBindings[key][0]
                elif(key == 'j' or key=='l'):
                    y = moveBindings[key][1]
                elif(key == 'u' or key=='o'):
                    th = moveBindings[key][1]

                count = 0
            elif key in speedBindings.keys():
                #speed = speed * speedBindings[key][0]
                #speedy = speedy * speedBindings[key][0]
                #turn = turn * speedBindings[key][1]
                count = 0

                print(vels(speed,turn))
                if (status == 14):
                    print(msg)
                status = (status + 1) % 15
            elif key == ' ' or key == 'k' :
                x = 0
                y = 0
                th = 0
                control_speed = 0
                control_turn = 0
            else:
                count = count + 1
                if count > 4:
                    x = 0
                    y = 0
                    th = 0
                if (key == '\x03'):
                    break

            target_speed = speed * x
            target_speedy = speedy * y
            target_turn = turn * th

            if target_speed > control_speed:
                control_speed = min( target_speed, control_speed + 10)
            elif target_speed < control_speed:
                control_speed = max( target_speed, control_speed - 10 )
            else:
                control_speed = target_speed

            if target_speedy > control_speedy:
                control_speedy = min( target_speedy, control_speedy + 10)
            elif target_speedy < control_speedy:
                control_speedy = max( target_speedy, control_speedy - 10 )
            else:
                control_speedy = target_speedy

            if target_turn > control_turn:
                control_turn = min( target_turn, control_turn + 10 )
            elif target_turn < control_turn:
                control_turn = max( target_turn, control_turn - 10 )
            else:
                control_turn = target_turn

            vel_msg.linear.x = control_speed
            vel_msg.linear.y = control_speedy
            vel_msg.angular.z = control_turn

            print("speed: ",control_speed, "speed: ",control_speedy, "speed: ",control_turn)
            velocity_publisher.publish(vel_msg)

            rate.sleep()


    except Exception as e:
        print(e)
