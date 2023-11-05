from pyvesc import VESC

from mathutils import map_range


class MotorController:
    """Sets the speed of the motor, from -1 to 1."""

    def set_speed(self, speed: float):
        pass


class VESCMotorController(MotorController):
    MAX_RPM = 10000

    def __init__(self, motor: VESC):
        self.motor = motor

    def set_speed(self, speed: float):
        scaled_speed = map_range(speed, -1, 1, -VESCMotorController.MAX_RPM, VESCMotorController.MAX_RPM)
        self.motor.set_rpm(int(scaled_speed))

    def __del__(self):
        # Stop the heartbeat to prevent the motor from spinning
        self.motor.stop_heartbeat()


class VirtualMotorController(MotorController):
    def __init__(self, name: str):
        self.speed = 0
        self.name = name
        print(f"Initialized motor {self.name}")

    def set_speed(self, speed: float):
        self.speed = speed
        print(f"Motor {self.name}: {self.speed}")

    def get_speed(self):
        return self.speed
