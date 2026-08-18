import os
import xacro
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    pkg_description = FindPackageShare('tortoisebot_description').find('tortoisebot_description')
    urdf_path = os.path.join(pkg_description, 'urdf', 'tortoisebot.urdf.xacro')

    pkg_gazebo = FindPackageShare('tortoisebot_gazebo').find('tortoisebot_gazebo')
    world_path = os.path.join(pkg_gazebo, 'worlds', 'empty_world.world')

    # xacro must be processed into plain URDF XML before handing to robot_state_publisher
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

    spawn_entity_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        output='screen',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'tortoisebot'
        ]
    )

    # rviz.launch.py included with standalone:=false, since robot_state_publisher
    # above already publishes robot_description -- avoids a duplicate node.
    # joint_state_publisher_gui is also skipped here: once spawned, the
    # libgazebo_ros_joint_state_publisher.so plugin in the URDF publishes real
    # joint states from physics, which the GUI slider would otherwise fight with.
    rviz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_description, 'launch', 'rviz.launch.py'])
        ),
        launch_arguments={
            'standalone': 'false',
            'use_sim_time': 'true'
        }.items()
    )

    return LaunchDescription([
        gazebo_server,
        robot_state_publisher_node,
        # Small delay so Gazebo's factory service is ready before we call it.
        TimerAction(period=3.0, actions=[spawn_entity_node]),
        TimerAction(period=3.0, actions=[rviz_launch]),
    ])