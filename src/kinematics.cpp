#include "rover_arm/kinematics.hpp"

#include <algorithm>
#include <cmath>

namespace RoverArm
{

std::optional<JointAngles> solvePlanarIk(
  const double x,
  const double z,
  const double link1,
  const double link2)
{
  if (link1 <= 0.0 || link2 <= 0.0) {
    return std::nullopt;
  }

  const double distanceSq{x * x + z * z};
  const double maxReach{link1 + link2};
  const double minReach{std::abs(link1 - link2)};
  const double distance{std::sqrt(distanceSq)};
  if (distance > maxReach || distance < minReach) {
    return std::nullopt;
  }

  const double cosElbowRaw{
    (distanceSq - link1 * link1 - link2 * link2) / (2.0 * link1 * link2)};
  const double cosElbow{std::clamp(cosElbowRaw, -1.0, 1.0)};
  const double elbow{-std::acos(cosElbow)};

  const double k1{link1 + link2 * std::cos(elbow)};
  const double k2{link2 * std::sin(elbow)};
  const double shoulder{std::atan2(z, x) - std::atan2(k2, k1)};

  return JointAngles{shoulder, elbow};
}

std::array<double, 2> forwardPlanar(
  const double shoulder,
  const double elbow,
  const double link1,
  const double link2)
{
  return {
    link1 * std::cos(shoulder) + link2 * std::cos(shoulder + elbow),
    link1 * std::sin(shoulder) + link2 * std::sin(shoulder + elbow),
  };
}

}  // namespace RoverArm
