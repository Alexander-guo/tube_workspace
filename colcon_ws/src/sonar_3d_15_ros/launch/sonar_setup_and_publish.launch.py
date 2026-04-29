from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _build_node(context, *args, **kwargs):
    node_args = ["--ip", LaunchConfiguration("ip").perform(context)]

    speed = LaunchConfiguration("speed").perform(context)
    if speed:
        node_args += ["--speed", speed]

    acoustics = LaunchConfiguration("acoustics").perform(context)
    if acoustics:
        node_args += ["--acoustics", acoustics]

    multicast_group = LaunchConfiguration("multicast_group").perform(context)
    if multicast_group:
        node_args += ["--multicast-group", multicast_group]

    port = LaunchConfiguration("port").perform(context)
    if port:
        node_args += ["--port", port]

    topic = LaunchConfiguration("topic").perform(context)
    if topic:
        node_args += ["--topic", topic]

    file_path = LaunchConfiguration("file").perform(context)
    if file_path:
        node_args += ["--file", file_path]

    index = LaunchConfiguration("index").perform(context)
    if index:
        node_args += ["--index", index]

    return [
        Node(
            package="sonar_3d_15_ros",
            executable="sonar_3d_setup_publish",
            name="sonar_3d_setup_publish",
            output="screen",
            arguments=node_args,
        )
    ]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("ip", default_value="192.168.2.96", description="IP address of the sonar"),
            DeclareLaunchArgument("speed", default_value=1500, description="Speed of sound in m/s"),
            DeclareLaunchArgument("acoustics", default_value=True, description="enable/disable"),
            DeclareLaunchArgument(
                "multicast_group",
                default_value="224.0.0.96",
                description="Multicast group to listen to",
            ),
            DeclareLaunchArgument(
                "port",
                default_value="4747",
                description="UDP port to listen on",
            ),
            DeclareLaunchArgument(
                "topic",
                default_value="sonar_3d/raw_data_multibyte",
                description="ROS 2 topic for raw sonar bytes",
            ),
            DeclareLaunchArgument("output-file-dir", default_value="", description="Output file directory for received data"),
            # DeclareLaunchArgument("index", default_value="", description="Index of filename"),
            OpaqueFunction(function=_build_node),
        ]
    )
