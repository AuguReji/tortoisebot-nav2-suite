from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'tortoisebot_gazebo'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*.launch.py'))),
        (os.path.join('share', package_name, 'worlds'),
            glob(os.path.join('worlds', '*.world'))),
        (os.path.join('share', package_name, 'worlds'),
            glob(os.path.join('worlds', '*.world')) + glob(os.path.join('worlds', '*.sdf'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='',
    maintainer_email='',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'closest_object_distance = tortoisebot_gazebo.closest_object_distance:main',
            'lidar_dis = tortoisebot_gazebo.lidar_dis:main',
            'ball_follower = tortoisebot_gazebo.ball_follower:main',
            'ball_lidar_dis = tortoisebot_gazebo.ball_lidar_dis:main',
        ],
    },
)
