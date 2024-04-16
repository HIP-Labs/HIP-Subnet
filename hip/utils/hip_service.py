from hip.protocol import TaskSynapse


# TODO: Call the HIP Service api to get the task
async def get_task() -> TaskSynapse:
    return TaskSynapse(
        id="task 1",
        label="What is the meaning of life?",
        type="select",
        options=["42", "24", "100", "0"],
        value="The life in its entirety is a mystery. But the meaning of life is 42. Deal with it, human.",
        image="",
        answer="",
    )
