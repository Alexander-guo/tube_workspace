#!/usr/bin/env python3
"""
Configure the Sonar 3D-15 via HTTP API, then listen to multicast data and publish raw bytes.
"""

import argparse
from datetime import datetime
from pathlib import Path

import rclpy
from rclpy.utilities import remove_ros_args

from .interface_sonar_api import (
    get_about,
    get_status,
    get_speed,
    get_acoustics,
    set_acoustics,
    set_speed,
    describe_response,
)
from .save_sonar_data import SonarMulticastReceiver, MULTICAST_GROUP, PORT


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Setup Sonar 3D-15 API settings and publish multicast data."
    )
    parser.add_argument(
        "--ip",
        type=str,
        required=True,
        help="IP address of the sonar.",
    )
    parser.add_argument(
        "--speed",
        type=int,
        default=1500,
        help="Speed of sound in m/s.",
    )
    parser.add_argument(
        "--acoustics",
        type=bool,
        default=True,
        help="Enable or disable acoustics (enable/disable).",
    )
    parser.add_argument(
        "--output-file-dir",
        type=str,
        default="",
        help="Output file directory for received data. If None, do not save. If not None, then 'dir/sonar-capture-\{ts\}.sonar'",
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
    parser = build_arg_parser()
    parsed_args = parser.parse_args(remove_ros_args(args))

    about = get_about(parsed_args.ip)
    print(f"About:\n{about}")

    status = get_status(parsed_args.ip)
    print(f"Status:\n{status}")

    speed = get_speed(parsed_args.ip)
    print(f"Speed of Sound:\t   {speed}")

    acoustics = get_acoustics(parsed_args.ip)
    print(f"Acoustics enabled: {acoustics}\n")

    if parsed_args.acoustics is not None:
        acoustics_response = set_acoustics(parsed_args.ip, parsed_args.acoustics)
        describe_response("Acoustics:\t  ", acoustics_response)

    if parsed_args.speed is not None:
        speed_response = set_speed(parsed_args.ip, parsed_args.speed)
        describe_response("Speed of sound:\t  ", speed_response)

    output_file_dir = parsed_args.output_file_dir
    if output_file_dir != "":
        ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = str(Path(output_file_dir) / f"sonar-capture-{ts}.sonar")
    else:
        filename = None

    rclpy.init(args=args)
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
