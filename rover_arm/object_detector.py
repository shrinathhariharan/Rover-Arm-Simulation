#!/usr/bin/env python3
"""Fake color detector using known Gazebo object positions and robot odometry."""

from __future__ import annotations

import math
from dataclasses import dataclass

import rclpy
from geometry_msgs.msg import Point
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String


@dataclass
class SimObject:
    name: str
    color: str
    x: float
    y: float


class ObjectDetector(Node):
    def __init__(self) -> None:
        super().__init__("object_detector")
        self.declare_parameter("target_color", "red")
        self.declare_parameter("detection_range_m", 3.0)
        self.declare_parameter("detection_fov_deg", 90.0)
        self.declare_parameter("color_pixel_threshold", 40)
        self.declare_parameter("object_names", ["red_ball", "green_cube", "purple_pyramid"])
        self.declare_parameter("object_colors", ["red", "green", "purple"])
        self.declare_parameter("object_positions_x", [2.2, 3.0, 1.8])
        self.declare_parameter("object_positions_y", [0.7, -1.0, 1.4])

        self.odom: Odometry | None = None
        self.camera_seen = False
        self.have_camera = False
        self.detection_pub = self.create_publisher(String, "/rover_arm/detected_object", 10)
        self.target_pub = self.create_publisher(Point, "/rover_arm/target_point", 10)
        self.create_subscription(Odometry, "/odom", self._on_odom, 10)
        self.create_subscription(Image, "/camera/image_raw", self._on_image, 10)
        self.create_timer(0.2, self._detect)

    def _on_odom(self, msg: Odometry) -> None:
        self.odom = msg

    def _on_image(self, msg: Image) -> None:
        self.have_camera = True
        target_color = str(self.get_parameter("target_color").value).lower()
        threshold = int(self.get_parameter("color_pixel_threshold").value)
        self.camera_seen = self._count_color_pixels(msg, target_color) >= threshold

    def _objects(self) -> list[SimObject]:
        names = list(self.get_parameter("object_names").value)
        colors = list(self.get_parameter("object_colors").value)
        xs = list(self.get_parameter("object_positions_x").value)
        ys = list(self.get_parameter("object_positions_y").value)
        return [
            SimObject(name, color, float(x), float(y))
            for name, color, x, y in zip(names, colors, xs, ys)
        ]

    def _detect(self) -> None:
        if self.odom is None:
            return

        pose = self.odom.pose.pose
        robot_x = pose.position.x
        robot_y = pose.position.y
        yaw = self._yaw_from_quaternion(pose.orientation)
        target_color = str(self.get_parameter("target_color").value).lower()
        detection_range = float(self.get_parameter("detection_range_m").value)
        half_fov = math.radians(float(self.get_parameter("detection_fov_deg").value) * 0.5)

        matches: list[tuple[float, SimObject]] = []
        for obj in self._objects():
            if obj.color.lower() != target_color:
                continue
            dx = obj.x - robot_x
            dy = obj.y - robot_y
            distance = math.hypot(dx, dy)
            bearing = math.atan2(dy, dx)
            if distance <= detection_range and abs(self._normalize(bearing - yaw)) <= half_fov:
                matches.append((distance, obj))

        if not matches or (self.have_camera and not self.camera_seen):
            return

        _, obj = min(matches, key=lambda item: item[0])
        detection = String()
        detection.data = f"{obj.name},{obj.color},{obj.x:.3f},{obj.y:.3f}"
        self.detection_pub.publish(detection)

        target = Point()
        target.x = obj.x
        target.y = obj.y
        self.target_pub.publish(target)

    @staticmethod
    def _yaw_from_quaternion(q) -> float:
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        return math.atan2(siny_cosp, cosy_cosp)

    @staticmethod
    def _normalize(angle: float) -> float:
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle

    @staticmethod
    def _count_color_pixels(msg: Image, color: str) -> int:
        if msg.encoding not in ("rgb8", "bgr8", "R8G8B8"):
            return 0

        red_index = 0 if msg.encoding in ("rgb8", "R8G8B8") else 2
        green_index = 1
        blue_index = 2 if msg.encoding in ("rgb8", "R8G8B8") else 0
        step = 3
        count = 0

        data = msg.data
        for offset in range(0, len(data) - 2, step * 20):
            red = data[offset + red_index]
            green = data[offset + green_index]
            blue = data[offset + blue_index]
            if color == "red" and red > 150 and green < 90 and blue < 90:
                count += 1
            elif color == "green" and green > 130 and red < 100 and blue < 110:
                count += 1
            elif color == "purple" and red > 80 and blue > 120 and green < 100:
                count += 1
        return count


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = ObjectDetector()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
