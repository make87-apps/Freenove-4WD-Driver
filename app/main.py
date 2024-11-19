import time
from threading import Thread
import cv2
import logging

from make87_messages.text.text_plain_pb2 import PlainText
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

    def handle_drive_instruction(self, message: PlainText) -> PlainText:
        instruction = message.body

        if instruction.upper() == "FORWARD":
            self.motor.setMotorModel(1000, 1000, 1000, 1000)
        elif instruction.upper() == "BACKWARD":
            self.motor.setMotorModel(-1000, -1000, -1000, -1000)
        elif instruction.upper() == "LEFT":
            self.motor.setMotorModel(-1500, -1500, 2000, 2000)
        elif instruction.upper() == "RIGHT":
            self.motor.setMotorModel(2000, 2000, -1500, -1500)
        elif instruction.upper() == "STOP":
            self.motor.setMotorModel(0, 0, 0, 0)
        else:
            logging.error(f"Invalid instruction: {instruction}")
            return PlainText(body="Invalid instruction")

        return PlainText(body="Success")

    def handle_set_camera_pitch(self, message: PlainText) -> PlainText:
        angle = message.body
        try:
            angle = float(angle)
            # clip angle to [50, 110]
            angle = max(50.0, min(110.0, angle))
            self.camera_servo.setServoPwm("1", angle)
        except ValueError:
            logging.error(f"Invalid angle: {angle}")
            return PlainText(body="Invalid angle")

        return PlainText(body="Success")

    def handle_set_camera_yaw(self, message: PlainText) -> PlainText:
        angle = message.body
        try:
            angle = float(angle)
            # clip angle to [80, 150]
            angle = max(80.0, min(150.0, angle))
            self.camera_servo.setServoPwm("0", angle)
        except ValueError:
            logging.error(f"Invalid angle: {angle}")
            return PlainText(body="Invalid angle")
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
            name=resolve_endpoint_name(name="SET_DRIVE_INSTRUCTION"),
            requester_message_type=PlainText,
            provider_message_type=PlainText,
        )
        drive_endpoint.provide(self.handle_drive_instruction)

        pitch_endpoint = get_provider(
            name=resolve_endpoint_name(name="SET_CAMERA_PITCH"),
            requester_message_type=PlainText,
            provider_message_type=PlainText,
        )
        pitch_endpoint.provide(self.handle_set_camera_pitch)

        yaw_endpoint = get_provider(
            name=resolve_endpoint_name(name="SET_CAMERA_YAW"),
            requester_message_type=PlainText,
            provider_message_type=PlainText,
        )
        yaw_endpoint.provide(self.handle_set_camera_yaw)

        camera_thread.join()


def main():
    initialize()
    vehicle = Vehicle()
    vehicle.run()


if __name__ == "__main__":
    main()
