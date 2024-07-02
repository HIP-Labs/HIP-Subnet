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


def linear_rewards(self, correct_answers: int) -> float:
    # make sure the values are within the correct range (0-480)
    # Max 480 assumes that the maximum number of questions is 480 in 24 hours
    # That is 180 seconds per question
    correct_answers = min(correct_answers, 480)
    correct_answers = max(correct_answers, 0)

    slope = 0
    y_intercept = 0

    if correct_answers <= 100:
        slope = 0.5
        y_intercept = 0
    else:
        slope = 0.11753
        y_intercept = 44

    score_out_of_100 = slope * correct_answers + y_intercept
    score_out_of_1 = min(
        score_out_of_100 / 100, 1
    )  # return a value between 0 and 1 (inclusive of 0 and 1)
    return score_out_of_1 * 65535  # return a value between 0 and 65535


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
    ground_truth: str,
    responses: List[TaskSynapse],
) -> List[bool]:
    """
    Returns a tensor of rewards for the given task and responses.

    Args:
    - task (TaskSynapse): The task sent to the miner.
    - responses (List[TaskSynapse]): A list of responses from the miner.

    Returns:
    - List[bool]: A list of boolean values indicating whether the response is correct or not.
    """
    correct_answer = ground_truth
    is_answer_correct = []
    for response in responses:
        """
        If the response is captcha, check if the response matches the ground truth based on the captcha_match function.
        otherwise, check if the response exactly matches the correct answer.
        """
        if response.type == "text" and response.image:
            is_answer_correct.append(captcha_match(correct_answer, response.answer))
        else:
            if response.answer == correct_answer:
                is_answer_correct.append(True)
            else:
                is_answer_correct.append(False)
    return is_answer_correct
