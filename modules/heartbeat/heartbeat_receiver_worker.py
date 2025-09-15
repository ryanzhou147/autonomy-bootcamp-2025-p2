"""
Heartbeat worker that sends heartbeats periodically.
"""

import os
import pathlib
import time

from pymavlink import mavutil

from utilities.workers import queue_proxy_wrapper
from utilities.workers import worker_controller
from . import heartbeat_receiver
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
def heartbeat_receiver_worker(
    connection: mavutil.mavfile,
    controller: worker_controller.WorkerController,  # Place your own arguments here
    output_queue: queue_proxy_wrapper.QueueProxyWrapper,
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
    # Instantiate class object (heartbeat_receiver.HeartbeatReceiver)
    success, hb_receiver = heartbeat_receiver.HeartbeatReceiver.create(connection, local_logger)
    if not success or hb_receiver is None:
        local_logger.error("Failed to intialize HeartbeatReceiver", True)
        return
    # Main loop: do work.

    while not controller.is_exit_requested():
        if controller.check_pause():
            time.sleep(0.01)
            continue
    
        state = hb_receiver.run()

        try:
            output_queue.put(state)
        except Exception as e:
            local_logger.error(f"Failed to put state in queue: {e}", True)
        
        time.sleep(1)
    
    local_logger.info("heartbeat Reciever Worker exiting", True)


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
