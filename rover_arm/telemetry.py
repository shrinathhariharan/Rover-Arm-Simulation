#!/usr/bin/env python3
"""Publishes a compact rover status string for demos and debugging."""

from __future__ import annotations

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import String


class Telemetry(Node):
    def __init__(self) -> None:
        super().__init__("telemetry")
        self.state = "UNKNOWN"
        self.odom: Odometry | None = None
        self.pub = self.create_publisher(String, "/rover_arm/telemetry", 10)
        self.create_subscription(String, "/rover_arm/state", self._on_state, 10)
        self.create_subscription(Odometry, "/odom", self._on_odom, 10)
        self.create_timer(0.5, self._publish)

    def _on_state(self, msg: String) -> None:
        self.state = msg.data

    def _on_odom(self, msg: Odometry) -> None:
        self.odom = msg

    def _publish(self) -> None:
        msg = String()
        if self.odom is None:
            msg.data = f"state={self.state}; pose=unknown"
        else:
            p = self.odom.pose.pose.position
            msg.data = f"state={self.state}; x={p.x:.2f}; y={p.y:.2f}"
        self.pub.publish(msg)


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = Telemetry()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
