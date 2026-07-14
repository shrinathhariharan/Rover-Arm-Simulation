#include <algorithm>
#include <chrono>
#include <cmath>
#include <functional>
#include <memory>
#include <string>

#include "geometry_msgs/msg/point.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

class MotionController : public rclcpp::Node
{
public:
  MotionController()
  : Node("motion_controller")
  {
    linear_gain_ = declare_parameter("approach_linear_gain", 0.55);
    angular_gain_ = declare_parameter("approach_angular_gain", 1.8);
    max_linear_ = declare_parameter("max_linear_speed", 0.35);
    max_angular_ = declare_parameter("max_angular_speed", 0.9);
    pickup_distance_ = declare_parameter("pickup_distance_m", 0.45);

    cmd_pub_ = create_publisher<geometry_msgs::msg::Twist>("/cmd_vel_auto", 10);
    status_pub_ = create_publisher<std_msgs::msg::String>("/rover_arm/motion_status", 10);
    odom_sub_ = create_subscription<nav_msgs::msg::Odometry>(
      "/odom", 10,
      [this](nav_msgs::msg::Odometry::SharedPtr msg) {
        odom_ = *msg;
        have_odom_ = true;
      });
    target_sub_ = create_subscription<geometry_msgs::msg::Point>(
      "/rover_arm/target_point", 10,
      [this](geometry_msgs::msg::Point::SharedPtr msg) {
        target_x_ = msg->x;
        target_y_ = msg->y;
        have_target_ = true;
      });
    timer_ = create_wall_timer(
      std::chrono::milliseconds(50),
      std::bind(&MotionController::controlLoop, this));
  }

private:
  void controlLoop()
  {
    geometry_msgs::msg::Twist cmd{};
    std_msgs::msg::String status{};

    if (!have_odom_ || !have_target_) {
      status.data = "IDLE";
      status_pub_->publish(status);
      cmd_pub_->publish(cmd);
      return;
    }

    const auto & pose{odom_.pose.pose};
    const double dx{target_x_ - pose.position.x};
    const double dy{target_y_ - pose.position.y};
    const double distance{std::hypot(dx, dy)};
    const double yaw{yawFromQuaternion(
        pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w)};
    const double bearing{std::atan2(dy, dx)};
    const double heading_error{normalizeAngle(bearing - yaw)};

    if (distance <= pickup_distance_) {
      status.data = "ARRIVED";
      have_target_ = false;
    } else {
      cmd.linear.x = std::clamp(linear_gain_ * (distance - pickup_distance_), 0.0, max_linear_);
      cmd.angular.z = std::clamp(angular_gain_ * heading_error, -max_angular_, max_angular_);
      status.data = "APPROACHING";
    }

    cmd_pub_->publish(cmd);
    status_pub_->publish(status);
  }

  static double yawFromQuaternion(const double x, const double y, const double z, const double w)
  {
    const double siny_cosp{2.0 * (w * z + x * y)};
    const double cosy_cosp{1.0 - 2.0 * (y * y + z * z)};
    return std::atan2(siny_cosp, cosy_cosp);
  }

  static double normalizeAngle(double angle)
  {
    while (angle > M_PI) {
      angle -= 2.0 * M_PI;
    }
    while (angle < -M_PI) {
      angle += 2.0 * M_PI;
    }
    return angle;
  }

  bool have_odom_{false};
  bool have_target_{false};
  double target_x_{0.0};
  double target_y_{0.0};
  double linear_gain_{0.55};
  double angular_gain_{1.8};
  double max_linear_{0.35};
  double max_angular_{0.9};
  double pickup_distance_{0.45};
  nav_msgs::msg::Odometry odom_;

  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_pub_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr status_pub_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
  rclcpp::Subscription<geometry_msgs::msg::Point>::SharedPtr target_sub_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MotionController>());
  rclcpp::shutdown();
  return 0;
}
