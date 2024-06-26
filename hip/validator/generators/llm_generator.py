from hip.protocol import TaskSynapse
from hip.validator import text_generator
import random
import uuid
import bittensor as bt


def generate_llm_task() -> TaskSynapse:
    bt.logging.info("Generating a new task")
    context = text_generator.generate_paragraph()
    bt.logging.info(f"Context: {context}")
    taskType = random.choice(["qa", "sentiment_analysis", "summarization"])
    bt.logging.info(f"Task Type: {taskType}")
    if taskType == "qa":
        task = text_generator.generate_question_answer(context)
        bt.logging.info(f"Task: {task}")

        # Validate task["answer"] index
        if task["answer"] < 0 or task["answer"] >= len(task["options"]):
            raise IndexError("task['answer'] index out of range for task['options']")

        return TaskSynapse(
            id=str(uuid.uuid4()),
            label=task["question"],
            type="select",
            options=task["options"],
            value=context,
            image="",
            answer=task["options"][task["answer"]],
        )
    elif taskType == "sentiment_analysis":
        sentiment = text_generator.get_sentiment(context)
        bt.logging.info(f"Task: {sentiment}")
        return TaskSynapse(
            id=str(uuid.uuid4()),
            label="What is the sentiment of the given text?",
            type="select",
            options=["Positive", "Negative", "Neutral"],
            value=context,
            image="",
            answer=sentiment,
        )
    elif taskType == "summarization":
        summaries = text_generator.generate_summaries(context)
        shuffledSummaries = summaries.copy()
        bt.logging.info(f"Task: {summaries}")
        random.shuffle(shuffledSummaries)

        # Validate summaries list
        if not summaries:
            raise ValueError("Summaries list is empty")

        return TaskSynapse(
            id=str(uuid.uuid4()),
            label="Select the correct summary for the given text:",
            type="select",
            options=shuffledSummaries,
            value=context,
            image="",
            answer=summaries[0],
        )
    else:
        # throw an error
        raise ValueError("Invalid task type")
