# Task 1: Simulate TortoiseBot in Gazebo and Control with Teleop

**Difficulty:** Easy
**Status:** ✅ Completed

---

## 📋 Task Statement

Create a `tortoisebot_description` package to load and visualize the robot in RViz, then build a separate `tortoisebot_gazebo` package with an `empty_world.world` to spawn the robot in Gazebo, integrate velocity command plugins (`/cmd_vel`), and control the robot using the `teleop_twist_keyboard` package to verify movement in the simulated environment.

---

## 🪜 Step-by-Step Approach

1. **Create `tortoisebot_description` package**
   - Defined robot links/joints in `tortoisebot.urdf.xacro` (differential drive: `base_footprint`, `base_link`, `left_wheel`, `right_wheel`, `caster_wheel`)
   - Used `xacro:property` values throughout (dimensions, masses, offsets) so geometry, ground-contact math, and inertia all stay consistent if any single value is tuned later
   - Wrote `rviz.launch.py` with a `standalone` launch argument so it can run alone (own `robot_state_publisher` + `joint_state_publisher_gui`) or be included from another launch file without duplicating nodes
   - Built a minimal `tortoisebot.rviz` config with `RobotModel` + `TF` displays

2. **Create `tortoisebot_gazebo` package**
   - Added `empty_world.world` (SDF, `sun` + `ground_plane` includes)
   - Wrote `spawn.launch.py`: launches Gazebo via `ExecuteProcess` with `libgazebo_ros_init.so` / `libgazebo_ros_factory.so`, starts `robot_state_publisher`, spawns via `spawn_entity.py -topic robot_description`, and includes `rviz.launch.py` (`standalone:=false`) so one command brings up the whole stack
   - Added `libgazebo_ros_diff_drive.so` and `libgazebo_ros_joint_state_publisher.so` plugins to the URDF for `/cmd_vel` support and real joint-state publishing

3. **Verify simulation**
   - Confirmed `/cmd_vel` is active and wheel joints respond once all install/dependency issues (below) were resolved

4. **Teleop control**
   - Ran `teleop_twist_keyboard`, confirmed forward/backward/turning all work correctly in Gazebo
   - Tuned default speed down from teleop's defaults (0.5 m/s / 1.0 rad/s) to roughly 0.15 m/s / 0.5–0.6 rad/s, since the defaults are scaled for full-size robots and made this small chassis (0.3m long) feel too fast/twitchy to control precisely

---

## 🛠️ Tools Used

- ROS 2 Humble
- Gazebo Classic 11
- `xacro` / URDF
- `robot_state_publisher`, `joint_state_publisher_gui`
- `gazebo_ros` plugins (`diff_drive`, `joint_state_publisher`, `ros_init`, `ros_factory`)
- `teleop_twist_keyboard`
- RViz2

---

## 🧩 Challenges Solved

- **URDF syntax bugs** — Cyrillic characters typo'd into `rpy` (`rру`), a stray space inside `wheel_separation`/`publish_wheel_joint_state` opening tags that broke SDF parsing, and 0–255 scale colors used where URDF expects normalized 0–1 `rgba`.
- **Wheel diameter/plugin mismatch** — the visual/collision cylinder radius and the `diff_drive` plugin's `<wheel_diameter>` were hardcoded separately and drifted out of sync, which would have thrown off odometry. Fixed by driving both from a single `xacro:property`.
- **Ground-contact math** — wheel and caster z-offsets were hardcoded and broke every time chassis dimensions changed. Replaced with a `radius - base_z_offset` formula so ground contact self-corrects regardless of future resizing.
- **Caster/chassis collision overlap** — after shrinking the chassis, the caster sphere ended up geometrically embedded ~1.8cm inside the `base_link` box collision volume. Not fatal (fixed joints get lumped into one rigid body by Gazebo's SDF conversion), but fixed by raising `base_z_offset` so the caster clears the box with a small gap.
- **Gazebo material reference typo** — used `references="..."` (invalid attribute) instead of `reference="..."`, which silently no-ops; also swapped `Gazebo/Pink` and `Gazebo/Silver` for valid default material names (`Gazebo/Purple`, `Gazebo/Grey`) since the originals aren't in Gazebo Classic's default material script library.
- **`ament_python` install bug** — `tortoisebot_gazebo/setup.py`'s `data_files` entry for `launch/` was a malformed 3-element tuple with an unexpanded glob string, so `colcon build` never installed the launch file. Fixed using `glob()` and correct `(dest, [files])` tuples, and added a matching entry for `worlds/`.
- **`xacro` module not found at runtime** — raw `.xacro` files were being read as plain text and handed to `robot_state_publisher` instead of being processed; also needed `ros-humble-xacro` installed system-wide (separate from a cosmetic VS Code/Pylance import warning, which was a red herring).
- **Missing `gazebo_ros` package** — `libgazebo_ros_init.so` / `libgazebo_ros_factory.so` failed to load because `ros-humble-gazebo-ros-pkgs` wasn't installed; installing it resolved all four plugin errors at once (`diff_drive`, `joint_state_publisher`, `ros_init`, `ros_factory` all live in the same package).
- **TF tree conflict** — `robot_base_frame` in the `diff_drive` plugin was set to `base_link`, but `base_footprint` already parents `base_link` via a fixed joint in the URDF. Two frames claiming the same child broke the TF tree (RViz: "No transform from [base_footprint] to [odom]"). Fixed by pointing `robot_base_frame` at `base_footprint` instead, giving a single continuous chain (`odom → base_footprint → base_link → wheels/caster`) — also the convention Nav2 expects in later tasks.

---

## ✅ Final Result

Robot spawns correctly in Gazebo sitting flush on the ground plane (no floating, no visible collision overlap). RViz's `RobotModel` display shows all TF transforms OK. `teleop_twist_keyboard` drives the robot forward/backward and turns it as expected via `/cmd_vel`, with wheel joints visibly rotating in both Gazebo and RViz. Default teleop speed was reduced from ~0.5 m/s to ~0.15 m/s for controllability at this robot's scale.

---

## 🎥 Gazebo Simulation Video

https://workdrive.zohoexternal.in/file/vqewi4caa4b5c2c9c48379ccac7b49629b714

---

## 📂 Package Structure

```
tortoisebot_description/          (ament_cmake)
├── urdf/
│   └── tortoisebot.urdf.xacro
├── launch/
│   └── rviz.launch.py
├── config/
│   └── tortoisebot.rviz
├── CMakeLists.txt
└── package.xml

tortoisebot_gazebo/                (ament_python)
├── worlds/
│   └── empty_world.world
├── launch/
│   └── spawn.launch.py
├── resource/
│   └── tortoisebot_gazebo
├── tortoisebot_gazebo/
│   └── __init__.py
├── test/
│   ├── test_copyright.py
│   ├── test_flake8.py
│   └── test_pep257.py
├── setup.py
├── setup.cfg
└── package.xml
```
