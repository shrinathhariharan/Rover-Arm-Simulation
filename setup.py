from setuptools import find_packages, setup

package_name = "rover_arm"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="shrin",
    maintainer_email="shrin@todo.todo",
    description="Rover arm simulation nodes for color detection and pick behavior.",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "teleop_node = rover_arm.teleop_node:main",
            "state_machine = rover_arm.state_machine:main",
            "object_detector = rover_arm.object_detector:main",
            "telemetry = rover_arm.telemetry:main",
            "cmd_vel_mux = rover_arm.cmd_vel_mux:main",
        ],
    },
)
