# Rover-Arm-Simulation
A plane where a robot can interact with different shapes including a square, sphere, and pyramid

# Items Needed
Running 26.04 Ubuntu Terminal
Running ros2 lyrical luth
A ROS 2 workspace folder (preferably named ros2_ws) with an 'src' folder inside


# Setup (Put in Terminal)
sudo apt install ros-lyrical-ros-gz #install gazebo simulation

cd ~/ros2_ws

colcon build --packages-select rover_arm
source /opt/ros/lyrical/setup.bash #build the workspace

source ~/ros2_ws/install/setup.bash
ros2 launch rover_arm rover_arm.launch.py #launch simulation

# Optional Manual Teleop:
#If wanting to use WASD to control the robot
source ~/ros2_ws/install/setup.bash
ros2 run rover_arm teleop_node #Do commands inside the teleop terminal to move the robot


# Extra Monitoring Commands
source ~/ros2_ws/install/setup.bash
#Current behavior state
ros2 topic echo /rover_arm/state
#What the camera sees
ros2 topic echo /camera/image_raw --no-arr
#Detected object
ros2 topic echo /rover_arm/detected_object
#List all topics
ros2 topic list