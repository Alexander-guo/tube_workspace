import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():

    aruco_params = os.path.join(
        get_package_share_directory('ros2_aruco'),
        'config',
        'aruco_parameters.yaml'
        )

    image_topic = LaunchConfiguration('image_topic')
    camera_info_topic = LaunchConfiguration('camera_info_topic')
    aruco_dictionary_id = LaunchConfiguration('aruco_dictionary_id')

    aruco_node = Node(
        package='ros2_aruco',
        executable='aruco_node',
        parameters=[
            aruco_params,
            {
                'image_topic': image_topic,
                'camera_info_topic': camera_info_topic,
                'aruco_dictionary_id': aruco_dictionary_id,
            },
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'image_topic',
            default_value='/image_raw',
            description='Image topic for ArUco detection.',
        ),
        DeclareLaunchArgument(
            'camera_info_topic',
            default_value='/camera_info',
            description='Camera info topic for ArUco detection.',
        ),
        DeclareLaunchArgument(
            'aruco_dictionary_id',
            default_value='DICT_5X5_250',
            description='ArUco dictionary ID.',
        ),
        aruco_node
    ])
