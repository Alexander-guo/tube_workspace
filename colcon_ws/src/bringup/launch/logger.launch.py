#!/usr/bin/env python3

import os
from datetime import datetime

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    experiment = os.getenv('EXPERIMENT', 'tube0')
    user = os.getenv('USER', 'afrl')
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    default_bag_name = f"/home/{user}/data/{experiment}_{timestamp}"

    bag_name = LaunchConfiguration('bag_name')

    default_topics = [
        # '/sonar_3d/raw_data',
        # '/sonar_3d/raw_data_multibyte',
        # '/camera_array/cam0/image_raw/compressed',
        # '/camera_array/cam0/camera_info',
        # '/mini_ahrs_ros/imu',
        # '/mini_ahrs_ros/magnetic_field',
        # '/mini_ahrs_ros/temperature',
        '/image_raw',
        '/image_raw/compressed',
        '/imu/data',
        '/imu/data_raw',
        '/ekf/status',
        '/tf',
        '/tf_static',
        '/bar30/depth',
        '/bar30/pressure',
        '/bar30/temperature',
    ]

    return LaunchDescription([
        DeclareLaunchArgument('bag_name', default_value=default_bag_name),
        ExecuteProcess(
            cmd=['ros2', 'bag', 'record', '-o', bag_name] + default_topics,
            output='screen',
        ),
    ])
