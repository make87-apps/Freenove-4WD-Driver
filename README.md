# Freenove 4WD Platform Driver

This application serves as a driver for the **Freenove 4WD Smart Car Kit** for Raspberry Pi, as
listed [here on Amazon](https://www.amazon.com/Freenove-Raspberry-Tracking-Avoidance-Ultrasonic/dp/B07YD2LT9D). It is
designed to control the vehicle's motors, camera, and servos via the **make87 platform**. The application enables remote
operation through message-based commands and real-time camera streaming.

---

## Functionality Overview

1. **Vehicle Drive Control**:
    - Drive the vehicle in multiple directions (`FORWARD`, `BACKWARD`, `LEFT`, `RIGHT`) or stop it.
    - Commands are sent as text messages to the `SET_DRIVE_INSTRUCTION` endpoint.

2. **Camera Control**:
    - Adjust the **pitch** (up/down) and **yaw** (left/right) angles of the vehicle's camera by sending messages to
      dedicated endpoints.
    - Camera pitch range: **50°–110°**.
    - Camera yaw range: **80°–150°**.

3. **Camera Image Streaming**:
    - Publishes real-time images captured from the vehicle's camera to the `IMAGE` topic.
    - Images are encoded in JPEG format.

---

## Topics and Endpoints

### **1. Drive Instructions**

- **Endpoint**: `SET_DRIVE_INSTRUCTION`
- **Message Type**: `PlainText`
- **Description**: Controls the vehicle's movement.

| Instruction | Description                |
|-------------|----------------------------|
| `FORWARD`   | Move the vehicle forward.  |
| `BACKWARD`  | Move the vehicle backward. |
| `LEFT`      | Turn the vehicle left.     |
| `RIGHT`     | Turn the vehicle right.    |
| `STOP`      | Stop the vehicle.          |

---

### **2. Set Camera Pitch**

- **Endpoint**: `SET_CAMERA_PITCH`
- **Message Type**: `PlainText`
- **Description**: Sets the pitch (up/down angle) of the camera.

| Input Value | Action                       |
|-------------|------------------------------|
| `50`–`110`  | Sets pitch angle in degrees. |

If the value is out of range, it will be clipped to the nearest valid value (50 or 110).

---

### **3. Set Camera Yaw**

- **Endpoint**: `SET_CAMERA_YAW`
- **Message Type**: `PlainText`
- **Description**: Sets the yaw (left/right angle) of the camera.

| Input Value | Action                     |
|-------------|----------------------------|
| `80`–`150`  | Sets yaw angle in degrees. |

If the value is out of range, it will be clipped to the nearest valid value (80 or 150).

---

### **4. Camera Image Streaming**

- **Topic**: `IMAGE`
- **Message Type**: `ImageJPEG`
- **Description**: Streams real-time JPEG-encoded images captured from the vehicle's camera.

The platform automatically resolves the camera peripheral for capturing images.

---

## Summary of Messages

| Feature                | Endpoint/Topic          | Message Type | Payload                                        |
|------------------------|-------------------------|--------------|------------------------------------------------|
| Drive Control          | `SET_DRIVE_INSTRUCTION` | `PlainText`  | `FORWARD`, `BACKWARD`, `LEFT`, `RIGHT`, `STOP` |
| Set Camera Pitch       | `SET_CAMERA_PITCH`      | `PlainText`  | Angle (50–110)                                 |
| Set Camera Yaw         | `SET_CAMERA_YAW`        | `PlainText`  | Angle (80–150)                                 |
| Camera Image Streaming | `IMAGE`                 | `ImageJPEG`  | JPEG-encoded image                             |

---

## About the Freenove 4WD Smart Car Kit

The Freenove 4WD Smart Car Kit is a versatile and educational robotic platform designed for use with Raspberry Pi. It
features:

- Four motors for omnidirectional movement.
- A camera module for real-time video streaming and tracking.
- Servo motors for controlling the camera's pitch and yaw.

This application integrates seamlessly with the Freenove kit, enabling remote control and real-time monitoring via the
make87 platform.
