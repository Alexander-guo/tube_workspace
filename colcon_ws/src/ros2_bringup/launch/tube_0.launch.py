import os
import launch
import yaml
import datetime
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node, PushRosNamespace
from launch.actions import IncludeLaunchDescription, ExecuteProcess, OpaqueFunction, GroupAction, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def bag_exists(time_cap):
    file_path = '/home/afrl/data/'
    num= 0
    for dirpath, dirnames, filenames in os.walk(file_path):
        for dirname in dirnames:
            if time_cap in dirname:
                num = num + 1
    return num

def generate_launch_description():

    ct = datetime.datetime.now()
    ct_str = ct.strftime("%Y-%m-%d-%H_%M_%S")
    num_files = bag_exists(ct_str)
    if num_files > 0:
        ct_str = ct_str + "_" + str(num_files)

    launch_params_path = os.path.join('/home/afrl/tube_workspace/colcon_ws/src/ros2_bringup/config/params.yaml')
    with open(launch_params_path, 'r') as f:
        launch_params = yaml.safe_load(f)

    device = launch_params["tube0"]['ros_parameters']['device']
    data_path = launch_params["tube0"]['ros_parameters']['data_path']
    cam_topic = launch_params["tube0"]['ros_parameters']['cam_topic']
    cam_info_topic = launch_params["tube0"]['ros_parameters']['cam_info_topic']
    # serial = launch_params["tube0"]['ros_parameters']['serial']
    # sonar = launch_params["tube0"]['ros_parameters']['sonar']
    #pixel_format = launch_params["tube0"]['ros_parameters']['pixel_format']
    # camera_type = launch_params["tube0"]['ros_parameters']['camera_type']
    # debug = launch_params["tube0"]['ros_parameters']['debug']
    # compute_brightness = launch_params["tube0"]['ros_parameters']['compute_brightness']
    # adjust_timestamp = launch_params["tube0"]['ros_parameters']['adjust_timestamp']
    # dump_node_map = launch_params["tube0"]['ros_parameters']['dump_node_map']
    # gain_auto = launch_params["tube0"]['ros_parameters']['gain_auto']
    # exposure_auto = launch_params["tube0"]['ros_parameters']['exposure_auto']
    # user_set_selector = launch_params["tube0"]['ros_parameters']['user_set_selector']
    # user_set_load = launch_params["tube0"]['ros_parameters']['user_set_load']
    # frame_rate_auto = launch_params["tube0"]['ros_parameters']['frame_rate_auto']
    # frame_rate = launch_params["tube0"]['ros_parameters']['frame_rate']
    # frame_rate_enable = launch_params["tube0"]['ros_parameters']['frame_rate_enable']
    # buffer_queue_size = launch_params["tube0"]['ros_parameters']['buffer_queue_size']
    # trigger_mode = launch_params["tube0"]['ros_parameters']['trigger_mode']
    # chunk_mode_active = launch_params["tube0"]['ros_parameters']['chunk_mode_active']
    # chunk_selector_frame_id = launch_params["tube0"]['ros_parameters']['chunk_selector_frame_id']
    # chunk_enable_frame_id = launch_params["tube0"]['ros_parameters']['chunk_enable_frame_id']
    # chunk_selector_exposure_time = launch_params["tube0"]['ros_parameters']['chunk_selector_exposure_time']
    # chunk_enable_exposure_time = launch_params["tube0"]['ros_parameters']['chunk_enable_exposure_time']
    # chunk_selector_gain = launch_params["tube0"]['ros_parameters']['chunk_selector_gain']
    # chunk_enable_gain = launch_params["tube0"]['ros_parameters']['chunk_enable_gain']
    # chunk_selector_timestamp = launch_params["tube0"]['ros_parameters']['chunk_selector_timestamp']
    # chunk_enable_timestamp = launch_params["tube0"]['ros_parameters']['chunk_enable_timestamp']
    namespace = LaunchConfiguration('namespace')

   
    # Paths to various files
    # microstrain_launch_file = os.path.join(
    #     get_package_share_directory('microstrain_inertial_examples'),
    #     'launch', 'cv7_launch.py'
    # )
    # cv7_params_file = os.path.join(
    #     get_package_share_directory('microstrain_inertial_examples'),
    #     'config', 'cv7', 'cv7.yml'
    # )
    microstrain_launch_file = os.path.join(
        get_package_share_directory('microstrain_inertial_driver'),
        'launch', 'microstrain_gx5_25_launch.py'
    )
    # sonar_config = os.path.join(
    #     get_package_share_directory('imagenex831l_ros2'),
    #     'cfg', 'sonar.yaml'
    # )

    # cam_dir = get_package_share_directory('spinnaker_camera_driver')
    # sonar_dir = get_package_share_directory('imagenex831l_ros2')
    # screen_dir = get_package_share_directory('custom_guyi')
    cam_dir = get_package_share_directory('usb_cam')
    tag_dir = get_package_share_directory('ros2_aruco')

    usb_cam_params = os.path.join(
        cam_dir,
        'config',
        'params_1.yaml'
    )

    # Group actions and nodes
    # included_cam_launch = GroupAction(
    #     actions=[
    #         PushRosNamespace(namespace),
    #         IncludeLaunchDescription(
    #             PythonLaunchDescriptionSource(os.path.join(cam_dir, 'launch', 'driver_node.launch.py')),
    #             launch_arguments={
    #                 'camera_type': camera_type,
    #                 'serial': serial,
    #                 'debug': debug,
    #                 'compute_brightness': compute_brightness,
    #                 'adjust_timestamp': adjust_timestamp,
    #                 'dump_node_map': dump_node_map,
    #                 'gain_auto': gain_auto,
    #                 'exposure_auto': exposure_auto,
    #                 'user_set_selector': user_set_selector,
    #                 'user_set_load': user_set_load,
    #                 'frame_rate_auto': frame_rate_auto,
    #                 'frame_rate': frame_rate,
    #                 'frame_rate_enable': frame_rate_enable,
    #                 'buffer_queue_size': buffer_queue_size,
    #                 'trigger_mode': trigger_mode,
    #                 'chunk_mode_active': chunk_mode_active,
    #                 'chunk_selector_frame_id': chunk_selector_frame_id,
    #                 'chunk_enable_frame_id': chunk_enable_frame_id,
    #                 'chunk_selector_exposure_time': chunk_selector_exposure_time,
    #                 'chunk_enable_exposure_time': chunk_enable_exposure_time,
    #                 'chunk_selector_gain': chunk_selector_gain,
    #                 'chunk_enable_gain': chunk_enable_gain,
    #                 'chunk_selector_timestamp': chunk_selector_timestamp,
    #                 'chunk_enable_timestamp': chunk_enable_timestamp
    #             }.items()
    #         )
    #     ]
    # )
    cam_node = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        namespace=namespace,
        parameters=[usb_cam_params]
    )

    depth_sensor_node = Node(
        package='ms5837_bar_ros',
        executable='bar30_node',
        namespace=namespace,
        output="screen"
    )

    # base_to_range = Node(
    #     package='tf2_ros',
    #     executable='static_transform_publisher',
    #     output='screen',
    #     namespace=namespace,
    #     arguments=['0.0', '0.0', '0.0', '0', '0.0', '0.0', 'base_link', 'bar30_link']
    # )

    included_imu_launch = GroupAction(
        actions=[
            # PushRosNamespace(namespace),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(microstrain_launch_file),
                launch_arguments={'namespace': namespace}.items()
            )
        ]
    )

    # included_sonar_launch = GroupAction(
    #     actions=[
    #         PushRosNamespace(namespace),
    #         IncludeLaunchDescription(
    #             PythonLaunchDescriptionSource(os.path.join(sonar_dir, 'launch', 'sonar.launch.py')),
    #             launch_arguments={'sonar': sonar, 'device': device, 'config': sonar_config}.items()
    #         )
    #     ]
    # )
    
    # included_screen_launch = GroupAction(
    #     actions=[
    #         PushRosNamespace(namespace),
    #         IncludeLaunchDescription(
    #             PythonLaunchDescriptionSource(os.path.join(screen_dir, 'launch', 'gui.launch.py')),
    #             launch_arguments={'cam_topic': cam_topic, 'device': device}.items(),
    #         )
    #     ]
    # )

    included_tag_launch = GroupAction(
        actions=[
            PushRosNamespace(namespace),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(os.path.join(tag_dir, 'launch', 'aruco_recognition.launch.py')),
                launch_arguments={'image_topic': cam_topic, 'aruco_dictionary_id': 'DICT_ARUCO_ORIGINAL', 
                                  'camera_info_topic': cam_info_topic}.items(),
            )
        ]
    )

    rosbag_node = Node(
        package='ros2_bringup',
        executable='rosbag.py',
        parameters=[{'device': device, 'data_path': data_path}]
    )

    tag_id_bridge_node = Node(
        package='ros2_bringup',
        executable='tag_id_bridge.py',
        namespace=namespace,
        parameters=[{
            'in_topic': 'aruco_markers',
            'out_topic': 'tag_id'
        }]
    )

    # Return the LaunchDescription
    return LaunchDescription([
        DeclareLaunchArgument(
            'namespace',
            default_value=device,
            description='ROS namespace for all nodes in this launch.'
        ),
        included_tag_launch,
        tag_id_bridge_node,
        # included_cam_launch,
        cam_node,
        rosbag_node,
        depth_sensor_node,
        # base_to_range,
        included_imu_launch
        # included_sonar_launch,
        # included_screen_launch
    ])
