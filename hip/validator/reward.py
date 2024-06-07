# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2023 HIP LABS

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import torch
from typing import List
from hip.protocol import TaskSynapse
import random
import bittensor as bt


def find_answer_with_highest_count(data):
    # Initialize variables to store the maximum count and corresponding string
    max_count = -1
    max_answer = None

    # Iterate through the dictionary items
    for answer, count in data.items():
        # Check if the current count is greater than the max_count found so far
        if count > max_count:
            max_count = count
            max_answer = answer

    # Return the string with the highest count
    return max_answer


def captcha_match(captcha_ground_truth: str, captchaValue: str) -> bool:
    # convert both to uppercase and remove all non alphanumeric characters
    captcha_ground_truth = "".join(
        [c.upper() for c in captcha_ground_truth if c.isalnum()]
    )
    response_captcha = "".join([c.upper() for c in captchaValue if c.isalnum()])
    return captcha_ground_truth == response_captcha


def get_rewards(
    self,
    task: TaskSynapse,
    responses: List[TaskSynapse],
    captcha_ground_truth: str,
) -> torch.FloatTensor:
    """
    Returns a tensor of rewards for the given task and responses.

    Args:
    - task (TaskSynapse): The task sent to the miner.
    - responses (List[TaskSynapse]): A list of responses from the miner.

    Returns:
    - torch.FloatTensor: A tensor of rewards for the given query and responses.
    """
    # Randomly choose if the correct answer is the llm generated one from tasksynapse or the most common of the responses
    useLLMGeneratedAnswer = random.choice([True, False])

    # But if image task, always use the preknown answer
    if task.image != "":
        useLLMGeneratedAnswer = True

    scores: list[float] = [0.0] * len(responses)
    chosen_answer = None
    if useLLMGeneratedAnswer:
        chosen_answer = task.answer
        for idx, response in enumerate(responses):
            if captcha_match(captcha_ground_truth, response.captchaValue):
                if response.answer == task.answer:
                    scores[idx] = 1.0
                else:
                    scores[idx] = 0.1
            else:
                scores[idx] = 0.0
    else:
        for idx, response in enumerate(responses):
            # only consider if the captcha is correct
            if captcha_match(captcha_ground_truth, response.captchaValue):
                answer_counts = {}
                if response.answer in answer_counts:
                    answer_counts[response.answer] += 1
                else:
                    answer_counts[response.answer] = 1
        # Get the answer with the most votes
        chosen_answer = find_answer_with_highest_count(answer_counts)
        for idx, response in enumerate(responses):
            if response.axon and response.axon.status_code == 200:
                if chosen_answer:
                    if captcha_match(captcha_ground_truth, response.captchaValue):
                        if chosen_answer == task.answer:
                            scores[idx] = 1.0
                        else:
                            scores[idx] = 0.1
                    else:
                        scores[idx] = 0.0
            else:
                scores[idx] = 0.0
    bt.logging.info(f"Use LLM Generated Answer: {useLLMGeneratedAnswer}")
    if not useLLMGeneratedAnswer:
        bt.logging.info(f"Chosen Answer: {chosen_answer}")

    # Get all the reward results by iteratively calling your reward() function.
    return torch.FloatTensor(scores).to(  # type: ignore
        self.device
    )  # type: ignore
