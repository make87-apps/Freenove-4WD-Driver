# Freenove 4WD Smart Car Kit Driver for make87

This application is a driver for the **Freenove 4WD Smart Car Kit** (as
listed [here on Amazon](https://www.amazon.com/Freenove-Raspberry-Tracking-Avoidance-Ultrasonic/dp/B07YD2LT9D)) for
Raspberry Pi, integrated with the **make87 platform**. It allows for controlling the vehicle's movement, adjusting the
camera's orientation, and streaming real-time camera images. Communication is handled via the make87 messaging system,
enabling seamless integration and control.

## Purpose

The primary purpose of this application is to provide a control interface for the Freenove 4WD Smart Car Kit through the
make87 platform. It enables:

- Driving the vehicle using 2D directional vectors.
- Adjusting the camera's pitch (up/down) and yaw (left/right) angles.
- Streaming real-time images from the camera for monitoring and tracking.

## Message Details and Value Ranges

### 1. Drive Control (`SET_DRIVE_DIRECTION`)

- **Message Type**: `Vector2`
- **Payload**:
    - `x`: Forward/backward component.
        - Positive values move the vehicle forward.
        - Negative values move it backward.
    - `y`: Left/right component.
        - Positive values steer the vehicle to the right.
        - Negative values steer it to the left.

- **Value Handling**:
    - The vector's magnitude is clipped to a maximum value of `1` to prevent exceeding motor limits.
    - Example:
        - Input: `Vector2(x=2.0, y=-0.5)`  
          Handling: The vector is normalized to `Vector2(x=0.97, y=-0.24)`.

### 2. Camera Direction Control (`SET_CAMERA_DIRECTION`)

- **Message Type**: `Vector2`
- **Payload**:
    - `x`: Pitch angle (up/down).
        - Valid range: `50°–110°`.
        - Values outside this range are clipped to the nearest boundary.
        - Example: `x=45.0` is adjusted to `50.0`.
    - `y`: Yaw angle (left/right).
        - Valid range: `80°–150°`.
        - Values outside this range are clipped to the nearest boundary.
        - Example: `y=160.0` is adjusted to `150.0`.

- **Purpose**:
    - The pitch controls the vertical orientation of the camera.
    - The yaw controls the horizontal orientation of the camera.

### 3. Camera Image Streaming (`IMAGE`)

- **Message Type**: `ImageJPEG`
- **Payload**:
    - JPEG-encoded image data from the vehicle's camera.

- **Purpose**:
    - Provides a real-time video feed for monitoring.
    - The image resolution is set to `640x480`, with a frame rate of `30 FPS`.

## Value Handling Summary

- **Drive Control**:  
  Direction vectors are normalized to ensure motor values remain within safe limits.

- **Camera Pitch and Yaw**:  
  Angles are clipped to predefined ranges to protect the servos and ensure stability.

- **Camera Streaming**:  
  Ensures reliable encoding and publishing of real-time images for efficient monitoring.

This application is an essential component for remotely operating and monitoring the Freenove 4WD Smart Car Kit via the
make87 platform, providing precise control and a live video feed for robotics applications.
