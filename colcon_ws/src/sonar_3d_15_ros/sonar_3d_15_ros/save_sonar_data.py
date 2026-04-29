#!/usr/bin/env python3
"""
Simple example script to listen for Sonar 3D-15 data over multicast and store it to a file for later.
The "inspect_sonar_data.py" script can be used to read the data from the file and decode it.
"""

import argparse
import socket
import struct
from datetime import datetime

import rclpy
from rclpy.node import Node
from rclpy.utilities import remove_ros_args
from std_msgs.msg import UInt8MultiArray

MULTICAST_GROUP = "224.0.0.96"
PORT = 4747
BUFFER_SIZE = 65535


class SonarMulticastReceiver(Node):
    def __init__(
        self,
        sonar_ip: str,
        output_file: str,
        multicast_group: str,
        port: int,
        topic: str,
    ) -> None:
        super().__init__("sonar_3d_receiver")
        self.sonar_ip = sonar_ip
        self.output_file = output_file
        self.multicast_group = multicast_group
        self.port = port
        self.publisher = self.create_publisher(UInt8MultiArray, topic, 10)

    def receive_multicast(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", self.port))

        group = socket.inet_aton(self.multicast_group)
        mreq = struct.pack("4sL", group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        self.get_logger().info(
            f"Listening for Sonar 3D-15 RIP1 packets on {self.multicast_group}:{self.port}"
        )
        if self.sonar_ip:
            self.get_logger().info(f"Filtering packets from IP: {self.sonar_ip}")

        if self.output_file:
            self.get_logger().info(f"Saving data to: {self.output_file}")
        else:
            self.get_logger().info("No output file set. Publishing only.")
        self.get_logger().info("Press Ctrl+C to stop.")

        file_handle = None
        if self.output_file:
            file_handle = open(self.output_file, "wb")

        try:
            while rclpy.ok():
                data, addr = sock.recvfrom(BUFFER_SIZE)

                if self.sonar_ip and addr[0] != self.sonar_ip:
                    continue

                if file_handle is not None:
                    file_handle.write(data)
                    file_handle.flush()

                msg = UInt8MultiArray()
                msg.data = list(data)
                self.publisher.publish(msg)
        except KeyboardInterrupt:
            self.get_logger().info("Stopping multicast receiver.")
        finally:
            if file_handle is not None:
                file_handle.close()
            sock.close()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Receive data from a Sonar 3D-15 via Multicast and save to file."
    )
    parser.add_argument(
        "--ip",
        type=str,
        default="",
        help="Limit to packets from this IP address (default: all).",
    )
    parser.add_argument(
        "--file",
        type=str,
        default="",
        help="Output filename for received data (default: generated).",
    )
    parser.add_argument(
        "--index",
        type=str,
        default="",
        help="Index of filename",
    )
    parser.add_argument(
        "--multicast-group",
        type=str,
        default=MULTICAST_GROUP,
        help=f"Multicast group to listen to (default: {MULTICAST_GROUP}).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=PORT,
        help=f"UDP port to listen on (default: {PORT}).",
    )
    parser.add_argument(
        "--topic",
        type=str,
        default="sonar_3d/raw_data_multibyte",
        help="ROS 2 topic for raw sonar bytes.",
    )
    return parser


def main(args=None) -> None:
    rclpy.init(args=args)
    parser = build_arg_parser()
    parsed_args = parser.parse_args(remove_ros_args(args))

    filename = parsed_args.file
    if not filename:
        ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"sonar-capture-{ts}-{parsed_args.index}.sonar"

    node = SonarMulticastReceiver(
        sonar_ip=parsed_args.ip,
        output_file=filename,
        multicast_group=parsed_args.multicast_group,
        port=parsed_args.port,
        topic=parsed_args.topic,
    )

    try:
        node.receive_multicast()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
