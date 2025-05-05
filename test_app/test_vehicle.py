from make87_messages.tensor.vector_2_pb2 import Vector2

from app.main import Vehicle

import pytest
from app.external.servo import Servo


class DummyServo(Servo):
    """Servo mock to capture set angles without hardware."""

    def __init__(self):
        self.angles = {"0": None, "1": None}

    def setServoPwm(self, channel, angle):
        self.angles[str(channel)] = angle


class DummyMotor:
    """Motor mock to avoid hardware calls."""

    def setMotorModel(self, front_left, rear_left, front_right, rear_right):
        pass


@pytest.fixture
def vehicle():
    v = Vehicle(servo=DummyServo(), motor=DummyMotor())
    return v


def test_camera_initial_angles(vehicle):
    assert vehicle.pitch == 135.0
    assert vehicle.yaw == 75.0


def test_yaw_right(vehicle):
    vehicle.handle_set_camera_direction(Vector2(x=10.0, y=0.0))
    assert vehicle.yaw == pytest.approx(85.0)
    assert vehicle.camera_servo.angles["0"] == 85.0  # yaw
    assert vehicle.camera_servo.angles["1"] == 135.0  # pitch unchanged


def test_pitch_down(vehicle):
    vehicle.handle_set_camera_direction(Vector2(x=0.0, y=10.0))
    assert vehicle.pitch == pytest.approx(145.0)
    assert vehicle.camera_servo.angles["1"] == 145.0  # pitch
    assert vehicle.camera_servo.angles["0"] == 75.0  # yaw unchanged


def test_yaw_limit_right(vehicle):
    # Try to exceed yaw max limit
    vehicle.handle_set_camera_direction(Vector2(x=100.0, y=0.0))
    assert vehicle.yaw == 149.0  # clamped
    assert vehicle.camera_servo.angles["0"] == 149.0


def test_pitch_limit_down(vehicle):
    vehicle.handle_set_camera_direction(Vector2(x=0.0, y=100.0))
    assert vehicle.pitch == 159.0  # clamped
    assert vehicle.camera_servo.angles["1"] == 159.0


def test_yaw_limit_left(vehicle):
    vehicle.handle_set_camera_direction(Vector2(x=-100.0, y=0.0))
    assert vehicle.yaw == 1.0  # clamped


def test_pitch_limit_up(vehicle):
    vehicle.handle_set_camera_direction(Vector2(x=0.0, y=-100.0))
    assert vehicle.pitch == 111.0  # clamped


def test_wheel_speeds_forward():
    left, right = Vehicle.compute_wheel_speeds(0, 1)
    assert left == 1000
    assert right == 1000


def test_wheel_speeds_backward():
    left, right = Vehicle.compute_wheel_speeds(0, -1)
    assert left == -1000
    assert right == -1000


def test_wheel_speeds_turn_right_in_place():
    left, right = Vehicle.compute_wheel_speeds(1, 0)
    assert left == 1000
    assert right == -1000


def test_wheel_speeds_turn_left_in_place():
    left, right = Vehicle.compute_wheel_speeds(-1, 0)
    assert left == -1000
    assert right == 1000


def test_wheel_speeds_diagonal_right():
    left, right = Vehicle.compute_wheel_speeds(0.5, 0.5)
    assert left == 1000
    assert right == 0


def test_wheel_speeds_diagonal_left():
    left, right = Vehicle.compute_wheel_speeds(-0.5, 0.5)
    assert left == 0
    assert right == 1000
