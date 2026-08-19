# Task 2: Get Object Distance from Gazebo LIDAR using ROS2 Filters

**Difficulty:** Easy
**Status:** ✅ Completed

---

## 📋 Task Statement

Using the LIDAR plugin in your Gazebo-based TortoiseBot simulation, subscribe to the `/scan` topic and write a ROS2 node to process the `LaserScan` data. Apply filters to extract the closest object distance directly in front of the robot (e.g., within ±15° field of view). The node should ignore invalid ranges (`inf`, `nan`, or zero), focus only on scan angles between -15° to +15°, filter out spikes using a median/moving average/minimum valid value, and publish the filtered distance to a topic like `/closest_object_distance`.

---

## 🪜 Step-by-Step Approach

1. **Add a LIDAR sensor to the URDF** (not yet present after Task 1)
   - New `lidar_link` (cylinder) fixed to `base_link`, mounted flush and centered on the chassis roof
   - Added `<sensor type="ray">` + `libgazebo_ros_ray_sensor.so` plugin, remapped to `/scan`, full 360° sweep, 360 samples, range `0.12m`–`3.5m`, `10Hz`
   - Went with a full 360° sweep now rather than a narrow front slice, since Tasks 3 and 4 reuse this same sensor for ball-following and obstacle mapping

2. **Write the filtering node** (`closest_object_distance.py`, rclpy, inside the existing `tortoisebot_gazebo` package)
   - Subscribes to `/scan`
   - Computes the front ±15° index window from the message's own `angle_min`/`angle_increment` at runtime (not hardcoded indices), so it stays correct if the sensor's resolution or range ever changes
   - Discards `inf`, `nan`, and any reading at or below `range_min` (covers the "zero" case too)
   - Applies a median filter across the remaining valid readings in the window to reject single-ray spikes
   - Publishes the result as `std_msgs/Float32` to `/closest_object_distance`

3. **Verify**
   - Confirmed `/scan` publishes correctly (360 samples, correct `frame_id`, all `.inf` in the empty world as expected with nothing in range)
   - Confirmed `/closest_object_distance` publishes stable, tightly-clustered values matching a real object placed in front of the robot

---

## 🛠️ Tools Used

- ROS 2 Humble
- Gazebo Classic 11 (`libgazebo_ros_ray_sensor.so`)
- `rclpy`
- `sensor_msgs/LaserScan`, `std_msgs/Float32`
- Python `statistics.median`

---

## 🧩 Challenges Solved

- **LIDAR link had no joint** — the link was defined but never attached to `base_link`, which would have made the URDF an invalid disconnected tree. Added a fixed joint mounting it flush on the chassis roof.
- **Missing Gazebo sensor block entirely** — the link existed but had no `<sensor>`/`<plugin>` definition, so nothing would have published to `/scan` at all.
- **Wrong inertia formula copied from the caster** — the LIDAR cylinder had been given the caster's *sphere* inertia formula instead of the correct cylinder formula (same class of bug caught earlier on the wheels).
- **Geometry/inertia value mismatch** — the visual cylinder used its own radius while the inertia calculation reused an unrelated property (`caster_radius`). Fixed by introducing dedicated `lidar_radius`/`lidar_length`/`lidar_mass` properties feeding both.
- **FOV index math** — computed the ±15° window boundaries from `angle_min`/`angle_increment` dynamically rather than assuming fixed array indices, verified against the robot's actual published scan parameters (`angle_increment ≈ 0.0175 rad` → ~30-sample window, `-14.5°` to `+14.5°`, matching the requested ±15° within the sensor's angular resolution).

---

## ✅ Final Result

`/closest_object_distance` publishes stable `Float32` values (observed ~0.46m, tightly clustered within ~0.02m of noise) matching a real object placed in front of the robot in Gazebo. All-`.inf` scans in an empty world correctly produce no output (logged, not published), confirming the invalid-range filtering works as well as the positive-detection case.

---

## 🎥 Gazebo Simulation Video

https://workdrive.zohoexternal.in/file/vqewi3dce7d7157b14478ba35905fe0f5aaa9

---

## 🔧 Shared / Utility Nodes

Some nodes are reused across multiple tasks rather than belonging to a single one:

| Node | Publishes | Used By | Description |
|------|-----------|---------|--------------|
| `closest_object_distance.py` | `/closest_object_distance` (Float32) | Task 2 | Median-filtered closest-object distance in front ±15° FOV |
| `lidar_dis.py` | `/closest_object_info` (Float32MultiArray: [distance, angle_deg]) | Task 2 (extended), Task 3 | Closest object's distance *and* angle within ±15° FOV, moving-average filtered over the last 5 scans — the angle output is what makes ball-following (Task 3) possible |

## 📂 Package Structure

```
tortoisebot_description/
└── urdf/
    └── tortoisebot.urdf.xacro        (lidar_link + sensor plugin added)

tortoisebot_gazebo/                    (ament_python)
└── tortoisebot_gazebo/
    ├── __init__.py
    ├── closest_object_distance.py     # Task 2
    └── lidar_dis.py                   # Task 2/3 shared utility
```
