# Rover-Arm Simulation

A ROS 2 simulation environment where a robot arm rover can interact with different shapes in a Gazebo physics environment, including cubes, spheres, and pyramids.

## Overview

This project simulates a robotic rover equipped with an arm that can perceive and manipulate objects in a virtual environment. The rover uses camera-based object detection and can be controlled manually or autonomously to interact with objects in the simulation.

## System Requirements

- **OS**: Ubuntu 26.04
- **ROS 2**: Lyrical Luth
- **Simulation**: Gazebo (installed and configured)
- **Workspace**: ROS 2 workspace folder (recommended name: `ros2_ws`) with an `src` subdirectory

## Setup Instructions

### Initial Setup

```bash
# Navigate to your workspace
cd ros2_ws

# Source ROS 2 environment
source /opt/ros/lyrical/setup.bash

# Source your workspace setup
source install/setup.bash

# Build the rover_arm package
colcon build --packages-select rover_arm

# Source the updated environment
source /opt/ros/lyrical/setup.bash
```

### Launch the Simulation

```bash
# Start the rover arm simulation
ros2 launch rover_arm rover_arm.launch.py
```

## Manual Control (Optional)

To control the rover using WASD keyboard commands:

```bash
source ~/ros2_ws/install/setup.bash
ros2 run rover_arm teleop_node
```

Then use keyboard commands in the teleop terminal to move the robot.

## Monitoring Topics

After sourcing your workspace, you can monitor the following ROS 2 topics:

```bash
source ~/ros2_ws/install/setup.bash

# View current rover state
ros2 topic echo /rover_arm/state

# View camera feed
ros2 topic echo /camera/image_raw --no-arr

# View detected objects
ros2 topic echo /rover_arm/detected_object

# List all available topics
ros2 topic list
```

## How It Works

1. **Simulation Environment**: Gazebo provides a physics-based 3D environment where the rover arm can move and interact with objects.

2. **Perception**: A simulated camera on the rover captures images of the environment. Object detection algorithms process these images to identify shapes (cubes, spheres, pyramids) and their positions.

3. **Control**: The rover can be controlled through:
   - Manual keyboard input via the teleop node
   - Autonomous behaviors defined in the rover logic

4. **Interaction**: The rover arm reaches toward detected objects and can manipulate them based on the control commands.

5. **Monitoring**: ROS 2 topics provide real-time feedback on the rover's state, camera input, and detected objects for debugging and development.
