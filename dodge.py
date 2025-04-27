import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from irobot_create_msgs.action import RotateAngle
from rclpy.action import ActionClient
import time

class Create3RobotControl(Node):
    def __init__(self):
        super().__init__('create3_robot_control')
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
    def move_forward(self, duration):
        move_cmd = Twist()
        move_cmd.linear.x = 0.2
        self.cmd_vel_pub.publish(move_cmd)
        time.sleep(duration)
        move_cmd.linear.x = 0.0
        self.cmd_vel_pub.publish(move_cmd)

    def turn_left(self, duration):
        move_cmd = Twist()
        move_cmd.angular.z = 0.5
        self.cmd_vel_pub.publish(move_cmd)
        time.sleep(duration)
        move_cmd.angular.z = 0.0
        self.cmd_vel_pub.publish(move_cmd)

    def turn_right(self, duration):
        move_cmd = Twist()
        move_cmd.angular.z = -0.5
        self.cmd_vel_pub.publish(move_cmd)
        time.sleep(duration)
        move_cmd.angular.z = 0.0
        self.cmd_vel_pub.publish(move_cmd)

def main(args=None):
    rclpy.init(args=args)
    control_node = Create3RobotControl()

    control_node.move_forward(2)
    control_node.turn_left(1)
    control_node.move_forward(3)
    control_node.turn_right(1)

    control_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
