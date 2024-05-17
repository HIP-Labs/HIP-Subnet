from hip.protocol import TaskSynapse
import hip.validator.generator
import random
import uuid
import bittensor as bt


async def get_llm_task() -> TaskSynapse:
    bt.logging.info("Generating a new task")
    context = hip.validator.generator.generate_paragraph()
    bt.logging.info(f"Context: {context}")
    taskType = random.choice(["qa", "sentiment_analysis", "summarization"])
    bt.logging.info(f"Task Type: {taskType}")
    if taskType == "qa":
        task = hip.validator.generator.generate_question_answer(context)
        bt.logging.info(f"Task: {task}")
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
        sentiment = hip.validator.generator.get_sentiment(context)
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
        summaries = hip.validator.generator.generate_summaries(context)
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
        )
    else:
        # throw an error
        raise ValueError("Invalid task type")
