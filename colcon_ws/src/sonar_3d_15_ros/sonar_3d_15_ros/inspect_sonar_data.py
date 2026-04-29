#!/usr/bin/env python3
"""
Example script to read Sonar 3D-15 data from a file and decode the packets.
The sonar file can be generated with the "save_sonar_data.py" script or in the Sonar GUI (release 1.4.0 or later).

Optionally it can save the RangeImage data to XYZ file format and BitmapImage
to PGM file format.
"""

import argparse
import os
import struct
import zlib
import math

from .sonar_3d_15_protocol_pb2 import (
    Packet,
    BitmapImageGreyscale8,
    RangeImage,
)


def parse_rip1_packet(data: bytes):
    """
    Parse the RIP1 framing:
      1. Verify the "RIP1" magic header
      2. Verify total_length field matches the data size
      3. Check CRC
      4. Extract payload (proto data) from the packet

    Returns:
      payload (bytes) if valid, or None if there's an error.
    """
    if len(data) < 13:
        print(f"Packet too small: only {len(data)} bytes.")
        return None

    magic = data[:4]
    if magic != b"RIP1":
        print(f"Invalid magic: got {magic!r} instead of b'RIP1'.")
        return None

    total_length = struct.unpack("<I", data[4:8])[0]
    if len(data) < total_length:
        print(
            f"Packet truncated: needed {total_length} bytes, got {len(data)}.")
        return None

    payload = data[8: total_length - 4]

    crc_received = struct.unpack("<I", data[total_length - 4: total_length])[0]
    crc_calculated = zlib.crc32(data[: total_length - 4]) & 0xffffffff
    if crc_calculated != crc_received:
        print(
            f"CRC mismatch: expected 0x{crc_calculated:08x}, got 0x{crc_received:08x}.")
        return None

    return payload


def decode_protobuf_packet(payload: bytes):
    """
    Decode the Protobuf Packet (top-level), which may contain:
      - BitmapImageGreyscale8
      - RangeImage
      - or an unknown message type (google.protobuf.Any)

    Returns:
      (msg_type_name, message_object) if successfully parsed,
      or None if parsing failed.
    """
    packet = Packet()
    try:
        packet.ParseFromString(payload)
    except Exception as e:
        print(f"Protobuf parse error: {e}")
        return None

    any_msg = packet.msg
    if not any_msg.IsInitialized():
        return None

    bmp = BitmapImageGreyscale8()
    if any_msg.Unpack(bmp):
        return ("BitmapImageGreyscale8", bmp)

    rng = RangeImage()
    if any_msg.Unpack(rng):
        return ("RangeImage", rng)

    return ("Unknown", any_msg)


def range_image_to_xyz(ri):
    """Convert RangeImage data to a list of voxels with X, Y, Z coordinates."""
    max_pixel_x = ri.width - 1
    max_pixel_y = ri.height - 1
    fov_h = math.radians(ri.fov_horizontal)
    fov_v = math.radians(ri.fov_vertical)

    voxels = []

    for pixel_x in range(ri.width):
        for pixel_y in range(ri.height):
            pixel_value = ri.image_pixel_data[pixel_y * ri.width + pixel_x]
            if pixel_value == 0:
                continue

            yaw_rad = (pixel_x / max_pixel_x) * fov_h - fov_h / 2
            pitch_rad = (pixel_y / max_pixel_y) * fov_v - fov_v / 2
            distance_meters = pixel_value * ri.image_pixel_scale

            x = distance_meters * math.cos(pitch_rad) * math.cos(yaw_rad)
            y = distance_meters * math.cos(pitch_rad) * math.sin(yaw_rad)
            z = -distance_meters * math.sin(pitch_rad)

            voxel = {
                "yaw": yaw_rad,
                "pitch": pitch_rad,
                "distance": distance_meters,
                "x": x,
                "y": y,
                "z": z,
            }

            voxels.append(voxel)
    return voxels


def save_xyz(voxels, file_path):
    """Save the list of voxels to a file in XYZ format."""
    with open(file_path, "w") as f:
        for voxel in voxels:
            x = voxel["x"]
            y = voxel["y"]
            z = voxel["z"]
            f.write(f"{x} {y} {z}\n")
    print(f"Saved {len(voxels)} voxels to {file_path}")


def save_image(bmp_img, file_path: str):
    """Save the BitmapImageGreyscale8 data to a file in PGM format."""
    with open(file_path, "wb") as f:
        f.write(b"P2\n")
        f.write(f"{bmp_img.width} {bmp_img.height}\n".encode())
        f.write(b"255\n")
        for y in range(bmp_img.height - 1, 0, -1):
            for x in range(bmp_img.width):
                pixel_value = bmp_img.image_pixel_data[y * bmp_img.width + x]
                f.write(f"{pixel_value} ".encode())
            f.write(b"\n")
    print(f"Saved BitmapImage to {file_path}")


def handle_packet(data: bytes, save: bool = False, save_path: str = ""):
    payload = parse_rip1_packet(data)
    if payload is None:
        return

    result = decode_protobuf_packet(payload)
    if not result:
        return

    msg_type, msg_obj = result

    if msg_type == "BitmapImageGreyscale8":
        print("  BitmapImageGreyscale8 data:")
        print(f"    Type: {msg_obj.type}")
        print(f"    Width x Height:  {msg_obj.width} x {msg_obj.height}")
        print(f"    Horizontal FoV:  {msg_obj.fov_horizontal}")
        print(f"    Vertical FoV:    {msg_obj.fov_vertical}")

        seq_id = msg_obj.header.sequence_id
        dt = msg_obj.header.timestamp.ToDatetime()
        print(f"    Sequence ID:     {seq_id}")
        print(f"    Timestamp (UTC): {dt.isoformat()}")

        if save:
            filename = f"sonar_image_{seq_id}.pgm"
            file_path = os.path.join(save_path, filename)
            save_image(msg_obj, file_path)

    elif msg_type == "RangeImage":
        print("  RangeImage data:")
        print(f"    Width x Height:    {msg_obj.width} x {msg_obj.height}")
        print(f"    Horizontal FoV:    {msg_obj.fov_horizontal}")
        print(f"    Vertical FoV:      {msg_obj.fov_vertical}")
        print(f"    image_pixel_scale: {msg_obj.image_pixel_scale}")

        seq_id = msg_obj.header.sequence_id
        dt = msg_obj.header.timestamp.ToDatetime()
        print(f"    Sequence ID:         {seq_id}")
        print(f"    Timestamp (UTC):     {dt.isoformat()}")

        voxels = range_image_to_xyz(msg_obj)
        print(f"    Voxel count:         {len(voxels)}")
        if save:
            filename = f"sonar_voxels_{seq_id}.xyz"
            file_path = os.path.join(save_path, filename)
            save_xyz(voxels, file_path)

    else:
        print(
            "  Received an unknown message type (not RangeImage or BitmapImage).")

    print()


def parse_file(filename, save: bool = False):
    with open(filename, "rb") as f:
        content = f.read()

    save_path = os.path.splitext(os.path.basename(filename))[0]
    if save:
        os.makedirs(save_path, exist_ok=True)

    packets = content.split(b"RIP1")
    for pkt in packets:
        handle_packet(b"RIP1" + pkt, save=save, save_path=save_path)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Decode Sonar 3D-15 data from file.")
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save RangeImage data to XYZ file format and BitmapImage to PGM file format.",
    )
    parser.add_argument(
        "--file",
        type=str,
        default="",
        help="Filename to parse.",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.file:
        print(f"Parsing file: {args.file}")
        try:
            with open(args.file, "rb"):
                pass
        except FileNotFoundError:
            print(f"File not found: {args.file}")
            raise SystemExit(1)

        parse_file(args.file, save=args.save)
        raise SystemExit(0)

    print("No file specified. Use --file to specify a file to parse.")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
