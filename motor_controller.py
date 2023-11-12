from pyvesc import VESC, encode
from pyvesc.VESC.messages import SetRPM

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


class CanVESC(MotorController):
    def __init__(self, parent_vesc: VESC, can_id: int):
        self.parent_vesc = parent_vesc
        self.can_id = can_id

    def set_speed(self, speed: float):
        scaled_speed = int(map_range(speed, -1, 1, -VESCMotorController.MAX_RPM, VESCMotorController.MAX_RPM))
        packet = encode(SetRPM(scaled_speed, can_id=self.can_id))
        self.parent_vesc.write(packet)

    def __del__(self):
        # Stop the heartbeat to prevent the motor from spinning
        self.parent_vesc.stop_heartbeat()


class VirtualMotorController(MotorController):
    def __init__(self, name: str):
        self.speed = 0
        self.name = name
        print(f"Initialized motor {self.name}")

    def set_speed(self, speed: float):
        self.speed = speed

    def get_speed(self):
        return self.speed
