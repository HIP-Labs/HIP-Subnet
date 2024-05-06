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


def get_rewards(
    self,
    task: TaskSynapse,
    responses: List[TaskSynapse],
) -> torch.FloatTensor:
    """
    Returns a tensor of rewards for the given task and responses.

    Args:
    - task (TaskSynapse): The task sent to the miner.
    - responses (List[TaskSynapse]): A list of responses from the miner.

    Returns:
    - torch.FloatTensor: A tensor of rewards for the given query and responses.
    """
    scores: list[float] = [0.0] * len(responses)
    timeout = self.config.neuron.timeout

    for idx, response in enumerate(responses):
        if not response.dendrite or response.dendrite.status_code != 200:
            if response.dendrite and response.dendrite.status_code == 408:
                scores[idx] = (
                    0.1  # In case of timeout, give a small reward to keep the miner in the loop for future tasks
                )
                continue
            else:
                scores[idx] = 0.1
        elif not response.answer:
            scores[idx] = 0.1
        elif task.type == "select":
            if not response.answer in task.options:
                scores[idx] = 0.1
            elif response.dendrite.process_time == None:
                scores[idx] = 0.1
            elif response.dendrite.process_time >= timeout:  # type: ignore
                scores[idx] = (
                    0.1  # Give a small reward for a timeout (to keep the miner in the loop for future tasks
                )
            else:
                # TODO(developer): Define how the validator scores responses.
                scores[idx] = (
                    1.0  # dummy score that will be replaced by the actual scoring logic
                )
        elif task.type == "input":
            # check if the answer is of type string
            if not isinstance(response.answer, str):
                scores[idx] = 0.1
            else:
                scores[idx] = (
                    1.0  # dummy score that will be replaced by the actual scoring logic
                )

    if task.type == "select":
        answer_counts = {}
        for idx, response in enumerate(responses):
            if scores[idx] == 1.0:
                if response.answer in answer_counts:
                    answer_counts[response.answer] += 1
                else:
                    answer_counts[response.answer] = 1
        # Get the answer with the most votes
        chosen_answer = find_answer_with_highest_count(answer_counts)
        if chosen_answer:
            for idx, response in enumerate(responses):
                if response.answer == chosen_answer:
                    scores[idx] += answer_counts[chosen_answer] - 1
                else:
                    scores[idx] = 0.1
        else:
            for idx, response in enumerate(responses):
                if scores[idx] == 1.0:
                    scores[idx] = 0.1

    # Get all the reward results by iteratively calling your reward() function.
    return torch.FloatTensor(scores).to(  # type: ignore
        self.device
    )  # type: ignore
