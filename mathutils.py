"""Math utilities."""
from typing import Tuple


def map_range(x, in_min, in_max, out_min, out_max):
    """
    Maps a value in one range to another range.
    For example: map_range(x, -1, 1, 0, 100) will rescale outputs
    in a [-1,1] range to a [0,100] range.
    """
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def deadzone(x: float, min_val: float) -> float:
    """Returns x with a deadzone applied."""
    if abs(x) < min_val:
        return 0
    return x


def scale_and_deadzone_inputs(speed: float, rotation: float, square_rotation: bool = True, deadband: float = 0.05) -> Tuple[float, float]:
    """Apply deadzone and scaling to the inputs.

    Args:
        speed: The linear speed component.
        rotation: The rotational speed component.
        square_rotation: Whether to square the rotation input to decrease sensitivity.
        deadzone: The deadzone to apply to the inputs.

    Returns:
        Tuple of scaled speed and rotation.
    """
    speed = deadzone(speed, deadband)
    rotation = deadzone(rotation, deadband)
    speed = square(speed)
    if square_rotation:
        rotation = square(rotation)
    return speed, rotation


def desaturate_wheel_speeds(left_speed: float, right_speed: float, use_max: bool = True) -> Tuple[float, float]:
    """Rescale wheel speeds to [-1.0..1.0] range if necessary.

    Args:
        left_speed: The calculated speed for the left wheel.
        right_speed: The calculated speed for the right wheel.
        use_max: If True, use the maximum absolute speed for desaturation. If False, use a different calculation involving both inputs.

    Returns:
        Tuple of desaturated left and right wheel speeds.
    """
    if use_max:
        max_magnitude = max(abs(left_speed), abs(right_speed))
        if max_magnitude > 1:
            left_speed /= max_magnitude
            right_speed /= max_magnitude
    else:
        greater_input = max(abs(left_speed), abs(right_speed))
        less_input = min(abs(left_speed), abs(right_speed))
        if greater_input == 0:
            return 0, 0
        saturated_input = (greater_input + less_input) / greater_input
        left_speed /= saturated_input
        right_speed /= saturated_input

    return left_speed, right_speed


def apply_deadband(value: float, deadband: float, max_magnitude: float) -> float:
    """
    Currently unused.
    Returns 0.0 if the given value is within the specified range around zero. The remaining range
    between the deadband and the maximum magnitude is scaled from 0.0 to the maximum magnitude.

    @param value: Value to clip.
    @param deadband: Range around zero.
    @param max_magnitude: The maximum magnitude of the input. Can be infinite.
    @return: The value after the deadband is applied.
    """

    if abs(value) > deadband:
        if max_magnitude / deadband > 1.0e12:
            # If max magnitude is sufficiently large, the implementation encounters
            # roundoff error. Implementing the limiting behavior directly avoids
            # the problem.
            return value - deadband if value > 0.0 else value + deadband
        if value > 0.0:
            # Map deadband to 0 and map max to max.
            #
            # y - y₁ = m(x - x₁)
            # y - y₁ = (y₂ - y₁)/(x₂ - x₁) (x - x₁)
            # y = (y₂ - y₁)/(x₂ - x₁) (x - x₁) + y₁
            #
            # (x₁, y₁) = (deadband, 0) and (x₂, y₂) = (max, max).
            # x₁ = deadband
            # y₁ = 0
            # x₂ = max
            # y₂ = max
            #
            # y = (max - 0)/(max - deadband) (x - deadband) + 0
            # y = max/(max - deadband) (x - deadband)
            # y = max (x - deadband)/(max - deadband)
            return max_magnitude * (value - deadband) / (max_magnitude - deadband)
        else:
            # Map -deadband to 0 and map -max to -max.
            #
            # y - y₁ = m(x - x₁)
            # y - y₁ = (y₂ - y₁)/(x₂ - x₁) (x - x₁)
            # y = (y₂ - y₁)/(x₂ - x₁) (x - x₁) + y₁
            #
            # (x₁, y₁) = (-deadband, 0) and (x₂, y₂) = (-max, -max).
            # x₁ = -deadband
            # y₁ = 0
            # x₂ = -max
            # y₂ = -max
            #
            # y = (-max - 0)/(-max + deadband) (x + deadband) + 0
            # y = max/(max - deadband) (x + deadband)
            # y = max (x + deadband)/(max - deadband)
            return max_magnitude * (value + deadband) / (max_magnitude - deadband)
    else:
        return 0.0


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Currently unused.
    Returns the value clamped to the range [min_value, max_value].

    @param value: Value to clamp.
    @param min_value: Minimum value.
    @param max_value: Maximum value.
    @return: The value clamped to the range [min_value, max_value].
    """
    return max(min(value, max_value), min_value)


def square(value: float) -> float:
    """
    Squares the value while keeping the sign the same
    :param value: value to square
    :return: the squared value, with the same sign as the input
    """
    return abs(value) * value
