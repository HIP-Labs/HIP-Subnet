from transformers import pipeline
from hip.validator.words import get_random_words
import torch
import json

model_name = "HuggingFaceH4/zephyr-7b-beta"
pipe = pipeline(
    "text-generation",
    model=model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)


def generate_paragraph():
    [noun, verb, adjective, tone] = get_random_words()
    prompt = f"Write a 150 words paragraph using the following words: {noun}, {verb}, {adjective}. Make sure the tone is {tone}. Paragraph:"
    outputs = pipe(
        prompt,
        max_new_tokens=3000,
        do_sample=True,
        temperature=0.7,
        top_k=50,
        top_p=0.95,
    )
    return f"{outputs[0]['generated_text']}".replace(prompt, "")  # type: ignore


def generate_summaries(text):
    prompt1: str = (
        f"Generate a concise 50 words summary of the following context. \nContext: {text}\n\nSummary:"
    )
    prompt2: str = (
        f"Generate a slightly misleading 50 words summary of the following context that can trick the reader to belive the summary is correct \nContext: {text}\n\nSummary:"
    )
    prompt3: str = (
        f"Generate a concise 50 words incorrect summary of the following context that tricks the reader and looks correct if not read properly. Make sure the resulting summary is close to the text in text similarity. \nContext: {text}\n\nSummary:"
    )

    outputs1 = pipe(
        prompt1,
        max_new_tokens=1000,
        do_sample=True,
        top_k=50,
        top_p=0.9,
        temperature=0.7,
    )

    outputs2 = pipe(
        prompt2,
        max_new_tokens=1000,
        do_sample=True,
        top_k=100,
        top_p=0.95,
        temperature=0.9,
    )

    outputs3 = pipe(
        prompt3,
        max_new_tokens=1000,
        do_sample=True,
        top_k=200,
        top_p=0.98,
        temperature=1.2,
    )

    summaries = [
        # index 0: correct summary
        f"{outputs1[0]['generated_text']}".replace(prompt1, ""),  # type: ignore
        f"{outputs2[0]['generated_text']}".replace(prompt2, ""),  # type: ignore
        f"{outputs3[0]['generated_text']}".replace(prompt3, ""),  # type: ignore
    ]
    return summaries


def generate_question_answer(text):
    prompt = f"""Generate a multiple choice question based on the following context.
Context: {text}

Output must only contain the following JSON format and nothing else:
{{
    "question": "question text", // question text
    "options": ["option1", "option2", "option3", "option4"], // list of options
    "answer": 0 // index of the correct option
}}

Output:
```json
"""

    outputs = pipe(
        prompt,
        max_new_tokens=1000,
        do_sample=True,
        top_k=50,
        top_p=0.9,
        temperature=0.7,
    )
    generated_text = f"{outputs[0]['generated_text']}".replace(prompt, "").replace("```", "")  # type: ignore
    # remove anything before { and after }
    start = generated_text.find("{")
    end = generated_text.find("}")
    json_converted = json.loads(generated_text[start : end + 1])
    # make sure the json is in the correct format
    assert "question" in json_converted, "Question key not found in the JSON"
    assert "options" in json_converted, "Options key not found in the JSON"
    assert "answer" in json_converted, "Answer key not found in the JSON"
    return json_converted


def get_sentiment(text):
    prompt = f"Select the sentiment of the following text based on given options: Text: \n{text}\n\nSentiment Options: Positive, Negative, Neutral\n\nSentiment (just the selected sentiment):"
    outputs = pipe(
        prompt,
        max_new_tokens=5,
        do_sample=True,
        top_k=50,
        top_p=0.9,
        temperature=0.3,
    )
    output_text = f"{outputs[0]['generated_text']}".replace(prompt, "").lower()  # type: ignore
    output_opts = [
        output_text.find("positive"),
        output_text.find("negative"),
        output_text.find("neutral"),
    ]
    output = ["Positive", "Negative", "Neutral"][output_opts.index(max(output_opts))]
    return output
