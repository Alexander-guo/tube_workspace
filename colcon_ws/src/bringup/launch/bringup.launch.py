#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    usb_cam_params = os.path.join(
        get_package_share_directory('usb_cam'),
        'config',
        'params_1.yaml',
    )

    microstrain_launch = os.path.join(
        get_package_share_directory('microstrain_inertial_driver'),
        'launch',
        'microstrain_launch.py',
    )

    return LaunchDescription([
        Node(
            package='usb_cam',
            executable='usb_cam_node_exe',
            parameters=[usb_cam_params],
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(microstrain_launch),
        ),
        Node(
            package='ms5837_bar_ros',
            executable='bar30_node',
        ),
    ])
