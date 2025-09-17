"""
Telemetry gathering logic.
"""

import time

from pymavlink import mavutil

from ..common.modules.logger import logger


class TelemetryData:  # pylint: disable=too-many-instance-attributes
    """
    Python struct to represent Telemtry Data. Contains the most recent attitude and position reading.
    """

    def __init__(
        self,
        time_since_boot: int | None = None,  # ms
        x: float | None = None,  # m
        y: float | None = None,  # m
        z: float | None = None,  # m
        x_velocity: float | None = None,  # m/s
        y_velocity: float | None = None,  # m/s
        z_velocity: float | None = None,  # m/s
        roll: float | None = None,  # rad
        pitch: float | None = None,  # rad
        yaw: float | None = None,  # rad
        roll_speed: float | None = None,  # rad/s
        pitch_speed: float | None = None,  # rad/s
        yaw_speed: float | None = None,  # rad/s
    ) -> None:
        self.time_since_boot = time_since_boot
        self.x = x
        self.y = y
        self.z = z
        self.x_velocity = x_velocity
        self.y_velocity = y_velocity
        self.z_velocity = z_velocity
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        self.roll_speed = roll_speed
        self.pitch_speed = pitch_speed
        self.yaw_speed = yaw_speed

    def __str__(self) -> str:
        return f"""{{
            time_since_boot: {self.time_since_boot},
            x: {self.x},
            y: {self.y},
            z: {self.z},
            x_velocity: {self.x_velocity},
            y_velocity: {self.y_velocity},
            z_velocity: {self.z_velocity},
            roll: {self.roll},
            pitch: {self.pitch},
            yaw: {self.yaw},
            roll_speed: {self.roll_speed},
            pitch_speed: {self.pitch_speed},
            yaw_speed: {self.yaw_speed}
        }}"""


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class Telemetry:
    """
    Telemetry class to read position and attitude (orientation).
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> tuple[bool, object]:
        """
        Falliable create (instantiation) method to create a Telemetry object.
        """
        try:
            return True, Telemetry(
                cls.__private_key, connection, local_logger
            )  # Create a Telemetry object
        except Exception as e:
            local_logger.error(f"Failed to create Telemetry: {e}", True)
            return False, None

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> None:
        assert key is Telemetry.__private_key, "Use create() method"

        # Do any intializiation here
        self.__connection = connection
        self.__logger = local_logger
        self.__last_attitude = None
        self.__last_position = None

    def run(
        self,
    ) -> None:
        """
        Receive LOCAL_POSITION_NED and ATTITUDE messages from the drone,
        combining them together to form a single TelemetryData object.
        """
        # Read MAVLink message LOCAL_POSITION_NED (32)
        # Read MAVLink message ATTITUDE (30)
        # Return the most recent of both, and use the most recent message's timestamp
        try:
            # Non-blocking read of ATTITUDE (msgid=30)
            attitude_msg = self._connection.recv_match(type="ATTITUDE", blocking=False)
            if attitude_msg:
                self._last_attitude = attitude_msg

            # Non-blocking read of LOCAL_POSITION_NED (msgid=32)
            position_msg = self._connection.recv_match(type="LOCAL_POSITION_NED", blocking=False)
            if position_msg:
                self._last_position = position_msg

            if self._last_attitude and self._last_position:
                # Combine latest messages into TelemetryData
                telemetry_data = TelemetryData(
                    time_since_boot=max(
                        getattr(self._last_attitude, "time_boot_ms", 0),
                        getattr(self._last_position, "time_boot_ms", 0),
                    ),
                    x=getattr(self._last_position, "x", 0.0),
                    y=getattr(self._last_position, "y", 0.0),
                    z=getattr(self._last_position, "z", 0.0),
                    x_velocity=getattr(self._last_position, "vx", 0.0),
                    y_velocity=getattr(self._last_position, "vy", 0.0),
                    z_velocity=getattr(self._last_position, "vz", 0.0),
                    roll=getattr(self._last_attitude, "roll", 0.0),
                    pitch=getattr(self._last_attitude, "pitch", 0.0),
                    yaw=getattr(self._last_attitude, "yaw", 0.0),
                    roll_speed=getattr(self._last_attitude, "rollspeed", 0.0),
                    pitch_speed=getattr(self._last_attitude, "pitchspeed", 0.0),
                    yaw_speed=getattr(self._last_attitude, "yawspeed", 0.0),
                )
                return telemetry_data

        except Exception as e:
            self._logger.error(f"Error while collecting telemetry: {e}", True)

        return None


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
