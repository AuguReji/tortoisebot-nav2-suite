import os
import xacro
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_description = FindPackageShare('tortoisebot_description').find('tortoisebot_description')
    urdf_path = os.path.join(pkg_description, 'urdf', 'tortoisebot.urdf.xacro')

    pkg_gazebo = FindPackageShare('tortoisebot_gazebo').find('tortoisebot_gazebo')
    world_path = os.path.join(pkg_gazebo, 'worlds', 'empty_world.world')
    robot_description_xml = xacro.process_file(urdf_path).toxml()

    gazebo_server = ExecuteProcess(
        cmd=[
            'gazebo',
            '--verbose',
            world_path,
            '-s', 'libgazebo_ros_init.so',
            '-s', 'libgazebo_ros_factory.so'
        ],
        output='screen'
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_xml,
            'use_sim_time': True
        }]
    )

    spawn_robot_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        output='screen',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'tortoisebot'
        ]
    )
    lidar_dis_node = Node(
        package='tortoisebot_gazebo',
        executable='ball_lidar_dis',
        output='screen'
    )

    ball_follower_node = Node(
        package='tortoisebot_gazebo',
        executable='ball_follower',
        output='screen'
    )

    return LaunchDescription([
        gazebo_server,
        robot_state_publisher_node,
        # Staggered delays give Gazebo's factory service, then the robot
        # itself, time to be ready before each next step fires.
        TimerAction(period=3.0, actions=[spawn_robot_node]),
        TimerAction(period=5.0, actions=[lidar_dis_node, ball_follower_node]),
    ])
