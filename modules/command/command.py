"""
Decision-making logic.
"""

import math

from pymavlink import mavutil

from ..common.modules.logger import logger
from ..telemetry import telemetry


class Position:
    """
    3D vector struct.
    """

    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class Command:  # pylint: disable=too-many-instance-attributes
    """
    Command class to make a decision based on recieved telemetry,
    and send out commands based upon the data.
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        target: Position,
        local_logger: logger.Logger,
    ):
        """
        Falliable create (instantiation) method to create a Command object.
        """
        try:
            return cls(Command.__private_key, connection, target, local_logger)  #  Create a Command object
        except Exception as e:
            local_logger.error(f"Failed to create command: {e}", True)
            return None

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        target: Position,
        local_logger: logger.Logger,
    ) -> None:
        assert key is Command.__private_key, "Use create() method"

        # Do any intializiation here
        self.connection = connection
        self.target = target
        self.local_logger = local_logger

        self.velocities = []  # list of (x_vel, y_vel, z_vel)
        self.last_alt = None
        self.last_yaw = None


    def run(
        self,
        telemetry_data: telemetry.TelemetryData,  # Put your own arguments here
    ):
        """
        Make a decision based on received telemetry data.
        """
        output_strings = []


        # Log average velocity for this trip so far
        if telemetry_data.x_velocity is not None:
            self.velocities.append((
                telemetry_data.x_velocity,
                telemetry_data.y_velocity,
                telemetry_data.z_velocity,
            ))
            avg_velocity = tuple(
                sum(v[i] for v in self.velocities)/len(self.velocities) for i in range(3)
            )
            self.local_logger.info(f"Average velocity: {avg_velocity}", True)

        # Use COMMAND_LONG (76) message, assume the target_system=1 and target_componenet=0
        # The appropriate commands to use are instructed below

        # Adjust height using the comand MAV_CMD_CONDITION_CHANGE_ALT (113)
        # String to return to main: "CHANGE_ALTITUDE: {amount you changed it by, delta height in meters}"
        if telemetry_data.z is not None:
            if self.last_alt is None:
                self.last_alt = telemetry_data.z

            delta_alt = self.target.z - telemetry_data.z
            if abs(delta_alt) > 0.5:
                self.connection.mav.command_long_send(
                    1, 0,  # target_system, target_component
                    mavutil.mavlink.MAV_CMD_CONDITION_CHANGE_ALT,
                    0,  # confirmation
                    delta_alt, 0, 0, 0, 0, 0, 0
                )
                self.last_alt += delta_alt
                output_strings.append(f"CHANGE_ALTITUDE: {delta_alt:.2f}")
        # Adjust direction (yaw) using MAV_CMD_CONDITION_YAW (115). Must use relative angle to current state
        # String to return to main: "CHANGING_YAW: {degree you changed it by in range [-180, 180]}"
        # Positive angle is counter-clockwise as in a right handed system
        if telemetry_data.x is not None and telemetry_data.y is not None and telemetry_data.yaw is not None:
            dx = self.target.x - telemetry_data.x
            dy = self.target.y - telemetry_data.y
            target_yaw_deg = math.degrees(math.atan2(dy, dx))

            current_yaw_deg = math.degrees(telemetry_data.yaw)
            delta_yaw = (target_yaw_deg - current_yaw_deg + 180) % 360 - 180  # wrap to [-180, 180]

            if abs(delta_yaw) > 5:
                self.connection.mav.command_long_send(
                    1, 0,  # target_system, target_component
                    mavutil.mavlink.MAV_CMD_CONDITION_YAW,
                    0,  # confirmation
                    delta_yaw, 0, 0, 0, 0, 0, 0
                )
                output_strings.append(f"CHANGING_YAW: {delta_yaw:.2f}")
                self.last_yaw = math.radians(current_yaw_deg + delta_yaw)

        return output_strings

# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
