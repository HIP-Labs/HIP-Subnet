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
    db_task = add_task(
        id=synapse.id,
        label=synapse.label,
        type=synapse.type,
        options=synapse.options,
        value=synapse.value,
        image=synapse.image,
        expiry=int(time.time()) + 180,
    )
    bt.logging.debug(f"Task: {synapse.id} inserted into the database")

    answered = False

    start_time = int(time.time())
    timeout = 180  # Default timeout is 180 seconds
    bt.logging.debug(f"Waiting for the task: {synapse.id} to be answered")
    while int(time.time()) - start_time < timeout:
        db.refresh(db_task)  # Refresh the task instance to get the latest state
        answered = str(db_task.answer) != ""
        if answered:
            bt.logging.debug(f"Task: {db_task.id} answered with: {db_task.answer}")
            break
        else:
            bt.logging.debug(f"Task: {db_task.id} not answered yet")
        # Sleep for a certain amount of time before checking again
        time.sleep(2)
    if not answered:
        bt.logging.debug(f"Task: {synapse.id} not answered within the timeout")

    # If the task is answered
    if answered:
        print(f"Task: {db_task.id} answered within the timeout")
        synapse.answer = str(db_task.answer)
        print(f"For the task: {db_task.id} the answer is: {synapse.answer}")
    else:
        synapse.answer = "Task not answered within the timeout"

    return synapse
