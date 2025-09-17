"""
Heartbeat sending logic.
"""

from pymavlink import mavutil


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class HeartbeatSender:
    """
    HeartbeatSender class to send a heartbeat
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
    ) -> tuple[bool, mavutil.mavfile]:
        """
        Falliable create (instantiation) method to create a HeartbeatSender object.
        """

        return True, HeartbeatSender(
            cls.__private_key,
            connection,
        )  # Create a HeartbeatSender object

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
    ) -> None:
        assert key is HeartbeatSender.__private_key, "Use create() method"

        # Do any intializiation here

        self.__connection = connection

    def run(self) -> None:
        """
        Attempt to send a heartbeat message.
        """
        try:
            self.__connection.mav.heartbeat_send(
                mavutil.mavlink.MAV_TYPE_GENERIC, mavutil.mavlink.MAV_AUTOPILOT_GENERIC, 0, 0, 0
            )  # Send a heartbeat message
            self.__logger.debug("Heartbeat sent", True)
        except Exception as e:
            self.__logger.error(f"Error while sending heartbeat: {e}", True)


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
