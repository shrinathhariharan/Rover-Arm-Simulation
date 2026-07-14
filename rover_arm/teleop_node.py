#!/usr/bin/env python3
"""WASD keyboard teleoperation for the rover base."""

from __future__ import annotations

import select
import sys
import termios
import tty

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


HELP = "W/S forward/back, A/D turn, space stop, Q quit"


class TeleopNode(Node):
    def __init__(self) -> None:
        super().__init__("teleop_node")
        self.declare_parameter("linear_step", 0.25)
        self.declare_parameter("angular_step", 0.75)
        self.publisher = self.create_publisher(Twist, "/cmd_vel_teleop", 10)

    def publish_key(self, key: str) -> bool:
        twist = Twist()
        linear = float(self.get_parameter("linear_step").value)
        angular = float(self.get_parameter("angular_step").value)

        if key == "w":
            twist.linear.x = linear
        elif key == "s":
            twist.linear.x = -linear
        elif key == "a":
            twist.angular.z = angular
        elif key == "d":
            twist.angular.z = -angular
        elif key == " ":
            pass
        elif key == "q":
            return False
        else:
            return True

        self.publisher.publish(twist)
        return True


def read_key(timeout: float = 0.1) -> str:
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        return sys.stdin.read(1).lower()
    return ""


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = TeleopNode()
    old_settings = termios.tcgetattr(sys.stdin)
    print(HELP)
    try:
        tty.setcbreak(sys.stdin.fileno())
        keep_running = True
        while rclpy.ok() and keep_running:
            rclpy.spin_once(node, timeout_sec=0.0)
            key = read_key()
            if key:
                keep_running = node.publish_key(key)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
