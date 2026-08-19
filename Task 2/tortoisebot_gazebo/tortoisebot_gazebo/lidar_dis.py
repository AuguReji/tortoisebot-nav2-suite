import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32MultiArray
from rclpy.qos import QoSProfile, ReliabilityPolicy
import math

class LidarDis(Node):
    def __init__(self):
        super().__init__('lidar_dis')

        qos = QoSProfile(depth = 10, reliability = ReliabilityPolicy.BEST_EFFORT)

        self.subscription = self.create_subscription(LaserScan, '/scan', self.listener_callback, qos)

        """self.dist_pub = self.create_publisher (Float32, '/closest_object_distance', 10)
        self.ang_pub = self.create_publisher (Float32, '/closest_object_angle', 10)"""


        #we are publishing distance and angle to single topic
        self.obs_data_pub = self.create_publisher (Float32MultiArray, '/closest_object_info', 10)
        #self.create_publisher(Message_type, Topic_name, Queue Size)

        self.dist_history= [] # list to store min distance
        self.ang_history= [] #list to store angles
        self.history_size = 5
        #Implements a Moving Average filter by keeping only the last 5 readings to smooth out noise.


        self.count = 0

    def listener_callback(self, msg): #Callback Function
        relevant_data = [] # list to store distance and angle
        self.count += 1

        for i, d in enumerate(msg.ranges):
            #checking the values in list are (inf, nan, or zero). If so ignore it.
            if math.isinf(d) or math.isnan (d) or d <= 0:
                continue

            angle = msg.angle_min + (i* msg.angle_increment)
            #finding the angle

            #checking angle is between 15 and +15
            if abs(angle) < math.radians (15):
                if msg.range_min< d < msg.range_max:
                    relevant_data.append((d, angle)) # appending the distance and angle as a tuple inside the list.

        if relevant_data:
            closest_pair = min(relevant_data, key=lambda x: x[0])
            #Finds the tuple with the minimum distance (first element of the tuple) from the list.
            raw_dist = closest_pair[0]
            ang_rad = closest_pair [1]
            ang_deg = math.degrees (ang_rad)
            #angle will be in radian, we need to convert it to degree
            
            self.dist_history.append(raw_dist)
            if len(self.dist_history) > self.history_size:
                self.dist_history.pop(0)

            self.ang_history.append(ang_deg)
            if len(self.ang_history) > self.history_size:
                self.ang_history.pop(0)

            filtered_dist = sum(self.dist_history) / len(self.dist_history) # Taking avg of distance min
            filtered_ang = sum(self.ang_history) / len(self.ang_history)# Taking avg of angle

            #creating object for msg
            info_msg = Float32MultiArray()

            #give data as a list
            info_msg.data = [float(filtered_dist), float(filtered_ang)]
            #publishing
            self.obs_data_pub.publish(info_msg)

            """self.dist_pub.publish(Float32(data=float(filtered_dist))) #publishing filtered distance
            self.ang_pub.publish(Float32(data=float(filtered_ang))) #publishing filtered angle"""
            #self.get_logger().info(f'Filtered Distance: (filtered_dist:.2f]m, Filtered Angle: (filtered_ang:.2f), throttle_duration_sec=1.0)
            
            if self.count %5 ==0:
                print(f'Filtered Distance: {filtered_dist:.2f}m, Filtered Angle: {filtered_ang:.2f}°',flush = True)

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