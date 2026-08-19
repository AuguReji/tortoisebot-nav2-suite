# TortoiseBot Nav2 Suite

![ROS2](https://img.shields.io/badge/ROS2-Humble-blue?logo=ros&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04-E95420?logo=ubuntu&logoColor=white)
![Gazebo](https://img.shields.io/badge/Gazebo-Classic-orange?logo=gazebo&logoColor=white)
![Nav2](https://img.shields.io/badge/Nav2-Enabled-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A structured, task-by-task build-up of a differential drive robot (**TortoiseBot**) in ROS 2 Humble — from basic teleop simulation through LIDAR-based sensing, depth camera fusion, SLAM mapping, Nav2 autonomous navigation, multi-waypoint routing, and zig-zag area coverage.

Each task is self-contained but builds on the URDF, Gazebo world, and navigation stack from the previous one.

---

## 📦 Repository Structure

```
tortoisebot-nav2-suite/
├── tortoisebot_description/   # URDF, RViz config (Task 1)
├── tortoisebot_gazebo/        # Worlds, sensor plugins, Gazebo launch (Tasks 1–5)
├── tortoisebot_nav/           # Nav2 configs, waypoint & zig-zag nodes (Tasks 6–8)
├── docs/                      # Per-task writeups + simulation video links
└── README.md
```

---

## 🧭 Task Index

| Task | Title | Difficulty | Status |
|------|-------|------------|--------|
| [1](docs/task1.md) | Simulate TortoiseBot in Gazebo + Teleop Control | Easy | ✅️ |
| [2](docs/task2.md) | Get Object Distance from LIDAR (filtered) | Easy | ✅️ |
| [3](docs/task3.md) | Follow a Ball Using LIDAR Only | Easy |  ✅️  |
| [4](docs/task4.md) | Map a Custom World with Obstacles | Medium | ⬜ |
| [5](docs/task5.md) | Fuse 2D LIDAR + Depth Camera → 3D Point Cloud | Medium | ⬜ |
| [6](docs/task6.md) | Autonomous Navigation with Nav2 + RViz | Medium | ⬜ |
| [7](docs/task7.md) | Multi-Waypoint Navigation with Timed Pit Stops | Medium | ⬜ |
| [8](docs/task8.md) | Zig-Zag Area Coverage (Cleaning Pattern) | Medium | ⬜ |

---

## 🛠️ Tools & Stack

- **ROS 2 Humble** on **Ubuntu 22.04**
- **Gazebo Classic** for simulation
- **Nav2** (`nav2_bringup`, `map_server`, `amcl`, `bt_navigator`)
- **RViz2** for visualization/debugging
- `teleop_twist_keyboard`, `pointcloud_to_laserscan`, `depth_image_proc`
- SLAM Toolbox (mapping)

---

## 🚀 Setup

```bash
# Clone into your workspace
cd ~/ros2_ws/src
git clone https://github.com/AuguReji/tortoisebot-nav2-suite.git

# Build
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

Each package's own README (or the relevant `docs/taskN.md`) has task-specific launch instructions.

---

## 📄 Per-Task Documentation

Every task folder in `docs/` follows the same format:
- Task statement
- Step-by-step approach
- Tools used
- Challenges solved
- Final result
- Gazebo simulation video link

---

## 📌 Notes

This repo is part of an ongoing robotics skills build-up (ROS 2, Nav2, SLAM, sensor fusion) alongside a separate hexapod firmware project. Commits are made incrementally per task to avoid data loss.

---
