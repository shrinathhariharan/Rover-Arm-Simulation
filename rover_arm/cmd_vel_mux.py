#!/usr/bin/env python3
"""
Priority mux between manual WASD teleop and autonomous driving.

Both `state_machine` and `motion_controller` publish autonomous velocity
commands, and `teleop_node` publishes manual WASD commands. Previously all
three published directly to `/cmd_vel`, so autonomous commands (published
on a timer, tens of times per second) would immediately stomp on manual
keypresses. This node arbitrates: if a teleop command was received within
`teleop_priority_timeout_s`, it wins and is forwarded to `/cmd_vel`.
Otherwise the latest autonomous command is forwarded instead.
"""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class CmdVelMux(Node):
    def __init__(self) -> None:
        super().__init__("cmd_vel_mux")
        self.declare_parameter("teleop_priority_timeout_s", 0.75)
        self.declare_parameter("publish_rate_hz", 20.0)

        self.last_teleop_cmd = Twist()
        self.last_auto_cmd = Twist()
        self.last_teleop_time: rclpy.time.Time | None = None

        self.cmd_pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.create_subscription(Twist, "/cmd_vel_teleop", self._on_teleop, 10)
        self.create_subscription(Twist, "/cmd_vel_auto", self._on_auto, 10)

        rate_hz = float(self.get_parameter("publish_rate_hz").value)
        self.create_timer(1.0 / rate_hz, self._tick)

    def _on_teleop(self, msg: Twist) -> None:
        self.last_teleop_cmd = msg
        self.last_teleop_time = self.get_clock().now()

    def _on_auto(self, msg: Twist) -> None:
        self.last_auto_cmd = msg

    def _teleop_is_fresh(self) -> bool:
        if self.last_teleop_time is None:
            return False
        timeout_s = float(self.get_parameter("teleop_priority_timeout_s").value)
        age_s = (self.get_clock().now() - self.last_teleop_time).nanoseconds / 1e9
        return age_s < timeout_s

    def _tick(self) -> None:
        if self._teleop_is_fresh():
            self.cmd_pub.publish(self.last_teleop_cmd)
        else:
            self.cmd_pub.publish(self.last_auto_cmd)


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = CmdVelMux()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
