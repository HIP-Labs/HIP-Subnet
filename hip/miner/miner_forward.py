import bittensor as bt
import time
from hip.protocol import TaskSynapse
from hip.miner.db import Task, Option, SessionLocal

# Create a new database session
db = SessionLocal()


def add_task(id, label, type, value, image, expiry, options):
    task = Task(
        id=id,
        label=label,
        type=type,
        value=value,
        image=image,
        expiry=expiry,
        answer="",
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    for option_text in options:
        option = Option(task_id=task.id, option=option_text)
        db.add(option)
    db.commit()
    return task


def get_task(task_id: str):
    return db.query(Task).filter(Task.id == task_id).first()


async def miner_forward(self, synapse: TaskSynapse) -> TaskSynapse:
    """
    Processes the incoming 'TaskSynapse' synapse by performing a predefined operation on the input data.

    Args:
        synapse (hip.protocol.TaskSynapse): The synapse object containing the task data.

    Returns:
        hip.protocol.TaskSynapse: The synapse object with the 'answer' field set to the answer from miner.
    """
    bt.logging.debug("Forwarding synapse to frontend")
    add_task(
        id=synapse.id,
        label=synapse.label,
        type=synapse.type,
        options=synapse.options,
        value=synapse.value,
        image=synapse.image,
        expiry=time.time() + 180,
    )
    bt.logging.debug(f"Task: {synapse.id} inserted into the database")

    answered = False

    start_time = int(time.time())
    timeout = 180  # Default timeout is 180 seconds
    bt.logging.debug(f"Waiting for the task: {synapse.id} to be answered")
    db_task = None
    sleep_times = [30, 20, 10, 2]
    sleep_index = 0

    while int(time.time()) - start_time < timeout:
        db_task = get_task(synapse.id)
        if db_task is not None:
            answered = str(db_task.answer) != ""
            if answered:
                break
        # Sleep for a certain amount of time before checking again
        time.sleep(sleep_times[sleep_index])
        if sleep_index < len(sleep_times) - 1:
            sleep_index += 1

    # If the task is answered within the timeout the db_task will not be None
    if answered and db_task is not None:
        print(f"Task: {db_task.id} answered within the timeout")
        synapse.answer = str(db_task.answer)
        print(f"For the task: {db_task.id} the answer is: {synapse.answer}")

    return synapse
