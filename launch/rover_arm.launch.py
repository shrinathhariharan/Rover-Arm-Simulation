import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    pkg_share = get_package_share_directory("rover_arm")
    pkg_ros_gz_sim = get_package_share_directory("ros_gz_sim")

    world_path = os.path.join(pkg_share, "worlds", "rover_world.sdf")
    params_path = os.path.join(pkg_share, "config", "params.yaml")

    use_sim_time = LaunchConfiguration("use_sim_time")
    gz_args = LaunchConfiguration("gz_args")
    target_color = LaunchConfiguration("target_color")
    gazebo_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=os.path.join(pkg_share, "models"),
    )
    # Force dzn (D3D12) Vulkan backend to use the Intel GPU on WSL
    mesa_d3d12_adapter = SetEnvironmentVariable(
        name="MESA_D3D12_DEFAULT_ADAPTER_NAME",
        value="Intel",
    )
    # Use llvmpipe (software Vulkan) to avoid dzn conformance issues on WSL
    # llvmpipe is conformant and supports all required extensions for Ogre2 Vulkan
    vk_icd_filenames = SetEnvironmentVariable(
        name="VK_ICD_FILENAMES",
        value="/usr/share/vulkan/icd.d/lvp_icd.x86_64.json",
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={
            "gz_args": gz_args,
            "on_exit_shutdown": "true",
        }.items(),
    )

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="rover_arm_bridge",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}],
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",
            "/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry",
            "/rover/joint1_position@std_msgs/msg/Float64]gz.msgs.Double",
            "/rover/joint2_position@std_msgs/msg/Float64]gz.msgs.Double",
            "/rover/gripper_position@std_msgs/msg/Float64]gz.msgs.Double",
            "/camera@sensor_msgs/msg/Image[gz.msgs.Image",
        ],
        remappings=[
            ("/odometry", "/odom"),
            ("/camera", "/camera/image_raw"),
        ],
    )

    common_params = [params_path, {"use_sim_time": use_sim_time}]

    motion_controller = Node(
        package="rover_arm",
        executable="motion_controller",
        name="motion_controller",
        output="screen",
        parameters=common_params,
    )

    object_detector = Node(
        package="rover_arm",
        executable="object_detector",
        name="object_detector",
        output="screen",
        parameters=[params_path, {"use_sim_time": use_sim_time, "target_color": target_color}],
    )

    state_machine = Node(
        package="rover_arm",
        executable="state_machine",
        name="state_machine",
        output="screen",
        parameters=common_params,
    )

    telemetry = Node(
        package="rover_arm",
        executable="telemetry",
        name="telemetry",
        output="screen",
        parameters=common_params,
    )

    cmd_vel_mux = Node(
        package="rover_arm",
        executable="cmd_vel_mux",
        name="cmd_vel_mux",
        output="screen",
        parameters=common_params,
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
            description="Use simulation clock if true",
        ),
        DeclareLaunchArgument(
            "target_color",
            default_value="red",
            description="Object color to search for: red, green, or purple",
        ),
        DeclareLaunchArgument(
            "gz_args",
            default_value=f"-r {world_path} --render-engine-api-backend vulkan",
            description="Gazebo Sim arguments",
        ),
        gazebo_resource_path,
        mesa_d3d12_adapter,
        vk_icd_filenames,
        gazebo,
        bridge,
        motion_controller,
        object_detector,
        state_machine,
        telemetry,
        cmd_vel_mux,
    ])
