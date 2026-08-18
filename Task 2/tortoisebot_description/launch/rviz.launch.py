import os
import xacro
import launch_ros
import launch
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_path = launch_ros.substitutions.FindPackageShare(
        package="tortoisebot_description"
    ).find("tortoisebot_description")

    urdf_model_path = os.path.join(pkg_path, 'urdf', 'tortoisebot.urdf.xacro')
    rviz_config_path = os.path.join(pkg_path, 'config', 'tortoisebot.rviz')

    standalone_arg = DeclareLaunchArgument(
        'standalone',
        default_value='false',
        description='Run robot_state_publisher + joint_state_publisher_gui here (true), '
                     'or assume another launch file already provides them (false)'
    )
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true'
    )

    standalone = LaunchConfiguration('standalone')
    use_sim_time = LaunchConfiguration('use_sim_time')

    robot_description_xml = xacro.process_file(urdf_model_path).toxml()
    params = {'robot_description': robot_description_xml}

    robot_state_publisher_node = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params, {'use_sim_time': use_sim_time, 'publish_frequency': 50.0}],
        condition=IfCondition(standalone)
    )

    joint_state_publisher_gui_node = launch_ros.actions.Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        condition=IfCondition(standalone)
    )

    rviz_node = launch_ros.actions.Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    return launch.LaunchDescription([
        standalone_arg,
        use_sim_time_arg,
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])