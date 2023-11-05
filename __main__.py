from typing import Tuple

import Gamepad.Gamepad as Gamepad
import Gamepad.Controllers as Controllers
import time
from detect_motor_controllers import get_motor_controllers
from mathutils import square, deadzone
from motor_controller import VirtualMotorController


def curvture_drive_ik(speed: float, rotation: float) -> Tuple[float, float]:

    DEADZONE = 0.05

    """Curvature drive inverse kinematics for a differential drive platform.

    Args:
      speed: The speed along the X axis [-1.0..1.0]. Forward is positive.
      rotation: The normalized curvature [-1.0..1.0]. Counterclockwise is positive.

    Returns:
      Wheel speeds [-1.0..1.0].
    """
    # decreases input sensitivity at low speeds
    speed = square(speed)
    rotation = square(rotation)

    speed = deadzone(speed, DEADZONE)
    left_speed = speed + abs(speed) * rotation
    right_speed = speed - abs(speed) * rotation

    # desaturates the wheel speeds
    max_magnitude = max(abs(left_speed), abs(right_speed))
    if max_magnitude > 1:
        left_speed /= max_magnitude
        right_speed /= max_magnitude

    return left_speed, right_speed


if __name__ == '__main__':

    VERTICAL_JOYSTICK_AXIS = 1
    HORIZONTAL_JOYSTICK_AXIS = 0
    POLL_INTERVAL = 0.1

    # Waits for the joystick to be connected
    while not Gamepad.available():
        print("Please connect your gamepad")
        time.sleep(1)
    joystick = Controllers.Joystick()  # Initializes the joystick as a generic gamepad
    print("Gamepad connected")

    joystick.startBackgroundUpdates()

    # Waits for the motor controllers to be connected
    # left_motor, right_motor = get_motor_controllers()
    left_motor = VirtualMotorController("Left")
    right_motor = VirtualMotorController("Right")

    # Main loop
    try:
        while joystick.isConnected():
            joystick_vertical = -joystick.axis('Y')
            joystick_horizontal = joystick.axis('X')
            # print(f"Vertical: {joystick_vertical}, Horizontal: {joystick_horizontal}")
            ik_left, ik_right = curvture_drive_ik(joystick_vertical, joystick_horizontal)
            print(f"Left: {ik_left}, Right: {ik_right}")
            left_motor.set_speed(ik_left)
            right_motor.set_speed(ik_right)

    finally:
        del left_motor
        del right_motor
        joystick.disconnect()
