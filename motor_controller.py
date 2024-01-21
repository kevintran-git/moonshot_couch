from pyvesc import VESC, encode, encode_request, decode
from pyvesc.VESC.messages import SetCurrent, SetRPM, GetValues, SetDutyCycle
from mathutils import map_range


class MotorController:
    """Sets the speed of the motor, from -1 to 1."""

    def speed_to_rpm(self, speed: float):
        return int(map_range(speed, -1, 1, -VESCMotorController.MAX_RPM, VESCMotorController.MAX_RPM))

    def speed_to_current(self, speed: float):
        return int(map_range(speed, -1, 1, -VESCMotorController.MAX_CURRENT, VESCMotorController.MAX_CURRENT))
    
    def set_duty_cycle(self, speed: float):
        return int(map_range(speed, -1, 1, -1e5, 1e5))

    def set_rpm(self, speed: float):
        raise NotImplementedError

    def set_current(self, speed: float):
        raise NotImplementedError

    def get_rpm(self):
        raise NotImplementedError

    def get_measurements(self):
        raise NotImplementedError


class VESCMotorController(MotorController):
    MAX_RPM = 20000
    MAX_CURRENT = 20

    def __init__(self, motor: VESC):
        self.motor = motor

    def set_rpm(self, speed: float):
        rpm = self.speed_to_rpm(speed)
        self.motor.set_rpm(rpm)

    def set_current(self, speed: float):
        current = self.speed_to_current(speed)
        self.motor.set_current(current)

    def set_duty_cycle(self, speed: float):
        duty_cycle = self.set_duty_cycle(speed)
        self.motor.set_duty_cycle(duty_cycle)

    def get_measurements(self):
        return self.motor.get_measurements()
    
    def get_rpm(self):
        return self.motor.get_rpm()

    def __del__(self):
        # Stop the heartbeat to prevent the motor from spinning
        self.motor.stop_heartbeat()


class CanVESC(MotorController):
    def __init__(self, parent_vesc: VESC, can_id: int):
        self.parent_vesc = parent_vesc
        self.can_id = can_id
        msg = GetValues(can_id=can_id)
        self._get_values_msg = encode_request(msg)
        self._get_values_msg_expected_length = msg._full_msg_size

    def set_rpm(self, speed: float):
        rpm = self.speed_to_rpm(speed)
        packet = encode(SetRPM(rpm, can_id=self.can_id))
        self.parent_vesc.write(packet)

    def set_current(self, speed: float):
        current = self.speed_to_current(speed)
        packet = encode(SetCurrent(current, can_id=self.can_id))
        self.parent_vesc.write(packet)
    
    def set_duty_cycle(self, speed: float):
        duty_cycle = self.set_duty_cycle(speed)
        packet = encode(SetDutyCycle(duty_cycle, can_id=self.can_id))
        self.parent_vesc.write(packet)

    def get_measurements(self):
        return self.parent_vesc.write(self._get_values_msg, num_read_bytes=self._get_values_msg_expected_length)

    def get_rpm(self):
        return self.get_measurements().rpm

    def __del__(self):
        # Stop the heartbeat to prevent the motor from spinning
        self.parent_vesc.stop_heartbeat()
