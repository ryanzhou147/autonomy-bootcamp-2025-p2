"""
Command worker to make decisions based on Telemetry Data.
"""

import os
import pathlib
import time

from pymavlink import mavutil

from utilities.workers import queue_proxy_wrapper
from utilities.workers import worker_controller
from . import command
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
def command_worker(
    connection: mavutil.mavfile,
    target: command.Position,
    telemetry_queue: queue_proxy_wrapper.QueueProxyWrapper,  # Place your own arguments here
    # Add other necessary worker arguments here
) -> None:
    """
    Worker process.

    args... describe what the arguments are
    """
    # =============================================================================================
    #                          ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
    # =============================================================================================

    # Instantiate logger
    worker_name = pathlib.Path(__file__).stem
    process_id = os.getpid()
    result, local_logger = logger.Logger.create(f"{worker_name}_{process_id}", True)
    if not result:
        print("ERROR: Worker failed to create logger")
        return

    # Get Pylance to stop complaining
    assert local_logger is not None

    local_logger.info("Logger initialized", True)

    # =============================================================================================
    #                          ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
    # =============================================================================================
    # Instantiate class object (command.Command)
    cmd_obj = command.Command.create(connection,target,local_logger)
    if cmd_obj is None:
        local_logger.error("Failed to create Command object, exiting worker", True)
        return
    local_logger.info("Command worker started", True)

    # Main loop: do work.
    while True:
        try:
            if telemetry_queue.empty():
                time.sleep(0.01)
                continue
            
            telemetry_data = telemetry_queue.get()

            output_strings = cmd_obj.run(telemetry_data)

            for s in output_strings:
                local_logger.info(s, True)
        
        except Exception as e:
            local_logger.error(f"Exception in Command worker loop: {e}", True)
            time.sleep(0.1)

# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
