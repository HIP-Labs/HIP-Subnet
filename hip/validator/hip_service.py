from hip.protocol import TaskSynapse
from hip.validator import text_generator
import random
import uuid
import bittensor as bt

from hip.validator.image_generator import generate_image_task


def get_llm_task(captcha: str) -> TaskSynapse:
    bt.logging.info("Generating a new task")
    context = text_generator.generate_paragraph()
    bt.logging.info(f"Context: {context}")
    taskType = random.choice(["qa", "sentiment_analysis", "summarization"])
    bt.logging.info(f"Task Type: {taskType}")
    if taskType == "qa":
        task = text_generator.generate_question_answer(context)
        bt.logging.info(f"Task: {task}")
        return TaskSynapse(
            id=str(uuid.uuid4()),
            label=task["question"],
            type="select",
            options=task["options"],
            value=context,
            image="",
            answer=task["options"][task["answer"]],
            captcha=captcha,
            captchaValue="",
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
            captcha=captcha,
            captchaValue="",
        )
    elif taskType == "summarization":
        summaries = text_generator.generate_summaries(context)
        shuffledSummaries = summaries.copy()
        bt.logging.info(f"Task: {summaries}")
        random.shuffle(shuffledSummaries)

        return TaskSynapse(
            id=str(uuid.uuid4()),
            label="Select the correct summary for the given text:",
            type="select",
            options=shuffledSummaries,
            value=context,
            image="",
            answer=summaries[0],
            captcha=captcha,
            captchaValue="",
        )
    else:
        # throw an error
        raise ValueError("Invalid task type")


def get_image_task(captcha: str) -> TaskSynapse:
    bt.logging.info("Generating a new image task")
    task = generate_image_task(captcha)
    return task


if __name__ == "__main__":
    task = get_image_task(captcha="captcha")
    print(task)
