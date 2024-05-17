from hip.protocol import TaskSynapse
import hip.validator.generator
import random
import uuid


async def get_llm_task() -> TaskSynapse:
    context = hip.validator.generator.generate_paragraph()
    taskType = random.choice(["qa", "sentiment_analysis", "summarization"])
    if taskType == "qa":
        task = hip.validator.generator.generate_question_answer(context)
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
