import threading
import time
from threading import Thread
import logging
import numpy as np
import cv2

from make87_messages.core.empty_pb2 import Empty
from make87_messages.core.header_pb2 import Header
from make87_messages.tensor.vector_2_pb2 import Vector2
from make87_messages.tensor.vector_3_pb2 import Vector3
from make87_messages.image.compressed.image_jpeg_pb2 import ImageJPEG

# from make87 import (
#     initialize,
#     get_publisher,
#     resolve_topic_name,
#     resolve_peripheral_name,
#     resolve_endpoint_name,
#     get_provider,
# )
import make87
from picamera2.picamera2 import Picamera2
from app.external.Motor import Motor
from app.external.servo import Servo


class Vehicle:
    def __init__(self):
        pass
        self.motor = Motor()
        self.camera_servo = Servo()
        self.last_image_lock = threading.Lock()
        self.last_image = None

    def handle_drive_instruction(self, message: Vector3) -> Empty:
        duration = message.z
        max_speed = 1000

        # Vector input (x=turn, y=forward)
        vector = np.array([message.x, message.y])
        mag = np.linalg.norm(vector)
        if mag > 1:
            vector /= mag

        turn = vector[0]  # + right turn
        speed = vector[1]  # + forward

        # Differential drive logic
        left_speed = speed - turn
        right_speed = speed + turn

        # Normalize if needed
        max_val = max(abs(left_speed), abs(right_speed))
        if max_val > 1:
            left_speed /= max_val
            right_speed /= max_val

        # Scale to motor range
        left_motor = int(left_speed * max_speed)
        right_motor = int(right_speed * max_speed)

        # Set speeds using correct named parameters
        self.motor.setMotorModel(
            front_left=left_motor,
            rear_left=left_motor,
            front_right=right_motor,
            rear_right=right_motor,
        )

        time.sleep(max(0.0, duration))
        self.motor.setMotorModel(front_left=0, rear_left=0, front_right=0, rear_right=0)
        return Empty()

    def handle_set_camera_direction(self, direction: Vector2) -> Empty:
        # x: pitch, y: yaw

        angle = max(111.0, min(159.0, direction.x))
        self.camera_servo.setServoPwm("1", angle)
        angle = max(1.0, min(149.0, direction.y))
        self.camera_servo.setServoPwm("0", angle)

        return Empty()

    def handle_get_latest_camera_image(self, request: Empty) -> ImageJPEG:
        # This method is not implemented in the original code
        # You can implement it if needed
        img_msg = None
        with self.last_image_lock:
            if self.last_image is not None:
                img_msg = self.last_image
            else:
                header = make87.create_header(Header, entity_path="/picamera")
                img_msg = ImageJPEG(data=b"", header=header)

        return img_msg

    def publish_camera_image(self):
        topic = make87.get_publisher(name="IMAGE", message_type=ImageJPEG)

        try:
            picam2 = Picamera2()
            video_config = picam2.create_video_configuration(
                main={"size": (640, 480), "format": "RGB888"}
            )
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
                header = make87.create_header(Header, entity_path="/picamera")
                message = ImageJPEG(data=frame_jpeg_bytes, header=header)
                with self.last_image_lock:
                    self.last_image = message
                topic.publish(message)
            except Exception as e:
                logging.error(f"Error while capturing or publishing image: {e}")
                break

        picam2.stop()

    def run(self):
        camera_thread = Thread(target=self.publish_camera_image)
        camera_thread.start()

        drive_endpoint = make87.get_provider(
            name="SET_DRIVE_DIRECTION",
            requester_message_type=Vector3,
            provider_message_type=Empty,
        )
        drive_endpoint.provide(self.handle_drive_instruction)

        camera_direction_endpoint = make87.get_provider(
            name="SET_CAMERA_DIRECTION",
            requester_message_type=Vector2,
            provider_message_type=Empty,
        )
        camera_direction_endpoint.provide(self.handle_set_camera_direction)

        camera_image_endpoint = make87.get_provider(
            name="GET_CAMERA_IMAGE",
            requester_message_type=Empty,
            provider_message_type=ImageJPEG,
        )
        camera_image_endpoint.provide(self.handle_get_latest_camera_image)

        # angle = max(50.0, min(110.0, 70))
        # self.camera_servo.setServoPwm("1", -180)
        # angle = max(80.0, min(150.0, 110))
        # self.camera_servo.setServoPwm("0", 20)

        camera_thread.join()


def main():
    make87.initialize()
    vehicle = Vehicle()
    vehicle.run()


if __name__ == "__main__":
    main()
