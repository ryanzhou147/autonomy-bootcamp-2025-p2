"""
Telemtry worker that gathers GPS data.
"""

import os
import pathlib
import time

from pymavlink import mavutil

from utilities.workers import queue_proxy_wrapper
from utilities.workers import worker_controller
from . import telemetry
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
def telemetry_worker(
    connection: mavutil.mavfile,
    output_queue: queue_proxy_wrapper.QueueProxyWrapper,  # Place your own arguments here
    controller: worker_controller.WorkerController,# Add other necessary worker arguments here
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
    # Instantiate class object (telemetry.Telemetry)
    success, telemetry_instance = telemetry.Telemetry.create(connection, local_logger)
    if not success or telemetry_instance is None:
        local_logger.error("Failed to initalize Telemetry", True)
        return
    
    MESSAGE_TIMEOUT = 1.0
    last_message_time = time.time()
    # Main loop: do work.

    while not controller.is_exit_requested():
        try:
            data_received = telemetry_instance.collect_latest()
            if data_received:
                output_queue.put(data_received)
                last_message_time = time.time()
                local_logger.debug(f"TelemetryData sent: {data_received}", True)
            else:
                if time.time() - last_message_time > MESSAGE_TIMEOUT:
                    local_logger.warning("Telemetry timeout, restarting.", True)
        except Exception as e:
            local_logger.error(f"Error in telemetry_worker main loop: {e}", True)
    
        if controller.check_pause():
            time.sleep(0.01)
            continue
        
        time.sleep(0.01)
    
    local_logger.info("Telemetry Worker exiting", True)


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
