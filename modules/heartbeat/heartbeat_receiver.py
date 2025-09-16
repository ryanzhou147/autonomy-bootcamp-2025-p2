"""
Heartbeat receiving logic.
"""

from pymavlink import mavutil

from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class HeartbeatReceiver:
    """
    HeartbeatReceiver class to send a heartbeat
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ):
        """
        Falliable create (instantiation) method to create a HeartbeatReceiver object.
        """
        try:  # Create a HeartbeatReceiver object
            return True, HeartbeatReceiver(cls.__private_key, connection, local_logger)
        except Exception as e:
            local_logger.error(f"Failed to create HeartbeatReceiver: {e}", True)
            return False, None
        
    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> None:
        assert key is HeartbeatReceiver.__private_key, "Use create() method"

        # Do any intializiation here

        self.__connection = connection
        self.__logger = local_logger
        self.__missed_count = 0
        self.__state = "Disconnected"

        self.__MAX_MISSED = 5

    def run(
        self  # Put your own arguments here
    ) -> str:
        """
        Attempt to recieve a heartbeat message.
        If disconnected for over a threshold number of periods,
        the connection is considered disconnected.
        """
        try:
            msg = self.__connection.recv_match(type="HEARTBEAT", blocking=False,)

            if msg:
                if self.__state != "Connected":
                    self.__logger.info("Heartbeat received -> Connected", True)
                self.__missed_count = 0
                self.__state = "Connected"
            else:
                self.__missed_count += 1
                self.__logger.warning(f"Missed heartbeat ({self.__missed_count})", True)
                if self.__missed_count >= 5:
                    self.__state = "Disconnected"
        except Exception as e:
            self.__logger.error(f"Error while receiving heartbeat: {e}", True)
        
        return self.__state

# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
