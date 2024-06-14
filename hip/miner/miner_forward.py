import bittensor as bt
import time
from hip.miner.db import SQLiteClient
from hip.protocol import TaskSynapse

tasks_db = SQLiteClient("tasks.db")
tasks_db.check_schema()
tasks_db.create_tables()
tasks_db.connect()
tasks_db.remove_expired_tasks()


async def miner_forward(self, synapse: TaskSynapse) -> TaskSynapse:
    """
    Processes the incoming 'TaskSynapse' synapse by performing a predefined operation on the input data.

    Args:
        synapse (hip.protocol.TaskSynapse): The synapse object containing the task data.

    Returns:
        hip.protocol.TaskSynapse: The synapse object with the 'answer' field set to the answer from miner.
    """
    tasks_db.remove_expired_tasks()
    bt.logging.debug("Forwarding synapse to frontend")
    tasks_db.insert_task(
        task_id=synapse.id,
        label=synapse.label,
        type=synapse.type,
        options=synapse.options,
        value=synapse.value,
        image=synapse.image,
        answer="",
    )
    bt.logging.debug(f"Task: {synapse.id} inserted into the database")

    answered = False

    start_time = int(time.time())
    timeout = 180  # Default timeout is 180 seconds
    bt.logging.debug(f"Waiting for the task: {synapse.id} to be answered")
    db_task = None
    while int(time.time()) - start_time < timeout:
        db_task = tasks_db.get_task(synapse.id)
        if db_task is not None:
            answered = db_task.answer != ""
            if answered:
                break
        time.sleep(1)
    # If the task is answered within the timeout the db_task will not be None
    if answered and db_task is not None:
        print(f"Task: {db_task.id} answered within the timeout")
        synapse.answer = str(db_task.answer)
        print(f"For the task: {db_task.id} the answer is: {synapse.answer}")

    return synapse
