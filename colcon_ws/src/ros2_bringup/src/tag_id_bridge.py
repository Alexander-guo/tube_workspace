#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from ros2_aruco_interfaces.msg import ArucoMarkers


class TagIdBridge(Node):
    def __init__(self):
        super().__init__("tag_id_bridge")

        self.declare_parameter("in_topic", "aruco_markers")
        self.declare_parameter("out_topic", "tag_id")

        in_topic = self.get_parameter("in_topic").get_parameter_value().string_value
        out_topic = self.get_parameter("out_topic").get_parameter_value().string_value

        self.publisher = self.create_publisher(Int32, out_topic, 10)
        self.subscription = self.create_subscription(
            ArucoMarkers, in_topic, self.markers_callback, 10
        )

    def markers_callback(self, msg: ArucoMarkers):
        if not msg.marker_ids:
            return
        tag_msg = Int32()
        tag_msg.data = int(msg.marker_ids[0])
        self.publisher.publish(tag_msg)


def main(args=None):
    rclpy.init(args=args)
    node = TagIdBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
