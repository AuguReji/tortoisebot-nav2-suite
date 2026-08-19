#!/usr/bin/env python3
"""
Subscribes to /closest_object_info and drives the robot to follow it.
Uses proportional linear and angular control with enhanced stopping logic 
to prevent colliding with/hitting the object.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from std_msgs.msg import Float32MultiArray
from geometry_msgs.msg import Twist


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


class BallFollower(Node):

    def __init__(self):
        super().__init__('ball_follower')

        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)

        self.subscription = self.create_subscription(
            Float32MultiArray,
            '/closest_object_info',
            self.info_callback,
            qos
        )
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Control Parameters
        self.declare_parameter('align_threshold_deg', 8.0)
        self.declare_parameter('stop_distance_m', 0.25)       # Increased safety standoff distance
        self.declare_parameter('slowdown_distance_m', 0.50)   # Distance to begin gentle braking
        self.declare_parameter('max_linear_speed', 0.8)
        self.declare_parameter('max_angular_speed', 1.2)
        self.declare_parameter('kp_linear', 0.6)
        self.declare_parameter('kp_angular', 0.03)
        self.declare_parameter('detection_timeout_sec', 1.0)

        self.align_threshold_deg = self.get_parameter('align_threshold_deg').value
        self.stop_distance_m = self.get_parameter('stop_distance_m').value
        self.slowdown_distance_m = self.get_parameter('slowdown_distance_m').value
        self.max_linear_speed = self.get_parameter('max_linear_speed').value
        self.max_angular_speed = self.get_parameter('max_angular_speed').value
        self.kp_linear = self.get_parameter('kp_linear').value
        self.kp_angular = self.get_parameter('kp_angular').value
        self.detection_timeout_sec = self.get_parameter('detection_timeout_sec').value

        self.last_detection_time = None
        self.watchdog_timer = self.create_timer(0.2, self.watchdog_check)

    def info_callback(self, msg: Float32MultiArray):
        if len(msg.data) < 2:
            return

        distance, angle_deg = msg.data[0], msg.data[1]
        self.last_detection_time = self.get_clock().now()

        twist = Twist()

        # Proportional Steering
        angular_cmd = clamp(
            self.kp_angular * angle_deg, -self.max_angular_speed, self.max_angular_speed
        )

        distance_error = distance - self.stop_distance_m

        if distance_error > 0.0:
            # Quadratic/Scaled deceleration curve as it gets inside slowdown_distance_m
            if distance_error < self.slowdown_distance_m:
                # Smooth deceleration scaling factor (0.0 to 1.0)
                speed_scale = (distance_error / self.slowdown_distance_m) ** 2
                calculated_linear_speed = self.kp_linear * distance_error * speed_scale
            else:
                calculated_linear_speed = self.kp_linear * distance_error

            linear_cmd = clamp(calculated_linear_speed, 0.0, self.max_linear_speed)

            if abs(angle_deg) > (self.align_threshold_deg * 2.5):
                twist.linear.x = 0.0
                twist.angular.z = angular_cmd
            else:
                twist.linear.x = linear_cmd
                twist.angular.z = angular_cmd
        else:
            # Target reached or passed stop_distance: Hard brake
            twist.linear.x = 0.0
            twist.angular.z = 0.0

        self.cmd_pub.publish(twist)

    def watchdog_check(self):
        if self.last_detection_time is None:
            return

        elapsed = (self.get_clock().now() - self.last_detection_time).nanoseconds / 1e9
        if elapsed > self.detection_timeout_sec:
            self.cmd_pub.publish(Twist())


def main(args=None):
    rclpy.init(args=args)
    node = BallFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cmd_pub.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()