#!/usr/bin/env python3
"""SEARCHING/NAVIGATING/PICKING behavior for the rover arm demo."""

from __future__ import annotations

from enum import Enum

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Float64, Float64MultiArray, String


class State(Enum):
    SEARCHING = "SEARCHING"
    NAVIGATING = "NAVIGATING"
    PICKING = "PICKING"
    DONE = "DONE"


class StateMachine(Node):
    def __init__(self) -> None:
        super().__init__("state_machine")
        self.declare_parameter("search_linear_speed", 0.0)
        self.declare_parameter("search_angular_speed", 0.35)
        self.declare_parameter("arm_home", [0.0, 0.75, -1.15, 0.0])
        self.declare_parameter("arm_grasp", [0.0, 0.15, -1.25, 1.0])

        self.state = State.SEARCHING
        self.target_object = ""
        self.pick_ticks = 0

        self.cmd_pub = self.create_publisher(Twist, "/cmd_vel_auto", 10)
        self.status_pub = self.create_publisher(String, "/rover_arm/state", 10)
        self.arm_pub = self.create_publisher(Float64MultiArray, "/rover_arm/arm_targets", 10)
        self.joint1_pub = self.create_publisher(Float64, "/rover/joint1_position", 10)
        self.joint2_pub = self.create_publisher(Float64, "/rover/joint2_position", 10)
        self.gripper_pub = self.create_publisher(Float64, "/rover/gripper_position", 10)

        self.create_subscription(String, "/rover_arm/detected_object", self._on_detection, 10)
        self.create_subscription(String, "/rover_arm/motion_status", self._on_motion_status, 10)
        self.create_timer(0.1, self._tick)

    def _on_detection(self, msg: String) -> None:
        if self.state is State.SEARCHING:
            self.target_object = msg.data
            self.state = State.NAVIGATING

    def _on_motion_status(self, msg: String) -> None:
        if self.state is State.NAVIGATING and msg.data == "ARRIVED":
            self.state = State.PICKING
            self.pick_ticks = 0

    def _tick(self) -> None:
        self._publish_state()
        if self.state is State.SEARCHING:
            self._publish_search_cmd()
            self._publish_arm(self._parameter_list("arm_home"))
        elif self.state is State.PICKING:
            self._publish_stop()
            grasp = self._parameter_list("arm_grasp")
            self._publish_arm(grasp)
            self.pick_ticks += 1
            if self.pick_ticks > 25:
                self.state = State.DONE
        elif self.state is State.DONE:
            self._publish_stop()

    def _publish_search_cmd(self) -> None:
        cmd = Twist()
        cmd.linear.x = float(self.get_parameter("search_linear_speed").value)
        cmd.angular.z = float(self.get_parameter("search_angular_speed").value)
        self.cmd_pub.publish(cmd)

    def _publish_stop(self) -> None:
        self.cmd_pub.publish(Twist())

    def _publish_state(self) -> None:
        msg = String()
        if self.target_object:
            msg.data = f"{self.state.value}:{self.target_object}"
        else:
            msg.data = self.state.value
        self.status_pub.publish(msg)

    def _publish_arm(self, values: list[float]) -> None:
        msg = Float64MultiArray()
        msg.data = values
        self.arm_pub.publish(msg)

        if len(values) >= 4:
            joint1 = Float64()
            joint1.data = values[1]
            joint2 = Float64()
            joint2.data = values[2]
            gripper = Float64()
            gripper.data = values[3]
            self.joint1_pub.publish(joint1)
            self.joint2_pub.publish(joint2)
            self.gripper_pub.publish(gripper)

    def _parameter_list(self, name: str) -> list[float]:
        return [float(value) for value in self.get_parameter(name).value]


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = StateMachine()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
