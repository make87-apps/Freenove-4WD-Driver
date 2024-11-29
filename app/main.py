import time
from threading import Thread
import logging
import numpy as np
import cv2

from make87_messages.text.text_plain_pb2 import PlainText
from make87_messages.tensor.vector_2_pb2 import Vector2
from make87_messages.image.compressed.image_jpeg_pb2 import ImageJPEG
from make87 import (
    initialize,
    get_publisher,
    resolve_topic_name,
    resolve_peripheral_name,
    resolve_endpoint_name,
    get_provider,
)
from picamera2.picamera2 import Picamera2
from app.external.Motor import Motor
from app.external.servo import Servo


class Vehicle:
    def __init__(self):
        pass
        self.motor = Motor()
        self.camera_servo = Servo()

    def handle_drive_instruction(self, message: Vector2) -> PlainText:
        # Your desired movement vector (Vx, Vy)
        vector = np.array([message.x, message.y])
        # drive straight
        max_speed = 1000  # Adjust as necessary

        # Normalize the vector to ensure the magnitude does not exceed 1
        norm = np.linalg.norm(vector)
        if norm > 1:
            vector = vector / norm

        # Extract the strafe and forward components
        Vx = vector[0]  # Strafe component (left/right)
        Vy = vector[1]  # Forward component (forward/backward)

        # Rotation component (set to zero if not rotating)
        V_rotation = 0.0  # Adjust as needed for rotation

        # Calculate wheel speeds
        front_left = Vy + Vx + V_rotation
        front_right = Vy - Vx - V_rotation
        rear_left = Vy - Vx + V_rotation
        rear_right = Vy + Vx - V_rotation

        # Scale wheel speeds by the maximum speed
        front_left *= max_speed
        front_right *= max_speed
        rear_left *= max_speed
        rear_right *= max_speed

        # Normalize wheel speeds to prevent any from exceeding the maximum
        max_wheel_speed = max(abs(front_left), abs(front_right), abs(rear_left), abs(rear_right))
        if max_wheel_speed > max_speed:
            scale = max_speed / max_wheel_speed
            front_left *= scale
            front_right *= scale
            rear_left *= scale
            rear_right *= scale

        # Convert wheel speeds to integers
        front_left = int(front_left)
        front_right = int(front_right)
        rear_left = int(rear_left)
        rear_right = int(rear_right)

        # Set the motor speeds
        self.motor.setMotorModel(front_left, front_right, rear_left, rear_right)

        return PlainText(body="Success")

    def handle_set_camera_direction(self, direction: Vector2) -> PlainText:
        # x: pitch, y: yaw

        angle = max(50.0, min(110.0, direction.x))
        self.camera_servo.setServoPwm("1", angle)
        angle = max(80.0, min(150.0, direction.y))
        self.camera_servo.setServoPwm("0", angle)

        return PlainText(body="Success")

    @staticmethod
    def publish_camera_image():
        topic_name = resolve_topic_name("IMAGE")
        topic = get_publisher(name=topic_name, message_type=ImageJPEG)
        
        try:
            picam2 = Picamera2()
            video_config = picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"})
            picam2.configure(video_config)
            picam2.start()
        except Exception as e:
            logging.error(f"Cannot initialize camera: {e}")
            return

        while True:
            try:
                frame = picam2.capture_array()
                ret, frame_jpeg = cv2.imencode(".jpeg", frame)
                if not ret:
                    logging.error("Error: Could not encode frame to JPEG.")
                    break
                frame_jpeg_bytes = frame_jpeg.tobytes()
                message = ImageJPEG(data=frame_jpeg_bytes)
                topic.publish(message)
            except Exception as e:
                logging.error(f"Error while capturing or publishing image: {e}")
                break
        
        picam2.stop()

    def run(self):
        camera_thread = Thread(target=self.publish_camera_image)
        camera_thread.start()

        drive_endpoint = get_provider(
            name=resolve_endpoint_name(name="SET_DRIVE_DIRECTION"),
            requester_message_type=PlainText,
            provider_message_type=PlainText,
        )
        drive_endpoint.provide(self.handle_drive_instruction)

        camera_direction_endpoint = get_provider(
            name=resolve_endpoint_name(name="SET_CAMERA_DIRECTION"),
            requester_message_type=PlainText,
            provider_message_type=PlainText,
        )
        camera_direction_endpoint.provide(self.handle_set_camera_direction)


        angle = max(50.0, min(110.0, 70))
        self.camera_servo.setServoPwm("1", -180)
        angle = max(80.0, min(150.0, 110))
        self.camera_servo.setServoPwm("0", 20)

        camera_thread.join()


def main():
    initialize()
    vehicle = Vehicle()
    vehicle.run()


if __name__ == "__main__":
    main()
