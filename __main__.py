from typing import Tuple

import Gamepad.Gamepad as Gamepad
import Gamepad.Controllers as Controllers
import time
from detect_motor_controllers import get_motor_controllers
from mathutils import square, deadzone

SLOW_SPEED = 0.3
MEDIUM_SPEED = 0.5
MAX_SPEED = 1


def curvture_drive_ik(speed: float, rotation: float) -> Tuple[float, float]:
    DEADZONE = 0.05

    """Curvature drive inverse kinematics for a differential drive platform.

    Args:
      speed: The speed along the X axis [-1.0..1.0]. Forward is positive.
      rotation: The normalized curvature [-1.0..1.0]. Counterclockwise is positive.

    Returns:
      Wheel speeds [-1.0..1.0].
    """
    speed = deadzone(speed, DEADZONE)

    # decreases input sensitivity at low speeds
    speed = square(speed)
    rotation = square(rotation)

    left_speed = speed + abs(speed) * rotation
    right_speed = speed - abs(speed) * rotation

    # desaturates the wheel speeds
    max_magnitude = max(abs(left_speed), abs(right_speed))
    if max_magnitude > 1:
        left_speed /= max_magnitude
        right_speed /= max_magnitude

    return left_speed, right_speed


def get_speed_multiplier(stick: Controllers.Joystick) -> float:
    if stick.isPressed('MODEA'):
        return MEDIUM_SPEED
    elif stick.isPressed('MODEB'):
        return MAX_SPEED
    else:
        return SLOW_SPEED


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
    left_motor, right_motor = get_motor_controllers()

    # Main loop
    try:
        while joystick.isConnected():
            joystick_vertical = -joystick.axis('Y')
            joystick_horizontal = joystick.axis('X')
            # print(f"Vertical: {joystick_vertical}, Horizontal: {joystick_horizontal}")
            ik_left, ik_right = curvture_drive_ik(joystick_vertical, joystick_horizontal)
            ik_left *= get_speed_multiplier(joystick)
            ik_right *= get_speed_multiplier(joystick)

            try:
                left_rpm = left_motor.get_rpm()
                right_rpm = right_motor.get_rpm()
            except:
                left_rpm = 0
                right_rpm = 0

            print(f"Left: {ik_left}, Right: {ik_right}, Left RPM: {left_rpm}, Right RPM {right_rpm}")

            if left_rpm >= 0 or ik_left >= 0:
                left_motor.set_current(ik_left)
            else:
                left_motor.set_rpm(0)

            if right_rpm >= 0 or ik_right >= 0:
                right_motor.set_current(ik_right)
            else:
                right_motor.set_rpm(0)

    finally:
        del left_motor
        del right_motor
        joystick.disconnect()
