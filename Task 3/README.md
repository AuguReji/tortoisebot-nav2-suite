# Task 3: Follow a Ball Using Gazebo LIDAR and the Same TortoiseBot URDF

**Difficulty:** Easy
**Status:** 🚧 In Progress

---

## 📋 Task Statement

Using the same TortoiseBot URDF and LIDAR setup from previous tasks, simulate a ball-shaped object in front of the robot inside the Gazebo world. Write a ROS2 node to process LIDAR data from `/scan` and detect the direction and distance to the closest object (the ball). Based on that, publish velocity commands to `/cmd_vel` to make the robot follow the ball slowly by aligning itself and moving forward when the object is centered. LIDAR data only — no cameras.

---

## 🪜 Step-by-Step Approach

1. **Reused the existing LIDAR** (added in Task 2) rather than adding a second sensor
   - Increased `range_max` in the sensor config so the ball can be detected further away, especially useful once it's moving fast

2. **Added a ball to the simulation**
   - Initially spawned via a standalone `ball.sdf` + `spawn_entity.py` in the launch file
   - Switched approach: inserted a dynamic sphere (`unit_sphere`) directly in the Gazebo GUI (Insert tool) and saved the world, baking it into `empty_world.world` — removed the automated spawn step from the launch file accordingly, since there's nothing left to spawn at launch time
   - Ball is manually repositioned/pushed via the GUI each run rather than fixed at a scripted starting pose, to allow flexible speed/distance testing

3. **Wrote the detection node** (`ball_lidar_dis.py`, renamed from the earlier shared `lidar_dis.py`)
   - Searches the **entire** `/scan` array (no fixed front-facing cone) to find the true globally closest valid point — this is what gives 360° detection instead of only tracking objects already in front
   - Applies a **spatial** median filter (same technique as Task 2's `closest_object_distance.py`) in a small angular window centered on wherever that closest point actually is, to reject single-ray spikes
   - Deliberately does **not** keep any history across scans — every message is processed independently, replacing an earlier temporal moving-average approach that smoothed values across the last 5 scans

4. **Wrote the controller node** (`ball_follower.py`)
   - Proportional angular control steers toward the object's bearing (REP103 sign convention: positive angle = object to the left = positive `angular.z`)
   - Proportional linear control with a **quadratic deceleration taper** close to the stop distance, and a much higher speed ceiling further out — needed so the robot can actually keep pace with a ball that's moving, not just crawl at a fixed slow speed regardless of distance
   - Loosened the "must be aligned before moving" gate so the robot starts advancing sooner instead of spending time purely rotating in place while a moving ball pulls further away
   - A watchdog timer stops the robot if the object hasn't been seen for over a second (lost from `/scan` entirely)

5. **Wrote `ball_follow.launch.py`** to bring up Gazebo, spawn the robot, and start both new nodes together

6. **Updated `setup.py`** entry points to match the `ball_lidar_dis.py` rename, and to register `ball_follower`

---

## 🛠️ Tools Used

- ROS 2 Humble
- Gazebo Classic 11 (`libgazebo_ros_ray_sensor.so`, Insert/Translate GUI tools)
- `rclpy`
- `sensor_msgs/LaserScan`, `std_msgs/Float32MultiArray`, `geometry_msgs/Twist`
- Python `statistics.median`

---

## 🧩 Challenges Solved

- **Front-only detection was too limiting** — the original `±15°` cone (correct for Task 2) meant the robot could only react to the ball if it was already roughly in front. Rewrote detection to search the full scan for the true nearest point in any direction.
- **Temporal smoothing vs. spatial smoothing** — the first version of the detection node reduced noise by averaging the closest distance/angle across the last 5 scans (memory across messages). Replaced with Task 2's spatial-median approach instead: filter within a single scan, centered on wherever the closest point is found, so detection has no lag from stale history and works identically well anywhere in the 360° sweep.
- **Speed too low to track a moving ball** — an early version capped forward speed at a fairly low value and required near-perfect alignment before allowing any forward motion at all, so a ball moving away would out-pace the robot before it finished turning. Fixed with a continuous proportional speed curve (quadratic taper only very close to the stop point, otherwise scaling with distance up to a much higher cap) and a looser alignment gate that lets the robot steer and drive forward at the same time.
- **Velocity discontinuity risk** — an intermediate two-zone design (constant "chase" speed beyond a threshold, proportional taper below it) risked a sudden jump in commanded speed right at the zone boundary. The final single-formula version avoids this: the quadratic-taper and linear-scaling branches evaluate to the same value at their boundary, so there's no discontinuity.
- **World file became a GUI-saved snapshot** — inserting the ball via Gazebo's GUI and saving the world replaced the original hand-written `empty_world.world` with an auto-generated one containing `<state>`/`<gui>` blocks and the ball's last-saved pose. Noted as a deliberate tradeoff: the ball's starting position isn't scripted/reproducible run-to-run, since it's now placed manually each time for flexible speed testing.
- **Renamed module without updating the entry point** — `lidar_dis.py` → `ball_lidar_dis.py` needed a matching update in `setup.py`'s `console_scripts`, otherwise `ros2 run`/the launch file can't find the renamed executable.

---

## ✅ Final Result

*(Pending final verification run with a fast-moving ball — update once confirmed working end-to-end, including behavior when the ball is deliberately pushed away quickly.)*

---

## 📂 Package Structure

```
tortoisebot_description/
└── urdf/
    └── tortoisebot.urdf.xacro     

tortoisebot_gazebo/                  
├── worlds/
│   └── empty_world.world             
├── launch/
│   └── ball_follow.launch.py       
└── tortoisebot_gazebo/
    ├── ball_lidar_dis.py       
    └── ball_follower.py             
```
