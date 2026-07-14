#ifndef ROVER_ARM__KINEMATICS_HPP_
#define ROVER_ARM__KINEMATICS_HPP_

#include <array>
#include <optional>

namespace RoverArm
{

struct JointAngles
{
  double shoulder;
  double elbow;
};

std::optional<JointAngles> solvePlanarIk(
  double x,
  double z,
  double link1,
  double link2);

std::array<double, 2> forwardPlanar(
  double shoulder,
  double elbow,
  double link1,
  double link2);

}  // namespace RoverArm

#endif
