import time
from threading import Thread
import cv2
import logging
import numpy as np

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

from app.external.Motor import Motor
from app.external.servo import Servo


class Vehicle:
    def __init__(self):
        self.motor = Motor()
        self.camera_servo = Servo()

    def handle_drive_instruction(self, message: Vector2) -> PlainText:
        vector = np.array([message.x, message.y])
        # if longer than one, clip to unit
        if np.linalg.norm(vector) > 1:
            vector = vector / np.linalg.norm(vector)

        front_left = vector[0] * 1000
        front_right = vector[0] * 1000
        rear_left = vector[0] * 1000
        rear_right = vector[0] * 1000
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
        cap = cv2.VideoCapture(resolve_peripheral_name("CAMERA"))

        if not cap.isOpened():
            logging.error("Cannot open camera")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)

        while True:
            ret, frame = cap.read()
            if not ret:
                logging.error("Error: failed to capture frame.")
                break
            ret, frame_jpeg = cv2.imencode(".jpeg", frame)
            if not ret:
                logging.error("Error: Could not encode frame to JPEG.")
                break
            frame_jpeg_bytes = frame_jpeg.tobytes()
            message = ImageJPEG(data=frame_jpeg_bytes)
            topic.publish(message)

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
        camera_direction_endpoint.provide(self.handle_set_camera_pitch)

        camera_thread.join()


def main():
    initialize()
    vehicle = Vehicle()
    vehicle.run()


if __name__ == "__main__":
    main()
