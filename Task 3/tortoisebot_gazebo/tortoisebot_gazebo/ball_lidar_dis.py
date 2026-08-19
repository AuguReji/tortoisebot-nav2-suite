import math
import statistics

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32MultiArray


class LidarDis(Node):

  def __init__(self):
    super().__init__('lidar_dis')

    self.declare_parameter('median_window_deg', 15.0)
    self.median_window_deg = (
        self.get_parameter('median_window_deg')
        .get_parameter_value()
        .double_value
    )

    qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)

    self.subscription = self.create_subscription(
        LaserScan, '/scan', self.listener_callback, qos
    )
    self.obs_data_pub = self.create_publisher(
        Float32MultiArray, '/closest_object_info', 10
    )

  def listener_callback(self, msg: LaserScan):
    valid_indices = [
        i
        for i, d in enumerate(msg.ranges)
        if not (math.isinf(d) or math.isnan(d) or d <= 0)
        and msg.range_min < d < msg.range_max
    ]

    if not valid_indices:
      return

    min_idx = min(valid_indices, key=lambda i: msg.ranges[i])
    min_angle_rad = msg.angle_min + (min_idx * msg.angle_increment)

    window_half_samples = max(
        1,
        int(
            round(math.radians(self.median_window_deg) / msg.angle_increment)
        ),
    )
    lo = max(0, min_idx - window_half_samples)
    hi = min(len(msg.ranges) - 1, min_idx + window_half_samples)

    local_window = msg.ranges[lo : hi + 1]
    local_valid = [
        d
        for d in local_window
        if not (math.isinf(d) or math.isnan(d) or d <= 0)
        and msg.range_min < d < msg.range_max
    ]

    filtered_dist = (
        statistics.median(local_valid) if local_valid else msg.ranges[min_idx]
    )
    filtered_ang_deg = math.degrees(min_angle_rad)

    info_msg = Float32MultiArray()
    info_msg.data = [float(filtered_dist), float(filtered_ang_deg)]
    self.obs_data_pub.publish(info_msg)


def main(args=None):
  rclpy.init(args=args)
  node = LidarDis()
  try:
    rclpy.spin(node)
  except KeyboardInterrupt:
    pass
  finally:
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
  main()