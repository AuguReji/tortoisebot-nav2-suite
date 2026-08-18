#!/usr/bin/env python3

import math
import statistics

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32

# Half-width of the front-facing field of view, in degrees.
FOV_HALF_DEG = 15.0


class ClosestObjectDistance(Node):

    def __init__(self):
        super().__init__('closest_object_distance')

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )
        self.publisher = self.create_publisher(
            Float32,
            '/closest_object_distance',
            10
        )

        self.get_logger().info(
            f'closest_object_distance node started, watching front ±{FOV_HALF_DEG}° FOV'
        )

    def scan_callback(self, msg: LaserScan):
        fov_half_rad = math.radians(FOV_HALF_DEG)


        start_angle = -fov_half_rad
        end_angle = fov_half_rad

        idx_start = int(round((start_angle - msg.angle_min) / msg.angle_increment))
        idx_end = int(round((end_angle - msg.angle_min) / msg.angle_increment))

        idx_start = max(0, idx_start)
        idx_end = min(len(msg.ranges) - 1, idx_end)

        if idx_start > idx_end:
            self.get_logger().warn('Computed FOV window is empty; check angle_min/increment')
            return

        window = msg.ranges[idx_start:idx_end + 1]


        valid = [
            r for r in window
            if math.isfinite(r) and r > msg.range_min
        ]

        if not valid:
            self.get_logger().info('No valid returns in front FOV (all inf/nan/out of range)')
            return

        filtered_distance = statistics.median(valid)

        out_msg = Float32()
        out_msg.data = float(filtered_distance)
        self.publisher.publish(out_msg)

        self.get_logger().info(f'Closest object distance: {filtered_distance:.3f} m')


def main(args=None):
    rclpy.init(args=args)
    node = ClosestObjectDistance()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
