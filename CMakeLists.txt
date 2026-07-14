cmake_minimum_required(VERSION 3.20)
project(rover_arm)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)

add_library(kinematics src/kinematics.cpp)
target_include_directories(kinematics PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

add_executable(motion_controller src/motion_controller.cpp)
target_link_libraries(motion_controller PUBLIC
  rclcpp::rclcpp
  geometry_msgs::geometry_msgs
  nav_msgs::nav_msgs
  std_msgs::std_msgs
  kinematics
)

install(TARGETS
  kinematics
  motion_controller
  EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
  DESTINATION include
)

install(PROGRAMS rover_arm/teleop_node.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME teleop_node
)

install(PROGRAMS rover_arm/state_machine.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME state_machine
)

install(PROGRAMS rover_arm/object_detector.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME object_detector
)

install(PROGRAMS rover_arm/telemetry.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME telemetry
)

install(PROGRAMS rover_arm/cmd_vel_mux.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME cmd_vel_mux
)

install(DIRECTORY launch config worlds models
  DESTINATION share/${PROJECT_NAME}
)

ament_python_install_package(${PROJECT_NAME}
  SCRIPTS_DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_export_targets(export_${PROJECT_NAME} HAS_LIBRARY_TARGET)
ament_export_include_directories(include)
ament_package()
